"""Standard modules (E07, ADR-013): sheets every model of a tier gets.

ADR-013 replaced "the goal adds sheets" with "the tier decides the sheets"; the brief's ``goal`` now only sets
the Cover's purpose line.

- ``breakeven`` (Light and Full) → **Break-even** sheet: uses and sources of funds up to the lowest cash point,
  funding surplus / shortfall after a minimum cash buffer, first period of positive EBITDA / net income,
  payback of the cash invested, and annual break-even revenue.
- ``dcf`` (Full) → **Valuation** sheet: unlevered free cash flow from the model, discounting at the
  WACC, terminal value by perpetual growth and by exit multiple, and a WACC × growth sensitivity table.

This file holds what does not need openpyxl: the extra drivers, their defaults, the extra grid lines
and the plain-Python twin the challenger compares against. Sheets are written by
``engine.goal_sheets``.
"""

from __future__ import annotations

from collections.abc import Collection

from engine.brief import Brief, BriefError
from engine.spec import DriverSpec, Line, Timing

#: modules by tier (ADR-013, docs/WORKBOOK_STANDARD.md §1)
MODULES: dict[str, tuple[str, ...]] = {
    "light": ("breakeven",),
    "full": ("breakeven", "dcf"),
}
#: the Cover's purpose line by wizard goal
PURPOSE: dict[str, str] = {
    "revenue_profit": "Revenue and profit plan",
    "startup_breakeven": "Startup costs, funding need and break-even",
    "dcf_valuation": "Business valuation (DCF)",
    "investor_pitch": "Investor-ready plan",
    "other": "Financial plan",
}

NOT_WITHIN = "Not within horizon"
NOTHING_TO_PAY_BACK = "No investment to pay back"
NA = "n/a"

BREAKEVEN_SPECS = [
    DriverSpec("cash_buffer", "Minimum cash buffer to keep", "$", "usd", 0, 1e9, section="Break-even & funding"),
]
DCF_SPECS = [
    DriverSpec("wacc", "Discount rate (WACC)", "%", "pct", 0.03, 0.6, "desc", "Valuation"),
    DriverSpec("tg", "Terminal growth rate (perpetuity)", "%", "pct", -0.05, 0.06, "asc", "Valuation"),
    DriverSpec("exit_mult", "Exit multiple (EV ÷ final-year EBITDA)", "x", "x", 0, 40, "asc", "Valuation"),
    DriverSpec("wacc_step", "Sensitivity table: WACC step", "%", "pct", 0.0025, 0.03, section="Valuation"),
    DriverSpec("g_step", "Sensitivity table: growth step", "%", "pct", 0.001, 0.02, section="Valuation"),
]
ALL_GOAL_KEYS = {s.key for s in BREAKEVEN_SPECS + DCF_SPECS}
#: smallest WACC − terminal growth spread accepted in any scenario
MIN_SPREAD = 0.01

#: illustrative DCF defaults by stage: (low, base, high); Low has the higher discount rate
DCF_DEFAULTS: dict[str, dict[str, tuple[float, float, float]]] = {
    "planning": {"wacc": (0.30, 0.25, 0.20), "exit_mult": (3.0, 4.0, 5.0)},
    "early": {"wacc": (0.25, 0.20, 0.17), "exit_mult": (3.5, 4.5, 6.0)},
    "growing": {"wacc": (0.20, 0.16, 0.13), "exit_mult": (4.0, 5.5, 7.0)},
    "established": {"wacc": (0.15, 0.12, 0.10), "exit_mult": (5.0, 6.0, 8.0)},
}


def modules_for(tier: str) -> tuple[str, ...]:
    return MODULES.get(tier, ())


def purpose(goal: str) -> str:
    return PURPOSE.get(goal, "Financial plan")


def goal_specs(tier: str) -> list[DriverSpec]:
    mods = modules_for(tier)
    return (BREAKEVEN_SPECS if "breakeven" in mods else []) + (DCF_SPECS if "dcf" in mods else [])


def validate_goal(brief: Brief) -> None:
    if "dcf" not in modules_for(brief.tier):
        return
    errs = []
    for scen, name in ((1, "low"), (2, "base"), (3, "high")):
        v = brief.values(scen)
        if v.get("wacc", 1) - v.get("tg", 0) < MIN_SPREAD - 1e-12:
            errs.append(f"{name}: WACC must exceed terminal growth by at least {MIN_SPREAD:.0%}")
    if errs:
        raise BriefError("; ".join(errs))


# --------------------------------------------------------------------------- defaults
def default_values(tier: str, brief: Brief, tpl=None) -> list[dict]:
    """Driver values a brief needs for its tier's modules (stage defaults; buffer = 3 months of opex)."""
    out: list[dict] = []
    mods = modules_for(tier)
    if "breakeven" in mods:
        buf = _three_months_opex(brief, tpl)
        out.append({"key": "cash_buffer", "low": buf, "base": buf, "high": buf, "note": "About 3 months of costs"})
    if "dcf" in mods:
        d = DCF_DEFAULTS.get(brief.stage, DCF_DEFAULTS["growing"])
        out += [
            {"key": "wacc", "low": d["wacc"][0], "base": d["wacc"][1], "high": d["wacc"][2]},
            {"key": "tg", "low": 0.01, "base": 0.02, "high": 0.03},
            {"key": "exit_mult", "low": d["exit_mult"][0], "base": d["exit_mult"][1], "high": d["exit_mult"][2]},
            {"key": "wacc_step", "low": 0.01, "base": 0.01, "high": 0.01},
            {"key": "g_step", "low": 0.005, "base": 0.005, "high": 0.005},
        ]
    return out


def _three_months_opex(brief: Brief, tpl=None) -> float:
    from engine.core import reference_run
    from engine.templates import get_template

    tpl = tpl or get_template(brief.template)
    d = {k: v for k, v in brief.values(2).items() if k not in ALL_GOAL_KEYS}
    s = reference_run(d, brief.roles, Timing("monthly", 1), tpl.reference_top)
    spec = BREAKEVEN_SPECS[0]  # the buffer stays inside its own allowed range, whatever the costs
    return float(min(spec.max, max(spec.min, round(-sum(s["opex_total"]) / 12 * 3, -3))))


#: goal drivers whose default is computed from other drivers (see ``default_values``)
DERIVED_KEYS = frozenset({"cash_buffer"})


def refresh_derived(brief: Brief, keep: Collection[str] = ()) -> Brief:
    """Recompute the derived goal defaults (``DERIVED_KEYS``) after other drivers changed.

    Keys in ``keep`` (changed by the model, or typed by the customer) are left alone. Low / High follow
    the same derivation as the defaults. A brief without those drivers is returned as is.
    """
    fresh = {
        dv["key"]: dv
        for dv in default_values(brief.tier, brief)
        if dv["key"] in DERIVED_KEYS and dv["key"] not in keep and any(d.key == dv["key"] for d in brief.drivers)
    }
    if not fresh:
        return brief
    data = brief.model_dump()
    for d in data["drivers"]:
        if d["key"] in fresh:
            d.update(low=fresh[d["key"]]["low"], base=fresh[d["key"]]["base"], high=fresh[d["key"]]["high"])
    return Brief.model_validate(data)


def apply_goal(brief: Brief, goal: str | None = None, tpl=None) -> Brief:
    """Brief with ``goal`` set and exactly the module drivers its **tier** needs (existing values are kept).

    Idempotent; the build, the challenger and the worker call it, so briefs stored before ADR-013 (a goal
    without module drivers, or a Light brief with DCF drivers) still build.
    """
    goal = goal or brief.goal
    from engine.templates import get_template

    tpl = tpl or get_template(brief.template)
    base_keys = {s.key for s in tpl.all_specs(brief.roles, brief.tier)} - ALL_GOAL_KEYS
    if not base_keys <= {d.key for d in brief.drivers}:
        # incomplete brief: leave the module drivers alone and let validation report what is missing
        return brief if goal == brief.goal else brief.model_copy(update={"goal": goal})
    need = {s.key for s in goal_specs(brief.tier)}
    data = brief.model_dump()
    data["goal"] = goal
    data["drivers"] = [d for d in data["drivers"] if d["key"] not in ALL_GOAL_KEYS or d["key"] in need]
    have = {d["key"] for d in data["drivers"]}
    base = Brief.model_validate(data)
    data["drivers"] += [dv for dv in default_values(brief.tier, base, tpl) if dv["key"] not in have]
    return Brief.model_validate(data)


standardize = apply_goal


# --------------------------------------------------------------------------- grid lines
def module_lines(tier: str) -> list[Line]:
    mods = modules_for(tier)
    out: list[Line] = []
    if "breakeven" in mods:
        out += [
            Line(
                "ni_flag",
                "Helper: net income positive (1/0)",
                "=IF({ni}>0,1,0)",
                "goal",
                "int",
                agg="none",
                section="Goal modules",
            ),
            Line("pre_fin_cf", "Cash flow before financing (operating + investing)", "={cfo}+{cfi}", "goal"),
            Line(
                "cum_pre_fin",
                "Cumulative cash flow before financing",
                "={cum_pre_fin[-1]}+{pre_fin_cf}",
                "goal",
                first="={pre_fin_cf}",
                agg="last",
            ),
            Line(
                "cum_pre_fin_min",
                "Helper: lowest cumulative cash flow so far",
                "=MIN({cum_pre_fin_min[-1]},{cum_pre_fin})",
                "goal",
                first="={cum_pre_fin}",
                agg="none",
            ),
            Line(
                "payback_flag",
                "Helper: investment paid back (1/0)",
                "=IF(AND({cum_pre_fin}>=0,{cum_pre_fin_min}<0),1,0)",
                "goal",
                "int",
                agg="none",
            ),
        ]
    if "dcf" in mods:
        out.append(
            Line(
                "fcff",
                "Unlevered free cash flow (operating + after-tax interest − capex)",
                "={cfo}-{interest}*(1-{in:tax_rate})+{cfi}",
                "goal",
                section=None if out else "Goal modules",
            )
        )
    return out


# --------------------------------------------------------------------------- python twin
#: tolerances for the challenger (default $1)
TOLERANCE = {
    "gm": 1e-6,
    "mos": 1e-6,
    "df": 1e-9,
    "tv_share_g": 1e-6,
    "tv_share_m": 1e-6,
    "implied_mult": 1e-4,
    "implied_g": 1e-6,
    "cagr": 1e-6,
}


def _first(flags: list[bool]) -> int | str:
    for i, f in enumerate(flags):
        if f:
            return i + 1
    return NOT_WITHIN


def reference(brief: Brief, d: dict, s: dict[str, list[float]], t: Timing) -> dict:
    """Plain-Python values of the goal modules for one scenario.

    ``d`` = active driver values, ``s`` = per-period series from ``engine.core.reference_run``.
    Returns ``{"cells": {name: value}, "years": {name: {year: value}}}``; values are floats or the
    exact text the workbook shows (e.g. "Not within horizon").
    """
    mods = modules_for(brief.tier)
    cells: dict[str, float | str] = {}
    years: dict[str, dict[int, float | str]] = {}
    n, ppy, H = t.periods, t.ppy, t.years

    def ysum(key: str, y: int) -> float:
        return sum(s[key][(y - 1) * ppy : y * ppy])

    if "breakeven" in mods:
        cash = s["cash_close"]
        low = cash.index(min(cash)) + 1
        capex = sum(s["capex"][:low])
        burn = -sum(s["cfo"][:low])
        repay = -sum(s["loan_repay"][:low])
        uses = capex + burn + repay
        required = uses + d["cash_buffer"]
        sources = d["equity"] + d["loan_amount"]
        cells.update(
            low_p=low,
            capex_to_low=capex,
            burn_to_low=burn,
            repay_to_low=repay,
            uses=uses,
            buffer=d["cash_buffer"],
            required=required,
            sources=sources,
            gap=sources - required,
            min_cash=min(cash),
        )
        cells["first_ebitda"] = _first([v > 0 for v in s["ebitda"]])
        cells["first_ni"] = _first([v > 0 for v in s["ni"]])
        cum, cmin, flags = 0.0, None, []
        for p in range(n):
            cum += s["cfo"][p] + s["cfi"][p]
            cmin = cum if cmin is None else min(cmin, cum)
            flags.append(cum >= 0 and cmin < 0)
        if cmin >= 0:
            cells["payback"] = NOTHING_TO_PAY_BACK
        else:
            cells["payback"] = _first(flags)
        years.update(gm={}, be_rev={}, mos={})
        for y in range(1, H + 1):
            rev, gp, opex = ysum("rev", y), ysum("gp", y), -ysum("opex_total", y)
            gm = gp / rev if rev else 0.0
            be = opex / gm if gm > 0 else NA
            years["gm"][y] = gm
            years["be_rev"][y] = be
            years["mos"][y] = (rev - be) / rev if not isinstance(be, str) and rev > 0 else NA
    if "dcf" in mods:
        w, g, mult = d["wacc"], d["tg"], d["exit_mult"]
        fcf = {
            y: sum(
                s["cfo"][p] - s["interest"][p] * (1 - d["tax_rate"]) + s["cfi"][p]
                for p in range((y - 1) * ppy, y * ppy)
            )
            for y in range(1, H + 1)
        }
        df = {y: 1 / (1 + w) ** y for y in range(1, H + 1)}
        years["fcff"] = fcf
        years["df"] = df
        years["pv"] = {y: fcf[y] * df[y] for y in fcf}
        sum_pv = sum(years["pv"].values())
        ebitda_h = ysum("ebitda", H)
        tv_g = fcf[H] * (1 + g) / (w - g) if w > g else 0.0
        tv_m = ebitda_h * mult
        pv_g, pv_m = tv_g / (1 + w) ** H, tv_m / (1 + w) ** H
        ev_g, ev_m = sum_pv + pv_g, sum_pv + pv_m
        cells.update(
            sum_pv=sum_pv,
            tv_g=tv_g,
            tv_m=tv_m,
            pv_tv_g=pv_g,
            pv_tv_m=pv_m,
            ev_g=ev_g,
            ev_m=ev_m,
            ev_avg=(ev_g + ev_m) / 2,
            tv_share_g=pv_g / ev_g if ev_g != 0 else 0.0,
            tv_share_m=pv_m / ev_m if ev_m != 0 else 0.0,
            implied_mult=tv_g / ebitda_h if ebitda_h > 0 else NA,
            implied_g=(tv_m * w - fcf[H]) / (tv_m + fcf[H]) if tv_m + fcf[H] != 0 else NA,
            sens_centre=ev_g,
        )
    return {"cells": cells, "years": years}
