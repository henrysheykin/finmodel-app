"""SaaS / software template: customers by channel → MRR waterfall → revenue.

Monthly columns roll customers and MRR month by month. Annual columns use the
same monthly rates compounded over the year, with customers won during the
year treated as joining mid-year (they experience six months of churn and
expansion). Assumption memo: docs/templates/saas.md.
"""

from __future__ import annotations

from engine.brief import Brief
from engine.core import HC, Top
from engine.spec import DashChart, DashMetric, DriverSpec, KpiChart, Line, StmtRow, Timing
from engine.templates.base import Template, div

ROLES = [
    ("eng", "Engineering & product"),
    ("gtm", "Sales & marketing"),
    ("cs", "Customer success"),
    ("ga", "G&A (finance, ops)"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer
# replaces them with their own numbers; the assumption memo says so.
_COMMON = {
    "price_g": (0.0, 0.03, 0.05),
    "expansion_m": (0.0, 0.005, 0.01),
    "organic_g": (0.1, 0.3, 0.5),
    "mkt_g": (0.2, 0.2, 0.2),
    "annual_pct": (0.2, 0.2, 0.2),
    "hosting_pct": (0.12, 0.10, 0.08),
    "support_cost": (3.0, 2.0, 1.5),
    "tools_per_fte": (150, 150, 150),
    "payroll_tax": (0.2, 0.2, 0.2),
    "wage_g": (0.04, 0.04, 0.04),
    "loan_rate": (0.0, 0.0, 0.0),
    "loan_term_years": (1, 1, 1),
    "ar_days": (5, 5, 5),
    "inv_days": (0, 0, 0),
    "ap_days": (30, 30, 30),
    "dep_years": (3, 3, 3),
    "tax_rate": (0.21, 0.21, 0.21),
    "loan_amount": (0, 0, 0),
}
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "start_customers": (0, 0, 0),
            "arpa": (59, 79, 99),
            "churn_m": (0.05, 0.035, 0.025),
            "organic_new": (3, 5, 8),
            "mkt_budget": (3000, 3000, 3000),
            "cac": (500, 400, 300),
            "office": (0, 0, 0),
            "ga_other": (1500, 1500, 1500),
            "capex": (10000, 10000, 10000),
            "equity": (500000, 500000, 500000),
        },
        "hire_g": {"eng": 0.5, "gtm": 1.0, "cs": 1.0, "ga": 0.0},
        "roles": {
            "eng": ((2, 2, 2), (120000, 120000, 120000), 1),
            "gtm": ((1, 1, 1), (90000, 90000, 90000), 4),
            "cs": ((0.5, 0.5, 0.5), (60000, 60000, 60000), 7),
            "ga": ((0.5, 0.5, 0.5), (75000, 75000, 75000), 1),
        },
    },
    "early": {
        "drivers": {
            "start_customers": (30, 30, 30),
            "arpa": (79, 99, 119),
            "churn_m": (0.045, 0.03, 0.02),
            "organic_new": (8, 12, 18),
            "mkt_budget": (8000, 8000, 8000),
            "cac": (600, 450, 350),
            "office": (1500, 1500, 1500),
            "ga_other": (3000, 3000, 3000),
            "capex": (20000, 20000, 20000),
            "equity": (3000000, 3000000, 3000000),
        },
        "hire_g": {"eng": 0.5, "gtm": 0.5, "cs": 0.5, "ga": 0.5},
        "roles": {
            "eng": ((3, 3, 3), (125000, 125000, 125000), 1),
            "gtm": ((1.5, 1.5, 1.5), (95000, 95000, 95000), 1),
            "cs": ((1, 1, 1), (60000, 60000, 60000), 1),
            "ga": ((0.5, 0.5, 0.5), (80000, 80000, 80000), 1),
        },
    },
    "growing": {
        "drivers": {
            "start_customers": (300, 300, 300),
            "arpa": (99, 129, 149),
            "churn_m": (0.03, 0.02, 0.015),
            "organic_new": (20, 30, 45),
            "mkt_budget": (30000, 30000, 30000),
            "cac": (900, 700, 550),
            "office": (6000, 6000, 6000),
            "ga_other": (8000, 8000, 8000),
            "capex": (60000, 60000, 60000),
            "equity": (3000000, 3000000, 3000000),
        },
        "hire_g": {"eng": 0.4, "gtm": 0.4, "cs": 0.4, "ga": 0.3},
        "roles": {
            "eng": ((6, 6, 6), (130000, 130000, 130000), 1),
            "gtm": ((3, 3, 3), (100000, 100000, 100000), 1),
            "cs": ((2, 2, 2), (65000, 65000, 65000), 1),
            "ga": ((1, 1, 1), (85000, 85000, 85000), 1),
        },
    },
    "established": {
        "drivers": {
            "start_customers": (3000, 3000, 3000),
            "arpa": (230, 250, 270),
            "churn_m": (0.02, 0.015, 0.01),
            "organic_new": (30, 40, 50),
            "mkt_budget": (60000, 60000, 60000),
            "cac": (1200, 1000, 800),
            "office": (20000, 20000, 20000),
            "ga_other": (25000, 25000, 25000),
            "capex": (150000, 150000, 150000),
            "equity": (1000000, 1000000, 1000000),
        },
        "hire_g": {"eng": 0.2, "gtm": 0.2, "cs": 0.2, "ga": 0.15},
        "roles": {
            "eng": ((20, 20, 20), (135000, 135000, 135000), 1),
            "gtm": ((14, 14, 14), (105000, 105000, 105000), 1),
            "cs": ((8, 8, 8), (65000, 65000, 65000), 1),
            "ga": ((6, 6, 6), (90000, 90000, 90000), 1),
        },
    },
}


class SaasTemplate(Template):
    key = "saas"
    title = "SaaS / software"
    business_types = ("saas",)
    order = 10
    key_numbers = ("start_customers", "arpa", "churn_m", "organic_new", "mkt_budget", "cac", "equity")
    sample_title = "SaaS startup"
    sample_desc = "Full workbook with MRR, churn, CAC payback and runway"
    sample_stage = "early"
    kpi_title = "SaaS metrics"
    kpi_checked = {
        "cust_end": "cust_close",
        "mrr_end": "mrr_close",
        "new_cust": "new_total",
        "lost": "churned",
        "rev": "rev",
        "gp": "gp",
        "cash": "cash_close",
    }
    kpi_derived = ("arr", "arpa", "gm", "cac", "ltv", "ltv_cac", "payback")
    kpi_flows = ("new_total", "churned")

    def driver_specs(self) -> list[DriverSpec]:
        return [
            DriverSpec("start_customers", "Paying customers at start", "#", "int", 0, 1e6, "asc"),
            DriverSpec("arpa", "Average MRR per new customer (ARPA)", "$ / month", "usd", 0, 1e5, "asc"),
            DriverSpec("price_g", "Price increase per year for new customers", "%", "pct", -0.5, 1, "asc"),
            DriverSpec("churn_m", "Customer churn per month", "%", "pct", 0, 0.5, "desc"),
            DriverSpec("expansion_m", "Expansion MRR per month, % of opening MRR", "%", "pct", 0, 0.2, "asc"),
            DriverSpec(
                "organic_new", "Organic / referral new customers per month (year 1)", "# / month", "dec1", 0, 1e5, "asc"
            ),
            DriverSpec("organic_g", "Growth of organic new customers per year", "%", "pct", -0.9, 5, "asc"),
            DriverSpec("mkt_budget", "Paid marketing budget per month (year 1)", "$ / month", "usd", 0, 1e8),
            DriverSpec("mkt_g", "Paid marketing budget growth per year", "%", "pct", -0.9, 5),
            DriverSpec("cac", "Paid customer acquisition cost (CAC)", "$", "usd", 1, 1e6, "desc"),
            DriverSpec("annual_pct", "Share of MRR billed annually in advance", "%", "pct", 0, 1),
            DriverSpec("hosting_pct", "Hosting & payment fees, % of revenue", "%", "pct", 0, 1, "desc"),
            DriverSpec("support_cost", "Support & onboarding cost per customer per month", "$", "usd2", 0, 1e4, "desc"),
            DriverSpec("tools_per_fte", "Software & tools per FTE per month", "$", "usd", 0, 1e4),
            DriverSpec("office", "Office & rent per month", "$", "usd", 0, 1e7),
            DriverSpec("ga_other", "Other G&A per month (legal, accounting, insurance)", "$", "usd", 0, 1e7),
            DriverSpec("capex", "Start-up capex (equipment)", "$", "usd", 0, 1e8),
        ]

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        if t.granularity == "monthly":
            cust_close = "={cust_open}+{new_total}+{churned}"
            churned = "=-{cust_open}*{in:churn_m}"
            mrr = [
                Line(
                    "mrr_open",
                    "Opening MRR",
                    "={mrr_close[-1]}",
                    "top",
                    first="={in:start_customers}*{in:arpa}",
                    agg="first",
                    section="MRR waterfall",
                ),
                Line("mrr_new", "New MRR", "={new_total}*{arpa_new}", "top"),
                Line("mrr_exp", "Expansion MRR", "={mrr_open}*{in:expansion_m}", "top"),
                Line("mrr_churn", "Churned MRR", "=-{mrr_open}*{in:churn_m}", "top"),
                Line(
                    "mrr_close",
                    "Closing MRR",
                    "={mrr_open}+{mrr_new}+{mrr_exp}+{mrr_churn}",
                    "top",
                    agg="last",
                    bold=True,
                    total=True,
                ),
            ]
        else:
            # monthly rates compounded over 12 months; customers won in the year join mid-year
            cust_close = "={cust_open}*(1-{in:churn_m})^12+{new_total}*(1-{in:churn_m})^6"
            churned = "={cust_close}-{cust_open}-{new_total}"
            mrr = [
                Line(
                    "mrr_open",
                    "Opening MRR",
                    "={mrr_close[-1]}",
                    "top",
                    first="={in:start_customers}*{in:arpa}",
                    agg="first",
                    section="MRR waterfall",
                ),
                Line("mrr_new", "New MRR (at signing)", "={new_total}*{arpa_new}", "top"),
                Line("mrr_net", "Expansion less churn over the year", "={mrr_close}-{mrr_open}-{mrr_new}", "top"),
                Line(
                    "mrr_close",
                    "Closing MRR",
                    "={mrr_open}*(1-{in:churn_m}+{in:expansion_m})^12+{mrr_new}*(1-{in:churn_m}+{in:expansion_m})^6",
                    "top",
                    agg="last",
                    bold=True,
                    total=True,
                ),
            ]
        return [
            Line(
                "new_organic",
                "New customers — organic / referral",
                "={in:organic_new}*(1+{in:organic_g})^({y}-1)*{mpp}",
                "top",
                "dec1",
                section="Customers",
            ),
            Line("new_paid", "New customers — paid marketing", "=-{mkt}/MAX(1,{in:cac})", "top", "dec1"),
            Line("new_total", "New customers — total", "={new_organic}+{new_paid}", "top", "dec1", bold=True),
            Line(
                "cust_open",
                "Customers — opening",
                "={cust_close[-1]}",
                "top",
                "dec1",
                first="={in:start_customers}",
                agg="first",
            ),
            Line("churned", "Customers lost (churn)", churned, "top", "dec1"),
            Line("cust_close", "Customers — closing", cust_close, "top", "dec1", agg="last", bold=True, total=True),
            Line("arpa_new", "MRR per new customer", "={in:arpa}*(1+{in:price_g})^({y}-1)", "top", "usd2", agg="none"),
            *mrr,
            Line(
                "rev",
                "Revenue (average MRR × months)",
                "=({mrr_open}+{mrr_close})/2*{mpp}",
                "top",
                bold=True,
                total=True,
                section="Revenue & cost of revenue",
            ),
            Line(
                "cogs",
                "Hosting, payment fees & support",
                "=-({rev}*{in:hosting_pct}+({cust_open}+{cust_close})/2*{in:support_cost}*{mpp})",
                "top",
            ),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        return [
            Line("payroll", "Payroll", "={payroll_total}", "top", section="Operating expenses"),
            Line("mkt", "Paid marketing", "=-{in:mkt_budget}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
            Line("tools", "Software & tools", "=-{fte_total}*{in:tools_per_fte}*{mpp}", "top"),
            Line("office", "Office & rent", "=-{in:office}*{mpp}", "top"),
            Line("ga_other", "Other G&A", "=-{in:ga_other}*{mpp}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [Line("capex", "Capital spending", "=IF({p}=1,{in:capex},0)", "top")]

    def liability_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "defrev",
                "Deferred revenue (annual plans, ~6 months unearned)",
                "={mrr_close}*{in:annual_pct}*6",
                "top",
                agg="last",
            )
        ]

    def extra_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "burn_m",
                "Net burn per month (operating + investing; negative = cash generative)",
                "=-({cfo}+{cfi})/{mpp}",
                "top",
                agg="last",
                section="SaaS metric helpers",
            ),
            Line("churn_rate", "Customer churn per month", "={in:churn_m}", "top", "pct", agg="last"),
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("cust", "Paying customers (year end)", "kpi:cust_end", "int"),
            DashMetric("arr", "ARR (year-end MRR × 12)", "kpi:arr", "usdk"),
            DashMetric("ltv_cac", "LTV ÷ CAC", "kpi:ltv_cac", "x"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("ARR & paying customers", bars=("arr",), lines=("cust",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("cust_end", "Customers (year end)", "line", "cust_close", "dec1", bold=True),
            StmtRow("new_cust", "New customers in the year", "line", "new_total", "dec1"),
            StmtRow("lost", "Customers lost in the year", "line", "churned", "dec1"),
            StmtRow("mrr_end", "MRR (year end)", "line", "mrr_close", bold=True),
            StmtRow("arr", "ARR (year-end MRR × 12)", "formula", "={mrr_end}*12", bold=True),
            StmtRow(
                "arpa", "Average MRR per customer (year end)", "formula", "=IF({cust_end}=0,0,{mrr_end}/{cust_end})"
            ),
            StmtRow("rev", "Revenue", "line", "rev"),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("paid_mkt", "Paid marketing spend", "line", "mkt", neg=True),
            StmtRow(
                "cac",
                "Blended CAC (paid spend ÷ all new customers)",
                "formula",
                "=IF({new_cust}=0,0,{paid_mkt}/{new_cust})",
            ),
            StmtRow("churn", "Customer churn per month", "line", "churn_rate", "pct"),
            StmtRow(
                "ltv",
                "Customer lifetime value (MRR × margin ÷ churn)",
                "formula",
                "=IF({churn}=0,0,{arpa}*{gm}/{churn})",
            ),
            StmtRow("ltv_cac", "LTV ÷ CAC", "formula", "=IF({cac}=0,0,{ltv}/{cac})", "x"),
            StmtRow(
                "payback",
                "CAC payback (months of gross profit)",
                "formula",
                "=IF({arpa}*{gm}<=0,0,{cac}/({arpa}*{gm}))",
                "dec1",
            ),
            StmtRow("burn", "Net burn per month (year end)", "line", "burn_m"),
            StmtRow("cash", "Cash (year end)", "line", "cash_close"),
            StmtRow(
                "runway",
                "Runway at year-end burn (months; - = not burning)",
                "formula",
                "=IF({burn}<=0,0,MAX(0,{cash})/{burn})",
                "dec1",
            ),
        ]

    def kpi_charts(self, t: Timing) -> list[KpiChart]:
        return [
            KpiChart("LTV ÷ CAC and CAC payback", bars=("ltv_cac",), lines=("payback",)),
            KpiChart("New customers and customers lost", bars=("new_cust", "lost")),
        ]

    # ------------------------------------------------------------------ python twin
    def kpi_reference(self, ann: dict, d: dict, t: Timing) -> dict:
        out: dict[str, dict] = {k: {} for k in self.kpi_derived}
        for y in range(1, t.years + 1):
            mrr, cust = ann["mrr_close"][y], ann["cust_close"][y]
            arpa = div(mrr, cust)
            gm = div(ann["gp"][y], ann["rev"][y])
            cac = div(-ann["opex_mkt"][y], ann["new_total"][y])
            ltv = div(arpa * gm, d["churn_m"])
            margin = arpa * gm
            out["arr"][y], out["arpa"][y], out["gm"][y], out["cac"][y] = mrr * 12, arpa, gm, cac
            out["ltv"][y], out["ltv_cac"][y] = ltv, div(ltv, cac)
            out["payback"][y] = 0.0 if margin <= 0 else cac / margin
        return out

    def _path(self, d: dict, t: Timing, upto: int) -> list[dict]:
        """Customer and MRR roll-forward for periods 1..upto (plain Python)."""
        out = []
        cust, mrr = d["start_customers"], d["start_customers"] * d["arpa"]
        r, f = 1 - d["churn_m"], 1 - d["churn_m"] + d["expansion_m"]
        for p in range(1, upto + 1):
            y = t.year_of(p)
            mkt = d["mkt_budget"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp
            new = d["organic_new"] * (1 + d["organic_g"]) ** (y - 1) * t.mpp + mkt / max(1, d["cac"])
            arpa_new = d["arpa"] * (1 + d["price_g"]) ** (y - 1)
            c0, m0 = cust, mrr
            if t.granularity == "monthly":
                cust = c0 * r + new
                mrr = m0 * f + new * arpa_new
            else:
                cust = c0 * r**12 + new * r**6
                mrr = m0 * f**12 + new * arpa_new * f**6
            out.append({"c0": c0, "c1": cust, "m0": m0, "m1": mrr, "new": new, "mkt": mkt})
        return out

    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        s = self._path(d, t, p)[-1]
        rev = (s["m0"] + s["m1"]) / 2 * t.mpp
        cogs = -(rev * d["hosting_pct"] + (s["c0"] + s["c1"]) / 2 * d["support_cost"] * t.mpp)
        return Top(
            rev=rev,
            cogs=cogs,
            opex={
                "payroll": hc.payroll,
                "mkt": -s["mkt"],
                "tools": -hc.fte * d["tools_per_fte"] * t.mpp,
                "office": -d["office"] * t.mpp,
                "ga_other": -d["ga_other"] * t.mpp,
            },
            capex=d["capex"] if p == 1 else 0.0,
            liabilities={"defrev": s["m1"] * d["annual_pct"] * 6},
            kpis={
                "cust_close": s["c1"],
                "mrr_close": s["m1"],
                "new_total": s["new"],
                "churned": s["c1"] - s["c0"] - s["new"],
            },
        )

    # ------------------------------------------------------------------ defaults
    def default_brief(self, stage: str = "planning", **opts) -> Brief:
        cfg = _STAGES[stage]
        vals = {**_COMMON, **cfg["drivers"]}
        drivers = [{"key": k, "low": v[0], "base": v[1], "high": v[2]} for k, v in vals.items()]
        roles = []
        for key, title in ROLES:
            fte, sal, start = cfg["roles"][key]
            g = cfg["hire_g"][key]
            roles.append({"key": key, "title": title})
            drivers += [
                {"key": f"{key}_fte", "low": fte[0], "base": fte[1], "high": fte[2]},
                {"key": f"{key}_salary", "low": sal[0], "base": sal[1], "high": sal[2]},
                {"key": f"{key}_start", "low": start, "base": start, "high": start},
                {"key": f"{key}_fte_g", "low": g, "base": g, "high": g},
            ]
        brief = Brief.model_validate(
            {
                "model_name": f"SaaS financial model ({stage})",
                "template": "saas",
                "business_type": "saas",
                "stage": stage,
                "assumption_note": "Illustrative assumptions — replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
