"""Retail / e-commerce template economics in the plain-Python twin (no LibreOffice)."""

import pytest

from engine.challenger import python_model
from engine.core import reference_run
from engine.spec import Timing
from engine.templates import get_template

RETAIL = get_template("retail")
STAGES = ["planning", "early", "growing", "established"]


def run(brief, scen=2, g="monthly", years=3):
    return reference_run(brief.values(scen), brief.roles, Timing(g, years), RETAIL.reference_top)


def with_values(brief, **vals):
    d = brief.model_dump()
    for drv in d["drivers"]:
        if drv["key"] in vals:
            v = vals[drv["key"]]
            drv.update(low=v, base=v, high=v)
    return brief.model_validate(d)


@pytest.mark.parametrize("stage", STAGES)
def test_stage_defaults_are_valid_and_ordered(stage):
    b = RETAIL.default_brief(stage)
    low, base, high = (python_model(b, s) for s in (1, 2, 3))
    for y in (1, 2, 3):
        assert low["rev"][y] < base["rev"][y] < high["rev"][y]


@pytest.mark.parametrize("stage", STAGES)
def test_monthly_and_annual_agree_exactly(stage):
    """Seasonality averages to 1 and all rates change yearly, so annual = sum of months."""
    b = RETAIL.default_brief(stage)
    m, a = python_model(b, 2), python_model(b.with_options(granularity="annual"), 2)
    for k in ("rev", "gp", "ebitda", "payroll_total", "orders"):
        for y in (1, 2, 3):
            assert m[k][y] == pytest.approx(a[k][y], abs=0.01), (k, y)


def test_seasonality_shifts_sales_into_q4_but_keeps_the_year(retail_brief):
    s = run(retail_brief)
    year1 = s["rev"][:12]
    assert year1[10] > year1[0] and year1[11] > year1[9]
    flat = run(with_values(retail_brief, q4_uplift=0))
    assert sum(year1) == pytest.approx(sum(flat["rev"][:12]))


def test_inventory_follows_product_cost_days(retail_brief):
    d = retail_brief.values(2)
    s = run(retail_brief, g="annual")
    for cogs, inv in zip(s["cogs"], s["inv"], strict=True):
        assert inv == pytest.approx(-cogs * d["inv_days"] / 360)


def test_store_openings_add_capex_each_year(retail_brief):
    d = retail_brief.values(2)
    s = run(retail_brief)
    assert s["capex"][0] == pytest.approx(d["capex"] + d["stores"] * d["fitout"])
    assert s["capex"][12] == pytest.approx(d["stores_add"] * d["fitout"])
    assert sum(1 for c in s["capex"] if c) == 3
    assert s["stores"][-1] == d["stores"] + 2 * d["stores_add"]


def test_online_only_and_store_only(retail_brief):
    online = run(with_values(retail_brief, stores=0, stores_add=0))
    stores = run(with_values(retail_brief, visits=0, ad_budget=0))
    both = run(retail_brief)
    for y in range(36):
        assert online["rev"][y] + stores["rev"][y] == pytest.approx(both["rev"][y])
    assert min(stores["orders"]) == 0


@pytest.mark.parametrize("scen", [1, 2, 3])
def test_balance_sheet_balances(retail_brief, scen):
    s = run(retail_brief, scen)
    for ta, tle in zip(s["total_assets"], s["total_le"], strict=True):
        assert ta == pytest.approx(tle, abs=1e-6)
