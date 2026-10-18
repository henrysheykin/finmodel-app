"""FastAPI application: order API and signed downloads (pages arrive with E10/E13)."""

from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session, sessionmaker

from adapters.email import make_sender
from adapters.notify import Notifier
from adapters.payments import PaymentProvider, make_provider
from adapters.storage import Storage, make_storage
from app import __version__, links, ratelimit
from app.briefing import Answers, BriefSource, PrefillBriefSource, supported_business_types
from app.config import Settings, load_settings
from app.db import make_engine, make_sessionmaker, migrate, session_scope
from app.emails import EmailNotifier
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
    payments: PaymentProvider | None = None
    notifier: Notifier | None = None


#: Content-Security-Policy for every response (E17). Scripts and styles come from our own origin
#: only; JSON data blocks (<script type="application/json">) are not executed, so need no exception.
#: form-action is left out on purpose: Chrome applies it to the 303 redirect to Stripe Checkout.
CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
    "font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
)
UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
#: no endpoint takes uploads: wizard forms and Stripe events are a few kilobytes
MAX_BODY_BYTES = 1_000_000
#: server-to-server callers (no browser, no Origin) authenticated by their own signature
ORIGIN_EXEMPT = ("/webhooks/",)


def _origin_of(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}".lower()


def cross_site(request: Request, public_base_url: str) -> bool:
    """True for a browser form or fetch POSTed from another site (CSRF defence in depth, E17).

    Browsers send ``Origin`` with every cross-origin POST; requests without it (API clients,
    tests, old browsers on same-origin forms) pass, and the admin forms carry their own tokens.
    """
    if request.method not in UNSAFE_METHODS or request.url.path.startswith(ORIGIN_EXEMPT):
        return False
    origin = request.headers.get("origin")
    if origin is None:
        return False
    own = {_origin_of(public_base_url), f"{request.url.scheme}://{request.headers.get('host', '')}".lower()}
    return origin.lower() not in own


def _too_large(request: Request) -> bool:
    try:
        return int(request.headers.get("content-length") or 0) > MAX_BODY_BYTES
    except ValueError:
        return True


class OrderIn(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    answers: Answers


def create_app(services: Services | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        if getattr(app.state, "services", None) is None:
            from app.logs import configure_logging

            configure_logging()
            cfg = load_settings()
            if not cfg.is_prod:
                migrate(cfg.database_url)  # prod runs migrations as a deploy step (E15)
            app.state.services = Services(
                cfg,
                make_sessionmaker(make_engine(cfg.database_url)),
                make_storage(cfg.storage_backend, cfg.storage_dir, cfg.s3_bucket, cfg.s3_endpoint_url),
                PrefillBriefSource(),
                make_provider(
                    cfg.payment_provider,
                    cfg.public_base_url,
                    cfg.stripe_secret_key,
                    cfg.stripe_webhook_secret,
                    cfg.allow_live_payments,
                ),
                None,
            )
            sv = app.state.services
            sv.notifier = EmailNotifier(
                make_sender(cfg.email_provider, cfg.email_api_key, cfg.email_from), cfg, sv.sessions
            )
        yield

    app = FastAPI(title="StartupModel", docs_url=None, redoc_url=None, lifespan=lifespan)
    app.state.services = services
    app.state.limiter = None  # built from the settings on the first rate-limited request

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        sv = request.app.state.services
        if _too_large(request):
            resp = PlainTextResponse("request body too large", status_code=413)
        elif sv is not None and cross_site(request, sv.cfg.public_base_url):
            resp = PlainTextResponse("cross-site request refused", status_code=403)
        else:
            resp = await call_next(request)
        h = resp.headers
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        h.setdefault("X-Frame-Options", "DENY")
        h.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        h.setdefault("Content-Security-Policy", CSP)
        if sv is not None and sv.cfg.is_prod:
            h.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        if request.url.path.startswith("/static/") and resp.status_code == 200:
            # Versioned URLs (asset() adds ?v=<content hash>) never change; unversioned ones must revalidate.
            versioned = "v" in request.query_params
            h["Cache-Control"] = (
                "public, max-age=31536000, immutable" if versioned else "public, max-age=0, must-revalidate"
            )
        return resp

    app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
    from app.account_web import router as account_router
    from app.admin import router as admin_router
    from app.landing import router as landing_router
    from app.seo import router as seo_router
    from app.web import router as web_router

    app.include_router(web_router)
    app.include_router(account_router)
    app.include_router(admin_router)
    app.include_router(landing_router)
    app.include_router(seo_router)

    def svc(request: Request) -> Services:
        return request.app.state.services

    @app.get("/healthz")
    def healthz() -> dict:
        return {"status": "ok", "version": __version__}

    @app.get("/api/business-types")
    def business_types() -> dict:
        return {"available": supported_business_types()}

    @app.post("/api/orders", status_code=201)
    def post_order(body: OrderIn, request: Request) -> dict:
        sv = svc(request)
        wait = ratelimit.check(request, "orders")
        if wait:
            raise HTTPException(429, "too many orders from this address; try again later", {"Retry-After": str(wait)})
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
