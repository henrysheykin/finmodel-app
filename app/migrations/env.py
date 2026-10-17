"""Alembic environment: URL from the Alembic config (programmatic) or DATABASE_URL."""

from __future__ import annotations

import os

from alembic import context
from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401  (registers tables on Base.metadata)
from app.db import Base

config = context.config
url = config.get_main_option("sqlalchemy.url") or os.environ.get("DATABASE_URL") or "sqlite:///./dev.db"
config.set_main_option("sqlalchemy.url", url)
target_metadata = Base.metadata


def run_offline() -> None:
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


def run_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section) or {}, prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata, render_as_batch=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_offline()
else:
    run_online()
