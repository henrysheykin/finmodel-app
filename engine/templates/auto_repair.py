"""Auto repair shop template: repair orders x billed hours, capped by service bays and technicians.

Repair orders arrive per operating day (a linear ramp-up from opening, then a yearly growth rate); each
order needs a number of billed labor hours. Hours billed = the lower of demand and capacity, where capacity
is the smaller of the bay limit (bays x billed hours a bay can carry per day) and the technician limit
(technicians x paid hours per day x efficiency). Labor revenue = billed hours x the effective labor rate;
parts revenue = billed hours x parts sales per billed hour (a parts margin sets the parts cost); a shop supplies
fee is a share of labor revenue. Technician payroll, parts, shop supplies and comebacks (warranty rework) are
cost of sales; advisors and manager payroll, rent, insurance, software and marketing are operating expenses;
lifts and bay equipment (per bay), diagnostic tools and leasehold improvements are capex (optional land).
Assumption memo: docs/templates/auto_repair.md.
"""

from __future__ import annotations

from engine.brief import Brief, BriefError
from engine.core import HC, Top, role_period
from engine.spec import DashChart, DashMetric, DriverSpec, KpiChart, Line, StmtRow, Timing
from engine.templates.base import Template, div

TECH = "tech"
ROLES = [
    (TECH, "Technicians"),
    ("advisor", "Service advisors & front desk"),
    ("manager", "Shop manager"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data: the customer replaces
# them with their own numbers; the assumption memo labels every figure as an assumption.
_COMMON = {
    "days_open": (25, 25, 25),
    "hrs_ro": (2.0, 2.0, 2.0),
    "bay_hours": (6.0, 6.5, 7.0),
    "tech_hours": (8, 8, 8),
    "tech_eff": (0.82, 0.88, 0.95),
    "labor_rate": (118, 125, 132),
    "parts_hr": (92, 100, 108),
    "parts_margin": (0.44, 0.47, 0.5),
    "supplies_pct": (0.04, 0.05, 0.05),
    "supplies_cost_pct": (0.04, 0.035, 0.03),
    "warranty_pct": (0.04, 0.03, 0.025),
    "price_g": (0.01, 0.03, 0.04),
    "card_pct": (0.032, 0.03, 0.028),
    "rent_g": (0.03, 0.03, 0.03),
    "cost_g": (0.04, 0.03, 0.025),
    "payroll_tax": (0.15, 0.15, 0.15),
    "wage_g": (0.04, 0.03, 0.03),
    "ar_days": (3, 3, 3),
    "inv_days": (8, 8, 8),
    "ap_days": (25, 25, 25),
    "dep_years": (8, 8, 8),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "bays": (6, 6, 6),
            "ro_day": (11, 13.5, 16),
            "ro_g": (0.0, 0.03, 0.06),
            "ramp_months": (16, 12, 9),
            "ramp_start": (0.3, 0.4, 0.5),
            "rent": (18000, 18000, 18000),
            "insurance": (4500, 4500, 4500),
            "ga_other": (9000, 9000, 9000),
            "mkt": (7000, 7000, 7000),
            "mkt_g": (-0.3, -0.2, -0.1),
            "capex_bay": (22000, 22000, 22000),
            "capex_diag": (70000, 70000, 70000),
            "capex_fit": (180000, 180000, 180000),
            "capex_land": (0, 0, 0),
            "capex_refresh": (20000, 20000, 20000),
            "equity": (480000, 480000, 480000),
            "loan_amount": (250000, 250000, 250000),
            "loan_rate": (0.09, 0.09, 0.09),
            "loan_term_years": (7, 7, 7),
        },
        "roles": {
            "tech": (5, 78000, 1, 0.0),
            "advisor": (2, 50000, 1, 0.0),
            "manager": (1, 85000, 1, 0.0),
        },
    },
    "early": {
        "drivers": {
            "bays": (6, 6, 6),
            "ro_day": (11, 13.5, 16),
            "ro_g": (0.0, 0.03, 0.06),
            "ramp_months": (6, 4, 3),
            "ramp_start": (0.6, 0.7, 0.8),
            "rent": (18000, 18000, 18000),
            "insurance": (4500, 4500, 4500),
            "ga_other": (9000, 9000, 9000),
            "mkt": (5000, 5000, 5000),
            "mkt_g": (-0.1, 0.0, 0.05),
            "capex_bay": (5000, 5000, 5000),
            "capex_diag": (15000, 15000, 15000),
            "capex_fit": (20000, 20000, 20000),
            "capex_land": (0, 0, 0),
            "capex_refresh": (20000, 20000, 20000),
            "equity": (150000, 150000, 150000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "tech": (5, 78000, 1, 0.0),
            "advisor": (2, 50000, 1, 0.0),
            "manager": (1, 85000, 1, 0.0),
        },
    },
    "growing": {
        "drivers": {
            "bays": (8, 8, 8),
            "ro_day": (14, 18, 22),
            "ro_g": (0.0, 0.03, 0.05),
            "ramp_months": (0, 0, 0),
            "ramp_start": (1, 1, 1),
            "rent": (21000, 21000, 21000),
            "insurance": (5500, 5500, 5500),
            "ga_other": (10500, 10500, 10500),
            "mkt": (6000, 6000, 6000),
            "mkt_g": (0.0, 0.03, 0.06),
            "capex_bay": (6000, 6000, 6000),
            "capex_diag": (25000, 25000, 25000),
            "capex_fit": (30000, 30000, 30000),
            "capex_land": (0, 0, 0),
            "capex_refresh": (30000, 30000, 30000),
            "equity": (200000, 200000, 200000),
            "loan_amount": (150000, 150000, 150000),
            "loan_rate": (0.09, 0.09, 0.09),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {
            "tech": (7, 79000, 1, 0.0),
            "advisor": (2.5, 52000, 1, 0.0),
            "manager": (1, 88000, 1, 0.0),
        },
    },
    "established": {
        "drivers": {
            "bays": (8, 8, 8),
            "ro_day": (16, 20, 23),
            "ro_g": (0.0, 0.02, 0.04),
            "ramp_months": (0, 0, 0),
            "ramp_start": (1, 1, 1),
            "rent": (22000, 22000, 22000),
            "insurance": (6000, 6000, 6000),
            "ga_other": (11500, 11500, 11500),
            "mkt": (5000, 5000, 5000),
            "mkt_g": (0.0, 0.03, 0.06),
            "capex_bay": (3000, 3000, 3000),
            "capex_diag": (15000, 15000, 15000),
            "capex_fit": (15000, 15000, 15000),
            "capex_land": (0, 0, 0),
            "capex_refresh": (35000, 35000, 35000),
            "equity": (200000, 200000, 200000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "tech": (8, 80000, 1, 0.0),
            "advisor": (3, 54000, 1, 0.0),
            "manager": (1, 90000, 1, 0.0),
        },
    },
}


def _ramp(d: dict, p: int, t: Timing) -> float:
    """Average share of mature order volume in period ``p``: a straight line from ``ramp_start`` to 1 over
    ``ramp_months`` months, averaged over the months the period covers (so annual = the mean of its months)."""
    months = d["ramp_months"]
    if months <= 0:
        return 1.0
    j0 = (p - 1) * t.mpp  # months elapsed before the period
    n = max(0.0, min(float(t.mpp), months - j0))  # months of the period still on the ramp
    s = d["ramp_start"]
    return (n * s + (1 - s) / max(1, months) * (n * j0 + n * (n - 1) / 2) + t.mpp - n) / t.mpp


class AutoRepairTemplate(Template):
    key = "auto_repair"
    title = "Auto repair shop"
    business_types = ("auto_repair",)
    order = 120
    key_numbers = ("ro_day", "labor_rate", "bays", "parts_margin", "rent", "capex_bay", "equity")
    sample_title = "Auto repair shop"
    sample_desc = "Full workbook with service bays, technician hours, labor rate, parts margin and the shop lease"
    sample_stage = "planning"
    kpi_title = "Auto repair metrics"
    kpi_checked = {
        "billed_h": "billed",
        "ro": "ro",
        "cap_h": "cap_hours",
        "lost_h": "lost_hours",
        "tech_fte": "tech_fte",
        "rev_labor": "rev_labor",
        "rev_parts": "rev_parts",
        "parts_cost": "parts_cost",
        "rev": "rev",
        "gp": "gp",
        "ebitda": "ebitda",
    }
    kpi_derived = (
        "cap_use",
        "bay_use",
        "rev_ro",
        "rev_hour",
        "rev_tech",
        "parts_share",
        "parts_gm",
        "gm",
        "em",
    )
    kpi_flows = ("billed", "ro", "cap_hours", "lost_hours", "rev_labor", "rev_parts", "parts_cost")

    def driver_specs(self) -> list[DriverSpec]:
        dem, cap, price, parts, cost, fix, cx = (
            "Repair orders",
            "Shop capacity",
            "Labor prices",
            "Parts & supplies",
            "Cost of sales",
            "Shop costs",
            "Capital spending",
        )
        return [
            DriverSpec(
                "ro_day", "Repair orders per operating day at maturity (year 1)", "orders", "dec1", 0, 1e4, "asc", dem
            ),
            DriverSpec("ro_g", "Repair orders growth per year", "%", "pct", -0.9, 5, "asc", dem),
            DriverSpec("hrs_ro", "Billed labor hours per repair order", "hours", "dec1", 0.1, 100, "asc", dem),
            DriverSpec("days_open", "Operating days per month", "days", "dec1", 1, 31, section=dem),
            DriverSpec(
                "ramp_months",
                "Months to reach mature order volume (0 = already mature)",
                "months",
                "int",
                0,
                60,
                "desc",
                dem,
                integer=True,
            ),
            DriverSpec("ramp_start", "Order volume in month 1, % of mature", "%", "pct", 0, 1, "asc", dem),
            DriverSpec("bays", "Service bays (lifts)", "bays", "int", 1, 1000, section=cap),
            DriverSpec(
                "bay_hours", "Billed hours one bay can carry per operating day", "hours", "dec1", 0.1, 48, "asc", cap
            ),
            DriverSpec(
                "tech_hours", "Paid hours per technician per operating day", "hours", "dec1", 1, 24, section=cap
            ),
            DriverSpec(
                "tech_eff",
                "Technician efficiency (billed hours per paid hour)",
                "%",
                "pct",
                0.05,
                3,
                "asc",
                cap,
            ),
            DriverSpec(
                "labor_rate", "Effective labor rate per billed hour (year 1)", "$", "usd2", 0, 1e4, "asc", price
            ),
            DriverSpec("price_g", "Price increase per year", "%", "pct", -0.5, 1, "asc", price),
            DriverSpec("supplies_pct", "Shop supplies fee, % of labor revenue", "%", "pct", 0, 1, "asc", price),
            DriverSpec("parts_hr", "Parts sales per billed labor hour (year 1)", "$", "usd2", 0, 1e4, "asc", parts),
            DriverSpec("parts_margin", "Parts gross margin, % of parts sales", "%", "pct", 0, 1, "asc", parts),
            DriverSpec(
                "supplies_cost_pct",
                "Shop supplies & waste disposal cost, % of labor revenue",
                "%",
                "pct",
                0,
                1,
                "desc",
                cost,
            ),
            DriverSpec(
                "warranty_pct",
                "Comebacks & warranty rework, % of labor revenue",
                "%",
                "pct",
                0,
                1,
                "desc",
                cost,
            ),
            DriverSpec("card_pct", "Card processing fees, % of revenue", "%", "pct", 0, 0.2, "desc", cost),
            DriverSpec(
                "cost_g", "Cost increase per year (insurance, software & other)", "%", "pct", -0.5, 1, "desc", cost
            ),
            DriverSpec("rent", "Shop rent or land cost per month", "$", "usd", 0, 1e7, section=fix),
            DriverSpec("rent_g", "Rent increase per year", "%", "pct", 0, 0.5, section=fix),
            DriverSpec(
                "insurance", "Insurance (garage liability, property) per month", "$", "usd", 0, 1e7, section=fix
            ),
            DriverSpec(
                "ga_other",
                "Shop software, diagnostic subscriptions, utilities & other G&A per month",
                "$",
                "usd",
                0,
                1e7,
                section=fix,
            ),
            DriverSpec("mkt", "Marketing budget per month (year 1)", "$", "usd", 0, 1e7, section=fix),
            DriverSpec("mkt_g", "Marketing budget growth per year", "%", "pct", -0.9, 5, "asc", fix),
            DriverSpec("capex_bay", "Lift & bay equipment per bay (month 1)", "$", "usd", 0, 1e7, section=cx),
            DriverSpec("capex_diag", "Diagnostic tools & scan equipment (month 1)", "$", "usd", 0, 1e8, section=cx),
            DriverSpec("capex_fit", "Leasehold improvements & signage (month 1)", "$", "usd", 0, 1e8, section=cx),
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
                "capex_refresh", "Equipment & tool refresh per year (from year 2)", "$", "usd", 0, 1e8, section=cx
            ),
        ]

    def validate(self, brief: Brief) -> None:
        if TECH not in {r.key for r in brief.roles}:
            raise BriefError("template 'auto_repair' needs the 'tech' (technicians) role")
        super().validate(brief)

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        idx = "(1+{in:price_g})^({y}-1)"
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
                section="Demand",
            ),
            Line("ramp", "Ramp-up factor (share of mature order volume)", ramp, "top", "pct", agg="none"),
            Line(
                "ro_demand",
                "Repair orders demanded",
                "={in:ro_day}*(1+{in:ro_g})^({y}-1)*{in:days_open}*{mpp}*{ramp}",
                "top",
                "int",
            ),
            Line("hours_demand", "Billed hours demanded", "={ro_demand}*{in:hrs_ro}", "top", "int"),
            Line("tech_fte", "Technicians (FTE)", "={hc_tech_fte}", "top", "dec1", agg="last", section="Capacity"),
            Line(
                "cap_bay",
                "Bay capacity (bays × billed hours per bay-day × operating days)",
                "={in:bays}*{in:bay_hours}*{in:days_open}*{mpp}",
                "top",
                "int",
            ),
            Line(
                "cap_tech",
                "Technician capacity (FTE × paid hours × efficiency × operating days)",
                "={tech_fte}*{in:tech_hours}*{in:tech_eff}*{in:days_open}*{mpp}",
                "top",
                "int",
            ),
            Line(
                "cap_hours",
                "Billed-hour capacity (lower of bays and technicians)",
                "=MIN({cap_bay},{cap_tech})",
                "top",
                "int",
            ),
            Line(
                "billed",
                "Billed labor hours (demand capped by capacity)",
                "=MIN({hours_demand},{cap_hours})",
                "top",
                "int",
                bold=True,
            ),
            Line("lost_hours", "Billed hours lost to the capacity limit", "={hours_demand}-{billed}", "top", "int"),
            Line(
                "served",
                "Share of demand the shop can serve",
                "=MIN(1,{billed}/MAX(1,{hours_demand}))",
                "top",
                "pct",
                agg="none",
            ),
            Line("ro", "Repair orders completed", "={ro_demand}*{served}", "top", "int"),
            Line(
                "rate_now",
                "Effective labor rate per billed hour",
                f"={{in:labor_rate}}*{idx}",
                "top",
                "usd2",
                agg="last",
                section="Revenue",
            ),
            Line("rev_labor", "Labor revenue", "={billed}*{rate_now}", "top"),
            Line("rev_parts", "Parts revenue", f"={{billed}}*{{in:parts_hr}}*{idx}", "top"),
            Line("rev_supplies", "Shop supplies fee", "={rev_labor}*{in:supplies_pct}", "top"),
            Line("rev", "Revenue", "={rev_labor}+{rev_parts}+{rev_supplies}", "top", bold=True, total=True),
            Line("cost_tech", "Technician payroll", "={hc_tech_cost}", "top", section="Cost of sales"),
            Line("parts_cost", "Parts cost", "=-{rev_parts}*(1-{in:parts_margin})", "top"),
            Line("supplies_cost", "Shop supplies & waste disposal", "=-{rev_labor}*{in:supplies_cost_pct}", "top"),
            Line("warranty", "Comebacks & warranty rework", "=-{rev_labor}*{in:warranty_pct}", "top"),
            Line(
                "cogs",
                "Cost of sales",
                "={cost_tech}+{parts_cost}+{supplies_cost}+{warranty}",
                "top",
                bold=True,
            ),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        cidx = "(1+{in:cost_g})^({y}-1)"
        return [
            Line(
                "payroll_nb",
                "Advisors, manager & other payroll",
                "={payroll_total}-{hc_tech_cost}",
                "top",
                section="Operating expenses",
            ),
            Line("rent", "Shop rent or land cost", "=-{in:rent}*(1+{in:rent_g})^({y}-1)*{mpp}", "top"),
            Line("insurance", "Insurance", f"=-{{in:insurance}}*{cidx}*{{mpp}}", "top"),
            Line("ga_other", "Software, utilities & other G&A", f"=-{{in:ga_other}}*{cidx}*{{mpp}}", "top"),
            Line("mkt", "Marketing", "=-{in:mkt}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
            Line("card_fees", "Card processing fees", "=-{rev}*{in:card_pct}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [
            Line("capex_lifts", "Lifts & bay equipment", "=IF({p}=1,{in:bays}*{in:capex_bay},0)", "top"),
            Line("capex_diag", "Diagnostic tools & scan equipment", "=IF({p}=1,{in:capex_diag},0)", "top"),
            Line("capex_fit", "Leasehold improvements & signage", "=IF({p}=1,{in:capex_fit},0)", "top"),
            Line("capex_land", "Land or building (not depreciated)", "=IF({p}=1,{in:capex_land},0)", "top"),
            Line(
                "capex_refresh",
                "Equipment & tool refresh (first period of each year from year 2)",
                "=IF(AND({y}>1,MOD({p}-1,{ppy})=0),{in:capex_refresh},0)",
                "top",
            ),
            Line(
                "capex",
                "Capital spending",
                "={capex_lifts}+{capex_diag}+{capex_fit}+{capex_land}+{capex_refresh}",
                "top",
                bold=True,
            ),
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("billed_h", "Billed labor hours", "kpi:billed_h", "int"),
            DashMetric("cap_use", "Shop capacity used", "kpi:cap_use", "pct"),
            DashMetric("rev_ro", "Revenue per repair order", "kpi:rev_ro", "usd2"),
            DashMetric("rev_hour", "Revenue per billed hour", "kpi:rev_hour", "usd2"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Billed hours & shop capacity used", bars=("billed_h",), lines=("cap_use",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("tech_fte", "Technicians (FTE, year end)", "line", "tech_fte", "dec1", bold=True),
            StmtRow("ro", "Repair orders completed", "line", "ro", "int", bold=True),
            StmtRow("billed_h", "Billed labor hours", "line", "billed", "int", bold=True),
            StmtRow("cap_h", "Billed-hour capacity (lower of bays and technicians)", "line", "cap_hours", "int"),
            StmtRow("cap_use", "Shop capacity used", "formula", "=IF({cap_h}=0,0,{billed_h}/{cap_h})", "pct"),
            StmtRow(
                "bay_use",
                "Bay capacity used (billed hours ÷ bay limit)",
                "formula",
                "=IF({in:bays}*{in:bay_hours}*{in:days_open}=0,0,{billed_h}/({in:bays}*{in:bay_hours}*{in:days_open}*12))",
                "pct",
            ),
            StmtRow("lost_h", "Billed hours lost to the capacity limit", "line", "lost_hours", "int"),
            StmtRow("rev", "Revenue", "line", "rev", bold=True),
            StmtRow("rev_labor", "Labor revenue", "line", "rev_labor"),
            StmtRow("rev_parts", "Parts revenue", "line", "rev_parts"),
            StmtRow("parts_share", "Parts share of revenue", "formula", "=IF({rev}=0,0,{rev_parts}/{rev})", "pct"),
            StmtRow("rev_ro", "Revenue per repair order", "formula", "=IF({ro}=0,0,{rev}/{ro})", "usd2"),
            StmtRow("rev_hour", "Revenue per billed hour", "formula", "=IF({billed_h}=0,0,{rev}/{billed_h})", "usd2"),
            StmtRow(
                "rev_tech",
                "Revenue per technician (year-end FTE)",
                "formula",
                "=IF({tech_fte}=0,0,{rev}/{tech_fte})",
            ),
            StmtRow("parts_cost", "Parts cost", "line", "parts_cost"),
            StmtRow(
                "parts_gm",
                "Parts gross margin",
                "formula",
                "=IF({rev_parts}=0,0,({rev_parts}+{parts_cost})/{rev_parts})",
                "pct",
            ),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("ebitda", "EBITDA", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
        ]

    def kpi_charts(self, t: Timing) -> list[KpiChart]:
        return [
            KpiChart("Billed hours and shop capacity used", bars=("billed_h",), lines=("cap_use",)),
            KpiChart(
                "Labor and parts revenue, EBITDA margin", bars=("rev_labor", "rev_parts"), lines=("em",), stacked=True
            ),
        ]

    # ------------------------------------------------------------------ python twin
    def kpi_reference(self, ann: dict, d: dict, t: Timing) -> dict:
        out: dict[str, dict] = {k: {} for k in self.kpi_derived}
        for y in range(1, t.years + 1):
            rev, billed = ann["rev"][y], ann["billed"][y]
            out["cap_use"][y] = div(billed, ann["cap_hours"][y])
            bay_cap = d["bays"] * d["bay_hours"] * d["days_open"]
            out["bay_use"][y] = div(billed, bay_cap * 12) if bay_cap else 0.0
            out["rev_ro"][y] = div(rev, ann["ro"][y])
            out["rev_hour"][y] = div(rev, billed)
            out["rev_tech"][y] = div(rev, ann["tech_fte"][y])
            out["parts_share"][y] = div(ann["rev_parts"][y], rev)
            out["parts_gm"][y] = div(ann["rev_parts"][y] + ann["parts_cost"][y], ann["rev_parts"][y])
            out["gm"][y] = div(ann["gp"][y], rev)
            out["em"][y] = div(ann["ebitda"][y], rev)
        return out

    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        fte, tech_cost = role_period(d, TECH, p, t)
        ro_demand = d["ro_day"] * (1 + d["ro_g"]) ** (y - 1) * d["days_open"] * t.mpp * _ramp(d, p, t)
        hours_demand = ro_demand * d["hrs_ro"]
        cap_bay = d["bays"] * d["bay_hours"] * d["days_open"] * t.mpp
        cap_tech = fte * d["tech_hours"] * d["tech_eff"] * d["days_open"] * t.mpp
        cap = min(cap_bay, cap_tech)
        billed = min(hours_demand, cap)
        served = min(1.0, billed / max(1.0, hours_demand))
        idx = (1 + d["price_g"]) ** (y - 1)
        cidx = (1 + d["cost_g"]) ** (y - 1)
        rev_labor = billed * d["labor_rate"] * idx
        rev_parts = billed * d["parts_hr"] * idx
        rev = rev_labor + rev_parts + rev_labor * d["supplies_pct"]
        parts_cost = -rev_parts * (1 - d["parts_margin"])
        cogs = tech_cost + parts_cost - rev_labor * d["supplies_cost_pct"] - rev_labor * d["warranty_pct"]
        land = d["capex_land"] if p == 1 else 0.0
        refresh = d["capex_refresh"] if y > 1 and (p - 1) % t.ppy == 0 else 0.0
        capex = refresh + land
        if p == 1:
            capex += d["bays"] * d["capex_bay"] + d["capex_diag"] + d["capex_fit"]
        return Top(
            rev=rev,
            cogs=cogs,
            opex={
                "payroll_nb": hc.payroll - tech_cost,
                "rent": -d["rent"] * (1 + d["rent_g"]) ** (y - 1) * t.mpp,
                "insurance": -d["insurance"] * cidx * t.mpp,
                "ga_other": -d["ga_other"] * cidx * t.mpp,
                "mkt": -d["mkt"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp,
                "card_fees": -rev * d["card_pct"],
            },
            capex=capex,
            land=land,
            kpis={
                "billed": billed,
                "ro": ro_demand * served,
                "cap_hours": cap,
                "lost_hours": hours_demand - billed,
                "tech_fte": fte,
                "rev_labor": rev_labor,
                "rev_parts": rev_parts,
                "parts_cost": parts_cost,
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
                "model_name": f"Auto repair shop financial model ({stage})",
                "template": self.key,
                "business_type": "auto_repair",
                "stage": stage,
                "assumption_note": "Illustrative assumptions - replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
