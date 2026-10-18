"""scripts/load_test.py (E17): the order mix covers the catalogue, and a 2-order run completes."""

import importlib.util
import json
from pathlib import Path

import pytest

from app import wizard

ROOT = Path(__file__).resolve().parents[1]


def _script():
    spec = importlib.util.spec_from_file_location("load_test", ROOT / "scripts" / "load_test.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_mix_of_fifty_covers_every_industry_and_shape():
    mix = _script().order_mix(50)
    assert len({m["email"] for m in mix}) == 50
    available = {bt for bt, _ in wizard.BUSINESS_TYPES if wizard.available(bt)}
    assert {m["business_type"] for m in mix} == available
    assert {(m["tier"], m["horizon_years"], m["granularity"]) for m in mix} == {
        ("light", "1", "monthly"),
        ("full", "3", "monthly"),
        ("full", "5", "annual"),
        ("full", "5", "monthly"),
    }


@pytest.mark.libreoffice
def test_two_orders_end_to_end(tmp_path):
    out = tmp_path / "result.json"
    assert _script().main(["--orders", "2", "--timeout", "300", "--out", str(out)]) == 0
    r = json.loads(out.read_text())
    assert r["ready"] == 2 and r["build_jobs"] == 2 and r["webhook_actions"] == {"paid": 2, "already_paid": 2}
