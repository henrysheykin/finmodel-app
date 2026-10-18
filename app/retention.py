"""Data retention promised in content/legal/privacy.md ("How long we keep it").

- orders that were never paid (draft, awaiting_payment): deleted 12 months after creation;
- sign-in link tokens and customer sessions: deleted 12 months after they expired.

Paid orders stay (accounting records). Runs on every container start (deploy/start.sh) through
``python -m app.manage purge``; deleting is idempotent, so running it often is harmless.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.db import utcnow
from app.models import Artifact, CustomerSession, Job, LoginToken, Order, OrderEvent

KEEP = timedelta(days=365)
UNPAID = ("draft", "awaiting_payment")


def purge(s: Session, now: datetime | None = None) -> dict[str, int]:
    cutoff = (now or utcnow()) - KEEP
    out = {}
    ids = list(s.scalars(select(Order.id).where(Order.status.in_(UNPAID), Order.created_at < cutoff)))
    for chunk in (ids[i : i + 500] for i in range(0, len(ids), 500)):
        # children first: works whether or not the database enforces ON DELETE CASCADE
        for child in (OrderEvent, Job, Artifact):
            s.execute(delete(child).where(child.order_id.in_(chunk)))
        s.execute(delete(Order).where(Order.id.in_(chunk)))
    out["unpaid_orders"] = len(ids)
    out["login_tokens"] = s.execute(delete(LoginToken).where(LoginToken.expires_at < cutoff)).rowcount
    out["sessions"] = s.execute(delete(CustomerSession).where(CustomerSession.expires_at < cutoff)).rowcount
    return out
