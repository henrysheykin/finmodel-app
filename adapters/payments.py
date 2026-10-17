"""Payment providers: Stripe Checkout (test mode until go-live) and a fake for dev and tests.

The app never trusts the browser about payment. Only a webhook whose signature verifies
moves an order to ``paid``; the amount and currency must match the order.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import time
from dataclasses import dataclass, field
from typing import Literal, Protocol

import httpx

STRIPE_API = "https://api.stripe.com/v1"
SIGNATURE_TOLERANCE_SECONDS = 300


class PaymentError(RuntimeError):
    """The provider refused or failed a request."""


class SignatureError(ValueError):
    """A webhook did not come from the provider (or is too old to trust)."""


@dataclass(frozen=True)
class CheckoutSession:
    id: str
    url: str


@dataclass(frozen=True)
class PaymentEvent:
    kind: Literal["paid", "expired", "ignored"]
    event_id: str
    order_id: str = ""
    payment_ref: str = ""  # checkout session id
    payment_intent: str = ""
    amount_cents: int = 0
    currency: str = ""


@dataclass(frozen=True)
class CheckoutRequest:
    order_id: str
    amount_cents: int
    currency: str
    product_name: str
    email: str
    success_url: str
    cancel_url: str


class PaymentProvider(Protocol):
    name: str

    def create_checkout(self, req: CheckoutRequest) -> CheckoutSession: ...
    def parse_webhook(self, payload: bytes, signature_header: str) -> PaymentEvent: ...
    def refund(self, payment_intent: str, amount_cents: int, idempotency_key: str) -> str: ...


# --------------------------------------------------------------------------- signatures (Stripe scheme)
def stripe_signature(secret: str, payload: bytes, timestamp: int) -> str:
    mac = hmac.new(secret.encode(), f"{timestamp}.".encode() + payload, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={mac}"


def verify_stripe_signature(secret: str, payload: bytes, header: str, now: float | None = None) -> None:
    """Stripe-Signature: ``t=<unix>,v1=<hex hmac>[,v1=...]``; raises SignatureError."""
    if not secret:
        raise SignatureError("webhook secret is not configured")
    parts = [p.split("=", 1) for p in (header or "").split(",") if "=" in p]
    ts = [v for k, v in parts if k == "t"]
    sigs = [v for k, v in parts if k == "v1"]
    if len(ts) != 1 or not sigs:
        raise SignatureError("malformed signature header")
    try:
        t = int(ts[0])
    except ValueError:
        raise SignatureError("malformed timestamp") from None
    if abs((now if now is not None else time.time()) - t) > SIGNATURE_TOLERANCE_SECONDS:
        raise SignatureError("signature timestamp outside tolerance")
    expected = hmac.new(secret.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(expected, s) for s in sigs):
        raise SignatureError("signature mismatch")


def _event_from_stripe(evt: dict) -> PaymentEvent:
    etype, obj = evt.get("type", ""), (evt.get("data") or {}).get("object") or {}
    eid = str(evt.get("id", ""))
    order_id = str(obj.get("client_reference_id") or (obj.get("metadata") or {}).get("order_id") or "")
    common = {
        "event_id": eid,
        "order_id": order_id,
        "payment_ref": str(obj.get("id", "")),
        "payment_intent": str(obj.get("payment_intent") or ""),
        "amount_cents": int(obj.get("amount_total") or 0),
        "currency": str(obj.get("currency") or "").upper(),
    }
    if etype in ("checkout.session.completed", "checkout.session.async_payment_succeeded"):
        if obj.get("payment_status") == "paid":
            return PaymentEvent("paid", **common)
        return PaymentEvent("ignored", **common)  # async methods: wait for async_payment_succeeded
    if etype == "checkout.session.expired":
        return PaymentEvent("expired", **common)
    return PaymentEvent("ignored", event_id=eid)


# --------------------------------------------------------------------------- Stripe
class StripeProvider:
    name = "stripe"

    def __init__(
        self, secret_key: str, webhook_secret: str, allow_live: bool = False, client: httpx.Client | None = None
    ):
        if not secret_key:
            raise PaymentError("STRIPE_SECRET_KEY is not set")
        if secret_key.startswith(("sk_live_", "rk_live_")) and not allow_live:
            # hard rule: test mode only until Henry switches payments on at go-live
            raise PaymentError("live Stripe keys are refused (set ALLOW_LIVE_PAYMENTS=1 only at go-live)")
        self.webhook_secret = webhook_secret
        self.client = client or httpx.Client(base_url=STRIPE_API, timeout=20)
        self.client.auth = (secret_key, "")

    def _post(self, path: str, data: dict, idem: str) -> dict:
        try:
            r = self.client.post(path, data=data, headers={"Idempotency-Key": idem})
        except httpx.HTTPError as exc:
            raise PaymentError(f"stripe unreachable: {type(exc).__name__}") from exc
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
        if r.status_code >= 400:
            msg = (body.get("error") or {}).get("message") or f"HTTP {r.status_code}"
            raise PaymentError(f"stripe: {msg}")
        return body

    def create_checkout(self, req: CheckoutRequest) -> CheckoutSession:
        data = {
            "mode": "payment",
            "client_reference_id": req.order_id,
            "metadata[order_id]": req.order_id,
            "customer_email": req.email,
            "line_items[0][quantity]": "1",
            "line_items[0][price_data][currency]": req.currency.lower(),
            "line_items[0][price_data][unit_amount]": str(req.amount_cents),
            "line_items[0][price_data][product_data][name]": req.product_name,
            "success_url": req.success_url,
            "cancel_url": req.cancel_url,
        }
        body = self._post("/checkout/sessions", data, f"checkout:{req.order_id}:{secrets.token_hex(8)}")
        return CheckoutSession(body["id"], body["url"])

    def parse_webhook(self, payload: bytes, signature_header: str) -> PaymentEvent:
        verify_stripe_signature(self.webhook_secret, payload, signature_header)
        try:
            return _event_from_stripe(json.loads(payload))
        except (ValueError, TypeError) as exc:
            raise SignatureError(f"unreadable event: {exc}") from None

    def refund(self, payment_intent: str, amount_cents: int, idempotency_key: str) -> str:
        if not payment_intent:
            raise PaymentError("no payment intent recorded for this order")
        body = self._post("/refunds", {"payment_intent": payment_intent, "amount": str(amount_cents)}, idempotency_key)
        return str(body["id"])


# --------------------------------------------------------------------------- fake (dev + tests)
@dataclass
class FakeProvider:
    """Stripe-shaped fake: signed events, hosted page at /dev/pay/{session} (dev only)."""

    base_url: str
    webhook_secret: str = "whsec_fake"
    name: str = "fake"
    sessions: dict[str, CheckoutRequest] = field(default_factory=dict)
    refunds: list[tuple[str, int, str]] = field(default_factory=list)

    def create_checkout(self, req: CheckoutRequest) -> CheckoutSession:
        sid = "cs_fake_" + secrets.token_hex(8)
        self.sessions[sid] = req
        return CheckoutSession(sid, f"{self.base_url}/dev/pay/{sid}")

    def event(self, sid: str, kind: str = "checkout.session.completed", paid: bool = True, **override) -> dict:
        req = self.sessions[sid]
        obj = {
            "id": sid,
            "client_reference_id": req.order_id,
            "metadata": {"order_id": req.order_id},
            "payment_status": "paid" if paid else "unpaid",
            "payment_intent": "pi_" + sid,
            "amount_total": req.amount_cents,
            "currency": req.currency.lower(),
            **override,
        }
        return {"id": "evt_" + secrets.token_hex(6), "type": kind, "data": {"object": obj}}

    def signed(self, evt: dict, now: int | None = None) -> tuple[bytes, str]:
        payload = json.dumps(evt).encode()
        return payload, stripe_signature(self.webhook_secret, payload, int(now if now is not None else time.time()))

    def parse_webhook(self, payload: bytes, signature_header: str) -> PaymentEvent:
        verify_stripe_signature(self.webhook_secret, payload, signature_header)
        return _event_from_stripe(json.loads(payload))

    def refund(self, payment_intent: str, amount_cents: int, idempotency_key: str) -> str:
        for _pi, _amt, key in self.refunds:
            if key == idempotency_key:
                return f"re_{key}"
        if not payment_intent:
            raise PaymentError("no payment intent recorded for this order")
        self.refunds.append((payment_intent, amount_cents, idempotency_key))
        return f"re_{idempotency_key}"


def make_provider(name: str, base_url: str, secret_key: str, webhook_secret: str, allow_live: bool) -> PaymentProvider:
    if name == "stripe":
        return StripeProvider(secret_key, webhook_secret, allow_live)
    if name == "fake":
        return FakeProvider(base_url, webhook_secret or "whsec_fake")
    raise RuntimeError(f"unknown PAYMENT_PROVIDER {name!r}")
