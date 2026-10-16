import json
import os
import shutil
from pathlib import Path

import pytest

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
def cafe_brief() -> dict:
    return json.loads(CAFE_BRIEF.read_text(encoding="utf-8"))


@pytest.fixture
def cafe_xlsx(tmp_path, cafe_brief) -> Path:
    from engine.templates import cafe

    out = tmp_path / "cafe.xlsx"
    cafe.build(cafe_brief, str(out))
    return out
