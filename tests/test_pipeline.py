"""Worker pipeline with fake build steps (fast, no LibreOffice)."""

from datetime import timedelta

import pytest

from app import links
from app.briefing import Answers, PrefillBriefSource
from app.db import session_scope, utcnow
from app.models import Job, Order
from app.orders import create_order, mark_paid, rebuild
from tests.conftest import ANSWERS
from worker.pipeline import BuildRejected, Pipeline


def fake_generate(brief, path):
    path.write_bytes(b"PK-fake-xlsx-" + brief.template.encode())


def fake_check(brief, path):
    return {"verdict": "PASS", "problems": []}


def make(services, notifier, **kw):
    return Pipeline(
        services.sessions,
        services.cfg,
        services.storage,
        notifier,
        generate=kw.get("generate", fake_generate),
        check=kw.get("check", fake_check),
    )


def paid_order(services, ref="cs_1"):
    brief = PrefillBriefSource().build_brief(Answers(**ANSWERS))
    with session_scope(services.sessions) as s:
        oid = create_order(s, services.cfg, "a@b.co", brief).id
    with session_scope(services.sessions) as s:
        mark_paid(s, services.cfg, oid, ref)
    return oid


def state(services, oid):
    with session_scope(services.sessions) as s:
        o = s.get(Order, oid)
        o.event_trail = [e.to_status for e in o.events]  # loaded while the session is open
        return o.status, [(j.status, j.attempts) for j in o.jobs], [a.kind for a in o.artifacts], o


def test_happy_path_delivers_a_signed_link(services, notifier):
    oid = paid_order(services)
    pipe = make(services, notifier)
    assert pipe.run_once() is True
    assert pipe.run_once() is False  # queue empty
    status, jobs, arts, o = state(services, oid)
    assert status == "ready" and jobs == [("done", 1)] and sorted(arts) == ["check_report", "model_xlsx"]
    assert o.event_trail[-3:] == ["building", "checking", "ready"]
    ((email, got_oid, url),) = notifier.ready
    assert (email, got_oid) == ("a@b.co", oid) and url.startswith("http://testserver/download/")
    art_id = links.verify(services.cfg.secret_key, url.rsplit("/", 1)[1])
    with session_scope(services.sessions) as s:
        art = s.get(Order, oid).artifact("model_xlsx")
        assert art.id == art_id and art.filename.endswith("-light.xlsx")
        assert services.storage.get(art.storage_key).startswith(b"PK-fake")
    assert notifier.alerts == []


def test_rejected_model_never_reaches_the_customer(services, notifier):
    def bad_check(brief, path):
        raise BuildRejected("challenger: scenario 2 year 1 rev: workbook 10 vs python 11")

    oid = paid_order(services)
    make(services, notifier, check=bad_check).run_once()
    status, jobs, arts, o = state(services, oid)
    assert status == "failed" and jobs == [("failed", 1)] and arts == []
    assert "challenger" in o.failure_reason
    assert notifier.ready == []
    ((subject, body),) = notifier.alerts
    assert oid in subject and "challenger" in body


def test_infrastructure_error_retries_with_backoff_then_fails(services, notifier):
    calls = []

    def flaky(brief, path):
        calls.append(1)
        raise TimeoutError("soffice timed out")

    oid = paid_order(services)
    pipe = make(services, notifier, generate=flaky)
    before = utcnow()
    pipe.run_once()
    status, jobs, _, _ = state(services, oid)
    assert status == "paid" and jobs == [("queued", 1)]
    with session_scope(services.sessions) as s:
        job = s.query(Job).one()
        assert job.run_after >= before + timedelta(seconds=29) and "TimeoutError" in job.last_error
    assert pipe.run_once() is False  # not due yet
    for expected_delay in (60, None):
        with session_scope(services.sessions) as s:
            s.query(Job).update({"run_after": utcnow() - timedelta(seconds=1)})
        t0 = utcnow()
        pipe.run_once()
        if expected_delay:
            with session_scope(services.sessions) as s:
                assert s.query(Job).one().run_after >= t0 + timedelta(seconds=expected_delay - 1)
    status, jobs, arts, o = state(services, oid)
    assert len(calls) == 3 and status == "failed" and jobs == [("failed", 3)] and arts == []
    assert "gave up after 3 attempts" in o.failure_reason and len(notifier.alerts) == 1


def test_retry_then_success(services, notifier):
    n = {"calls": 0}

    def once_flaky(brief, path):
        n["calls"] += 1
        if n["calls"] == 1:
            raise OSError("disk hiccup")
        fake_generate(brief, path)

    oid = paid_order(services)
    pipe = make(services, notifier, generate=once_flaky)
    pipe.run_once()
    with session_scope(services.sessions) as s:
        s.query(Job).update({"run_after": utcnow()})
    pipe.run_once()
    assert state(services, oid)[0] == "ready" and len(notifier.ready) == 1


def test_stale_running_job_is_reclaimed(services, notifier):
    oid = paid_order(services)
    pipe = make(services, notifier)
    jid = pipe.claim()
    with session_scope(services.sessions) as s:  # simulate a crash mid-build
        s.get(Order, oid).status = "building"
        s.get(Job, jid).locked_at = utcnow() - timedelta(hours=1)
    assert pipe.reclaim_stale() == 1
    status, jobs, _, _ = state(services, oid)
    assert status == "paid" and jobs == [("queued", 1)]


def test_claim_is_exclusive(services, notifier):
    paid_order(services)
    a, b = make(services, notifier), make(services, notifier)
    assert a.claim() is not None and b.claim() is None


def test_job_for_an_order_that_is_not_paid_is_skipped(services, notifier):
    oid = paid_order(services)
    with session_scope(services.sessions) as s:
        s.get(Order, oid).status = "ready"
    make(services, notifier).run_once()
    status, jobs, arts, _ = state(services, oid)
    assert status == "ready" and jobs == [("done", 1)] and arts == [] and notifier.ready == []


def test_rebuild_after_ready_delivers_again(services, notifier):
    oid = paid_order(services)
    pipe = make(services, notifier)
    pipe.run_once()
    with session_scope(services.sessions) as s:
        rebuild(s, services.cfg, s.get(Order, oid))
    pipe.run_once()
    status, jobs, arts, _ = state(services, oid)
    assert status == "ready" and jobs == [("done", 1), ("done", 1)] and arts.count("model_xlsx") == 2
    assert len(notifier.ready) == 2


def test_notification_failure_does_not_lose_the_model(services):
    class Broken:
        def model_ready(self, *a):
            raise ConnectionError("smtp down")

        def admin_alert(self, *a):
            pass

    oid = paid_order(services)
    make(services, Broken()).run_once()
    assert state(services, oid)[0] == "ready"


@pytest.mark.parametrize(
    "name,expected", [("Acme Advisory — financial model", "acme-advisory-financial-model-light.xlsx")]
)
def test_filename(name, expected):
    from worker.pipeline import _filename

    b = PrefillBriefSource().build_brief(Answers(**ANSWERS)).model_copy(update={"model_name": name})
    assert _filename(b) == expected
