"""Professional services template: billable capacity → rate card → retainer / project fees.

Billable hours = billable FTE × available hours × utilisation, for two billable employee
roles (``senior`` and ``staff``, both required), plus contractor hours bought in. Hours are
priced at the rate card; retainer work carries a discount, project work a realisation
rate (write-offs). Billable payroll and contractors are cost of delivery, so gross margin
is the delivery margin; any other roles are non-billable overhead.
Assumption memo: docs/templates/services.md.
"""

from __future__ import annotations

from engine.brief import Brief, BriefError
from engine.core import HC, Top, role_period
from engine.spec import DriverSpec, Line, StmtRow, Timing
from engine.templates.base import Template

BILLABLE = ("senior", "staff")
ROLES = [
    ("senior", "Partners & senior consultants"),
    ("staff", "Consultants"),
    ("bd", "Business development"),
    ("ops", "Operations & admin"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer
# replaces them with their own numbers; the assumption memo says so.
_COMMON = {
    "avail_hours": (1800, 1800, 1800),
    "senior_util": (0.5, 0.55, 0.6),
    "staff_util": (0.68, 0.75, 0.8),
    "contractor_g": (0.1, 0.2, 0.3),
    "senior_rate": (300, 350, 400),
    "staff_rate": (150, 175, 200),
    "contractor_rate": (140, 150, 165),
    "rate_g": (0.02, 0.03, 0.04),
    "retainer_pct": (0.4, 0.4, 0.4),
    "retainer_disc": (0.12, 0.1, 0.08),
    "realisation": (0.88, 0.92, 0.95),
    "contractor_cost": (95, 90, 85),
    "delivery_pct": (0.04, 0.03, 0.025),
    "tools_per_fte": (200, 200, 200),
    "payroll_tax": (0.2, 0.2, 0.2),
    "wage_g": (0.03, 0.03, 0.03),
    "ar_days": (45, 45, 45),
    "inv_days": (0, 0, 0),
    "ap_days": (15, 15, 15),
    "dep_years": (5, 5, 5),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "contractor_hours": (20, 40, 60),
            "mkt": (1000, 1000, 1000),
            "office": (0, 0, 0),
            "ga_other": (1000, 1000, 1000),
            "capex": (10000, 10000, 10000),
            "equity": (100000, 100000, 100000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "senior": (1, 140000, 1, 0.0),
            "staff": (1, 85000, 4, 1.0),
            "bd": (0.5, 70000, 7, 1.0),
            "ops": (0.5, 60000, 1, 0.0),
        },
    },
    "early": {
        "drivers": {
            "contractor_hours": (100, 150, 200),
            "mkt": (3000, 3000, 3000),
            "office": (2500, 2500, 2500),
            "ga_other": (2500, 2500, 2500),
            "capex": (25000, 25000, 25000),
            "equity": (250000, 250000, 250000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "senior": (2, 150000, 1, 0.25),
            "staff": (3, 90000, 1, 0.5),
            "bd": (1, 80000, 1, 0.0),
            "ops": (1, 60000, 1, 0.0),
        },
    },
    "growing": {
        "drivers": {
            "contractor_hours": (300, 400, 500),
            "mkt": (8000, 8000, 8000),
            "office": (8000, 8000, 8000),
            "ga_other": (6000, 6000, 6000),
            "capex": (60000, 60000, 60000),
            "equity": (300000, 300000, 300000),
            "loan_amount": (200000, 200000, 200000),
            "loan_rate": (0.08, 0.08, 0.08),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {
            "senior": (4, 160000, 1, 0.2),
            "staff": (12, 95000, 1, 0.3),
            "bd": (2, 85000, 1, 0.2),
            "ops": (3, 65000, 1, 0.15),
        },
    },
    "established": {
        "drivers": {
            "contractor_hours": (800, 1000, 1200),
            "mkt": (20000, 20000, 20000),
            "office": (25000, 25000, 25000),
            "ga_other": (15000, 15000, 15000),
            "capex": (150000, 150000, 150000),
            "equity": (500000, 500000, 500000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "senior": (10, 175000, 1, 0.1),
            "staff": (40, 100000, 1, 0.1),
            "bd": (5, 90000, 1, 0.1),
            "ops": (8, 70000, 1, 0.1),
        },
    },
}


class ServicesTemplate(Template):
    key = "services"
    title = "Professional services"
    business_types = ("professional_services",)
    kpi_title = "Services metrics"
    kpi_checked = {"hours": "hours", "billable_fte": "billable_fte", "retainer": "rev_retainer"}
    kpi_flows = ("hours", "rev_retainer")

    def driver_specs(self) -> list[DriverSpec]:
        cap, rates, mix, cost = "Billable capacity", "Rate card", "Retainer vs project", "Costs"
        return [
            DriverSpec(
                "avail_hours", "Available hours per billable FTE per year", "hours", "int", 1, 4000, section=cap
            ),
            DriverSpec("senior_util", "Utilisation — partners & senior consultants", "%", "pct", 0, 1, "asc", cap),
            DriverSpec("staff_util", "Utilisation — consultants", "%", "pct", 0, 1, "asc", cap),
            DriverSpec(
                "contractor_hours", "Contractor billable hours per month (year 1)", "hours", "dec1", 0, 1e6, "asc", cap
            ),
            DriverSpec("contractor_g", "Contractor hours growth per year", "%", "pct", -0.9, 5, "asc", cap),
            DriverSpec(
                "senior_rate", "Hourly rate — partners & senior consultants", "$ / hour", "usd", 0, 1e5, "asc", rates
            ),
            DriverSpec("staff_rate", "Hourly rate — consultants", "$ / hour", "usd", 0, 1e5, "asc", rates),
            DriverSpec(
                "contractor_rate", "Hourly rate billed for contractor hours", "$ / hour", "usd", 0, 1e5, "asc", rates
            ),
            DriverSpec("rate_g", "Rate card increase per year", "%", "pct", -0.5, 1, "asc", rates),
            DriverSpec("retainer_pct", "Share of billable hours under retainers", "%", "pct", 0, 1, section=mix),
            DriverSpec("retainer_disc", "Retainer discount vs rate card", "%", "pct", 0, 0.9, "desc", mix),
            DriverSpec("realisation", "Project realisation (billed ÷ rate-card value)", "%", "pct", 0, 1, "asc", mix),
            DriverSpec(
                "contractor_cost", "Contractor cost per hour (year 1)", "$ / hour", "usd2", 0, 1e5, "desc", cost
            ),
            DriverSpec("delivery_pct", "Non-rebillable delivery costs, % of fees", "%", "pct", 0, 1, "desc", cost),
            DriverSpec("tools_per_fte", "Software & tools per FTE per month", "$", "usd", 0, 1e4, section=cost),
            DriverSpec("mkt", "Marketing & business development per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("office", "Office & rent per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec(
                "ga_other", "Other G&A per month (insurance, legal, accounting)", "$", "usd", 0, 1e7, section=cost
            ),
            DriverSpec("capex", "Start-up capex (equipment, fit-out)", "$", "usd", 0, 1e8, section=cost),
        ]

    def validate(self, brief: Brief) -> None:
        missing = [k for k in BILLABLE if k not in {r.key for r in brief.roles}]
        if missing:
            raise BriefError(f"template 'services' needs billable roles {list(BILLABLE)}; missing {missing}")
        super().validate(brief)

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        hours = "={hc_%s_fte}*{in:avail_hours}/12*{mpp}*{in:%s_util}"
        rate = "={in:%s_rate}*(1+{in:rate_g})^({y}-1)"
        return [
            Line(
                "billable_fte",
                "Billable employees (FTE)",
                "={hc_senior_fte}+{hc_staff_fte}",
                "top",
                "dec1",
                agg="last",
                section="Billable capacity",
            ),
            Line(
                "cap_hours",
                "Available hours — billable employees",
                "={billable_fte}*{in:avail_hours}/12*{mpp}",
                "top",
                "int",
            ),
            Line("hours_senior", "Billable hours — partners & senior", hours % ("senior", "senior"), "top", "int"),
            Line("hours_staff", "Billable hours — consultants", hours % ("staff", "staff"), "top", "int"),
            Line(
                "hours_contr",
                "Billable hours — contractors",
                "={in:contractor_hours}*(1+{in:contractor_g})^({y}-1)*{mpp}",
                "top",
                "int",
            ),
            Line(
                "hours",
                "Billable hours — total",
                "={hours_senior}+{hours_staff}+{hours_contr}",
                "top",
                "int",
                bold=True,
            ),
            Line("rate_senior", "Rate — partners & senior", rate % "senior", "top", "usd2", agg="none", section="Fees"),
            Line("rate_staff", "Rate — consultants", rate % "staff", "top", "usd2", agg="none"),
            Line("rate_contr", "Rate — contractor hours", rate % "contractor", "top", "usd2", agg="none"),
            Line(
                "fees_std",
                "Fees at rate card",
                "={hours_senior}*{rate_senior}+{hours_staff}*{rate_staff}+{hours_contr}*{rate_contr}",
                "top",
            ),
            Line("rev_retainer", "Retainer fees", "={fees_std}*{in:retainer_pct}*(1-{in:retainer_disc})", "top"),
            Line("rev_project", "Project fees", "={fees_std}*(1-{in:retainer_pct})*{in:realisation}", "top"),
            Line("rev", "Fee revenue", "={rev_retainer}+{rev_project}", "top", bold=True, total=True),
            Line(
                "cost_billable",
                "Billable staff payroll",
                "={hc_senior_cost}+{hc_staff_cost}",
                "top",
                section="Cost of delivery",
            ),
            Line(
                "cost_contr",
                "Contractor cost",
                "=-{hours_contr}*{in:contractor_cost}*(1+{in:wage_g})^({y}-1)",
                "top",
            ),
            Line("delivery", "Non-rebillable delivery costs", "=-{rev}*{in:delivery_pct}", "top"),
            Line("cogs", "Cost of delivery", "={cost_billable}+{cost_contr}+{delivery}", "top", bold=True),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "payroll_nb",
                "Non-billable payroll",
                "={payroll_total}-{hc_senior_cost}-{hc_staff_cost}",
                "top",
                section="Operating expenses",
            ),
            Line("mkt", "Marketing & business development", "=-{in:mkt}*{mpp}", "top"),
            Line("tools", "Software & tools", "=-{fte_total}*{in:tools_per_fte}*{mpp}", "top"),
            Line("office", "Office & rent", "=-{in:office}*{mpp}", "top"),
            Line("ga_other", "Other G&A", "=-{in:ga_other}*{mpp}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [Line("capex", "Capital spending", "=IF({p}=1,{in:capex},0)", "top")]

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("billable_fte", "Billable employees (FTE, year end)", "line", "billable_fte", "dec1", bold=True),
            StmtRow("hours", "Billable hours", "line", "hours", "int", bold=True),
            StmtRow("hours_emp", "Billable hours — employees", "formula", "={hours}-{hours_contr}", "int"),
            StmtRow("hours_contr", "Billable hours — contractors", "line", "hours_contr", "int"),
            StmtRow("cap_hours", "Available hours — billable employees", "line", "cap_hours", "int"),
            StmtRow(
                "util",
                "Utilisation of billable employees",
                "formula",
                "=IF({cap_hours}=0,0,{hours_emp}/{cap_hours})",
                "pct",
            ),
            StmtRow(
                "contr_share",
                "Contractor share of billable hours",
                "formula",
                "=IF({hours}=0,0,{hours_contr}/{hours})",
                "pct",
            ),
            StmtRow("fees_std", "Fees at rate card", "line", "fees_std"),
            StmtRow("rev", "Fee revenue", "line", "rev", bold=True),
            StmtRow("retainer", "Retainer fees", "line", "rev_retainer"),
            StmtRow("retainer_share", "Retainer share of revenue", "formula", "=IF({rev}=0,0,{retainer}/{rev})", "pct"),
            StmtRow(
                "realised",
                "Realisation vs rate card (all work)",
                "formula",
                "=IF({fees_std}=0,0,{rev}/{fees_std})",
                "pct",
            ),
            StmtRow(
                "eff_rate", "Effective rate per billable hour", "formula", "=IF({hours}=0,0,{rev}/{hours})", "usd2"
            ),
            StmtRow(
                "rev_fte",
                "Revenue per billable FTE (year-end FTE)",
                "formula",
                "=IF({billable_fte}=0,0,{rev}/{billable_fte})",
            ),
            StmtRow("cost_emp", "Billable staff payroll", "line", "cost_billable", neg=True),
            StmtRow("cost_contr", "Contractor cost", "line", "cost_contr", neg=True),
            StmtRow(
                "emp_hr",
                "Employee cost per billable hour",
                "formula",
                "=IF({hours_emp}=0,0,{cost_emp}/{hours_emp})",
                "usd2",
            ),
            StmtRow(
                "contr_hr",
                "Contractor cost per billable hour",
                "formula",
                "=IF({hours_contr}=0,0,{cost_contr}/{hours_contr})",
                "usd2",
            ),
            StmtRow("gp", "Gross profit (delivery margin)", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("ar", "Receivables (year end)", "line", "ar"),
        ]

    # ------------------------------------------------------------------ python twin
    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        fte_s, cost_s = role_period(d, "senior", p, t)
        fte_c, cost_c = role_period(d, "staff", p, t)
        per_fte_hours = d["avail_hours"] / 12 * t.mpp
        h_senior = fte_s * per_fte_hours * d["senior_util"]
        h_staff = fte_c * per_fte_hours * d["staff_util"]
        h_contr = d["contractor_hours"] * (1 + d["contractor_g"]) ** (y - 1) * t.mpp
        idx = (1 + d["rate_g"]) ** (y - 1)
        fees = (h_senior * d["senior_rate"] + h_staff * d["staff_rate"] + h_contr * d["contractor_rate"]) * idx
        retainer = fees * d["retainer_pct"] * (1 - d["retainer_disc"])
        rev = retainer + fees * (1 - d["retainer_pct"]) * d["realisation"]
        contr_cost = -h_contr * d["contractor_cost"] * (1 + d["wage_g"]) ** (y - 1)
        return Top(
            rev=rev,
            cogs=cost_s + cost_c + contr_cost - rev * d["delivery_pct"],
            opex={
                "payroll_nb": hc.payroll - cost_s - cost_c,
                "mkt": -d["mkt"] * t.mpp,
                "tools": -hc.fte * d["tools_per_fte"] * t.mpp,
                "office": -d["office"] * t.mpp,
                "ga_other": -d["ga_other"] * t.mpp,
            },
            capex=d["capex"] if p == 1 else 0.0,
            kpis={"hours": h_senior + h_staff + h_contr, "billable_fte": fte_s + fte_c, "rev_retainer": retainer},
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
                "model_name": f"Professional services financial model ({stage})",
                "template": "services",
                "business_type": "professional_services",
                "stage": stage,
                "assumption_note": "Illustrative assumptions — replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
