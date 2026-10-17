"""Order state machine, creation and idempotent payment (no LibreOffice)."""

import pytest

from app.briefing import Answers, PrefillBriefSource
from app.db import session_scope
from app.models import Job, Order
from app.orders import TRANSITIONS, InvalidTransition, OrderError, create_order, mark_paid, rebuild, transition
from tests.conftest import ANSWERS


def _order(services, **kw):
    brief = PrefillBriefSource().build_brief(Answers(**{**ANSWERS, **kw}))
    with session_scope(services.sessions) as s:
        return create_order(s, services.cfg, " Founder@Example.COM ", brief, ANSWERS).id


def test_create_order_prices_by_tier(services):
    light, full = _order(services, tier="light"), _order(services, tier="full")
    with session_scope(services.sessions) as s:
        a, b = s.get(Order, light), s.get(Order, full)
        assert (a.price_cents, b.price_cents) == (14900, 34900)
        assert a.status == "awaiting_payment" and a.email == "founder@example.com"
        assert [(e.from_status, e.to_status) for e in a.events] == [("draft", "awaiting_payment")]


def test_invalid_email_rejected(services):
    brief = PrefillBriefSource().build_brief(Answers(**ANSWERS))
    with session_scope(services.sessions) as s, pytest.raises(OrderError, match="email"):
        create_order(s, services.cfg, "not-an-email", brief)


@pytest.mark.parametrize(
    "src,dst",
    [("awaiting_payment", "ready"), ("draft", "paid"), ("paid", "ready"), ("building", "ready"), ("ready", "building")],
)
def test_forbidden_transitions(services, src, dst):
    assert dst not in TRANSITIONS[src]
    with session_scope(services.sessions) as s:
        o = s.get(Order, _order(services))
        o.status = src
        with pytest.raises(InvalidTransition):
            transition(s, o, dst)


def test_happy_path_transitions_are_allowed():
    path = ["draft", "awaiting_payment", "paid", "building", "checking", "ready"]
    for a, b in zip(path, path[1:], strict=False):
        assert b in TRANSITIONS[a]


def test_mark_paid_is_idempotent(services):
    oid = _order(services)
    for _ in range(3):  # duplicate webhook deliveries
        with session_scope(services.sessions) as s:
            mark_paid(s, services.cfg, oid, "cs_test_1", 14900)
    with session_scope(services.sessions) as s:
        o = s.get(Order, oid)
        assert o.status == "paid" and o.paid_at is not None
        assert len(o.jobs) == 1 and o.jobs[0].idempotency_key == f"build:{oid}:1"


def test_mark_paid_rejects_wrong_amount_and_reused_reference(services):
    a, b = _order(services), _order(services)
    with session_scope(services.sessions) as s, pytest.raises(OrderError, match="amount"):
        mark_paid(s, services.cfg, a, "cs_x", 100)
    with session_scope(services.sessions) as s:
        mark_paid(s, services.cfg, a, "cs_a")
    with session_scope(services.sessions) as s, pytest.raises(OrderError, match="another"):
        mark_paid(s, services.cfg, a, "cs_other")
    with session_scope(services.sessions) as s, pytest.raises(OrderError, match="already used"):
        mark_paid(s, services.cfg, b, "cs_a")
    with session_scope(services.sessions) as s, pytest.raises(OrderError, match="unknown"):
        mark_paid(s, services.cfg, "nope", "cs_z")


def test_rebuild_queues_a_new_round(services):
    oid = _order(services)
    with session_scope(services.sessions) as s:
        mark_paid(s, services.cfg, oid, "cs_r")
    with session_scope(services.sessions) as s:
        o = s.get(Order, oid)
        o.status = "failed"
        rebuild(s, services.cfg, o)
    with session_scope(services.sessions) as s:
        keys = [j.idempotency_key for j in s.query(Job).filter_by(order_id=oid).order_by(Job.id)]
        assert keys == [f"build:{oid}:1", f"build:{oid}:2"]
        assert s.get(Order, oid).status == "paid"


def test_rebuild_never_marks_an_unpaid_order_paid(services):
    oid = _order(services)
    with session_scope(services.sessions) as s, pytest.raises(OrderError, match="only ready or failed"):
        rebuild(s, services.cfg, s.get(Order, oid))
    with session_scope(services.sessions) as s:
        assert s.get(Order, oid).status == "awaiting_payment"
