"""Customer accounts: magic-link sign-in, My models, downloads, sign-out (ADR-006)."""

from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from sqlalchemy import select

from app import accounts
from app.account_web import COOKIE
from app.db import session_scope, utcnow
from app.models import CustomerSession, LoginToken, Order
from app.orders import mark_paid
from tests.conftest import ANSWERS
from tests.test_pipeline import make


def _token(notifier, i=-1):
    return parse_qs(urlparse(notifier.logins[i][1]).query)["token"][0]


def sign_in(client, notifier, email="buyer@example.com"):
    r = client.post("/login", data={"email": email})
    assert r.status_code == 200 and "Check your email" in r.text
    tok = _token(notifier)
    page = client.get(f"/login/verify?token={tok}")
    assert page.status_code == 200 and 'value="' + tok + '"' in page.text  # confirm page, not consumed
    r = client.post("/login/verify", data={"token": tok}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/account"
    return r


def ready_order(client, services, notifier, email="buyer@example.com", name="Acme Advisory"):
    r = client.post("/api/orders", json={"email": email, "answers": {**ANSWERS, "business_name": name}})
    oid = r.json()["order_id"]
    with session_scope(services.sessions) as s:
        mark_paid(s, services.cfg, oid, f"cs_{oid}")
    make(services, notifier).run_once()
    return oid


def test_sign_in_see_models_and_download(client, services, notifier):
    oid = ready_order(client, services, notifier)
    pending = client.post("/api/orders", json={"email": "BUYER@example.com", "answers": ANSWERS}).json()["order_id"]
    r = sign_in(client, notifier, " Buyer@Example.com ")
    cookie = r.headers["set-cookie"]
    assert f"{COOKIE}=" in cookie and "HttpOnly" in cookie and "samesite=lax" in cookie.lower()
    assert "Secure" not in cookie  # dev over http; prod sets Secure (test below)
    page = client.get("/account")
    assert page.status_code == 200 and "buyer@example.com" in page.text and "Acme Advisory" in page.text
    assert f"/account/orders/{oid}/download" in page.text and f"/checkout/{pending}" in page.text
    d = client.get(f"/account/orders/{oid}/download", follow_redirects=False)
    assert d.status_code == 303 and d.headers["location"].startswith("/download/")
    f = client.get(d.headers["location"])
    assert f.status_code == 200 and f.content.startswith(b"PK-fake")


def test_same_answer_for_unknown_email_and_bad_input(client, notifier):
    a = client.post("/login", data={"email": "nobody@example.com"})
    assert a.status_code == 200 and "If nobody@example.com can sign in" in a.text
    r = client.post("/login", data={"email": "not-an-email"})
    assert r.status_code == 422 and "valid email" in r.text


@pytest.mark.parametrize("problem", ["reused", "expired", "garbage", "empty"])
def test_bad_tokens(client, services, notifier, problem):
    client.post("/login", data={"email": "a@example.com"})
    tok = _token(notifier)
    if problem == "reused":
        client.post("/login/verify", data={"token": tok})
        client.cookies.clear()
    if problem == "expired":
        with session_scope(services.sessions) as s:
            s.query(LoginToken).update({"expires_at": utcnow() - timedelta(seconds=1)})
    tok = {"garbage": "x" * 43, "empty": ""}.get(problem, tok)
    r = client.post("/login/verify", data={"token": tok}, follow_redirects=False)
    assert r.status_code == 400 and "Get a new link" in r.text
    assert COOKIE not in r.headers.get("set-cookie", "")


def test_only_hashes_are_stored(client, services, notifier):
    sign_in(client, notifier)
    tok = _token(notifier)
    cookie = client.cookies.get(COOKIE)
    with session_scope(services.sessions) as s:
        hashes = [t.token_hash for t in s.scalars(select(LoginToken))] + [
            x.token_hash for x in s.scalars(select(CustomerSession))
        ]
    assert tok not in hashes and cookie not in hashes and all(len(h) == 64 for h in hashes)


def test_rate_limit_per_email_and_ip(client, notifier):
    for _ in range(accounts.MAX_PER_EMAIL + 2):
        r = client.post("/login", data={"email": "spam@example.com"})
        assert r.status_code == 200 and "Check your email" in r.text  # no enumeration, no error
    assert len(notifier.logins) == accounts.MAX_PER_EMAIL
    for i in range(accounts.MAX_PER_IP):
        client.post("/login", data={"email": f"user{i}@example.com"})
    assert len(notifier.logins) == accounts.MAX_PER_IP  # the IP budget is spent (5 + 15 others)


def test_other_customers_orders_are_invisible(client, services, notifier):
    theirs = ready_order(client, services, notifier, email="other@example.com", name="Secret Co")
    mine = client.post("/api/orders", json={"email": "me@example.com", "answers": ANSWERS}).json()["order_id"]
    sign_in(client, notifier, "me@example.com")
    page = client.get("/account").text
    assert "Secret Co" not in page and theirs not in page
    assert client.get(f"/account/orders/{theirs}/download", follow_redirects=False).status_code == 404
    assert client.get(f"/account/orders/{mine}/download", follow_redirects=False).status_code == 404  # not ready
    assert client.get("/account/orders/nope/download", follow_redirects=False).status_code == 404


def test_anonymous_is_sent_to_login(client):
    assert client.get("/account", follow_redirects=False).headers["location"] == "/login"
    assert client.get("/account/orders/x/download", follow_redirects=False).headers["location"] == "/login"
    client.cookies.set(COOKIE, "forged")
    assert client.get("/account", follow_redirects=False).status_code == 303


def test_logout_and_sign_out_everywhere(client, services, notifier):
    sign_in(client, notifier)
    first = client.cookies.get(COOKIE)
    client.cookies.clear()
    sign_in(client, notifier)  # second device
    second = client.cookies.get(COOKIE)
    client.post("/logout")
    client.cookies.set(COOKIE, second)
    assert client.get("/account", follow_redirects=False).status_code == 303  # this session is gone
    client.cookies.set(COOKIE, first)
    assert client.get("/account").status_code == 200  # the other device still works
    client.post("/account/sign-out-everywhere")
    client.cookies.set(COOKIE, first)
    assert client.get("/account", follow_redirects=False).status_code == 303


def test_session_expiry(client, services, notifier):
    sign_in(client, notifier)
    with session_scope(services.sessions) as s:
        s.query(CustomerSession).update({"expires_at": utcnow() - timedelta(seconds=1)})
    assert client.get("/account", follow_redirects=False).status_code == 303


def test_secure_cookie_in_production(client, services, notifier):
    from dataclasses import replace

    client.post("/login", data={"email": "a@example.com"})
    services.cfg = replace(services.cfg, app_env="prod", payment_provider="stripe")
    r = client.post("/login/verify", data={"token": _token(notifier)}, follow_redirects=False)
    assert "Secure" in r.headers["set-cookie"]


def test_guest_link_still_works_without_signing_in(client, services, notifier):
    ready_order(client, services, notifier)
    link = notifier.ready[-1][2].replace("http://testserver", "")
    assert client.get(link).status_code == 200


def test_orders_are_listed_newest_first(client, services, notifier):
    a = ready_order(client, services, notifier, name="Older")
    b = ready_order(client, services, notifier, name="Newer")
    with session_scope(services.sessions) as s:
        s.get(Order, a).created_at = utcnow() - timedelta(days=2)
    sign_in(client, notifier)
    page = client.get("/account").text
    assert page.index("Newer") < page.index("Older") and b in page
