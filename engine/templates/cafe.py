"""Restaurant / cafe template: traffic ramp × average ticket × operating days."""

from __future__ import annotations

from engine.core import HC, Top
from engine.spec import DriverSpec, Line, Timing
from engine.templates.base import Template


class CafeTemplate(Template):
    key = "cafe"
    title = "Restaurant / cafe"
    business_types = ("restaurant_cafe",)
    order = 20
    key_numbers = ("cust_full", "ticket", "days", "cogs_pct", "rent", "capex", "equity")
    sample_title = "Neighborhood cafe"
    sample_desc = "Full workbook, three years, monthly detail"
    sample_stage = "early"

    def default_brief(self, stage: str = "planning", **opts):
        """The cafe has one illustrative brief (engine/briefs/cafe.json) for every stage."""
        from pathlib import Path

        from engine.brief import Brief

        brief = Brief.load(Path(__file__).resolve().parents[1] / "briefs" / "cafe.json")
        return brief.with_options(stage=stage, **opts) if stage else brief

    def driver_specs(self) -> list[DriverSpec]:
        return [
            DriverSpec("cust_full", "Customers per day at full traffic", "#", "int", 0, 100000, "asc"),
            DriverSpec("ramp_months", "Months to reach full traffic", "months", "int", 0, 36, "desc", integer=True),
            DriverSpec("open_pct", "Opening traffic, % of full", "%", "pct", 0, 1, "asc"),
            DriverSpec("traffic_g", "Traffic growth per year (after year 1)", "%", "pct", -0.5, 1, "asc"),
            DriverSpec("ticket", "Average ticket", "$", "usd2", 0, 1000, "asc"),
            DriverSpec("price_g", "Price growth per year", "%", "pct", -0.5, 1, "asc"),
            DriverSpec("days", "Operating days per month", "days", "int", 1, 31),
            DriverSpec("cogs_pct", "Food & beverage cost, % of revenue", "%", "pct", 0, 1, "desc"),
            DriverSpec("rent", "Rent per month", "$", "usd", 0, 1e6),
            DriverSpec("mkt_pct", "Marketing, % of revenue", "%", "pct", 0, 1, "desc"),
            DriverSpec("other_opex", "Utilities & other per month", "$", "usd", 0, 1e6, "desc"),
            DriverSpec("capex", "Start-up capex (fit-out, equipment)", "$", "usd", 0, 1e8, "desc"),
        ]

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
                    section="Revenue build",
                )
            ]
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
                    section="Revenue build",
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
        return ramp + [
            Line(
                "cust",
                "Customers per day",
                "={in:cust_full}*{ramp}*(1+{in:traffic_g})^({y}-1)",
                "top",
                "dec1",
                agg="none",
            ),
            Line("ticket", "Average ticket", "={in:ticket}*(1+{in:price_g})^({y}-1)", "top", "usd2", agg="none"),
            Line("days", "Operating days in period", "={in:days}*{mpp}", "top", "int", agg="none"),
            Line("rev", "Revenue", "={cust}*{ticket}*{days}", "top", bold=True, total=True),
            Line("cogs", "Food & beverage cost", "=-{rev}*{in:cogs_pct}", "top"),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        return [
            Line("rent", "Rent", "=-{in:rent}*{mpp}", "top", section="Operating expenses"),
            Line("payroll", "Payroll", "={payroll_total}", "top"),
            Line("mkt", "Marketing", "=-{rev}*{in:mkt_pct}", "top"),
            Line("other", "Utilities & other", "=-{in:other_opex}*{mpp}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [Line("capex", "Capital spending", "=IF({p}=1,{in:capex},0)", "top", section="Capital spending")]

    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        a, r = d["open_pct"], max(1, d["ramp_months"])
        if t.granularity == "monthly":
            ramp = min(1, a + (1 - a) * (p - 1) / r)
        else:
            ramp = sum(min(1, a + (1 - a) * (12 * (y - 1) + k) / r) for k in range(12)) / 12
        cust = d["cust_full"] * ramp * (1 + d["traffic_g"]) ** (y - 1)
        ticket = d["ticket"] * (1 + d["price_g"]) ** (y - 1)
        rev = cust * ticket * d["days"] * t.mpp
        return Top(
            rev=rev,
            cogs=-rev * d["cogs_pct"],
            opex={
                "rent": -d["rent"] * t.mpp,
                "payroll": hc.payroll,
                "mkt": -rev * d["mkt_pct"],
                "other": -d["other_opex"] * t.mpp,
            },
            capex=d["capex"] if p == 1 else 0.0,
        )
