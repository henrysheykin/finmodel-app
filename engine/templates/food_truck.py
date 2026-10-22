"""Food truck template: street service days × meals per day × ticket, plus events and catering.

A fleet of one or more trucks. Street sales: service days per truck per month (fewer in winter, the other nine
months give the days back so the year is unchanged) × meals per street day (a straight-line ramp-up from opening)
× average ticket. Events and catering: event days per truck per month (also on the ramp) × revenue per event.
Cost of sales = food (% of sales), packaging per meal, card fees and event / festival fees (a % of event revenue
plus a booth fee per event day). Operating costs: payroll (owner-operator, cooks, cashiers), commissary kitchen,
permits and licences, insurance, maintenance (all per truck), fuel and generator per service day, POS software,
marketing and other G&A. Capex: the truck and its build-out (optionally financed with the standard loan), POS
hardware, trucks added in later years and a yearly equipment refresh. Inventory is a few days of perishables.
Assumption memo: docs/templates/food_truck.md.
"""

from __future__ import annotations

from engine.brief import Brief
from engine.core import HC, Top
from engine.spec import DashChart, DashMetric, DriverSpec, KpiChart, Line, StmtRow, Timing
from engine.templates.base import Template, div

ROLES = [
    ("owner", "Owner-operator (salary optional)"),
    ("cook", "Cooks"),
    ("cashier", "Cashiers & service staff"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer replaces
# them with their own numbers; the assumption memo says which are sourced and which are assumptions.
_COMMON = {
    "winter_dip": (0.3, 0.25, 0.2),
    "meals_g": (0.0, 0.03, 0.05),
    "price_g": (0.02, 0.03, 0.04),
    "events_g": (0.0, 0.05, 0.1),
    "event_meals": (100, 100, 100),
    "event_fee_pct": (0.05, 0.04, 0.03),
    "event_fee_day": (120, 100, 80),
    "pack": (0.5, 0.45, 0.4),
    "card_pct": (0.031, 0.029, 0.027),
    "cost_g": (0.04, 0.03, 0.025),
    "capex_pos": (3000, 3000, 3000),
    "payroll_tax": (0.12, 0.12, 0.12),
    "wage_g": (0.03, 0.03, 0.03),
    "ar_days": (3, 3, 3),
    "inv_days": (3, 3, 3),
    "ap_days": (7, 7, 7),
    "dep_years": (7, 7, 7),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "trucks": (1, 1, 1),
            "trucks_add": (0, 0, 0),
            "trucks_new": (1, 1, 1),
            "street_days": (17, 18, 19),
            "events_pm": (2.5, 3, 3.5),
            "ramp_months": (9, 6, 4),
            "ramp_start": (0.35, 0.5, 0.6),
            "meals_day": (78, 88, 98),
            "ticket": (13, 14, 15),
            "event_rev": (1250, 1400, 1550),
            "food_pct": (0.345, 0.33, 0.315),
            "commissary": (1050, 950, 850),
            "permits": (400, 380, 360),
            "insurance": (480, 450, 420),
            "fuel": (40, 38, 36),
            "maint": (550, 500, 450),
            "pos_sub": (125, 120, 115),
            "mkt": (800, 700, 600),
            "mkt_g": (0.0, 0.0, 0.0),
            "ga_other": (380, 350, 320),
            "capex_truck": (95000, 95000, 95000),
            "capex_build": (40000, 40000, 40000),
            "capex_refresh": (2500, 2500, 2500),
            "equity": (100000, 100000, 100000),
            "loan_amount": (90000, 90000, 90000),
            "loan_rate": (0.09, 0.09, 0.09),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {
            "owner": (1, 36000, 1, 0.0),
            "cook": (1.2, 34000, 1, 0.0),
            "cashier": (1, 29000, 1, 0.0),
        },
    },
    "early": {
        "drivers": {
            "trucks": (1, 1, 1),
            "trucks_add": (0, 0, 0),
            "trucks_new": (0, 0, 0),
            "street_days": (18, 19, 20),
            "events_pm": (2.5, 3, 3.5),
            "ramp_months": (6, 4, 3),
            "ramp_start": (0.6, 0.7, 0.8),
            "meals_day": (80, 90, 100),
            "ticket": (13, 14, 15),
            "event_rev": (1250, 1400, 1550),
            "food_pct": (0.34, 0.325, 0.31),
            "commissary": (1050, 950, 850),
            "permits": (400, 380, 360),
            "insurance": (480, 450, 420),
            "fuel": (40, 38, 36),
            "maint": (600, 550, 500),
            "pos_sub": (125, 120, 115),
            "mkt": (750, 650, 550),
            "mkt_g": (0.0, 0.0, 0.0),
            "ga_other": (380, 350, 320),
            "capex_truck": (95000, 95000, 95000),
            "capex_build": (40000, 40000, 40000),
            "capex_refresh": (3000, 3000, 3000),
            "equity": (35000, 35000, 35000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "owner": (1, 36000, 1, 0.0),
            "cook": (1.2, 34000, 1, 0.0),
            "cashier": (1, 29000, 1, 0.0),
        },
    },
    "growing": {
        "drivers": {
            "trucks": (2, 2, 2),
            "trucks_add": (0, 0, 0),
            "trucks_new": (0, 0, 0),
            "street_days": (19, 20, 21),
            "events_pm": (3.5, 4, 4.5),
            "ramp_months": (0, 0, 0),
            "ramp_start": (1, 1, 1),
            "meals_day": (75, 85, 95),
            "ticket": (13.5, 14.5, 15.5),
            "event_rev": (1300, 1450, 1600),
            "food_pct": (0.33, 0.315, 0.3),
            "commissary": (980, 900, 820),
            "permits": (380, 360, 340),
            "insurance": (450, 430, 410),
            "fuel": (40, 38, 36),
            "maint": (600, 550, 500),
            "pos_sub": (125, 120, 115),
            "mkt": (1300, 1200, 1100),
            "mkt_g": (0.03, 0.03, 0.03),
            "ga_other": (650, 600, 550),
            "capex_truck": (95000, 95000, 95000),
            "capex_build": (40000, 40000, 40000),
            "capex_refresh": (3500, 3500, 3500),
            "equity": (40000, 40000, 40000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "owner": (1, 44000, 1, 0.0),
            "cook": (3, 35000, 1, 0.0),
            "cashier": (2.6, 30000, 1, 0.0),
        },
    },
    "established": {
        "drivers": {
            "trucks": (3, 3, 3),
            "trucks_add": (0, 0, 0),
            "trucks_new": (0, 0, 0),
            "street_days": (19, 20, 21),
            "events_pm": (3.5, 4, 4.5),
            "ramp_months": (0, 0, 0),
            "ramp_start": (1, 1, 1),
            "meals_day": (78, 88, 98),
            "ticket": (13.5, 14.5, 15.5),
            "event_rev": (1400, 1550, 1700),
            "food_pct": (0.32, 0.305, 0.29),
            "commissary": (950, 850, 780),
            "permits": (370, 350, 330),
            "insurance": (440, 420, 400),
            "fuel": (40, 38, 36),
            "maint": (650, 600, 550),
            "pos_sub": (135, 130, 125),
            "mkt": (1700, 1500, 1300),
            "mkt_g": (0.03, 0.03, 0.03),
            "ga_other": (950, 850, 750),
            "capex_truck": (95000, 95000, 95000),
            "capex_build": (40000, 40000, 40000),
            "capex_refresh": (4000, 4000, 4000),
            "equity": (40000, 40000, 40000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "owner": (1, 56000, 1, 0.0),
            "cook": (4.6, 36000, 1, 0.0),
            "cashier": (3.9, 31000, 1, 0.0),
        },
    },
}


def _ramp(d: dict, p: int, t: Timing) -> float:
    """Average share of mature volume in period ``p``: a straight line from ``ramp_start`` to 1 over
    ``ramp_months`` months, averaged over the months the period covers (so annual = the mean of its months)."""
    months = d["ramp_months"]
    if months <= 0:
        return 1.0
    j0 = (p - 1) * t.mpp  # months elapsed before the period
    n = max(0.0, min(float(t.mpp), months - j0))  # months of the period still on the ramp
    s = d["ramp_start"]
    return (n * s + (1 - s) / max(1, months) * (n * j0 + n * (n - 1) / 2) + t.mpp - n) / t.mpp


def _season(d: dict, p: int, t: Timing) -> float:
    """Winter dip in street service days, December-February (model month 1 = January); the other nine months
    give the days back so the year is unchanged. Annual models carry no seasonality."""
    if t.granularity != "monthly":
        return 1.0
    m = (p - 1) % 12  # 0 = January
    dip = d["winter_dip"]
    return 1 - dip if m in (11, 0, 1) else 1 + dip / 3


class FoodTruckTemplate(Template):
    key = "food_truck"
    title = "Food truck"
    business_types = ("food_truck",)
    order = 140
    key_numbers = ("street_days", "meals_day", "ticket", "events_pm", "food_pct", "capex_truck", "equity")
    sample_title = "Food truck"
    sample_desc = "Full workbook with street service days, meals per day, events and catering, food cost and commissary"
    sample_stage = "planning"
    kpi_title = "Food truck metrics"
    kpi_checked = {
        "trucks_end": "trucks_total",
        "service_days": "service_days",
        "meals": "meals",
        "rev": "rev",
        "rev_street": "rev_street",
        "rev_event": "rev_event",
        "food_pack": "food_pack",
        "payroll": "payroll_total",
        "gp": "gp",
        "ebitda": "ebitda",
    }
    kpi_derived = (
        "meals_day",
        "ticket",
        "rev_day",
        "rev_truck",
        "event_share",
        "food_pct",
        "prime",
        "gm",
        "em",
    )
    kpi_flows = ("service_days", "meals", "rev_street", "rev_event", "food_pack")

    def driver_specs(self) -> list[DriverSpec]:
        fleet, ramp, street, events = "Fleet & service days", "Ramp-up", "Street sales", "Events & catering"
        cost, opex, cx = "Cost of sales", "Operating costs", "Capital spending"
        return [
            DriverSpec("trucks", "Food trucks in operation at start", "#", "int", 1, 100, section=fleet, integer=True),
            DriverSpec(
                "trucks_add",
                "Trucks added each year (from year 2; raise headcount to match)",
                "#",
                "int",
                0,
                100,
                section=fleet,
                integer=True,
            ),
            DriverSpec(
                "street_days",
                "Street service days per truck per month (year average)",
                "days",
                "dec1",
                0,
                28,
                "asc",
                fleet,
            ),
            DriverSpec(
                "winter_dip",
                "Winter dip in street service days, December-February (monthly models)",
                "%",
                "pct",
                0,
                0.9,
                "desc",
                fleet,
            ),
            DriverSpec(
                "ramp_months",
                "Months to reach mature volume (0 = already mature)",
                "months",
                "int",
                0,
                60,
                "desc",
                ramp,
                integer=True,
            ),
            DriverSpec("ramp_start", "Volume in month 1, % of mature", "%", "pct", 0, 1, "asc", ramp),
            DriverSpec(
                "meals_day",
                "Meals per street service day at maturity (year 1)",
                "meals",
                "dec1",
                0,
                2000,
                "asc",
                street,
            ),
            DriverSpec("meals_g", "Meals per day growth per year", "%", "pct", -0.9, 5, "asc", street),
            DriverSpec("ticket", "Average ticket per meal (year 1)", "$", "usd2", 0, 1000, "asc", street),
            DriverSpec("price_g", "Price increase per year", "%", "pct", -0.5, 1, "asc", street),
            DriverSpec(
                "events_pm",
                "Event and catering days per truck per month (year 1)",
                "days",
                "dec1",
                0,
                28,
                "asc",
                events,
            ),
            DriverSpec("events_g", "Event days growth per year", "%", "pct", -0.9, 5, "asc", events),
            DriverSpec("event_rev", "Revenue per event or catering day (year 1)", "$", "usd", 0, 1e6, "asc", events),
            DriverSpec(
                "event_meals", "Meals served per event or catering day", "meals", "dec1", 0, 5000, section=events
            ),
            DriverSpec("food_pct", "Food cost, % of sales", "%", "pct", 0, 1, "desc", cost),
            DriverSpec("pack", "Packaging & disposables per meal (year 1)", "$", "usd2", 0, 100, "desc", cost),
            DriverSpec("card_pct", "Card & POS processing fees, % of revenue", "%", "pct", 0, 0.2, "desc", cost),
            DriverSpec("event_fee_pct", "Event & festival fees, % of event revenue", "%", "pct", 0, 1, "desc", cost),
            DriverSpec(
                "event_fee_day", "Event booth or vendor fee per event day (year 1)", "$", "usd", 0, 1e5, "desc", cost
            ),
            DriverSpec(
                "cost_g", "Cost increase per year (packaging, fuel, fixed costs)", "%", "pct", -0.5, 1, "desc", cost
            ),
            DriverSpec("commissary", "Commissary kitchen rent per truck per month", "$", "usd", 0, 1e6, section=opex),
            DriverSpec(
                "permits", "Permits & licences per truck per month (annual fees ÷ 12)", "$", "usd", 0, 1e6, section=opex
            ),
            DriverSpec("insurance", "Insurance per truck per month", "$", "usd", 0, 1e6, section=opex),
            DriverSpec("fuel", "Fuel, propane & generator per service day", "$", "usd2", 0, 1e4, section=opex),
            DriverSpec("maint", "Truck maintenance & repairs per truck per month", "$", "usd", 0, 1e6, section=opex),
            DriverSpec("pos_sub", "POS & ordering software per month", "$", "usd", 0, 1e6, section=opex),
            DriverSpec("mkt", "Marketing budget per month (year 1)", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("mkt_g", "Marketing budget growth per year", "%", "pct", -0.9, 5, section=opex),
            DriverSpec("ga_other", "Accounting, bank fees & other G&A per month", "$", "usd", 0, 1e7, section=opex),
            DriverSpec(
                "trucks_new", "Trucks to buy and build out in month 1", "#", "int", 0, 100, section=cx, integer=True
            ),
            DriverSpec("capex_truck", "Truck purchase, each", "$", "usd", 0, 1e7, section=cx),
            DriverSpec("capex_build", "Kitchen build-out, equipment & wrap, per truck", "$", "usd", 0, 1e7, section=cx),
            DriverSpec("capex_pos", "POS hardware & smallwares (month 1)", "$", "usd", 0, 1e7, section=cx),
            DriverSpec(
                "capex_refresh", "Equipment refresh per truck per year (from year 2)", "$", "usd", 0, 1e7, section=cx
            ),
        ]

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        if t.granularity == "monthly":
            season = "=IF(OR(MOD({p}-1,12)>=11,MOD({p}-1,12)<=1),1-{in:winter_dip},1+{in:winter_dip}/3)"
        else:
            season = "=1"
        idx = "(1+{in:price_g})^({y}-1)"
        cidx = "(1+{in:cost_g})^({y}-1)"
        ramp = (
            "=IF({in:ramp_months}<=0,1,({ramp_n}*{in:ramp_start}"
            "+(1-{in:ramp_start})/MAX(1,{in:ramp_months})*({ramp_n}*({p}-1)*{mpp}+{ramp_n}*({ramp_n}-1)/2)"
            "+{mpp}-{ramp_n})/{mpp})"
        )
        return [
            Line(
                "trucks_total",
                "Trucks in operation",
                "={in:trucks}+{in:trucks_add}*({y}-1)",
                "top",
                "int",
                agg="last",
                section="Fleet & volume",
            ),
            Line(
                "ramp_n",
                "Helper: months of the period still on the ramp-up",
                "=MAX(0,MIN({mpp},{in:ramp_months}-({p}-1)*{mpp}))",
                "top",
                "dec1",
                agg="none",
            ),
            Line("ramp", "Ramp-up factor (share of mature volume)", ramp, "top", "pct", agg="none"),
            Line("season", "Season factor (winter dip in street days)", season, "top", "dec3", agg="none"),
            Line(
                "street_days",
                "Street service days",
                "={trucks_total}*{in:street_days}*{mpp}*{season}",
                "top",
                "dec1",
            ),
            Line(
                "event_days",
                "Event and catering days",
                "={trucks_total}*{in:events_pm}*(1+{in:events_g})^({y}-1)*{mpp}*{ramp}",
                "top",
                "dec1",
            ),
            Line("service_days", "Service days - total", "={street_days}+{event_days}", "top", "dec1", bold=True),
            Line(
                "meals_street",
                "Meals sold on the street",
                "={street_days}*{in:meals_day}*(1+{in:meals_g})^({y}-1)*{ramp}",
                "top",
                "int",
            ),
            Line("meals_event", "Meals served at events", "={event_days}*{in:event_meals}", "top", "int"),
            Line("meals", "Meals - total", "={meals_street}+{meals_event}", "top", "int", bold=True),
            Line(
                "ticket_now",
                "Average ticket per street meal",
                f"={{in:ticket}}*{idx}",
                "top",
                "usd2",
                agg="last",
                section="Revenue",
            ),
            Line("event_rev_now", "Revenue per event day", f"={{in:event_rev}}*{idx}", "top", "usd", agg="last"),
            Line("rev_street", "Street sales", "={meals_street}*{ticket_now}", "top"),
            Line("rev_event", "Events & catering", "={event_days}*{event_rev_now}", "top"),
            Line("rev", "Revenue", "={rev_street}+{rev_event}", "top", bold=True, total=True),
            Line("food", "Food cost", "=-{rev}*{in:food_pct}", "top", section="Cost of sales"),
            Line("pack_cost", "Packaging & disposables", f"=-{{meals}}*{{in:pack}}*{cidx}", "top"),
            Line("food_pack", "Food & packaging", "={food}+{pack_cost}", "top"),
            Line("card_fees", "Card & POS processing fees", "=-{rev}*{in:card_pct}", "top"),
            Line(
                "event_fees",
                "Event & festival fees",
                f"=-{{rev_event}}*{{in:event_fee_pct}}-{{event_days}}*{{in:event_fee_day}}*{cidx}",
                "top",
            ),
            Line("cogs", "Cost of sales", "={food_pack}+{card_fees}+{event_fees}", "top", bold=True),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        cidx = "(1+{in:cost_g})^({y}-1)"
        return [
            Line(
                "payroll",
                "Payroll (owner-operator, cooks, cashiers)",
                "={payroll_total}",
                "top",
                section="Operating expenses",
            ),
            Line("commissary", "Commissary kitchen", f"=-{{in:commissary}}*{{trucks_total}}*{cidx}*{{mpp}}", "top"),
            Line("permits", "Permits & licences", f"=-{{in:permits}}*{{trucks_total}}*{cidx}*{{mpp}}", "top"),
            Line("insurance", "Insurance", f"=-{{in:insurance}}*{{trucks_total}}*{cidx}*{{mpp}}", "top"),
            Line("fuel", "Fuel, propane & generator", f"=-{{in:fuel}}*{{service_days}}*{cidx}", "top"),
            Line("maint", "Truck maintenance & repairs", f"=-{{in:maint}}*{{trucks_total}}*{cidx}*{{mpp}}", "top"),
            Line("pos_sub", "POS & ordering software", f"=-{{in:pos_sub}}*{cidx}*{{mpp}}", "top"),
            Line("mkt", "Marketing", "=-{in:mkt}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
            Line("ga_other", "Accounting, bank fees & other G&A", f"=-{{in:ga_other}}*{cidx}*{{mpp}}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        later = "AND({y}>1,MOD({p}-1,{ppy})=0)"
        return [
            Line(
                "capex_truck",
                "Truck purchase (month 1; trucks added from year 2)",
                f"=IF({later},{{in:trucks_add}}*{{in:capex_truck}},0)",
                "top",
                first="={in:trucks_new}*{in:capex_truck}",
            ),
            Line(
                "capex_build",
                "Kitchen build-out, equipment & wrap",
                f"=IF({later},{{in:trucks_add}}*{{in:capex_build}},0)",
                "top",
                first="={in:trucks_new}*{in:capex_build}",
            ),
            Line("capex_pos", "POS hardware & smallwares", "=IF({p}=1,{in:capex_pos},0)", "top"),
            Line(
                "capex_refresh",
                "Equipment refresh (first period of each year from year 2)",
                f"=IF({later},{{in:capex_refresh}}*{{trucks_total}},0)",
                "top",
            ),
            Line(
                "capex",
                "Capital spending",
                "={capex_truck}+{capex_build}+{capex_pos}+{capex_refresh}",
                "top",
                bold=True,
            ),
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("meals", "Meals served", "kpi:meals", "int"),
            DashMetric("rev_day", "Revenue per service day", "kpi:rev_day", "usd2"),
            DashMetric("event_share", "Events & catering, % of revenue", "kpi:event_share", "pct"),
            DashMetric("prime", "Prime cost (food, packaging, payroll), % of revenue", "kpi:prime", "pct"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Meals served & prime cost", bars=("meals",), lines=("prime",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("trucks_end", "Trucks in operation (year end)", "line", "trucks_total", "int", bold=True),
            StmtRow("service_days", "Service days (street and events)", "line", "service_days", "int"),
            StmtRow("meals", "Meals served", "line", "meals", "int", bold=True),
            StmtRow(
                "meals_day",
                "Meals per service day",
                "formula",
                "=IF({service_days}=0,0,{meals}/{service_days})",
                "dec1",
            ),
            StmtRow("rev", "Revenue", "line", "rev", bold=True),
            StmtRow("rev_street", "Street sales", "line", "rev_street"),
            StmtRow("rev_event", "Events & catering", "line", "rev_event"),
            StmtRow(
                "event_share", "Events & catering, % of revenue", "formula", "=IF({rev}=0,0,{rev_event}/{rev})", "pct"
            ),
            StmtRow("ticket", "Revenue per meal", "formula", "=IF({meals}=0,0,{rev}/{meals})", "usd2"),
            StmtRow(
                "rev_day", "Revenue per service day", "formula", "=IF({service_days}=0,0,{rev}/{service_days})", "usd2"
            ),
            StmtRow(
                "rev_truck",
                "Revenue per truck (year-end fleet)",
                "formula",
                "=IF({trucks_end}=0,0,{rev}/{trucks_end})",
            ),
            StmtRow("food_pack", "Food & packaging", "line", "food_pack"),
            StmtRow(
                "food_pct", "Food & packaging, % of revenue", "formula", "=IF({rev}=0,0,-{food_pack}/{rev})", "pct"
            ),
            StmtRow("payroll", "Payroll", "line", "payroll_total"),
            StmtRow(
                "prime",
                "Prime cost (food, packaging, payroll), % of revenue",
                "formula",
                "=IF({rev}=0,0,-({food_pack}+{payroll})/{rev})",
                "pct",
            ),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("ebitda", "EBITDA", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
        ]

    def kpi_charts(self, t: Timing) -> list[KpiChart]:
        return [
            KpiChart("Meals served and prime cost", bars=("meals",), lines=("prime",)),
            KpiChart("Revenue by source", bars=("rev_street", "rev_event"), stacked=True),
        ]

    # ------------------------------------------------------------------ python twin
    def kpi_reference(self, ann: dict, d: dict, t: Timing) -> dict:
        out: dict[str, dict] = {k: {} for k in self.kpi_derived}
        for y in range(1, t.years + 1):
            rev, days, meals = ann["rev"][y], ann["service_days"][y], ann["meals"][y]
            out["meals_day"][y] = div(meals, days)
            out["ticket"][y] = div(rev, meals)
            out["rev_day"][y] = div(rev, days)
            out["rev_truck"][y] = div(rev, ann["trucks_total"][y])
            out["event_share"][y] = div(ann["rev_event"][y], rev)
            out["food_pct"][y] = div(-ann["food_pack"][y], rev)
            out["prime"][y] = div(-(ann["food_pack"][y] + ann["payroll_total"][y]), rev)
            out["gm"][y] = div(ann["gp"][y], rev)
            out["em"][y] = div(ann["ebitda"][y], rev)
        return out

    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        idx = (1 + d["price_g"]) ** (y - 1)
        cidx = (1 + d["cost_g"]) ** (y - 1)
        trucks = d["trucks"] + d["trucks_add"] * (y - 1)
        ramp = _ramp(d, p, t)
        street_days = trucks * d["street_days"] * t.mpp * _season(d, p, t)
        event_days = trucks * d["events_pm"] * (1 + d["events_g"]) ** (y - 1) * t.mpp * ramp
        service_days = street_days + event_days
        meals_street = street_days * d["meals_day"] * (1 + d["meals_g"]) ** (y - 1) * ramp
        meals = meals_street + event_days * d["event_meals"]
        rev_street = meals_street * d["ticket"] * idx
        rev_event = event_days * d["event_rev"] * idx
        rev = rev_street + rev_event
        food = -rev * d["food_pct"]
        pack = -meals * d["pack"] * cidx
        event_fees = -rev_event * d["event_fee_pct"] - event_days * d["event_fee_day"] * cidx
        cogs = food + pack - rev * d["card_pct"] + event_fees
        later = y > 1 and (p - 1) % t.ppy == 0
        if p == 1:
            capex = d["trucks_new"] * (d["capex_truck"] + d["capex_build"]) + d["capex_pos"]
        else:
            capex = 0.0
        if later:
            capex += d["trucks_add"] * (d["capex_truck"] + d["capex_build"]) + d["capex_refresh"] * trucks
        return Top(
            rev=rev,
            cogs=cogs,
            opex={
                "payroll": hc.payroll,
                "commissary": -d["commissary"] * trucks * cidx * t.mpp,
                "permits": -d["permits"] * trucks * cidx * t.mpp,
                "insurance": -d["insurance"] * trucks * cidx * t.mpp,
                "fuel": -d["fuel"] * service_days * cidx,
                "maint": -d["maint"] * trucks * cidx * t.mpp,
                "pos_sub": -d["pos_sub"] * cidx * t.mpp,
                "mkt": -d["mkt"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp,
                "ga_other": -d["ga_other"] * cidx * t.mpp,
            },
            capex=capex,
            kpis={
                "trucks_total": trucks,
                "street_days": street_days,
                "event_days": event_days,
                "service_days": service_days,
                "meals_street": meals_street,
                "meals": meals,
                "rev_street": rev_street,
                "rev_event": rev_event,
                "food_pack": food + pack,
                "event_fees": event_fees,
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
                "model_name": f"Food truck financial model ({stage})",
                "template": self.key,
                "business_type": "food_truck",
                "stage": stage,
                "assumption_note": "Illustrative assumptions - replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
