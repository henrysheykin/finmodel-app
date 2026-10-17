"""Order API and signed downloads."""

from app import links
from app.db import session_scope
from app.models import Order
from app.orders import mark_paid
from tests.conftest import ANSWERS
from tests.test_pipeline import make


def test_create_and_read_order(client):
    r = client.post("/api/orders", json={"email": "Me@Example.com", "answers": ANSWERS})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["status"] == "awaiting_payment" and body["price_cents"] == 14900 and "email" not in body
    got = client.get(f"/api/orders/{body['order_id']}")
    assert got.status_code == 200 and got.json()["order_id"] == body["order_id"]
    assert client.get("/api/orders/doesnotexist").status_code == 404


def test_unsupported_or_invalid_answers(client):
    r = client.post("/api/orders", json={"email": "a@b.co", "answers": {**ANSWERS, "business_type": "real_estate"}})
    assert r.status_code == 422 and "not available" in r.text
    r = client.post("/api/orders", json={"email": "a@b.co", "answers": {**ANSWERS, "horizon_years": 7}})
    assert r.status_code == 422
    r = client.post("/api/orders", json={"email": "nope", "answers": ANSWERS})
    assert r.status_code == 422
    from engine.templates import planned, template_for_business_type

    available = client.get("/api/business-types").json()["available"]
    assert available == sorted(template_for_business_type())  # every catalog template (ADR-009)
    assert {"saas", "restaurant_cafe", "retail_ecommerce", "professional_services"} <= set(available)
    assert not set(planned()) & set(available)  # "coming soon" industries cannot be ordered


def _ready(client, services, notifier):
    oid = client.post("/api/orders", json={"email": "a@b.co", "answers": ANSWERS}).json()["order_id"]
    with session_scope(services.sessions) as s:
        mark_paid(s, services.cfg, oid, f"cs_{oid}")
    make(services, notifier).run_once()
    return oid, notifier.ready[-1][2].replace("http://testserver", "")


def test_download_with_signed_link(client, services, notifier):
    oid, path = _ready(client, services, notifier)
    r = client.get(path)
    assert r.status_code == 200 and r.content.startswith(b"PK-fake")
    assert "attachment" in r.headers["content-disposition"] and r.headers["cache-control"] == "private, no-store"


def test_download_rejections(client, services, notifier):
    oid, path = _ready(client, services, notifier)
    assert client.get(path[:-3] + "abc").status_code == 404
    assert client.get("/download/garbage").status_code == 404
    with session_scope(services.sessions) as s:
        art = s.get(Order, oid).artifact("model_xlsx")
        report = s.get(Order, oid).artifact("check_report")
        expired = links.sign(services.cfg.secret_key, art.id, -10)
        rep_tok = links.sign(services.cfg.secret_key, report.id, 60)
    assert client.get(f"/download/{expired}").status_code == 410
    assert client.get(f"/download/{rep_tok}").status_code == 404  # internal report is not downloadable
    with session_scope(services.sessions) as s:
        s.get(Order, oid).status = "failed"
    assert client.get(path).status_code == 404
