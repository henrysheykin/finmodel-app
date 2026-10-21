"""Dental practice template: chair capacity and patient base → production → collections.

General and family dental practices. Active patients open at the current base; each period new patients join
(marketing budget ÷ cost per new patient, plus referrals & walk-ins) and a monthly share is lost. Two production
streams:

* doctor visits = the lower of demand (treatment visits per active patient + the new-patient exam and first
  treatment) and chair capacity (operatories × visits per chair per day × working days);
* hygiene recall visits = the lower of demand (active patients × recall visits per year) and hygienist capacity
  (hygienist FTE, limited by hygiene operatories, × visits per day × working days).

Production is gross (office fees). Revenue = collections = production less the PPO fee-schedule write-off (insurance
mix) and the share never collected. Cost of sales: supplies, lab fees, card fees. The associate dentist is paid a
share of the collections he or she produces; everyone else is payroll through roles.
Assumption memo: docs/templates/dental.md.
"""

from __future__ import annotations

from engine.brief import Brief, BriefError
from engine.core import HC, Top, role_period
from engine.spec import DashChart, DashMetric, DriverSpec, KpiChart, Line, StmtRow, Timing
from engine.templates.base import Template, div

HYG = "hyg"
ROLES = [
    ("owner", "Owner dentist"),
    (HYG, "Hygienists"),
    ("asst", "Dental assistants"),
    ("front", "Front desk"),
    ("mgr", "Office manager"),
]

# Illustrative defaults per wizard stage: (low, base, high). Not market data — the customer replaces
# them with their own numbers; the assumption memo says so.
_COMMON = {
    "visits_chair": (3.8, 4.0, 4.2),
    "hyg_per_day": (7.5, 8, 8.5),
    "work_days": (18, 18, 18),
    "doc_visits": (1.1, 1.15, 1.2),
    "recall": (1.4, 1.5, 1.6),
    "np_visits": (1, 1, 1),
    "fee_doc": (320, 330, 340),
    "fee_hyg": (195, 200, 205),
    "price_g": (0.02, 0.03, 0.04),
    "ppo_share": (0.6, 0.55, 0.5),
    "ppo_disc": (0.27, 0.25, 0.23),
    "bad_debt": (0.02, 0.015, 0.01),
    "assoc_pct": (0.32, 0.3, 0.28),
    "card_pct": (0.014, 0.012, 0.01),
    "capex_op": (45000, 45000, 45000),
    "refresh_pct": (0.015, 0.015, 0.015),
    "payroll_tax": (0.1, 0.1, 0.1),
    "wage_g": (0.03, 0.03, 0.03),
    "ar_days": (22, 17, 14),
    "inv_days": (12, 12, 12),
    "ap_days": (25, 25, 25),
    "dep_years": (7, 7, 7),
    "tax_rate": (0.21, 0.21, 0.21),
}
# roles: key -> (fte, salary per year, first month, headcount growth per year)
_STAGES: dict[str, dict] = {
    "planning": {
        "drivers": {
            "ops": (3, 3, 3),
            "hyg_ops": (2, 2, 2),
            "sqft": (1800, 1800, 1800),
            "fit_psf": (110, 110, 110),
            "rent_psf": (32, 30, 28),
            "pat_start": (100, 150, 200),
            "ref_new": (14, 18, 22),
            "ref_g": (0.2, 0.3, 0.4),
            "mkt": (8000, 8000, 8000),
            "mkt_g": (-0.1, 0.0, 0.1),
            "cpnp": (240, 220, 200),
            "attr_m": (0.018, 0.015, 0.013),
            "assoc_share": (0, 0, 0),
            "supplies_pct": (0.055, 0.05, 0.047),
            "lab_pct": (0.11, 0.1, 0.09),
            "utilities": (900, 900, 900),
            "software": (700, 700, 700),
            "malpractice": (450, 450, 450),
            "maint": (700, 700, 700),
            "ga_other": (1500, 1500, 1500),
            "ops_equipped": (0, 0, 0),
            "capex_img": (70000, 70000, 70000),
            "equity": (400000, 400000, 400000),
            "loan_amount": (450000, 450000, 450000),
            "loan_rate": (0.09, 0.09, 0.09),
            "loan_term_years": (10, 10, 10),
        },
        "roles": {
            "owner": (1, 120000, 1, 0.0),
            HYG: (0.6, 95000, 3, 0.6),
            "asst": (1.5, 44000, 1, 0.3),
            "front": (1, 40000, 1, 0.3),
            "mgr": (0, 65000, 1, 0.0),
        },
    },
    "early": {
        "drivers": {
            "ops": (4, 4, 4),
            "hyg_ops": (3, 3, 3),
            "sqft": (2600, 2600, 2600),
            "fit_psf": (0, 0, 0),
            "rent_psf": (32, 30, 28),
            "pat_start": (1300, 1500, 1700),
            "ref_new": (16, 20, 24),
            "ref_g": (0.05, 0.1, 0.15),
            "mkt": (5500, 5500, 5500),
            "mkt_g": (-0.05, 0.0, 0.05),
            "cpnp": (240, 220, 200),
            "attr_m": (0.017, 0.015, 0.013),
            "assoc_share": (0.2, 0.2, 0.2),
            "supplies_pct": (0.055, 0.05, 0.047),
            "lab_pct": (0.11, 0.1, 0.09),
            "utilities": (1200, 1200, 1200),
            "software": (900, 900, 900),
            "malpractice": (650, 650, 650),
            "maint": (900, 900, 900),
            "ga_other": (2000, 2000, 2000),
            "ops_equipped": (7, 7, 7),
            "capex_img": (30000, 30000, 30000),
            "equity": (100000, 100000, 100000),
            "loan_amount": (60000, 60000, 60000),
            "loan_rate": (0.09, 0.09, 0.09),
            "loan_term_years": (5, 5, 5),
        },
        "roles": {
            "owner": (1, 150000, 1, 0.0),
            HYG: (1.5, 95000, 1, 0.15),
            "asst": (2.5, 44000, 1, 0.15),
            "front": (1.5, 40000, 1, 0.15),
            "mgr": (0.5, 65000, 1, 0.0),
        },
    },
    "growing": {
        "drivers": {
            "ops": (6, 6, 6),
            "hyg_ops": (4, 4, 4),
            "sqft": (4000, 4000, 4000),
            "fit_psf": (0, 0, 0),
            "rent_psf": (32, 30, 28),
            "pat_start": (2700, 3000, 3300),
            "ref_new": (20, 24, 28),
            "ref_g": (0.03, 0.06, 0.09),
            "mkt": (7000, 7000, 7000),
            "mkt_g": (0.0, 0.05, 0.1),
            "cpnp": (230, 210, 190),
            "attr_m": (0.016, 0.014, 0.012),
            "assoc_share": (0.4, 0.4, 0.4),
            "supplies_pct": (0.054, 0.049, 0.046),
            "lab_pct": (0.108, 0.098, 0.088),
            "utilities": (1800, 1800, 1800),
            "software": (1300, 1300, 1300),
            "malpractice": (1100, 1100, 1100),
            "maint": (1400, 1400, 1400),
            "ga_other": (3000, 3000, 3000),
            "ops_equipped": (10, 10, 10),
            "capex_img": (60000, 60000, 60000),
            "equity": (100000, 100000, 100000),
            "loan_amount": (150000, 150000, 150000),
            "loan_rate": (0.085, 0.085, 0.085),
            "loan_term_years": (7, 7, 7),
        },
        "roles": {
            "owner": (1, 180000, 1, 0.0),
            HYG: (3, 96000, 1, 0.06),
            "asst": (4.5, 45000, 1, 0.04),
            "front": (3, 41000, 1, 0.04),
            "mgr": (1, 68000, 1, 0.0),
        },
    },
    "established": {
        "drivers": {
            "ops": (8, 8, 8),
            "hyg_ops": (5, 5, 5),
            "sqft": (5200, 5200, 5200),
            "fit_psf": (0, 0, 0),
            "rent_psf": (32, 30, 28),
            "pat_start": (3900, 4200, 4500),
            "ref_new": (15, 20, 25),
            "ref_g": (0.02, 0.03, 0.04),
            "mkt": (8000, 8000, 8000),
            "mkt_g": (0.0, 0.03, 0.06),
            "cpnp": (220, 200, 180),
            "attr_m": (0.015, 0.013, 0.011),
            "assoc_share": (0.55, 0.55, 0.55),
            "supplies_pct": (0.052, 0.047, 0.044),
            "lab_pct": (0.105, 0.095, 0.085),
            "utilities": (2300, 2300, 2300),
            "software": (1700, 1700, 1700),
            "malpractice": (1500, 1500, 1500),
            "maint": (1800, 1800, 1800),
            "ga_other": (4000, 4000, 4000),
            "ops_equipped": (13, 13, 13),
            "capex_img": (0, 0, 0),
            "equity": (150000, 150000, 150000),
            "loan_amount": (0, 0, 0),
            "loan_rate": (0, 0, 0),
            "loan_term_years": (1, 1, 1),
        },
        "roles": {
            "owner": (1, 200000, 1, 0.0),
            HYG: (4, 98000, 1, 0.03),
            "asst": (5.5, 46000, 1, 0.02),
            "front": (3, 42000, 1, 0.02),
            "mgr": (1, 72000, 1, 0.0),
        },
    },
}


class DentalTemplate(Template):
    key = "dental"
    title = "Dental practice"
    business_types = ("dental",)
    order = 100
    key_numbers = ("pat_start", "ops", "fee_doc", "recall", "cpnp", "rent_psf", "equity")
    sample_title = "Dental practice"
    sample_desc = "Full workbook with chairs, active patients, hygiene recall, insurance write-offs and collections"
    sample_stage = "growing"
    kpi_title = "Dental practice metrics"
    kpi_checked = {
        "pat_end": "pat_close",
        "new_p": "new_total",
        "lost_p": "lost",
        "new_paid": "new_mkt",
        "visits_doc": "visits_doc",
        "cap_doc": "cap_doc",
        "visits_hyg": "visits_hyg",
        "cap_hyg": "cap_hyg",
        "prod": "prod",
        "prod_hyg": "prod_hyg",
        "rev": "rev",
        "gp": "gp",
        "ebitda": "ebitda",
    }
    kpi_derived = (
        "util_doc",
        "util_hyg",
        "hyg_share",
        "coll_rate",
        "prod_visit",
        "cac",
        "rev_pat",
        "rev_op",
        "gm",
        "em",
        "rev_sqft",
    )
    kpi_flows = (
        "new_total",
        "lost",
        "new_mkt",
        "visits_doc",
        "cap_doc",
        "visits_hyg",
        "cap_hyg",
        "prod",
        "prod_hyg",
    )

    def driver_specs(self) -> list[DriverSpec]:
        cap, pat, fee, ins = "Chairs & schedule", "Patients", "Fees", "Insurance & collections"
        cost, space, cx = "Costs", "Space", "Capex"
        return [
            DriverSpec("ops", "Doctor operatories (restorative chairs)", "#", "int", 0, 200, section=cap),
            DriverSpec("hyg_ops", "Hygiene operatories", "#", "int", 0, 200, section=cap),
            DriverSpec(
                "visits_chair", "Doctor visits per operatory per working day", "visits", "dec1", 0, 30, "asc", cap
            ),
            DriverSpec(
                "hyg_per_day", "Hygiene visits per hygienist per working day", "visits", "dec1", 0, 30, "asc", cap
            ),
            DriverSpec("work_days", "Working days per month", "days", "int", 1, 31, "asc", cap),
            DriverSpec("pat_start", "Active patients at start", "#", "int", 0, 1e6, "asc", pat),
            DriverSpec(
                "ref_new", "Referral & walk-in new patients per month (year 1)", "#", "dec1", 0, 1e5, "asc", pat
            ),
            DriverSpec("ref_g", "Referral & walk-in new patients growth per year", "%", "pct", -0.9, 5, "asc", pat),
            DriverSpec("mkt", "Marketing budget per month (year 1)", "$", "usd", 0, 1e7, section=pat),
            DriverSpec("mkt_g", "Marketing budget growth per year", "%", "pct", -0.9, 5, "asc", pat),
            DriverSpec("cpnp", "Marketing cost per new patient", "$", "usd2", 0, 1e5, "desc", pat),
            DriverSpec("attr_m", "Active patients lost per month", "%", "pct", 0, 1, "desc", pat),
            DriverSpec("doc_visits", "Doctor visits per active patient per year", "visits", "dec1", 0, 50, "asc", pat),
            DriverSpec(
                "recall", "Hygiene recall visits per active patient per year", "visits", "dec1", 0, 12, "asc", pat
            ),
            DriverSpec(
                "np_visits",
                "Doctor visits per new patient in the period they join",
                "visits",
                "dec1",
                0,
                20,
                "asc",
                pat,
            ),
            DriverSpec("fee_doc", "Production per doctor visit, office fees (year 1)", "$", "usd2", 0, 1e5, "asc", fee),
            DriverSpec(
                "fee_hyg", "Production per hygiene visit, office fees (year 1)", "$", "usd2", 0, 1e5, "asc", fee
            ),
            DriverSpec("price_g", "Fee increase per year", "%", "pct", -0.5, 1, "asc", fee),
            DriverSpec(
                "ppo_share", "Production from in-network insurance (PPO) patients", "%", "pct", 0, 1, "desc", ins
            ),
            DriverSpec("ppo_disc", "PPO fee-schedule write-off, % of PPO production", "%", "pct", 0, 1, "desc", ins),
            DriverSpec(
                "bad_debt", "Production never collected (bad debt), % of net production", "%", "pct", 0, 1, "desc", ins
            ),
            DriverSpec("supplies_pct", "Dental supplies, % of gross production", "%", "pct", 0, 1, "desc", cost),
            DriverSpec("lab_pct", "Lab fees, % of doctor production", "%", "pct", 0, 1, "desc", cost),
            DriverSpec("card_pct", "Card & payment processing, % of collections", "%", "pct", 0, 0.2, "desc", cost),
            DriverSpec("assoc_share", "Doctor visits seen by associate dentists", "%", "pct", 0, 1, section=cost),
            DriverSpec("assoc_pct", "Associate pay, % of the collections they produce", "%", "pct", 0, 1, "desc", cost),
            DriverSpec("utilities", "Utilities & phone per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("software", "Practice software & IT per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec("malpractice", "Malpractice & liability insurance per month", "$", "usd", 0, 1e7, section=cost),
            DriverSpec(
                "maint", "Equipment maintenance, cleaning & compliance per month", "$", "usd", 0, 1e7, section=cost
            ),
            DriverSpec(
                "ga_other", "Other G&A per month (accounting, legal, licences, CE)", "$", "usd", 0, 1e7, section=cost
            ),
            DriverSpec("sqft", "Practice size", "sq ft", "int", 1, 1e7, section=space),
            DriverSpec("rent_psf", "Rent per sq ft per year (incl. CAM)", "$", "usd2", 0, 1e4, "desc", space),
            DriverSpec(
                "fit_psf",
                "Fit-out cost per sq ft, net of landlord allowance (month 1)",
                "$",
                "usd2",
                0,
                1e4,
                section=cx,
            ),
            DriverSpec(
                "capex_op", "Equipment per operatory (chair, unit, light, cabinetry)", "$", "usd", 0, 1e7, section=cx
            ),
            DriverSpec("ops_equipped", "Operatories already equipped at start", "#", "int", 0, 400, section=cx),
            DriverSpec(
                "capex_img", "Imaging & IT (x-ray, panoramic / CBCT, scanner) (month 1)", "$", "usd", 0, 1e8, section=cx
            ),
            DriverSpec(
                "refresh_pct", "Equipment refresh & technology, % of collections", "%", "pct", 0, 0.5, "desc", cx
            ),
        ]

    def validate(self, brief: Brief) -> None:
        if HYG not in {r.key for r in brief.roles}:
            raise BriefError("template 'dental' needs the 'hyg' (hygienists) role")
        super().validate(brief)

    # ------------------------------------------------------------------ formula lines
    def revenue_lines(self, t: Timing) -> list[Line]:
        if t.granularity == "monthly":
            close = "={pat_open}*(1-{in:attr_m})+{new_total}"
        else:  # monthly loss compounded over 12 months; the year's new patients join mid-year
            close = "={pat_open}*(1-{in:attr_m})^12+{new_total}*(1-{in:attr_m})^6"
        idx = "(1+{in:price_g})^({y}-1)"
        return [
            Line(
                "new_mkt",
                "New patients from marketing",
                "=-{mkt}/MAX(1,{in:cpnp})",
                "top",
                "dec1",
                section="Patients",
            ),
            Line(
                "new_ref",
                "New patients from referrals & walk-ins",
                "={in:ref_new}*(1+{in:ref_g})^({y}-1)*{mpp}",
                "top",
                "dec1",
            ),
            Line("new_total", "New patients — total", "={new_mkt}+{new_ref}", "top", "dec1", bold=True),
            Line(
                "pat_open",
                "Active patients — opening",
                "={pat_close[-1]}",
                "top",
                "dec1",
                first="={in:pat_start}",
                agg="first",
            ),
            Line("lost", "Patients lost", "={pat_close}-{pat_open}-{new_total}", "top", "dec1"),
            Line("pat_close", "Active patients — closing", close, "top", "dec1", agg="last", bold=True),
            Line("pat_avg", "Active patients — average", "=({pat_open}+{pat_close})/2", "top", "dec1", agg="none"),
            Line(
                "cap_doc",
                "Doctor visit capacity (operatories × visits per chair-day × working days)",
                "={in:ops}*{in:visits_chair}*{in:work_days}*{mpp}",
                "top",
                "int",
                section="Visits",
            ),
            Line(
                "dem_doc",
                "Doctor visits demanded",
                "={pat_avg}*{in:doc_visits}/12*{mpp}+{new_total}*{in:np_visits}",
                "top",
                "int",
            ),
            Line(
                "visits_doc",
                "Doctor visits (demand capped by chairs)",
                "=MIN({cap_doc},{dem_doc})",
                "top",
                "int",
                bold=True,
            ),
            Line("hyg_fte", "Hygienists (FTE)", "={hc_hyg_fte}", "top", "dec1", agg="last"),
            Line(
                "cap_hyg",
                "Hygiene visit capacity (hygienists, up to hygiene rooms, × visits per day × working days)",
                "=MIN({hyg_fte},{in:hyg_ops})*{in:hyg_per_day}*{in:work_days}*{mpp}",
                "top",
                "int",
            ),
            Line("dem_hyg", "Hygiene recall visits demanded", "={pat_avg}*{in:recall}/12*{mpp}", "top", "int"),
            Line(
                "visits_hyg",
                "Hygiene visits (demand capped by hygienists)",
                "=MIN({cap_hyg},{dem_hyg})",
                "top",
                "int",
                bold=True,
            ),
            Line(
                "prod_doc",
                "Doctor production (office fees)",
                f"={{visits_doc}}*{{in:fee_doc}}*{idx}",
                "top",
                section="Production & collections",
            ),
            Line("prod_hyg", "Hygiene production (office fees)", f"={{visits_hyg}}*{{in:fee_hyg}}*{idx}", "top"),
            Line("prod", "Gross production", "={prod_doc}+{prod_hyg}", "top", bold=True),
            Line("adj_ppo", "PPO fee-schedule write-offs", "=-{prod}*{in:ppo_share}*{in:ppo_disc}", "top"),
            Line("bad", "Bad debt (never collected)", "=-({prod}+{adj_ppo})*{in:bad_debt}", "top"),
            Line("rev", "Collections (revenue)", "={prod}+{adj_ppo}+{bad}", "top", bold=True, total=True),
            Line("supplies", "Dental supplies", "=-{prod}*{in:supplies_pct}", "top", section="Cost of sales"),
            Line("lab", "Lab fees", "=-{prod_doc}*{in:lab_pct}", "top"),
            Line("card", "Card & payment processing", "=-{rev}*{in:card_pct}", "top"),
            Line("cogs", "Cost of sales", "={supplies}+{lab}+{card}", "top", bold=True),
        ]

    def opex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "payroll",
                "Staff payroll (owner dentist, hygienists, assistants, front desk)",
                "={payroll_total}",
                "top",
                section="Operating expenses",
            ),
            Line(
                "assoc",
                "Associate dentists (% of the collections they produce)",
                "=-{rev}*{prod_doc}/MAX(1,{prod})*{in:assoc_share}*{in:assoc_pct}",
                "top",
            ),
            Line("mkt", "Marketing", "=-{in:mkt}*(1+{in:mkt_g})^({y}-1)*{mpp}", "top"),
            Line("rent", "Rent", "=-{in:sqft}*{in:rent_psf}/12*{mpp}", "top"),
            Line("utilities", "Utilities & phone", "=-{in:utilities}*{mpp}", "top"),
            Line("software", "Practice software & IT", "=-{in:software}*{mpp}", "top"),
            Line("malpractice", "Malpractice & liability insurance", "=-{in:malpractice}*{mpp}", "top"),
            Line("maint", "Equipment maintenance, cleaning & compliance", "=-{in:maint}*{mpp}", "top"),
            Line("ga_other", "Other G&A", "=-{in:ga_other}*{mpp}", "top"),
        ]

    def capex_lines(self, t: Timing) -> list[Line]:
        return [
            Line(
                "capex",
                "Capital spending (fit-out, operatories, imaging at start; then equipment refresh)",
                "={rev}*{in:refresh_pct}",
                "top",
                first=(
                    "={in:fit_psf}*{in:sqft}+MAX(0,{in:ops}+{in:hyg_ops}-{in:ops_equipped})*{in:capex_op}"
                    "+{in:capex_img}+{rev}*{in:refresh_pct}"
                ),
            )
        ]

    # ------------------------------------------------------------------ dashboard / KPIs
    def dashboard_metrics(self, t: Timing) -> list[DashMetric]:
        return [
            DashMetric("pat", "Active patients (year end)", "kpi:pat_end", "int"),
            DashMetric("util", "Doctor chair utilisation", "kpi:util_doc", "pct"),
            DashMetric("prod_visit", "Production per visit", "kpi:prod_visit", "usd2"),
        ]

    def dashboard_chart(self, t: Timing) -> DashChart:
        return DashChart("Active patients & doctor chair utilisation", bars=("pat",), lines=("util",))

    def kpi_rows(self, t: Timing) -> list[StmtRow]:
        return [
            StmtRow("pat_end", "Active patients (year end)", "line", "pat_close", "int", bold=True),
            StmtRow("new_p", "New patients in the year", "line", "new_total", "int"),
            StmtRow("lost_p", "Patients lost in the year", "line", "lost", "int"),
            StmtRow("mkt_spend", "Marketing spend", "line", "mkt", neg=True),
            StmtRow("new_paid", "New patients from marketing", "line", "new_mkt", "int"),
            StmtRow(
                "cac", "Marketing cost per new patient", "formula", "=IF({new_paid}=0,0,{mkt_spend}/{new_paid})", "usd2"
            ),
            StmtRow("visits_doc", "Doctor visits", "line", "visits_doc", "int"),
            StmtRow("cap_doc", "Doctor visit capacity", "line", "cap_doc", "int"),
            StmtRow(
                "util_doc",
                "Doctor chair utilisation (visits ÷ capacity)",
                "formula",
                "=IF({cap_doc}=0,0,{visits_doc}/{cap_doc})",
                "pct",
            ),
            StmtRow("visits_hyg", "Hygiene visits", "line", "visits_hyg", "int"),
            StmtRow("cap_hyg", "Hygiene visit capacity", "line", "cap_hyg", "int"),
            StmtRow(
                "util_hyg",
                "Hygiene utilisation (visits ÷ capacity)",
                "formula",
                "=IF({cap_hyg}=0,0,{visits_hyg}/{cap_hyg})",
                "pct",
            ),
            StmtRow("prod", "Gross production", "line", "prod", bold=True),
            StmtRow("prod_hyg", "Hygiene production", "line", "prod_hyg"),
            StmtRow("hyg_share", "Hygiene share of production", "formula", "=IF({prod}=0,0,{prod_hyg}/{prod})", "pct"),
            StmtRow(
                "prod_visit",
                "Production per visit (doctor and hygiene)",
                "formula",
                "=IF({visits_doc}+{visits_hyg}=0,0,{prod}/({visits_doc}+{visits_hyg}))",
                "usd2",
            ),
            StmtRow("rev", "Collections (revenue)", "line", "rev", bold=True),
            StmtRow("coll_rate", "Collections ÷ gross production", "formula", "=IF({prod}=0,0,{rev}/{prod})", "pct"),
            StmtRow(
                "rev_pat",
                "Collections per active patient (year-end base)",
                "formula",
                "=IF({pat_end}=0,0,{rev}/{pat_end})",
                "usd2",
            ),
            StmtRow(
                "rev_op",
                "Collections per doctor operatory",
                "formula",
                "=IF({in:ops}=0,0,{rev}/{in:ops})",
            ),
            StmtRow("gp", "Gross profit (after supplies, lab and card fees)", "line", "gp"),
            StmtRow("gm", "Gross margin", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
            StmtRow("ebitda", "EBITDA (after owner-dentist pay)", "line", "ebitda"),
            StmtRow("em", "EBITDA margin", "formula", "=IF({rev}=0,0,{ebitda}/{rev})", "pct"),
            StmtRow("rev_sqft", "Collections per square foot", "formula", "=IF({in:sqft}=0,0,{rev}/{in:sqft})", "usd2"),
        ]

    def kpi_charts(self, t: Timing) -> list[KpiChart]:
        return [
            KpiChart("Production per visit and collections ÷ production", bars=("prod_visit",), lines=("coll_rate",)),
            KpiChart("Doctor and hygiene utilisation", bars=("util_doc", "util_hyg")),
        ]

    # ------------------------------------------------------------------ python twin
    def kpi_reference(self, ann: dict, d: dict, t: Timing) -> dict:
        out: dict[str, dict] = {k: {} for k in self.kpi_derived}
        for y in range(1, t.years + 1):
            rev, gp, prod = ann["rev"][y], ann["gp"][y], ann["prod"][y]
            visits = ann["visits_doc"][y] + ann["visits_hyg"][y]
            out["util_doc"][y] = div(ann["visits_doc"][y], ann["cap_doc"][y])
            out["util_hyg"][y] = div(ann["visits_hyg"][y], ann["cap_hyg"][y])
            out["hyg_share"][y] = div(ann["prod_hyg"][y], prod)
            out["coll_rate"][y] = div(rev, prod)
            out["prod_visit"][y] = div(prod, visits)
            out["cac"][y] = div(-ann["opex_mkt"][y], ann["new_mkt"][y])
            out["rev_pat"][y] = div(rev, ann["pat_close"][y])
            out["rev_op"][y] = div(rev, d["ops"])
            out["gm"][y] = div(gp, rev)
            out["em"][y] = div(ann["ebitda"][y], rev)
            out["rev_sqft"][y] = div(rev, d["sqft"])
        return out

    def _path(self, d: dict, t: Timing, upto: int) -> list[dict]:
        out = []
        pat = d["pat_start"]
        r = 1 - d["attr_m"]
        for p in range(1, upto + 1):
            y = t.year_of(p)
            mkt = d["mkt"] * (1 + d["mkt_g"]) ** (y - 1) * t.mpp
            new_mkt = mkt / max(1, d["cpnp"])
            new = new_mkt + d["ref_new"] * (1 + d["ref_g"]) ** (y - 1) * t.mpp
            p0 = pat
            pat = p0 * r + new if t.granularity == "monthly" else p0 * r**12 + new * r**6
            out.append({"p0": p0, "p1": pat, "new": new, "new_mkt": new_mkt, "lost": pat - p0 - new, "mkt": mkt})
        return out

    def reference_top(self, d: dict, p: int, y: int, t: Timing, hc: HC) -> Top:
        s = self._path(d, t, p)[-1]
        fte, _ = role_period(d, HYG, p, t)
        avg = (s["p0"] + s["p1"]) / 2
        idx = (1 + d["price_g"]) ** (y - 1)
        cap_doc = d["ops"] * d["visits_chair"] * d["work_days"] * t.mpp
        dem_doc = avg * d["doc_visits"] / 12 * t.mpp + s["new"] * d["np_visits"]
        visits_doc = min(cap_doc, dem_doc)
        cap_hyg = min(fte, d["hyg_ops"]) * d["hyg_per_day"] * d["work_days"] * t.mpp
        dem_hyg = avg * d["recall"] / 12 * t.mpp
        visits_hyg = min(cap_hyg, dem_hyg)
        prod_doc = visits_doc * d["fee_doc"] * idx
        prod_hyg = visits_hyg * d["fee_hyg"] * idx
        prod = prod_doc + prod_hyg
        adj = -prod * d["ppo_share"] * d["ppo_disc"]
        bad = -(prod + adj) * d["bad_debt"]
        rev = prod + adj + bad
        cogs = -prod * d["supplies_pct"] - prod_doc * d["lab_pct"] - rev * d["card_pct"]
        assoc = -rev * (prod_doc / max(1, prod)) * d["assoc_share"] * d["assoc_pct"]
        capex = rev * d["refresh_pct"]
        if p == 1:
            capex += (
                d["fit_psf"] * d["sqft"]
                + max(0.0, d["ops"] + d["hyg_ops"] - d["ops_equipped"]) * d["capex_op"]
                + d["capex_img"]
            )
        return Top(
            rev=rev,
            cogs=cogs,
            opex={
                "payroll": hc.payroll,
                "assoc": assoc,
                "mkt": -s["mkt"],
                "rent": -d["sqft"] * d["rent_psf"] / 12 * t.mpp,
                "utilities": -d["utilities"] * t.mpp,
                "software": -d["software"] * t.mpp,
                "malpractice": -d["malpractice"] * t.mpp,
                "maint": -d["maint"] * t.mpp,
                "ga_other": -d["ga_other"] * t.mpp,
            },
            capex=capex,
            kpis={
                "pat_close": s["p1"],
                "new_total": s["new"],
                "lost": s["lost"],
                "new_mkt": s["new_mkt"],
                "visits_doc": visits_doc,
                "cap_doc": cap_doc,
                "visits_hyg": visits_hyg,
                "cap_hyg": cap_hyg,
                "prod": prod,
                "prod_hyg": prod_hyg,
            },
        )

    # ------------------------------------------------------------------ defaults
    def default_brief(self, stage: str = "growing", **opts) -> Brief:
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
                "model_name": f"Dental practice financial model ({stage})",
                "template": self.key,
                "business_type": "dental",
                "stage": stage,
                "assumption_note": "Illustrative assumptions — replace them with your own numbers.",
                "roles": roles,
                "drivers": drivers,
                **opts,
            }
        )
        self.validate(brief)
        return brief
