import os
import shutil
from pathlib import Path

import pytest

from engine.brief import Brief

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


@pytest.fixture(params=["cafe", "saas", "retail"])
def any_brief(request, cafe_brief) -> Brief:
    """The cafe sample brief and the 'early' default brief of every other template."""
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
