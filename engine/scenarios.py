"""Scenarios sheet (E29, docs/WORKBOOK_STANDARD.md §1): Low / Base / High side by side, live.

The model's own grid computes only the scenario chosen on the Dashboard (Inputs column E). For the side-by-side
view the engine copies the whole period calculation three times onto the "Scenario calc" sheet; each copy reads
its own Inputs column (B = Low, C = Base, D = High) and refers only to its own rows, so all three stay live
whatever the selector says. Every copy is rendered from the same template lines as the model's grid — no second
formula set to keep in step.

The Scenarios sheet then shows, per scenario: the template's key drivers (links to Inputs), the outputs (columns
B / C / D from the chains, E = Active from the statements and the Break-even sheet), per-year tables and four
line charts. The in-file check "Scenarios: Active = selected scenario" proves that the chain of the selected
scenario equals the model; the challenger recomputes every Low / Base / High cell with the Python reference for
that scenario (``reference``), independent of the selector.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from openpyxl.utils import get_column_letter as L

from engine import charts as ch
from engine import style as st
from engine.builder import FIRST_COL, GridPlan, Plan, _layout_grid, _write_grid, q
from engine.dashboard import MONEY_K, PCT, YEAR_FMT
from engine.spec import FORMATS, Brief

SHEET = "Scenarios"
CALC = "Scenario calc"
NAMES = {1: "Low", 2: "Base", 3: "High"}
COLS = {1: "B", 2: "C", 3: "D"}
ACTIVE = "E"
#: Base in the lead colour, Low amber, High sage (docs/WORKBOOK_STANDARD.md §3 palette)
SERIES_COLOR = {1: st.AMBER, 2: st.PINE, 3: st.SAGE}
INT = "0"
#: per-year tables: metric -> (title, grid line, flow summed over the year / balance at year end)
TABLES = {
    "rev": ("Revenue", "rev", True),
    "ebitda": ("EBITDA", "ebitda", True),
    "ni": ("Net income", "ni", True),
    "cash": ("Cash at year end", "cash_close", False),
}
#: output rows: name -> label (the formulas are built in ``_plan_outputs``)
OUTPUT_LABELS = {
    "rev_last": "Revenue — final year",
    "rev_total": "Revenue — whole plan",
    "ebitda_last": "EBITDA — final year",
    "ebitda_m": "EBITDA margin — final year",
    "ni_last": "Net income — final year",
    "ni_cum": "Net income — whole plan",
    "cash_end": "Cash at the end of the plan",
    "min_cash": "Lowest cash balance",
    "low_p": "Lowest cash point ({word} #)",
    "required": "Funding required (incl. cash buffer)",
}
#: challenger tolerances by output name (money cells: $1)
TOLERANCE = {"ebitda_m": 1e-6, "low_p": 0.0}
#: Active-check tolerance per output (money within $0.5)
_TIE = {"ebitda_m": "0.000001", "low_p": "0.5"}


@dataclass
class ScenLayout:
    grids: dict[int, GridPlan]
    drivers: list[tuple[str, int]] = field(default_factory=list)  # (input key, row)
    outputs: dict[str, int] = field(default_factory=dict)  # output name -> row
    tables: dict[str, int] = field(default_factory=dict)  # metric -> header row (Low / Base / High below)
    #: challenger manifest: ``<name>_<s>`` (s = 1, 2, 3) and ``<name>_a`` (Active) -> cell
    cells: dict[str, str] = field(default_factory=dict)
    #: ``<metric>_<s>`` -> {year: cell}
    years: dict[str, dict[int, str]] = field(default_factory=dict)
    end: int = 0
    calc_end: int = 0
    years_n: int = 1

    @property
    def error_range(self) -> str:
        return f"{q(SHEET)}!$B$5:${L(max(5, 1 + self.years_n))}${self.end}"


# --------------------------------------------------------------------------- planning
def _plan_chains(pl: Plan) -> dict[int, GridPlan]:
    lines = [ln for g in pl.grids for ln in g.lines]
    grids, start = {}, 5
    for s in (1, 2, 3):
        g = GridPlan(CALC, start, lines, input_col=COLS[s])
        _layout_grid(g)
        g.line_at = {k: (CALC, r) for k, r in g.rows.items()}
        grids[s] = g
        start = g.end_row + 4
    return grids


def _chain_range(pl: Plan, g: GridPlan, key: str) -> str:
    r = g.rows[key]
    return f"{q(CALC)}!${L(FIRST_COL)}${r}:${L(FIRST_COL + pl.t.periods - 1)}${r}"


def _chain_row(pl: Plan, g: GridPlan, which: str) -> str:
    r = g.period_row if which == "period" else g.year_row
    return f"{q(CALC)}!${L(FIRST_COL)}${r}:${L(FIRST_COL + pl.t.periods - 1)}${r}"


def plan_scenarios(pl: Plan) -> ScenLayout | None:
    if pl.brief.tier != "full":
        return None
    lay = ScenLayout(_plan_chains(pl), years_n=pl.t.years)
    r = 5
    keys = [k for k in pl.template.key_numbers if k in pl.input_row]
    r += 1  # section band
    r += 1  # header
    for k in keys:
        lay.drivers.append((k, r))
        r += 1
    r += 1
    r += 2  # band + header
    for name in OUTPUT_LABELS:
        lay.outputs[name] = r
        r += 1
    r += 1
    for metric in TABLES:
        r += 1  # band
        lay.tables[metric] = r  # header with the year numbers
        r += 5  # header, Low, Base, High, blank
    lay.end = r - 2
    years = range(1, pl.t.years + 1)
    for metric, top in lay.tables.items():
        for s in (1, 2, 3):
            lay.years[f"{metric}_{s}"] = {y: f"{q(SHEET)}!{L(1 + y)}{top + s}" for y in years}
    for name, row in lay.outputs.items():
        for s, col in COLS.items():
            lay.cells[f"{name}_{s}"] = f"{q(SHEET)}!{col}{row}"
        lay.cells[f"{name}_a"] = f"{q(SHEET)}!{ACTIVE}{row}"
    lay.calc_end = lay.grids[3].end_row
    return lay


# --------------------------------------------------------------------------- formulas
def _table_formula(pl: Plan, g: GridPlan, metric: str, year_cell: str) -> str:
    _, key, flow = TABLES[metric]
    rng = _chain_range(pl, g, key)
    if flow:
        return f"=SUMIF({_chain_row(pl, g, 'year')},{year_cell},{rng})"
    return f"=INDEX({rng},{year_cell}*{pl.t.ppy})"


def _scenario_outputs(pl: Plan, lay: ScenLayout, s: int) -> dict[str, str]:
    g, col, last = lay.grids[s], COLS[s], L(1 + pl.t.years)

    def t(metric: str) -> tuple[str, str]:
        r = lay.tables[metric] + s
        return f"{last}{r}", f"B{r}:{last}{r}"

    cash, prow = _chain_range(pl, g, "cash_close"), _chain_row(pl, g, "period")
    lo = f"{col}{lay.outputs['low_p']}"
    buffer = pl.input_col("cash_buffer", col)
    return {
        "rev_last": f"={t('rev')[0]}",
        "rev_total": f"=SUM({t('rev')[1]})",
        "ebitda_last": f"={t('ebitda')[0]}",
        "ebitda_m": _margin(col, lay),
        "ni_last": f"={t('ni')[0]}",
        "ni_cum": f"=SUM({t('ni')[1]})",
        "cash_end": f"={t('cash')[0]}",
        "min_cash": f"=MIN({cash})",
        "low_p": f"=MATCH(MIN({cash}),{cash},0)",
        "required": (
            f"=SUMPRODUCT(--({prow}<={lo}),{_chain_range(pl, g, 'capex')})"
            f"-SUMPRODUCT(--({prow}<={lo}),{_chain_range(pl, g, 'cfo')})"
            f"-SUMPRODUCT(--({prow}<={lo}),{_chain_range(pl, g, 'loan_repay')})+{buffer}"
        ),
    }


def _margin(col: str, lay: ScenLayout) -> str:
    rev, e = f"{col}{lay.outputs['rev_last']}", f"{col}{lay.outputs['ebitda_last']}"
    return f"=IF({rev}=0,0,{e}/{rev})"


def _active_outputs(pl: Plan, lay: ScenLayout) -> dict[str, str]:
    n = pl.t.years
    be = pl.modules["breakeven"].cells
    return {
        "rev_last": f"={pl.stmt_cell('pl', 'rev', n)}",
        "rev_total": f"=SUM({pl.stmt_range('pl', 'rev')})",
        "ebitda_last": f"={pl.stmt_cell('pl', 'ebitda', n)}",
        "ebitda_m": _margin(ACTIVE, lay),
        "ni_last": f"={pl.stmt_cell('pl', 'ni', n)}",
        "ni_cum": f"=SUM({pl.stmt_range('pl', 'ni')})",
        "cash_end": f"={pl.stmt_cell('bs', 'cash', n)}",
        "min_cash": f"={be['min_cash']}",
        "low_p": f"={be['low_p']}",
        "required": f"={be['required']}",
    }


def active_check(pl: Plan) -> str:
    """Condition: column E (the live model) equals the selected scenario's column for every output."""
    lay = pl.scen
    sheet, cell = pl.selector
    sel = f"{q(sheet)}!${cell[0]}${cell[1:]}"
    sh = q(SHEET)
    conds = [
        f"ABS({sh}!{ACTIVE}{r}-INDEX({sh}!B{r}:D{r},1,{sel}))<{_TIE.get(name, '0.5')}"
        for name, r in lay.outputs.items()
    ]
    return f"IFERROR(AND({','.join(conds)}),FALSE)"


# --------------------------------------------------------------------------- writing
def write_scenarios(wb, pl: Plan) -> None:
    lay = pl.scen
    _write_calc(wb, pl, lay)
    ws = wb[SHEET]
    n = pl.t.years
    st.title(
        ws,
        "Scenarios — Low / Base / High",
        "All three scenarios calculated side by side, live: change any input and every column updates. "
        "Active = the scenario chosen on the Dashboard.",
        8,
        link_col=8,
    )

    def head(row: int, labels: dict[int, str], fmt: str | None = None) -> None:
        for c, text in labels.items():
            x = ws.cell(row=row, column=c, value=text)
            st.header(x, right=c > 1)
            if fmt:
                x.number_format = fmt

    def band(row: int, text: str) -> None:
        st.section(ws, row, text, 1 + max(4, n))

    scen_head = {1: "", 2: "Low", 3: "Base", 4: "High", 5: "Active"}
    if lay.drivers:
        first = lay.drivers[0][1]
        band(first - 2, "Key drivers")
        head(first - 1, scen_head | {1: "Driver"})
    specs = {s.key: s for s in pl.specs}
    for key, r in lay.drivers:
        sp = specs[key]
        ws.cell(row=r, column=1, value=f"{sp.label} ({sp.unit})" if sp.unit else sp.label).font = st.font()
        for i, col in enumerate("BCDE"):
            c = ws.cell(row=r, column=2 + i, value=f"={pl.input_col(key, col)}")
            c.font = st.font(st.INK, bold=col == ACTIVE)
            c.number_format = FORMATS[sp.fmt]
            if col == ACTIVE:
                c.fill = st.ACTIVE_FILL
    top = lay.outputs["rev_last"]
    band(top - 2, "Results by scenario ($'000)")
    head(top - 1, scen_head | {1: "Output"})
    cols = {s: _scenario_outputs(pl, lay, s) for s in (1, 2, 3)}
    active = _active_outputs(pl, lay)
    word = pl.t.period_word
    for name, r in lay.outputs.items():
        ws.cell(row=r, column=1, value=OUTPUT_LABELS[name].format(word=word)).font = st.font(bold=name in ("required",))
        fmt = PCT if name == "ebitda_m" else INT if name == "low_p" else MONEY_K
        for s, col in COLS.items():
            c = ws[f"{col}{r}"]
            c.value = cols[s][name]
            c.font = st.font()
            c.number_format = fmt
        c = ws[f"{ACTIVE}{r}"]
        c.value = active[name]
        c.font = st.font(st.INK, bold=True)
        c.fill = st.ACTIVE_FILL
        c.number_format = fmt
    for metric, hdr in lay.tables.items():
        title = TABLES[metric][0]
        band(hdr - 1, f"{title} by year ($'000)")
        ws.cell(row=hdr, column=1, value="Scenario")
        st.header(ws.cell(row=hdr, column=1))
        for y in range(1, n + 1):
            x = ws.cell(row=hdr, column=1 + y, value=y)
            st.header(x, right=True)
            x.number_format = YEAR_FMT
        for s in (1, 2, 3):
            r = hdr + s
            ws.cell(row=r, column=1, value=NAMES[s]).font = st.font()
            for y in range(1, n + 1):
                c = ws.cell(row=r, column=1 + y, value=_table_formula(pl, lay.grids[s], metric, f"{L(1 + y)}${hdr}"))
                c.font = st.font()
                c.number_format = MONEY_K
    ws.column_dimensions["A"].width = 40
    for c in "BCDEF":
        ws.column_dimensions[c].width = 12
    ws.column_dimensions["G"].width = 2
    ws.freeze_panes = "B5"
    _write_charts(ws, pl, lay)


def _write_calc(wb, pl: Plan, lay: ScenLayout) -> None:
    ws = wb[CALC]
    for s, g in lay.grids.items():
        _write_grid(wb, pl, g, f"{NAMES[s]} scenario — reads Inputs column {COLS[s]}", "")
    st.title(
        ws,
        "Scenario calculation — Low, Base and High side by side",
        "The model's period calculation, copied three times; each copy reads its own Inputs column. "
        "Feeds the Scenarios sheet only.",
        min(2 + pl.t.periods, 16),
        link_col=4,
    )
    ws.freeze_panes = "C3"


def _write_charts(ws, pl: Plan, lay: ScenLayout) -> None:
    sh, n = q(SHEET), pl.t.years
    for slot, (metric, hdr) in enumerate(lay.tables.items()):
        cats = f"{sh}!$B${hdr}:${L(1 + n)}${hdr}"
        series = [
            ch.Ser(f"{sh}!$B${hdr + s}:${L(1 + n)}${hdr + s}", f"{sh}!$A${hdr + s}", SERIES_COLOR[s]) for s in (1, 2, 3)
        ]
        chart = ch.line(TABLES[metric][0], cats, series, cat_fmt=YEAR_FMT, legend=True)
        ch.place(ws, chart, ch.slot_anchor(slot, 5))


# --------------------------------------------------------------------------- Python twin
def reference(brief: Brief, scenario: int) -> dict:
    """Plain-Python values of one scenario's column: ``cells`` (output name -> value), ``years`` (metric -> {y})."""
    from engine.core import annualise, reference_run
    from engine.goals import apply_goal
    from engine.goals import reference as goal_reference
    from engine.spec import Timing
    from engine.templates import get_template

    brief = apply_goal(brief)
    tpl = get_template(brief.template)
    t = Timing(brief.granularity, brief.horizon_years)
    d = brief.values(scenario)
    series = reference_run(d, brief.roles, t, tpl.reference_top, tpl.loan_style)
    ann = annualise(series, t)
    years = {m: dict(ann[key]) for m, (_, key, _flow) in TABLES.items()}
    n = t.years
    goal = goal_reference(brief, d, series, t)["cells"]
    rev, ebitda = years["rev"][n], years["ebitda"][n]
    cells = {
        "rev_last": rev,
        "rev_total": sum(years["rev"].values()),
        "ebitda_last": ebitda,
        "ebitda_m": ebitda / rev if rev != 0 else 0.0,
        "ni_last": years["ni"][n],
        "ni_cum": sum(years["ni"].values()),
        "cash_end": years["cash"][n],
        "min_cash": goal["min_cash"],
        "low_p": goal["low_p"],
        "required": goal["required"],
    }
    return {"cells": cells, "years": years}
