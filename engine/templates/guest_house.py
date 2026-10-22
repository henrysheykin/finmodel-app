"""Guest house / B&B template: rooms x occupancy x average daily rate, breakfast & extras, annuity property loan.

Room-nights sold = rooms x calendar nights x occupancy. Occupancy = occupancy at maturity x (1 + occupancy growth)
^(year-1) x an opening ramp x, in monthly models, a simple season (June-August busier, the other nine months give it
back, year unchanged), capped at 100%. Room revenue = room-nights x the average daily rate (ADR); breakfast & extras
revenue = occupied room-nights x a spend per night. Stays = room-nights / average length of stay (guarded), and the
cleaning and linen cost is charged per stay. Cost of sales: housekeeping payroll (Headcount sheet), OTA / booking
commission (OTA share of room revenue x commission rate), breakfast food cost, cleaning per stay and guest supplies per
room-night. Operating expenses: host / front-desk / kitchen payroll, rent (0 if owned), property tax, insurance,
utilities, repairs, marketing, other G&A and card fees. Capex: room furnishing and fit-out in month 1, an optional
property purchase (the land share is never depreciated, ADR-011) and an FF&E replacement reserve every period. The
property loan is an annuity (``loan_style``): a level monthly payment, interest on the opening balance.
Assumption memo: docs/templates/guest_house.md.
"""

from __future__ import annotations

from engine.brief import Brief, BriefError
from engine.core import HC, Top, role_period
from engine.spec import DashChart, DashMetric, DriverSpec, KpiChart, Line, StmtRow, Timing
from engine.templates.base import Template, div

HOUSEKEEPER = "housekeeper"
ROLES = [
    (HOUSEKEEPER, "Housekeeping staff"),
    ("host", "Host, manager & front desk"),
    ("kitchen", "Breakfast kitchen & maintenance"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data: the customer replaces
# them with their own numbers; the assumption memo labels every figure as an assumption.
_COMMON = {
    "nights_m": (30.4, 30.4, 30.4),
    "occ_g": (0.0, 0.02, 0.03),
    "peak_uplift": (0.25, 0.25, 0.25),
    "price_g": (0.01, 0.03, 0.04),
    "extras_night": (9, 12, 15),
    "extras_cost_pct": (0.55, 0.5, 0.45),
    "los": (1.8, 2.2, 2.6),
    "clean_stay": (26, 22, 19),
    "supplies_night": (5.0, 4.0, 3.5),
    "ota_share": (0.65, 0.55, 0.45),
    "ota_comm": (0.17, 0.15, 0.14),
    "card_pct": (0.03, 0.027, 0.025),
    "repairs_pct": (0.05, 0.04, 0.035),
    "land_pct": (0.25, 0.25, 0.25),
    "rent_g": (0.03, 0.03, 0.03),
    "cost_g": (0.04, 0.03, 0.025),
    "capex_room": (7500, 7500, 7500),
    "ffe_room": (900, 900, 900),
    "payroll_tax": (0.15, 0.15, 0.15),
    "wage_g": (0.04, 0.03, 0.03),
    "ar_days": (3, 3, 3),
    "inv_days": (3, 3, 3),
    "ap_days": (25, 25, 25),
    "dep_years": (15, 15, 15),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    # buy a house and convert it to a small guest house
    "planning": {
        "drivers": {
            "rooms": (10, 10, 10),
            "occ": (0.5, 0.62, 0.7),
            "ramp_months": (14, 10, 8),
            "ramp_start": (0.3, 0.4, 0.5),
            "adr": (135, 155, 170),
            "rent": (0, 0, 0),
            "prop_tax": (8000, 8000, 8000),
            "insurance": (700, 700, 700),
            "utilities": (1800, 1800, 1800),
            "mkt": (1500, 1500, 1500),
            "mkt_g": (-0.3, -0.2, -0.1),
            "ga_other": (1200, 1200, 1200),
            "capex_buy": (720000, 720000, 720000),
            "capex_fit": (70000, 70000, 70000),
            "equity": (430000, 430000, 430000),
            "loan_amount": (500000, 500000, 500000),
            "loan_rate": (0.07, 0.07, 0.07),
            "loan_term_years": (25, 25, 25),
        },
        "roles": {
            "housekeeper": (1.5, 32000, 1, 0.0),
            "host": (1, 40000, 1, 0.0),
            "kitchen": (0.6, 30000, 1, 0.0),
        },
    },
    # leased building, small fit-out, no loan
    "early": {
        "drivers": {
            "rooms": (10, 10, 10),
            "occ": (0.5, 0.62, 0.7),
            "ramp_months": (6, 4, 3),
            "ramp_start": (0.6, 0.7, 0.8),
            "adr": (135, 155, 170),
            "rent": (6500, 7000, 7000),
            "prop_tax": (0, 0, 0),
            "insurance": (700, 700, 700),
            "utilities": (1800, 1800, 1800),
            "mkt": (1500, 1500, 1500),
            "mkt_g": (-0.1, 0.0, 0.05),
            "ga_other": (1200, 1200, 1200),
            "capex_buy": (0, 0, 0),
            "capex_fit": (25000, 25000, 25000),
            "equity": (200000, 200000, 200000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "housekeeper": (1.5, 32000, 1, 0.0),
            "host": (1, 40000, 1, 0.0),
            "kitchen": (0.6, 30000, 1, 0.0),
        },
    },
    # an operating guest house after an extension, still carrying its mortgage
    "growing": {
        "drivers": {
            "rooms": (12, 12, 12),
            "occ": (0.58, 0.68, 0.74),
            "ramp_months": (0, 0, 0),
            "ramp_start": (1, 1, 1),
            "adr": (135, 155, 170),
            "rent": (0, 0, 0),
            "prop_tax": (11000, 11000, 11000),
            "insurance": (1000, 1000, 1000),
            "utilities": (2600, 2600, 2600),
            "mkt": (2000, 2000, 2000),
            "mkt_g": (0.0, 0.03, 0.06),
            "ga_other": (1800, 1800, 1800),
            "capex_buy": (0, 0, 0),
            "capex_fit": (40000, 40000, 40000),
            "equity": (120000, 120000, 120000),
            "loan_amount": (150000, 150000, 150000),
            "loan_rate": (0.07, 0.07, 0.07),
            "loan_term_years": (15, 15, 15),
        },
        "roles": {
            "housekeeper": (2, 33000, 1, 0.0),
            "host": (1.2, 42000, 1, 0.0),
            "kitchen": (0.9, 31000, 1, 0.0),
        },
    },
    "established": {
        "drivers": {
            "rooms": (14, 14, 14),
            "occ": (0.62, 0.72, 0.78),
            "ramp_months": (0, 0, 0),
            "ramp_start": (1, 1, 1),
            "adr": (140, 160, 175),
            "rent": (0, 0, 0),
            "prop_tax": (13000, 13000, 13000),
            "insurance": (1200, 1200, 1200),
            "utilities": (3000, 3000, 3000),
            "mkt": (2000, 2000, 2000),
            "mkt_g": (0.0, 0.03, 0.06),
            "ga_other": (2000, 2000, 2000),
            "capex_buy": (0, 0, 0),
            "capex_fit": (20000, 20000, 20000),
            "equity": (150000, 150000, 150000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "housekeeper": (2.3, 34000, 1, 0.0),
            "host": (1.4, 44000, 1, 0.0),
            "kitchen": (1, 32000, 1, 0.0),
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
    """Season (model month 1 = January): June-August get +uplift, the other nine months give back uplift/3,
    so the year is unchanged. Annual models use 1."""
    if t.granularity != "monthly":
        return 1.0
    m = (p - 1) % 12  # 0 = January
    up = d["peak_uplift"]
    return 1 + up if m in (5, 6, 7) else 1 - up / 3


class GuestHouseTemplate(Template):
    key = "guest_house"
    title = "Guest house / B&B"
    business_types = ("guest_house",)
    order = 140
    key_numbers = ("rooms", "adr", "occ", "capex_buy", "loan_amount", "loan_rate", "equity")
    sample_title = "Guest house / B&B"
    sample_desc = "Full workbook with rooms, occupancy, daily rate, breakfast, cleaning per stay and the property loan"
    sample_stage = "planning"
    loan_style = "annuity"
    kpi_title = "Guest house metrics"
    kpi_checked = {
        "nights": "room_nights",
        "avail_n": "avail_nights",
        "stays": "stays",
        "rev_room": "rev_room",
        "rev_extras": "rev_extras",
        "rev": "rev",
        "gp": "gp",
        "ebitda": "ebitda",
    }
    kpi_derived = ("occ_rate", "adr_eff", "revpar", "trevpar", "extras_share", "rev_stay", "gm", "em")
    kpi_flows = ("room_nights", "avail_nights", "stays", "rev_room", "rev_extras")

    def driver_specs(self) -> list[DriverSpec]:
        rm, pr, cs, fx, cx = (
            "Rooms & occupancy",
            "Rates & extras",
            "Cost of sales",
            "Property costs",
            "Capital spending",
        )
        return [
            DriverSpec("rooms", "Lettable rooms", "rooms", "int", 1, 1000, section=rm, integer=True),
            DriverSpec("occ", "Average occupancy at maturity, % of room-nights (year 1)", "%", "pct", 0, 1, "asc", rm),
            DriverSpec("occ_g", "Occupancy growth per year (capped at 100%)", "%", "pct", -0.9, 5, "asc", rm),
            DriverSpec(
                "ramp_months",
                "Months to reach mature occupancy (0 = already mature)",
                "months",
                "int",
                0,
                60,
                "desc",
                rm,
                integer=True,
            ),
            DriverSpec("ramp_start", "Occupancy in month 1, % of mature", "%", "pct", 0, 1, "asc", rm),
            DriverSpec(
                "peak_uplift",
                "Peak-season uplift, June-August (monthly models)",
                "%",
                "pct",
                0,
                1,
                section=rm,
            ),
            DriverSpec("nights_m", "Calendar nights per month", "nights", "dec1", 28, 31, section=rm),
            DriverSpec("los", "Average length of stay", "nights", "dec1", 0.5, 60, "asc", rm),
            DriverSpec("adr", "Average daily rate per occupied room (year 1)", "$", "usd2", 0, 1e5, "asc", pr),
            DriverSpec("price_g", "Rate increase per year (rooms and extras)", "%", "pct", -0.5, 1, "asc", pr),
            DriverSpec(
                "extras_night",
                "Breakfast & extras revenue per occupied room-night (year 1)",
                "$",
                "usd2",
                0,
                1e4,
                "asc",
                pr,
            ),
            DriverSpec("extras_cost_pct", "Breakfast & extras cost, % of that revenue", "%", "pct", 0, 1, "desc", cs),
            DriverSpec("clean_stay", "Cleaning & linen per stay (year 1)", "$", "usd2", 0, 1e4, "desc", cs),
            DriverSpec(
                "supplies_night", "Guest supplies per occupied room-night (year 1)", "$", "usd2", 0, 1e4, "desc", cs
            ),
            DriverSpec("ota_share", "Share of room revenue booked through OTAs", "%", "pct", 0, 1, "desc", cs),
            DriverSpec("ota_comm", "OTA / booking commission, % of OTA room revenue", "%", "pct", 0, 1, "desc", cs),
            DriverSpec("rent", "Building rent per month (0 = owned property)", "$", "usd", 0, 1e7, section=fx),
            DriverSpec("rent_g", "Rent increase per year", "%", "pct", 0, 0.5, section=fx),
            DriverSpec(
                "prop_tax", "Property tax per year (0 if leased or included in rent)", "$", "usd", 0, 1e7, section=fx
            ),
            DriverSpec("insurance", "Insurance (property, liability) per month", "$", "usd", 0, 1e7, section=fx),
            DriverSpec("utilities", "Utilities per month", "$", "usd", 0, 1e7, section=fx),
            DriverSpec("repairs_pct", "Repairs & maintenance, % of revenue", "%", "pct", 0, 0.5, "desc", fx),
            DriverSpec("ga_other", "Software, accounting & other G&A per month", "$", "usd", 0, 1e7, section=fx),
            DriverSpec("mkt", "Marketing budget per month (year 1)", "$", "usd", 0, 1e7, section=fx),
            DriverSpec("mkt_g", "Marketing budget growth per year", "%", "pct", -0.9, 5, "asc", fx),
            DriverSpec("card_pct", "Card processing fees, % of revenue", "%", "pct", 0, 0.2, "desc", fx),
            DriverSpec(
                "cost_g",
                "Cost increase per year (insurance, utilities, supplies, cleaning, tax)",
                "%",
                "pct",
                -0.5,
                1,
                "desc",
                fx,
            ),
            DriverSpec(
                "capex_buy",
                "Property purchase (month 1; 0 = leased building)",
                "$",
                "usd",
                0,
                1e9,
                section=cx,
            ),
            DriverSpec(
                "land_pct",
                "Land share of the property purchase (never depreciated)",
                "%",
                "pct",
                0,
                0.95,
                section=cx,
            ),
            DriverSpec(
                "capex_room", "Furnishing & bathroom fit-out per room (month 1)", "$", "usd", 0, 1e7, section=cx
            ),
            DriverSpec(
                "capex_fit", "Building works, kitchen, signage & systems (month 1)", "$", "usd", 0, 1e8, section=cx
            ),
            DriverSpec("ffe_room", "FF&E replacement per room per year", "$", "usd", 0, 1e6, section=cx),
        ]

    def validate(self, brief: Brief) -> None:
        if HOUSEKEEPER not in {r.key for r in brief.roles}:
            raise BriefError("template 'guest_house' needs the 'housekeeper' (housekeeping staff) role")
        super().validate(brief)

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        if t.granularity == "monthly":
            season = "=IF(AND(MOD({p}-1,12)>=5,MOD({p}-1,12)<=7),1+{in:peak_uplift},1-{in:peak_uplift}/3)"
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
                "ramp_n",
                "Helper: months of the period still on the opening ramp",
                "=MAX(0,MIN({mpp},{in:ramp_months}-({p}-1)*{mpp}))",
                "top",
                "dec1",
                agg="none",
                section="Rooms & occupancy",
            ),
            Line("ramp", "Opening ramp factor (share of mature occupancy)", ramp, "top", "pct", agg="none"),
            Line("season", "Season factor (June-August)", season, "top", "dec3", agg="none"),
            Line(
                "avail_nights",
                "Available room-nights (rooms × calendar nights)",
                "={in:rooms}*{in:nights_m}*{mpp}",
                "top",
                "int",
            ),
            Line(
                "occ_eff",
                "Occupancy (maturity × growth × ramp × season, capped at 100%)",
                "=MIN(1,{in:occ}*(1+{in:occ_g})^({y}-1)*{ramp}*{season})",
                "top",
                "pct",
                agg="none",
            ),
            Line("room_nights", "Occupied room-nights", "={avail_nights}*{occ_eff}", "top", "int", bold=True),
            Line(
                "stays",
                "Guest stays (room-nights ÷ average length of stay)",
                "=IF({in:los}<=0,0,{room_nights}/{in:los})",
                "top",
                "int",
            ),
            Line(
                "adr_now",
                "Average daily rate",
                f"={{in:adr}}*{idx}",
                "top",
                "usd2",
                agg="last",
                section="Revenue",
            ),
            Line("rev_room", "Room revenue", "={room_nights}*{adr_now}", "top"),
            Line("rev_extras", "Breakfast & extras revenue", f"={{room_nights}}*{{in:extras_night}}*{idx}", "top"),
            Line("rev", "Revenue", "={rev_room}+{rev_extras}", "top", bold=True, total=True),
            Line(
                "cost_housekeeping",
                "Housekeeping payroll",
                "={hc_housekeeper_cost}",
                "top",
                section="Cost of sales",
            ),
            Line("ota_fees", "OTA / booking commission", "=-{rev_room}*{in:ota_share}*{in:ota_comm}", "top"),
            Line("extras_cost", "Breakfast & extras cost", "=-{rev_extras}*{in:extras_cost_pct}", "top"),
            Line("cleaning", "Cleaning & linen (per stay)", f"=-{{stays}}*{{in:clean_stay}}*{cidx}", "top"),
            Line("supplies", "Guest supplies", f"=-{{room_nights}}*{{in:supplies_night}}*{cidx}", "top"),
            Line(
                "cogs",
                "Cost of sales",
                "={cost_housekeeping}+{ota_fees}+{extras_cost}+{cleaning}+{supplies}",
                "top",
                bold=True,
            ),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        cidx = "(1+{in:cost_g})^({y}-1)"
        return [
            Line(
                "payroll_nb",
                "Host, front desk, kitchen & maintenance payroll",
                "={payroll_total}-{hc_housekeeper_cost}",
                "top",
                section="Operating expenses",
            ),
            Line("rent", "Building rent", "=-{in:rent}*(1+{in:rent_g})^({y}-1)*{mpp}", "top"),
            Line("prop_tax", "Property tax", f"=-{{in:prop_tax}}/12*{cidx}*{{mpp}}", "top"),
            Line("insurance", "Insurance", f"=-{{in:insurance}}*{cidx}*{{mpp}}", "top"),
            Line("utilities", "Utilities", f"=-{{in:utilities}}*{cidx}*{{mpp}}", "top"),
            Line("repairs", "Repairs & maintenance", "=-{rev}*{in:repairs_pct}", "top"),
            Line("mkt", "Marketing", "=-{in:mkt}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
            Line("ga_other", "Software, accounting & other G&A", f"=-{{in:ga_other}}*{cidx}*{{mpp}}", "top"),
            Line("card_fees", "Card processing fees", "=-{rev}*{in:card_pct}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [
            Line("capex_buy", "Property purchase", "=IF({p}=1,{in:capex_buy},0)", "top"),
            Line("capex_land", "of which land (not depreciated)", "=IF({p}=1,{in:capex_buy}*{in:land_pct},0)", "top"),
            Line("capex_rooms", "Room furnishing & fit-out", "=IF({p}=1,{in:rooms}*{in:capex_room},0)", "top"),
            Line("capex_fit", "Building works, kitchen & signage", "=IF({p}=1,{in:capex_fit},0)", "top"),
            Line(
                "capex_ffe",
                "FF&E replacement",
                "={in:rooms}*{in:ffe_room}/12*(1+{in:cost_g})^({y}-1)*{mpp}",
                "top",
            ),
            Line(
                "capex",
                "Capital spending",
                "={capex_buy}+{capex_rooms}+{capex_fit}+{capex_ffe}",
                "top",
                bold=True,
            ),
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("occ_rate", "Occupancy", "kpi:occ_rate", "pct"),
            DashMetric("adr_eff", "Average daily rate", "kpi:adr_eff", "usd2"),
            DashMetric("revpar", "RevPAR (room revenue per available room-night)", "kpi:revpar", "usd2"),
            DashMetric("stays", "Guest stays", "kpi:stays", "int"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Room-nights sold & occupancy", bars=("stays",), lines=("occ_rate",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("avail_n", "Available room-nights", "line", "avail_nights", "int"),
            StmtRow("nights", "Occupied room-nights", "line", "room_nights", "int", bold=True),
            StmtRow("occ_rate", "Occupancy", "formula", "=IF({avail_n}=0,0,{nights}/{avail_n})", "pct"),
            StmtRow("stays", "Guest stays", "line", "stays", "int"),
            StmtRow("rev", "Revenue", "line", "rev", bold=True),
            StmtRow("rev_room", "Room revenue", "line", "rev_room"),
            StmtRow("rev_extras", "Breakfast & extras revenue", "line", "rev_extras"),
            StmtRow("extras_share", "Extras share of revenue", "formula", "=IF({rev}=0,0,{rev_extras}/{rev})", "pct"),
            StmtRow(
                "adr_eff",
                "Average daily rate (room revenue ÷ occupied room-nights)",
                "formula",
                "=IF({nights}=0,0,{rev_room}/{nights})",
                "usd2",
            ),
            StmtRow(
                "revpar",
                "RevPAR (room revenue ÷ available room-nights)",
                "formula",
                "=IF({avail_n}=0,0,{rev_room}/{avail_n})",
                "usd2",
            ),
            StmtRow(
                "trevpar",
                "Total revenue per available room-night",
                "formula",
                "=IF({avail_n}=0,0,{rev}/{avail_n})",
                "usd2",
            ),
            StmtRow("rev_stay", "Revenue per stay", "formula", "=IF({stays}=0,0,{rev}/{stays})", "usd2"),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("ebitda", "EBITDA", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
        ]

    def kpi_charts(self, t: Timing) -> list[KpiChart]:
        return [
            KpiChart("Occupied room-nights and occupancy", bars=("nights",), lines=("occ_rate",)),
            KpiChart("ADR and RevPAR", bars=("adr_eff", "revpar"), lines=("em",)),
        ]

    # ------------------------------------------------------------------ python twin
    def kpi_reference(self, ann: dict, d: dict, t: Timing) -> dict:
        out: dict[str, dict] = {k: {} for k in self.kpi_derived}
        for y in range(1, t.years + 1):
            rev, nights, avail = ann["rev"][y], ann["room_nights"][y], ann["avail_nights"][y]
            out["occ_rate"][y] = div(nights, avail)
            out["adr_eff"][y] = div(ann["rev_room"][y], nights)
            out["revpar"][y] = div(ann["rev_room"][y], avail)
            out["trevpar"][y] = div(rev, avail)
            out["extras_share"][y] = div(ann["rev_extras"][y], rev)
            out["rev_stay"][y] = div(rev, ann["stays"][y])
            out["gm"][y] = div(ann["gp"][y], rev)
            out["em"][y] = div(ann["ebitda"][y], rev)
        return out

    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        _, hk_cost = role_period(d, HOUSEKEEPER, p, t)
        avail = d["rooms"] * d["nights_m"] * t.mpp
        occ = min(1.0, d["occ"] * (1 + d["occ_g"]) ** (y - 1) * _ramp(d, p, t) * _season(d, p, t))
        nights = avail * occ
        stays = 0.0 if d["los"] <= 0 else nights / d["los"]
        idx = (1 + d["price_g"]) ** (y - 1)
        cidx = (1 + d["cost_g"]) ** (y - 1)
        rev_room = nights * d["adr"] * idx
        rev_extras = nights * d["extras_night"] * idx
        rev = rev_room + rev_extras
        cogs = (
            hk_cost
            - rev_room * d["ota_share"] * d["ota_comm"]
            - rev_extras * d["extras_cost_pct"]
            - stays * d["clean_stay"] * cidx
            - nights * d["supplies_night"] * cidx
        )
        buy = d["capex_buy"] if p == 1 else 0.0
        capex = buy + d["rooms"] * d["ffe_room"] / 12 * cidx * t.mpp
        if p == 1:
            capex += d["rooms"] * d["capex_room"] + d["capex_fit"]
        return Top(
            rev=rev,
            cogs=cogs,
            opex={
                "payroll_nb": hc.payroll - hk_cost,
                "rent": -d["rent"] * (1 + d["rent_g"]) ** (y - 1) * t.mpp,
                "prop_tax": -d["prop_tax"] / 12 * cidx * t.mpp,
                "insurance": -d["insurance"] * cidx * t.mpp,
                "utilities": -d["utilities"] * cidx * t.mpp,
                "repairs": -rev * d["repairs_pct"],
                "mkt": -d["mkt"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp,
                "ga_other": -d["ga_other"] * cidx * t.mpp,
                "card_fees": -rev * d["card_pct"],
            },
            capex=capex,
            land=buy * d["land_pct"],
            kpis={
                "room_nights": nights,
                "avail_nights": avail,
                "stays": stays,
                "rev_room": rev_room,
                "rev_extras": rev_extras,
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
                "model_name": f"Guest house financial model ({stage})",
                "template": self.key,
                "business_type": "guest_house",
                "stage": stage,
                "assumption_note": "Illustrative assumptions - replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
