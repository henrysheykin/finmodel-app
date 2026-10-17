"""Per-IP rate limits on the public endpoints that create work (E15)."""

from dataclasses import replace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.config import Settings, load_settings
from app.db import session_scope
from app.main import create_app
from app.models import Order
from app.ratelimit import RateLimiter
from tests.conftest import ANSWERS
from tests.test_web import FORM


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


# --------------------------------------------------------------------------- limiter
def test_sliding_window_and_retry_after():
    clock = Clock()
    rl = RateLimiter(3, window=60, clock=clock)
    assert [rl.hit("orders", "1.2.3.4") for _ in range(3)] == [0, 0, 0]
    clock.t += 10
    assert rl.hit("orders", "1.2.3.4") == pytest.approx(50)  # oldest hit leaves the window in 50 s
    clock.t += 50
    assert rl.hit("orders", "1.2.3.4") == 0


def test_buckets_and_addresses_are_independent():
    rl = RateLimiter(1, window=60, clock=Clock())
    assert rl.hit("orders", "a") == 0
    assert rl.hit("orders", "a") > 0
    assert rl.hit("orders", "b") == 0
    assert rl.hit("checkout", "a") == 0


def test_rejected_attempts_do_not_extend_the_block():
    clock = Clock()
    rl = RateLimiter(1, window=60, clock=clock)
    rl.hit("orders", "a")
    for _ in range(5):
        clock.t += 10
        rl.hit("orders", "a")
    clock.t += 11  # 61 s after the only recorded hit
    assert rl.hit("orders", "a") == 0


def test_zero_limit_disables():
    rl = RateLimiter(0)
    assert not rl.enabled
    assert all(rl.hit("orders", "a") == 0 for _ in range(100))


def test_idle_keys_are_swept(monkeypatch):
    import app.ratelimit as m

    monkeypatch.setattr(m, "MAX_KEYS", 2)
    clock = Clock()
    rl = RateLimiter(5, window=60, clock=clock)
    for ip in ("a", "b", "c"):
        rl.hit("orders", ip)
    clock.t += 61
    rl.hit("orders", "d")
    assert set(rl._hits) == {("orders", "d")}


def test_setting_from_env(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_10MIN", "7")
    assert load_settings().rate_limit_per_10min == 7
    monkeypatch.delenv("RATE_LIMIT_PER_10MIN")
    assert load_settings().rate_limit_per_10min == Settings().rate_limit_per_10min == 30


# --------------------------------------------------------------------------- endpoints
@pytest.fixture
def limited(services):
    """App with a limit of 2 per 10 minutes."""
    sv = replace(services, cfg=replace(services.cfg, rate_limit_per_10min=2))
    with TestClient(create_app(sv)) as c:
        yield c, sv


def _orders(sv) -> int:
    with session_scope(sv.sessions) as s:
        return s.scalar(select(func.count()).select_from(Order))


def test_wizard_submit_is_limited_per_ip(limited):
    c, sv = limited
    for _ in range(2):
        assert c.post("/start", data=FORM, follow_redirects=False).status_code == 303
    r = c.post("/start", data=FORM, follow_redirects=False)
    assert r.status_code == 429
    assert int(r.headers["Retry-After"]) > 0
    assert "Too many requests" in r.text and "Rocket Notes" in r.text  # answers kept in the form
    assert _orders(sv) == 2


def test_api_orders_is_limited_per_ip(limited):
    c, sv = limited
    body = {"email": "founder@example.com", "answers": ANSWERS}
    assert [c.post("/api/orders", json=body).status_code for _ in range(3)] == [201, 201, 429]
    r = c.post("/api/orders", json=body)
    assert r.status_code == 429 and int(r.headers["Retry-After"]) > 0
    assert _orders(sv) == 2


def test_wizard_and_api_share_the_order_budget(limited):
    c, _ = limited
    assert c.post("/api/orders", json={"email": "a@example.com", "answers": ANSWERS}).status_code == 201
    assert c.post("/start", data=FORM, follow_redirects=False).status_code == 303
    assert c.post("/start", data=FORM, follow_redirects=False).status_code == 429


def test_checkout_session_is_limited_per_ip(limited):
    c, sv = limited
    oid = c.post("/api/orders", json={"email": "a@example.com", "answers": ANSWERS}).json()["order_id"]
    for _ in range(2):
        assert c.post(f"/checkout/{oid}/pay", follow_redirects=False).status_code == 303
    r = c.post(f"/checkout/{oid}/pay", follow_redirects=False)
    assert r.status_code == 429 and int(r.headers["Retry-After"]) > 0
    assert "Too many" in r.text and f"/checkout/{oid}" in r.text
    assert len(sv.payments.sessions) == 2  # no third provider call


def test_other_ip_is_not_affected(limited):
    c, _ = limited
    for _ in range(3):
        c.post("/api/orders", json={"email": "a@example.com", "answers": ANSWERS})
    other = TestClient(c.app, client=("203.0.113.9", 50000))  # same app, another address
    assert other.post("/api/orders", json={"email": "b@example.com", "answers": ANSWERS}).status_code == 201


def test_reads_are_never_limited(limited):
    c, _ = limited
    oid = c.post("/api/orders", json={"email": "a@example.com", "answers": ANSWERS}).json()["order_id"]
    for _ in range(10):
        assert c.get(f"/api/orders/{oid}").status_code == 200
        assert c.get("/start").status_code == 200
    assert c.get("/healthz").status_code == 200


def test_client_ip_header_is_used_when_configured(services):
    sv = replace(services, cfg=replace(services.cfg, rate_limit_per_10min=1, client_ip_header="X-Real-IP"))
    with TestClient(create_app(sv)) as c:
        body = {"email": "a@example.com", "answers": ANSWERS}
        assert c.post("/api/orders", json=body, headers={"X-Real-IP": "198.51.100.1"}).status_code == 201
        assert c.post("/api/orders", json=body, headers={"X-Real-IP": "198.51.100.1"}).status_code == 429
        assert c.post("/api/orders", json=body, headers={"X-Real-IP": "198.51.100.2"}).status_code == 201
        # without the header: the peer address
        assert c.post("/api/orders", json=body).status_code == 201
        assert c.post("/api/orders", json=body).status_code == 429


def test_client_ip_header_is_ignored_when_not_configured(limited):
    c, _ = limited
    body = {"email": "a@example.com", "answers": ANSWERS}
    codes = [c.post("/api/orders", json=body, headers={"X-Real-IP": f"198.51.100.{i}"}).status_code for i in range(3)]
    assert codes == [201, 201, 429]
