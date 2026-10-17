import os
import shutil
from pathlib import Path

import pytest

from engine.brief import Brief
from engine.templates import TEMPLATES

ROOT = Path(__file__).resolve().parents[1]
CAFE_BRIEF = ROOT / "engine" / "briefs" / "cafe.json"


def pytest_collection_modifyitems(config, items):
    """Skip LibreOffice tests when soffice is missing, unless CI requires it."""
    if shutil.which(os.environ.get("SOFFICE_BIN") or "soffice"):
        return
    if os.environ.get("REQUIRE_LIBREOFFICE") == "1":
        raise pytest.UsageError("REQUIRE_LIBREOFFICE=1 but soffice is not on PATH")
    skip = pytest.mark.skip(reason="soffice not installed")
    for item in items:
        if "libreoffice" in item.keywords:
            item.add_marker(skip)


@pytest.fixture
def cafe_brief() -> Brief:
    return Brief.load(CAFE_BRIEF)


@pytest.fixture
def build(tmp_path):
    from engine.build import build_model

    def _build(brief: Brief, name: str = "model.xlsx") -> Path:
        out = tmp_path / name
        build_model(brief, out)
        return out

    return _build


@pytest.fixture
def cafe_xlsx(build, cafe_brief) -> Path:
    return build(cafe_brief, "cafe.xlsx")


@pytest.fixture(params=sorted(TEMPLATES))
def any_brief(request, cafe_brief) -> Brief:
    """Every registered template (ADR-009): the cafe sample brief, the 'early' defaults of the rest."""
    if request.param == "cafe":
        return cafe_brief
    from engine.templates import get_template

    return get_template(request.param).default_brief("early")


@pytest.fixture
def saas_brief() -> Brief:
    from engine.templates import get_template

    return get_template("saas").default_brief("early")


@pytest.fixture
def retail_brief() -> Brief:
    from engine.templates import get_template

    return get_template("retail").default_brief("growing")


@pytest.fixture
def services_brief() -> Brief:
    from engine.templates import get_template

    return get_template("services").default_brief("growing")


# --------------------------------------------------------------------------- app / pipeline
@pytest.fixture
def services(tmp_path):
    """Fresh migrated SQLite DB, local storage in tmp, test settings."""
    from adapters.storage import LocalStorage
    from app.briefing import PrefillBriefSource
    from app.config import Settings
    from app.db import make_engine, make_sessionmaker, migrate
    from app.main import Services

    url = f"sqlite:///{tmp_path / 'test.db'}"
    migrate(url)
    cfg = Settings(
        database_url=url,
        secret_key="test-secret-key-0123456789abcdef0123456789",
        public_base_url="http://testserver",
        storage_dir=str(tmp_path / "storage"),
        job_backoff_seconds=30,
    )
    from adapters.notify import RecordingNotifier
    from adapters.payments import FakeProvider

    return Services(
        cfg,
        make_sessionmaker(make_engine(url)),
        LocalStorage(cfg.storage_dir),
        PrefillBriefSource(),
        FakeProvider("http://testserver"),
        RecordingNotifier(),
    )


@pytest.fixture
def notifier(services):
    return services.notifier


@pytest.fixture
def client(services):
    from fastapi.testclient import TestClient

    from app.main import create_app

    with TestClient(create_app(services)) as c:
        yield c


ANSWERS = {
    "business_type": "professional_services",
    "stage": "early",
    "tier": "light",
    "horizon_years": 1,
    "business_name": "Acme Advisory",
}
