"""Fitness studio / gym template economics in the plain-Python twin (no LibreOffice)."""

import pytest

from engine.challenger import python_model
from engine.core import reference_run
from engine.spec import Timing
from engine.templates import get_template

FIT = get_template("fitness")
STAGES = ["planning", "early", "growing", "established"]


@pytest.fixture
def fit_brief():
    return FIT.default_brief("early")


def run(brief, scen=2, g="monthly", years=3):
    return reference_run(brief.values(scen), brief.roles, Timing(g, years), FIT.reference_top)


def with_values(brief, **vals):
    d = brief.model_dump()
    for drv in d["drivers"]:
        if drv["key"] in vals:
            v = vals[drv["key"]]
            drv.update(low=v, base=v, high=v)
    return brief.model_validate(d)


@pytest.mark.parametrize("stage", STAGES)
def test_stage_defaults_are_valid_ordered_and_funded(stage):
    b = FIT.default_brief(stage)
    low, base, high = (python_model(b, s) for s in (1, 2, 3))
    for y in (1, 2, 3):
        assert low["rev"][y] < base["rev"][y] < high["rev"][y]
        assert base["members_close"][y] <= b.values(2)["max_members"] + 1e-9
    assert min(base["cash_close"].values()) > 0  # the Base case is funded; Low is the stress case


def test_member_roll_forward(fit_brief):
    d = fit_brief.values(2)
    roomy = with_values(fit_brief, max_members=1e6)
    s = run(roomy)
    new = d["mkt"] / d["cpl"] * d["conv"] + d["ref_new"]
    m1 = d["members_start"] * (1 - d["churn_m"]) + new
    assert s["members_close"][0] == pytest.approx(m1)
    assert s["members_close"][1] == pytest.approx(m1 * (1 - d["churn_m"]) + new)
    assert s["capped"][0] == pytest.approx(0)


def test_capacity_caps_the_base_and_counts_lost_joins(fit_brief):
    d = fit_brief.values(2)
    tight = with_values(fit_brief, max_members=d["members_start"])
    s = run(tight)
    assert max(s["members_close"]) == pytest.approx(d["members_start"])
    assert s["capped"][0] > 0
    # joining fees are only earned on members who actually join
    roomy = run(with_values(fit_brief, max_members=1e6))
    assert s["rev"][0] < roomy["rev"][0]


def test_revenue_streams_scale_with_the_average_base(fit_brief):
    d = fit_brief.values(2)
    b = with_values(fit_brief, max_members=1e6, join_fee=0)
    s = run(b)
    m0, m1 = d["members_start"], s["members_close"][0]
    avg = (m0 + m1) / 2
    per_member = d["fee"] + d["pt_share"] * d["pt_sessions"] * d["pt_rate"] + d["retail_pm"]
    assert s["rev"][0] == pytest.approx(avg * per_member)


def test_instructors_and_payouts_are_cost_of_sales(fit_brief):
    d = fit_brief.values(2)
    s = run(with_values(fit_brief, pt_share=0, retail_pm=0))
    assert s["cogs"][0] == pytest.approx(-d["classes_wk"] * 52 / 12 * d["class_cost"])


def test_annual_approximates_monthly(fit_brief):
    """Annual columns compound the monthly cancellation rate; joins arrive mid-year (same as SaaS)."""
    b = with_values(fit_brief, max_members=1e6)
    m, a = python_model(b, 2), python_model(b.with_options(granularity="annual"), 2)
    for y in (1, 2, 3):
        assert a["members_close"][y] == pytest.approx(m["members_close"][y], rel=0.05)
        assert a["rev"][y] == pytest.approx(m["rev"][y], rel=0.08)


@pytest.mark.parametrize("g", ["monthly", "annual"])
@pytest.mark.parametrize("scen", [1, 2, 3])
def test_balance_sheet_balances(fit_brief, g, scen):
    s = run(fit_brief, scen, g)
    for ta, tle in zip(s["total_assets"], s["total_le"], strict=True):
        assert ta == pytest.approx(tle, abs=1e-6)


def test_zero_cost_per_lead_is_guarded(fit_brief):
    s = run(with_values(fit_brief, cpl=0))
    assert all(v >= 0 for v in s["members_close"])
