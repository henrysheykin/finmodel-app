"""Fitness studio / gym template: member base (joins − cancellations, capped by capacity) × fees.

Members open with the presale / current base. Each period new members join from marketing (spend ÷ cost
per lead × leads that join) and from referrals & walk-ins; a monthly share cancels; the base never
exceeds the studio's capacity (joins above it are lost). Revenue = membership fees on the average base,
joining fees on new members, personal training and retail & drinks per member. Instructors are paid per
class, trainers a share of personal-training revenue.
Assumption memo: docs/templates/fitness.md.
"""

from __future__ import annotations

from engine.brief import Brief
from engine.core import HC, Top
from engine.spec import DriverSpec, Line, StmtRow, Timing
from engine.templates.base import Template

ROLES = [
    ("manager", "Studio manager"),
    ("desk", "Front desk & sales"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer replaces
# them with their own numbers; the assumption memo says so.
_COMMON = {
    "conv": (0.11, 0.12, 0.13),
    "cpl": (28, 25, 22),
    "fee_g": (0.02, 0.03, 0.04),
    "join_fee": (49, 49, 49),
    "pt_share": (0.07, 0.08, 0.09),
    "pt_sessions": (4, 4, 4),
    "pt_rate": (55, 60, 65),
    "pt_payout": (0.55, 0.5, 0.45),
    "retail_pm": (4, 5, 6),
    "retail_cogs": (0.55, 0.5, 0.45),
    "class_cost": (50, 45, 40),
    "fees_pct": (0.045, 0.04, 0.035),
    "payroll_tax": (0.1, 0.1, 0.1),
    "wage_g": (0.03, 0.03, 0.03),
    "ar_days": (0, 0, 0),
    "inv_days": (10, 10, 10),
    "ap_days": (20, 20, 20),
    "dep_years": (7, 7, 7),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "members_start": (80, 120, 160),
            "max_members": (450, 450, 450),
            "ref_new": (12, 15, 18),
            "ref_g": (0.05, 0.1, 0.15),
            "mkt": (4000, 4000, 4000),
            "mkt_g": (0.0, 0.05, 0.1),
            "churn_m": (0.07, 0.06, 0.05),
            "fee": (89, 99, 109),
            "classes_wk": (40, 40, 40),
            "rent": (12000, 12000, 12000),
            "utilities": (2200, 2200, 2200),
            "maint": (1800, 1800, 1800),
            "ga_other": (2000, 2000, 2000),
            "sqft": (4000, 4000, 4000),
            "capex": (250000, 250000, 250000),
            "equity": (330000, 330000, 330000),
            "loan_amount": (150000, 150000, 150000),
            "loan_rate": (0.08, 0.08, 0.08),
            "loan_term_years": (7, 7, 7),
        },
        "roles": {"manager": (1, 55000, 1, 0.0), "desk": (3, 32000, 1, 0.0)},
    },
    "early": {
        "drivers": {
            "members_start": (260, 300, 340),
            "max_members": (550, 550, 550),
            "ref_new": (18, 22, 26),
            "ref_g": (0.05, 0.1, 0.15),
            "mkt": (4500, 4500, 4500),
            "mkt_g": (0.0, 0.05, 0.1),
            "churn_m": (0.065, 0.055, 0.045),
            "fee": (89, 99, 109),
            "classes_wk": (45, 45, 45),
            "rent": (14000, 14000, 14000),
            "utilities": (2600, 2600, 2600),
            "maint": (2000, 2000, 2000),
            "ga_other": (2400, 2400, 2400),
            "sqft": (5000, 5000, 5000),
            "capex": (20000, 20000, 20000),
            "equity": (120000, 120000, 120000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {"manager": (1.5, 58000, 1, 0.0), "desk": (3.5, 33000, 1, 0.0)},
    },
    "growing": {
        "drivers": {
            "members_start": (650, 700, 750),
            "max_members": (1200, 1200, 1200),
            "ref_new": (35, 40, 45),
            "ref_g": (0.05, 0.08, 0.11),
            "mkt": (8000, 8000, 8000),
            "mkt_g": (0.03, 0.06, 0.09),
            "churn_m": (0.06, 0.05, 0.04),
            "fee": (79, 89, 99),
            "classes_wk": (80, 80, 80),
            "rent": (26000, 26000, 26000),
            "utilities": (5500, 5500, 5500),
            "maint": (4000, 4000, 4000),
            "ga_other": (4500, 4500, 4500),
            "sqft": (10000, 10000, 10000),
            "capex": (80000, 80000, 80000),
            "equity": (150000, 150000, 150000),
            "loan_amount": (100000, 100000, 100000),
            "loan_rate": (0.08, 0.08, 0.08),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {"manager": (3, 60000, 1, 0.0), "desk": (7, 34000, 1, 0.03)},
    },
    "established": {
        "drivers": {
            "members_start": (1500, 1600, 1700),
            "max_members": (2000, 2000, 2000),
            "ref_new": (60, 70, 80),
            "ref_g": (0.02, 0.04, 0.06),
            "mkt": (12000, 12000, 12000),
            "mkt_g": (0.02, 0.04, 0.06),
            "churn_m": (0.055, 0.045, 0.04),
            "fee": (79, 89, 99),
            "classes_wk": (120, 120, 120),
            "rent": (42000, 42000, 42000),
            "utilities": (9500, 9500, 9500),
            "maint": (6500, 6500, 6500),
            "ga_other": (7500, 7500, 7500),
            "sqft": (20000, 20000, 20000),
            "capex": (60000, 60000, 60000),
            "equity": (100000, 100000, 100000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {"manager": (4, 62000, 1, 0.0), "desk": (12, 35000, 1, 0.03)},
    },
}


class FitnessTemplate(Template):
    key = "fitness"
    title = "Fitness studio / gym"
    business_types = ("fitness",)
    order = 60
    key_numbers = ("members_start", "fee", "churn_m", "mkt", "max_members", "rent", "equity")
    sample_title = "Fitness studio"
    sample_desc = "Full workbook with members, cancellations, capacity, personal training and rent"
    sample_stage = "planning"
    kpi_title = "Membership metrics"
    kpi_checked = {"members_end": "members_close", "new_m": "new_total", "lost_cap": "capped"}
    kpi_flows = ("new_total", "capped")

    def driver_specs(self) -> list[DriverSpec]:
        mem, price, extra, cost = "Members", "Prices", "Personal training & retail", "Costs"
        return [
            DriverSpec("members_start", "Members at start (presale or current base)", "#", "int", 0, 1e6, "asc", mem),
            DriverSpec("max_members", "Capacity: most members the studio can hold", "#", "int", 1, 1e6, section=mem),
            DriverSpec("ref_new", "Referral & walk-in joins per month (year 1)", "#", "dec1", 0, 1e5, "asc", mem),
            DriverSpec("ref_g", "Referral & walk-in joins growth per year", "%", "pct", -0.9, 5, "asc", mem),
            DriverSpec("mkt", "Marketing budget per month (year 1)", "$", "usd", 0, 1e7, section=mem),
            DriverSpec("mkt_g", "Marketing budget growth per year", "%", "pct", -0.9, 5, "asc", mem),
            DriverSpec("cpl", "Cost per lead", "$", "usd2", 0, 1e5, "desc", mem),
            DriverSpec("conv", "Leads that join", "%", "pct", 0, 1, "asc", mem),
            DriverSpec("churn_m", "Members who cancel per month", "%", "pct", 0, 1, "desc", mem),
            DriverSpec("fee", "Membership fee per month (year 1)", "$", "usd2", 0, 1e5, "asc", price),
            DriverSpec("fee_g", "Price increase per year", "%", "pct", -0.5, 1, "asc", price),
            DriverSpec("join_fee", "Joining fee per new member", "$", "usd2", 0, 1e5, "asc", price),
            DriverSpec("pt_share", "Members buying personal training", "%", "pct", 0, 1, "asc", extra),
            DriverSpec(
                "pt_sessions", "Sessions per personal-training client per month", "#", "dec1", 0, 100, "asc", extra
            ),
            DriverSpec("pt_rate", "Price per personal-training session", "$", "usd2", 0, 1e4, "asc", extra),
            DriverSpec("pt_payout", "Trainer payout, % of personal-training revenue", "%", "pct", 0, 1, "desc", extra),
            DriverSpec("retail_pm", "Retail & drinks sales per member per month", "$", "usd2", 0, 1e4, "asc", extra),
            DriverSpec("retail_cogs", "Retail & drinks cost, % of sales", "%", "pct", 0, 1, "desc", extra),
            DriverSpec("classes_wk", "Group classes per week", "#", "dec1", 0, 1e4, section=cost),
            DriverSpec("class_cost", "Instructor cost per class (year 1)", "$", "usd2", 0, 1e5, "desc", cost),
            DriverSpec("rent", "Rent per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("utilities", "Utilities per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("maint", "Equipment maintenance & cleaning per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("fees_pct", "Booking software & payment fees, % of revenue", "%", "pct", 0, 0.3, "desc", cost),
            DriverSpec("ga_other", "Insurance & other G&A per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("sqft", "Studio size", "sq ft", "int", 1, 1e7, section=cost),
            DriverSpec("capex", "Fit-out & equipment (month 1)", "$", "usd", 0, 1e8, section=cost),
        ]

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        if t.granularity == "monthly":
            uncapped = "={members_open}*(1-{in:churn_m})+{new_total}"
            churned = "=-{members_open}*{in:churn_m}"
        else:
            # monthly cancellation rate compounded over 12 months; members who join in the year join mid-year
            uncapped = "={members_open}*(1-{in:churn_m})^12+{new_total}*(1-{in:churn_m})^6"
            churned = "={uncapped}-{members_open}-{new_total}"
        idx = "(1+{in:fee_g})^({y}-1)"
        return [
            Line(
                "new_mkt",
                "New members from marketing",
                "=-{mkt}/MAX(1,{in:cpl})*{in:conv}",
                "top",
                "dec1",
                section="Members",
            ),
            Line(
                "new_ref",
                "New members from referrals & walk-ins",
                "={in:ref_new}*(1+{in:ref_g})^({y}-1)*{mpp}",
                "top",
                "dec1",
            ),
            Line("new_total", "New members — total", "={new_mkt}+{new_ref}", "top", "dec1", bold=True),
            Line(
                "members_open",
                "Members — opening",
                "={members_close[-1]}",
                "top",
                "dec1",
                first="={in:members_start}",
                agg="first",
            ),
            Line("churned", "Members who cancelled", churned, "top", "dec1"),
            Line("uncapped", "Helper: members before the capacity limit", uncapped, "top", "dec1", agg="none"),
            Line(
                "members_close",
                "Members — closing",
                "=MIN({in:max_members},{uncapped})",
                "top",
                "dec1",
                agg="last",
                bold=True,
            ),
            Line("capped", "Joins lost to the capacity limit", "={uncapped}-{members_close}", "top", "dec1"),
            Line("members_avg", "Members — average", "=({members_open}+{members_close})/2", "top", "dec1", agg="none"),
            Line(
                "fee_now",
                "Membership fee per month",
                f"={{in:fee}}*{idx}",
                "top",
                "usd2",
                agg="last",
                section="Revenue",
            ),
            Line("rev_mem", "Membership fees", "={members_avg}*{fee_now}*{mpp}", "top"),
            Line("rev_join", "Joining fees", f"=({{new_total}}-{{capped}})*{{in:join_fee}}*{idx}", "top"),
            Line(
                "rev_pt",
                "Personal training",
                f"={{members_avg}}*{{in:pt_share}}*{{in:pt_sessions}}*{{in:pt_rate}}*{idx}*{{mpp}}",
                "top",
            ),
            Line("rev_retail", "Retail & drinks", f"={{members_avg}}*{{in:retail_pm}}*{idx}*{{mpp}}", "top"),
            Line("rev", "Revenue", "={rev_mem}+{rev_join}+{rev_pt}+{rev_retail}", "top", bold=True, total=True),
            Line(
                "instructors",
                "Group-class instructors",
                "=-{in:classes_wk}*52/12*{in:class_cost}*(1+{in:wage_g})^({y}-1)*{mpp}",
                "top",
                section="Cost of sales",
            ),
            Line("pt_cost", "Trainer payouts", "=-{rev_pt}*{in:pt_payout}", "top"),
            Line("retail_cost", "Retail & drinks cost", "=-{rev_retail}*{in:retail_cogs}", "top"),
            Line("cogs", "Cost of sales", "={instructors}+{pt_cost}+{retail_cost}", "top", bold=True),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        return [
            Line("payroll", "Staff payroll", "={payroll_total}", "top", section="Operating expenses"),
            Line("mkt", "Marketing", "=-{in:mkt}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
            Line("rent", "Rent", "=-{in:rent}*{mpp}", "top"),
            Line("utilities", "Utilities", "=-{in:utilities}*{mpp}", "top"),
            Line("maint", "Equipment maintenance & cleaning", "=-{in:maint}*{mpp}", "top"),
            Line("fees", "Booking software & payment fees", "=-{rev}*{in:fees_pct}", "top"),
            Line("ga_other", "Insurance & other G&A", "=-{in:ga_other}*{mpp}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [Line("capex", "Capital spending (fit-out & equipment)", "=IF({p}=1,{in:capex},0)", "top")]

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("members_end", "Members (year end)", "line", "members_close", "dec1", bold=True),
            StmtRow("new_m", "New members in the year", "line", "new_total", "dec1"),
            StmtRow("lost_m", "Members who cancelled in the year", "line", "churned", "dec1"),
            StmtRow("lost_cap", "Joins lost to the capacity limit", "line", "capped", "dec1"),
            StmtRow(
                "cap_use",
                "Capacity used (year-end members ÷ capacity)",
                "formula",
                "=IF({in:max_members}=0,0,{members_end}/{in:max_members})",
                "pct",
            ),
            StmtRow("mrr", "Membership fees per month at year end", "formula", "={members_end}*{fee_m}"),
            StmtRow("fee_m", "Membership fee per month", "line", "fee_now", "usd2"),
            StmtRow("rev", "Revenue", "line", "rev", bold=True),
            StmtRow("rev_mem", "Membership fees", "line", "rev_mem"),
            StmtRow("rev_extra", "Personal training, retail & joining fees", "formula", "={rev}-{rev_mem}"),
            StmtRow("mkt_spend", "Marketing spend", "line", "mkt", neg=True),
            StmtRow("new_paid", "New members from marketing", "line", "new_mkt", "dec1"),
            StmtRow(
                "cac", "Marketing cost per new member", "formula", "=IF({new_paid}=0,0,{mkt_spend}/{new_paid})", "usd2"
            ),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("churn", "Members who cancel per month", "formula", "={in:churn_m}", "pct"),
            StmtRow(
                "ltv",
                "Member lifetime value (fee × gross margin ÷ monthly cancellations)",
                "formula",
                "=IF({churn}=0,0,{fee_m}*{gm}/{churn})",
                "usd2",
            ),
            StmtRow("ebitda", "EBITDA", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
            StmtRow("rev_sqft", "Revenue per square foot", "formula", "=IF({in:sqft}=0,0,{rev}/{in:sqft})", "usd2"),
        ]

    # ------------------------------------------------------------------ python twin
    def _path(self, d: dict, t: Timing, upto: int) -> list[dict]:
        out = []
        members = d["members_start"]
        r = 1 - d["churn_m"]
        for p in range(1, upto + 1):
            y = t.year_of(p)
            mkt = d["mkt"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp
            new_mkt = mkt / max(1, d["cpl"]) * d["conv"]
            new = new_mkt + d["ref_new"] * (1 + d["ref_g"]) ** (y - 1) * t.mpp
            m0 = members
            uncapped = m0 * r + new if t.granularity == "monthly" else m0 * r**12 + new * r**6
            members = min(d["max_members"], uncapped)
            out.append(
                {"m0": m0, "m1": members, "new": new, "new_mkt": new_mkt, "capped": uncapped - members, "mkt": mkt}
            )
        return out

    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        s = self._path(d, t, p)[-1]
        idx = (1 + d["fee_g"]) ** (y - 1)
        avg = (s["m0"] + s["m1"]) / 2
        rev_mem = avg * d["fee"] * idx * t.mpp
        rev_join = (s["new"] - s["capped"]) * d["join_fee"] * idx
        rev_pt = avg * d["pt_share"] * d["pt_sessions"] * d["pt_rate"] * idx * t.mpp
        rev_retail = avg * d["retail_pm"] * idx * t.mpp
        rev = rev_mem + rev_join + rev_pt + rev_retail
        instructors = -d["classes_wk"] * 52 / 12 * d["class_cost"] * (1 + d["wage_g"]) ** (y - 1) * t.mpp
        cogs = instructors - rev_pt * d["pt_payout"] - rev_retail * d["retail_cogs"]
        return Top(
            rev=rev,
            cogs=cogs,
            opex={
                "payroll": hc.payroll,
                "mkt": -s["mkt"],
                "rent": -d["rent"] * t.mpp,
                "utilities": -d["utilities"] * t.mpp,
                "maint": -d["maint"] * t.mpp,
                "fees": -rev * d["fees_pct"],
                "ga_other": -d["ga_other"] * t.mpp,
            },
            capex=d["capex"] if p == 1 else 0.0,
            kpis={"members_close": s["m1"], "new_total": s["new"], "capped": s["capped"]},
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
                "model_name": f"Fitness studio financial model ({stage})",
                "template": self.key,
                "business_type": "fitness",
                "stage": stage,
                "assumption_note": "Illustrative assumptions — replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
