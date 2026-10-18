"""Server-rendered pages: the wizard (/start) and the checkout summary (/checkout/{id})."""

from __future__ import annotations

import hashlib
import json
import logging
from functools import cache
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from adapters.payments import CheckoutRequest, FakeProvider, PaymentError, PaymentEvent, SignatureError
from app import ratelimit, wizard
from app.briefing import Answers
from app.db import session_scope
from app.models import Order
from app.orders import AlreadyPaid, DuplicatePayment, OrderError, create_order, mark_paid
from engine.brief import BriefError

templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))
templates.env.filters["money"] = lambda cents: f"${cents / 100:,.0f}"
templates.env.filters["fmtnum"] = lambda v: f"{v:g}" if isinstance(v, float) else str(v)

STATIC_DIR = Path(__file__).resolve().parents[1] / "web" / "static"


@cache
def asset(path: str) -> str:
    """URL of a static file with a content hash, so browsers and the CDN never serve a stale copy
    after a deploy (static files are cached for hours under a fixed URL)."""
    file = STATIC_DIR / path
    try:
        digest = hashlib.sha256(file.read_bytes()).hexdigest()[:10]
    except OSError:
        return f"/static/{path}"
    return f"/static/{path}?v={digest}"


templates.env.globals["asset"] = asset

STATUS_LABEL = {
    "awaiting_payment": "waiting for payment",
    "paid": "paid — queued for building",
    "building": "building",
    "checking": "checking",
    "ready": "ready — the download link is in your email",
    "failed": "we could not deliver this model; we are on it and will email you",
}

DEFAULT_FORM = {
    "business_type": "",
    "business_name": "",
    "goal": "revenue_profit",
    "stage": "planning",
    "horizon_years": "3",
    "granularity": "monthly",
    "tier": "full",
    "email": "",
    "sample_data": "",
}

router = APIRouter()
log = logging.getLogger("web")


async def form_data(request: Request) -> dict[str, str]:
    """The submitted form, read on the event loop. Handlers that take it as a dependency are plain
    ``def`` functions, so FastAPI runs them in its thread pool: their database work and the calls
    to Stripe and the email API never block the event loop (E17)."""
    return {k: str(v) for k, v in (await request.form()).items()}


async def raw_body(request: Request) -> bytes:
    return await request.body()


FormData = Annotated[dict, Depends(form_data)]
RawBody = Annotated[bytes, Depends(raw_body)]

TOO_MANY = "Too many requests from your network. Please wait a few minutes and try again."


def _label(options, value) -> str:
    return next((label for v, label in options if str(v) == str(value)), str(value))


def _render_start(request: Request, form: dict, errors: list[str], status: int = 200) -> HTMLResponse:
    sv = request.app.state.services
    bt, stage = form.get("business_type", ""), form.get("stage", "planning")
    kn = wizard.key_numbers(bt, stage) if wizard.available(bt) else []
    data = {
        "labels": {
            "business_type": dict(wizard.BUSINESS_TYPES),
            "goal": dict(wizard.GOALS),
            "stage": dict(wizard.STAGES),
            "granularity": dict(wizard.GRANULARITIES),
            "tier": {k: p["name"] for k, p in wizard.PLANS.items()},
        },
        "prices": sv.cfg.prices,
        "available": [k for k, _ in wizard.BUSINESS_TYPES if wizard.available(k)],
        "start_step": _first_error_step(errors) if errors else 1,
    }
    return templates.TemplateResponse(
        request,
        "start.html",
        {
            "form": form,
            "errors": errors,
            "business_types": wizard.BUSINESS_TYPES,
            "goals": wizard.GOALS,
            "stages": wizard.STAGES,
            "horizons": wizard.HORIZONS,
            "granularities": wizard.GRANULARITIES,
            "plans": wizard.PLANS,
            "prices": sv.cfg.prices,
            "key_numbers": kn,
            "wizard_data": data,
        },
        status_code=status,
    )


def _first_error_step(errors: list[str]) -> int:
    if TOO_MANY in errors:
        return 7  # they were submitting: keep them on the last step with their answers
    text = " ".join(errors).lower()
    for step, words in ((1, ("business",)), (5, ("number", "between", "must")), (7, ("email",))):
        if any(w in text for w in words):
            return step
    return 1


@router.get("/start", response_class=HTMLResponse)
def start(
    request: Request,
    plan: str = "full",
    type: str = "",
    goal: str = "",
    horizon: str = "",
    granularity: str = "",
    sample: str = "",
) -> HTMLResponse:
    """The brief. Query parameters pre-fill it (used by the landing page's demo); unknown values are ignored."""
    form = {**DEFAULT_FORM, "tier": plan if plan in wizard.PLANS else "full"}
    if type in dict(wizard.BUSINESS_TYPES):
        form["business_type"] = type
    if goal in dict(wizard.GOALS):
        form["goal"] = goal
    if horizon in {str(y) for y, _ in wizard.HORIZONS}:
        form["horizon_years"] = horizon
    if granularity in dict(wizard.GRANULARITIES):
        form["granularity"] = granularity
    if sample == "1":
        form["sample_data"] = "1"
    return _render_start(request, form, [])


@router.get("/api/key-numbers")
def api_key_numbers(business_type: str, stage: str = "planning") -> JSONResponse:
    if stage not in dict(wizard.STAGES):
        raise HTTPException(422, "unknown stage")
    if not wizard.available(business_type):
        return JSONResponse({"available": False, "fields": []})
    return JSONResponse({"available": True, "fields": [k.to_dict() for k in wizard.key_numbers(business_type, stage)]})


@router.post("/start")
def start_submit(request: Request, raw: FormData):
    sv = request.app.state.services
    form = {**DEFAULT_FORM, **raw}
    wait = ratelimit.check(request, "orders")
    if wait:
        resp = _render_start(request, form, [TOO_MANY], status=429)
        resp.headers["Retry-After"] = str(wait)
        return resp
    errors: list[str] = []
    bt = form["business_type"]
    if not bt:
        errors.append("Choose your business type.")
    elif not wizard.available(bt):
        errors.append(f"{_label(wizard.BUSINESS_TYPES, bt)}: this business type is not available yet.")
    key_numbers: dict[str, float] = {}
    if not errors and not form.get("sample_data"):
        try:
            key_numbers = wizard.parse_key_numbers(bt, form["stage"], form)
        except ValueError as exc:
            errors.append(str(exc))
    email = form["email"].strip()
    if "@" not in email or "." not in email.split("@")[-1]:
        errors.append("Enter the email address where we should send the model.")
    answers = None
    if not errors:
        try:
            answers = Answers(
                business_type=bt,
                goal=form["goal"],
                stage=form["stage"],
                horizon_years=int(form["horizon_years"]),
                granularity=form["granularity"],
                tier=form["tier"],
                business_name=form["business_name"].strip()[:60],
                key_numbers=key_numbers,
            )
            brief = sv.briefs.build_brief(answers)
        except (ValidationError, ValueError, BriefError) as exc:
            errors.append(f"Some answers could not be used: {_short(exc)}")
    if errors:
        return _render_start(request, form, errors, status=422)
    try:
        with session_scope(sv.sessions) as s:
            order = create_order(s, sv.cfg, email, brief, answers.model_dump())
            oid = order.id
    except OrderError as exc:
        return _render_start(request, form, [str(exc)], status=422)
    return RedirectResponse(f"/checkout/{oid}", status_code=303)


def _short(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        return "; ".join(f"{'.'.join(map(str, e['loc']))}: {e['msg']}" for e in exc.errors()[:3])
    return str(exc)[:300]


@router.get("/checkout/{order_id}", response_class=HTMLResponse)
def checkout(order_id: str, request: Request, cancelled: int = 0) -> HTMLResponse:
    sv = request.app.state.services
    with session_scope(sv.sessions) as s:
        order = s.get(Order, order_id)
        if order is None:
            raise HTTPException(404, "order not found")
        a = json.loads(order.answers_json or "{}")
        summary = {
            "order_id": order.id,
            "status": order.status,
            "status_label": STATUS_LABEL.get(order.status, order.status),
            "business": a.get("business_name") or _label(wizard.BUSINESS_TYPES, a.get("business_type", "")),
            "goal": _label(wizard.GOALS, a.get("goal", "")),
            "stage": _label(wizard.STAGES, a.get("stage", "")),
            "period": f"{a.get('horizon_years', '')} years, {a.get('granularity', '')}".replace("1 years", "1 year"),
            "plan": wizard.PLANS[order.tier]["name"],
            "email": _mask(order.email),
            "price": f"${order.price_cents / 100:,.0f}",
        }
    return templates.TemplateResponse(request, "checkout.html", {"s": summary, "cancelled": bool(cancelled)})


@router.post("/checkout/{order_id}/pay")
def pay(order_id: str, request: Request):
    """Create a hosted checkout session and send the customer to it."""
    sv = request.app.state.services
    wait = ratelimit.check(request, "checkout")
    if wait:
        return templates.TemplateResponse(
            request,
            "message.html",
            {"heading": "Too many attempts", "text": TOO_MANY, "link": (f"/checkout/{order_id}", "Back to your order")},
            status_code=429,
            headers={"Retry-After": str(wait)},
        )
    with session_scope(sv.sessions) as s:
        order = s.get(Order, order_id)
        if order is None:
            raise HTTPException(404, "order not found")
        if order.status != "awaiting_payment":
            return RedirectResponse(f"/checkout/{order_id}", status_code=303)
        a = json.loads(order.answers_json or "{}")
        btype = _label(wizard.BUSINESS_TYPES, a.get("business_type", ""))
        name = f"StartupModel {wizard.PLANS[order.tier]['name']} — {btype}"
        req = CheckoutRequest(
            order_id=order.id,
            amount_cents=order.price_cents,
            currency=order.currency,
            product_name=name,
            email=order.email,
            success_url=f"{sv.cfg.public_base_url}/checkout/{order.id}/success",
            cancel_url=f"{sv.cfg.public_base_url}/checkout/{order.id}?cancelled=1",
        )
    try:
        session = sv.payments.create_checkout(req)
    except PaymentError:
        log.exception("checkout session failed for order %s", order_id)
        return templates.TemplateResponse(
            request,
            "message.html",
            {
                "heading": "Payment page unavailable",
                "text": "We could not open the payment page. Nothing was charged. Please try again in a minute.",
                "link": (f"/checkout/{order_id}", "Back to your order"),
            },
            status_code=502,
        )
    return RedirectResponse(session.url, status_code=303)


@router.get("/checkout/{order_id}/success", response_class=HTMLResponse)
def paid_page(order_id: str, request: Request) -> HTMLResponse:
    """Where the provider sends the customer back. Shows status only; the webhook decides payment."""
    sv = request.app.state.services
    with session_scope(sv.sessions) as s:
        order = s.get(Order, order_id)
        if order is None:
            raise HTTPException(404, "order not found")
        status = order.status
    return templates.TemplateResponse(
        request,
        "success.html",
        {"order_id": order_id, "status": status, "label": STATUS_LABEL.get(status, status)},
    )


@router.post("/webhooks/stripe")
def stripe_webhook(request: Request, payload: RawBody) -> JSONResponse:
    sv = request.app.state.services
    try:
        event = sv.payments.parse_webhook(payload, request.headers.get("stripe-signature", ""))
    except SignatureError as exc:
        log.warning("webhook rejected: %s", exc)
        raise HTTPException(400, "invalid signature") from None
    return JSONResponse(apply_payment_event(sv, event))


def apply_payment_event(sv, event: PaymentEvent) -> dict:
    """Idempotent: duplicate deliveries of the same payment are no-ops."""
    if event.kind != "paid":
        return {"received": True, "action": "ignored"}
    try:
        with session_scope(sv.sessions) as s:
            mark_paid(
                s,
                sv.cfg,
                event.order_id,
                event.payment_ref,
                amount_cents=event.amount_cents,
                currency=event.currency,
                payment_intent=event.payment_intent,
                strict=True,
            )
    except AlreadyPaid:
        return {"received": True, "action": "already_paid"}  # duplicate delivery: no second receipt
    except DuplicatePayment as exc:
        # the customer paid twice for one order: give the second payment back automatically
        try:
            ref = sv.payments.refund(event.payment_intent, event.amount_cents, f"duplicate:{event.payment_ref}")
        except PaymentError:
            log.exception("PAYMENT NEEDS ATTENTION: duplicate payment %s could not be refunded", event.payment_ref)
            return {"received": True, "action": "needs_attention"}
        log.warning("duplicate payment %s refunded as %s: %s", event.payment_ref, ref, exc)
        return {"received": True, "action": "duplicate_refunded"}
    except OrderError as exc:
        # acknowledged so the provider stops retrying; needs a human (refund or fix)
        log.error("PAYMENT NEEDS ATTENTION: event %s order %s: %s", event.event_id, event.order_id, exc)
        return {"received": True, "action": "needs_attention"}
    try:
        sv.notifier.order_received(event.order_id)
    except Exception:  # the payment is recorded; a missing receipt email must not fail the webhook
        log.exception("order-received email failed for %s", event.order_id)
    return {"received": True, "action": "paid"}


# --------------------------------------------------------------------------- dev-only fake hosted page
@router.get("/dev/pay/{session_id}", response_class=HTMLResponse)
def dev_pay_page(session_id: str, request: Request) -> HTMLResponse:
    sv = request.app.state.services
    if not isinstance(sv.payments, FakeProvider) or sv.cfg.is_prod or session_id not in sv.payments.sessions:
        raise HTTPException(404, "not found")
    req = sv.payments.sessions[session_id]
    return templates.TemplateResponse(
        request, "dev_pay.html", {"sid": session_id, "req": req, "price": f"${req.amount_cents / 100:,.0f}"}
    )


@router.post("/dev/pay/{session_id}")
def dev_pay_submit(session_id: str, request: Request, form: FormData):
    sv = request.app.state.services
    if not isinstance(sv.payments, FakeProvider) or sv.cfg.is_prod or session_id not in sv.payments.sessions:
        raise HTTPException(404, "not found")
    req = sv.payments.sessions[session_id]
    action = form.get("action")
    if action != "pay":
        return RedirectResponse(req.cancel_url, status_code=303)
    payload, sig = sv.payments.signed(sv.payments.event(session_id))
    apply_payment_event(sv, sv.payments.parse_webhook(payload, sig))
    return RedirectResponse(req.success_url, status_code=303)


def _mask(email: str) -> str:
    """f***@example.com — the checkout URL may be shared, the address should not be."""
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}" if domain else "***"
