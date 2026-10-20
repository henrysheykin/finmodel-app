"""Home services / trades template: demand vs technician capacity → jobs × average ticket + plans.

Plumbing, HVAC, electrical, cleaning, landscaping. Jobs demanded = booked leads (marketing budget ÷
cost per lead × booking rate) + repeat & referral jobs, shaped by a June–August busy season in monthly
models. Jobs completed = the lower of demand and technician capacity (technicians × jobs per day ×
working days), so hiring and marketing both show up in revenue. Maintenance-plan members pay a
monthly fee. Technician payroll, materials, vehicles and plan visits are cost of delivery; a van and
tools are bought for every technician added.
Assumption memo: docs/templates/home_services.md.
"""

from __future__ import annotations

from engine.brief import Brief, BriefError
from engine.core import HC, Top, role_period
from engine.spec import DashChart, DashMetric, DriverSpec, Line, StmtRow, Timing
from engine.templates.base import Template

TECH = "tech"
ROLES = [
    (TECH, "Field technicians"),
    ("office", "Dispatch & office"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer replaces
# them with their own numbers; the assumption memo says so.
_COMMON = {
    "jobs_per_tech": (2.35, 2.5, 2.65),
    "work_days": (21, 21, 21),
    "booking": (0.42, 0.45, 0.48),
    "cpl": (52, 50, 48),
    "peak_uplift": (0.25, 0.25, 0.25),
    "ticket": (415, 440, 465),
    "price_g": (0.02, 0.03, 0.04),
    "plan_fee": (18, 20, 22),
    "plan_cost_pct": (0.42, 0.4, 0.38),
    "materials_pct": (0.26, 0.25, 0.24),
    "vehicle": (1350, 1300, 1250),
    "software": (120, 120, 120),
    "card_fee_pct": (0.029, 0.027, 0.025),
    "capex_tech": (47000, 45000, 43000),
    "payroll_tax": (0.15, 0.15, 0.15),
    "wage_g": (0.03, 0.03, 0.03),
    "ar_days": (10, 10, 10),
    "inv_days": (5, 5, 5),
    "ap_days": (20, 20, 20),
    "dep_years": (5, 5, 5),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "mkt": (2500, 2500, 2500),
            "mkt_g": (0.5, 0.6, 0.7),
            "repeat_jobs": (8, 12, 16),
            "repeat_g": (0.5, 0.6, 0.7),
            "plan_members": (10, 20, 30),
            "plan_g": (0.8, 1.0, 1.2),
            "insurance": (900, 900, 900),
            "rent": (1200, 1200, 1200),
            "ga_other": (600, 600, 600),
            "capex": (15000, 15000, 15000),
            "equipped_start": (0, 0, 0),
            "equity": (120000, 120000, 120000),
            "loan_amount": (60000, 60000, 60000),
            "loan_rate": (0.09, 0.09, 0.09),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {TECH: (1, 55000, 1, 0.5), "office": (0.5, 40000, 4, 0.0)},
    },
    "early": {
        "drivers": {
            "mkt": (4000, 4000, 4000),
            "mkt_g": (0.25, 0.3, 0.35),
            "repeat_jobs": (40, 55, 70),
            "repeat_g": (0.25, 0.3, 0.35),
            "plan_members": (60, 80, 100),
            "plan_g": (0.3, 0.4, 0.5),
            "insurance": (1500, 1500, 1500),
            "rent": (2000, 2000, 2000),
            "ga_other": (1000, 1000, 1000),
            "capex": (10000, 10000, 10000),
            "equipped_start": (2, 2, 2),
            "equity": (120000, 120000, 120000),
            "loan_amount": (80000, 80000, 80000),
            "loan_rate": (0.09, 0.09, 0.09),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {TECH: (2, 58000, 1, 0.25), "office": (1, 42000, 1, 0.0)},
    },
    "growing": {
        "drivers": {
            "mkt": (9000, 9000, 9000),
            "mkt_g": (0.12, 0.15, 0.18),
            "repeat_jobs": (190, 230, 270),
            "repeat_g": (0.12, 0.15, 0.18),
            "plan_members": (300, 400, 500),
            "plan_g": (0.15, 0.2, 0.25),
            "insurance": (3500, 3500, 3500),
            "rent": (4500, 4500, 4500),
            "ga_other": (2500, 2500, 2500),
            "capex": (20000, 20000, 20000),
            "equipped_start": (7, 7, 7),
            "equity": (100000, 100000, 100000),
            "loan_amount": (250000, 250000, 250000),
            "loan_rate": (0.08, 0.08, 0.08),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {TECH: (7, 62000, 1, 0.12), "office": (2, 45000, 1, 0.1)},
    },
    "established": {
        "drivers": {
            "mkt": (20000, 20000, 20000),
            "mkt_g": (0.04, 0.06, 0.08),
            "repeat_jobs": (650, 750, 850),
            "repeat_g": (0.04, 0.06, 0.08),
            "plan_members": (1200, 1500, 1800),
            "plan_g": (0.05, 0.08, 0.1),
            "insurance": (8000, 8000, 8000),
            "rent": (9000, 9000, 9000),
            "ga_other": (6000, 6000, 6000),
            "capex": (0, 0, 0),
            "equipped_start": (20, 20, 20),
            "equity": (50000, 50000, 50000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {TECH: (20, 65000, 1, 0.05), "office": (5, 48000, 1, 0.05)},
    },
}


def _season(p: int, t: Timing, uplift: float) -> float:
    """Busy season June–August: +uplift in those three months, −uplift/3 in the other nine (year unchanged)."""
    if t.granularity != "monthly":
        return 1.0
    m = (p - 1) % 12  # 0 = January
    return 1 + uplift if 5 <= m <= 7 else 1 - uplift / 3


class HomeServicesTemplate(Template):
    key = "home_services"
    title = "Home services / trades"
    business_types = ("home_services",)
    order = 50
    key_numbers = ("ticket", "jobs_per_tech", "mkt", "cpl", "booking", "materials_pct", "equity")
    sample_title = "Home services company"
    sample_desc = "Full workbook with technician capacity, booked jobs, maintenance plans and vans"
    sample_stage = "growing"
    kpi_title = "Home services metrics"
    kpi_checked = {"jobs": "jobs", "tech_fte": "tech_fte", "plan_rev": "rev_plans", "cap_jobs": "cap_jobs"}
    kpi_flows = ("jobs", "rev_plans", "cap_jobs")

    def driver_specs(self) -> list[DriverSpec]:
        cap, dem, price, plans, cost = "Technician capacity", "Demand", "Prices", "Maintenance plans", "Costs"
        return [
            DriverSpec("jobs_per_tech", "Jobs per technician per working day", "jobs", "dec1", 0, 50, "asc", cap),
            DriverSpec("work_days", "Working days per month", "days", "int", 1, 31, section=cap),
            DriverSpec("mkt", "Marketing budget per month", "$", "usd", 0, 1e7, section=dem),
            DriverSpec("mkt_g", "Marketing budget growth per year", "%", "pct", -0.9, 5, "asc", dem),
            DriverSpec("cpl", "Cost per lead", "$", "usd2", 0, 1e5, "desc", dem),
            DriverSpec("booking", "Leads booked as jobs", "%", "pct", 0, 1, "asc", dem),
            DriverSpec("repeat_jobs", "Repeat & referral jobs per month (year 1)", "jobs", "dec1", 0, 1e6, "asc", dem),
            DriverSpec("repeat_g", "Repeat & referral jobs growth per year", "%", "pct", -0.9, 5, "asc", dem),
            DriverSpec(
                "peak_uplift", "Busy-season uplift, June–August (monthly models)", "%", "pct", 0, 1, section=dem
            ),
            DriverSpec("ticket", "Average revenue per job (year 1)", "$", "usd2", 0, 1e6, "asc", price),
            DriverSpec("price_g", "Price increase per year", "%", "pct", -0.5, 1, "asc", price),
            DriverSpec("plan_members", "Maintenance plan members (year-1 average)", "#", "int", 0, 1e7, "asc", plans),
            DriverSpec("plan_g", "Plan members growth per year", "%", "pct", -0.9, 10, "asc", plans),
            DriverSpec("plan_fee", "Plan fee per member per month (year 1)", "$", "usd2", 0, 1e5, "asc", plans),
            DriverSpec("plan_cost_pct", "Cost of plan visits, % of plan fees", "%", "pct", 0, 1, "desc", plans),
            DriverSpec("materials_pct", "Materials & parts, % of job revenue", "%", "pct", 0, 1, "desc", cost),
            DriverSpec(
                "vehicle", "Vehicle per technician per month (lease, fuel, upkeep)", "$", "usd", 0, 1e5, "desc", cost
            ),
            DriverSpec("software", "Field software & phone per technician per month", "$", "usd", 0, 1e5, section=cost),
            DriverSpec("insurance", "Insurance & licences per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("rent", "Shop / office rent per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("ga_other", "Other G&A per month (accounting, legal, bank)", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("card_fee_pct", "Card processing fees, % of revenue", "%", "pct", 0, 0.2, "desc", cost),
            DriverSpec("capex", "Start-up capex (shop, equipment)", "$", "usd", 0, 1e8, section=cost),
            DriverSpec("capex_tech", "Van & tools per technician added", "$", "usd", 0, 1e6, "desc", cost),
            DriverSpec(
                "equipped_start",
                "Technicians already equipped at start (own vans & tools)",
                "FTE",
                "dec1",
                0,
                1e5,
                section=cost,
            ),
        ]

    def validate(self, brief: Brief) -> None:
        if TECH not in {r.key for r in brief.roles}:
            raise BriefError("template 'home_services' needs the 'tech' (field technicians) role")
        super().validate(brief)

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        if t.granularity == "monthly":
            season = "=IF(AND(MOD({p}-1,12)>=5,MOD({p}-1,12)<=7),1+{in:peak_uplift},1-{in:peak_uplift}/3)"
        else:
            season = "=1"
        idx = "(1+{in:price_g})^({y}-1)"
        return [
            Line("tech_fte", "Field technicians (FTE)", "={hc_tech_fte}", "top", "dec1", agg="last", section="Jobs"),
            Line(
                "cap_jobs",
                "Job capacity (technicians × jobs per day × working days)",
                "={tech_fte}*{in:jobs_per_tech}*{in:work_days}*{mpp}",
                "top",
                "int",
            ),
            Line("season", "Season factor (June–August busy season)", season, "top", "dec1", agg="none"),
            Line("leads", "Leads from marketing", "=-{mkt}/MAX(1,{in:cpl})", "top", "int"),
            Line("booked", "Jobs booked from leads", "={leads}*{in:booking}*{season}", "top", "int"),
            Line(
                "repeat",
                "Repeat & referral jobs",
                "={in:repeat_jobs}*(1+{in:repeat_g})^({y}-1)*{mpp}*{season}",
                "top",
                "int",
            ),
            Line("demand", "Jobs demanded", "={booked}+{repeat}", "top", "int"),
            Line(
                "jobs",
                "Jobs completed (demand capped by capacity)",
                "=MIN({cap_jobs},{demand})",
                "top",
                "int",
                bold=True,
            ),
            Line(
                "price",
                "Average revenue per job",
                f"={{in:ticket}}*{idx}",
                "top",
                "usd2",
                agg="none",
                section="Revenue",
            ),
            Line("rev_jobs", "Job revenue", "={jobs}*{price}", "top"),
            Line(
                "plan_m",
                "Maintenance plan members (average)",
                "={in:plan_members}*(1+{in:plan_g})^({y}-1)",
                "top",
                "int",
                agg="last",
            ),
            Line("rev_plans", "Maintenance plan revenue", f"={{plan_m}}*{{in:plan_fee}}*{idx}*{{mpp}}", "top"),
            Line("rev", "Revenue", "={rev_jobs}+{rev_plans}", "top", bold=True, total=True),
            Line("cost_tech", "Technician payroll", "={hc_tech_cost}", "top", section="Cost of delivery"),
            Line("materials", "Materials & parts", "=-{rev_jobs}*{in:materials_pct}", "top"),
            Line("vehicles", "Vehicles", "=-{tech_fte}*{in:vehicle}*{mpp}", "top"),
            Line("plan_cost", "Plan visits", "=-{rev_plans}*{in:plan_cost_pct}", "top"),
            Line("cogs", "Cost of delivery", "={cost_tech}+{materials}+{vehicles}+{plan_cost}", "top", bold=True),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "payroll_nb",
                "Dispatch, office & other payroll",
                "={payroll_total}-{hc_tech_cost}",
                "top",
                section="Operating expenses",
            ),
            Line("mkt", "Marketing", "=-{in:mkt}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
            Line("software", "Field software & phones", "=-{tech_fte}*{in:software}*{mpp}", "top"),
            Line("insurance", "Insurance & licences", "=-{in:insurance}*{mpp}", "top"),
            Line("rent", "Shop / office rent", "=-{in:rent}*{mpp}", "top"),
            Line("ga_other", "Other G&A", "=-{in:ga_other}*{mpp}", "top"),
            Line("card_fees", "Card processing fees", "=-{rev}*{in:card_fee_pct}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "capex",
                "Capital spending (start-up + van & tools per technician added)",
                "=MAX(0,{tech_fte}-{tech_fte[-1]})*{in:capex_tech}",
                "top",
                first="={in:capex}+MAX(0,{tech_fte}-{in:equipped_start})*{in:capex_tech}",
            )
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("jobs", "Jobs completed", "kpi:jobs", "int"),
            DashMetric("util", "Technician utilisation", "kpi:util", "pct"),
            DashMetric("rev_job", "Average revenue per job", "kpi:rev_job", "usd2"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Jobs completed & technician utilisation", bars=("jobs",), lines=("util",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("tech_fte", "Field technicians (FTE, year end)", "line", "tech_fte", "dec1", bold=True),
            StmtRow("cap_jobs", "Job capacity", "line", "cap_jobs", "int"),
            StmtRow("demand", "Jobs demanded", "line", "demand", "int"),
            StmtRow("jobs", "Jobs completed", "line", "jobs", "int", bold=True),
            StmtRow(
                "util",
                "Technician utilisation (jobs ÷ capacity)",
                "formula",
                "=IF({cap_jobs}=0,0,{jobs}/{cap_jobs})",
                "pct",
            ),
            StmtRow("unserved", "Jobs turned away (demand above capacity)", "formula", "={demand}-{jobs}", "int"),
            StmtRow("booked", "Jobs booked from marketing leads", "line", "booked", "int"),
            StmtRow("mkt_spend", "Marketing spend", "line", "mkt", neg=True),
            StmtRow(
                "cost_booked",
                "Marketing cost per booked job",
                "formula",
                "=IF({booked}=0,0,{mkt_spend}/{booked})",
                "usd2",
            ),
            StmtRow("rev", "Revenue", "line", "rev", bold=True),
            StmtRow("rev_jobs", "Job revenue", "line", "rev_jobs"),
            StmtRow("rev_job", "Average revenue per job", "formula", "=IF({jobs}=0,0,{rev_jobs}/{jobs})", "usd2"),
            StmtRow(
                "rev_tech",
                "Revenue per technician (year-end FTE)",
                "formula",
                "=IF({tech_fte}=0,0,{rev}/{tech_fte})",
            ),
            StmtRow("plan_m", "Maintenance plan members (year end)", "line", "plan_m", "int"),
            StmtRow("plan_rev", "Maintenance plan revenue", "line", "rev_plans"),
            StmtRow("plan_share", "Plans share of revenue", "formula", "=IF({rev}=0,0,{plan_rev}/{rev})", "pct"),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow(
                "gp_job",
                "Gross profit per job (all gross profit ÷ jobs)",
                "formula",
                "=IF({jobs}=0,0,{gp}/{jobs})",
                "usd2",
            ),
            StmtRow("ebitda", "EBITDA", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
        ]

    # ------------------------------------------------------------------ python twin
    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        fte, tech_cost = role_period(d, TECH, p, t)
        season = _season(p, t, d["peak_uplift"])
        cap = fte * d["jobs_per_tech"] * d["work_days"] * t.mpp
        mkt = d["mkt"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp
        leads = mkt / max(1, d["cpl"])
        booked = leads * d["booking"] * season
        repeat = d["repeat_jobs"] * (1 + d["repeat_g"]) ** (y - 1) * t.mpp * season
        jobs = min(cap, booked + repeat)
        idx = (1 + d["price_g"]) ** (y - 1)
        rev_jobs = jobs * d["ticket"] * idx
        plan_m = d["plan_members"] * (1 + d["plan_g"]) ** (y - 1)
        rev_plans = plan_m * d["plan_fee"] * idx * t.mpp
        rev = rev_jobs + rev_plans
        cogs = tech_cost - rev_jobs * d["materials_pct"] - fte * d["vehicle"] * t.mpp - rev_plans * d["plan_cost_pct"]
        if p == 1:
            capex = d["capex"] + max(0.0, fte - d["equipped_start"]) * d["capex_tech"]
        else:
            prev_fte, _ = role_period(d, TECH, p - 1, t)
            capex = max(0.0, fte - prev_fte) * d["capex_tech"]
        return Top(
            rev=rev,
            cogs=cogs,
            opex={
                "payroll_nb": hc.payroll - tech_cost,
                "mkt": -mkt,
                "software": -fte * d["software"] * t.mpp,
                "insurance": -d["insurance"] * t.mpp,
                "rent": -d["rent"] * t.mpp,
                "ga_other": -d["ga_other"] * t.mpp,
                "card_fees": -rev * d["card_fee_pct"],
            },
            capex=capex,
            kpis={"jobs": jobs, "tech_fte": fte, "rev_plans": rev_plans, "cap_jobs": cap},
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
                "model_name": f"Home services financial model ({stage})",
                "template": self.key,
                "business_type": "home_services",
                "stage": stage,
                "assumption_note": "Illustrative assumptions — replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
