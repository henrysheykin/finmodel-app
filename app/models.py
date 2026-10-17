"""Orders, build jobs and stored artifacts."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base, utcnow


def _uuid() -> str:
    return uuid.uuid4().hex


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(254), index=True)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    template: Mapped[str] = mapped_column(String(40))
    tier: Mapped[str] = mapped_column(String(10))
    price_cents: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    answers_json: Mapped[str] = mapped_column(Text, default="{}")
    brief_json: Mapped[str] = mapped_column(Text)
    #: provider payment id (e.g. Stripe Checkout session); unique so a payment is applied once
    payment_ref: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    payment_intent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    refund_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    failure_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=utcnow, onupdate=utcnow)
    paid_at: Mapped[datetime | None] = mapped_column(nullable=True)
    ready_at: Mapped[datetime | None] = mapped_column(nullable=True)
    refunded_at: Mapped[datetime | None] = mapped_column(nullable=True)

    jobs: Mapped[list[Job]] = relationship(back_populates="order", order_by="Job.id")
    artifacts: Mapped[list[Artifact]] = relationship(back_populates="order", order_by="Artifact.created_at")
    events: Mapped[list[OrderEvent]] = relationship(back_populates="order", order_by="OrderEvent.id")

    def artifact(self, kind: str) -> Artifact | None:
        found = [a for a in self.artifacts if a.kind == kind]
        return found[-1] if found else None


class OrderEvent(Base):
    """Audit trail of status changes."""

    __tablename__ = "order_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    from_status: Mapped[str] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20))
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    order: Mapped[Order] = relationship(back_populates="events")


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_jobs_idempotency_key"),
        Index("ix_jobs_pick", "status", "run_after"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    kind: Mapped[str] = mapped_column(String(20), default="build")
    #: queued | running | done | failed
    status: Mapped[str] = mapped_column(String(10), default="queued")
    idempotency_key: Mapped[str] = mapped_column(String(80))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    run_after: Mapped[datetime] = mapped_column(default=utcnow)
    locked_by: Mapped[str | None] = mapped_column(String(80), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)

    order: Mapped[Order] = relationship(back_populates="jobs")


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
    #: model_xlsx | check_report
    kind: Mapped[str] = mapped_column(String(20))
    storage_key: Mapped[str] = mapped_column(String(255))
    filename: Mapped[str] = mapped_column(String(120))
    content_type: Mapped[str] = mapped_column(String(100))
    sha256: Mapped[str] = mapped_column(String(64))
    size: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    order: Mapped[Order] = relationship(back_populates="artifacts")


class Customer(Base):
    """A person who signs in by magic link. Orders belong to a customer through the checkout email."""

    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(254), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)


class LoginToken(Base):
    """Single-use magic-link token; only its SHA-256 is stored."""

    __tablename__ = "login_tokens"
    __table_args__ = (Index("ix_login_tokens_email_created", "email", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(254))
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    ip: Mapped[str] = mapped_column(String(64), default="", index=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    expires_at: Mapped[datetime] = mapped_column()
    used_at: Mapped[datetime | None] = mapped_column(nullable=True)


class CustomerSession(Base):
    """Server-side session; the cookie carries a random token, the DB only its SHA-256."""

    __tablename__ = "customer_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[str] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    expires_at: Mapped[datetime] = mapped_column()
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    user_agent: Mapped[str] = mapped_column(String(200), default="")
