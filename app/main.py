"""FastAPI application: order API and signed downloads (pages arrive with E10/E13)."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session, sessionmaker

from adapters.storage import Storage, make_storage
from app import links
from app.briefing import Answers, BriefSource, PrefillBriefSource, supported_business_types
from app.config import Settings, load_settings
from app.db import make_engine, make_sessionmaker, migrate, session_scope
from app.models import Artifact, Order
from app.orders import OrderError, create_order
from engine.brief import BriefError

STATIC = Path(__file__).resolve().parents[1] / "web" / "static"


@dataclass
class Services:
    cfg: Settings
    sessions: sessionmaker[Session]
    storage: Storage
    briefs: BriefSource


class OrderIn(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    answers: Answers


def create_app(services: Services | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if getattr(app.state, "services", None) is None:
            cfg = load_settings()
            if not cfg.is_prod:
                migrate(cfg.database_url)  # prod runs migrations as a deploy step (E15)
            app.state.services = Services(
                cfg,
                make_sessionmaker(make_engine(cfg.database_url)),
                make_storage(cfg.storage_backend, cfg.storage_dir, cfg.s3_bucket, cfg.s3_endpoint_url),
                PrefillBriefSource(),
            )
        yield

    app = FastAPI(title="StartupModel", docs_url=None, redoc_url=None, lifespan=lifespan)
    app.state.services = services
    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
    from app.web import router as web_router

    app.include_router(web_router)

    def svc(request: Request) -> Services:
        return request.app.state.services

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok"}

    @app.get("/api/business-types")
    def business_types() -> dict:
        return {"available": supported_business_types()}

    @app.post("/api/orders", status_code=201)
    def post_order(body: OrderIn, request: Request) -> dict:
        sv = svc(request)
        try:
            brief = sv.briefs.build_brief(body.answers)
        except (BriefError, ValidationError) as exc:
            raise HTTPException(422, f"cannot build a model from these answers: {exc}") from None
        try:
            with session_scope(sv.sessions) as s:
                order = create_order(s, sv.cfg, body.email, brief, body.answers.model_dump())
                out = _public(order)
        except OrderError as exc:
            raise HTTPException(422, str(exc)) from None
        return out

    @app.get("/api/orders/{order_id}")
    def get_order(order_id: str, request: Request) -> dict:
        sv = svc(request)
        with session_scope(sv.sessions) as s:
            order = s.get(Order, order_id)
            if order is None:
                raise HTTPException(404, "order not found")
            return _public(order)

    @app.get("/download/{token}")
    def download(token: str, request: Request) -> Response:
        sv = svc(request)
        try:
            artifact_id = links.verify(sv.cfg.secret_key, token)
        except links.LinkError as exc:
            code = 410 if "expired" in str(exc) else 404
            raise HTTPException(code, "this download link has expired" if code == 410 else "not found") from None
        with session_scope(sv.sessions) as s:
            art = s.get(Artifact, artifact_id)
            if art is None or art.kind != "model_xlsx" or art.order.status != "ready":
                raise HTTPException(404, "not found")
            key, name, ctype = art.storage_key, art.filename, art.content_type
        data = sv.storage.get(key)
        return Response(
            data,
            media_type=ctype,
            headers={
                "Content-Disposition": f'attachment; filename="{name}"',
                "Cache-Control": "private, no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    return app


def _public(order: Order) -> dict:
    """What the customer-facing API may show (no email, no brief internals)."""
    return {
        "order_id": order.id,
        "status": order.status,
        "template": order.template,
        "tier": order.tier,
        "price_cents": order.price_cents,
        "currency": order.currency,
        "created_at": order.created_at.isoformat() + "Z",
    }


app = create_app()
