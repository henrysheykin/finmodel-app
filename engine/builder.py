"""Turn a validated brief + template into an .xlsx workbook.

Two phases: ``plan`` assigns every line and statement row to a sheet/row
(pure, no openpyxl), ``build`` writes the workbook from that plan. The plan
also yields the ``Manifest`` the challenger uses to find cells.

Tiers differ in presentation only — the calculation lines (and therefore the
numbers) are identical, so a Light → Full upgrade never changes a figure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

from engine import style as st
from engine.brief import Brief
from engine.core import (
    balance_sheet_lines,
    headcount_lines,
    liability_delta_lines,
    pnl_head_lines,
    pnl_tail_lines,
)
from engine.spec import FORMATS, DriverSpec, Line, StmtRow, Timing
from engine.templates.base import Template

FIRST_COL = 3  # period 1 is column C on every grid sheet
DASH_KPI_ROW = 25  # template KPI table on the Dashboard starts here (below Health)
TOKEN = re.compile(r"\{([^{}]+)\}")
PURE_LINK = re.compile(r"^=(?:'[^']+'|[A-Za-z0-9_]+)!\$?[A-Z]{1,3}\$?\d+$")


def q(sheet: str) -> str:
    return sheet if re.fullmatch(r"[A-Za-z0-9_]+", sheet) else f"'{sheet}'"


# --------------------------------------------------------------------------- plan types
@dataclass
class Block:
    name: str
    sheet: str
    start_row: int
    rows: list[StmtRow]
    title: str = ""
    year_row: int = 0  # filled by plan
    placed: dict[str, int] = field(default_factory=dict)


@dataclass
class GridPlan:
    sheet: str
    start_row: int
    lines: list[Line]
    period_row: int = 0
    year_row: int = 0
    rows: dict[str, int] = field(default_factory=dict)
    sections: dict[int, str] = field(default_factory=dict)
    end_row: int = 0


@dataclass
class Manifest:
    tier: str
    granularity: str
    years: int
    sheets: list[str]
    selector: str
    verdict: str
    metrics: dict[str, dict[int, str]]
    grid_ranges: dict[str, str]

    def to_dict(self) -> dict:
        return self.__dict__.copy()


@dataclass
class Plan:
    brief: Brief
    template: Template
    t: Timing
    specs: list[DriverSpec]
    lines: dict[str, Line]
    grids: list[GridPlan]
    blocks: dict[str, Block]
    sheets: list[str]
    selector: tuple[str, str]  # sheet, cell
    input_row: dict[str, int]
    calc_sheet: str
    line_at: dict[str, tuple[str, int]] = field(default_factory=dict)

    # ---- references ------------------------------------------------------
    def period_cell(self, key: str, p: int, from_sheet: str, absolute: bool = False) -> str:
        sheet, row = self.line_at[key]
        col = L(FIRST_COL + p - 1)
        ref = f"${col}${row}" if absolute else f"{col}{row}"
        return ref if sheet == from_sheet else f"{q(sheet)}!{ref}"

    def grid_range(self, key: str, from_sheet: str | None = None) -> str:
        sheet, row = self.line_at[key]
        rng = f"${L(FIRST_COL)}${row}:${L(FIRST_COL + self.t.periods - 1)}${row}"
        return rng if sheet == from_sheet else f"{q(sheet)}!{rng}"

    def input_ref(self, key: str) -> str:
        return f"Inputs!$E${self.input_row[key]}"

    def input_col(self, key: str, col: str) -> str:
        return f"Inputs!${col}${self.input_row[key]}"

    def stmt_cell(self, block: str, key: str, y: int, from_sheet: str | None = None) -> str:
        b = self.blocks[block]
        ref = f"{L(1 + y)}{b.placed[key]}"
        return ref if b.sheet == from_sheet else f"{q(b.sheet)}!{ref}"

    def stmt_range(self, block: str, key: str) -> str:
        b = self.blocks[block]
        r = b.placed[key]
        return f"{q(b.sheet)}!$B${r}:${L(1 + self.t.years)}${r}"

    def render(self, ln: Line, p: int, sheet: str) -> str:
        text = ln.first if (p == 1 and ln.first is not None) else ln.formula
        grid = next(g for g in self.grids if g.sheet == sheet)

        def sub(m: re.Match) -> str:
            tok = m.group(1)
            if tok.startswith("in:"):
                return self.input_ref(tok[3:])
            if tok == "p":
                return f"{L(FIRST_COL + p - 1)}${grid.period_row}"
            if tok == "y":
                return f"{L(FIRST_COL + p - 1)}${grid.year_row}"
            if tok in ("mpp", "ppy", "dpp"):
                return str(getattr(self.t, tok))
            key, off = tok, 0
            mm = re.fullmatch(r"([a-z0-9_]+)\[(-\d+)\]", tok)
            if mm:
                key, off = mm.group(1), int(mm.group(2))
            if key not in self.line_at:
                raise KeyError(f"line {ln.key!r} references unknown line {key!r}")
            if p + off < 1:
                raise ValueError(f"line {ln.key!r} looks before period 1; give it a `first` formula")
            return self.period_cell(key, p + off, sheet)

        return TOKEN.sub(sub, text)


# --------------------------------------------------------------------------- planning
def _calc_lines(tpl: Template, brief: Brief, t: Timing) -> tuple[list[Line], list[Line], list[Line]]:
    top = tpl.revenue_lines(t) + pnl_head_lines() + tpl.opex_lines(t)
    liabs = tpl.liability_lines(t)
    liab_keys = [ln.key for ln in liabs]
    core = pnl_tail_lines(tpl.opex_keys(t), liab_keys)
    capex = tpl.capex_lines(t)
    capex[0] = replace(capex[0], section="Fixed assets & capital spending")
    at = next(i for i, ln in enumerate(core) if ln.key == "ppe_gross")
    core = core[:at] + capex + core[at:]
    at = next(i for i, ln in enumerate(core) if ln.key == "d_ap") + 1
    core = core[:at] + liabs + liability_delta_lines(liabs) + core[at:]
    hc = headcount_lines(brief.roles)
    return top + core + tpl.extra_lines(t), hc, balance_sheet_lines(liab_keys)


def _layout_grid(g: GridPlan) -> None:
    g.period_row, g.year_row = g.start_row + 1, g.start_row + 2
    r = g.start_row + 3
    for ln in g.lines:
        if ln.section:
            r += 1
            g.sections[r] = ln.section
            r += 1
        g.rows[ln.key] = r
        r += 1
    g.end_row = r - 1


def _layout_block(b: Block) -> None:
    b.year_row = b.start_row
    r = b.start_row + 2
    for row in b.rows:
        if row.kind == "section":
            r += 1 if r > b.start_row + 2 else 0
        b.placed[row.key] = r
        r += 1


def _pl_rows(tpl: Template, t: Timing, lines: dict[str, Line]) -> list[StmtRow]:
    margin = "=IF({rev}=0,0,{%s}/{rev})"
    rows = [
        StmtRow("rev", "Revenue", "line", "rev", bold=True),
        StmtRow("cogs", lines["cogs"].label, "line", "cogs"),
        StmtRow("gp", "Gross profit", "line", "gp", bold=True, total=True),
        StmtRow("gm", "Gross margin", "formula", margin % "gp", "pct"),
    ]
    rows += [StmtRow(k, lines[k].label, "line", k) for k in tpl.opex_keys(t)]
    rows += [
        StmtRow("opex_total", "Total operating expenses", "line", "opex_total", bold=True, total=True),
        StmtRow("ebitda", "EBITDA", "line", "ebitda", bold=True, total=True),
        StmtRow("ebitda_m", "EBITDA margin", "formula", margin % "ebitda", "pct"),
        StmtRow("dep", "Depreciation", "line", "dep"),
        StmtRow("ebit", "EBIT", "line", "ebit", bold=True),
        StmtRow("interest", "Interest", "line", "interest"),
        StmtRow("ebt", "Pre-tax income", "line", "ebt", total=True),
        StmtRow("tax", "Income tax", "line", "tax"),
        StmtRow("ni", "Net income", "line", "ni", bold=True, total=True),
        StmtRow("ni_m", "Net margin", "formula", margin % "ni", "pct"),
    ]
    return rows


def _cf_rows(liabs: list[Line]) -> list[StmtRow]:
    rows = [
        StmtRow("ni", "Net income", "line", "ni"),
        StmtRow("dep", "Add back depreciation", "line", "dep", neg=True),
        StmtRow("d_ar", "(Increase) / decrease in receivables", "line", "d_ar"),
        StmtRow("d_inv", "(Increase) / decrease in inventory", "line", "d_inv"),
        StmtRow("d_ap", "Increase / (decrease) in payables", "line", "d_ap"),
        *[
            StmtRow(
                f"d_{ln.key}", f"Increase / (decrease) in {ln.label[0].lower() + ln.label[1:]}", "line", f"d_{ln.key}"
            )
            for ln in liabs
        ],
        StmtRow("cfo", "Operating cash flow", "line", "cfo", bold=True, total=True),
        StmtRow("cfi", "Capital spending", "line", "cfi"),
        StmtRow("equity_in", "Equity raised", "line", "equity_in"),
        StmtRow("loan_draw", "Loan drawdown", "line", "loan_draw"),
        StmtRow("loan_repay", "Loan repayment", "line", "loan_repay"),
        StmtRow("cff", "Financing cash flow", "line", "cff", bold=True, total=True),
        StmtRow("net_cf", "Net change in cash", "line", "net_cf", bold=True),
        StmtRow("cash_open", "Opening cash", "line", "cash_open"),
        StmtRow("cash_close", "Closing cash", "line", "cash_close", bold=True, total=True),
    ]
    return rows


def _bs_rows(liabs: list[Line]) -> list[StmtRow]:
    return [
        StmtRow("cash", "Cash", "line", "cash_close"),
        StmtRow("ar", "Accounts receivable", "line", "ar"),
        StmtRow("inv", "Inventory", "line", "inv"),
        StmtRow("ppe_net", "Net fixed assets", "line", "ppe_net"),
        StmtRow("total_assets", "Total assets", "line", "total_assets", bold=True, total=True),
        StmtRow("ap", "Accounts payable", "line", "ap"),
        *[StmtRow(ln.key, ln.label, "line", ln.key) for ln in liabs],
        StmtRow("loan", "Loan", "line", "loan_close"),
        StmtRow("total_liab", "Total liabilities", "line", "total_liab", total=True),
        StmtRow("paid_in", "Paid-in capital", "line", "paid_in"),
        StmtRow("retained", "Retained earnings", "line", "retained"),
        StmtRow("total_equity", "Total equity", "line", "total_equity", total=True),
        StmtRow("total_le", "Total liabilities & equity", "line", "total_le", bold=True, total=True),
        StmtRow("bs_diff", "Check: assets − liabilities − equity (must be 0)", "line", "bs_diff"),
    ]


def _summary_rows() -> list[StmtRow]:
    margin = "=IF({rev}=0,0,{%s}/{rev})"
    return [
        StmtRow("rev", "Revenue", "line", "rev", bold=True),
        StmtRow("gp", "Gross profit", "line", "gp"),
        StmtRow("gm", "Gross margin", "formula", margin % "gp", "pct"),
        StmtRow("opex_total", "Total operating expenses", "line", "opex_total"),
        StmtRow("ebitda", "EBITDA", "line", "ebitda", bold=True, total=True),
        StmtRow("ebitda_m", "EBITDA margin", "formula", margin % "ebitda", "pct"),
        StmtRow("ni", "Net income", "line", "ni", bold=True),
        StmtRow("cash", "Year-end cash", "line", "cash_close", bold=True, total=True),
        StmtRow("loan", "Year-end loan balance", "line", "loan_close"),
    ]


def plan(brief: Brief, tpl: Template) -> Plan:
    tpl.validate(brief)
    t = Timing(brief.granularity, brief.horizon_years)
    calc, hc, bs = _calc_lines(tpl, brief, t)
    all_lines = calc + hc + bs
    lines = {ln.key: ln for ln in all_lines}
    if len(lines) != len(all_lines):
        raise ValueError("duplicate line keys in template")
    for k in ("rev", "cogs", "capex"):
        if k not in lines:
            raise ValueError(f"template {tpl.key!r} must define line {k!r}")
    grid_name = "Monthly" if t.granularity == "monthly" else "Annual"
    blocks: dict[str, Block] = {}
    if brief.tier == "full":
        sheets = ["Dashboard", "Inputs", grid_name, "P&L", "Cash Flow", "Balance Sheet", "Headcount", "Checks"]
        grids = [GridPlan(grid_name, 3, calc + bs), GridPlan("Headcount", 3, hc)]
        blocks["pl"] = Block("pl", "P&L", 3, _pl_rows(tpl, t, lines), "Annual profit & loss")
        liabs = tpl.liability_lines(t)
        blocks["cf"] = Block("cf", "Cash Flow", 3, _cf_rows(liabs), "Annual cash flow statement")
        blocks["bs"] = Block("bs", "Balance Sheet", 3, _bs_rows(liabs), "Balance sheet at year end")
        kpis = tpl.kpi_rows(t)
        if kpis:
            blocks["kpi"] = Block("kpi", "Dashboard", DASH_KPI_ROW, kpis, tpl.kpi_title)
        selector = ("Dashboard", "B4")
        calc_sheet = grid_name
    else:
        sheets = ["Inputs", "P&L", "Checks"]
        summary = Block("sum", "P&L", 3, _summary_rows(), "Annual summary")
        _layout_block(summary)
        blocks["sum"] = summary
        start = max(summary.placed.values()) + 3
        kpis = tpl.kpi_rows(t)
        if kpis:
            kb = Block("kpi", "P&L", start, kpis, tpl.kpi_title)
            _layout_block(kb)
            blocks["kpi"] = kb
            start = max(kb.placed.values()) + 3
        grids = [GridPlan("P&L", start, calc + hc)]
        selector = ("Inputs", "B3")
        calc_sheet = "P&L"
    for g in grids:
        _layout_grid(g)
    for b in blocks.values():
        if not b.placed:
            _layout_block(b)
    specs = tpl.all_specs(brief.roles)
    input_row = _input_rows(specs)
    pl = Plan(brief, tpl, t, specs, lines, grids, blocks, sheets, selector, input_row, calc_sheet)
    for g in grids:
        for k, r in g.rows.items():
            pl.line_at[k] = (g.sheet, r)
    return pl


def _input_rows(specs: list[DriverSpec]) -> dict[str, int]:
    rows, r, last_sec = {}, 6, None
    for s in specs:
        if s.section != last_sec:
            r += 1 if last_sec is not None else 0
            r += 1  # section header row
            last_sec = s.section
        rows[s.key] = r
        r += 1
    return rows


# --------------------------------------------------------------------------- writing
def _write_inputs(wb: Workbook, pl: Plan) -> None:
    ws = wb["Inputs"]
    st.title(ws, "Inputs — Low / Base / High", pl.brief.assumption_note or None, 7)
    sel_sheet, sel_cell = pl.selector
    if sel_sheet == "Inputs":
        _write_selector(ws, 3, pl.brief.default_scenario)
    hdr = ["Driver", "Low", "Base", "High", "Active", "Unit", "Note"]
    for i, h in enumerate(hdr, 1):
        st.header(ws.cell(row=5, column=i, value=h), right=i not in (1, 6, 7))
    sel = f"{q(sel_sheet)}!${sel_cell[0]}${sel_cell[1:]}"
    last_sec = None
    given = {d.key: d for d in pl.brief.drivers}
    for s in pl.specs:
        r = pl.input_row[s.key]
        if s.section != last_sec:
            st.section(ws, r - 1, s.section, 7)
            last_sec = s.section
        d = given[s.key]
        ws.cell(row=r, column=1, value=s.label).font = st.font()
        for col, v in ((2, d.low), (3, d.base), (4, d.high)):
            c = ws.cell(row=r, column=col, value=int(v) if s.integer else v)
            c.font = st.font(st.BLUE)
            c.number_format = FORMATS[s.fmt]
        act = ws.cell(row=r, column=5, value=f"=CHOOSE({sel},B{r},C{r},D{r})")
        act.font = st.font(bold=True)
        act.number_format = FORMATS[s.fmt]
        ws.cell(row=r, column=6, value=s.unit).font = st.font(st.GREY)
        note = d.note or {"asc": "Low ≤ Base ≤ High", "desc": "Low ≥ Base ≥ High (lower is better)"}.get(s.order, "")
        ws.cell(row=r, column=7, value=note).font = st.font(st.GREY, size=9)
    last = max(pl.input_row.values())
    ws.cell(
        row=last + 2,
        column=1,
        value=(
            "Legend: blue = input you can change · black = formula · green = link to another sheet · "
            "yellow = scenario selector. Column E follows the selected scenario."
        ),
    ).font = st.font(st.GREY, size=9, italic=True)
    for col, w in zip("ABCDEFG", (46, 12, 12, 12, 12, 12, 30), strict=True):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "B6"


def _write_selector(ws, row: int, default: int) -> None:
    ws.cell(row=row, column=1, value="Scenario selector (1 = Low, 2 = Base, 3 = High)").font = st.font(bold=True)
    c = ws.cell(row=row, column=2, value=int(default))
    c.font = st.font(st.BLUE, bold=True)
    c.fill = st.YELLOW_FILL
    c.alignment = Alignment(horizontal="center")
    lab = ws.cell(row=row, column=3, value=f'=CHOOSE(B{row},"Low","Base","High")')
    lab.font = st.font(st.ORANGE, bold=True)
    dv = DataValidation(
        type="list",
        formula1='"1,2,3"',
        allow_blank=False,
        showErrorMessage=True,
        errorTitle="Scenario",
        error="Enter 1, 2 or 3",
    )
    ws.add_data_validation(dv)
    dv.add(f"B{row}")


def _write_grid(wb: Workbook, pl: Plan, g: GridPlan, title: str, sub: str) -> None:
    ws = wb[g.sheet]
    n = pl.t.periods
    width = min(2 + n, 16)
    if g.start_row == 3:
        st.title(ws, title, sub, width)
    else:
        st.section(ws, g.start_row - 1, title, width)
    word = "M" if pl.t.granularity == "monthly" else "Y"
    ws.cell(row=g.start_row, column=1, value=f"{pl.t.period_word.capitalize()}").font = st.font(bold=True)
    ws.cell(row=g.period_row, column=1, value="Period #").font = st.font(st.GREY, size=9)
    ws.cell(row=g.year_row, column=1, value="Year #").font = st.font(st.GREY, size=9)
    for p in range(1, n + 1):
        col = FIRST_COL + p - 1
        st.header(ws.cell(row=g.start_row, column=col, value=f"{word}{p}"), right=True)
        c = ws.cell(row=g.period_row, column=col, value=p)
        c.font = st.font(st.BLUE, size=9)
        y = ws.cell(row=g.year_row, column=col, value=f"=ROUNDUP({L(col)}{g.period_row}*{pl.t.mpp}/12,0)")
        y.font = st.font(st.GREY, size=9)
        ws.column_dimensions[L(col)].width = 11
    for r, text in g.sections.items():
        st.section(ws, r, text, width)
    for ln in g.lines:
        r = g.rows[ln.key]
        helper = ln.label.startswith("Helper")
        ws.cell(row=r, column=1, value=ln.label).font = st.font(
            st.GREY if helper else "000000", bold=ln.bold, size=9 if helper else 10
        )
        for p in range(1, n + 1):
            f = pl.render(ln, p, g.sheet)
            c = ws.cell(row=r, column=FIRST_COL + p - 1, value=f)
            c.font = st.font(st.GREEN if PURE_LINK.match(f) else "000000", bold=ln.bold)
            c.number_format = FORMATS[ln.fmt]
            if ln.total:
                c.border = st.TOTAL_TOP
    ws.column_dimensions["A"].width = 44
    ws.column_dimensions["B"].width = 2
    ws.freeze_panes = ws.cell(row=g.year_row + 1, column=FIRST_COL)


def _write_block(wb: Workbook, pl: Plan, b: Block, sub: str | None) -> None:
    ws = wb[b.sheet]
    years = pl.t.years
    if b.start_row == 3:
        st.title(
            ws,
            b.title if b.sheet != "P&L" or pl.brief.tier == "full" else f"{pl.brief.model_name} — P&L",
            sub,
            1 + years,
        )
    elif b.title:
        st.section(ws, b.start_row - 1, b.title, max(3, 1 + years))
    ws.cell(row=b.year_row, column=1, value="Year #").font = st.font(st.GREY, size=9)
    for y in range(1, years + 1):
        ws.cell(row=b.year_row, column=1 + y, value=y).font = st.font(st.GREY, size=9)
        st.header(ws.cell(row=b.year_row + 1, column=1 + y, value=f"Year {y}"), right=True)
        ws.column_dimensions[L(1 + y)].width = 14
    for row in b.rows:
        r = b.placed[row.key]
        ws.cell(row=r, column=1, value=row.label).font = st.font(bold=row.bold)
        for y in range(1, years + 1):
            col = L(1 + y)
            if row.kind == "line":
                ln = pl.lines[row.src]
                f = _rollup(pl, ln, col, b.year_row)
                if row.neg:
                    f = "=-" + f[1:]
            elif row.kind == "formula":
                # {key} = another row of this table in the same year; {in:driver} = the live input cell
                f = TOKEN.sub(
                    lambda m, col=col: (
                        pl.input_ref(m.group(1)[3:]) if m.group(1).startswith("in:") else f"{col}{b.placed[m.group(1)]}"
                    ),
                    row.src,
                )
            else:
                raise ValueError(row.kind)
            c = ws.cell(row=r, column=1 + y, value=f)
            c.font = st.font(bold=row.bold)
            c.number_format = FORMATS[row.fmt]
            if row.total:
                c.border = st.TOTAL_TOP
    ws.column_dimensions["A"].width = max(ws.column_dimensions["A"].width or 0, 44)
    if b.start_row == 3:
        ws.freeze_panes = f"B{b.year_row + 2}"


def _rollup(pl: Plan, ln: Line, col: str, year_row: int) -> str:
    rng = pl.grid_range(ln.key)
    sheet, _ = pl.line_at[ln.key]
    g = next(g for g in pl.grids if g.sheet == sheet)
    yr = f"{q(sheet)}!${L(FIRST_COL)}${g.year_row}:${L(FIRST_COL + pl.t.periods - 1)}${g.year_row}"
    ppy = pl.t.ppy
    if ln.agg == "sum":
        return f"=SUMIF({yr},{col}${year_row},{rng})"
    if ln.agg == "last":
        return f"=INDEX({rng},{col}${year_row}*{ppy})"
    if ln.agg == "first":
        return f"=INDEX({rng},({col}${year_row}-1)*{ppy}+1)"
    raise ValueError(f"line {ln.key!r} has agg={ln.agg!r} and cannot be rolled up")


def _write_dashboard(wb: Workbook, pl: Plan, checks_verdict: str) -> None:
    ws = wb["Dashboard"]
    years = pl.t.years
    st.title(
        ws,
        pl.brief.model_name,
        "Change the scenario in B4 (1 = Low, 2 = Base, 3 = High); every sheet recalculates.",
        max(3, 1 + years),
    )
    _write_selector(ws, 4, pl.brief.default_scenario)
    ws["A4"] = "Scenario selector"
    st.section(ws, 6, "Key metrics", max(3, 1 + years))
    for y in range(1, years + 1):
        st.header(ws.cell(row=7, column=1 + y, value=f"Year {y}"), right=True)
    metrics = [
        ("Revenue", "pl", "rev", "usd"),
        ("Gross profit", "pl", "gp", "usd"),
        ("EBITDA", "pl", "ebitda", "usd"),
        ("EBITDA margin", "pl", "ebitda_m", "pct"),
        ("Net income", "pl", "ni", "usd"),
        ("Year-end cash", "bs", "cash", "usd"),
        ("Year-end loan balance", "bs", "loan", "usd"),
        ("Total FTE (year end)", None, "fte_total", "dec1"),
    ]
    r = 8
    for label, block, key, fmt in metrics:
        ws.cell(row=r, column=1, value=label).font = st.font(bold=label in ("Revenue", "EBITDA"))
        for y in range(1, years + 1):
            if block:
                f = f"={pl.stmt_cell(block, key, y)}"
            else:
                f = f"=INDEX({pl.grid_range(key)},{y * pl.t.ppy})"
            c = ws.cell(row=r, column=1 + y, value=f)
            c.font = st.font(st.GREEN if PURE_LINK.match(f) else "000000")
            c.number_format = FORMATS[fmt]
        r += 1
    r += 1
    st.section(ws, r, "Health", max(3, 1 + years))
    word = pl.t.period_word
    pos, cash = pl.grid_range("pos_flag"), pl.grid_range("cash_close")
    low_row = r + 2
    health = [
        (f"First {word} with positive EBITDA", f'=IFERROR(MATCH(1,{pos},0),"Not within horizon")', "0"),
        ("Lowest cash balance", f"=MIN({cash})", FORMATS["usd"]),
        (f"{word.capitalize()} of lowest cash", f"=MATCH(B{low_row},{cash},0)", "0"),
        ("Model checks", f"={checks_verdict}", "@"),
    ]
    for i, (label, f, fmt) in enumerate(health):
        ws.cell(row=r + 1 + i, column=1, value=label).font = st.font()
        c = ws.cell(row=r + 1 + i, column=2, value=f)
        c.font = st.font(st.GREEN if PURE_LINK.match(f) else "000000", bold=True)
        c.number_format = fmt
    ws.column_dimensions["A"].width = 40
    for y in range(1, max(3, years) + 1):
        ws.column_dimensions[L(1 + y)].width = 14


def _write_checks(wb: Workbook, pl: Plan) -> str:
    ws = wb["Checks"]
    st.title(ws, "Model checks", "Live formulas: they re-run every time an input changes.", 3)
    for i, h in enumerate(["Check", "Result", "What it tests"], 1):
        st.header(ws.cell(row=3, column=i, value=h))
    sel_sheet, sel_cell = pl.selector
    sel = f"{q(sel_sheet)}!{sel_cell}"
    stmt = "pl" if "pl" in pl.blocks else "sum"
    gr = pl.grid_range

    def ok(cond: str, warn: bool = False) -> str:
        return f'=IF({cond},"PASS","{"WARN" if warn else "FAIL"}")'

    checks = [
        (
            "Annual revenue ties to period detail",
            ok(f"ABS(SUM({pl.stmt_range(stmt, 'rev')})-SUM({gr('rev')}))<0.5"),
            "Sum of annual revenue equals the sum of every period",
        ),
        (
            "Annual net income ties to period detail",
            ok(f"ABS(SUM({pl.stmt_range(stmt, 'ni')})-SUM({gr('ni')}))<0.5"),
            "Sum of annual net income equals the sum of every period",
        ),
        (
            "EBITDA reconciliation",
            ok(f"ABS(SUM({gr('ebitda')})-SUM({gr('gp')})-SUM({gr('opex_total')}))<0.5"),
            "EBITDA = gross profit + operating expenses (costs are negative)",
        ),
        (
            "Cash roll-forward",
            ok(f"ABS(INDEX({gr('cash_close')},{pl.t.periods})-SUM({gr('net_cf')}))<0.5"),
            "Closing cash = all net cash flows since the start (opening cash is zero)",
        ),
        (
            "Scenario selector valid",
            ok(f"AND(ISNUMBER({sel}),{sel}>=1,{sel}<=3,INT({sel})={sel})"),
            f"{sel} is 1, 2 or 3",
        ),
    ]
    ordered = [s for s in pl.specs if s.order != "none"]
    if ordered:
        conds = []
        for s in ordered:
            lo, ba, hi = (pl.input_col(s.key, c) for c in "BCD")
            conds.append(f"{lo}<={ba},{ba}<={hi}" if s.order == "asc" else f"{lo}>={ba},{ba}>={hi}")
        checks.append(
            (
                "Scenario ordering of drivers",
                ok(f"AND({','.join(conds)})"),
                "Low / Base / High ordered the right way for every growth and cost driver",
            )
        )
    checks += [
        (
            "Gross margin within 0–100%",
            ok(f"AND(MIN({pl.stmt_range(stmt, 'gm')})>=0,MAX({pl.stmt_range(stmt, 'gm')})<=1)"),
            "Gross margin never negative or above 100%",
        ),
        ("Loan balance never negative", ok(f"MIN({gr('loan_close')})>=-0.5"), "Repayments never exceed the loan"),
    ]
    err_terms = []
    for g in pl.grids:
        rng = f"{q(g.sheet)}!${L(FIRST_COL)}${g.period_row}:${L(FIRST_COL + pl.t.periods - 1)}${g.end_row}"
        err_terms.append(f"SUMPRODUCT(--ISERROR({rng}))")
    for b in pl.blocks.values():
        last = max(b.placed.values())
        err_terms.append(f"SUMPRODUCT(--ISERROR({q(b.sheet)}!$B${b.year_row}:${L(1 + pl.t.years)}${last}))")
    checks.append(
        (
            "No error values",
            ok(f"{'+'.join(err_terms)}=0"),
            "No error values (divide-by-zero, broken references) on any calculation sheet",
        )
    )
    if "bs" in pl.blocks:
        checks.append(
            (
                "Balance sheet balances every period",
                ok(f"SUMPRODUCT(--(ABS({gr('bs_diff')})>0.5))=0"),
                "Assets = liabilities + equity in every period",
            )
        )
    checks.append(
        (
            "Funding sufficient (cash ≥ 0)",
            ok(f"MIN({gr('cash_close')})>=0", warn=True),
            "Business warning, not an error: cash dips below zero in this scenario",
        )
    )
    first = 4
    for i, (name, f, desc) in enumerate(checks):
        r = first + i
        ws.cell(row=r, column=1, value=name).font = st.font()
        ws.cell(row=r, column=2, value=f).font = st.font(bold=True)
        ws.cell(row=r, column=3, value=desc).font = st.font(st.GREY, size=9)
    last = first + len(checks) - 1
    vr = last + 2
    ws.cell(row=vr, column=1, value="Overall verdict").font = st.font(bold=True)
    c = ws.cell(
        row=vr,
        column=2,
        value=(
            f'=IF(COUNTIF(B{first}:B{last},"FAIL")>0,"FAIL",'
            f'IF(COUNTIF(B{first}:B{last},"WARN")>0,"PASS WITH WARNINGS","PASS"))'
        ),
    )
    c.font = st.font(bold=True)
    c.border = st.TOTAL_TOP
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 64
    return f"Checks!B{vr}"


def manifest_for(pl: Plan, verdict: str) -> Manifest:
    years = range(1, pl.t.years + 1)
    if pl.brief.tier == "full":
        src = {
            "rev": ("pl", "rev"),
            "gp": ("pl", "gp"),
            "ebitda": ("pl", "ebitda"),
            "ni": ("pl", "ni"),
            "cash": ("bs", "cash"),
            "loan": ("bs", "loan"),
            "total_assets": ("bs", "total_assets"),
            "total_le": ("bs", "total_le"),
            "cfo": ("cf", "cfo"),
        }
    else:
        src = {
            "rev": ("sum", "rev"),
            "gp": ("sum", "gp"),
            "ebitda": ("sum", "ebitda"),
            "ni": ("sum", "ni"),
            "cash": ("sum", "cash"),
            "loan": ("sum", "loan"),
        }
    if "kpi" in pl.blocks:
        src.update({f"kpi:{k}": ("kpi", k) for k in pl.template.kpi_checked})
    metrics = {m: {y: pl.stmt_cell(b, k, y) for y in years} for m, (b, k) in src.items()}
    sheet, cell = pl.selector
    return Manifest(
        pl.brief.tier,
        pl.t.granularity,
        pl.t.years,
        pl.sheets,
        f"{sheet}!{cell}",
        verdict,
        metrics,
        {k: pl.grid_range(k) for k in ("rev", "ebitda", "ni", "cash_close")},
    )


def build(brief: Brief, tpl: Template, out_path: str | Path) -> Manifest:
    pl = plan(brief, tpl)
    wb = Workbook()
    wb.active.title = pl.sheets[0]
    for name in pl.sheets[1:]:
        wb.create_sheet(name)
    _write_inputs(wb, pl)
    unit = "$ unless stated; costs shown as negatives. Every period uses the same formula."
    for g in pl.grids:
        if g.sheet == "Headcount":
            _write_grid(wb, pl, g, "Headcount & payroll", unit)
        elif pl.brief.tier == "full":
            _write_grid(wb, pl, g, f"{pl.t.period_word.capitalize()}ly projection".replace("Yearly", "Annual"), unit)
        else:
            _write_grid(wb, pl, g, f"{pl.t.period_word.capitalize()}ly detail".replace("Yearly", "Annual"), unit)
    for b in pl.blocks.values():
        _write_block(wb, pl, b, "Rolled up from the period detail (SUMIF on the year row; balances at year end).")
    verdict = _write_checks(wb, pl)
    if "Dashboard" in pl.sheets:
        _write_dashboard(wb, pl, verdict)
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False
    wb.save(out_path)
    return manifest_for(pl, verdict)
