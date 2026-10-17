"""Passwordless sign-in (ADR-006): magic-link tokens, sessions, rate limits.

Tokens and session ids are random (256 bits); only their SHA-256 is stored, so a database
leak does not let anyone sign in. Magic links are single-use and live 15 minutes.
"""

from __future__ import annotations

import hashlib
import re
import secrets
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.db import utcnow
from app.models import Customer, CustomerSession, LoginToken

TOKEN_TTL = timedelta(minutes=15)
SESSION_TTL = timedelta(days=30)
RATE_WINDOW = timedelta(minutes=15)
MAX_PER_EMAIL = 5
MAX_PER_IP = 20
EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]+\.[^@\s]{2,}$")


class LoginError(ValueError):
    pass


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def normalise_email(email: str) -> str:
    e = (email or "").strip().lower()
    if len(e) > 254 or not EMAIL_RE.match(e):
        raise LoginError("enter a valid email address")
    return e


def request_login(s: Session, email: str, ip: str) -> str | None:
    """Create a magic-link token, or None when rate-limited. Callers answer the same either way."""
    email = normalise_email(email)
    since = utcnow() - RATE_WINDOW
    by_email = s.scalar(select(func.count()).where(LoginToken.email == email, LoginToken.created_at >= since))
    by_ip = s.scalar(select(func.count()).where(LoginToken.ip == ip, LoginToken.created_at >= since))
    if by_email >= MAX_PER_EMAIL or by_ip >= MAX_PER_IP:
        return None
    token = secrets.token_urlsafe(32)
    s.add(LoginToken(email=email, token_hash=_hash(token), ip=ip[:64], expires_at=utcnow() + TOKEN_TTL))
    return token


@dataclass(frozen=True)
class NewSession:
    token: str
    customer_id: str
    email: str


def consume_login(s: Session, token: str, user_agent: str = "") -> NewSession:
    """Exchange a magic-link token for a session. Single use; expired or reused tokens fail."""
    row = s.scalar(select(LoginToken).where(LoginToken.token_hash == _hash(token or "")))
    if row is None:
        raise LoginError("this sign-in link is not valid")
    if row.used_at is not None:
        raise LoginError("this sign-in link was already used")
    if row.expires_at < utcnow():
        raise LoginError("this sign-in link has expired")
    # atomic single use even under a double click / two tabs
    res = s.execute(
        update(LoginToken).where(LoginToken.id == row.id, LoginToken.used_at.is_(None)).values(used_at=utcnow())
    )
    if res.rowcount != 1:
        raise LoginError("this sign-in link was already used")
    customer = s.scalar(select(Customer).where(Customer.email == row.email))
    if customer is None:
        customer = Customer(email=row.email)
        s.add(customer)
        s.flush()
    customer.last_login_at = utcnow()
    session_token = secrets.token_urlsafe(32)
    s.add(
        CustomerSession(
            customer_id=customer.id,
            token_hash=_hash(session_token),
            expires_at=utcnow() + SESSION_TTL,
            user_agent=(user_agent or "")[:200],
        )
    )
    return NewSession(session_token, customer.id, customer.email)


def customer_for(s: Session, session_token: str | None) -> Customer | None:
    if not session_token:
        return None
    sess = s.scalar(select(CustomerSession).where(CustomerSession.token_hash == _hash(session_token)))
    if sess is None or sess.revoked_at is not None or sess.expires_at < utcnow():
        return None
    return s.get(Customer, sess.customer_id)


def revoke(s: Session, session_token: str | None) -> None:
    if session_token:
        s.execute(
            update(CustomerSession)
            .where(CustomerSession.token_hash == _hash(session_token), CustomerSession.revoked_at.is_(None))
            .values(revoked_at=utcnow())
        )


def revoke_all(s: Session, customer_id: str) -> int:
    res = s.execute(
        update(CustomerSession)
        .where(CustomerSession.customer_id == customer_id, CustomerSession.revoked_at.is_(None))
        .values(revoked_at=utcnow())
    )
    return res.rowcount
