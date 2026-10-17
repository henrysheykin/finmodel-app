"""Payments: Stripe adapter (mocked HTTP), webhook signatures, paid/cancel/duplicate flows, refunds."""

import json
import time
from dataclasses import replace

import httpx
import pytest

from adapters.payments import (
    CheckoutRequest,
    FakeProvider,
    PaymentError,
    SignatureError,
    StripeProvider,
    _event_from_stripe,
    stripe_signature,
    verify_stripe_signature,
)
from app.config import Settings
from app.db import session_scope
from app.models import Job, Order
from app.orders import OrderError, refund_order
from tests.conftest import ANSWERS

SECRET = "whsec_test_123"
REQ = CheckoutRequest("ord1", 14900, "USD", "StartupModel Light", "a@b.co", "https://x/s", "https://x/c")


# --------------------------------------------------------------------------- signatures
def test_signature_roundtrip_and_rejections():
    body, now = b'{"id":"evt_1"}', 1_700_000_000
    header = stripe_signature(SECRET, body, now)
    verify_stripe_signature(SECRET, body, header, now=now + 10)
    verify_stripe_signature(SECRET, body, header + ",v1=deadbeef", now=now)  # extra signatures allowed
    cases = [
        (SECRET, body + b" ", header, now),  # body changed
        ("whsec_other", body, header, now),  # wrong secret
        (SECRET, body, header, now + 301),  # replay outside tolerance
        (SECRET, body, "v1=abc", now),  # no timestamp
        (SECRET, body, "t=abc,v1=abc", now),
        (SECRET, body, "", now),
        ("", body, header, now),  # secret not configured
    ]
    for secret, b, h, t in cases:
        with pytest.raises(SignatureError):
            verify_stripe_signature(secret, b, h, now=t)


def _session_event(etype="checkout.session.completed", **obj):
    base = {
        "id": "cs_1",
        "client_reference_id": "ord1",
        "payment_status": "paid",
        "payment_intent": "pi_1",
        "amount_total": 14900,
        "currency": "usd",
    }
    return {"id": "evt_1", "type": etype, "data": {"object": {**base, **obj}}}


def test_event_mapping():
    e = _event_from_stripe(_session_event())
    assert (e.kind, e.order_id, e.payment_ref, e.payment_intent, e.amount_cents, e.currency) == (
        "paid",
        "ord1",
        "cs_1",
        "pi_1",
        14900,
        "USD",
    )
    assert _event_from_stripe(_session_event(payment_status="unpaid")).kind == "ignored"
    assert _event_from_stripe(_session_event("checkout.session.async_payment_succeeded")).kind == "paid"
    assert _event_from_stripe(_session_event("checkout.session.expired", payment_status="unpaid")).kind == "expired"
    assert _event_from_stripe({"id": "evt_2", "type": "customer.created", "data": {"object": {}}}).kind == "ignored"
    meta_only = _session_event(client_reference_id=None, metadata={"order_id": "ord9"})
    assert _event_from_stripe(meta_only).order_id == "ord9"


# --------------------------------------------------------------------------- Stripe adapter (no network)
def _stripe(handler, key="sk_test_abc", **kw):
    client = httpx.Client(base_url="https://api.stripe.com/v1", transport=httpx.MockTransport(handler))
    return StripeProvider(key, SECRET, client=client, **kw)


def test_stripe_create_checkout_sends_the_right_fields():
    seen = {}

    def handler(request: httpx.Request):
        seen["path"], seen["headers"] = request.url.path, request.headers
        seen["form"] = dict(httpx.QueryParams(request.content.decode()))
        return httpx.Response(200, json={"id": "cs_test_1", "url": "https://checkout.stripe.com/c/pay/cs_test_1"})

    s = _stripe(handler).create_checkout(REQ)
    assert (s.id, s.url) == ("cs_test_1", "https://checkout.stripe.com/c/pay/cs_test_1")
    f = seen["form"]
    assert seen["path"] == "/v1/checkout/sessions" and f["mode"] == "payment"
    assert f["line_items[0][price_data][unit_amount]"] == "14900" and f["line_items[0][price_data][currency]"] == "usd"
    assert f["client_reference_id"] == "ord1" and f["metadata[order_id]"] == "ord1" and f["customer_email"] == "a@b.co"
    assert seen["headers"]["idempotency-key"].startswith("checkout:ord1:")
    assert seen["headers"]["authorization"].startswith("Basic ")


def test_stripe_errors_and_live_key_guard():
    def err(request):
        return httpx.Response(402, json={"error": {"message": "Your card was declined."}})

    with pytest.raises(PaymentError, match="declined"):
        _stripe(err).create_checkout(REQ)

    def boom(request):
        raise httpx.ConnectError("down")

    with pytest.raises(PaymentError, match="unreachable"):
        _stripe(boom).create_checkout(REQ)
    with pytest.raises(PaymentError, match="live Stripe keys are refused"):
        _stripe(err, key="sk_live_abc")
    _stripe(err, key="sk_live_abc", allow_live=True)  # only with the explicit go-live switch
    with pytest.raises(PaymentError, match="not set"):
        StripeProvider("", SECRET)


def test_stripe_refund():
    def handler(request):
        form = dict(httpx.QueryParams(request.content.decode()))
        assert request.url.path == "/v1/refunds" and form == {"payment_intent": "pi_1", "amount": "14900"}
        assert request.headers["idempotency-key"] == "refund:ord1"
        return httpx.Response(200, json={"id": "re_1"})

    assert _stripe(handler).refund("pi_1", 14900, "refund:ord1") == "re_1"
    with pytest.raises(PaymentError, match="no payment intent"):
        _stripe(handler).refund("", 14900, "refund:ord1")


def test_stripe_webhook_parse_verifies_signature():
    p = _stripe(lambda r: httpx.Response(500))
    body = json.dumps(_session_event()).encode()
    assert p.parse_webhook(body, stripe_signature(SECRET, body, int(time.time()))).kind == "paid"
    with pytest.raises(SignatureError):
        p.parse_webhook(body, stripe_signature("whsec_wrong", body, int(time.time())))


def test_production_requires_stripe():
    with pytest.raises(RuntimeError, match="PAYMENT_PROVIDER=stripe"):
        Settings(app_env="prod", secret_key="k" * 40, payment_provider="fake").check()
    Settings(app_env="prod", secret_key="k" * 40, payment_provider="stripe").check()


# --------------------------------------------------------------------------- web flow
def _order(client):
    r = client.post("/start", data={**ANSWERS, "horizon_years": "1", "email": "a@b.co"}, follow_redirects=False)
    return r.headers["location"].rsplit("/", 1)[1]


def _pay(client):
    oid = _order(client)
    r = client.post(f"/checkout/{oid}/pay", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].startswith("http://testserver/dev/pay/cs_fake_")
    return oid, r.headers["location"].rsplit("/", 1)[1]


def _status(services, oid):
    with session_scope(services.sessions) as s:
        o = s.get(Order, oid)
        return o.status, len(o.jobs)


def test_success_flow_through_the_hosted_page(client, services):
    oid, sid = _pay(client)
    page = client.get(f"/dev/pay/{sid}")
    assert page.status_code == 200 and "$149" in page.text and "No real card" in page.text
    r = client.post(f"/dev/pay/{sid}", data={"action": "pay"}, follow_redirects=False)
    assert r.headers["location"] == f"http://testserver/checkout/{oid}/success"
    assert _status(services, oid) == ("paid", 1)
    done = client.get(f"/checkout/{oid}/success")
    assert done.status_code == 200 and "Payment received" in done.text
    with session_scope(services.sessions) as s:
        o = s.get(Order, oid)
        assert o.payment_ref == sid and o.payment_intent == "pi_" + sid


def test_cancel_returns_to_checkout_unpaid(client, services):
    oid, sid = _pay(client)
    r = client.post(f"/dev/pay/{sid}", data={"action": "cancel"}, follow_redirects=False)
    assert r.headers["location"] == f"http://testserver/checkout/{oid}?cancelled=1"
    page = client.get(f"/checkout/{oid}?cancelled=1")
    assert "Payment was cancelled" in page.text and "Pay $149" in page.text
    assert _status(services, oid) == ("awaiting_payment", 0)


def _webhook(client, services, sid, **override):
    evt = services.payments.event(sid, **override)
    body, sig = services.payments.signed(evt)
    return client.post("/webhooks/stripe", content=body, headers={"Stripe-Signature": sig})


def test_duplicate_webhooks_apply_once(client, services):
    oid, sid = _pay(client)
    for _ in range(3):
        r = _webhook(client, services, sid)
        assert r.status_code == 200 and r.json()["action"] == "paid"
    assert _status(services, oid) == ("paid", 1)


def test_bad_signature_is_rejected(client, services):
    oid, sid = _pay(client)
    body, sig = services.payments.signed(services.payments.event(sid))
    r = client.post("/webhooks/stripe", content=body, headers={"Stripe-Signature": sig.replace("v1=", "v1=00")})
    assert r.status_code == 400
    r = client.post("/webhooks/stripe", content=body + b" ", headers={"Stripe-Signature": sig})
    assert r.status_code == 400
    old_body, old_sig = services.payments.signed(services.payments.event(sid), now=int(time.time()) - 3600)
    assert client.post("/webhooks/stripe", content=old_body, headers={"Stripe-Signature": old_sig}).status_code == 400
    assert client.post("/webhooks/stripe", content=body).status_code == 400
    assert _status(services, oid) == ("awaiting_payment", 0)


def test_wrong_amount_or_unknown_order_needs_attention(client, services):
    oid, sid = _pay(client)
    r = _webhook(client, services, sid, amount_total=100)
    assert r.status_code == 200 and r.json()["action"] == "needs_attention"
    r = _webhook(client, services, sid, currency="eur")
    assert r.json()["action"] == "needs_attention"
    r = _webhook(client, services, sid, client_reference_id="nope", metadata={})
    assert r.json()["action"] == "needs_attention"
    assert _status(services, oid) == ("awaiting_payment", 0)


def test_unpaid_and_expired_events_are_ignored(client, services):
    oid, sid = _pay(client)
    assert _webhook(client, services, sid, paid=False).json()["action"] == "ignored"
    assert _webhook(client, services, sid, kind="checkout.session.expired").json()["action"] == "ignored"
    assert _status(services, oid) == ("awaiting_payment", 0)


def test_pay_on_a_paid_order_goes_back_to_checkout(client, services):
    oid, sid = _pay(client)
    _webhook(client, services, sid)
    r = client.post(f"/checkout/{oid}/pay", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == f"/checkout/{oid}"


def test_provider_outage_shows_a_friendly_page(client, services):
    class Down(FakeProvider):
        def create_checkout(self, req):
            raise PaymentError("stripe unreachable")

    services.payments = Down("http://testserver")
    oid = _order(client)
    r = client.post(f"/checkout/{oid}/pay")
    assert r.status_code == 502 and "Nothing was charged" in r.text


def test_dev_page_is_hidden_without_fake_provider_or_in_prod(client, services):
    oid, sid = _pay(client)
    assert client.get("/dev/pay/cs_unknown").status_code == 404
    services.cfg = replace(services.cfg, app_env="prod")
    assert client.get(f"/dev/pay/{sid}").status_code == 404
    assert client.post(f"/dev/pay/{sid}", data={"action": "pay"}).status_code == 404


# --------------------------------------------------------------------------- refunds
def test_refund_paid_order_cancels_queued_build(client, services):
    oid, sid = _pay(client)
    _webhook(client, services, sid)
    with session_scope(services.sessions) as s:
        o = s.get(Order, oid)
        ref = refund_order(s, services.payments, o, "customer asked")
        assert ref == f"re_refund:{oid}" and o.status == "refunded" and o.refunded_at is not None
    with session_scope(services.sessions) as s:
        o = s.get(Order, oid)
        assert refund_order(s, services.payments, o) == ref  # idempotent
        assert [j.status for j in s.query(Job).filter_by(order_id=oid)] == ["done"]
    assert services.payments.refunds == [("pi_" + sid, 14900, f"refund:{oid}")]


def test_unpaid_order_cannot_be_refunded(client, services):
    oid = _order(client)
    with session_scope(services.sessions) as s, pytest.raises(OrderError, match="only paid"):
        refund_order(s, services.payments, s.get(Order, oid))


def test_second_payment_for_the_same_order_is_refunded(client, services):
    oid = _order(client)
    sid1 = client.post(f"/checkout/{oid}/pay", follow_redirects=False).headers["location"].rsplit("/", 1)[1]
    sid2 = client.post(f"/checkout/{oid}/pay", follow_redirects=False).headers["location"].rsplit("/", 1)[1]
    assert _webhook(client, services, sid1).json()["action"] == "paid"
    assert _webhook(client, services, sid2).json()["action"] == "duplicate_refunded"
    assert _webhook(client, services, sid2).json()["action"] == "duplicate_refunded"  # retried webhook
    assert services.payments.refunds == [("pi_" + sid2, 14900, f"duplicate:{sid2}")]  # refunded once
    assert _status(services, oid) == ("paid", 1)
