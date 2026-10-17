"""E14 admin panel: auth (env credentials, rate limit, signed cookie, CSRF) and every action."""

import re
import time
from dataclasses import replace

import pytest

from app import admin
from app.config import Settings
from app.db import session_scope
from app.models import Job, Order
from app.orders import mark_paid
from tests.conftest import ANSWERS
from tests.test_pipeline import make

USER, PASSWORD = "henry", "correct horse battery"


@pytest.fixture
def admin_on(services):
    admin._fails.clear()
    services.cfg = replace(services.cfg, admin_user=USER, admin_password=PASSWORD)
    yield services
    admin._fails.clear()


def login(client, user=USER, password=PASSWORD):
    return client.post("/admin/login", data={"user": user, "password": password}, follow_redirects=False)


def csrf(client, path="/admin"):
    return re.search(r'name="csrf" value="([0-9a-f]+)"', client.get(path).text).group(1)


def order(client, services, notifier, email="a@b.co", build=True, ref=None):
    oid = client.post("/api/orders", json={"email": email, "answers": ANSWERS}).json()["order_id"]
    if build:
        with session_scope(services.sessions) as s:
            mark_paid(s, services.cfg, oid, ref or f"cs_{oid}")
            s.get(Order, oid).payment_intent = f"pi_{oid}"
        make(services, notifier).run_once()
    return oid


# --------------------------------------------------------------------------- auth
def test_admin_is_disabled_without_credentials(client):
    assert client.get("/admin/login").status_code == 404
    assert client.get("/admin").status_code == 404


def test_weak_admin_password_is_refused():
    with pytest.raises(RuntimeError, match="12 characters"):
        Settings(admin_user="a", admin_password="short").check()


def test_anonymous_is_redirected(client, admin_on):
    for path in ("/admin", "/admin/orders/x", "/admin/orders/x/download"):
        r = client.get(path, follow_redirects=False)
        assert r.status_code == 303 and r.headers["location"] == "/admin/login"
    assert client.post("/admin/orders/x/refund", data={"csrf": "x"}, follow_redirects=False).status_code == 303


def test_login_cookie_and_logout(client, admin_on):
    r = login(client)
    assert r.status_code == 303 and r.headers["location"] == "/admin"
    cookie = r.headers["set-cookie"]
    assert "HttpOnly" in cookie and "samesite=strict" in cookie.lower() and "Path=/admin" in cookie
    assert client.get("/admin").status_code == 200
    client.post("/admin/logout", data={"csrf": csrf(client)})
    assert client.get("/admin", follow_redirects=False).status_code == 303


def test_wrong_password_and_rate_limit(client, admin_on):
    assert login(client, password="nope").status_code == 401
    assert login(client, user="root").status_code == 401
    for _ in range(3):
        login(client, password="nope")
    r = login(client)  # right password, but 5 failures already
    assert r.status_code == 429 and "Too many attempts" in r.text
    admin._fails.clear()
    assert login(client).status_code == 303


@pytest.mark.parametrize("forge", ["garbage", "9999999999.deadbeef", "expired"])
def test_forged_or_expired_cookie(client, admin_on, forge):
    if forge == "expired":
        exp = int(time.time()) - 1
        forge = f"{exp}.{admin._mac(admin_on.cfg.secret_key, f'admin:{USER}:{exp}')}"
    client.cookies.set(admin.COOKIE, forge, path="/admin")
    assert client.get("/admin", follow_redirects=False).status_code == 303


def test_actions_need_csrf(client, admin_on, notifier):
    oid = order(client, admin_on, notifier)
    login(client)
    for action in ("rebuild", "refund", "resend"):
        r = client.post(f"/admin/orders/{oid}/{action}", data={"confirm": "yes"})
        assert r.status_code == 403
    assert client.post("/admin/logout").status_code == 403
    with session_scope(admin_on.sessions) as s:
        assert s.get(Order, oid).status == "ready"


# --------------------------------------------------------------------------- pages
def test_list_filters_and_counters(client, admin_on, notifier):
    a = order(client, admin_on, notifier, email="alice@example.com")
    b = order(client, admin_on, notifier, email="bob@example.com")
    order(client, admin_on, notifier, email="carol@example.com", build=False)
    login(client)
    page = client.get("/admin").text
    assert a[:8] in page and b[:8] in page and "carol@example.com" in page
    assert "Paid, all time (excl. refunded)</dt><dd>2 · $298" in page and "Awaiting payment</dt><dd>1" in page
    only_ready = client.get("/admin?status=awaiting_payment").text
    assert "carol@example.com" in only_ready and "alice@example.com" not in only_ready
    search = client.get("/admin?q=BOB").text
    assert "bob@example.com" in search and "alice@example.com" not in search
    assert a[:8] in client.get(f"/admin?q={a[:6]}").text


def test_order_detail_shows_brief_report_and_timeline(client, admin_on, notifier):
    oid = order(client, admin_on, notifier)
    login(client)
    page = client.get(f"/admin/orders/{oid}").text
    assert "&#34;template&#34;: &#34;services&#34;" in page and "&#34;verdict&#34;: &#34;PASS&#34;" in page
    assert "checking → ready" in page and "Re-send download email" in page and "Refund $149 in full" in page
    assert client.get("/admin/orders/nope").status_code == 404


# --------------------------------------------------------------------------- actions
def test_rebuild(client, admin_on, notifier):
    oid = order(client, admin_on, notifier)
    pending = order(client, admin_on, notifier, build=False)
    login(client)
    token = csrf(client)
    r = client.post(f"/admin/orders/{oid}/rebuild", data={"csrf": token}, follow_redirects=False)
    assert "Re-build%20queued" in r.headers["location"]
    with session_scope(admin_on.sessions) as s:
        assert s.get(Order, oid).status == "paid"
        assert s.query(Job).filter_by(order_id=oid, status="queued").count() == 1
    make(admin_on, notifier).run_once()
    with session_scope(admin_on.sessions) as s:
        assert s.get(Order, oid).status == "ready"
    r = client.post(f"/admin/orders/{pending}/rebuild", data={"csrf": token}, follow_redirects=False)
    assert "refused" in r.headers["location"]


def test_refund_needs_confirmation_then_refunds_and_emails(client, admin_on, notifier):
    oid = order(client, admin_on, notifier)
    login(client)
    token = csrf(client)
    r = client.post(f"/admin/orders/{oid}/refund", data={"csrf": token}, follow_redirects=False)
    assert "confirmation" in r.headers["location"]
    r = client.post(f"/admin/orders/{oid}/refund", data={"csrf": token, "confirm": "yes"}, follow_redirects=False)
    assert "Refunded" in r.headers["location"]
    with session_scope(admin_on.sessions) as s:
        assert s.get(Order, oid).status == "refunded"
    assert ("refund_issued", oid) in notifier.events
    assert admin_on.payments.refunds == [(f"pi_{oid}", 14900, f"refund:{oid}")]
    # a refunded order no longer downloads for the customer
    link = notifier.ready[-1][2].replace("http://testserver", "")
    assert client.get(link).status_code == 404


def test_refund_unpaid_order_is_refused(client, admin_on, notifier):
    oid = order(client, admin_on, notifier, build=False)
    login(client)
    r = client.post(
        f"/admin/orders/{oid}/refund", data={"csrf": csrf(client), "confirm": "yes"}, follow_redirects=False
    )
    assert "Refund%20failed" in r.headers["location"]


def test_resend_and_download(client, admin_on, notifier):
    oid = order(client, admin_on, notifier)
    pending = order(client, admin_on, notifier, build=False)
    login(client)
    token = csrf(client)
    before = len(notifier.ready)
    r = client.post(f"/admin/orders/{oid}/resend", data={"csrf": token}, follow_redirects=False)
    assert "re-sent" in r.headers["location"] and len(notifier.ready) == before + 1
    assert client.get(notifier.ready[-1][2].replace("http://testserver", "")).status_code == 200
    r = client.post(f"/admin/orders/{pending}/resend", data={"csrf": token}, follow_redirects=False)
    assert "Only%20ready" in r.headers["location"]
    d = client.get(f"/admin/orders/{oid}/download")
    assert d.status_code == 200 and d.content.startswith(b"PK-fake")
    assert client.get(f"/admin/orders/{pending}/download").status_code == 404
