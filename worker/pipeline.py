"""The delivery pipeline: claim a build job, generate, recalculate, challenge, store, notify.

A model reaches the customer only when the challenger says PASS. Deterministic failures
(invalid brief, formula errors, challenger mismatch) fail the order at once and alert the
admin; infrastructure errors (LibreOffice timeout, storage outage) are retried with
exponential backoff up to ``max_attempts``.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import tempfile
import traceback
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import timedelta
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.orm import Session, sessionmaker

from adapters.notify import Notifier
from adapters.storage import Storage
from app import links
from app.config import Settings
from app.db import session_scope, utcnow
from app.models import Artifact, Job, Order
from app.orders import brief_of, transition
from engine.brief import Brief, BriefError

log = logging.getLogger("worker")
XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class BuildRejected(Exception):
    """The model was built but must not be delivered (deterministic: retrying will not help)."""


# --------------------------------------------------------------------------- build steps
def generate(brief: Brief, path: Path) -> None:
    """Write the workbook and recalculate it; any formula error rejects the build."""
    from engine.build import build_model
    from engine.recalc import recalc

    build_model(brief, path)
    res = recalc(path, 120)
    if not res.ok:
        raise BuildRejected(f"formula errors after recalculation: {res.errors}")


def check(brief: Brief, path: Path) -> dict:
    """Independent challenger; anything but PASS rejects the build."""
    from engine.challenger import challenge

    report = challenge(brief, path)
    if report["verdict"] != "PASS":
        raise BuildRejected("challenger: " + "; ".join(report["problems"][:10]))
    return report


@dataclass
class Pipeline:
    sessions: sessionmaker[Session]
    cfg: Settings
    storage: Storage
    notifier: Notifier
    worker_id: str = "worker-1"
    # stored as instance attributes so tests can swap in fakes
    generate: Callable[[Brief, Path], None] = field(default_factory=lambda: generate)
    check: Callable[[Brief, Path], dict] = field(default_factory=lambda: check)

    # ------------------------------------------------------------------ queue
    def reclaim_stale(self) -> int:
        """Jobs stuck in 'running' past the timeout (worker crashed) go back to the queue."""
        cutoff = utcnow() - timedelta(seconds=self.cfg.job_timeout_seconds)
        n = 0
        with session_scope(self.sessions) as s:
            stale = s.scalars(select(Job).where(Job.status == "running", Job.locked_at < cutoff)).all()
            for job in stale:
                self._retry_or_fail(s, job, "worker timed out or crashed")
                n += 1
        return n

    def claim(self) -> int | None:
        """Atomically take the oldest due job (works on SQLite and Postgres)."""
        with session_scope(self.sessions) as s:
            ids = s.scalars(
                select(Job.id).where(Job.status == "queued", Job.run_after <= utcnow()).order_by(Job.id).limit(5)
            ).all()
            for jid in ids:
                res = s.execute(
                    update(Job)
                    .where(Job.id == jid, Job.status == "queued")
                    .values(status="running", locked_by=self.worker_id, locked_at=utcnow(), attempts=Job.attempts + 1)
                )
                if res.rowcount == 1:
                    return jid
        return None

    def run_once(self) -> bool:
        """Process at most one job. Returns True if a job was processed."""
        self.reclaim_stale()
        jid = self.claim()
        if jid is None:
            return False
        self.process(jid)
        return True

    # ------------------------------------------------------------------ one job
    def process(self, job_id: int) -> None:
        with session_scope(self.sessions) as s:
            job = s.get(Job, job_id)
            order = job.order
            if order.status != "paid":
                # superseded round or already handled: nothing to deliver twice
                job.status, job.finished_at = "done", utcnow()
                job.last_error = f"skipped: order is {order.status}"
                return
            transition(s, order, "building", f"job {job.id} attempt {job.attempts}")
            brief_json, order_id = order.brief_json, order.id
        try:
            brief = Brief.model_validate_json(brief_json)
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "model.xlsx"
                self.generate(brief, path)
                with session_scope(self.sessions) as s:
                    transition(s, s.get(Order, order_id), "checking", f"job {job_id}")
                report = self.check(brief, path)
                data = path.read_bytes()
            self._deliver(job_id, order_id, brief, data, report)
        except (BuildRejected, BriefError) as exc:
            self._fail(job_id, f"{type(exc).__name__}: {exc}")
        except Exception as exc:  # infrastructure: retry
            log.exception("job %s attempt failed", job_id)
            with session_scope(self.sessions) as s:
                job = s.get(Job, job_id)
                self._retry_or_fail(s, job, f"{type(exc).__name__}: {exc}\n{traceback.format_exc(limit=5)}")

    def _deliver(self, job_id: int, order_id: str, brief: Brief, data: bytes, report: dict) -> None:
        name = _filename(brief)
        base = f"orders/{order_id}/{job_id}"
        rep = json.dumps(report, indent=2, default=str).encode()
        self.storage.put(f"{base}/{name}", data, XLSX)
        self.storage.put(f"{base}/check-report.json", rep, "application/json")
        with session_scope(self.sessions) as s:
            order, job = s.get(Order, order_id), s.get(Job, job_id)
            model = Artifact(
                order_id=order_id,
                kind="model_xlsx",
                storage_key=f"{base}/{name}",
                filename=name,
                content_type=XLSX,
                sha256=hashlib.sha256(data).hexdigest(),
                size=len(data),
            )
            s.add(model)
            s.add(
                Artifact(
                    order_id=order_id,
                    kind="check_report",
                    storage_key=f"{base}/check-report.json",
                    filename="check-report.json",
                    content_type="application/json",
                    sha256=hashlib.sha256(rep).hexdigest(),
                    size=len(rep),
                )
            )
            s.flush()
            transition(s, order, "ready", f"job {job_id}: challenger PASS")
            job.status, job.finished_at, job.last_error = "done", utcnow(), None
            email, artifact_id = order.email, model.id
        token = links.sign(self.cfg.secret_key, artifact_id, self.cfg.link_ttl_seconds)
        url = f"{self.cfg.public_base_url}/download/{token}"
        try:
            self.notifier.model_ready(email, order_id, url)
        except Exception:  # the file is safe in storage; the customer can re-download (E19)
            log.exception("model_ready notification failed for order %s", order_id)

    def _fail(self, job_id: int, reason: str) -> None:
        with session_scope(self.sessions) as s:
            job = s.get(Job, job_id)
            self._fail_in(s, job, reason)

    def _fail_in(self, s: Session, job: Job, reason: str) -> None:
        order = job.order
        job.status, job.finished_at, job.last_error = "failed", utcnow(), reason[:4000]
        if order.status != "failed":
            transition(s, order, "failed", reason)
        order.failure_reason = reason[:4000]
        s.flush()
        try:
            self.notifier.admin_alert(
                f"Build failed: order {order.id}",
                f"Order {order.id} ({order.template}, {order.tier}, {order.email})\n"
                f"Job {job.id}, attempt {job.attempts}/{job.max_attempts}\n\n{reason}",
            )
        except Exception:
            log.exception("admin alert failed for order %s", order.id)
        try:
            self.notifier.build_failed(order.id)
        except Exception:
            log.exception("build-failed email failed for order %s", order.id)

    def _retry_or_fail(self, s: Session, job: Job, reason: str) -> None:
        order = job.order
        if job.attempts >= job.max_attempts:
            self._fail_in(s, job, f"gave up after {job.attempts} attempts: {reason}")
            return
        delay = self.cfg.job_backoff_seconds * 2 ** max(0, job.attempts - 1)
        job.status, job.locked_by, job.locked_at = "queued", None, None
        job.run_after = utcnow() + timedelta(seconds=delay)
        job.last_error = reason[:4000]
        if order.status in ("building", "checking"):
            transition(s, order, "paid", f"retry in {delay}s: {reason.splitlines()[0][:200]}")


def _filename(brief: Brief) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", brief.model_name.lower()).strip("-")[:60] or "financial-model"
    return f"{slug}-{brief.tier}.xlsx"


__all__ = ["BuildRejected", "Pipeline", "brief_of", "check", "generate"]
