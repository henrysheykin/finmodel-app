"""Car wash template: express tunnel with retail cars and unlimited-plan members.

Two customer groups share one tunnel. Retail cars arrive per operating day (a linear ramp-up from opening and
a winter dip in monthly models) and pay the average price per wash plus add-ons. Unlimited-plan members open
with the presale / current base; each period new members join from a share of retail cars and from direct
sign-ups, a monthly share cancels (start + adds - churn, as in the SaaS and fitness templates). Members pay a
monthly fee whatever they use; their washes cost money but earn nothing extra, so members drive variable cost,
not revenue. Total washes are capped by the tunnel's practical throughput; above the cap retail revenue and
member washes are scaled down in proportion. Chemicals, water, electricity and card fees are cost of sales;
the site lease, maintenance, payroll and marketing are operating expenses; tunnel equipment, building and
site works and pay stations are capex (optional equipment loan).
Assumption memo: docs/templates/car_wash.md.
"""

from __future__ import annotations

from engine.brief import Brief
from engine.core import HC, Top
from engine.spec import DashChart, DashMetric, DriverSpec, KpiChart, Line, StmtRow, Timing
from engine.templates.base import Template, div

ROLES = [
    ("manager", "Site manager"),
    ("crew", "Wash attendants & customer service"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer replaces
# them with their own numbers; the assumption memo says which are sourced and which are assumptions.
_COMMON = {
    "days_open": (29, 29, 29),
    "winter_dip": (0.2, 0.15, 0.1),
    "cph": (140, 140, 140),
    "hours_day": (11, 11, 11),
    "cap_util": (0.55, 0.55, 0.55),
    "conv": (0.006, 0.008, 0.01),
    "churn_m": (0.05, 0.04, 0.032),
    "wash_pm": (3.8, 3.5, 3.2),
    "price": (12, 13, 14),
    "addon": (1.2, 1.5, 1.8),
    "mem_fee": (32, 35, 38),
    "price_g": (0.01, 0.02, 0.03),
    "chem_car": (0.95, 0.85, 0.75),
    "water_gal": (45, 40, 36),
    "water_rate": (10, 9, 8),
    "elec_car": (0.45, 0.42, 0.4),
    "card_pct": (0.032, 0.03, 0.028),
    "cost_g": (0.04, 0.03, 0.025),
    "lease_g": (0.03, 0.03, 0.03),
    "payroll_tax": (0.12, 0.12, 0.12),
    "wage_g": (0.03, 0.03, 0.03),
    "ar_days": (2, 2, 2),
    "inv_days": (15, 15, 15),
    "ap_days": (25, 25, 25),
    "dep_years": (12, 12, 12),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "cars_day": (200, 240, 280),
            "ramp_months": (12, 9, 7),
            "ramp_start": (0.35, 0.45, 0.55),
            "members_start": (150, 250, 350),
            "mem_new": (40, 50, 60),
            "mem_g": (0.0, 0.05, 0.1),
            "lease": (30000, 30000, 30000),
            "maint": (5500, 5500, 5500),
            "ga_other": (9500, 9500, 9500),
            "mkt": (12000, 12000, 12000),
            "mkt_g": (-0.3, -0.2, -0.1),
            "capex_equip": (1650000, 1650000, 1650000),
            "capex_site": (2300000, 2300000, 2300000),
            "capex_pay": (150000, 150000, 150000),
            "capex_refresh": (40000, 40000, 40000),
            "equity": (2100000, 2100000, 2100000),
            "loan_amount": (3000000, 3000000, 3000000),
            "loan_rate": (0.085, 0.085, 0.085),
            "loan_term_years": (10, 10, 10),
        },
        "roles": {"manager": (1, 72000, 1, 0.0), "crew": (10, 32000, 1, 0.0)},
    },
    "early": {
        "drivers": {
            "cars_day": (210, 250, 290),
            "ramp_months": (6, 4, 3),
            "ramp_start": (0.65, 0.75, 0.85),
            "members_start": (900, 1100, 1300),
            "mem_new": (40, 50, 60),
            "mem_g": (0.0, 0.05, 0.1),
            "lease": (30000, 30000, 30000),
            "maint": (5500, 5500, 5500),
            "ga_other": (9500, 9500, 9500),
            "mkt": (9000, 9000, 9000),
            "mkt_g": (-0.2, -0.1, 0.0),
            "capex_equip": (80000, 80000, 80000),
            "capex_site": (40000, 40000, 40000),
            "capex_pay": (10000, 10000, 10000),
            "capex_refresh": (40000, 40000, 40000),
            "equity": (350000, 350000, 350000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {"manager": (1, 72000, 1, 0.0), "crew": (10, 32000, 1, 0.0)},
    },
    "growing": {
        "drivers": {
            "cars_day": (220, 260, 300),
            "ramp_months": (0, 0, 0),
            "ramp_start": (1, 1, 1),
            "members_start": (1500, 1800, 2100),
            "mem_new": (45, 55, 65),
            "mem_g": (0.0, 0.05, 0.1),
            "lease": (31000, 31000, 31000),
            "maint": (6000, 6000, 6000),
            "ga_other": (10000, 10000, 10000),
            "mkt": (8000, 8000, 8000),
            "mkt_g": (0.0, 0.03, 0.06),
            "capex_equip": (150000, 150000, 150000),
            "capex_site": (60000, 60000, 60000),
            "capex_pay": (20000, 20000, 20000),
            "capex_refresh": (60000, 60000, 60000),
            "equity": (250000, 250000, 250000),
            "loan_amount": (400000, 400000, 400000),
            "loan_rate": (0.085, 0.085, 0.085),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {"manager": (1.5, 74000, 1, 0.0), "crew": (11, 33000, 1, 0.0)},
    },
    "established": {
        "drivers": {
            "cars_day": (220, 260, 300),
            "ramp_months": (0, 0, 0),
            "ramp_start": (1, 1, 1),
            "members_start": (2400, 2800, 3200),
            "mem_new": (50, 60, 70),
            "mem_g": (0.0, 0.03, 0.06),
            "lease": (32000, 32000, 32000),
            "maint": (7000, 7000, 7000),
            "ga_other": (11000, 11000, 11000),
            "mkt": (6000, 6000, 6000),
            "mkt_g": (0.0, 0.03, 0.06),
            "capex_equip": (100000, 100000, 100000),
            "capex_site": (40000, 40000, 40000),
            "capex_pay": (10000, 10000, 10000),
            "capex_refresh": (80000, 80000, 80000),
            "equity": (150000, 150000, 150000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {"manager": (2, 76000, 1, 0.0), "crew": (12, 34000, 1, 0.0)},
    },
}


def _ramp(d: dict, p: int, t: Timing) -> float:
    """Average share of mature retail volume in period ``p``: a straight line from ``ramp_start`` to 1 over
    ``ramp_months`` months, averaged over the months the period covers (so annual = the mean of its months)."""
    months = d["ramp_months"]
    if months <= 0:
        return 1.0
    j0 = (p - 1) * t.mpp  # months elapsed before the period
    n = max(0.0, min(float(t.mpp), months - j0))  # months of the period still on the ramp
    s = d["ramp_start"]
    return (n * s + (1 - s) / months * (n * j0 + n * (n - 1) / 2) + t.mpp - n) / t.mpp


def _season(d: dict, p: int, t: Timing) -> float:
    """Winter dip December-February (model month 1 = January); the other nine months give it back (year unchanged)."""
    if t.granularity != "monthly":
        return 1.0
    m = (p - 1) % 12  # 0 = January
    dip = d["winter_dip"]
    return 1 - dip if m in (11, 0, 1) else 1 + dip / 3


class CarWashTemplate(Template):
    key = "car_wash"
    title = "Car wash (express tunnel)"
    business_types = ("car_wash",)
    order = 110
    key_numbers = ("cars_day", "price", "members_start", "mem_fee", "churn_m", "lease", "capex_equip", "equity")
    sample_title = "Car wash"
    sample_desc = "Full workbook with retail cars, unlimited members, tunnel capacity and the site lease"
    sample_stage = "planning"
    kpi_title = "Car wash metrics"
    kpi_checked = {
        "members_end": "members_close",
        "new_m": "new_total",
        "lost_m": "churned",
        "washes": "washes",
        "ret_cars": "ret_cars",
        "mem_washes": "mem_washes",
        "cap_washes": "cap_washes",
        "lost_w": "lost_washes",
        "rev": "rev",
        "rev_mem": "rev_mem",
        "var_cost": "var_cost",
        "gp": "gp",
        "ebitda": "ebitda",
    }
    kpi_derived = (
        "churn",
        "mem_share",
        "washes_day",
        "cap_use",
        "rev_retail",
        "mem_rev_share",
        "rev_per_wash",
        "rev_per_member_wash",
        "var_per_wash",
        "gm",
        "em",
    )
    kpi_flows = (
        "new_total",
        "churned",
        "washes",
        "ret_cars",
        "mem_washes",
        "lost_washes",
        "cap_washes",
        "rev_mem",
        "var_cost",
    )

    def driver_specs(self) -> list[DriverSpec]:
        vol, cap, mem, price, var, fix, cx = (
            "Retail volume",
            "Tunnel capacity",
            "Unlimited members",
            "Prices",
            "Variable cost per wash",
            "Site costs",
            "Capital spending",
        )
        return [
            DriverSpec(
                "cars_day", "Retail cars per operating day at maturity (year 1)", "cars", "dec1", 0, 1e5, "asc", vol
            ),
            DriverSpec("days_open", "Operating days per month", "days", "dec1", 1, 31, section=vol),
            DriverSpec(
                "ramp_months",
                "Months to reach mature retail volume (0 = already mature)",
                "months",
                "int",
                0,
                60,
                "desc",
                vol,
                integer=True,
            ),
            DriverSpec("ramp_start", "Retail volume in month 1, % of mature", "%", "pct", 0, 1, "asc", vol),
            DriverSpec(
                "winter_dip", "Winter volume dip, December-February (monthly models)", "%", "pct", 0, 0.9, "desc", vol
            ),
            DriverSpec("cph", "Rated tunnel speed", "cars/hour", "int", 1, 1e4, section=cap),
            DriverSpec("hours_day", "Hours open per day", "hours", "dec1", 1, 24, section=cap),
            DriverSpec(
                "cap_util", "Practical throughput, % of rated speed over open hours", "%", "pct", 0.01, 1, section=cap
            ),
            DriverSpec(
                "members_start", "Unlimited members at start (presale or current base)", "#", "int", 0, 1e6, "asc", mem
            ),
            DriverSpec("mem_new", "Direct sign-ups per month at maturity (year 1)", "#", "dec1", 0, 1e5, "asc", mem),
            DriverSpec("mem_g", "Direct sign-ups growth per year", "%", "pct", -0.9, 5, "asc", mem),
            DriverSpec("conv", "Retail cars that sign up for an unlimited plan", "%", "pct", 0, 1, "asc", mem),
            DriverSpec("churn_m", "Members who cancel per month", "%", "pct", 0, 1, "desc", mem),
            DriverSpec("wash_pm", "Washes per member per month", "washes", "dec1", 0, 60, "desc", mem),
            DriverSpec("price", "Average price per retail wash (year 1)", "$", "usd2", 0, 1e4, "asc", price),
            DriverSpec(
                "addon", "Add-on revenue per retail car (wax, ceramic, tire shine)", "$", "usd2", 0, 1e4, "asc", price
            ),
            DriverSpec(
                "mem_fee", "Unlimited plan fee per member per month (year 1)", "$", "usd2", 0, 1e4, "asc", price
            ),
            DriverSpec("price_g", "Price increase per year", "%", "pct", -0.5, 1, "asc", price),
            DriverSpec("chem_car", "Chemicals per wash", "$", "usd2", 0, 100, "desc", var),
            DriverSpec("water_gal", "Fresh water per wash (after reclaim)", "gallons", "dec1", 0, 1e4, "desc", var),
            DriverSpec("water_rate", "Water and sewer rate per 1,000 gallons", "$", "usd2", 0, 1e3, "desc", var),
            DriverSpec("elec_car", "Electricity per wash", "$", "usd2", 0, 100, "desc", var),
            DriverSpec("card_pct", "Card processing fees, % of revenue", "%", "pct", 0, 0.2, "desc", var),
            DriverSpec(
                "cost_g",
                "Cost increase per year (per-wash costs, maintenance, other)",
                "%",
                "pct",
                -0.5,
                1,
                "desc",
                var,
            ),
            DriverSpec("lease", "Site lease or land cost per month", "$", "usd", 0, 1e7, section=fix),
            DriverSpec("lease_g", "Lease increase per year", "%", "pct", 0, 0.5, section=fix),
            DriverSpec("maint", "Equipment maintenance & repairs per month", "$", "usd", 0, 1e7, section=fix),
            DriverSpec(
                "ga_other", "Insurance, property tax, software & other G&A per month", "$", "usd", 0, 1e7, section=fix
            ),
            DriverSpec("mkt", "Marketing budget per month (year 1)", "$", "usd", 0, 1e7, section=fix),
            DriverSpec("mkt_g", "Marketing budget growth per year", "%", "pct", -0.9, 5, "asc", fix),
            DriverSpec("capex_equip", "Tunnel equipment (month 1)", "$", "usd", 0, 1e8, section=cx),
            DriverSpec("capex_site", "Building & site works (month 1)", "$", "usd", 0, 1e8, section=cx),
            DriverSpec("capex_pay", "Pay stations, signage & vacuums (month 1)", "$", "usd", 0, 1e8, section=cx),
            DriverSpec(
                "capex_refresh", "Equipment refresh & upgrades per year (from year 2)", "$", "usd", 0, 1e8, section=cx
            ),
        ]

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        if t.granularity == "monthly":
            season = "=IF(OR(MOD({p}-1,12)>=11,MOD({p}-1,12)<=1),1-{in:winter_dip},1+{in:winter_dip}/3)"
            close = "={members_open}*(1-{in:churn_m})+{new_total}"
        else:
            season = "=1"
            close = "={members_open}*(1-{in:churn_m})^12+{new_total}*(1-{in:churn_m})^6"
        idx = "(1+{in:price_g})^({y}-1)"
        cidx = "(1+{in:cost_g})^({y}-1)"
        ramp = (
            "=IF({in:ramp_months}<=0,1,({ramp_n}*{in:ramp_start}"
            "+(1-{in:ramp_start})/{in:ramp_months}*({ramp_n}*({p}-1)*{mpp}+{ramp_n}*({ramp_n}-1)/2)"
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
                section="Volume",
            ),
            Line("ramp", "Ramp-up factor (share of mature retail volume)", ramp, "top", "pct", agg="none"),
            Line("season", "Season factor (winter dip)", season, "top", "dec3", agg="none"),
            Line(
                "ret_demand",
                "Retail cars demanded",
                "={in:cars_day}*{in:days_open}*{mpp}*{ramp}*{season}",
                "top",
                "int",
            ),
            Line(
                "new_conv", "New members from retail cars", "={ret_demand}*{in:conv}", "top", "dec1", section="Members"
            ),
            Line(
                "new_direct",
                "New members from direct sign-ups",
                "={in:mem_new}*(1+{in:mem_g})^({y}-1)*{mpp}*{ramp}",
                "top",
                "dec1",
            ),
            Line("new_total", "New members - total", "={new_conv}+{new_direct}", "top", "dec1", bold=True),
            Line(
                "members_open",
                "Members - opening",
                "={members_close[-1]}",
                "top",
                "dec1",
                first="={in:members_start}",
                agg="first",
            ),
            Line("churned", "Members who cancelled", "={members_close}-{members_open}-{new_total}", "top", "dec1"),
            Line("members_close", "Members - closing", close, "top", "dec1", agg="last", bold=True),
            Line("members_avg", "Members - average", "=({members_open}+{members_close})/2", "top", "dec1", agg="none"),
            Line(
                "mem_demand",
                "Member washes demanded",
                "={members_avg}*{in:wash_pm}*{season}*{mpp}",
                "top",
                "int",
                section="Washes",
            ),
            Line(
                "cap_washes",
                "Tunnel capacity (rated speed × hours × practical share × days)",
                "={in:cph}*{in:hours_day}*{in:cap_util}*{in:days_open}*{mpp}",
                "top",
                "int",
            ),
            Line(
                "served",
                "Share of demand the tunnel can wash",
                "=IF({ret_demand}+{mem_demand}<=0,1,MIN(1,{cap_washes}/({ret_demand}+{mem_demand})))",
                "top",
                "pct",
                agg="none",
            ),
            Line("ret_cars", "Retail cars washed", "={ret_demand}*{served}", "top", "int"),
            Line("mem_washes", "Member washes", "={mem_demand}*{served}", "top", "int"),
            Line("washes", "Washes - total", "={ret_cars}+{mem_washes}", "top", "int", bold=True),
            Line(
                "lost_washes",
                "Washes lost to the capacity limit",
                "={ret_demand}+{mem_demand}-{washes}",
                "top",
                "int",
            ),
            Line(
                "price_now",
                "Average price per retail wash",
                f"={{in:price}}*{idx}",
                "top",
                "usd2",
                agg="last",
                section="Revenue",
            ),
            Line("fee_now", "Unlimited plan fee per month", f"={{in:mem_fee}}*{idx}", "top", "usd2", agg="last"),
            Line("rev_wash", "Retail wash revenue", "={ret_cars}*{price_now}", "top"),
            Line("rev_addon", "Add-on revenue", f"={{ret_cars}}*{{in:addon}}*{idx}", "top"),
            Line("rev_mem", "Unlimited plan fees", "={members_avg}*{fee_now}*{mpp}", "top"),
            Line("rev", "Revenue", "={rev_wash}+{rev_addon}+{rev_mem}", "top", bold=True, total=True),
            Line(
                "chem",
                "Chemicals",
                f"=-{{washes}}*{{in:chem_car}}*{cidx}",
                "top",
                section="Cost of sales",
            ),
            Line("water", "Water & sewer", f"=-{{washes}}*{{in:water_gal}}/1000*{{in:water_rate}}*{cidx}", "top"),
            Line("elec", "Electricity", f"=-{{washes}}*{{in:elec_car}}*{cidx}", "top"),
            Line("var_cost", "Chemicals, water & electricity", "={chem}+{water}+{elec}", "top"),
            Line("card_fees", "Card processing fees", "=-{rev}*{in:card_pct}", "top"),
            Line("cogs", "Cost of sales", "={var_cost}+{card_fees}", "top", bold=True),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        cidx = "(1+{in:cost_g})^({y}-1)"
        return [
            Line("payroll", "Site payroll", "={payroll_total}", "top", section="Operating expenses"),
            Line("lease", "Site lease or land cost", "=-{in:lease}*(1+{in:lease_g})^({y}-1)*{mpp}", "top"),
            Line("maint", "Equipment maintenance & repairs", f"=-{{in:maint}}*{cidx}*{{mpp}}", "top"),
            Line("ga_other", "Insurance, property tax, software & other", f"=-{{in:ga_other}}*{cidx}*{{mpp}}", "top"),
            Line("mkt", "Marketing", "=-{in:mkt}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [
            Line("capex_equip", "Tunnel equipment", "=IF({p}=1,{in:capex_equip},0)", "top"),
            Line("capex_site", "Building & site works", "=IF({p}=1,{in:capex_site},0)", "top"),
            Line("capex_pay", "Pay stations, signage & vacuums", "=IF({p}=1,{in:capex_pay},0)", "top"),
            Line(
                "capex_refresh",
                "Equipment refresh & upgrades (first period of each year from year 2)",
                "=IF(AND({y}>1,MOD({p}-1,{ppy})=0),{in:capex_refresh},0)",
                "top",
            ),
            Line(
                "capex",
                "Capital spending",
                "={capex_equip}+{capex_site}+{capex_pay}+{capex_refresh}",
                "top",
                bold=True,
            ),
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("members", "Unlimited members (year end)", "kpi:members_end", "int"),
            DashMetric("washes_day", "Washes per operating day", "kpi:washes_day", "int"),
            DashMetric("cap_use", "Tunnel capacity used", "kpi:cap_use", "pct"),
            DashMetric("rev_wash", "Revenue per wash", "kpi:rev_per_wash", "usd2"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Washes per day & tunnel capacity used", bars=("washes_day",), lines=("cap_use",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("members_end", "Unlimited members (year end)", "line", "members_close", "int", bold=True),
            StmtRow("new_m", "New members in the year", "line", "new_total", "int"),
            StmtRow("lost_m", "Members who cancelled in the year", "line", "churned", "int"),
            StmtRow("churn", "Members who cancel per month", "formula", "={in:churn_m}", "pct"),
            StmtRow("washes", "Washes in the year", "line", "washes", "int", bold=True),
            StmtRow("ret_cars", "Retail cars washed", "line", "ret_cars", "int"),
            StmtRow("mem_washes", "Member washes", "line", "mem_washes", "int"),
            StmtRow("mem_share", "Member share of washes", "formula", "=IF({washes}=0,0,{mem_washes}/{washes})", "pct"),
            StmtRow(
                "washes_day",
                "Washes per operating day",
                "formula",
                "=IF({in:days_open}=0,0,{washes}/({in:days_open}*12))",
                "int",
            ),
            StmtRow("cap_washes", "Tunnel capacity (washes)", "line", "cap_washes", "int"),
            StmtRow("cap_use", "Tunnel capacity used", "formula", "=IF({cap_washes}=0,0,{washes}/{cap_washes})", "pct"),
            StmtRow("lost_w", "Washes lost to the capacity limit", "line", "lost_washes", "int"),
            StmtRow("rev", "Revenue", "line", "rev", bold=True),
            StmtRow("rev_mem", "Unlimited plan fees", "line", "rev_mem"),
            StmtRow("rev_retail", "Retail wash & add-on revenue", "formula", "={rev}-{rev_mem}"),
            StmtRow("mem_rev_share", "Plan fees share of revenue", "formula", "=IF({rev}=0,0,{rev_mem}/{rev})", "pct"),
            StmtRow("rev_per_wash", "Revenue per wash", "formula", "=IF({washes}=0,0,{rev}/{washes})", "usd2"),
            StmtRow(
                "rev_per_member_wash",
                "Plan fee revenue per member wash",
                "formula",
                "=IF({mem_washes}=0,0,{rev_mem}/{mem_washes})",
                "usd2",
            ),
            StmtRow("var_cost", "Chemicals, water & electricity", "line", "var_cost"),
            StmtRow(
                "var_per_wash",
                "Chemicals, water & electricity per wash",
                "formula",
                "=IF({washes}=0,0,-{var_cost}/{washes})",
                "usd2",
            ),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("ebitda", "EBITDA", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
        ]

    # ------------------------------------------------------------------ python twin
    def kpi_charts(self, t: Timing) -> list[KpiChart]:
        return [
            KpiChart(
                "Retail and member washes, tunnel capacity used",
                bars=("ret_cars", "mem_washes"),
                lines=("cap_use",),
                stacked=True,
            ),
            KpiChart("Revenue split and EBITDA margin", bars=("rev_retail", "rev_mem"), lines=("em",), stacked=True),
        ]

    def kpi_reference(self, ann: dict, d: dict, t: Timing) -> dict:
        out: dict[str, dict] = {k: {} for k in self.kpi_derived}
        for y in range(1, t.years + 1):
            washes, rev = ann["washes"][y], ann["rev"][y]
            out["churn"][y] = d["churn_m"]
            out["mem_share"][y] = div(ann["mem_washes"][y], washes)
            out["washes_day"][y] = div(washes, d["days_open"] * 12)
            out["cap_use"][y] = div(washes, ann["cap_washes"][y])
            out["rev_retail"][y] = rev - ann["rev_mem"][y]
            out["mem_rev_share"][y] = div(ann["rev_mem"][y], rev)
            out["rev_per_wash"][y] = div(rev, washes)
            out["rev_per_member_wash"][y] = div(ann["rev_mem"][y], ann["mem_washes"][y])
            out["var_per_wash"][y] = div(-ann["var_cost"][y], washes)
            out["gm"][y] = div(ann["gp"][y], rev)
            out["em"][y] = div(ann["ebitda"][y], rev)
        return out

    def _members(self, d: dict, t: Timing, upto: int) -> tuple[float, float, float, float]:
        """(opening, closing, new_conv, new_direct) members of period ``upto``; replays the roll-forward."""
        r = 1 - d["churn_m"]
        members = d["members_start"]
        for p in range(1, upto + 1):
            y = t.year_of(p)
            ramp = _ramp(d, p, t)
            ret_dem = d["cars_day"] * d["days_open"] * t.mpp * ramp * _season(d, p, t)
            new_conv = ret_dem * d["conv"]
            new_direct = d["mem_new"] * (1 + d["mem_g"]) ** (y - 1) * t.mpp * ramp
            new = new_conv + new_direct
            opening = members
            members = opening * r + new if t.granularity == "monthly" else opening * r**12 + new * r**6
        return opening, members, new_conv, new_direct

    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        m0, m1, new_conv, new_direct = self._members(d, t, p)
        new = new_conv + new_direct
        avg = (m0 + m1) / 2
        season = _season(d, p, t)
        ret_dem = d["cars_day"] * d["days_open"] * t.mpp * _ramp(d, p, t) * season
        mem_dem = avg * d["wash_pm"] * season * t.mpp
        cap = d["cph"] * d["hours_day"] * d["cap_util"] * d["days_open"] * t.mpp
        demand = ret_dem + mem_dem
        share = 1.0 if demand <= 0 else min(1.0, cap / demand)
        ret_cars, mem_washes = ret_dem * share, mem_dem * share
        washes = ret_cars + mem_washes
        idx = (1 + d["price_g"]) ** (y - 1)
        cidx = (1 + d["cost_g"]) ** (y - 1)
        rev_mem = avg * d["mem_fee"] * idx * t.mpp
        rev = ret_cars * d["price"] * idx + ret_cars * d["addon"] * idx + rev_mem
        var_cost = -washes * (d["chem_car"] + d["water_gal"] / 1000 * d["water_rate"] + d["elec_car"]) * cidx
        refresh = d["capex_refresh"] if y > 1 and (p - 1) % t.ppy == 0 else 0.0
        capex = refresh + (d["capex_equip"] + d["capex_site"] + d["capex_pay"] if p == 1 else 0.0)
        return Top(
            rev=rev,
            cogs=var_cost - rev * d["card_pct"],
            opex={
                "payroll": hc.payroll,
                "lease": -d["lease"] * (1 + d["lease_g"]) ** (y - 1) * t.mpp,
                "maint": -d["maint"] * cidx * t.mpp,
                "ga_other": -d["ga_other"] * cidx * t.mpp,
                "mkt": -d["mkt"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp,
            },
            capex=capex,
            kpis={
                "members_close": m1,
                "new_total": new,
                "churned": m1 - m0 - new,
                "washes": washes,
                "ret_cars": ret_cars,
                "mem_washes": mem_washes,
                "lost_washes": demand - washes,
                "cap_washes": cap,
                "rev_mem": rev_mem,
                "var_cost": var_cost,
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
                "model_name": f"Car wash financial model ({stage})",
                "template": self.key,
                "business_type": "car_wash",
                "stage": stage,
                "assumption_note": "Illustrative assumptions - replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
