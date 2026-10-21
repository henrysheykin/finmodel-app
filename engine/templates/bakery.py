"""Bakery template: retail counter (customers × ticket × opening days) plus wholesale accounts.

Retail revenue = customers per day (ramping to full traffic, growing yearly, with a November-December
holiday peak in monthly models) × average ticket × opening days. Wholesale revenue = accounts × weekly
order value, ramping with the same opening curve. Cost of sales = ingredients (own % for retail and
wholesale), the cost of the retail production that is baked but not sold (waste) and packaging. Payroll
comes from the headcount roles (bakers on early shifts, counter staff, manager); wholesale deliveries
cost a fixed amount per drop. Ovens, mixers and display cases are bought at start and replaced yearly.
Assumption memo: docs/templates/bakery.md.
"""

from __future__ import annotations

from engine.brief import Brief
from engine.core import HC, Top
from engine.spec import DashChart, DashMetric, DriverSpec, KpiChart, Line, StmtRow, Timing
from engine.templates.base import Template, div

ROLES = [
    ("baker", "Bakers & production"),
    ("counter", "Counter staff"),
    ("manager", "Manager"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer replaces
# them with their own numbers; the assumption memo says so for every driver.
_COMMON = {
    "ticket": (11.0, 11.5, 12.0),
    "price_g": (0.02, 0.03, 0.04),
    "traffic_g": (0.01, 0.03, 0.05),
    "open_days": (6, 6, 6),
    "peak_uplift": (0.2, 0.2, 0.2),
    "ws_g": (0.08, 0.12, 0.16),
    "ws_order": (500, 540, 580),
    "ws_deliv_wk": (5, 5, 5),
    "ingr_pct": (0.255, 0.24, 0.225),
    "ws_ingr_pct": (0.345, 0.33, 0.315),
    "waste_pct": (0.11, 0.09, 0.07),
    "pack_pct": (0.037, 0.035, 0.033),
    "cost_drop": (9.5, 9, 8.5),
    "mkt_pct": (0.022, 0.02, 0.018),
    "card_pct": (0.029, 0.028, 0.027),
    "payroll_tax": (0.12, 0.12, 0.12),
    "wage_g": (0.03, 0.03, 0.03),
    "inv_days": (3, 3, 3),
    "ap_days": (18, 18, 18),
    "dep_years": (7, 7, 7),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "cust_full": (205, 220, 235),
            "ramp_months": (11, 9, 7),
            "open_pct": (0.4, 0.45, 0.5),
            "ws_accounts": (5, 6, 7),
            "ar_days": (6, 6, 6),
            "rent": (8500, 8500, 8500),
            "utilities": (2800, 2800, 2800),
            "maint": (600, 600, 600),
            "ga_other": (1800, 1800, 1800),
            "capex": (240000, 240000, 240000),
            "capex_repl": (6000, 6000, 6000),
            "equity": (200000, 200000, 200000),
            "loan_amount": (150000, 150000, 150000),
            "loan_rate": (0.09, 0.09, 0.09),
            "loan_term_years": (7, 7, 7),
        },
        "roles": {
            "baker": (3, 42000, 1, 0.04),
            "counter": (4.5, 30000, 1, 0.04),
            "manager": (1, 58000, 1, 0.0),
        },
    },
    "early": {
        "drivers": {
            "cust_full": (245, 260, 275),
            "ramp_months": (7, 6, 5),
            "open_pct": (0.6, 0.65, 0.7),
            "ws_accounts": (7.5, 9, 10.5),
            "ar_days": (7, 7, 7),
            "rent": (9500, 9500, 9500),
            "utilities": (3200, 3200, 3200),
            "maint": (700, 700, 700),
            "ga_other": (2000, 2000, 2000),
            "capex": (40000, 40000, 40000),
            "capex_repl": (8000, 8000, 8000),
            "equity": (90000, 90000, 90000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "baker": (3.5, 42000, 1, 0.04),
            "counter": (5, 30000, 1, 0.04),
            "manager": (1, 58000, 1, 0.0),
        },
    },
    "growing": {
        "drivers": {
            "cust_full": (300, 320, 340),
            "ramp_months": (3, 2, 1),
            "open_pct": (0.85, 0.9, 0.95),
            "ws_accounts": (13, 16, 19),
            "ar_days": (9, 9, 9),
            "rent": (12000, 12000, 12000),
            "utilities": (4000, 4000, 4000),
            "maint": (1000, 1000, 1000),
            "ga_other": (2800, 2800, 2800),
            "capex": (90000, 90000, 90000),
            "capex_repl": (14000, 14000, 14000),
            "equity": (60000, 60000, 60000),
            "loan_amount": (80000, 80000, 80000),
            "loan_rate": (0.085, 0.085, 0.085),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {
            "baker": (5, 44000, 1, 0.06),
            "counter": (7, 31000, 1, 0.06),
            "manager": (1.5, 62000, 1, 0.0),
        },
    },
    "established": {
        "drivers": {
            "cust_full": (420, 440, 460),
            "ramp_months": (1, 1, 1),
            "open_pct": (1, 1, 1),
            "ws_accounts": (22, 26, 30),
            "ar_days": (10, 10, 10),
            "rent": (16000, 16000, 16000),
            "utilities": (5600, 5600, 5600),
            "maint": (1600, 1600, 1600),
            "ga_other": (4200, 4200, 4200),
            "capex": (60000, 60000, 60000),
            "capex_repl": (24000, 24000, 24000),
            "equity": (50000, 50000, 50000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "baker": (7.5, 44000, 1, 0.03),
            "counter": (9, 31000, 1, 0.03),
            "manager": (2, 62000, 1, 0.0),
        },
    },
}


def _season(p: int, t: Timing, uplift: float) -> float:
    """Holiday peak November-December: +uplift in those two months, -uplift/5 in the other ten (year unchanged)."""
    if t.granularity != "monthly":
        return 1.0
    return 1 + uplift if (p - 1) % 12 >= 10 else 1 - uplift / 5


class BakeryTemplate(Template):
    key = "bakery"
    title = "Bakery (retail counter + wholesale)"
    business_types = ("bakery",)
    order = 80
    key_numbers = ("cust_full", "ticket", "ws_accounts", "ws_order", "waste_pct", "rent", "capex", "equity")
    sample_title = "Bakery"
    sample_desc = "Full workbook with counter traffic, wholesale accounts, waste, deliveries and ovens"
    sample_stage = "growing"
    kpi_title = "Bakery metrics"
    kpi_checked = {
        "days": "days",
        "tx": "tx",
        "accounts_end": "accounts",
        "rev": "rev",
        "rev_retail": "rev_retail",
        "rev_ws": "rev_ws",
        "waste_k": "waste",
        "deliv_k": "deliv",
        "gp": "gp",
        "ebitda": "ebitda",
    }
    kpi_derived = ("cust_day", "ticket", "ws_share", "rev_day", "waste_share", "gm", "cogs_k", "pay_k", "prime", "em")
    kpi_unit_rows = ("rev_day",)
    kpi_flows = ("days", "tx", "rev_retail", "rev_ws", "waste", "deliv")

    def driver_specs(self) -> list[DriverSpec]:
        ret, whl, cos, cost, cap = "Retail counter", "Wholesale", "Cost of sales", "Operating costs", "Equipment"
        return [
            DriverSpec("cust_full", "Customers per day at full traffic", "#", "int", 0, 1e5, "asc", ret),
            DriverSpec("ramp_months", "Months to reach full traffic", "months", "int", 0, 36, "desc", ret, True),
            DriverSpec("open_pct", "Opening traffic, % of full", "%", "pct", 0, 1, "asc", ret),
            DriverSpec("traffic_g", "Traffic growth per year (after year 1)", "%", "pct", -0.5, 1, "asc", ret),
            DriverSpec("ticket", "Average ticket per customer (year 1)", "$", "usd2", 0, 1000, "asc", ret),
            DriverSpec("price_g", "Price increase per year", "%", "pct", -0.5, 1, "asc", ret),
            DriverSpec("open_days", "Opening days per week", "days", "dec1", 1, 7, section=ret),
            DriverSpec("peak_uplift", "Holiday uplift, Nov-Dec (monthly models)", "%", "pct", 0, 1, section=ret),
            DriverSpec("ws_accounts", "Wholesale accounts at full ramp (year 1)", "#", "dec1", 0, 1e5, "asc", whl),
            DriverSpec("ws_g", "Wholesale accounts growth per year", "%", "pct", -0.9, 5, "asc", whl),
            DriverSpec("ws_order", "Order value per account per week (year 1)", "$", "usd", 0, 1e6, "asc", whl),
            DriverSpec("ws_deliv_wk", "Deliveries per account per week", "#", "dec1", 0, 14, section=whl),
            DriverSpec("cost_drop", "Delivery cost per drop (driver, fuel, van)", "$", "usd2", 0, 1000, "desc", whl),
            DriverSpec(
                "ingr_pct", "Ingredients of items sold, % of retail sales (excl. waste)", "%", "pct", 0, 1, "desc", cos
            ),
            DriverSpec("ws_ingr_pct", "Ingredients of items sold, % of wholesale sales", "%", "pct", 0, 1, "desc", cos),
            DriverSpec("waste_pct", "Retail production baked but not sold (waste)", "%", "pct", 0, 0.5, "desc", cos),
            DriverSpec("pack_pct", "Packaging, % of sales", "%", "pct", 0, 0.3, "desc", cos),
            DriverSpec("rent", "Rent per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("utilities", "Utilities per month (gas, power, water)", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("maint", "Equipment repairs & cleaning per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("mkt_pct", "Marketing, % of revenue", "%", "pct", 0, 1, "desc", cost),
            DriverSpec("card_pct", "Card processing fees, % of retail sales", "%", "pct", 0, 0.2, "desc", cost),
            DriverSpec("ga_other", "Insurance, licences & other G&A per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("capex", "Fit-out & equipment: ovens, mixers, cases", "$", "usd", 0, 1e8, section=cap),
            DriverSpec("capex_repl", "Equipment replacement per year (from year 2)", "$", "usd", 0, 1e8, section=cap),
        ]

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        if t.granularity == "monthly":
            ramp = [
                Line(
                    "ramp",
                    "Traffic ramp factor",
                    "=MIN(1,{in:open_pct}+(1-{in:open_pct})*({p}-1)/MAX(1,{in:ramp_months}))",
                    "top",
                    "pct",
                    agg="none",
                    section="Retail counter",
                )
            ]
            season = "=IF(MOD({p}-1,12)>=10,1+{in:peak_uplift},1-{in:peak_uplift}/5)"
        else:
            # exact average of the monthly ramp over the 12 months of the year
            ramp = [
                Line(
                    "ramp_n",
                    "Helper: months below full traffic in the year",
                    "=MAX(0,MIN(12,MAX(1,{in:ramp_months})-12*({y}-1)))",
                    "top",
                    "int",
                    agg="none",
                    section="Retail counter",
                ),
                Line(
                    "ramp",
                    "Traffic ramp factor (average for the year)",
                    "=({ramp_n}*{in:open_pct}+(1-{in:open_pct})/MAX(1,{in:ramp_months})"
                    "*({ramp_n}*12*({y}-1)+{ramp_n}*({ramp_n}-1)/2)+12-{ramp_n})/12",
                    "top",
                    "pct",
                    agg="none",
                ),
            ]
            season = "=1"
        idx = "(1+{in:price_g})^({y}-1)"
        return ramp + [
            Line(
                "season", "Season factor (November-December peak, added to the ramp)", season, "top", "dec1", agg="none"
            ),
            Line(
                "cust",
                "Customers per day",
                "={in:cust_full}*(1+{in:traffic_g})^({y}-1)*MAX(0,{ramp}+{season}-1)",
                "top",
                "dec1",
                agg="none",
            ),
            Line("days", "Opening days in period", "={in:open_days}*52/12*{mpp}", "top", "dec1"),
            Line("tx", "Retail transactions", "={cust}*{days}", "top", "int"),
            Line("ticket", "Average ticket", f"={{in:ticket}}*{idx}", "top", "usd2", agg="none"),
            Line("rev_retail", "Retail revenue", "={tx}*{ticket}", "top"),
            Line(
                "accounts",
                "Wholesale accounts",
                "={in:ws_accounts}*{ramp}*(1+{in:ws_g})^({y}-1)",
                "top",
                "dec1",
                agg="last",
                section="Wholesale",
            ),
            Line("order_wk", "Order value per account per week", f"={{in:ws_order}}*{idx}", "top", "usd", agg="none"),
            Line("rev_ws", "Wholesale revenue", "={accounts}*{order_wk}*52/12*{mpp}", "top"),
            Line("rev", "Revenue", "={rev_retail}+{rev_ws}", "top", bold=True, total=True, section="Revenue"),
            Line(
                "ingredients",
                "Ingredients sold",
                "=-({rev_retail}*{in:ingr_pct}+{rev_ws}*{in:ws_ingr_pct})",
                "top",
                section="Cost of sales",
            ),
            Line(
                "waste",
                "Waste (retail production not sold, at ingredient cost)",
                "=-{rev_retail}*{in:ingr_pct}*{in:waste_pct}*100/MAX(1,100-100*{in:waste_pct})",
                "top",
            ),
            Line("packaging", "Packaging", "=-{rev}*{in:pack_pct}", "top"),
            Line("cogs", "Cost of sales", "={ingredients}+{waste}+{packaging}", "top", bold=True),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "payroll",
                "Payroll (bakers, counter, manager)",
                "={payroll_total}",
                "top",
                section="Operating expenses",
            ),
            Line("rent", "Rent", "=-{in:rent}*{mpp}", "top"),
            Line("utilities", "Utilities (ovens)", "=-{in:utilities}*{mpp}", "top"),
            Line(
                "deliv",
                "Wholesale delivery",
                "=-{accounts}*{in:ws_deliv_wk}*52/12*{mpp}*{in:cost_drop}",
                "top",
            ),
            Line("maint", "Equipment repairs & cleaning", "=-{in:maint}*{mpp}", "top"),
            Line("mkt", "Marketing", "=-{rev}*{in:mkt_pct}", "top"),
            Line("card_fees", "Card processing fees", "=-{rev_retail}*{in:card_pct}", "top"),
            Line("ga_other", "Insurance, licences & other G&A", "=-{in:ga_other}*{mpp}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "capex",
                "Capital spending (fit-out, ovens, mixers, display cases)",
                "=IF({p}=1,{in:capex},0)+IF({y}>1,{in:capex_repl}*{mpp}/12,0)",
                "top",
                section="Capital spending",
            )
        ]

    # ------------------------------------------------------------------ Dashboard and KPI table
    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("rev_retail", "Retail counter revenue", "kpi:rev_retail", "usdk"),
            DashMetric("rev_ws", "Wholesale revenue", "kpi:rev_ws", "usdk"),
            DashMetric("cust_day", "Customers per day (average)", "kpi:cust_day", "int"),
            DashMetric("accounts", "Wholesale accounts", "kpi:accounts_end", "dec1"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Retail and wholesale revenue", bars=("rev_retail", "rev_ws"), stacked=True)

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("days", "Opening days in the year", "line", "days", "dec1"),
            StmtRow("tx", "Retail transactions", "line", "tx", "int", bold=True),
            StmtRow("cust_day", "Customers per day (average)", "formula", "=IF({days}=0,0,{tx}/{days})", "int"),
            StmtRow("ticket", "Average ticket", "formula", "=IF({tx}=0,0,{rev_retail}/{tx})", "usd2"),
            StmtRow(
                "accounts_end", "Wholesale accounts (year end; annual model: year average)", "line", "accounts", "dec1"
            ),
            StmtRow("rev", "Revenue", "line", "rev", bold=True),
            StmtRow("rev_retail", "Retail counter revenue", "line", "rev_retail"),
            StmtRow("rev_ws", "Wholesale revenue", "line", "rev_ws"),
            StmtRow("ws_share", "Wholesale share of revenue", "formula", "=IF({rev}=0,0,{rev_ws}/{rev})", "pct"),
            StmtRow("rev_day", "Retail revenue per opening day", "formula", "=IF({days}=0,0,{rev_retail}/{days})"),
            StmtRow("waste_k", "Waste cost (unsold retail production)", "line", "waste", neg=True),
            StmtRow(
                "waste_share",
                "Waste cost, % of retail revenue",
                "formula",
                "=IF({rev_retail}=0,0,{waste_k}/{rev_retail})",
                "pct",
            ),
            StmtRow("deliv_k", "Wholesale delivery cost", "line", "deliv", neg=True),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("cogs_k", "Cost of sales", "line", "cogs", neg=True),
            StmtRow("pay_k", "Payroll", "line", "payroll", neg=True),
            StmtRow(
                "prime",
                "Prime cost (cost of sales + payroll) % of revenue",
                "formula",
                "=IF({rev}=0,0,({cogs_k}+{pay_k})/{rev})",
                "pct",
            ),
            StmtRow("ebitda", "EBITDA", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
        ]

    def kpi_charts(self, t: Timing) -> list[KpiChart]:
        return [
            KpiChart("Retail transactions and average ticket", bars=("tx",), lines=("ticket",)),
            KpiChart("Waste and delivery cost, with prime cost %", bars=("waste_k", "deliv_k"), lines=("prime",)),
        ]

    def kpi_reference(self, ann: dict, d: dict, t: Timing) -> dict:
        out: dict[str, dict] = {k: {} for k in self.kpi_derived}
        for y in range(1, t.years + 1):
            rev, rev_retail = ann["rev"][y], ann["rev_retail"][y]
            cogs, payroll = -ann["cogs"][y], -ann["opex_payroll"][y]
            out["cust_day"][y] = div(ann["tx"][y], ann["days"][y])
            out["ticket"][y] = div(rev_retail, ann["tx"][y])
            out["ws_share"][y] = div(ann["rev_ws"][y], rev)
            out["rev_day"][y] = div(rev_retail, ann["days"][y])
            out["waste_share"][y] = div(ann["waste"][y], rev_retail)
            out["gm"][y] = div(ann["gp"][y], rev)
            out["cogs_k"][y] = cogs
            out["pay_k"][y] = payroll
            out["prime"][y] = div(cogs + payroll, rev)
            out["em"][y] = div(ann["ebitda"][y], rev)
        return out

    # ------------------------------------------------------------------ python twin
    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        a, r = d["open_pct"], max(1, d["ramp_months"])
        if t.granularity == "monthly":
            ramp = min(1, a + (1 - a) * (p - 1) / r)
        else:
            ramp = sum(min(1, a + (1 - a) * (12 * (y - 1) + k) / r) for k in range(12)) / 12
        season = _season(p, t, d["peak_uplift"])
        cust = d["cust_full"] * (1 + d["traffic_g"]) ** (y - 1) * max(0.0, ramp + season - 1)
        days = d["open_days"] * 52 / 12 * t.mpp
        tx = cust * days
        idx = (1 + d["price_g"]) ** (y - 1)
        rev_retail = tx * d["ticket"] * idx
        accounts = d["ws_accounts"] * ramp * (1 + d["ws_g"]) ** (y - 1)
        rev_ws = accounts * d["ws_order"] * idx * 52 / 12 * t.mpp
        rev = rev_retail + rev_ws
        ingredients = -(rev_retail * d["ingr_pct"] + rev_ws * d["ws_ingr_pct"])
        waste = -rev_retail * d["ingr_pct"] * d["waste_pct"] * 100 / max(1, 100 - 100 * d["waste_pct"])
        deliv = -accounts * d["ws_deliv_wk"] * 52 / 12 * t.mpp * d["cost_drop"]
        return Top(
            rev=rev,
            cogs=ingredients + waste - rev * d["pack_pct"],
            opex={
                "payroll": hc.payroll,
                "rent": -d["rent"] * t.mpp,
                "utilities": -d["utilities"] * t.mpp,
                "deliv": deliv,
                "maint": -d["maint"] * t.mpp,
                "mkt": -rev * d["mkt_pct"],
                "card_fees": -rev_retail * d["card_pct"],
                "ga_other": -d["ga_other"] * t.mpp,
            },
            capex=(d["capex"] if p == 1 else 0.0) + (d["capex_repl"] * t.mpp / 12 if y > 1 else 0.0),
            kpis={
                "days": days,
                "tx": tx,
                "rev_retail": rev_retail,
                "rev_ws": rev_ws,
                "accounts": accounts,
                "waste": -waste,
                "deliv": -deliv,
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
                "model_name": f"Bakery financial model ({stage})",
                "template": self.key,
                "business_type": "bakery",
                "stage": stage,
                "assumption_note": "Illustrative assumptions — replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
