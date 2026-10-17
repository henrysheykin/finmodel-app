"""Customer pages: sign in by email link, "My models", downloads, sign out."""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select

from app import accounts, links, wizard
from app.db import session_scope
from app.models import Order
from app.web import _label, templates

COOKIE = "sm_session"
DOWNLOAD_TTL = 10 * 60  # account downloads get a fresh, short-lived link per click

SHORT_STATUS = {
    "awaiting_payment": "Waiting for payment",
    "paid": "Queued",
    "building": "Building",
    "checking": "Checking",
    "ready": "Ready",
    "failed": "Delayed — we'll email you",
    "refunded": "Refunded",
}

router = APIRouter()


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else ""


def _set_cookie(resp, token: str, secure: bool) -> None:
    resp.set_cookie(
        COOKIE,
        token,
        max_age=int(accounts.SESSION_TTL.total_seconds()),
        httponly=True,
        secure=secure,
        samesite="lax",
        path="/",
    )


def _customer(request: Request, s):
    return accounts.customer_for(s, request.cookies.get(COOKIE))


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, next: str = "") -> HTMLResponse:
    return templates.TemplateResponse(request, "login.html", {"error": "", "email": ""})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request) -> HTMLResponse:
    sv = request.app.state.services
    form = await request.form()
    email = str(form.get("email", ""))
    try:
        with session_scope(sv.sessions) as s:
            token = accounts.request_login(s, email, _client_ip(request))
            norm = accounts.normalise_email(email)
    except accounts.LoginError as exc:
        return templates.TemplateResponse(request, "login.html", {"error": str(exc), "email": email}, status_code=422)
    if token:
        sv.notifier.login_link(norm, f"{sv.cfg.public_base_url}/login/verify?token={token}")
    # same answer whether or not the address has orders, and whether or not it was rate-limited
    return templates.TemplateResponse(
        request,
        "message.html",
        {
            "heading": "Check your email",
            "text": f"If {norm} can sign in, a link is on its way. It works once and expires in 15 minutes.",
            "link": None,
        },
    )


@router.get("/login/verify", response_class=HTMLResponse)
def verify_page(request: Request, token: str = "") -> HTMLResponse:
    """A confirm button, not an automatic sign-in: mail scanners that open links must not use up the token."""
    return templates.TemplateResponse(request, "login_confirm.html", {"token": token})


@router.post("/login/verify")
async def verify_submit(request: Request):
    sv = request.app.state.services
    token = str((await request.form()).get("token", ""))
    try:
        with session_scope(sv.sessions) as s:
            new = accounts.consume_login(s, token, request.headers.get("user-agent", ""))
    except accounts.LoginError as exc:
        return templates.TemplateResponse(
            request,
            "message.html",
            {
                "heading": "Sign-in link not valid",
                "text": f"{str(exc).capitalize()}.",
                "link": ("/login", "Get a new link"),
            },
            status_code=400,
        )
    resp = RedirectResponse("/account", status_code=303)
    _set_cookie(resp, new.token, secure=sv.cfg.is_prod)
    return resp


@router.get("/account", response_class=HTMLResponse)
def account(request: Request):
    sv = request.app.state.services
    with session_scope(sv.sessions) as s:
        customer = _customer(request, s)
        if customer is None:
            return RedirectResponse("/login", status_code=303)
        orders = s.scalars(
            select(Order)
            .where(Order.email == customer.email, Order.status != "draft")
            .order_by(Order.created_at.desc())
            .limit(200)
        ).all()
        rows = []
        for o in orders:
            a = json.loads(o.answers_json or "{}")
            rows.append(
                {
                    "id": o.id,
                    "name": a.get("business_name") or _label(wizard.BUSINESS_TYPES, a.get("business_type", "")),
                    "plan": wizard.PLANS.get(o.tier, {}).get("name", o.tier),
                    "date": o.created_at.strftime("%d %b %Y"),
                    "status": o.status,
                    "label": SHORT_STATUS.get(o.status, o.status),
                    "ready": o.status == "ready" and o.artifact("model_xlsx") is not None,
                }
            )
        email = customer.email
    return templates.TemplateResponse(request, "account.html", {"email": email, "orders": rows})


@router.get("/account/orders/{order_id}/download")
def account_download(order_id: str, request: Request):
    sv = request.app.state.services
    with session_scope(sv.sessions) as s:
        customer = _customer(request, s)
        if customer is None:
            return RedirectResponse("/login", status_code=303)
        order = s.get(Order, order_id)
        # another customer's order and a missing order look the same
        if order is None or order.email != customer.email or order.status != "ready":
            raise HTTPException(404, "not found")
        art = order.artifact("model_xlsx")
        if art is None:
            raise HTTPException(404, "not found")
        token = links.sign(sv.cfg.secret_key, art.id, DOWNLOAD_TTL)
    return RedirectResponse(f"/download/{token}", status_code=303)


@router.post("/logout")
def logout(request: Request):
    sv = request.app.state.services
    with session_scope(sv.sessions) as s:
        accounts.revoke(s, request.cookies.get(COOKIE))
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie(COOKIE, path="/")
    return resp


@router.post("/account/sign-out-everywhere")
def sign_out_everywhere(request: Request):
    sv = request.app.state.services
    with session_scope(sv.sessions) as s:
        customer = _customer(request, s)
        if customer is not None:
            accounts.revoke_all(s, customer.id)
    resp = RedirectResponse("/login", status_code=303)
    resp.delete_cookie(COOKIE, path="/")
    return resp
