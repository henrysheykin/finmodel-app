"""Pet care template: pet grooming (tables x groomers) plus boarding (kennel runs x occupancy x nightly rate).

Grooming: appointments arrive per operating day (a linear ramp-up from opening, then a yearly growth rate).
Grooms completed = the lower of demand and capacity, where capacity is the smaller of the station limit
(grooming tables / tubs x grooms a station can turn per day) and the groomer limit (groomer FTE x grooms a
groomer can finish per day). Grooming revenue = grooms x the average groom price; a retail attach (shampoo,
treats, accessories) is a spend per groom with its own margin. Groomers get a small guaranteed base (Headcount
sheet) plus a commission on grooming revenue, both cost of sales.

Boarding: kennel runs x calendar nights x occupancy x nightly rate. Occupancy grows yearly, follows the ramp-up and,
in monthly models, a simple season (June-August and December busier, the other eight months give it back, year
unchanged); it is capped at 100%. Food, cleaning and laundry are a cost per boarded night (cost of sales).
Attendants, the manager, rent, insurance, utilities and software, marketing and card fees are operating expenses;
grooming tables / tubs / dryers, kennel build-out, fit-out and (optional) land are capex.
Assumption memo: docs/templates/pet_care.md.
"""

from __future__ import annotations

from engine.brief import Brief, BriefError
from engine.core import HC, Top, role_period
from engine.spec import DashChart, DashMetric, DriverSpec, KpiChart, Line, StmtRow, Timing
from engine.templates.base import Template, div

GROOMER = "groomer"
ROLES = [
    (GROOMER, "Groomers (guaranteed base pay)"),
    ("attendant", "Kennel attendants & daycare"),
    ("manager", "Manager & front desk"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data: the customer replaces
# them with their own numbers; the assumption memo labels every figure as an assumption.
_COMMON = {
    "days_open": (26, 26, 26),
    "grooms_table": (6, 6, 6),
    "grooms_groomer": (5, 5.5, 6),
    "groom_price": (68, 75, 82),
    "price_g": (0.01, 0.03, 0.04),
    "retail_groom": (6, 8, 10),
    "retail_margin": (0.36, 0.4, 0.44),
    "nights_m": (30.4, 30.4, 30.4),
    "occ_g": (0.0, 0.03, 0.05),
    "peak_uplift": (0.15, 0.2, 0.25),
    "night_rate": (50, 55, 60),
    "commission_pct": (0.37, 0.35, 0.33),
    "supplies_groom": (5.0, 4.5, 4.0),
    "board_night": (7.0, 6.0, 5.5),
    "card_pct": (0.032, 0.03, 0.028),
    "rent_g": (0.03, 0.03, 0.03),
    "cost_g": (0.04, 0.03, 0.025),
    "payroll_tax": (0.15, 0.15, 0.15),
    "wage_g": (0.04, 0.03, 0.03),
    "ar_days": (2, 2, 2),
    "inv_days": (6, 6, 6),
    "ap_days": (25, 25, 25),
    "dep_years": (8, 8, 8),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "tables": (4, 4, 4),
            "runs": (30, 30, 30),
            "grooms_day": (13, 16, 19),
            "groom_g": (0.0, 0.03, 0.06),
            "occ": (0.5, 0.62, 0.72),
            "ramp_months": (14, 10, 8),
            "ramp_start": (0.3, 0.4, 0.5),
            "rent": (9000, 9000, 9000),
            "insurance": (2500, 2500, 2500),
            "ga_other": (4500, 4500, 4500),
            "mkt": (3500, 3500, 3500),
            "mkt_g": (-0.3, -0.2, -0.1),
            "capex_table": (6000, 6000, 6000),
            "capex_run": (2500, 2500, 2500),
            "capex_fit": (90000, 90000, 90000),
            "capex_land": (0, 0, 0),
            "capex_refresh": (10000, 10000, 10000),
            "equity": (330000, 330000, 330000),
            "loan_amount": (100000, 100000, 100000),
            "loan_rate": (0.09, 0.09, 0.09),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {
            "groomer": (4, 10000, 1, 0.0),
            "attendant": (3, 33000, 1, 0.0),
            "manager": (1, 60000, 1, 0.0),
        },
    },
    "early": {
        "drivers": {
            "tables": (4, 4, 4),
            "runs": (30, 30, 30),
            "grooms_day": (13, 16, 19),
            "groom_g": (0.0, 0.03, 0.06),
            "occ": (0.5, 0.62, 0.72),
            "ramp_months": (6, 4, 3),
            "ramp_start": (0.6, 0.7, 0.8),
            "rent": (9000, 9000, 9000),
            "insurance": (2500, 2500, 2500),
            "ga_other": (4500, 4500, 4500),
            "mkt": (2500, 2500, 2500),
            "mkt_g": (-0.1, 0.0, 0.05),
            "capex_table": (1500, 1500, 1500),
            "capex_run": (500, 500, 500),
            "capex_fit": (10000, 10000, 10000),
            "capex_land": (0, 0, 0),
            "capex_refresh": (10000, 10000, 10000),
            "equity": (120000, 120000, 120000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "groomer": (4, 10000, 1, 0.0),
            "attendant": (3, 33000, 1, 0.0),
            "manager": (1, 60000, 1, 0.0),
        },
    },
    "growing": {
        "drivers": {
            "tables": (6, 6, 6),
            "runs": (40, 40, 40),
            "grooms_day": (21, 26, 30),
            "groom_g": (0.0, 0.03, 0.05),
            "occ": (0.58, 0.68, 0.76),
            "ramp_months": (0, 0, 0),
            "ramp_start": (1, 1, 1),
            "rent": (12000, 12000, 12000),
            "insurance": (3200, 3200, 3200),
            "ga_other": (7500, 7500, 7500),
            "mkt": (3500, 3500, 3500),
            "mkt_g": (0.0, 0.03, 0.06),
            "capex_table": (2500, 2500, 2500),
            "capex_run": (1200, 1200, 1200),
            "capex_fit": (20000, 20000, 20000),
            "capex_land": (0, 0, 0),
            "capex_refresh": (15000, 15000, 15000),
            "equity": (150000, 150000, 150000),
            "loan_amount": (80000, 80000, 80000),
            "loan_rate": (0.09, 0.09, 0.09),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {
            "groomer": (6, 10000, 1, 0.0),
            "attendant": (4, 34000, 1, 0.0),
            "manager": (1, 62000, 1, 0.0),
        },
    },
    "established": {
        "drivers": {
            "tables": (6, 6, 6),
            "runs": (40, 40, 40),
            "grooms_day": (23, 27, 31),
            "groom_g": (0.0, 0.02, 0.04),
            "occ": (0.62, 0.72, 0.8),
            "ramp_months": (0, 0, 0),
            "ramp_start": (1, 1, 1),
            "rent": (12500, 12500, 12500),
            "insurance": (3400, 3400, 3400),
            "ga_other": (8000, 8000, 8000),
            "mkt": (3000, 3000, 3000),
            "mkt_g": (0.0, 0.03, 0.06),
            "capex_table": (1500, 1500, 1500),
            "capex_run": (600, 600, 600),
            "capex_fit": (10000, 10000, 10000),
            "capex_land": (0, 0, 0),
            "capex_refresh": (20000, 20000, 20000),
            "equity": (150000, 150000, 150000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "groomer": (6, 10000, 1, 0.0),
            "attendant": (4, 35000, 1, 0.0),
            "manager": (1, 64000, 1, 0.0),
        },
    },
}


def _ramp(d: dict, p: int, t: Timing) -> float:
    """Average share of mature volume in period ``p``: a straight line from ``ramp_start`` to 1 over
    ``ramp_months`` months, averaged over the months the period covers (so annual = the mean of its months)."""
    months = d["ramp_months"]
    if months <= 0:
        return 1.0
    j0 = (p - 1) * t.mpp  # months elapsed before the period
    n = max(0.0, min(float(t.mpp), months - j0))  # months of the period still on the ramp
    s = d["ramp_start"]
    return (n * s + (1 - s) / max(1, months) * (n * j0 + n * (n - 1) / 2) + t.mpp - n) / t.mpp


def _season(d: dict, p: int, t: Timing) -> float:
    """Boarding season (model month 1 = January): June-August and December get +uplift, the other eight months
    give back uplift/2, so the year is unchanged. Annual models use 1."""
    if t.granularity != "monthly":
        return 1.0
    m = (p - 1) % 12  # 0 = January
    up = d["peak_uplift"]
    return 1 + up if m in (5, 6, 7, 11) else 1 - up / 2


class PetCareTemplate(Template):
    key = "pet_care"
    title = "Pet grooming & boarding"
    business_types = ("pet_care",)
    order = 130
    key_numbers = ("grooms_day", "groom_price", "runs", "occ", "night_rate", "rent", "equity")
    sample_title = "Pet grooming & boarding"
    sample_desc = "Full workbook with grooming tables and groomers, kennel runs, occupancy, nightly rate and the lease"
    sample_stage = "planning"
    kpi_title = "Pet care metrics"
    kpi_checked = {
        "grooms": "grooms",
        "groom_cap": "groom_cap",
        "lost_grooms": "lost_grooms",
        "groomer_fte": "groomer_fte",
        "nights": "nights",
        "avail_n": "avail_nights",
        "rev_groom": "rev_groom",
        "rev_board": "rev_board",
        "rev_retail": "rev_retail",
        "rev": "rev",
        "gp": "gp",
        "ebitda": "ebitda",
    }
    kpi_derived = (
        "groom_use",
        "occ_rate",
        "groom_ticket",
        "revpan",
        "board_share",
        "rev_groomer",
        "gm",
        "em",
    )
    kpi_flows = (
        "grooms",
        "groom_cap",
        "lost_grooms",
        "nights",
        "avail_nights",
        "rev_groom",
        "rev_board",
        "rev_retail",
    )

    def driver_specs(self) -> list[DriverSpec]:
        gd, gc, gp, bd, cos, fix, cx = (
            "Grooming demand",
            "Grooming capacity",
            "Grooming prices & retail",
            "Boarding",
            "Cost of sales",
            "Shop costs",
            "Capital spending",
        )
        return [
            DriverSpec(
                "grooms_day",
                "Grooming appointments per operating day at maturity (year 1)",
                "grooms",
                "dec1",
                0,
                1e4,
                "asc",
                gd,
            ),
            DriverSpec("groom_g", "Grooming volume growth per year", "%", "pct", -0.9, 5, "asc", gd),
            DriverSpec("days_open", "Operating days per month", "days", "dec1", 1, 31, section=gd),
            DriverSpec(
                "ramp_months",
                "Months to reach mature volume (0 = already mature)",
                "months",
                "int",
                0,
                60,
                "desc",
                gd,
                integer=True,
            ),
            DriverSpec(
                "ramp_start", "Volume in month 1, % of mature (grooming and boarding)", "%", "pct", 0, 1, "asc", gd
            ),
            DriverSpec("tables", "Grooming tables / tub stations", "stations", "int", 1, 1000, section=gc),
            DriverSpec(
                "grooms_table", "Grooms one station can turn per operating day", "grooms", "dec1", 0.1, 100, "asc", gc
            ),
            DriverSpec(
                "grooms_groomer",
                "Grooms one groomer can finish per operating day",
                "grooms",
                "dec1",
                0.1,
                100,
                "asc",
                gc,
            ),
            DriverSpec("groom_price", "Average price per groom (year 1)", "$", "usd2", 0, 1e4, "asc", gp),
            DriverSpec(
                "price_g", "Price increase per year (grooming, boarding, retail)", "%", "pct", -0.5, 1, "asc", gp
            ),
            DriverSpec(
                "retail_groom",
                "Retail sales per groom (shampoo, treats, accessories; year 1)",
                "$",
                "usd2",
                0,
                1e4,
                "asc",
                gp,
            ),
            DriverSpec("retail_margin", "Retail gross margin, % of retail sales", "%", "pct", 0, 1, "asc", gp),
            DriverSpec("runs", "Kennel runs / suites", "runs", "int", 1, 10000, section=bd),
            DriverSpec(
                "occ", "Average boarding occupancy at maturity, % of run-nights (year 1)", "%", "pct", 0, 1, "asc", bd
            ),
            DriverSpec("occ_g", "Occupancy growth per year (capped at 100%)", "%", "pct", -0.9, 5, "asc", bd),
            DriverSpec(
                "peak_uplift",
                "Peak-season uplift, June-August and December (monthly models)",
                "%",
                "pct",
                0,
                1,
                section=bd,
            ),
            DriverSpec("nights_m", "Calendar nights per month", "nights", "dec1", 28, 31, section=bd),
            DriverSpec("night_rate", "Average nightly rate per run (year 1)", "$", "usd2", 0, 1e4, "asc", bd),
            DriverSpec("commission_pct", "Groomer commission, % of grooming revenue", "%", "pct", 0, 1, "desc", cos),
            DriverSpec(
                "supplies_groom", "Shampoo, blades & supplies per groom (year 1)", "$", "usd2", 0, 1e4, "desc", cos
            ),
            DriverSpec(
                "board_night", "Food, cleaning & laundry per boarded night (year 1)", "$", "usd2", 0, 1e4, "desc", cos
            ),
            DriverSpec("rent", "Shop rent or land cost per month", "$", "usd", 0, 1e7, section=fix),
            DriverSpec("rent_g", "Rent increase per year", "%", "pct", 0, 0.5, section=fix),
            DriverSpec("insurance", "Insurance (care, custody, liability) per month", "$", "usd", 0, 1e7, section=fix),
            DriverSpec(
                "ga_other", "Utilities, software, vet-on-call & other G&A per month", "$", "usd", 0, 1e7, section=fix
            ),
            DriverSpec("mkt", "Marketing budget per month (year 1)", "$", "usd", 0, 1e7, section=fix),
            DriverSpec("mkt_g", "Marketing budget growth per year", "%", "pct", -0.9, 5, "asc", fix),
            DriverSpec("card_pct", "Card processing fees, % of revenue", "%", "pct", 0, 0.2, "desc", fix),
            DriverSpec(
                "cost_g",
                "Cost increase per year (insurance, utilities, supplies, food)",
                "%",
                "pct",
                -0.5,
                1,
                "desc",
                fix,
            ),
            DriverSpec(
                "capex_table", "Grooming table, tub & dryer per station (month 1)", "$", "usd", 0, 1e7, section=cx
            ),
            DriverSpec("capex_run", "Kennel run build-out per run (month 1)", "$", "usd", 0, 1e7, section=cx),
            DriverSpec(
                "capex_fit",
                "Leasehold improvements, flooring, HVAC & signage (month 1)",
                "$",
                "usd",
                0,
                1e8,
                section=cx,
            ),
            DriverSpec(
                "capex_land",
                "Land or building purchase (month 1; never depreciated, 0 = leased shop)",
                "$",
                "usd",
                0,
                1e8,
                section=cx,
            ),
            DriverSpec(
                "capex_refresh", "Equipment & kennel refresh per year (from year 2)", "$", "usd", 0, 1e8, section=cx
            ),
        ]

    def validate(self, brief: Brief) -> None:
        if GROOMER not in {r.key for r in brief.roles}:
            raise BriefError("template 'pet_care' needs the 'groomer' (groomers) role")
        super().validate(brief)

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        if t.granularity == "monthly":
            season = (
                "=IF(OR(AND(MOD({p}-1,12)>=5,MOD({p}-1,12)<=7),MOD({p}-1,12)=11),"
                "1+{in:peak_uplift},1-{in:peak_uplift}/2)"
            )
        else:
            season = "=1"
        idx = "(1+{in:price_g})^({y}-1)"
        cidx = "(1+{in:cost_g})^({y}-1)"
        ramp = (
            "=IF({in:ramp_months}<=0,1,({ramp_n}*{in:ramp_start}"
            "+(1-{in:ramp_start})/MAX(1,{in:ramp_months})*({ramp_n}*({p}-1)*{mpp}+{ramp_n}*({ramp_n}-1)/2)"
            "+{mpp}-{ramp_n})/{mpp})"
        )
        return [
            Line(
                "ramp_n",
                "Helper: months of the period still on the ramp-up",
                "=MAX(0,MIN({mpp},{in:ramp_months}-({p}-1)*{mpp}))",
                "top",
                "dec1",
                agg="none",
                section="Grooming demand",
            ),
            Line("ramp", "Ramp-up factor (share of mature volume)", ramp, "top", "pct", agg="none"),
            Line(
                "groom_demand",
                "Grooms demanded",
                "={in:grooms_day}*(1+{in:groom_g})^({y}-1)*{in:days_open}*{mpp}*{ramp}",
                "top",
                "int",
            ),
            Line(
                "groomer_fte",
                "Groomers (FTE)",
                "={hc_groomer_fte}",
                "top",
                "dec1",
                agg="last",
                section="Grooming capacity",
            ),
            Line(
                "cap_tables",
                "Station capacity (stations × grooms per station-day × operating days)",
                "={in:tables}*{in:grooms_table}*{in:days_open}*{mpp}",
                "top",
                "int",
            ),
            Line(
                "cap_groomers",
                "Groomer capacity (FTE × grooms per groomer-day × operating days)",
                "={groomer_fte}*{in:grooms_groomer}*{in:days_open}*{mpp}",
                "top",
                "int",
            ),
            Line(
                "groom_cap",
                "Grooming capacity (lower of stations and groomers)",
                "=MIN({cap_tables},{cap_groomers})",
                "top",
                "int",
            ),
            Line(
                "grooms",
                "Grooms completed (demand capped by capacity)",
                "=MIN({groom_demand},{groom_cap})",
                "top",
                "int",
                bold=True,
            ),
            Line("lost_grooms", "Grooms lost to the capacity limit", "={groom_demand}-{grooms}", "top", "int"),
            Line(
                "season",
                "Boarding season factor (June-August, December)",
                season,
                "top",
                "dec3",
                agg="none",
                section="Boarding",
            ),
            Line(
                "avail_nights",
                "Available run-nights (runs × calendar nights)",
                "={in:runs}*{in:nights_m}*{mpp}",
                "top",
                "int",
            ),
            Line(
                "occ_eff",
                "Occupancy (maturity × growth × ramp × season, capped at 100%)",
                "=MIN(1,{in:occ}*(1+{in:occ_g})^({y}-1)*{ramp}*{season})",
                "top",
                "pct",
                agg="none",
            ),
            Line("nights", "Boarded run-nights", "={avail_nights}*{occ_eff}", "top", "int", bold=True),
            Line(
                "groom_price_now",
                "Average price per groom",
                f"={{in:groom_price}}*{idx}",
                "top",
                "usd2",
                agg="last",
                section="Revenue",
            ),
            Line("rev_groom", "Grooming revenue", "={grooms}*{groom_price_now}", "top"),
            Line("rev_board", "Boarding revenue", f"={{nights}}*{{in:night_rate}}*{idx}", "top"),
            Line("rev_retail", "Retail revenue", f"={{grooms}}*{{in:retail_groom}}*{idx}", "top"),
            Line("rev", "Revenue", "={rev_groom}+{rev_board}+{rev_retail}", "top", bold=True, total=True),
            Line("cost_groomers", "Groomer base pay", "={hc_groomer_cost}", "top", section="Cost of sales"),
            Line("commission", "Groomer commission", "=-{rev_groom}*{in:commission_pct}", "top"),
            Line("groom_supplies", "Grooming supplies", f"=-{{grooms}}*{{in:supplies_groom}}*{cidx}", "top"),
            Line("board_cost", "Boarding food, cleaning & laundry", f"=-{{nights}}*{{in:board_night}}*{cidx}", "top"),
            Line("retail_cost", "Retail cost of goods", "=-{rev_retail}*(1-{in:retail_margin})", "top"),
            Line(
                "cogs",
                "Cost of sales",
                "={cost_groomers}+{commission}+{groom_supplies}+{board_cost}+{retail_cost}",
                "top",
                bold=True,
            ),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        cidx = "(1+{in:cost_g})^({y}-1)"
        return [
            Line(
                "payroll_nb",
                "Attendants, manager & other payroll",
                "={payroll_total}-{hc_groomer_cost}",
                "top",
                section="Operating expenses",
            ),
            Line("rent", "Shop rent or land cost", "=-{in:rent}*(1+{in:rent_g})^({y}-1)*{mpp}", "top"),
            Line("insurance", "Insurance", f"=-{{in:insurance}}*{cidx}*{{mpp}}", "top"),
            Line("ga_other", "Utilities, software & other G&A", f"=-{{in:ga_other}}*{cidx}*{{mpp}}", "top"),
            Line("mkt", "Marketing", "=-{in:mkt}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
            Line("card_fees", "Card processing fees", "=-{rev}*{in:card_pct}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [
            Line("capex_tables", "Grooming tables, tubs & dryers", "=IF({p}=1,{in:tables}*{in:capex_table},0)", "top"),
            Line("capex_runs", "Kennel run build-out", "=IF({p}=1,{in:runs}*{in:capex_run},0)", "top"),
            Line("capex_fit", "Leasehold improvements & signage", "=IF({p}=1,{in:capex_fit},0)", "top"),
            Line("capex_land", "Land or building (not depreciated)", "=IF({p}=1,{in:capex_land},0)", "top"),
            Line(
                "capex_refresh",
                "Equipment & kennel refresh (first period of each year from year 2)",
                "=IF(AND({y}>1,MOD({p}-1,{ppy})=0),{in:capex_refresh},0)",
                "top",
            ),
            Line(
                "capex",
                "Capital spending",
                "={capex_tables}+{capex_runs}+{capex_fit}+{capex_land}+{capex_refresh}",
                "top",
                bold=True,
            ),
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("grooms", "Grooms completed", "kpi:grooms", "int"),
            DashMetric("groom_use", "Grooming capacity used", "kpi:groom_use", "pct"),
            DashMetric("occ_rate", "Boarding occupancy", "kpi:occ_rate", "pct"),
            DashMetric("revpan", "Boarding revenue per available run-night", "kpi:revpan", "usd2"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Grooms completed & boarding occupancy", bars=("grooms",), lines=("occ_rate",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("groomer_fte", "Groomers (FTE)", "line", "groomer_fte", "dec1", bold=True),
            StmtRow("grooms", "Grooms completed", "line", "grooms", "int", bold=True),
            StmtRow("groom_cap", "Grooming capacity (lower of stations and groomers)", "line", "groom_cap", "int"),
            StmtRow(
                "groom_use", "Grooming capacity used", "formula", "=IF({groom_cap}=0,0,{grooms}/{groom_cap})", "pct"
            ),
            StmtRow("lost_grooms", "Grooms lost to the capacity limit", "line", "lost_grooms", "int"),
            StmtRow("nights", "Boarded run-nights", "line", "nights", "int", bold=True),
            StmtRow("avail_n", "Available run-nights", "line", "avail_nights", "int"),
            StmtRow("occ_rate", "Boarding occupancy", "formula", "=IF({avail_n}=0,0,{nights}/{avail_n})", "pct"),
            StmtRow("rev", "Revenue", "line", "rev", bold=True),
            StmtRow("rev_groom", "Grooming revenue", "line", "rev_groom"),
            StmtRow("rev_board", "Boarding revenue", "line", "rev_board"),
            StmtRow("rev_retail", "Retail revenue", "line", "rev_retail"),
            StmtRow("board_share", "Boarding share of revenue", "formula", "=IF({rev}=0,0,{rev_board}/{rev})", "pct"),
            StmtRow(
                "groom_ticket",
                "Revenue per groom (grooming + retail)",
                "formula",
                "=IF({grooms}=0,0,({rev_groom}+{rev_retail})/{grooms})",
                "usd2",
            ),
            StmtRow(
                "revpan",
                "Boarding revenue per available run-night",
                "formula",
                "=IF({avail_n}=0,0,{rev_board}/{avail_n})",
                "usd2",
            ),
            StmtRow(
                "rev_groomer",
                "Revenue per groomer (year-end FTE)",
                "formula",
                "=IF({groomer_fte}=0,0,{rev}/{groomer_fte})",
            ),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("ebitda", "EBITDA", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
        ]

    def kpi_charts(self, t: Timing) -> list[KpiChart]:
        return [
            KpiChart("Grooms completed and boarding occupancy", bars=("grooms",), lines=("occ_rate",)),
            KpiChart(
                "Grooming, boarding and retail revenue, EBITDA margin",
                bars=("rev_groom", "rev_board", "rev_retail"),
                lines=("em",),
                stacked=True,
            ),
        ]

    # ------------------------------------------------------------------ python twin
    def kpi_reference(self, ann: dict, d: dict, t: Timing) -> dict:
        out: dict[str, dict] = {k: {} for k in self.kpi_derived}
        for y in range(1, t.years + 1):
            rev, grooms = ann["rev"][y], ann["grooms"][y]
            out["groom_use"][y] = div(grooms, ann["groom_cap"][y])
            out["occ_rate"][y] = div(ann["nights"][y], ann["avail_nights"][y])
            out["board_share"][y] = div(ann["rev_board"][y], rev)
            out["groom_ticket"][y] = div(ann["rev_groom"][y] + ann["rev_retail"][y], grooms)
            out["revpan"][y] = div(ann["rev_board"][y], ann["avail_nights"][y])
            out["rev_groomer"][y] = div(rev, ann["groomer_fte"][y])
            out["gm"][y] = div(ann["gp"][y], rev)
            out["em"][y] = div(ann["ebitda"][y], rev)
        return out

    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        fte, groomer_cost = role_period(d, GROOMER, p, t)
        ramp = _ramp(d, p, t)
        demand = d["grooms_day"] * (1 + d["groom_g"]) ** (y - 1) * d["days_open"] * t.mpp * ramp
        cap_tables = d["tables"] * d["grooms_table"] * d["days_open"] * t.mpp
        cap_groomers = fte * d["grooms_groomer"] * d["days_open"] * t.mpp
        cap = min(cap_tables, cap_groomers)
        grooms = min(demand, cap)
        avail = d["runs"] * d["nights_m"] * t.mpp
        occ = min(1.0, d["occ"] * (1 + d["occ_g"]) ** (y - 1) * ramp * _season(d, p, t))
        nights = avail * occ
        idx = (1 + d["price_g"]) ** (y - 1)
        cidx = (1 + d["cost_g"]) ** (y - 1)
        rev_groom = grooms * d["groom_price"] * idx
        rev_board = nights * d["night_rate"] * idx
        rev_retail = grooms * d["retail_groom"] * idx
        rev = rev_groom + rev_board + rev_retail
        cogs = (
            groomer_cost
            - rev_groom * d["commission_pct"]
            - grooms * d["supplies_groom"] * cidx
            - nights * d["board_night"] * cidx
            - rev_retail * (1 - d["retail_margin"])
        )
        land = d["capex_land"] if p == 1 else 0.0
        refresh = d["capex_refresh"] if y > 1 and (p - 1) % t.ppy == 0 else 0.0
        capex = refresh + land
        if p == 1:
            capex += d["tables"] * d["capex_table"] + d["runs"] * d["capex_run"] + d["capex_fit"]
        return Top(
            rev=rev,
            cogs=cogs,
            opex={
                "payroll_nb": hc.payroll - groomer_cost,
                "rent": -d["rent"] * (1 + d["rent_g"]) ** (y - 1) * t.mpp,
                "insurance": -d["insurance"] * cidx * t.mpp,
                "ga_other": -d["ga_other"] * cidx * t.mpp,
                "mkt": -d["mkt"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp,
                "card_fees": -rev * d["card_pct"],
            },
            capex=capex,
            land=land,
            kpis={
                "grooms": grooms,
                "groom_cap": cap,
                "lost_grooms": demand - grooms,
                "groomer_fte": fte,
                "nights": nights,
                "avail_nights": avail,
                "rev_groom": rev_groom,
                "rev_board": rev_board,
                "rev_retail": rev_retail,
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
                "model_name": f"Pet grooming & boarding financial model ({stage})",
                "template": self.key,
                "business_type": "pet_care",
                "stage": stage,
                "assumption_note": "Illustrative assumptions - replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
