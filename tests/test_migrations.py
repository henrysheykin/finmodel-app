"""Alembic migrations create exactly the schema the models describe."""

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine, inspect

import app.models  # noqa: F401
from app.db import Base, migrate


def test_migrations_match_models(tmp_path):
    url = f"sqlite:///{tmp_path / 'm.db'}"
    migrate(url)
    migrate(url)  # idempotent
    eng = create_engine(url)
    assert {"orders", "jobs", "artifacts", "order_events", "alembic_version"} <= set(inspect(eng).get_table_names())
    with eng.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == []
