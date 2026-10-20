"""Retail / e-commerce template: an online channel (visits × conversion × AOV plus paid
orders bought at a cost per order) and a store channel (stores × floor area × sales per
sq ft). Either channel can be switched off by setting its volume drivers to zero.
Assumption memo: docs/templates/retail.md.
"""

from __future__ import annotations

from engine.brief import Brief
from engine.core import HC, Top
from engine.spec import DashChart, DashMetric, DriverSpec, Line, StmtRow, Timing
from engine.templates.base import Template

ROLES = [
    ("ops", "Operations & fulfilment"),
    ("mkt", "Marketing & e-commerce"),
    ("store", "Store staff"),
    ("ga", "G&A (finance, admin)"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data.
_COMMON = {
    "aov_g": (0.0, 0.02, 0.04),
    "traffic_g": (0.1, 0.25, 0.4),
    "ad_g": (0.2, 0.2, 0.2),
    "q4_uplift": (0.3, 0.3, 0.3),
    "returns_pct": (0.12, 0.10, 0.08),
    "cogs_pct": (0.45, 0.42, 0.39),
    "fulfil_order": (9.0, 8.0, 7.0),
    "payment_pct": (0.03, 0.03, 0.03),
    "lfl_g": (0.0, 0.02, 0.04),
    "payroll_tax": (0.15, 0.15, 0.15),
    "wage_g": (0.03, 0.03, 0.03),
    "loan_rate": (0.08, 0.08, 0.08),
    "loan_term_years": (5, 5, 5),
    "ar_days": (2, 2, 2),
    "inv_days": (75, 75, 75),
    "ap_days": (30, 30, 30),
    "dep_years": (7, 7, 7),
    "tax_rate": (0.21, 0.21, 0.21),
}
_NO_STORES = {
    "stores": (0, 0, 0),
    "stores_add": (0, 0, 0),
    "sqft": (0, 0, 0),
    "sales_sqft": (0, 0, 0),
    "rent_sqft": (0, 0, 0),
    "store_other": (0, 0, 0),
    "fitout": (0, 0, 0),
}
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "repeat_mult": (0.2, 0.3, 0.4),
            "visits": (4000, 5000, 6500),
            "conv": (0.015, 0.02, 0.025),
            "aov": (55, 65, 75),
            "ad_budget": (4000, 4000, 4000),
            "cpa": (40, 32, 25),
            **_NO_STORES,
            "platform": (500, 500, 500),
            "ga_other": (1500, 1500, 1500),
            "capex": (15000, 15000, 15000),
            "equity": (250000, 250000, 250000),
            "loan_amount": (0, 0, 0),
        },
        "roles": {
            "ops": (1, 50000, 1, 0.5),
            "mkt": (1, 60000, 1, 0.5),
            "store": (0, 0, 1, 0.0),
            "ga": (0.5, 60000, 1, 0.0),
        },
    },
    "early": {
        "drivers": {
            "repeat_mult": (0.3, 0.4, 0.5),
            "visits": (16000, 20000, 25000),
            "conv": (0.018, 0.022, 0.026),
            "aov": (60, 70, 80),
            "ad_budget": (15000, 15000, 15000),
            "cpa": (38, 30, 24),
            **_NO_STORES,
            "platform": (1500, 1500, 1500),
            "ga_other": (3000, 3000, 3000),
            "capex": (30000, 30000, 30000),
            "equity": (600000, 600000, 600000),
            "loan_amount": (100000, 100000, 100000),
        },
        "roles": {
            "ops": (2, 50000, 1, 0.3),
            "mkt": (1.5, 65000, 1, 0.3),
            "store": (0, 0, 1, 0.0),
            "ga": (1, 65000, 1, 0.2),
        },
    },
    "growing": {
        "drivers": {
            "repeat_mult": (0.4, 0.5, 0.6),
            "visits": (65000, 80000, 100000),
            "conv": (0.02, 0.024, 0.028),
            "aov": (65, 75, 85),
            "ad_budget": (50000, 50000, 50000),
            "cpa": (36, 28, 22),
            "stores": (2, 2, 2),
            "stores_add": (1, 1, 1),
            "sqft": (1500, 1500, 1500),
            "sales_sqft": (300, 375, 450),
            "rent_sqft": (40, 40, 40),
            "store_other": (2500, 2500, 2500),
            "fitout": (150000, 150000, 150000),
            "platform": (4000, 4000, 4000),
            "ga_other": (8000, 8000, 8000),
            "capex": (50000, 50000, 50000),
            "equity": (1500000, 1500000, 1500000),
            "loan_amount": (500000, 500000, 500000),
        },
        "roles": {
            "ops": (6, 50000, 1, 0.2),
            "mkt": (4, 70000, 1, 0.2),
            "store": (8, 38000, 1, 0.3),
            "ga": (3, 70000, 1, 0.15),
        },
    },
    "established": {
        "drivers": {
            "repeat_mult": (0.5, 0.6, 0.7),
            "visits": (200000, 250000, 300000),
            "conv": (0.022, 0.026, 0.03),
            "aov": (70, 80, 90),
            "ad_budget": (120000, 120000, 120000),
            "cpa": (34, 27, 21),
            "stores": (8, 8, 8),
            "stores_add": (2, 2, 2),
            "sqft": (2000, 2000, 2000),
            "sales_sqft": (325, 400, 475),
            "rent_sqft": (45, 45, 45),
            "store_other": (3500, 3500, 3500),
            "fitout": (200000, 200000, 200000),
            "platform": (12000, 12000, 12000),
            "ga_other": (25000, 25000, 25000),
            "capex": (100000, 100000, 100000),
            "equity": (1000000, 1000000, 1000000),
            "loan_amount": (2000000, 2000000, 2000000),
        },
        "roles": {
            "ops": (15, 52000, 1, 0.1),
            "mkt": (8, 75000, 1, 0.1),
            "store": (40, 40000, 1, 0.2),
            "ga": (8, 75000, 1, 0.1),
        },
    },
}


class RetailTemplate(Template):
    key = "retail"
    title = "Retail / e-commerce"
    business_types = ("retail_ecommerce",)
    order = 30
    key_numbers = ("visits", "conv", "aov", "ad_budget", "cogs_pct", "stores", "equity")
    sample_title = "Retail and e-commerce"
    sample_desc = "Full workbook with traffic, conversion, inventory and stores"
    sample_stage = "growing"
    kpi_title = "Retail metrics"
    kpi_checked = {"orders": "orders", "stores_end": "stores", "online_sales": "online_sales"}
    kpi_flows = ("orders", "online_sales")

    def driver_specs(self) -> list[DriverSpec]:
        on, st, cost = "Online channel", "Store channel", "Costs"
        return [
            DriverSpec("visits", "Website visits per month (year 1, non-paid)", "# / month", "int", 0, 1e9, "asc", on),
            DriverSpec("traffic_g", "Visit growth per year", "%", "pct", -0.9, 5, "asc", on),
            DriverSpec("conv", "Conversion rate (orders ÷ visits)", "%", "pct", 0, 1, "asc", on),
            DriverSpec("aov", "Average order value (before returns)", "$", "usd2", 0, 1e5, "asc", on),
            DriverSpec("aov_g", "Average order value growth per year", "%", "pct", -0.5, 1, "asc", on),
            DriverSpec(
                "repeat_mult", "Repeat orders per new-customer order (returning customers)", "x", "x", 0, 20, "asc", on
            ),
            DriverSpec("ad_budget", "Paid ads budget per month (year 1)", "$ / month", "usd", 0, 1e8, section=on),
            DriverSpec("ad_g", "Paid ads budget growth per year", "%", "pct", -0.9, 5, section=on),
            DriverSpec("cpa", "Paid cost per order (CAC)", "$", "usd2", 1, 1e5, "desc", on),
            DriverSpec("stores", "Stores open at start", "#", "int", 0, 10000, "asc", st, integer=True),
            DriverSpec(
                "stores_add",
                "New stores opened each year from year 2",
                "# / year",
                "int",
                0,
                1000,
                "asc",
                st,
                integer=True,
            ),
            DriverSpec("sqft", "Selling area per store", "sq ft", "int", 0, 1e6, section=st),
            DriverSpec("sales_sqft", "Sales per sq ft per year (year 1)", "$ / sq ft", "usd", 0, 1e5, "asc", st),
            DriverSpec("lfl_g", "Like-for-like store sales growth per year", "%", "pct", -0.5, 1, "asc", st),
            DriverSpec("rent_sqft", "Store rent per sq ft per year", "$ / sq ft", "usd2", 0, 1e4, section=st),
            DriverSpec("store_other", "Other running cost per store per month", "$", "usd", 0, 1e7, section=st),
            DriverSpec("fitout", "Fit-out capex per new store", "$", "usd", 0, 1e8, section=st),
            DriverSpec(
                "q4_uplift",
                "Seasonality: Nov–Dec sales uplift (annual total unchanged)",
                "%",
                "pct",
                0,
                1,
                section=cost,
            ),
            DriverSpec("returns_pct", "Returns & refunds, % of gross sales", "%", "pct", 0, 0.9, "desc", cost),
            DriverSpec("cogs_pct", "Product cost, % of net sales", "%", "pct", 0, 1, "desc", cost),
            DriverSpec("fulfil_order", "Fulfilment & shipping per online order", "$", "usd2", 0, 1e4, "desc", cost),
            DriverSpec("payment_pct", "Payment processing, % of net sales", "%", "pct", 0, 0.2, section=cost),
            DriverSpec("platform", "E-commerce platform & software per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("ga_other", "Other G&A per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("capex", "Start-up capex (equipment, systems)", "$", "usd", 0, 1e8, section=cost),
        ]

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        season = "=IF(MOD({p}-1,12)>=10,1+{in:q4_uplift},1-{in:q4_uplift}/5)" if t.granularity == "monthly" else "=1"
        return [
            Line(
                "season",
                "Seasonality factor (averages 1.0 over a year)",
                season,
                "top",
                "x",
                agg="none",
                section="Online channel",
            ),
            Line("visits", "Website visits", "={in:visits}*(1+{in:traffic_g})^({y}-1)*{mpp}*{season}", "top", "int"),
            Line("orders_organic", "Orders from visits", "={visits}*{in:conv}", "top", "dec1"),
            Line("orders_paid", "Orders from paid ads", "=-{ads}/MAX(1,{in:cpa})", "top", "dec1"),
            Line("orders_new", "Orders from new customers", "={orders_organic}+{orders_paid}", "top", "dec1"),
            Line(
                "orders_repeat",
                "Repeat orders from returning customers",
                "={orders_new}*{in:repeat_mult}",
                "top",
                "dec1",
            ),
            Line("orders", "Online orders", "={orders_new}+{orders_repeat}", "top", "dec1", bold=True),
            Line("aov", "Average order value", "={in:aov}*(1+{in:aov_g})^({y}-1)", "top", "usd2", agg="none"),
            Line("online_sales", "Online gross sales", "={orders}*{aov}", "top", bold=True),
            Line(
                "stores",
                "Stores open",
                "={in:stores}+{in:stores_add}*({y}-1)",
                "top",
                "int",
                agg="last",
                section="Store channel",
            ),
            Line(
                "store_sales",
                "Store gross sales",
                "={stores}*{in:sqft}*{in:sales_sqft}*(1+{in:lfl_g})^({y}-1)/12*{mpp}*{season}",
                "top",
                bold=True,
            ),
            Line(
                "gross_sales",
                "Gross sales",
                "={online_sales}+{store_sales}",
                "top",
                bold=True,
                total=True,
                section="Net sales & product cost",
            ),
            Line("returns", "Returns & refunds", "=-{gross_sales}*{in:returns_pct}", "top"),
            Line("rev", "Net sales", "={gross_sales}+{returns}", "top", bold=True, total=True),
            Line("cogs", "Product cost", "=-{rev}*{in:cogs_pct}", "top"),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "fulfil", "Fulfilment & shipping", "=-{orders}*{in:fulfil_order}", "top", section="Operating expenses"
            ),
            Line("payment", "Payment processing", "=-{rev}*{in:payment_pct}", "top"),
            Line("ads", "Paid ads", "=-{in:ad_budget}*(1+{in:ad_g})^({y}-1)*{mpp}", "top"),
            Line("payroll", "Payroll", "={payroll_total}", "top"),
            Line("store_rent", "Store rent", "=-{stores}*{in:sqft}*{in:rent_sqft}/12*{mpp}", "top"),
            Line("store_other", "Store running costs", "=-{stores}*{in:store_other}*{mpp}", "top"),
            Line("platform", "Platform & software", "=-{in:platform}*{mpp}", "top"),
            Line("ga_other", "Other G&A", "=-{in:ga_other}*{mpp}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "capex",
                "Capital spending (start-up + store fit-outs)",
                "=IF({p}=1,{in:capex}+{in:stores}*{in:fitout},0)"
                "+IF(AND({p}>1,MOD({p}-1,{ppy})=0),{in:stores_add}*{in:fitout},0)",
                "top",
            )
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("online", "Online gross sales", "kpi:online_sales", "usdk"),
            DashMetric("store", "Store gross sales", "kpi:store_sales", "usdk"),
            DashMetric("orders", "Online orders", "kpi:orders", "int"),
            DashMetric("stores", "Stores open (year end)", "kpi:stores_end", "int"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Sales by channel", bars=("online", "store"), stacked=True)

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("visits", "Website visits (non-paid)", "line", "visits", "int"),
            StmtRow("orders", "Online orders", "line", "orders", "int", bold=True),
            StmtRow("repeat", "Repeat orders", "line", "orders_repeat", "int"),
            StmtRow(
                "repeat_share",
                "Repeat orders, % of online orders",
                "formula",
                "=IF({orders}=0,0,{repeat}/{orders})",
                "pct",
            ),
            StmtRow("online_sales", "Online gross sales", "line", "online_sales"),
            StmtRow("aov", "Average order value", "formula", "=IF({orders}=0,0,{online_sales}/{orders})", "usd2"),
            StmtRow("ads", "Paid ads spend", "line", "ads", neg=True),
            StmtRow(
                "ads_pct",
                "Paid ads, % of online gross sales",
                "formula",
                "=IF({online_sales}=0,0,{ads}/{online_sales})",
                "pct",
            ),
            StmtRow("stores_end", "Stores open (year end)", "line", "stores", "int", bold=True),
            StmtRow("store_sales", "Store gross sales", "line", "store_sales"),
            StmtRow("rev", "Net sales", "line", "rev"),
            StmtRow("gp", "Gross profit (after product cost)", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("cogs", "Product cost", "line", "cogs", neg=True),
            StmtRow("inv", "Inventory (year end)", "line", "inv"),
            StmtRow(
                "turns",
                "Inventory turns (product cost ÷ year-end inventory)",
                "formula",
                "=IF({inv}=0,0,{cogs}/{inv})",
                "x",
            ),
        ]

    # ------------------------------------------------------------------ python twin
    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        if t.granularity == "monthly":
            season = 1 + d["q4_uplift"] if (p - 1) % 12 >= 10 else 1 - d["q4_uplift"] / 5
        else:
            season = 1.0
        ads = d["ad_budget"] * (1 + d["ad_g"]) ** (y - 1) * t.mpp
        visits = d["visits"] * (1 + d["traffic_g"]) ** (y - 1) * t.mpp * season
        orders = (visits * d["conv"] + ads / max(1, d["cpa"])) * (1 + d["repeat_mult"])
        online = orders * d["aov"] * (1 + d["aov_g"]) ** (y - 1)
        stores = d["stores"] + d["stores_add"] * (y - 1)
        store_sales = stores * d["sqft"] * d["sales_sqft"] * (1 + d["lfl_g"]) ** (y - 1) / 12 * t.mpp * season
        gross = online + store_sales
        rev = gross * (1 - d["returns_pct"])
        first_of_year = p > 1 and (p - 1) % t.ppy == 0
        capex = (d["capex"] + d["stores"] * d["fitout"] if p == 1 else 0.0) + (
            d["stores_add"] * d["fitout"] if first_of_year else 0.0
        )
        return Top(
            rev=rev,
            cogs=-rev * d["cogs_pct"],
            opex={
                "fulfil": -orders * d["fulfil_order"],
                "payment": -rev * d["payment_pct"],
                "ads": -ads,
                "payroll": hc.payroll,
                "store_rent": -stores * d["sqft"] * d["rent_sqft"] / 12 * t.mpp,
                "store_other": -stores * d["store_other"] * t.mpp,
                "platform": -d["platform"] * t.mpp,
                "ga_other": -d["ga_other"] * t.mpp,
            },
            capex=capex,
            kpis={"orders": orders, "stores": float(stores), "online_sales": online},
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
                "model_name": f"Retail / e-commerce financial model ({stage})",
                "template": "retail",
                "business_type": "retail_ecommerce",
                "stage": stage,
                "assumption_note": "Illustrative assumptions — replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
