import pytest
from openpyxl import load_workbook

from engine.builder import FIRST_COL, plan
from engine.challenger import challenge
from engine.templates import get_template

pytestmark = pytest.mark.libreoffice


def cell_of(brief, key, p):
    pl = plan(brief, get_template(brief.template))
    sheet, row = pl.line_at[key]
    return sheet, row, FIRST_COL + p - 1


def tamper(path, brief, key, p, fn):
    sheet, row, col = cell_of(brief, key, p)
    wb = load_workbook(path)
    c = wb[sheet].cell(row=row, column=col)
    c.value = fn(c.value)
    wb.save(path)


def test_cafe_full_monthly_passes(cafe_brief, cafe_xlsx):
    report = challenge(cafe_brief, cafe_xlsx)
    assert report["problems"] == []
    assert report["verdict"] == "PASS"
    assert set(report["scenarios"]) == {1, 2, 3}
    for s in (1, 2, 3):
        assert report["scenarios"][s]["verdict"] in ("PASS", "PASS WITH WARNINGS")
        assert len(report["scenarios"][s]["years"]) == 3


def test_wrong_revenue_formula_is_caught(cafe_brief, cafe_xlsx):
    tamper(cafe_xlsx, cafe_brief, "rev", 5, lambda v: v + "*1.01")
    report = challenge(cafe_brief, cafe_xlsx)
    assert report["verdict"] == "FAIL"
    assert any("year 1 rev" in p for p in report["problems"])


def test_broken_balance_sheet_is_caught(cafe_brief, cafe_xlsx):
    # paid-in capital forgets the equity raised: assets no longer equal liabilities + equity
    tamper(cafe_xlsx, cafe_brief, "paid_in", 1, lambda v: "=0")
    report = challenge(cafe_brief, cafe_xlsx)
    assert report["verdict"] == "FAIL"
    assert any("balance sheet off" in p for p in report["problems"])
    assert any("in-file checks 'FAIL'" in p for p in report["problems"])


def test_brief_mismatch_is_caught(cafe_brief, cafe_xlsx):
    d = cafe_brief.model_dump()
    for drv in d["drivers"]:
        if drv["key"] == "ticket":
            drv["base"] = 6.75
    report = challenge(d, cafe_xlsx)
    assert report["verdict"] == "FAIL"
    assert any(p.startswith("scenario 2") for p in report["problems"])


def test_formula_error_fails(cafe_brief, cafe_xlsx):
    tamper(cafe_xlsx, cafe_brief, "ticket", 3, lambda v: "=1/0")
    report = challenge(cafe_brief, cafe_xlsx)
    assert report["verdict"] == "FAIL"
    assert any("recalc" in p for p in report["problems"])
