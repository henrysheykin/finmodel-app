"""Home services / trades template economics in the plain-Python twin (no LibreOffice)."""

import pytest

from engine.brief import BriefError
from engine.challenger import python_model
from engine.core import reference_run
from engine.spec import Timing
from engine.templates import get_template

HS = get_template("home_services")
STAGES = ["planning", "early", "growing", "established"]


@pytest.fixture
def hs_brief():
    return HS.default_brief("growing")


def run(brief, scen=2, g="monthly", years=3):
    return reference_run(brief.values(scen), brief.roles, Timing(g, years), HS.reference_top)


def with_values(brief, **vals):
    d = brief.model_dump()
    for drv in d["drivers"]:
        if drv["key"] in vals:
            v = vals[drv["key"]]
            drv.update(low=v, base=v, high=v)
    return brief.model_validate(d)


@pytest.mark.parametrize("stage", STAGES)
def test_stage_defaults_are_valid_and_ordered(stage):
    b = HS.default_brief(stage)
    low, base, high = (python_model(b, s) for s in (1, 2, 3))
    for y in (1, 2, 3):
        assert low["rev"][y] < base["rev"][y] < high["rev"][y]
        assert 0 < base["gp"][y] / base["rev"][y] < 1
        assert base["jobs"][y] <= base["cap_jobs"][y] + 1e-9


def test_jobs_are_demand_capped_by_capacity(hs_brief):
    d = hs_brief.values(2)
    flat = with_values(hs_brief, peak_uplift=0)
    s = run(flat)
    cap = d["tech_fte"] * d["jobs_per_tech"] * d["work_days"]
    demand = d["mkt"] / d["cpl"] * d["booking"] + d["repeat_jobs"]
    assert s["cap_jobs"][0] == pytest.approx(cap)
    assert s["jobs"][0] == pytest.approx(min(cap, demand))
    starved = run(with_values(flat, tech_fte=1))  # one technician cannot serve the demand
    assert starved["jobs"][0] == pytest.approx(starved["cap_jobs"][0])
    idle = run(with_values(flat, mkt=0, repeat_jobs=1))  # no demand: capacity sits idle
    assert idle["jobs"][0] == pytest.approx(1)


def test_revenue_is_jobs_times_ticket_plus_plans(hs_brief):
    d = hs_brief.values(2)
    s = run(with_values(hs_brief, peak_uplift=0))
    plans = d["plan_members"] * d["plan_fee"]
    assert s["rev_plans"][0] == pytest.approx(plans)
    assert s["rev"][0] == pytest.approx(s["jobs"][0] * d["ticket"] + plans)
    y2 = s["rev_plans"][12]
    assert y2 == pytest.approx(plans * (1 + d["plan_g"]) * (1 + d["price_g"]))


def test_busy_season_moves_jobs_into_summer_but_keeps_the_year(hs_brief):
    roomy = with_values(hs_brief, tech_fte=50)  # capacity never binds
    flat, peak = run(with_values(roomy, peak_uplift=0)), run(roomy)
    assert peak["jobs"][6] > flat["jobs"][6] > peak["jobs"][0]  # July busy, January quiet
    assert sum(peak["jobs"][:12]) == pytest.approx(sum(flat["jobs"][:12]))


def test_monthly_and_annual_agree_without_seasonality_or_cap(hs_brief):
    b = with_values(hs_brief, peak_uplift=0, tech_fte=50)
    m, a = python_model(b, 2), python_model(b.with_options(granularity="annual"), 2)
    for k in ("rev", "gp", "ebitda", "jobs", "rev_plans", "cap_jobs"):
        for y in (1, 2, 3):
            assert m[k][y] == pytest.approx(a[k][y], rel=1e-9, abs=0.01), (k, y)


def test_capacity_binds_in_peak_months_only(hs_brief):
    """Tight capacity: summer demand is turned away, so a busy season costs revenue."""
    tight = with_values(hs_brief, tech_fte=6)
    flat, peak = run(with_values(tight, peak_uplift=0)), run(tight)
    assert peak["jobs"][6] == pytest.approx(peak["cap_jobs"][6])
    assert sum(peak["jobs"][:12]) < sum(flat["jobs"][:12])


def test_technician_costs_sit_in_cost_of_delivery(hs_brief):
    d = hs_brief.values(2)
    s = run(with_values(hs_brief, materials_pct=0, plan_cost_pct=0, vehicle=0))
    tech_cost = -d["tech_fte"] * d["tech_salary"] / 12 * (1 + d["payroll_tax"])
    assert s["cogs"][0] == pytest.approx(tech_cost)


def test_vans_are_bought_for_new_technicians_only(hs_brief):
    d = hs_brief.values(2)
    s = run(hs_brief, g="annual")
    fte = [d["tech_fte"] * (1 + d["tech_fte_g"]) ** y for y in range(3)]
    added_y1 = max(0.0, fte[0] - d["equipped_start"])
    assert s["capex"][0] == pytest.approx(d["capex"] + added_y1 * d["capex_tech"])
    assert s["capex"][1] == pytest.approx((fte[1] - fte[0]) * d["capex_tech"])
    start_up = run(with_values(hs_brief, equipped_start=0), g="annual")
    assert start_up["capex"][0] == pytest.approx(d["capex"] + fte[0] * d["capex_tech"])


def test_marketing_growth_drives_booked_jobs(hs_brief):
    s = run(with_values(hs_brief, peak_uplift=0, tech_fte=50, repeat_jobs=0), g="annual")
    d = hs_brief.values(2)
    assert s["jobs"][1] / s["jobs"][0] == pytest.approx(1 + d["mkt_g"])


@pytest.mark.parametrize("g", ["monthly", "annual"])
@pytest.mark.parametrize("scen", [1, 2, 3])
def test_balance_sheet_balances(hs_brief, g, scen):
    s = run(hs_brief, scen, g)
    for ta, tle in zip(s["total_assets"], s["total_le"], strict=True):
        assert ta == pytest.approx(tle, abs=1e-6)


def test_cost_per_lead_below_one_dollar_is_guarded(hs_brief):
    s = run(with_values(hs_brief, cpl=0))
    assert all(v >= 0 for v in s["jobs"])


def test_technician_role_is_required(hs_brief):
    d = hs_brief.model_dump()
    d["roles"] = [r for r in d["roles"] if r["key"] != "tech"]
    d["drivers"] = [x for x in d["drivers"] if not x["key"].startswith("tech_")]
    b = hs_brief.model_validate(d)
    with pytest.raises(BriefError, match="tech"):
        HS.validate(b)
