"""E17: 50 customers at once. Orders and payment webhooks (each delivered twice, in parallel) race
each other; one worker then drains the queue. Every order is built exactly once, every customer
gets exactly one receipt and one download email."""

import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

from sqlalchemy import func, select

from adapters.payments import stripe_signature
from app.db import session_scope
from app.models import Job, Order
from tests.conftest import ANSWERS
from tests.test_pipeline import make

N = 50


def _event(oid: str, price: int) -> dict:
    return {
        "id": f"evt_{oid[:8]}",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": f"cs_{oid}",
                "client_reference_id": oid,
                "payment_status": "paid",
                "payment_intent": f"pi_{oid}",
                "amount_total": price,
                "currency": "usd",
            }
        },
    }


def test_fifty_customers_at_once(client, services, notifier):
    import json
    import time

    services.cfg = replace(services.cfg, rate_limit_per_10min=0)
    lock = threading.Lock()

    def order(i: int) -> tuple[str, int]:
        r = client.post("/api/orders", json={"email": f"c{i}@example.com", "answers": ANSWERS})
        assert r.status_code == 201, r.text
        return r.json()["order_id"], r.json()["price_cents"]

    with ThreadPoolExecutor(16) as pool:
        orders = list(pool.map(order, range(N)))
    assert len({oid for oid, _ in orders}) == N

    def deliver(item) -> str:
        oid, price = item
        payload = json.dumps(_event(oid, price)).encode()
        sig = stripe_signature(services.payments.webhook_secret, payload, int(time.time()))
        r = client.post("/webhooks/stripe", content=payload, headers={"Stripe-Signature": sig})
        assert r.status_code == 200, r.text
        with lock:
            return r.json()["action"]

    with ThreadPoolExecutor(16) as pool:
        actions = Counter(pool.map(deliver, orders + orders))  # every payment arrives twice, concurrently
    assert actions == {"paid": N, "already_paid": N}

    worker = make(services, notifier)
    built = 0
    while worker.run_once():
        built += 1
    assert built == N
    with session_scope(services.sessions) as s:
        assert Counter(s.scalars(select(Order.status)).all()) == {"ready": N}
        per_order = s.execute(select(Job.order_id, func.count()).group_by(Job.order_id)).all()
        assert len(per_order) == N and {n for _, n in per_order} == {1}
    receipts = Counter(oid for kind, oid in notifier.events if kind == "order_received")
    assert len(receipts) == N and set(receipts.values()) == {1}
    assert sorted(e for e, _, _ in notifier.ready) == sorted(f"c{i}@example.com" for i in range(N))


def test_simultaneous_deliveries_of_one_payment_apply_it_once(client, services, notifier):
    """Threads released together on the same webhook: one wins; the rest see it as already paid
    (before E17 each one queued its own build and sent its own receipt)."""
    from adapters.payments import PaymentEvent
    from app.web import apply_payment_event

    services.cfg = replace(services.cfg, rate_limit_per_10min=0)
    for rnd in range(10):
        oid = client.post("/api/orders", json={"email": f"r{rnd}@example.com", "answers": ANSWERS}).json()["order_id"]
        event = PaymentEvent("paid", f"evt_{rnd}", oid, f"cs_race_{rnd}", f"pi_race_{rnd}", 14900, "USD")
        results = _race(lambda ev=event: apply_payment_event(services, ev)["action"], 6)
        assert results.count("paid") == 1, results
        assert set(results) <= {"paid", "already_paid", "OperationalError"}, results
        with session_scope(services.sessions) as s:
            assert s.scalar(select(func.count()).select_from(Job).where(Job.order_id == oid)) == 1
    receipts = Counter(oid for kind, oid in notifier.events if kind == "order_received")
    assert len(receipts) == 10 and set(receipts.values()) == {1}


def _race(fn, n: int) -> list[str]:
    """Run ``fn`` in ``n`` threads released at the same instant; exceptions become their class name."""
    start, results = threading.Barrier(n), []

    def go():
        start.wait()
        try:
            results.append(fn())
        except Exception as exc:  # e.g. SQLite "database is locked": the provider simply retries
            results.append(type(exc).__name__)

    threads = [threading.Thread(target=go) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def test_a_slow_email_api_does_not_stall_the_site(services):
    """Handlers that call Stripe or the email API run in the thread pool, not on the event loop:
    while one visitor's sign-in email takes seconds to send, other pages still answer at once."""
    import socket
    import time

    import httpx
    import uvicorn

    from app.main import create_app

    class SlowMail:
        def login_link(self, email, url):
            time.sleep(2)

    services.notifier = SlowMail()
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(create_app(services), host="127.0.0.1", port=port, log_level="warning"))
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    while not server.started:
        time.sleep(0.02)
    try:
        base = f"http://127.0.0.1:{port}"
        slow = threading.Thread(target=lambda: httpx.post(f"{base}/login", data={"email": "a@example.com"}, timeout=10))
        slow.start()
        time.sleep(0.3)  # the sign-in request is now inside the 2-second send
        t0 = time.monotonic()
        assert httpx.get(f"{base}/healthz", timeout=10).status_code == 200
        assert time.monotonic() - t0 < 1.0
        slow.join()
    finally:
        server.should_exit = True
        t.join(5)
