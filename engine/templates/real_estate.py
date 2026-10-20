"""Real estate template: a rental property bought at the start, held, and sold at the horizon.

Rent roll = units × average rent (grows yearly) less vacancy & credit loss, plus other income. Direct property
costs (repairs, owner-paid utilities) are cost of sales; property tax, insurance, management and G&A are
operating expenses, so EBITDA is the property's net operating income (NOI). The purchase (price + closing
costs) is capital spending in period 1; the land share is never depreciated, the building and closing costs
are depreciated over the depreciation period, and a capital reserve per unit is spent every period. The
mortgage is an annuity (level payment, ``loan_style``). The Returns sheet (engine/returns.py) adds the sale at
the end of the horizon (next-year NOI ÷ exit cap rate, less selling costs), unlevered and levered IRR, NPV,
equity multiple, DSCR and cash-on-cash.
Assumption memo: docs/templates/real_estate.md.
"""

from __future__ import annotations

from engine.brief import Brief
from engine.core import HC, Top
from engine.spec import DashChart, DashMetric, DriverSpec, Line, StmtRow, Timing
from engine.templates.base import Template

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer replaces
# them with their own numbers; the assumption memo says so.
_COMMON = {
    "land_pct": (0.2, 0.2, 0.2),
    "closing_pct": (0.03, 0.03, 0.03),
    "rent_g": (0.02, 0.03, 0.04),
    "vacancy": (0.08, 0.05, 0.04),
    "other_inc": (20, 25, 30),
    "repairs_pct": (0.07, 0.06, 0.05),
    "mgmt_pct": (0.08, 0.08, 0.08),
    "cost_g": (0.04, 0.03, 0.025),
    "exit_cap": (0.0725, 0.0675, 0.0625),
    "sell_pct": (0.06, 0.05, 0.05),
    "disc_rate": (0.1, 0.1, 0.1),
    "ar_days": (0, 0, 0),
    "inv_days": (0, 0, 0),
    "ap_days": (15, 15, 15),
    "dep_years": (27, 27, 27),
    "tax_rate": (0.21, 0.21, 0.21),
}
_STAGES: dict[str, dict] = {
    # first purchase: a fourplex
    "planning": {
        "price": (880000, 880000, 880000),
        "units": (4, 4, 4),
        "rent": (1900, 2000, 2100),
        "prop_tax_pct": (0.012, 0.012, 0.012),
        "insurance": (900, 900, 900),
        "utilities": (250, 250, 250),
        "ga_other": (150, 150, 150),
        "reserve": (400, 400, 400),
        "equity": (360000, 360000, 360000),
        "loan_amount": (570000, 570000, 570000),
        "loan_rate": (0.065, 0.065, 0.065),
        "loan_term_years": (30, 30, 30),
    },
    # small apartment building
    "early": {
        "price": (1850000, 1850000, 1850000),
        "units": (10, 10, 10),
        "rent": (1600, 1700, 1800),
        "prop_tax_pct": (0.011, 0.011, 0.011),
        "insurance": (800, 800, 800),
        "utilities": (900, 900, 900),
        "ga_other": (400, 400, 400),
        "reserve": (350, 350, 350),
        "equity": (760000, 760000, 760000),
        "loan_amount": (1200000, 1200000, 1200000),
        "loan_rate": (0.065, 0.065, 0.065),
        "loan_term_years": (30, 30, 30),
    },
    "growing": {
        "price": (5200000, 5200000, 5200000),
        "units": (30, 30, 30),
        "rent": (1500, 1600, 1700),
        "prop_tax_pct": (0.011, 0.011, 0.011),
        "insurance": (700, 700, 700),
        "utilities": (2500, 2500, 2500),
        "ga_other": (1200, 1200, 1200),
        "reserve": (300, 300, 300),
        "equity": (2130000, 2130000, 2130000),
        "loan_amount": (3380000, 3380000, 3380000),
        "loan_rate": (0.065, 0.065, 0.065),
        "loan_term_years": (30, 30, 30),
    },
    "established": {
        "price": (13600000, 13600000, 13600000),
        "units": (80, 80, 80),
        "rent": (1450, 1550, 1650),
        "prop_tax_pct": (0.01, 0.01, 0.01),
        "insurance": (650, 650, 650),
        "utilities": (6000, 6000, 6000),
        "ga_other": (3000, 3000, 3000),
        "reserve": (300, 300, 300),
        "equity": (5580000, 5580000, 5580000),
        "loan_amount": (8840000, 8840000, 8840000),
        "loan_rate": (0.065, 0.065, 0.065),
        "loan_term_years": (30, 30, 30),
    },
}


class RealEstateTemplate(Template):
    key = "real_estate"
    title = "Real estate (rental property)"
    business_types = ("real_estate",)
    order = 70
    key_numbers = ("price", "units", "rent", "vacancy", "loan_amount", "loan_rate", "equity", "exit_cap")
    sample_title = "Rental property"
    sample_desc = "Full workbook with rent roll, NOI, mortgage schedule, sale and IRR"
    sample_stage = "early"
    loan_style = "annuity"
    returns = True
    kpi_title = "Property metrics"
    kpi_checked = {"gpr": "gpr", "vac": "vac", "rent_unit": "rent_now"}
    kpi_flows = ("gpr", "vac", "capex_buy")

    def driver_specs(self) -> list[DriverSpec]:
        prop, rr, cost, ex = "Property", "Rent roll", "Operating costs", "Sale & returns"
        return [
            DriverSpec("price", "Purchase price", "$", "usd", 1, 1e10, section=prop),
            DriverSpec("land_pct", "Land share of the price (not depreciated)", "%", "pct", 0, 0.9, section=prop),
            DriverSpec("closing_pct", "Closing costs, % of price", "%", "pct", 0, 0.2, "desc", prop),
            DriverSpec("units", "Rentable units", "#", "int", 1, 1e5, section=prop, integer=True),
            DriverSpec("rent", "Average rent per unit per month (year 1)", "$", "usd2", 0, 1e6, "asc", rr),
            DriverSpec("rent_g", "Rent growth per year", "%", "pct", -0.2, 0.3, "asc", rr),
            DriverSpec("vacancy", "Vacancy & credit loss, % of potential rent", "%", "pct", 0, 1, "desc", rr),
            DriverSpec(
                "other_inc", "Other income per unit per month (parking, laundry, fees)", "$", "usd2", 0, 1e5, "asc", rr
            ),
            DriverSpec("repairs_pct", "Repairs & maintenance, % of collected rent", "%", "pct", 0, 0.5, "desc", cost),
            DriverSpec("utilities", "Owner-paid utilities & common areas per month", "$", "usd", 0, 1e8, section=cost),
            DriverSpec("prop_tax_pct", "Property tax per year, % of purchase price", "%", "pct", 0, 0.1, section=cost),
            DriverSpec("insurance", "Insurance per unit per year", "$", "usd", 0, 1e6, section=cost),
            DriverSpec("mgmt_pct", "Property management fee, % of revenue", "%", "pct", 0, 0.3, "desc", cost),
            DriverSpec("ga_other", "Legal, accounting & other G&A per month", "$", "usd", 0, 1e8, section=cost),
            DriverSpec("cost_g", "Operating cost inflation per year", "%", "pct", -0.1, 0.3, "desc", cost),
            DriverSpec(
                "reserve", "Capital reserve per unit per year (roofs, appliances)", "$", "usd", 0, 1e6, section=cost
            ),
            DriverSpec("exit_cap", "Exit cap rate (next-year NOI ÷ sale price)", "%", "pct", 0.01, 0.3, "desc", ex),
            DriverSpec("sell_pct", "Selling costs, % of sale price", "%", "pct", 0, 0.2, "desc", ex),
            DriverSpec("disc_rate", "Discount rate for NPV (your target return)", "%", "pct", 0, 0.5, section=ex),
        ]

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        rg = "(1+{in:rent_g})^({y}-1)"
        cg = "(1+{in:cost_g})^({y}-1)"
        return [
            Line(
                "rent_now",
                "Average rent per unit per month",
                f"={{in:rent}}*{rg}",
                "top",
                "usd2",
                agg="last",
                section="Rent roll",
            ),
            Line("gpr", "Gross potential rent (all units let)", "={in:units}*{rent_now}*{mpp}", "top"),
            Line("vac", "Vacancy & credit loss", "=-{gpr}*{in:vacancy}", "top"),
            Line(
                "other",
                "Other income (parking, laundry, fees)",
                f"={{in:units}}*{{in:other_inc}}*{rg}*(1-{{in:vacancy}})*{{mpp}}",
                "top",
            ),
            Line("rev", "Revenue (effective gross income)", "={gpr}+{vac}+{other}", "top", bold=True, total=True),
            Line(
                "repairs",
                "Repairs & maintenance",
                "=-({gpr}+{vac})*{in:repairs_pct}",
                "top",
                section="Direct property costs",
            ),
            Line("utilities", "Owner-paid utilities & common areas", f"=-{{in:utilities}}*{cg}*{{mpp}}", "top"),
            Line("cogs", "Direct property costs", "={repairs}+{utilities}", "top", bold=True),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        cg = "(1+{in:cost_g})^({y}-1)"
        return [
            Line(
                "prop_tax",
                "Property tax",
                f"=-{{in:price}}*{{in:prop_tax_pct}}/12*{cg}*{{mpp}}",
                "top",
                section="Operating expenses",
            ),
            Line("insurance", "Insurance", f"=-{{in:units}}*{{in:insurance}}/12*{cg}*{{mpp}}", "top"),
            Line("mgmt", "Property management", "=-{rev}*{in:mgmt_pct}", "top"),
            Line("ga_other", "Legal, accounting & other G&A", f"=-{{in:ga_other}}*{cg}*{{mpp}}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "capex_buy",
                "Property purchase incl. closing costs",
                "=IF({p}=1,{in:price}*(1+{in:closing_pct}),0)",
                "top",
            ),
            Line("capex_land", "of which land (not depreciated)", "=IF({p}=1,{in:price}*{in:land_pct},0)", "top"),
            Line(
                "capex_res",
                "Capital reserve spent",
                "={in:units}*{in:reserve}/12*(1+{in:cost_g})^({y}-1)*{mpp}",
                "top",
            ),
            Line("capex", "Capital spending", "={capex_buy}+{capex_res}", "top", bold=True),
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("noi", "Net operating income (NOI)", "kpi:noi", "usdk"),
            DashMetric("occ", "Economic occupancy", "kpi:occ", "pct"),
            DashMetric("ds", "Debt service (interest + principal)", "kpi:ds", "usdk"),
            DashMetric("dscr", "Debt service coverage", "kpi:dscr", "x"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("NOI, debt service & coverage", bars=("noi", "ds"), lines=("dscr",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("rent_unit", "Average rent per unit per month", "line", "rent_now", "usd2"),
            StmtRow("gpr", "Gross potential rent", "line", "gpr", bold=True),
            StmtRow("vac", "Vacancy & credit loss", "line", "vac"),
            StmtRow(
                "occ",
                "Economic occupancy (collected ÷ potential rent)",
                "formula",
                "=IF({gpr}=0,0,({gpr}+{vac})/{gpr})",
                "pct",
            ),
            StmtRow("rev", "Revenue (effective gross income)", "line", "rev"),
            StmtRow("noi", "Net operating income (NOI = EBITDA)", "line", "ebitda", bold=True),
            StmtRow("noi_m", "NOI margin", "formula", "=IF({rev}=0,0,{noi}/{rev})", "pct"),
            StmtRow("opex_ratio", "Operating expense ratio", "formula", "=IF({rev}=0,0,1-{noi}/{rev})", "pct"),
            StmtRow("noi_unit", "NOI per unit", "formula", "=IF({in:units}=0,0,{noi}/{in:units})"),
            StmtRow("yield", "NOI ÷ purchase price", "formula", "=IF({in:price}=0,0,{noi}/{in:price})", "pct"),
            StmtRow("ds", "Debt service (interest + principal)", "line", "debt_service", neg=True),
            StmtRow(
                "dscr", "Debt service coverage (NOI ÷ debt service)", "formula", '=IF({ds}>0.5,{noi}/{ds},"n/a")', "x"
            ),
            StmtRow("loan_end", "Loan balance (year end)", "line", "loan_close"),
            StmtRow(
                "ltv", "Loan ÷ purchase price (year end)", "formula", "=IF({in:price}=0,0,{loan_end}/{in:price})", "pct"
            ),
        ]

    # ------------------------------------------------------------------ python twin
    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        rg = (1 + d["rent_g"]) ** (y - 1)
        cg = (1 + d["cost_g"]) ** (y - 1)
        rent_now = d["rent"] * rg
        gpr = d["units"] * rent_now * t.mpp
        vac = -gpr * d["vacancy"]
        other = d["units"] * d["other_inc"] * rg * (1 - d["vacancy"]) * t.mpp
        rev = gpr + vac + other
        cogs = -(gpr + vac) * d["repairs_pct"] - d["utilities"] * cg * t.mpp
        buy = d["price"] * (1 + d["closing_pct"]) if p == 1 else 0.0
        reserve = d["units"] * d["reserve"] / 12 * cg * t.mpp
        return Top(
            rev=rev,
            cogs=cogs,
            opex={
                "prop_tax": -d["price"] * d["prop_tax_pct"] / 12 * cg * t.mpp,
                "insurance": -d["units"] * d["insurance"] / 12 * cg * t.mpp,
                "mgmt": -rev * d["mgmt_pct"],
                "ga_other": -d["ga_other"] * cg * t.mpp,
            },
            capex=buy + reserve,
            land=d["price"] * d["land_pct"] if p == 1 else 0.0,
            kpis={"gpr": gpr, "vac": vac, "rent_now": rent_now, "capex_buy": buy},
        )

    # ------------------------------------------------------------------ defaults
    def default_brief(self, stage: str = "early", **opts) -> Brief:
        vals = {**_COMMON, **_STAGES[stage]}
        drivers = [{"key": k, "low": v[0], "base": v[1], "high": v[2]} for k, v in vals.items()]
        brief = Brief.model_validate(
            {
                "model_name": f"Rental property financial model ({stage})",
                "template": self.key,
                "business_type": "real_estate",
                "stage": stage,
                "assumption_note": "Illustrative assumptions — replace them with your own numbers.",
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
