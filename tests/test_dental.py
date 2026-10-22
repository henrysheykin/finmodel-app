"""Dental practice template economics in the plain-Python twin (no LibreOffice)."""

import pytest

from engine.brief import BriefError
from engine.challenger import python_model
from engine.core import reference_run
from engine.spec import Timing
from engine.templates import get_template

DENTAL = get_template("dental")
STAGES = ["planning", "early", "growing", "established"]
ROOMY = {"ops": 500, "hyg_ops": 500, "hyg_per_day": 1000, "visits_chair": 1000}  # capacity never binds


@pytest.fixture
def dental_brief():
    return DENTAL.default_brief("early")


def run(brief, scen=2, g="monthly", years=3):
    return reference_run(brief.values(scen), brief.roles, Timing(g, years), DENTAL.reference_top)


def with_values(brief, **vals):
    d = brief.model_dump()
    for drv in d["drivers"]:
        if drv["key"] in vals:
            v = vals[drv["key"]]
            drv.update(low=v, base=v, high=v)
    return brief.model_validate(d)


@pytest.mark.parametrize("stage", STAGES)
def test_stage_defaults_are_valid_ordered_and_funded(stage):
    b = DENTAL.default_brief(stage)
    low, base, high = (python_model(b, s) for s in (1, 2, 3))
    for y in (1, 2, 3):
        assert low["rev"][y] < base["rev"][y] < high["rev"][y]
        assert 0 < base["gp"][y] / base["rev"][y] < 1
        assert base["visits_doc"][y] <= base["cap_doc"][y] + 1e-9
        assert base["visits_hyg"][y] <= base["cap_hyg"][y] + 1e-9
    # Base is funded in every month (month-end cash), in both granularities; Low is the stress case
    for g in ("monthly", "annual"):
        assert min(run(b, 2, g, 5)["cash_close"]) > 0, (stage, g)


@pytest.mark.parametrize("stage", STAGES)
def test_stage_defaults_scale_with_capacity(stage):
    """Space, rooms and staff go with the number of chairs."""
    d = DENTAL.default_brief(stage).values(2)
    assert 340 <= d["sqft"] / (d["ops"] + d["hyg_ops"]) <= 450  # sq ft per room, a plausible suite
    assert d["asst_fte"] >= 0.5 * d["ops"]  # assistants for the doctor chairs in year 1
    for y in range(1, 6):  # every year of a five-year horizon: headcount growth never outruns rooms and chairs
        grow = {k: d[f"{k}_fte"] * (1 + d[f"{k}_fte_g"]) ** (y - 1) for k in ("hyg", "asst", "front")}
        assert grow["hyg"] <= d["hyg_ops"] + 0.25, (stage, y, grow)  # a hygienist needs a hygiene room
        assert grow["asst"] <= 1.5 * d["ops"], (stage, y, grow)  # at most 1.5 assistants per doctor chair
        assert grow["front"] <= 0.75 * d["ops"] + 1, (stage, y, grow)


@pytest.mark.parametrize("stage", STAGES)
def test_base_margin_does_not_collapse_over_five_years(stage):
    """Staffing that outgrows the chairs would show as a falling margin; Base EBITDA margin must not fall year on year
    once the practice has opened (year 2 onward) by more than a few points."""
    s = python_model(DENTAL.default_brief(stage).with_options(horizon_years=5), 2)
    em = [s["ebitda"][y] / s["rev"][y] for y in range(1, 6)]
    for y in range(1, 5):
        assert em[y] >= em[y - 1] - 0.03, (stage, em)
    assert min(em[1:]) > 0.05, (stage, em)


def test_cost_ratios_improve_with_scale():
    ratios = {}
    for stage in STAGES:
        b = DENTAL.default_brief(stage)
        s = run(b, 2, "annual", 3)
        d = b.values(2)
        ratios[stage] = (d["sqft"] * d["rent_psf"]) / s["rev"][0]
    assert ratios["planning"] > ratios["early"] > ratios["growing"] > ratios["established"]
    assert ratios["established"] < 0.07  # rent below ~7% of collections once the chairs are busy


def test_patient_roll_forward(dental_brief):
    d = dental_brief.values(2)
    s = run(with_values(dental_brief, **ROOMY))
    new = d["mkt"] / d["cpnp"] + d["ref_new"]
    p1 = d["pat_start"] * (1 - d["attr_m"]) + new
    assert s["pat_close"][0] == pytest.approx(p1)
    assert s["pat_close"][1] == pytest.approx(p1 * (1 - d["attr_m"]) + new)
    assert s["lost"][0] == pytest.approx(-d["pat_start"] * d["attr_m"])


def test_new_patients_are_marketing_over_cost_per_patient_plus_referrals(dental_brief):
    d = dental_brief.values(2)
    s = run(dental_brief, g="annual")
    mkt = d["mkt"] * 12
    assert s["new_mkt"][0] == pytest.approx(mkt / d["cpnp"])
    assert s["new_total"][0] == pytest.approx(mkt / d["cpnp"] + d["ref_new"] * 12)
    assert s["new_mkt"][1] == pytest.approx(mkt * (1 + d["mkt_g"]) / d["cpnp"])
    assert s["new_total"][1] - s["new_mkt"][1] == pytest.approx(d["ref_new"] * (1 + d["ref_g"]) * 12)


def test_doctor_visits_are_capped_by_chairs(dental_brief):
    d = dental_brief.values(2)
    s = run(with_values(dental_brief, hyg_per_day=1000, hyg_ops=500))
    cap = d["ops"] * d["visits_chair"] * d["work_days"]
    assert s["cap_doc"][0] == pytest.approx(cap)
    assert max(s["visits_doc"]) <= cap + 1e-9
    one = run(with_values(dental_brief, ops=1))  # one chair cannot serve the patient base
    assert one["visits_doc"][0] == pytest.approx(one["cap_doc"][0])
    assert one["rev"][0] < s["rev"][0]
    idle = run(with_values(dental_brief, pat_start=0, ref_new=0, mkt=0))  # no patients: no visits
    assert idle["visits_doc"][0] == pytest.approx(0) and idle["rev"][0] == pytest.approx(0)


def test_hygiene_visits_follow_recall_and_are_capped_by_hygienists_and_rooms(dental_brief):
    d = dental_brief.values(2)
    roomy = run(with_values(dental_brief, **ROOMY))
    avg = (d["pat_start"] + roomy["pat_close"][0]) / 2
    assert roomy["visits_hyg"][0] == pytest.approx(avg * d["recall"] / 12)
    cap = min(d["hyg_fte"], d["hyg_ops"]) * d["hyg_per_day"] * d["work_days"]
    tight = run(dental_brief)
    assert tight["cap_hyg"][0] == pytest.approx(cap)
    fewer_rooms = run(with_values(dental_brief, hyg_ops=1))  # hygiene rooms bind before hygienists
    assert fewer_rooms["cap_hyg"][0] == pytest.approx(1 * d["hyg_per_day"] * d["work_days"])
    assert fewer_rooms["prod_hyg"][0] < tight["prod_hyg"][0]


def test_collections_follow_the_insurance_mix(dental_brief):
    d = dental_brief.values(2)
    s = run(dental_brief)
    prod = s["prod"][0]
    net = prod * (1 - d["ppo_share"] * d["ppo_disc"])
    assert s["rev"][0] == pytest.approx(net * (1 - d["bad_debt"]))
    fee_for_service = run(with_values(dental_brief, ppo_share=0, bad_debt=0))
    assert fee_for_service["rev"][0] == pytest.approx(fee_for_service["prod"][0])
    assert fee_for_service["rev"][0] > s["rev"][0]
    more_ppo = run(with_values(dental_brief, ppo_share=0.9))
    assert more_ppo["rev"][0] < s["rev"][0]


def test_production_is_visits_times_fees_with_a_yearly_fee_increase(dental_brief):
    d = dental_brief.values(2)
    s = run(dental_brief, g="annual")
    for i in (0, 1, 2):
        idx = (1 + d["price_g"]) ** i
        assert s["prod"][i] == pytest.approx(
            (s["visits_doc"][i] * d["fee_doc"] + s["visits_hyg"][i] * d["fee_hyg"]) * idx
        )


def test_cost_of_sales_is_supplies_lab_and_card_fees(dental_brief):
    d = dental_brief.values(2)
    s = run(dental_brief)
    prod_doc = s["prod"][0] - s["prod_hyg"][0]
    expected = -(s["prod"][0] * d["supplies_pct"] + prod_doc * d["lab_pct"] + s["rev"][0] * d["card_pct"])
    assert s["cogs"][0] == pytest.approx(expected)
    no_lab = run(with_values(dental_brief, lab_pct=0, card_pct=0))
    assert no_lab["cogs"][0] == pytest.approx(-no_lab["prod"][0] * d["supplies_pct"])


def test_associate_pay_is_a_share_of_the_collections_they_produce(dental_brief):
    d = dental_brief.values(2)
    s = run(dental_brief)
    doc_share = (s["prod"][0] - s["prod_hyg"][0]) / s["prod"][0]
    assert s["opex_assoc"][0] == pytest.approx(-s["rev"][0] * doc_share * d["assoc_share"] * d["assoc_pct"])
    none = run(with_values(dental_brief, assoc_share=0))
    assert none["opex_assoc"][0] == pytest.approx(0)
    assert none["ebitda"][0] > s["ebitda"][0]  # same collections, no associate cost


def test_rent_follows_square_feet(dental_brief):
    d = dental_brief.values(2)
    s = run(dental_brief)
    assert s["opex_rent"][0] == pytest.approx(-d["sqft"] * d["rent_psf"] / 12)
    assert run(with_values(dental_brief, sqft=2 * d["sqft"]))["opex_rent"][0] == pytest.approx(2 * s["opex_rent"][0])


def test_capex_is_start_up_spend_then_refresh(dental_brief):
    d = dental_brief.values(2)
    s = run(with_values(dental_brief, fit_psf=100, ops_equipped=1))
    start = 100 * d["sqft"] + (d["ops"] + d["hyg_ops"] - 1) * d["capex_op"] + d["capex_img"]
    assert s["capex"][0] == pytest.approx(start + s["rev"][0] * d["refresh_pct"])
    assert s["capex"][1] == pytest.approx(s["rev"][1] * d["refresh_pct"])
    equipped = run(with_values(dental_brief, fit_psf=0, capex_img=0, ops_equipped=1000))
    assert equipped["capex"][0] == pytest.approx(equipped["rev"][0] * d["refresh_pct"])


def test_receivables_follow_insurance_payment_days(dental_brief):
    d = dental_brief.values(2)
    s = run(dental_brief, g="annual")
    for rev, ar in zip(s["rev"], s["ar"], strict=True):
        assert ar == pytest.approx(rev * d["ar_days"] / 360)
    slow = run(with_values(dental_brief, ar_days=45), g="annual")
    assert slow["cash_close"][0] < s["cash_close"][0]


def test_inventory_is_supplies_only_in_effect(dental_brief):
    """inv_days applies to total cost of sales; at the default it equals about four weeks of supplies."""
    d = dental_brief.values(2)
    s = run(dental_brief, g="annual")
    supplies = s["prod"][1] * d["supplies_pct"]
    weeks = s["inv"][1] / (supplies / 360) / 7
    assert 3.5 < weeks < 4.8


def test_monthly_and_annual_agree_exactly_without_attrition_or_binding_capacity(dental_brief):
    """Attrition compounding and the capacity cap are the only non-linear parts; without them annual = sum of months."""
    b = with_values(dental_brief, attr_m=0, **ROOMY)
    m, a = python_model(b, 2), python_model(b.with_options(granularity="annual"), 2)
    for k in ("rev", "prod", "gp", "ebitda", "visits_doc", "visits_hyg", "new_total", "payroll_total"):
        for y in (1, 2, 3):
            assert m[k][y] == pytest.approx(a[k][y], rel=1e-9, abs=0.01), (k, y)


@pytest.mark.parametrize("stage", STAGES)
def test_annual_approximates_monthly_with_attrition_and_capacity(stage):
    """Annual columns compound the monthly loss rate and let the year's new patients join mid-year; the chair and
    hygiene caps bind month by month. So annual and monthly agree closely, not to the dollar."""
    b = DENTAL.default_brief(stage)
    b = b.with_options(horizon_years=5)
    m, a = python_model(b, 2), python_model(b.with_options(granularity="annual"), 2)
    for y in range(1, 6):
        assert a["pat_close"][y] == pytest.approx(m["pat_close"][y], rel=0.02), (stage, y)
        assert a["rev"][y] == pytest.approx(m["rev"][y], rel=0.02), (stage, y)
        assert a["prod"][y] == pytest.approx(m["prod"][y], rel=0.02), (stage, y)


@pytest.mark.parametrize("g", ["monthly", "annual"])
@pytest.mark.parametrize("scen", [1, 2, 3])
def test_balance_sheet_balances(dental_brief, g, scen):
    s = run(dental_brief, scen, g)
    for ta, tle in zip(s["total_assets"], s["total_le"], strict=True):
        assert ta == pytest.approx(tle, abs=1e-6)


def test_cost_per_new_patient_below_one_dollar_is_guarded(dental_brief):
    s = run(with_values(dental_brief, cpnp=0))
    assert all(v >= 0 for v in s["pat_close"])


def test_hygienist_role_is_required(dental_brief):
    d = dental_brief.model_dump()
    d["roles"] = [r for r in d["roles"] if r["key"] != "hyg"]
    gone = {"hyg_fte", "hyg_salary", "hyg_fte_g", "hyg_start"}
    d["drivers"] = [x for x in d["drivers"] if x["key"] not in gone]
    b = dental_brief.model_validate(d)
    with pytest.raises(BriefError, match="hyg"):
        DENTAL.validate(b)


def test_late_hygienist_has_no_hygiene_capacity_before_start(dental_brief):
    b = with_values(dental_brief, hyg_start=7)
    s = run(b)
    assert s["cap_hyg"][5] == pytest.approx(0)
    assert s["cap_hyg"][6] > 0


def test_associates_are_not_paid_twice(dental_brief):
    """Associate dentists are paid through assoc_share / assoc_pct; a payroll role for them would double count."""
    d = dental_brief.model_dump()
    d["roles"].append({"key": "associate", "title": "Associate dentist"})
    for suffix, v in (("fte", 1), ("salary", 120000), ("start", 1), ("fte_g", 0)):
        d["drivers"].append({"key": f"associate_{suffix}", "low": v, "base": v, "high": v})
    both = dental_brief.model_validate(d)
    with pytest.raises(BriefError, match="paid twice"):
        DENTAL.validate(both)
    off = with_values(both, assoc_share=0)  # salaried associates are fine when nobody is paid on collections
    DENTAL.validate(off)
    DENTAL.validate(dental_brief)  # the owner dentist role is not an associate
