"""Professional services template economics in the plain-Python twin (no LibreOffice)."""

import pytest

from engine.brief import BriefError
from engine.challenger import python_model
from engine.core import reference_run
from engine.spec import Timing
from engine.templates import get_template

SERVICES = get_template("services")
STAGES = ["planning", "early", "growing", "established"]


def run(brief, scen=2, g="monthly", years=3):
    return reference_run(brief.values(scen), brief.roles, Timing(g, years), SERVICES.reference_top)


def with_values(brief, **vals):
    d = brief.model_dump()
    for drv in d["drivers"]:
        if drv["key"] in vals:
            v = vals[drv["key"]]
            drv.update(low=v, base=v, high=v)
    return brief.model_validate(d)


@pytest.mark.parametrize("stage", STAGES)
def test_stage_defaults_are_valid_and_ordered(stage):
    b = SERVICES.default_brief(stage)
    low, base, high = (python_model(b, s) for s in (1, 2, 3))
    for y in (1, 2, 3):
        assert low["rev"][y] < base["rev"][y] < high["rev"][y]
        assert 0 < low["gp"][y] / low["rev"][y] < 1


@pytest.mark.parametrize("stage", STAGES)
def test_monthly_and_annual_agree_exactly(stage):
    """Rates change yearly and hours scale with average FTE, so annual = sum of months."""
    b = SERVICES.default_brief(stage)
    m, a = python_model(b, 2), python_model(b.with_options(granularity="annual"), 2)
    for k in ("rev", "gp", "ebitda", "payroll_total", "hours", "rev_retainer"):
        for y in (1, 2, 3):
            assert m[k][y] == pytest.approx(a[k][y], abs=0.01), (k, y)


def test_revenue_is_hours_times_rate_card_after_mix(services_brief):
    d = services_brief.values(2)
    s = run(services_brief)
    fte_s, fte_c = d["senior_fte"], d["staff_fte"]
    h = d["avail_hours"] / 12
    fees = fte_s * h * d["senior_util"] * d["senior_rate"]
    fees += fte_c * h * d["staff_util"] * d["staff_rate"]
    fees += d["contractor_hours"] * d["contractor_rate"]
    mix = d["retainer_pct"] * (1 - d["retainer_disc"]) + (1 - d["retainer_pct"]) * d["realisation"]
    assert s["rev"][0] == pytest.approx(fees * mix)
    assert s["rev_retainer"][0] == pytest.approx(fees * d["retainer_pct"] * (1 - d["retainer_disc"]))


def test_all_retainer_and_all_project(services_brief):
    ret = run(with_values(services_brief, retainer_pct=1, retainer_disc=0))
    proj = run(with_values(services_brief, retainer_pct=0, realisation=1))
    for a, b, r in zip(ret["rev"], proj["rev"], ret["rev_retainer"], strict=True):
        assert a == pytest.approx(b)
        assert r == pytest.approx(a)
    assert max(proj["rev_retainer"]) == 0


def test_billable_payroll_is_cost_of_delivery(services_brief):
    """Billable staff cost sits in COGS, the rest of payroll in operating expenses."""
    no_contr = with_values(services_brief, contractor_hours=0, delivery_pct=0)
    s = run(no_contr)
    nb = run(with_values(no_contr, bd_fte=0, ops_fte=0))
    for cogs, nb_payroll in zip(s["cogs"], nb["payroll_total"], strict=True):
        assert cogs == pytest.approx(nb_payroll)


def test_contractor_vs_employee(services_brief):
    """Replacing contractor hours removes their fees and cost one for one."""
    d = services_brief.values(2)
    base, none = run(services_brief), run(with_values(services_brief, contractor_hours=0))
    h = d["contractor_hours"]
    mix = d["retainer_pct"] * (1 - d["retainer_disc"]) + (1 - d["retainer_pct"]) * d["realisation"]
    assert base["rev"][0] - none["rev"][0] == pytest.approx(h * d["contractor_rate"] * mix)
    fee_delta = base["rev"][0] - none["rev"][0]
    cost_delta = -(h * d["contractor_cost"]) - fee_delta * d["delivery_pct"]
    assert base["cogs"][0] - none["cogs"][0] == pytest.approx(cost_delta)


def test_receivables_follow_payment_terms(services_brief):
    d = services_brief.values(2)
    s = run(services_brief, g="annual")
    for rev, ar in zip(s["rev"], s["ar"], strict=True):
        assert ar == pytest.approx(rev * d["ar_days"] / 360)
    slow = run(with_values(services_brief, ar_days=90), g="annual")
    assert slow["cash_close"][0] < s["cash_close"][0]


def test_late_hire_has_no_hours_before_start(services_brief):
    b = with_values(services_brief, staff_start=7)
    s = run(b)
    assert s["billable_fte"][5] == pytest.approx(b.values(2)["senior_fte"])
    assert s["billable_fte"][6] > s["billable_fte"][5]


@pytest.mark.parametrize("g", ["monthly", "annual"])
@pytest.mark.parametrize("scen", [1, 2, 3])
def test_balance_sheet_balances(services_brief, g, scen):
    s = run(services_brief, scen, g)
    for ta, tle in zip(s["total_assets"], s["total_le"], strict=True):
        assert ta == pytest.approx(tle, abs=1e-6)


def test_billable_roles_are_required(services_brief):
    d = services_brief.model_dump()
    d["roles"] = [r for r in d["roles"] if r["key"] != "senior"]
    d["drivers"] = [x for x in d["drivers"] if not x["key"].startswith("senior_")] + [
        x for x in d["drivers"] if x["key"] in ("senior_util", "senior_rate")
    ]
    b = services_brief.model_validate(d)
    with pytest.raises(BriefError, match="billable roles"):
        SERVICES.validate(b)
