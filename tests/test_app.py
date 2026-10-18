from fastapi.testclient import TestClient

from app import __version__
from app.main import app


def test_healthz():
    r = TestClient(app).get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "version": __version__}
