"""Hair salon / barbershop template: chairs × utilisation × hours × services per hour × price.

The salon has a number of styling chairs; a share of them is rented to independent stylists (weekly chair
rent), the rest are worked by employed stylists paid a commission on their service revenue. For the
employed chairs: bookable hours (days open × hours per chair per day) × utilisation (starts at a year-1
level and gains a few points a year up to a ceiling) × services per booked hour × average service price.
Retail products sell on a share of the services (attach rate × average product sale). Cost of sales =
stylist commission (with payroll taxes), product cost, backbar supplies per service and card fees.
Receptionist, assistants and manager come through headcount; capex is the fit-out, styling stations,
backwash units and the stations for chairs added each year.
Assumption memo: docs/templates/salon.md.
"""

from __future__ import annotations

from engine.brief import Brief
from engine.core import HC, Top
from engine.spec import DashChart, DashMetric, DriverSpec, Line, StmtRow, Timing
from engine.templates.base import Template

ROLES = [
    ("manager", "Salon manager"),
    ("reception", "Receptionist"),
    ("assistant", "Shampoo & floor assistants"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer replaces
# them with their own numbers; the assumption memo says which are sourced and which are assumptions.
_COMMON = {
    "rented_share": (0.25, 0.25, 0.25),
    "days_open": (24, 24, 24),
    "hrs_day": (8, 8, 8),
    "util_max": (0.8, 0.8, 0.8),
    "svc_hr": (0.9, 1.0, 1.1),
    "price": (62, 68, 74),
    "price_g": (0.02, 0.03, 0.04),
    "attach": (0.15, 0.2, 0.25),
    "product_ticket": (26, 30, 34),
    "chair_rent_wk": (180, 200, 220),
    "rent_occ": (0.85, 0.9, 0.95),
    "comm_pct": (0.48, 0.45, 0.42),
    "prod_cost_pct": (0.55, 0.5, 0.45),
    "backbar": (4.5, 4.0, 3.5),
    "card_pct": (0.031, 0.029, 0.027),
    "station_cost": (3200, 3200, 3200),
    "wash_cost": (3400, 3400, 3400),
    "payroll_tax": (0.12, 0.12, 0.12),
    "wage_g": (0.03, 0.03, 0.03),
    "ar_days": (2, 2, 2),
    "inv_days": (15, 15, 15),
    "ap_days": (20, 20, 20),
    "dep_years": (7, 7, 7),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "chairs": (8, 8, 8),
            "chairs_add": (0, 0, 0),
            "chairs_equipped": (0, 0, 0),
            "util": (0.38, 0.45, 0.52),
            "util_gain": (0.08, 0.1, 0.12),
            "mkt": (2500, 2500, 2500),
            "mkt_g": (-0.1, 0.0, 0.1),
            "rent": (6500, 6500, 6500),
            "utilities": (900, 900, 900),
            "software": (250, 250, 250),
            "insurance": (650, 650, 650),
            "laundry": (450, 450, 450),
            "ga_other": (700, 700, 700),
            "capex_fitout": (95000, 95000, 95000),
            "wash_new": (2, 2, 2),
            "equity": (150000, 150000, 150000),
            "loan_amount": (70000, 70000, 70000),
            "loan_rate": (0.08, 0.08, 0.08),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {
            "manager": (0.5, 48000, 1, 0.0),
            "reception": (1, 33000, 1, 0.0),
            "assistant": (1, 29000, 1, 0.0),
        },
    },
    "early": {
        "drivers": {
            "chairs": (8, 8, 8),
            "chairs_add": (0, 0, 0),
            "chairs_equipped": (8, 8, 8),
            "util": (0.5, 0.55, 0.6),
            "util_gain": (0.05, 0.07, 0.09),
            "mkt": (2500, 2500, 2500),
            "mkt_g": (-0.1, 0.0, 0.1),
            "rent": (6500, 6500, 6500),
            "utilities": (900, 900, 900),
            "software": (250, 250, 250),
            "insurance": (650, 650, 650),
            "laundry": (450, 450, 450),
            "ga_other": (700, 700, 700),
            "capex_fitout": (15000, 15000, 15000),
            "wash_new": (0, 0, 0),
            "equity": (60000, 60000, 60000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "manager": (0.5, 50000, 1, 0.0),
            "reception": (1, 34000, 1, 0.0),
            "assistant": (1, 30000, 1, 0.0),
        },
    },
    "growing": {
        "drivers": {
            "chairs": (12, 12, 12),
            "chairs_add": (2, 4, 4),
            "chairs_equipped": (12, 12, 12),
            "util": (0.55, 0.6, 0.65),
            "util_gain": (0.03, 0.04, 0.05),
            "mkt": (4000, 4000, 4000),
            "mkt_g": (-0.05, 0.05, 0.1),
            "rent": (10500, 10500, 10500),
            "utilities": (1300, 1300, 1300),
            "software": (350, 350, 350),
            "insurance": (950, 950, 950),
            "laundry": (700, 700, 700),
            "ga_other": (1000, 1000, 1000),
            "capex_fitout": (40000, 40000, 40000),
            "wash_new": (0, 0, 0),
            "equity": (80000, 80000, 80000),
            "loan_amount": (60000, 60000, 60000),
            "loan_rate": (0.08, 0.08, 0.08),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {
            "manager": (1, 52000, 1, 0.0),
            "reception": (1.5, 35000, 1, 0.1),
            "assistant": (2, 31000, 1, 0.1),
        },
    },
    "established": {
        "drivers": {
            "chairs": (16, 16, 16),
            "chairs_add": (0, 0, 0),
            "chairs_equipped": (16, 16, 16),
            "util": (0.6, 0.65, 0.7),
            "util_gain": (0.01, 0.02, 0.03),
            "mkt": (5000, 5000, 5000),
            "mkt_g": (0.0, 0.03, 0.06),
            "rent": (15000, 15000, 15000),
            "utilities": (1800, 1800, 1800),
            "software": (450, 450, 450),
            "insurance": (1400, 1400, 1400),
            "laundry": (1000, 1000, 1000),
            "ga_other": (1500, 1500, 1500),
            "capex_fitout": (30000, 30000, 30000),
            "wash_new": (0, 0, 0),
            "equity": (50000, 50000, 50000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "manager": (1, 56000, 1, 0.0),
            "reception": (2, 36000, 1, 0.03),
            "assistant": (2, 31000, 1, 0.03),
        },
    },
}


class SalonTemplate(Template):
    key = "salon"
    title = "Hair salon / barbershop"
    business_types = ("salon",)
    order = 90
    key_numbers = ("chairs", "util", "price", "comm_pct", "rented_share", "rent", "equity")
    sample_title = "Hair salon"
    sample_desc = "Full workbook with chairs, utilisation, stylist commission, chair rent and retail products"
    sample_stage = "planning"
    kpi_title = "Salon metrics"
    kpi_checked = {
        "chairs_end": "chairs_total",
        "rented_end": "chairs_rented",
        "hours_avail": "hours_avail",
        "hours_booked": "hours_booked",
        "services": "services",
        "rev_svc": "rev_svc",
        "rev_retail": "rev_retail",
        "rev_chair": "rev_chair",
    }
    kpi_flows = ("hours_avail", "hours_booked", "services", "rev_svc", "rev_retail", "rev_chair")

    def driver_specs(self) -> list[DriverSpec]:
        cap, price, retail = "Chairs & booking", "Prices", "Retail products"
        rent, cost, opex, cap_x = "Chair rent", "Cost of sales", "Operating costs", "Capex"
        return [
            DriverSpec("chairs", "Styling chairs at start", "#", "int", 1, 1000, section=cap),
            DriverSpec("chairs_add", "Chairs added each year (from year 2)", "#", "int", 0, 1000, "asc", cap),
            DriverSpec("days_open", "Days open per month", "days", "int", 1, 31, section=cap),
            DriverSpec("hrs_day", "Bookable service hours per chair per day", "hours", "dec1", 0.5, 24, section=cap),
            DriverSpec("util", "Chair utilisation, booked ÷ bookable hours (year 1)", "%", "pct", 0, 1, "asc", cap),
            DriverSpec("util_gain", "Utilisation gain per year (percentage points)", "%", "pct", 0, 1, "asc", cap),
            DriverSpec("util_max", "Utilisation ceiling", "%", "pct", 0.1, 1, section=cap),
            DriverSpec("svc_hr", "Services per booked hour", "#", "dec1", 0.1, 10, "asc", cap),
            DriverSpec("price", "Average service price (year 1)", "$", "usd2", 0, 1e5, "asc", price),
            DriverSpec("price_g", "Price increase per year", "%", "pct", -0.5, 1, "asc", price),
            DriverSpec("attach", "Services with a retail product sale (attach rate)", "%", "pct", 0, 1, "asc", retail),
            DriverSpec("product_ticket", "Average retail product sale (year 1)", "$", "usd2", 0, 1e4, "asc", retail),
            DriverSpec("rented_share", "Chairs rented to independent stylists", "%", "pct", 0, 1, section=rent),
            DriverSpec(
                "chair_rent_wk", "Chair rent per rented chair per week (year 1)", "$", "usd2", 0, 1e5, "asc", rent
            ),
            DriverSpec("rent_occ", "Rented chairs paying rent (occupancy)", "%", "pct", 0, 1, "asc", rent),
            DriverSpec("comm_pct", "Stylist commission, % of service revenue", "%", "pct", 0, 1, "desc", cost),
            DriverSpec("prod_cost_pct", "Retail product cost, % of product sales", "%", "pct", 0, 1, "desc", cost),
            DriverSpec("backbar", "Backbar supplies per service (year 1)", "$", "usd2", 0, 1e4, "desc", cost),
            DriverSpec("card_pct", "Card fees, % of service & product sales", "%", "pct", 0, 0.2, "desc", cost),
            DriverSpec("mkt", "Marketing budget per month (year 1)", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("mkt_g", "Marketing budget growth per year", "%", "pct", -0.9, 5, "asc", opex),
            DriverSpec("rent", "Salon rent per month", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("utilities", "Utilities per month", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("software", "Booking software per month", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("insurance", "Insurance & licences per month", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("laundry", "Towels, laundry & cleaning per month", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("ga_other", "Other G&A per month (accounting, bank, legal)", "$", "usd", 0, 1e7, section=opex),
            DriverSpec("capex_fitout", "Fit-out & refurbishment (month 1)", "$", "usd", 0, 1e8, section=cap_x),
            DriverSpec("station_cost", "Styling station & chair, per chair", "$", "usd", 0, 1e6, section=cap_x),
            DriverSpec("chairs_equipped", "Chairs already equipped at start", "#", "int", 0, 1000, section=cap_x),
            DriverSpec("wash_new", "Backwash units to buy at start", "#", "int", 0, 1000, section=cap_x),
            DriverSpec("wash_cost", "Backwash unit, each", "$", "usd", 0, 1e6, section=cap_x),
        ]

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        idx = "(1+{in:price_g})^({y}-1)"
        return [
            Line(
                "chairs_total",
                "Styling chairs",
                "={in:chairs}+{in:chairs_add}*({y}-1)",
                "top",
                "dec1",
                agg="last",
                section="Chairs & booking",
            ),
            Line(
                "chairs_rented",
                "Chairs rented to independent stylists",
                "={chairs_total}*{in:rented_share}",
                "top",
                "dec1",
                agg="last",
            ),
            Line(
                "chairs_emp",
                "Chairs worked by employed stylists",
                "={chairs_total}-{chairs_rented}",
                "top",
                "dec1",
                agg="last",
            ),
            Line(
                "hours_avail",
                "Bookable chair hours (employed chairs)",
                "={chairs_emp}*{in:days_open}*{in:hrs_day}*{mpp}",
                "top",
                "int",
            ),
            Line(
                "util_now",
                "Chair utilisation",
                "=MIN({in:util_max},{in:util}+{in:util_gain}*({y}-1))",
                "top",
                "pct",
                agg="last",
            ),
            Line("hours_booked", "Booked chair hours", "={hours_avail}*{util_now}", "top", "int"),
            Line("services", "Services performed", "={hours_booked}*{in:svc_hr}", "top", "int", bold=True),
            Line(
                "price_now",
                "Average service price",
                f"={{in:price}}*{idx}",
                "top",
                "usd2",
                agg="last",
                section="Revenue",
            ),
            Line("rev_svc", "Service revenue", "={services}*{price_now}", "top"),
            Line(
                "rev_retail",
                "Retail product sales",
                f"={{services}}*{{in:attach}}*{{in:product_ticket}}*{idx}",
                "top",
            ),
            Line(
                "rev_chair",
                "Chair rent income",
                f"={{chairs_rented}}*{{in:chair_rent_wk}}*52/12*{{mpp}}*{{in:rent_occ}}*{idx}",
                "top",
            ),
            Line("rev", "Revenue", "={rev_svc}+{rev_retail}+{rev_chair}", "top", bold=True, total=True),
            Line(
                "commission",
                "Stylist commission (with payroll taxes)",
                "=-{rev_svc}*{in:comm_pct}*(1+{in:payroll_tax})",
                "top",
                section="Cost of sales",
            ),
            Line("product_cost", "Retail product cost", "=-{rev_retail}*{in:prod_cost_pct}", "top"),
            Line("backbar_cost", "Backbar supplies", f"=-{{services}}*{{in:backbar}}*{idx}", "top"),
            Line("card_fees", "Card fees", "=-({rev_svc}+{rev_retail})*{in:card_pct}", "top"),
            Line(
                "cogs",
                "Cost of sales",
                "={commission}+{product_cost}+{backbar_cost}+{card_fees}",
                "top",
                bold=True,
            ),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "payroll",
                "Staff payroll (manager, reception, assistants)",
                "={payroll_total}",
                "top",
                section="Operating expenses",
            ),
            Line("mkt", "Marketing", "=-{in:mkt}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
            Line("rent", "Salon rent", "=-{in:rent}*{mpp}", "top"),
            Line("utilities", "Utilities", "=-{in:utilities}*{mpp}", "top"),
            Line("software", "Booking software", "=-{in:software}*{mpp}", "top"),
            Line("insurance", "Insurance & licences", "=-{in:insurance}*{mpp}", "top"),
            Line("laundry", "Towels, laundry & cleaning", "=-{in:laundry}*{mpp}", "top"),
            Line("ga_other", "Other G&A", "=-{in:ga_other}*{mpp}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "capex",
                "Capital spending (fit-out, stations, wash units; stations for chairs added)",
                "=IF(AND({y}>1,MOD({p}-1,{ppy})=0),{in:chairs_add}*{in:station_cost},0)",
                "top",
                first=(
                    "={in:capex_fitout}+MAX(0,{in:chairs}-{in:chairs_equipped})*{in:station_cost}"
                    "+{in:wash_new}*{in:wash_cost}"
                ),
            )
        ]

    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("services", "Services performed", "kpi:services", "int"),
            DashMetric("util", "Chair utilisation", "kpi:util", "pct"),
            DashMetric("ticket", "Revenue per service (service revenue ÷ services)", "kpi:ticket", "usd2"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Services performed & chair utilisation", bars=("services",), lines=("util",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("chairs_end", "Styling chairs (year end)", "line", "chairs_total", "dec1", bold=True),
            StmtRow("rented_end", "Chairs rented to independent stylists", "line", "chairs_rented", "dec1"),
            StmtRow("hours_avail", "Bookable chair hours (employed chairs)", "line", "hours_avail", "int"),
            StmtRow("hours_booked", "Booked chair hours", "line", "hours_booked", "int"),
            StmtRow(
                "util",
                "Chair utilisation (booked ÷ bookable hours)",
                "formula",
                "=IF({hours_avail}=0,0,{hours_booked}/{hours_avail})",
                "pct",
            ),
            StmtRow("services", "Services performed", "line", "services", "int", bold=True),
            StmtRow("rev", "Revenue", "line", "rev", bold=True),
            StmtRow("rev_svc", "Service revenue", "line", "rev_svc"),
            StmtRow("ticket", "Revenue per service", "formula", "=IF({services}=0,0,{rev_svc}/{services})", "usd2"),
            StmtRow("rev_retail", "Retail product sales", "line", "rev_retail"),
            StmtRow(
                "retail_share",
                "Retail products, % of service revenue",
                "formula",
                "=IF({rev_svc}=0,0,{rev_retail}/{rev_svc})",
                "pct",
            ),
            StmtRow("rev_chair", "Chair rent income", "line", "rev_chair"),
            StmtRow(
                "rev_emp_chair",
                "Service revenue per employed chair (year-end chairs)",
                "formula",
                "=IF({chairs_end}-{rented_end}=0,0,{rev_svc}/({chairs_end}-{rented_end}))",
            ),
            StmtRow(
                "rent_chair",
                "Chair rent per rented chair per month",
                "formula",
                "=IF({rented_end}=0,0,{rev_chair}/{rented_end}/12)",
                "usd2",
            ),
            StmtRow("gp", "Gross profit", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("ebitda", "EBITDA", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
        ]

    # ------------------------------------------------------------------ python twin
    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        idx = (1 + d["price_g"]) ** (y - 1)
        chairs = d["chairs"] + d["chairs_add"] * (y - 1)
        rented = chairs * d["rented_share"]
        emp = chairs - rented
        hours_avail = emp * d["days_open"] * d["hrs_day"] * t.mpp
        util = min(d["util_max"], d["util"] + d["util_gain"] * (y - 1))
        hours_booked = hours_avail * util
        services = hours_booked * d["svc_hr"]
        rev_svc = services * d["price"] * idx
        rev_retail = services * d["attach"] * d["product_ticket"] * idx
        rev_chair = rented * d["chair_rent_wk"] * 52 / 12 * t.mpp * d["rent_occ"] * idx
        rev = rev_svc + rev_retail + rev_chair
        cogs = (
            -rev_svc * d["comm_pct"] * (1 + d["payroll_tax"])
            - rev_retail * d["prod_cost_pct"]
            - services * d["backbar"] * idx
            - (rev_svc + rev_retail) * d["card_pct"]
        )
        if p == 1:
            capex = (
                d["capex_fitout"]
                + max(0.0, d["chairs"] - d["chairs_equipped"]) * d["station_cost"]
                + d["wash_new"] * d["wash_cost"]
            )
        else:
            capex = d["chairs_add"] * d["station_cost"] if y > 1 and (p - 1) % t.ppy == 0 else 0.0
        return Top(
            rev=rev,
            cogs=cogs,
            opex={
                "payroll": hc.payroll,
                "mkt": -d["mkt"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp,
                "rent": -d["rent"] * t.mpp,
                "utilities": -d["utilities"] * t.mpp,
                "software": -d["software"] * t.mpp,
                "insurance": -d["insurance"] * t.mpp,
                "laundry": -d["laundry"] * t.mpp,
                "ga_other": -d["ga_other"] * t.mpp,
            },
            capex=capex,
            kpis={
                "chairs_total": chairs,
                "chairs_rented": rented,
                "hours_avail": hours_avail,
                "hours_booked": hours_booked,
                "services": services,
                "rev_svc": rev_svc,
                "rev_retail": rev_retail,
                "rev_chair": rev_chair,
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
                "model_name": f"Hair salon financial model ({stage})",
                "template": self.key,
                "business_type": "salon",
                "stage": stage,
                "assumption_note": "Illustrative assumptions — replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
