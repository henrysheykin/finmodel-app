"""E17 hardening: security headers, cross-site POST refusal, one client-address rule for every limit."""

import re
from dataclasses import replace
from pathlib import Path

import pytest

from app import accounts, admin
from app.main import CSP
from tests.conftest import ANSWERS

TEMPLATES = Path(__file__).resolve().parents[1] / "app" / "templates"
BASE = "http://testserver"
EVIL = "https://evil.example"


# --------------------------------------------------------------------------- headers
@pytest.mark.parametrize("path", ["/", "/start", "/login", "/healthz", "/static/app.css"])
def test_every_response_carries_the_security_headers(client, path):
    r = client.get(path)
    assert r.status_code == 200
    assert r.headers["content-security-policy"] == CSP
    assert r.headers["x-frame-options"] == "DENY"
    assert r.headers["x-content-type-options"] == "nosniff"


def test_csp_allows_no_inline_or_foreign_script():
    script_src = next(d for d in CSP.split(";") if d.strip().startswith("script-src")).split()[1:]
    assert script_src == ["'self'"]
    assert "frame-ancestors 'none'" in CSP and "object-src 'none'" in CSP


def test_templates_have_no_executable_inline_script():
    """Inline scripts would be blocked by the CSP: only src= scripts and JSON data blocks are allowed."""
    for f in TEMPLATES.rglob("*.html"):
        for tag in re.findall(r"<script\b[^>]*>", f.read_text()):
            assert "src=" in tag or re.search(r'type="application/(ld\+)?json"', tag), f"{f.name}: {tag}"
        assert not re.search(r"\son[a-z]+=", f.read_text()), f"{f.name}: inline event handler"


# --------------------------------------------------------------------------- cross-site POSTs
@pytest.mark.parametrize(
    "path,data",
    [
        ("/login", {"email": "victim@example.com"}),
        ("/login/verify", {"token": "attacker-token"}),
        ("/logout", {}),
        ("/account/sign-out-everywhere", {}),
        ("/start", {"business_type": "professional_services", "email": "a@b.co"}),
        ("/checkout/some-order/pay", {}),
        ("/admin/login", {"user": "x", "password": "y"}),
    ],
)
def test_cross_site_form_posts_are_refused(client, notifier, path, data):
    r = client.post(path, data=data, headers={"Origin": EVIL}, follow_redirects=False)
    assert r.status_code == 403 and "cross-site" in r.text
    assert r.headers["content-security-policy"] == CSP
    assert notifier.logins == []


def test_cross_site_json_order_is_refused(client):
    r = client.post("/api/orders", json={"email": "a@b.co", "answers": ANSWERS}, headers={"Origin": "null"})
    assert r.status_code == 403


def test_same_origin_and_originless_posts_pass(client, notifier):
    assert client.post("/login", data={"email": "a@example.com"}, headers={"Origin": BASE}).status_code == 200
    assert client.post("/login", data={"email": "b@example.com"}).status_code == 200  # API clients, old browsers
    assert len(notifier.logins) == 2


def test_own_host_counts_as_same_origin_even_if_base_url_differs(client, services):
    services.cfg = replace(services.cfg, public_base_url="https://startup-model.com")
    r = client.post("/login", data={"email": "a@example.com"}, headers={"Origin": "http://testserver"})
    assert r.status_code == 200
    r = client.post("/login", data={"email": "a@example.com"}, headers={"Origin": "https://startup-model.com"})
    assert r.status_code == 200


def test_webhooks_are_exempt_and_still_need_a_signature(client):
    r = client.post("/webhooks/stripe", content=b"{}", headers={"Origin": EVIL, "Stripe-Signature": "t=1,v1=00"})
    assert r.status_code == 400  # reached the handler; the signature check refused it


def test_safe_methods_are_not_checked(client):
    assert client.get("/start", headers={"Origin": EVIL}).status_code == 200


# --------------------------------------------------------------------------- client address
def test_magic_link_limit_uses_the_configured_client_header(client, services, notifier):
    services.cfg = replace(services.cfg, client_ip_header="X-Real-IP")
    for i in range(accounts.MAX_PER_IP):
        client.post("/login", data={"email": f"u{i}@example.com"}, headers={"X-Real-IP": "203.0.113.7"})
    assert len(notifier.logins) == accounts.MAX_PER_IP
    client.post("/login", data={"email": "late@example.com"}, headers={"X-Real-IP": "203.0.113.7"})
    assert len(notifier.logins) == accounts.MAX_PER_IP  # this visitor's budget is spent
    client.post("/login", data={"email": "other@example.com"}, headers={"X-Real-IP": "203.0.113.8"})
    assert notifier.logins[-1][0] == "other@example.com"  # another visitor is not affected


@pytest.fixture
def admin_on(services):
    admin._fails.clear()
    services.cfg = replace(
        services.cfg, admin_user="henry", admin_password="correct horse battery", client_ip_header="X-Real-IP"
    )
    yield services
    admin._fails.clear()


def test_admin_login_limit_follows_the_client_header(client, admin_on):
    def attempt(ip):
        return client.post(
            "/admin/login", data={"user": "henry", "password": "wrong"}, headers={"X-Real-IP": ip}
        ).status_code

    assert [attempt("198.51.100.1") for _ in range(admin.MAX_FAILS)] == [401] * admin.MAX_FAILS
    assert attempt("198.51.100.1") == 429
    assert attempt("198.51.100.2") == 401


def test_admin_guessing_from_many_addresses_hits_the_global_cap(client, admin_on):
    for i in range(admin.MAX_FAILS_GLOBAL):
        r = client.post(
            "/admin/login", data={"user": "henry", "password": f"guess{i}"}, headers={"X-Real-IP": f"10.0.{i}.1"}
        )
        assert r.status_code == 401
    r = client.post(
        "/admin/login", data={"user": "henry", "password": "correct horse battery"}, headers={"X-Real-IP": "10.9.9.9"}
    )
    assert r.status_code == 429  # even the right password waits out the window during an attack


# --------------------------------------------------------------------------- logs
def test_access_log_hides_sign_in_and_download_tokens():
    import logging

    from app.logs import RedactSecrets, redact

    assert redact("GET /login/verify?token=abc_DEF-123 HTTP/1.1") == "GET /login/verify?token=[redacted] HTTP/1.1"
    assert redact("/download/42.1700000000.c2lnbmF0dXJl") == "/download/[redacted]"
    assert redact("/start?plan=full&type=saas") == "/start?plan=full&type=saas"
    rec = logging.LogRecord(
        "uvicorn.access",
        logging.INFO,
        "",
        0,
        '%s - "%s %s HTTP/%s" %d',
        ("1.2.3.4:5", "GET", "/login/verify?x=1&token=SECRET", "1.1", 200),
        None,
    )
    assert RedactSecrets().filter(rec) and "SECRET" not in rec.getMessage()


def test_oversized_bodies_are_refused_before_parsing(client):
    from app.main import MAX_BODY_BYTES

    big = b"x" * (MAX_BODY_BYTES + 1)
    assert client.post("/webhooks/stripe", content=big).status_code == 413
    assert (
        client.post("/login", content=big, headers={"Content-Type": "application/x-www-form-urlencoded"}).status_code
        == 413
    )
