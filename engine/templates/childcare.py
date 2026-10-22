"""Childcare / daycare centre template: licensed places × enrolment (with ramp-up) × tuition, staffed by ratio.

A centre is licensed for a number of places (children), split into an infant/toddler band and a preschool band.
Enrolment is a share of the licensed places: it starts at a low level in month 1 and climbs in a straight line to
its full level over a number of months (a new centre fills slowly; an established one starts full). Tuition is a
monthly fee per enrolled child, higher for infants and toddlers; a share of the children is paid by a subsidy
or voucher programme at a percentage of the list fee, and the rest pay list price less sibling and staff
discounts. Each new child pays a one-off registration fee. Teachers follow the staff-to-child ratios: children
in a band ÷ ratio, rounded up to whole teachers on the floor, times a coverage factor (the centre is open
longer than a shift) times the wage. Teacher payroll is a cost of sales line, so the headcount roles are the
director, the office/admin role and the kitchen role only: nothing is counted twice. Food is a cost per child per
operating day; supplies a cost per enrolled child per month. Rent, utilities and cleaning follow the floor area
(square feet per licensed place × licensed places). Capex is the build-out per square foot, furniture and
equipment per place, the playground and yearly replacement. Assumption memo: docs/templates/childcare.md.
"""

from __future__ import annotations

import math

from engine.brief import Brief
from engine.core import HC, Top
from engine.spec import DashChart, DashMetric, DriverSpec, KpiChart, Line, StmtRow, Timing
from engine.templates.base import Template, div

ROLES = [
    ("director", "Centre director"),
    ("admin", "Office & enrolment coordinator"),
    ("cook", "Cook / kitchen assistant"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer replaces them
# with their own numbers; the assumption memo says which are sourced and which are assumptions.
_COMMON = {
    "inf_share": (0.35, 0.35, 0.35),
    "days_open": (21, 21, 21),
    "turnover": (0.35, 0.3, 0.25),
    "tuit_inf": (1430, 1500, 1570),
    "tuit_pre": (1040, 1100, 1160),
    "tuition_g": (0.025, 0.03, 0.04),
    "disc_pct": (0.06, 0.05, 0.04),
    "reg_fee": (100, 150, 200),
    "subsidy_share": (0.25, 0.25, 0.25),
    "sub_rate": (0.82, 0.85, 0.88),
    "ratio_inf": (6, 6, 6),
    "ratio_pre": (12, 12, 12),
    "coverage": (1.25, 1.2, 1.15),
    "wage_teach": (36500, 35000, 33500),
    "food_day": (4.2, 4.0, 3.8),
    "supplies_child": (33, 30, 27),
    "cost_g": (0.03, 0.03, 0.03),
    "sqft_place": (75, 75, 75),
    "rent_sqft": (17, 16, 15),
    "rent_g": (0.03, 0.03, 0.03),
    "occ_sqft": (6.8, 6.5, 6.2),
    "mkt_g": (0.0, 0.0, 0.0),
    "pay_pct": (0.028, 0.025, 0.022),
    "payroll_tax": (0.12, 0.12, 0.12),
    "wage_g": (0.03, 0.03, 0.03),
    "ar_days": (13, 13, 13),
    "inv_days": (3, 3, 3),
    "ap_days": (11, 11, 11),
    "dep_years": (10, 10, 10),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "cap": (60, 60, 60),
            "cap_add": (0, 0, 0),
            "enr_full": (0.78, 0.85, 0.9),
            "enr_start": (0.15, 0.2, 0.25),
            "ramp_months": (18, 12, 9),
            "mkt": (2500, 2500, 2500),
            "insurance": (1800, 1800, 1800),
            "licensing": (600, 600, 600),
            "software": (400, 400, 400),
            "ga_other": (1200, 1200, 1200),
            "fitout_sqft": (60, 60, 60),
            "equip_place": (2200, 2200, 2200),
            "places_ready": (0, 0, 0),
            "capex_play": (40000, 40000, 40000),
            "refresh_place": (150, 150, 150),
            "equity": (450000, 450000, 450000),
            "loan_amount": (250000, 250000, 250000),
            "loan_rate": (0.08, 0.08, 0.08),
            "loan_term_years": (10, 10, 10),
        },
        "roles": {
            "director": (1, 62000, 1, 0.0),
            "admin": (0.5, 38000, 1, 0.0),
            "cook": (0.5, 34000, 1, 0.0),
        },
    },
    "early": {
        "drivers": {
            "cap": (60, 60, 60),
            "cap_add": (0, 0, 0),
            "enr_full": (0.78, 0.85, 0.9),
            "enr_start": (0.4, 0.5, 0.55),
            "ramp_months": (12, 9, 6),
            "mkt": (2500, 2500, 2500),
            "insurance": (1800, 1800, 1800),
            "licensing": (600, 600, 600),
            "software": (400, 400, 400),
            "ga_other": (1200, 1200, 1200),
            "fitout_sqft": (60, 60, 60),
            "equip_place": (2200, 2200, 2200),
            "places_ready": (60, 60, 60),
            "capex_play": (5000, 5000, 5000),
            "refresh_place": (150, 150, 150),
            "equity": (120000, 120000, 120000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "director": (1, 62000, 1, 0.0),
            "admin": (0.5, 38000, 1, 0.0),
            "cook": (0.5, 34000, 1, 0.0),
        },
    },
    "growing": {
        "drivers": {
            "cap": (90, 90, 90),
            "cap_add": (0, 10, 15),
            "enr_full": (0.8, 0.87, 0.92),
            "enr_start": (0.6, 0.7, 0.75),
            "ramp_months": (6, 4, 3),
            "mkt": (3000, 3000, 3000),
            "insurance": (2600, 2600, 2600),
            "licensing": (800, 800, 800),
            "software": (500, 500, 500),
            "ga_other": (1600, 1600, 1600),
            "fitout_sqft": (60, 60, 60),
            "equip_place": (2200, 2200, 2200),
            "places_ready": (90, 90, 90),
            "capex_play": (10000, 10000, 10000),
            "refresh_place": (150, 150, 150),
            "equity": (100000, 100000, 100000),
            "loan_amount": (100000, 100000, 100000),
            "loan_rate": (0.08, 0.08, 0.08),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {
            "director": (1, 66000, 1, 0.0),
            "admin": (1, 40000, 1, 0.1),
            "cook": (1, 35000, 1, 0.1),
        },
    },
    "established": {
        "drivers": {
            "cap": (120, 120, 120),
            "cap_add": (0, 0, 0),
            "enr_full": (0.82, 0.88, 0.92),
            "enr_start": (0.82, 0.88, 0.92),
            "ramp_months": (0, 0, 0),
            "mkt": (2000, 2000, 2000),
            "insurance": (3400, 3400, 3400),
            "licensing": (1000, 1000, 1000),
            "software": (600, 600, 600),
            "ga_other": (2000, 2000, 2000),
            "fitout_sqft": (60, 60, 60),
            "equip_place": (2200, 2200, 2200),
            "places_ready": (120, 120, 120),
            "capex_play": (15000, 15000, 15000),
            "refresh_place": (150, 150, 150),
            "equity": (80000, 80000, 80000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "director": (1, 70000, 1, 0.0),
            "admin": (1.5, 41000, 1, 0.03),
            "cook": (1.5, 36000, 1, 0.03),
        },
    },
}


def _enr_avg(d: dict, p: int, t: Timing) -> float:
    """Average enrolment (share of licensed places) in period ``p``: a straight line from the month-1 level to the
    full level over ``ramp_months`` months, averaged over the months the period covers."""
    j0 = (p - 1) * t.mpp  # months elapsed before the period
    n = max(0.0, min(float(t.mpp), d["ramp_months"] - j0))  # months of the period still on the ramp
    f = d["enr_full"]
    s = min(d["enr_start"], f)
    return (n * s + (f - s) / max(1, d["ramp_months"]) * (n * j0 + n * (n - 1) / 2) + (t.mpp - n) * f) / t.mpp


def _enr_end(d: dict, m: int) -> float:
    """Enrolment (share of licensed places) in model month ``m`` (the last month of a period)."""
    f = d["enr_full"]
    if d["ramp_months"] <= 0:
        return f
    s = min(d["enr_start"], f)
    return s + (f - s) * min(1.0, (m - 1) / max(1, d["ramp_months"]))


def _places(d: dict, y: int) -> float:
    return d["cap"] + d["cap_add"] * (y - 1)


def _kids_end(d: dict, m: int) -> float:
    """Children enrolled in model month ``m`` (0 before opening)."""
    return 0.0 if m <= 0 else _places(d, (m + 11) // 12) * _enr_end(d, m)


def _teachers(kids: float, ratio: float) -> int:
    """Teachers on the floor for a band: children ÷ ratio, rounded up (the round() keeps float dust from adding one)."""
    return math.ceil(round(kids / max(1.0, ratio), 6))


class ChildcareTemplate(Template):
    key = "childcare"
    title = "Childcare / daycare centre"
    business_types = ("childcare",)
    order = 130
    key_numbers = ("cap", "enr_full", "tuit_inf", "tuit_pre", "subsidy_share", "rent_sqft", "equity")
    sample_title = "Childcare centre"
    sample_desc = "Full workbook with licensed places, enrolment ramp, staff ratios, subsidies and the build-out"
    sample_stage = "planning"
    kpi_title = "Childcare metrics"
    kpi_checked = {
        "places": "cap_total",
        "enr_end": "enr_end_kids",
        "place_months": "place_months",
        "child_months": "child_months",
        "new_kids": "new_kids",
        "tch_pos": "tch_pos",
        "rev": "rev",
        "rev_tuition": "rev_tuition",
        "rev_sub": "rev_sub",
        "rev_reg": "rev_reg",
        "teach_pay": "teach_pay",
        "gp": "gp",
        "ebitda": "ebitda",
    }
    kpi_derived = ("occ", "rev_child", "sub_share", "care_pct", "gm", "em")
    kpi_flows = ("place_months", "child_months", "new_kids", "rev_tuition", "rev_sub", "rev_reg", "teach_pay")

    def driver_specs(self) -> list[DriverSpec]:
        cap, tuit, staff = "Places & enrolment", "Tuition & fees", "Staffing by ratio"
        cost, opex, cap_x = "Cost of sales", "Operating costs", "Capex"
        return [
            DriverSpec("cap", "Licensed places (children) at start", "#", "int", 1, 5000, section=cap),
            DriverSpec("cap_add", "Licensed places added each year (from year 2)", "#", "int", 0, 5000, "asc", cap),
            DriverSpec(
                "inf_share", "Places for infants & toddlers, % of licensed places", "%", "pct", 0, 1, section=cap
            ),
            DriverSpec("enr_full", "Enrolment once full, % of licensed places", "%", "pct", 0.1, 1, "asc", cap),
            DriverSpec("enr_start", "Enrolment in month 1, % of licensed places", "%", "pct", 0, 1, "asc", cap),
            DriverSpec(
                "ramp_months", "Months to reach full enrolment", "months", "int", 0, 60, "desc", cap, integer=True
            ),
            DriverSpec("days_open", "Operating days per month", "days", "int", 1, 31, section=cap),
            DriverSpec(
                "turnover", "Children leaving each year, % of enrolled (replaced by new)", "%", "pct", 0, 1, "desc", cap
            ),
            DriverSpec("tuit_inf", "Tuition per infant / toddler per month (year 1)", "$", "usd", 0, 1e5, "asc", tuit),
            DriverSpec("tuit_pre", "Tuition per preschooler per month (year 1)", "$", "usd", 0, 1e5, "asc", tuit),
            DriverSpec("tuition_g", "Tuition and fee increase per year", "%", "pct", -0.5, 1, "asc", tuit),
            DriverSpec(
                "disc_pct", "Sibling & staff discounts, % of parent-paid tuition", "%", "pct", 0, 1, "desc", tuit
            ),
            DriverSpec("reg_fee", "Registration fee per new child (year 1)", "$", "usd", 0, 1e5, "asc", tuit),
            DriverSpec(
                "subsidy_share", "Children paid by subsidy / vouchers, % of enrolled", "%", "pct", 0, 1, section=tuit
            ),
            DriverSpec("sub_rate", "Subsidy payment, % of the list tuition", "%", "pct", 0, 1.5, "asc", tuit),
            DriverSpec("ratio_inf", "Children per teacher, infants & toddlers", "#", "dec1", 1, 30, section=staff),
            DriverSpec("ratio_pre", "Children per teacher, preschool", "#", "dec1", 1, 40, section=staff),
            DriverSpec(
                "coverage",
                "Coverage factor (teachers hired per teacher on the floor)",
                "x",
                "dec1",
                1,
                3,
                "desc",
                staff,
            ),
            DriverSpec("wage_teach", "Teacher salary per FTE per year (year 1)", "$", "usd", 0, 5e6, "desc", staff),
            DriverSpec("food_day", "Food per child per operating day (year 1)", "$", "usd2", 0, 1e3, "desc", cost),
            DriverSpec(
                "supplies_child",
                "Supplies & activities per child per month (year 1)",
                "$",
                "usd2",
                0,
                1e4,
                "desc",
                cost,
            ),
            DriverSpec(
                "cost_g", "Food, supplies & utilities cost increase per year", "%", "pct", -0.5, 1, section=cost
            ),
            DriverSpec("sqft_place", "Floor area per licensed place", "sq ft", "int", 1, 1000, section=opex),
            DriverSpec("rent_sqft", "Rent per square foot per year (year 1)", "$", "usd2", 0, 1e4, "desc", opex),
            DriverSpec("rent_g", "Rent increase per year", "%", "pct", -0.5, 1, section=opex),
            DriverSpec(
                "occ_sqft", "Utilities & cleaning per square foot per year (year 1)", "$", "usd2", 0, 1e3, "desc", opex
            ),
            DriverSpec("insurance", "Insurance per month", "$", "usd", 0, 1e7, section=opex),
            DriverSpec(
                "licensing", "Licensing, background checks & training per month", "$", "usd", 0, 1e7, section=opex
            ),
            DriverSpec("mkt", "Marketing budget per month (year 1)", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("mkt_g", "Marketing budget growth per year", "%", "pct", -0.9, 5, section=opex),
            DriverSpec("software", "Parent app & management software per month", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("pay_pct", "Card / ACH fees, % of parent-paid tuition", "%", "pct", 0, 0.2, "desc", opex),
            DriverSpec("ga_other", "Other G&A per month (accounting, legal, bank)", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("fitout_sqft", "Build-out per square foot (new places)", "$", "usd2", 0, 1e4, section=cap_x),
            DriverSpec("equip_place", "Furniture & equipment per licensed place", "$", "usd", 0, 1e6, section=cap_x),
            DriverSpec(
                "places_ready", "Places already built out and equipped at start", "#", "int", 0, 5000, section=cap_x
            ),
            DriverSpec("capex_play", "Playground & outdoor area (month 1)", "$", "usd", 0, 1e8, section=cap_x),
            DriverSpec(
                "refresh_place",
                "Equipment replacement per licensed place per year (from year 2)",
                "$",
                "usd",
                0,
                1e6,
                section=cap_x,
            ),
        ]

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        idx = "(1+{in:tuition_g})^({y}-1)"
        avg = (
            "=({ramp_n}*{enr_s}+({in:enr_full}-{enr_s})/MAX(1,{in:ramp_months})"
            "*({ramp_n}*({p}-1)*{mpp}+{ramp_n}*({ramp_n}-1)/2)+({mpp}-{ramp_n})*{in:enr_full})/{mpp}"
        )
        end = (
            "=IF({in:ramp_months}<=0,{in:enr_full},{enr_s}+({in:enr_full}-{enr_s})"
            "*MIN(1,({p}*{mpp}-1)/MAX(1,{in:ramp_months})))"
        )
        kids = "{cap_total}*{enr_end_pct}"
        return [
            Line(
                "cap_total",
                "Licensed places",
                "={in:cap}+{in:cap_add}*({y}-1)",
                "top",
                "int",
                agg="last",
                section="Places & enrolment",
            ),
            Line(
                "enr_s",
                "Enrolment in month 1 (capped at the full level)",
                "=MIN({in:enr_start},{in:enr_full})",
                "top",
                "pct",
                agg="none",
            ),
            Line(
                "ramp_n",
                "Helper: months of the period still on the ramp-up",
                "=MAX(0,MIN({mpp},{in:ramp_months}-({p}-1)*{mpp}))",
                "top",
                "dec1",
                agg="none",
            ),
            Line("enr_pct", "Enrolment, average of the period (% of places)", avg, "top", "pct", agg="last"),
            Line("enr_end_pct", "Enrolment at the end of the period (% of places)", end, "top", "pct", agg="none"),
            Line(
                "enr_inf",
                "Infants & toddlers enrolled (average)",
                "={cap_total}*{in:inf_share}*{enr_pct}",
                "top",
                "dec1",
                agg="last",
            ),
            Line(
                "enr_pre",
                "Preschoolers enrolled (average)",
                "={cap_total}*(1-{in:inf_share})*{enr_pct}",
                "top",
                "dec1",
                agg="last",
            ),
            Line(
                "enrolled", "Children enrolled (average)", "={enr_inf}+{enr_pre}", "top", "dec1", agg="last", bold=True
            ),
            Line("child_months", "Child-months enrolled", "={enrolled}*{mpp}", "top", "int"),
            Line("place_months", "Licensed place-months", "={cap_total}*{mpp}", "top", "int"),
            Line("enr_end_kids", "Children enrolled at the end of the period", f"={kids}", "top", "dec1", agg="last"),
            Line(
                "new_kids",
                "New children enrolled (fill-up and replacement of leavers)",
                "=MAX(0,{enr_end_kids}-{enr_end_kids[-1]})+{enrolled}*{in:turnover}*{mpp}/12",
                "top",
                "dec1",
                first="=MAX(0,{enr_end_kids})+{enrolled}*{in:turnover}*{mpp}/12",
            ),
            Line(
                "tch_inf",
                "Teachers on the floor, infants & toddlers",
                "=ROUNDUP(ROUND({enr_inf}/MAX(1,{in:ratio_inf}),6),0)",
                "top",
                "int",
                agg="last",
                section="Staffing by ratio",
            ),
            Line(
                "tch_pre",
                "Teachers on the floor, preschool",
                "=ROUNDUP(ROUND({enr_pre}/MAX(1,{in:ratio_pre}),6),0)",
                "top",
                "int",
                agg="last",
            ),
            Line("tch_pos", "Teachers on the floor", "={tch_inf}+{tch_pre}", "top", "int", agg="last", bold=True),
            Line(
                "tch_fte", "Teaching FTE hired (with coverage)", "={tch_pos}*{in:coverage}", "top", "dec1", agg="last"
            ),
            Line(
                "tuit_gross",
                "Tuition at list price",
                f"=({{enr_inf}}*{{in:tuit_inf}}+{{enr_pre}}*{{in:tuit_pre}})*{{mpp}}*{idx}",
                "top",
                section="Revenue",
            ),
            Line(
                "rev_tuition",
                "Parent-paid tuition (after sibling & staff discounts)",
                "={tuit_gross}*(1-{in:subsidy_share})*(1-{in:disc_pct})",
                "top",
            ),
            Line("rev_sub", "Subsidy & voucher payments", "={tuit_gross}*{in:subsidy_share}*{in:sub_rate}", "top"),
            Line("rev_reg", "Registration fees", f"={{new_kids}}*{{in:reg_fee}}*{idx}", "top"),
            Line("rev", "Revenue", "={rev_tuition}+{rev_sub}+{rev_reg}", "top", bold=True, total=True),
            Line(
                "teach_pay",
                "Teacher payroll (with payroll taxes)",
                "=-{tch_fte}*{in:wage_teach}/12*{mpp}*(1+{in:payroll_tax})*(1+{in:wage_g})^({y}-1)",
                "top",
                section="Cost of sales",
            ),
            Line(
                "food_cost",
                "Food",
                "=-{enrolled}*{in:food_day}*{in:days_open}*{mpp}*(1+{in:cost_g})^({y}-1)",
                "top",
            ),
            Line(
                "supplies_cost",
                "Supplies & activities",
                "=-{enrolled}*{in:supplies_child}*{mpp}*(1+{in:cost_g})^({y}-1)",
                "top",
            ),
            Line("cogs", "Cost of sales", "={teach_pay}+{food_cost}+{supplies_cost}", "top", bold=True),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        area = "{cap_total}*{in:sqft_place}"
        cidx = "(1+{in:cost_g})^({y}-1)"
        return [
            Line(
                "payroll",
                "Staff payroll (director, office, kitchen)",
                "={payroll_total}",
                "top",
                section="Operating expenses",
            ),
            Line("rent", "Rent", f"=-{area}*{{in:rent_sqft}}/12*(1+{{in:rent_g}})^({{y}}-1)*{{mpp}}", "top"),
            Line("utilities", "Utilities & cleaning", f"=-{area}*{{in:occ_sqft}}/12*{cidx}*{{mpp}}", "top"),
            Line("insurance", "Insurance", "=-{in:insurance}*{mpp}", "top"),
            Line("licensing", "Licensing, background checks & training", "=-{in:licensing}*{mpp}", "top"),
            Line("mkt", "Marketing", "=-{in:mkt}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
            Line("software", "Parent app & management software", "=-{in:software}*{mpp}", "top"),
            Line("payfees", "Card / ACH fees", "=-{rev_tuition}*{in:pay_pct}", "top"),
            Line("ga_other", "Other G&A", "=-{in:ga_other}*{mpp}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        later = "IF(AND({y}>1,MOD({p}-1,{ppy})=0),{in:cap_add},0)"
        return [
            Line(
                "capex_fit",
                "Build-out of new places",
                f"={later}*{{in:sqft_place}}*{{in:fitout_sqft}}",
                "top",
                first="=MAX(0,{in:cap}-{in:places_ready})*{in:sqft_place}*{in:fitout_sqft}",
            ),
            Line(
                "capex_equip",
                "Furniture & equipment for new places",
                f"={later}*{{in:equip_place}}",
                "top",
                first="=MAX(0,{in:cap}-{in:places_ready})*{in:equip_place}",
            ),
            Line("capex_play", "Playground & outdoor area", "=IF({p}=1,{in:capex_play},0)", "top"),
            Line(
                "capex_refresh",
                "Equipment replacement (first period of each year from year 2)",
                "=IF(AND({y}>1,MOD({p}-1,{ppy})=0),{cap_total}*{in:refresh_place},0)",
                "top",
            ),
            Line(
                "capex",
                "Capital spending",
                "={capex_fit}+{capex_equip}+{capex_play}+{capex_refresh}",
                "top",
                bold=True,
            ),
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("enr_end", "Children enrolled (year end)", "kpi:enr_end", "int"),
            DashMetric("occ", "Occupancy (child-months ÷ place-months)", "kpi:occ", "pct"),
            DashMetric("care_pct", "Teacher payroll, % of revenue", "kpi:care_pct", "pct"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Children enrolled & occupancy", bars=("enr_end",), lines=("occ",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("places", "Licensed places (year end)", "line", "cap_total", "int", bold=True),
            StmtRow("enr_end", "Children enrolled (year end)", "line", "enr_end_kids", "int", bold=True),
            StmtRow("place_months", "Licensed place-months", "line", "place_months", "int"),
            StmtRow("child_months", "Child-months enrolled", "line", "child_months", "int"),
            StmtRow(
                "occ",
                "Occupancy (child-months ÷ licensed place-months)",
                "formula",
                "=IF({place_months}=0,0,{child_months}/{place_months})",
                "pct",
            ),
            StmtRow("new_kids", "New children enrolled", "line", "new_kids", "int"),
            StmtRow("tch_pos", "Teachers on the floor (year end)", "line", "tch_pos", "int"),
            StmtRow("rev", "Revenue", "line", "rev", bold=True),
            StmtRow("rev_tuition", "Parent-paid tuition", "line", "rev_tuition"),
            StmtRow("rev_sub", "Subsidy & voucher payments", "line", "rev_sub"),
            StmtRow(
                "sub_share",
                "Subsidy & vouchers, % of tuition revenue",
                "formula",
                "=IF({rev_tuition}+{rev_sub}=0,0,{rev_sub}/({rev_tuition}+{rev_sub}))",
                "pct",
            ),
            StmtRow("rev_reg", "Registration fees", "line", "rev_reg"),
            StmtRow(
                "rev_child",
                "Tuition revenue per child-month",
                "formula",
                "=IF({child_months}=0,0,({rev_tuition}+{rev_sub})/{child_months})",
                "usd2",
            ),
            StmtRow("teach_pay", "Teacher payroll (with payroll taxes)", "line", "teach_pay"),
            StmtRow(
                "care_pct",
                "Teacher payroll, % of revenue",
                "formula",
                "=IF({rev}=0,0,-{teach_pay}/{rev})",
                "pct",
            ),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("ebitda", "EBITDA", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
        ]

    def kpi_charts(self, t: Timing) -> list[KpiChart]:
        return [
            KpiChart("Children enrolled and occupancy", bars=("enr_end",), lines=("occ",)),
            KpiChart("Revenue by source", bars=("rev_tuition", "rev_sub", "rev_reg"), stacked=True),
        ]

    # ------------------------------------------------------------------ python twin
    def kpi_reference(self, ann: dict, d: dict, t: Timing) -> dict:
        out: dict[str, dict] = {k: {} for k in self.kpi_derived}
        for y in range(1, t.years + 1):
            rev, tuition = ann["rev"][y], ann["rev_tuition"][y] + ann["rev_sub"][y]
            out["occ"][y] = div(ann["child_months"][y], ann["place_months"][y])
            out["rev_child"][y] = div(tuition, ann["child_months"][y])
            out["sub_share"][y] = div(ann["rev_sub"][y], tuition)
            out["care_pct"][y] = div(-ann["teach_pay"][y], rev)
            out["gm"][y] = div(ann["gp"][y], rev)
            out["em"][y] = div(ann["ebitda"][y], rev)
        return out

    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        idx = (1 + d["tuition_g"]) ** (y - 1)
        cidx = (1 + d["cost_g"]) ** (y - 1)
        places = _places(d, y)
        enr = _enr_avg(d, p, t)
        enr_inf = places * d["inf_share"] * enr
        enr_pre = places * (1 - d["inf_share"]) * enr
        enrolled = enr_inf + enr_pre
        kids_end = _kids_end(d, p * t.mpp)
        new_kids = max(0.0, kids_end - _kids_end(d, (p - 1) * t.mpp)) + enrolled * d["turnover"] * t.mpp / 12
        tch_pos = _teachers(enr_inf, d["ratio_inf"]) + _teachers(enr_pre, d["ratio_pre"])
        tch_fte = tch_pos * d["coverage"]
        gross = (enr_inf * d["tuit_inf"] + enr_pre * d["tuit_pre"]) * t.mpp * idx
        rev_tuition = gross * (1 - d["subsidy_share"]) * (1 - d["disc_pct"])
        rev_sub = gross * d["subsidy_share"] * d["sub_rate"]
        rev_reg = new_kids * d["reg_fee"] * idx
        teach_pay = -tch_fte * d["wage_teach"] / 12 * t.mpp * (1 + d["payroll_tax"]) * (1 + d["wage_g"]) ** (y - 1)
        cogs = (
            teach_pay
            - enrolled * d["food_day"] * d["days_open"] * t.mpp * cidx
            - enrolled * d["supplies_child"] * t.mpp * cidx
        )
        area = places * d["sqft_place"]
        later_places = d["cap_add"] if y > 1 and (p - 1) % t.ppy == 0 else 0.0
        if p == 1:
            new_places = max(0.0, d["cap"] - d["places_ready"])
            capex = new_places * (d["sqft_place"] * d["fitout_sqft"] + d["equip_place"]) + d["capex_play"]
        else:
            capex = later_places * (d["sqft_place"] * d["fitout_sqft"] + d["equip_place"])
        if y > 1 and (p - 1) % t.ppy == 0:
            capex += places * d["refresh_place"]
        return Top(
            rev=rev_tuition + rev_sub + rev_reg,
            cogs=cogs,
            opex={
                "payroll": hc.payroll,
                "rent": -area * d["rent_sqft"] / 12 * (1 + d["rent_g"]) ** (y - 1) * t.mpp,
                "utilities": -area * d["occ_sqft"] / 12 * cidx * t.mpp,
                "insurance": -d["insurance"] * t.mpp,
                "licensing": -d["licensing"] * t.mpp,
                "mkt": -d["mkt"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp,
                "software": -d["software"] * t.mpp,
                "payfees": -rev_tuition * d["pay_pct"],
                "ga_other": -d["ga_other"] * t.mpp,
            },
            capex=capex,
            kpis={
                "cap_total": places,
                "place_months": places * t.mpp,
                "child_months": enrolled * t.mpp,
                "enr_end_kids": kids_end,
                "new_kids": new_kids,
                "tch_pos": tch_pos,
                "rev_tuition": rev_tuition,
                "rev_sub": rev_sub,
                "rev_reg": rev_reg,
                "teach_pay": teach_pay,
            },
        )

    # ------------------------------------------------------------------ defaults
    def default_brief(self, stage: str = "planning", **opts) -> Brief:
        cfg = _STAGES[stage]
        vals = {**_COMMON, **cfg["drivers"]}
        drivers = [{"key": k, "low": v[0], "base": v[1], "high": v[2]} for k, v in vals.items()]
        roles = []
        for key, title in ROLES:
            fte, salary, start, growth = cfg["roles"][key]
            roles.append({"key": key, "title": title})
            for suffix, v in (("fte", fte), ("salary", salary), ("start", start), ("fte_g", growth)):
                drivers.append({"key": f"{key}_{suffix}", "low": v, "base": v, "high": v})
        brief = Brief.model_validate(
            {
                "model_name": f"Childcare centre financial model ({stage})",
                "template": self.key,
                "business_type": "childcare",
                "stage": stage,
                "assumption_note": "Illustrative assumptions — replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
