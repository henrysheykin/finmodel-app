"""SaaS template economics in the plain-Python twin (no LibreOffice)."""

import pytest

from engine.challenger import python_model
from engine.core import reference_run
from engine.spec import Timing
from engine.templates import get_template

SAAS = get_template("saas")
STAGES = ["planning", "early", "growing", "established"]


def run(brief, scen=2, g="monthly", years=3):
    return reference_run(brief.values(scen), brief.roles, Timing(g, years), SAAS.reference_top)


@pytest.mark.parametrize("stage", STAGES)
def test_stage_defaults_are_valid_and_ordered(stage):
    b = SAAS.default_brief(stage)
    SAAS.validate(b)
    low, base, high = (python_model(b, s) for s in (1, 2, 3))
    for y in (1, 2, 3):
        assert low["rev"][y] < base["rev"][y] < high["rev"][y]


@pytest.mark.parametrize("g", ["monthly", "annual"])
def test_customer_and_mrr_roll_forward(saas_brief, g):
    d = saas_brief.values(2)
    s = run(saas_brief, g=g)
    assert s["cust_close"][0] > d["start_customers"]
    # MRR per customer never exceeds what price growth + expansion can explain
    for c, m in zip(s["cust_close"], s["mrr_close"], strict=True):
        assert 0 < m / c < d["arpa"] * 3


@pytest.mark.parametrize("g", ["monthly", "annual"])
@pytest.mark.parametrize("scen", [1, 2, 3])
def test_balance_sheet_balances_with_deferred_revenue(saas_brief, g, scen):
    s = run(saas_brief, scen, g)
    assert max(s["defrev"]) > 0
    for ta, tle in zip(s["total_assets"], s["total_le"], strict=True):
        assert ta == pytest.approx(tle, abs=1e-6)


def test_deferred_revenue_is_half_a_year_of_annual_plans(saas_brief):
    d = saas_brief.values(2)
    s = run(saas_brief)
    assert s["defrev"][-1] == pytest.approx(s["mrr_close"][-1] * d["annual_pct"] * 6)


def test_monthly_and_annual_close(saas_brief):
    """Annual columns compound the same monthly rates; results stay within a few percent."""
    m = python_model(saas_brief, 2)
    a = python_model(saas_brief.with_options(granularity="annual"), 2)
    for y in (1, 2, 3):
        assert a["rev"][y] == pytest.approx(m["rev"][y], rel=0.08)
        assert a["cust_close"][y] == pytest.approx(m["cust_close"][y], rel=0.05)
        assert a["payroll_total"][y] == pytest.approx(m["payroll_total"][y], abs=0.01)


def test_zero_churn_and_no_marketing(saas_brief):
    d = saas_brief.model_dump()
    for drv in d["drivers"]:
        if drv["key"] in ("churn_m", "mkt_budget", "expansion_m"):
            drv.update(low=0, base=0, high=0)
    b = saas_brief.model_validate(d)
    s = run(b)
    assert s["cust_close"][11] == pytest.approx(b.values(2)["start_customers"] + 12 * b.values(2)["organic_new"])


def test_headcount_grows_each_year(saas_brief):
    s = run(saas_brief, years=3)
    assert s["fte_total"][0] < s["fte_total"][12] < s["fte_total"][24]
    assert s["fte_total"][0] == s["fte_total"][11]
