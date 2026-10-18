"""Admin panel: orders, details, re-build, refund, re-send, download, counters.

Access: ADMIN_USER / ADMIN_PASSWORD from the environment (admin is disabled when unset).
The session is a signed, expiring cookie scoped to /admin (SameSite=Strict); every POST
also carries a CSRF token derived from it. Failed logins are rate-limited per IP.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from collections import defaultdict, deque
from datetime import timedelta
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy import func, select

from adapters.payments import PaymentError
from app import __version__, golive, links, ratelimit
from app.db import session_scope, utcnow
from app.models import Job, Order
from app.orders import OrderError, rebuild, refund_order
from app.web import STATUS_LABEL, FormData, templates

log = logging.getLogger("admin")
COOKIE = "sm_admin"
SESSION_SECONDS = 12 * 3600
MAX_FAILS, FAIL_WINDOW = 5, 15 * 60
#: failed logins from all addresses together per window: bounds password guessing even when the
#: attacker rotates addresses (E17); the owner may wait a few minutes during an attack
MAX_FAILS_GLOBAL = 50
ALL = "*"
PAGE = 50
PAID_STATUSES = ("paid", "building", "checking", "ready", "failed")

router = APIRouter(prefix="/admin")
_fails: dict[str, deque] = defaultdict(deque)  # per-process; one web process in this deployment


def _mac(secret: str, msg: str) -> str:
    return hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()


def _cfg(request: Request):
    cfg = request.app.state.services.cfg
    if not (cfg.admin_user and cfg.admin_password):
        raise HTTPException(404, "not found")  # admin disabled
    return cfg


def _session_ok(request: Request) -> str | None:
    cfg = _cfg(request)
    raw = request.cookies.get(COOKIE, "")
    try:
        exp_s, sig = raw.split(".")
        exp = int(exp_s)
    except ValueError:
        return None
    if exp < time.time() or not hmac.compare_digest(sig, _mac(cfg.secret_key, f"admin:{cfg.admin_user}:{exp}")):
        return None
    return raw


def _csrf(request: Request, cookie: str) -> str:
    return _mac(_cfg(request).secret_key, f"csrf:{cookie}")


def _require(request: Request) -> str:
    cookie = _session_ok(request)
    if cookie is None:
        raise HTTPException(303, headers={"Location": "/admin/login"})
    return cookie


def _require_post(request: Request, form: dict) -> dict:
    cookie = _require(request)
    if not hmac.compare_digest(str(form.get("csrf", "")), _csrf(request, cookie)):
        raise HTTPException(403, "bad csrf token")
    return form


def _ip(request: Request) -> str:
    return ratelimit.client_ip(request)


def _recent(key: str, now: float) -> deque:
    q = _fails[key]
    while q and q[0] < now - FAIL_WINDOW:
        q.popleft()
    return q


# --------------------------------------------------------------------------- auth
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    _cfg(request)
    return templates.TemplateResponse(request, "admin/login.html", {"error": ""})


@router.post("/login")
def login(request: Request, form: FormData):
    cfg = _cfg(request)
    ip, now = _ip(request), time.time()
    q, everyone = _recent(ip, now), _recent(ALL, now)
    if len(q) >= MAX_FAILS or len(everyone) >= MAX_FAILS_GLOBAL:
        return templates.TemplateResponse(
            request, "admin/login.html", {"error": "Too many attempts. Try again later."}, status_code=429
        )
    user_ok = hmac.compare_digest(str(form.get("user", "")).encode(), cfg.admin_user.encode())
    pass_ok = hmac.compare_digest(str(form.get("password", "")).encode(), cfg.admin_password.encode())
    if not (user_ok and pass_ok):
        q.append(now)
        everyone.append(now)
        log.warning("admin login failed from %s", ip)
        return templates.TemplateResponse(
            request, "admin/login.html", {"error": "Wrong user or password."}, status_code=401
        )
    q.clear()
    exp = int(now) + SESSION_SECONDS
    resp = RedirectResponse("/admin", status_code=303)
    resp.set_cookie(
        COOKIE,
        f"{exp}.{_mac(cfg.secret_key, f'admin:{cfg.admin_user}:{exp}')}",
        max_age=SESSION_SECONDS,
        httponly=True,
        secure=cfg.is_prod,
        samesite="strict",
        path="/admin",
    )
    return resp


@router.post("/logout")
def logout(request: Request, form: FormData):
    _require_post(request, form)
    resp = RedirectResponse("/admin/login", status_code=303)
    resp.delete_cookie(COOKIE, path="/admin")
    return resp


# --------------------------------------------------------------------------- pages
@router.get("", response_class=HTMLResponse)
def orders(request: Request, status: str = "", q: str = "", page: int = 1) -> HTMLResponse:
    cookie = _require(request)
    sv = request.app.state.services
    page = max(1, page)
    with session_scope(sv.sessions) as s:
        stmt = select(Order).where(Order.status != "draft")
        if status:
            stmt = stmt.where(Order.status == status)
        if q.strip():
            needle = q.strip().lower()
            stmt = stmt.where((Order.email.contains(needle)) | (Order.id.startswith(needle)))
        total = s.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = s.scalars(stmt.order_by(Order.created_at.desc()).offset((page - 1) * PAGE).limit(PAGE)).all()
        items = [
            {
                "id": o.id,
                "short": o.id[:8],
                "email": o.email,
                "template": o.template,
                "tier": o.tier,
                "status": o.status,
                "price": f"${o.price_cents / 100:,.0f}",
                "created": o.created_at.strftime("%Y-%m-%d %H:%M"),
            }
            for o in rows
        ]
        counters = _counters(s)
    return templates.TemplateResponse(
        request,
        "admin/orders.html",
        {
            "items": items,
            "total": total,
            "page": page,
            "pages": max(1, -(-total // PAGE)),
            "status": status,
            "q": q,
            "statuses": list(STATUS_LABEL) + ["refunded"],
            "c": counters,
            "readiness": [i for i in golive.readiness(sv.cfg) if i.level != golive.OK],
            "version": __version__,
            "csrf": _csrf(request, cookie),
        },
    )


def _counters(s) -> dict:
    def paid_since(days: int | None):
        stmt = select(func.count(), func.coalesce(func.sum(Order.price_cents), 0)).where(
            Order.status.in_(PAID_STATUSES)
        )
        if days is not None:
            stmt = stmt.where(
                Order.paid_at >= utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
            )
        n, cents = s.execute(stmt).one()
        return n, f"${cents / 100:,.0f}"

    by_status = dict(s.execute(select(Order.status, func.count()).group_by(Order.status)).all())
    return {
        "today": paid_since(0),
        "week": paid_since(6),
        "all": paid_since(None),
        "refunded": by_status.get("refunded", 0),
        "awaiting": by_status.get("awaiting_payment", 0),
        "failed": by_status.get("failed", 0),
        "queued_jobs": s.scalar(select(func.count()).where(Job.status.in_(("queued", "running")))),
    }


@router.get("/orders/{order_id}", response_class=HTMLResponse)
def order_detail(order_id: str, request: Request, msg: str = "") -> HTMLResponse:
    cookie = _require(request)
    sv = request.app.state.services
    with session_scope(sv.sessions) as s:
        o = s.get(Order, order_id)
        if o is None:
            raise HTTPException(404, "order not found")
        report = o.artifact("check_report")
        report_txt = sv.storage.get(report.storage_key).decode() if report else ""
        d = {
            "id": o.id,
            "email": o.email,
            "status": o.status,
            "template": o.template,
            "tier": o.tier,
            "price": f"${o.price_cents / 100:,.0f}",
            "payment_ref": o.payment_ref or "—",
            "refund_ref": o.refund_ref or "—",
            "failure": o.failure_reason or "",
            "created": o.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "paid": o.paid_at.strftime("%Y-%m-%d %H:%M:%S") if o.paid_at else "—",
            "ready": o.ready_at.strftime("%Y-%m-%d %H:%M:%S") if o.ready_at else "—",
            "brief": json.dumps(json.loads(o.brief_json), indent=2),
            "answers": json.dumps(json.loads(o.answers_json or "{}"), indent=2),
            "report": report_txt,
            "events": [(e.created_at.strftime("%m-%d %H:%M:%S"), e.from_status, e.to_status, e.note) for e in o.events],
            "jobs": [(j.id, j.status, j.attempts, j.max_attempts, (j.last_error or "")[:300]) for j in o.jobs],
            "has_model": o.artifact("model_xlsx") is not None,
            "can_rebuild": o.status in ("ready", "failed"),
            "can_refund": o.status in ("paid", "ready", "failed"),
            "can_resend": o.status == "ready" and o.artifact("model_xlsx") is not None,
        }
    return templates.TemplateResponse(request, "admin/order.html", {"o": d, "msg": msg, "csrf": _csrf(request, cookie)})


def _back(order_id: str, msg: str) -> RedirectResponse:
    return RedirectResponse(f"/admin/orders/{order_id}?msg={quote(msg)}", status_code=303)


@router.post("/orders/{order_id}/rebuild")
def do_rebuild(order_id: str, request: Request, form: FormData):
    _require_post(request, form)
    sv = request.app.state.services
    try:
        with session_scope(sv.sessions) as s:
            o = s.get(Order, order_id)
            if o is None:
                raise HTTPException(404, "order not found")
            rebuild(s, sv.cfg, o, "admin re-build")
    except (OrderError, ValueError) as exc:
        return _back(order_id, f"Re-build refused: {exc}")
    log.info("admin re-build queued for %s", order_id)
    return _back(order_id, "Re-build queued.")


@router.post("/orders/{order_id}/refund")
def do_refund(order_id: str, request: Request, form: FormData):
    _require_post(request, form)
    if form.get("confirm") != "yes":
        return _back(order_id, "Tick the confirmation box to refund.")
    sv = request.app.state.services
    try:
        with session_scope(sv.sessions) as s:
            o = s.get(Order, order_id)
            if o is None:
                raise HTTPException(404, "order not found")
            ref = refund_order(s, sv.payments, o, "admin refund")
    except (OrderError, PaymentError) as exc:
        return _back(order_id, f"Refund failed: {exc}")
    try:
        sv.notifier.refund_issued(order_id)
    except Exception:
        log.exception("refund email failed for %s", order_id)
        return _back(order_id, f"Refunded ({ref}); the email to the customer failed — see logs.")
    log.info("admin refund %s for %s", ref, order_id)
    return _back(order_id, f"Refunded ({ref}). Customer emailed.")


@router.post("/orders/{order_id}/resend")
def do_resend(order_id: str, request: Request, form: FormData):
    _require_post(request, form)
    sv = request.app.state.services
    with session_scope(sv.sessions) as s:
        o = s.get(Order, order_id)
        if o is None:
            raise HTTPException(404, "order not found")
        art = o.artifact("model_xlsx")
        if o.status != "ready" or art is None:
            return _back(order_id, "Only ready orders can be re-sent.")
        email, art_id = o.email, art.id
    url = f"{sv.cfg.public_base_url}/download/{links.sign(sv.cfg.secret_key, art_id, sv.cfg.link_ttl_seconds)}"
    try:
        sv.notifier.model_ready(email, order_id, url)
    except Exception as exc:
        return _back(order_id, f"Re-send failed: {type(exc).__name__}")
    return _back(order_id, f"Download email re-sent to {email}.")


@router.get("/orders/{order_id}/download")
def admin_download(order_id: str, request: Request) -> Response:
    _require(request)
    sv = request.app.state.services
    with session_scope(sv.sessions) as s:
        o = s.get(Order, order_id)
        art = o.artifact("model_xlsx") if o else None
        if art is None:
            raise HTTPException(404, "no model file for this order")
        key, name, ctype = art.storage_key, art.filename, art.content_type
    return Response(
        sv.storage.get(key),
        media_type=ctype,
        headers={"Content-Disposition": f'attachment; filename="{name}"', "Cache-Control": "private, no-store"},
    )
