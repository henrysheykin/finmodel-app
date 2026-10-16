"""Plain-Python reference model: accounting identities and golden numbers (no LibreOffice)."""

import itertools
import json
from pathlib import Path

import pytest

from engine.challenger import python_model
from engine.core import reference_run
from engine.spec import Timing
from engine.templates import get_template

GOLDEN = Path(__file__).parent / "golden" / "cafe.json"
COMBOS = list(itertools.product(["monthly", "annual"], [1, 3, 5]))


@pytest.mark.parametrize("g,years", COMBOS)
@pytest.mark.parametrize("scen", [1, 2, 3])
def test_balance_sheet_balances_every_period(cafe_brief, g, years, scen):
    t = Timing(g, years)
    s = reference_run(cafe_brief.values(scen), cafe_brief.roles, t, get_template("cafe").reference_top)
    for ta, tle in zip(s["total_assets"], s["total_le"], strict=True):
        assert abs(ta - tle) < 1e-6


@pytest.mark.parametrize("years", [1, 3, 5])
def test_monthly_and_annual_agree_on_operations(cafe_brief, years):
    for scen in (1, 2, 3):
        m = python_model(cafe_brief.with_options(horizon_years=years), scen)
        a = python_model(cafe_brief.with_options(horizon_years=years, granularity="annual"), scen)
        for k in ("rev", "gp", "ebitda", "payroll_total"):
            for y in range(1, years + 1):
                assert m[k][y] == pytest.approx(a[k][y], abs=0.01), (k, y)


def test_losses_carried_forward(cafe_brief):
    t = Timing("monthly", 3)
    s = reference_run(cafe_brief.values(2), cafe_brief.roles, t, get_template("cafe").reference_top)
    assert sum(s["tax"]) == pytest.approx(-max(0.0, max_cum(s["ebt"])) * 0.21, abs=0.01)
    assert all(x <= 1e-9 for x in s["tax"])


def max_cum(xs):
    run, peak = 0.0, 0.0
    for x in xs:
        run += x
        peak = max(peak, run)
    return peak


def test_loan_fully_repaid(cafe_brief):
    s = reference_run(cafe_brief.values(2), cafe_brief.roles, Timing("monthly", 5), get_template("cafe").reference_top)
    assert s["loan_close"][-1] == pytest.approx(80000 - 80000 / 60 * 59)
    assert min(s["loan_close"]) >= 0


def golden_values(brief) -> dict:
    out = {}
    for g, years in COMBOS:
        b = brief.with_options(granularity=g, horizon_years=years)
        res = python_model(b, 2)
        out[f"{g}-{years}"] = {
            k: {str(y): round(v, 2) for y, v in res[k].items()}
            for k in ("rev", "ebitda", "ni", "cash_close", "total_assets")
        }
    return out


def test_golden_numbers(cafe_brief):
    """Regenerate with: python -m tests.regen_golden (only after a reviewed, intended change)."""
    expected = json.loads(GOLDEN.read_text())
    got = golden_values(cafe_brief)
    assert got.keys() == expected.keys()
    for combo, metrics in expected.items():
        for k, years in metrics.items():
            for y, v in years.items():
                assert got[combo][k][y] == pytest.approx(v, abs=1.0), (combo, k, y)
