"""Deploy plumbing: database URL normalisation, ops commands, start script, image contents."""

import shutil
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import normalize_database_url
from app.main import create_app
from app.manage import main as manage_main

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("given", "expected"),
    [
        ("postgres://u:p@host:5432/db", "postgresql+psycopg://u:p@host:5432/db"),
        ("postgresql://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("postgresql+psycopg://u:p@host/db", "postgresql+psycopg://u:p@host/db"),
        ("sqlite:///./dev.db", "sqlite:///./dev.db"),
    ],
)
def test_database_url_gets_the_psycopg_driver(given, expected):
    assert normalize_database_url(given) == expected


def test_manage_migrate_and_check(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/ops.db")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    assert manage_main(["migrate"]) == 0
    assert (tmp_path / "ops.db").exists()
    assert manage_main(["check"]) == 0
    out = capsys.readouterr().out
    assert "stripe=test" in out and "sk_test_x" not in out  # never print secrets


def test_security_headers(services):
    with TestClient(create_app(services)) as c:
        r = c.get("/healthz")
    assert r.headers["X-Content-Type-Options"] == "nosniff"
    assert r.headers["X-Frame-Options"] == "DENY"
    assert "Referrer-Policy" in r.headers


@pytest.mark.skipif(shutil.which("bash") is None, reason="bash not available")
def test_start_script_is_valid_bash():
    subprocess.run(["bash", "-n", str(ROOT / "deploy" / "start.sh")], check=True)


def test_image_ships_runtime_folders():
    """The app reads emails from content/ and assets from web/ at run time; the image must copy both."""
    docker = (ROOT / "Dockerfile").read_text()
    for folder in ("content", "web", "deploy", "engine", "app", "worker", "adapters"):
        assert f"COPY {folder} ./{folder}" in docker, folder
