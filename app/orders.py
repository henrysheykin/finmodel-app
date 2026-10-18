"""Order state machine and the operations that move an order through it.

    draft → awaiting_payment → paid → building → checking → ready
                                  ↘            ↘          ↘ failed
    building / checking may fall back to paid when a retryable error re-queues the build.

Every transition goes through ``transition`` (one place to validate and audit). Payment is
idempotent per provider reference; the build job is unique per order and attempt round.
"""

from __future__ import annotations

import json

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config import Settings
from app.db import utcnow
from app.models import Job, Order, OrderEvent
from engine.brief import Brief

STATUSES = ("draft", "awaiting_payment", "paid", "building", "checking", "ready", "failed", "refunded")
TRANSITIONS: dict[str, set[str]] = {
    "draft": {"awaiting_payment"},
    "awaiting_payment": {"paid"},
    "paid": {"building", "failed", "refunded"},
    "building": {"checking", "paid", "failed"},
    "checking": {"ready", "paid", "failed"},
    "ready": {"paid", "refunded"},  # admin re-build (E14) or refund
    "failed": {"paid", "refunded"},  # admin re-build after a fix, or refund
    "refunded": set(),
}


class InvalidTransition(ValueError):
    pass


class OrderError(ValueError):
    """The request cannot become an order (unsupported business type, invalid numbers...)."""


class AlreadyPaid(OrderError):
    """The same payment was applied by a concurrent delivery of the same webhook (E17)."""


class DuplicatePayment(OrderError):
    """A second, different payment arrived for an order that is already paid (e.g. two browser tabs)."""


def transition(s: Session, order: Order, to: str, note: str = "") -> None:
    if to not in TRANSITIONS.get(order.status, set()):
        raise InvalidTransition(f"order {order.id}: {order.status} → {to} is not allowed")
    s.add(OrderEvent(order_id=order.id, from_status=order.status, to_status=to, note=note[:2000]))
    order.status = to
    order.updated_at = utcnow()
    if to == "paid" and order.paid_at is None:
        order.paid_at = utcnow()
    if to == "ready":
        order.ready_at = utcnow()
    if to == "refunded":
        order.refunded_at = utcnow()


def create_order(s: Session, cfg: Settings, email: str, brief: Brief, answers: dict | None = None) -> Order:
    """A validated brief becomes an order waiting for payment."""
    if brief.tier not in cfg.prices:
        raise OrderError(f"no price for tier {brief.tier!r}")
    email = email.strip().lower()
    if "@" not in email or len(email) > 254:
        raise OrderError("a valid email is required")
    order = Order(
        email=email,
        template=brief.template,
        tier=brief.tier,
        price_cents=cfg.prices[brief.tier],
        brief_json=brief.model_dump_json(),
        answers_json=json.dumps(answers or {}, sort_keys=True),
    )
    s.add(order)
    s.flush()
    transition(s, order, "awaiting_payment")
    return order


def enqueue_build(s: Session, order: Order, cfg: Settings, reason: str = "paid") -> Job:
    """Create the build job for the order's current round (idempotent per round)."""
    rnd = sum(1 for j in order.jobs if j.kind == "build") + 1
    job = Job(
        order=order,
        kind="build",
        idempotency_key=f"build:{order.id}:{rnd}",
        max_attempts=cfg.job_max_attempts,
        run_after=utcnow(),
    )
    s.add(job)
    s.flush()
    s.add(
        OrderEvent(order_id=order.id, from_status=order.status, to_status=order.status, note=f"build queued ({reason})")
    )
    return job


def mark_paid(
    s: Session,
    cfg: Settings,
    order_id: str,
    payment_ref: str,
    amount_cents: int | None = None,
    currency: str | None = None,
    payment_intent: str | None = None,
    strict: bool = False,
) -> Order:
    """Apply a confirmed payment. Safe to call twice with the same reference (duplicate webhooks);
    with ``strict`` a repeat raises ``AlreadyPaid`` instead, so the webhook knows not to send a
    second receipt.

    Concurrent deliveries of one payment race here (the provider retries, two web threads): the
    payment is claimed with a conditional UPDATE, so exactly one caller wins; a loser holding the
    same reference gets ``AlreadyPaid`` (no second build, no second receipt), one holding another
    reference gets ``DuplicatePayment``.
    """
    order = s.get(Order, order_id, with_for_update=True, populate_existing=True)
    if order is None:
        raise OrderError(f"unknown order {order_id}")
    if order.payment_ref == payment_ref:  # duplicate delivery: already applied
        if strict:
            raise AlreadyPaid(f"order {order.id}: payment {payment_ref} is already applied")
        return order
    if order.payment_ref is not None:
        raise DuplicatePayment(f"order {order.id} is already paid with another reference")
    clash = s.scalar(select(Order).where(Order.payment_ref == payment_ref, Order.id != order.id))
    if clash is not None:
        raise OrderError("payment reference already used by another order")
    if amount_cents is not None and amount_cents != order.price_cents:
        raise OrderError(f"amount {amount_cents} does not match order price {order.price_cents}")
    if currency is not None and currency.upper() != order.currency:
        raise OrderError(f"currency {currency} does not match order currency {order.currency}")
    if order.status != "awaiting_payment":
        raise OrderError(f"order {order.id} is {order.status}, not awaiting payment")
    claimed = s.execute(
        update(Order)
        .where(Order.id == order.id, Order.payment_ref.is_(None), Order.status == "awaiting_payment")
        .values(payment_ref=payment_ref)
        .execution_options(synchronize_session=False)
    )
    if claimed.rowcount != 1:
        s.refresh(order)
        if order.payment_ref == payment_ref:
            raise AlreadyPaid(f"order {order.id}: payment {payment_ref} was applied concurrently")
        raise DuplicatePayment(f"order {order.id} was paid concurrently with another reference")
    order.payment_ref = payment_ref
    order.payment_intent = payment_intent or order.payment_intent
    transition(s, order, "paid", f"payment {payment_ref}")
    enqueue_build(s, order, cfg)
    return order


def rebuild(s: Session, cfg: Settings, order: Order, note: str = "admin re-build") -> Job:
    """Queue another build of a ready or failed order (admin action, E14)."""
    if order.status not in ("ready", "failed"):
        # awaiting_payment → paid is the payment transition; a re-build must never stand in for a payment
        raise OrderError(f"order {order.id} is {order.status}; only ready or failed orders can be re-built")
    transition(s, order, "paid", note)
    order.failure_reason = None
    return enqueue_build(s, order, cfg, reason=note)


def brief_of(order: Order) -> Brief:
    return Brief.model_validate_json(order.brief_json)


def refund_order(s: Session, provider, order: Order, note: str = "refund") -> str:
    """Refund the full amount through the provider (idempotent per order) and close the order."""
    if order.status == "refunded":
        return order.refund_ref or ""
    if order.status not in ("paid", "ready", "failed"):
        raise OrderError(f"order {order.id} is {order.status}; only paid, ready or failed orders can be refunded")
    ref = provider.refund(order.payment_intent or "", order.price_cents, f"refund:{order.id}")
    order.refund_ref = ref
    transition(s, order, "refunded", f"{note}: {ref}")
    for job in order.jobs:  # a refunded order is never built or delivered
        if job.status == "queued":
            job.status, job.finished_at, job.last_error = "done", utcnow(), "cancelled: order refunded"
    return ref
