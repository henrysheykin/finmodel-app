"""Goal-module sheets (E07): Break-even, Valuation and the investor Summary.

``plan_modules`` lays every module out while the plan is built (so the challenger's manifest knows
each cell), ``write_modules`` writes them, ``module_checks`` adds their rows to the Checks sheet. The
numbers come from the period grid (the same calculation every tier shows); this file only rearranges
and discounts them. Economics and their plain-Python twin: ``engine/goals.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from openpyxl.utils import get_column_letter as L

from engine import style as st
from engine.builder import FIRST_COL, PURE_LINK, Block, Plan, StmtRow, _layout_block, q
from engine.goals import NA, NOT_WITHIN, NOTHING_TO_PAY_BACK, modules_for
from engine.spec import FORMATS

SHEETS = {"breakeven": "Break-even", "dcf": "Valuation", "summary": "Summary"}
INT = "0"


@dataclass
class Row:
    row: int
    label: str
    values: dict[str, str]  # column letter -> formula
    fmt: dict[str, str]  # column letter -> number format
    bold: bool = False
    note: str = ""
    total: bool = False


@dataclass
class ModuleLayout:
    sheet: str
    title: str
    sub: str
    block: str = ""  # block whose rows the challenger checks per year
    checked_rows: tuple[str, ...] = ()
    cells: dict[str, str] = field(default_factory=dict)  # checked single cells: name -> 'Sheet'!B7
    local: dict[str, str] = field(default_factory=dict)  # name -> B7 (same-sheet reference)
    rows: list[Row] = field(default_factory=list)
    sections: dict[int, str] = field(default_factory=dict)
    headers: dict[int, dict[str, str]] = field(default_factory=dict)  # row -> {col: header text}
    notes: dict[int, str] = field(default_factory=dict)
    error_range: str = ""
    width: int = 6


class _Sheet:
    """Row cursor that records labelled rows and the cells other formulas need."""

    def __init__(self, lay: ModuleLayout, start: int):
        self.lay, self.r = lay, start

    def section(self, text: str) -> None:
        self.lay.sections[self.r] = text
        self.r += 1

    def header(self, cols: dict[str, str]) -> None:
        self.lay.headers[self.r] = cols
        self.r += 1

    def row(self, name: str, label: str, values, fmt="usd", checked=True, **kw) -> int:
        if isinstance(values, str):
            values = {"B": values}
        fmts = fmt if isinstance(fmt, dict) else dict.fromkeys(values, fmt)
        fmts = {c: FORMATS.get(f, f) for c, f in fmts.items()}
        self.lay.rows.append(Row(self.r, label, values, fmts, **kw))
        for col in values:
            key = name if col == "B" else f"{name}_{col.lower()}"
            self.lay.local[key] = f"{col}{self.r}"
            if checked and col == "B":
                self.lay.cells[name] = f"{q(self.lay.sheet)}!B{self.r}"
        self.r += 1
        return self.r - 1

    def abs(self, name: str) -> str:
        ref = self.lay.local[name]
        return f"${ref[0]}${ref[1:]}"

    def blank(self, n: int = 1) -> None:
        self.r += n


def _scenario_label(pl: Plan) -> str:
    sheet, cell = pl.selector
    return f'=CHOOSE({q(sheet)}!${cell[0]}${cell[1:]},"Low","Base","High")'


def _period_row(pl: Plan) -> str:
    g = next(g for g in pl.grids if g.sheet == pl.calc_sheet)
    return f"{q(g.sheet)}!${L(FIRST_COL)}${g.period_row}:${L(FIRST_COL + pl.t.periods - 1)}${g.period_row}"


def _link(pl: Plan, key: str) -> str:
    return f"={pl.input_ref(key)}"


# --------------------------------------------------------------------------- Break-even
def _plan_breakeven(pl: Plan) -> ModuleLayout:
    word = pl.t.period_word
    lay = ModuleLayout(
        "Break-even",
        "Startup costs, funding need and break-even",
        f"Live for the selected scenario. Periods are counted in {word}s from the start of the plan.",
    )
    s = _Sheet(lay, 5)
    gr, prow = pl.grid_range, _period_row(pl)
    s.section("Startup costs & funding need (up to the lowest cash point)")
    low = s.row("low_p", f"Lowest cash point ({word} #)", f"=MATCH(MIN({gr('cash_close')}),{gr('cash_close')},0)", INT)
    lo = f"$B${low}"
    a = s.row(
        "capex_to_low",
        "Capital spending up to the lowest cash point",
        f"=SUMPRODUCT(--({prow}<={lo}),{gr('capex')})",
    )
    b = s.row(
        "burn_to_low",
        "Operating cash burn up to the lowest cash point",
        f"=-SUMPRODUCT(--({prow}<={lo}),{gr('cfo')})",
        note="Losses and working capital before the business funds itself",
    )
    c = s.row(
        "repay_to_low",
        "Loan repayments up to the lowest cash point",
        f"=-SUMPRODUCT(--({prow}<={lo}),{gr('loan_repay')})",
    )
    uses = s.row("uses", "Total uses of funds", f"=B{a}+B{b}+B{c}", bold=True, total=True)
    buf = s.row("buffer", "Minimum cash buffer to keep", _link(pl, "cash_buffer"), note="Input on the Inputs sheet")
    req = s.row("required", "Funding required (uses + buffer)", f"=B{uses}+B{buf}", bold=True, total=True)
    s.blank()
    eq = s.row("equity", "Equity raised", _link(pl, "equity"), checked=False)
    ln = s.row("loan", "Loan drawn", _link(pl, "loan_amount"), checked=False)
    src = s.row("sources", "Total sources of funds", f"=B{eq}+B{ln}", bold=True, total=True)
    s.row(
        "gap",
        "Funding surplus / (shortfall)",
        f"=B{src}-B{req}",
        bold=True,
        note="Negative = raise at least this much more",
    )
    s.row("min_cash", "Lowest cash balance in the plan", f"=MIN({gr('cash_close')})", note="Equals sources minus uses")
    s.blank()
    s.section("Break-even timing")
    s.row(
        "first_ebitda",
        f"First {word} with positive EBITDA ({word} #)",
        f'=IFERROR(MATCH(1,{gr("pos_flag")},0),"{NOT_WITHIN}")',
        INT,
    )
    s.row(
        "first_ni",
        f"First {word} with positive net income ({word} #)",
        f'=IFERROR(MATCH(1,{gr("ni_flag")},0),"{NOT_WITHIN}")',
        INT,
    )
    s.row(
        "payback",
        f"Cash invested paid back ({word} #)",
        f'=IF(MIN({gr("cum_pre_fin")})>=0,"{NOTHING_TO_PAY_BACK}",'
        f'IFERROR(MATCH(1,{gr("payback_flag")},0),"{NOT_WITHIN}"))',
        INT,
        note="Cumulative operating + investing cash flow back to zero",
    )
    rows = [
        StmtRow("rev", "Revenue", "line", "rev", bold=True),
        StmtRow("gp", "Gross profit", "line", "gp"),
        StmtRow("gm", "Gross margin (contribution)", "formula", "=IF({rev}=0,0,{gp}/{rev})", "pct"),
        StmtRow("fixed", "Operating expenses (treated as fixed)", "line", "opex_total", neg=True),
        StmtRow(
            "be_rev", "Break-even revenue (EBITDA = 0)", "formula", f'=IF({{gm}}>0,{{fixed}}/{{gm}},"{NA}")', bold=True
        ),
        StmtRow(
            "mos",
            "Margin of safety (revenue above break-even)",
            "formula",
            f'=IF(AND(ISNUMBER({{be_rev}}),{{rev}}>0),({{rev}}-{{be_rev}})/{{rev}},"{NA}")',
            "pct",
        ),
    ]
    blk = Block("be", lay.sheet, s.r + 2, rows, "Annual break-even revenue")
    _layout_block(blk)
    pl.blocks["be"] = blk
    lay.block, lay.checked_rows = "be", ("gm", "be_rev", "mos")
    end = max(blk.placed.values()) + 2
    lay.notes[end] = (
        "Simplification: cost of sales is treated as variable and operating expenses as fixed, so break-even "
        "revenue = operating expenses ÷ gross margin."
    )
    lay.width = max(3, 1 + pl.t.years)
    lay.error_range = f"{q(lay.sheet)}!$B$3:${L(max(3, 1 + pl.t.years))}${end}"
    return lay


# --------------------------------------------------------------------------- Valuation
def _plan_dcf(pl: Plan) -> ModuleLayout:
    H = pl.t.years
    lay = ModuleLayout(
        "Valuation",
        "Discounted cash flow valuation",
        "Enterprise value at the start of the plan, before the funding raised in period 1. Year-end discounting.",
    )
    s = _Sheet(lay, 5)
    s.section("Assumptions (active scenario, from the Inputs sheet)")
    for key, label, fmt in (
        ("wacc", "Discount rate (WACC)", "pct"),
        ("tg", "Terminal growth rate", "pct"),
        ("exit_mult", "Exit multiple (EV ÷ final-year EBITDA)", "x"),
        ("tax_rate", "Tax rate (for the interest tax shield)", "pct"),
        ("wacc_step", "Sensitivity step: WACC", "pct"),
        ("g_step", "Sensitivity step: terminal growth", "pct"),
    ):
        s.row(key, label, _link(pl, key), fmt, checked=False)
    w, g, mult = s.abs("wacc"), s.abs("tg"), s.abs("exit_mult")
    rows = [
        StmtRow("ebitda", "EBITDA", "line", "ebitda"),
        StmtRow("fcff", "Unlevered free cash flow", "line", "fcff", bold=True),
        StmtRow("df", "Discount factor", "formula", "=1/(1+{in:wacc})^{year}", "dec3"),
        StmtRow("pv", "Present value of free cash flow", "formula", "={fcff}*{df}"),
    ]
    blk = Block("dcf", lay.sheet, s.r + 2, rows, "Free cash flow by year")
    _layout_block(blk)
    pl.blocks["dcf"] = blk
    lay.block, lay.checked_rows = "dcf", ("fcff", "df", "pv")
    last = L(1 + H)
    hy = f"${last}${blk.year_row}"
    fcf_h, ebitda_h = f"${last}${blk.placed['fcff']}", f"${last}${blk.placed['ebitda']}"
    fcf_rng = f"$B${blk.placed['fcff']}:${last}${blk.placed['fcff']}"
    yr_rng = f"$B${blk.year_row}:${last}${blk.year_row}"
    pv_rng = f"$B${blk.placed['pv']}:${last}${blk.placed['pv']}"
    s.r = max(blk.placed.values()) + 2
    s.section("Enterprise value")
    s.header({"B": "Perpetual growth", "C": "Exit multiple"})
    sp = s.r
    s.row("sum_pv", "Present value of the plan's free cash flows", {"B": f"=SUM({pv_rng})", "C": f"=B{sp}"})
    bs = s.row(
        "basis",
        "Final-year free cash flow | final-year EBITDA",
        {"B": f"={fcf_h}", "C": f"={ebitda_h}"},
        checked=False,
    )
    tv = s.row(
        "tv_g",
        f"Terminal value at the end of year {H}",
        {"B": f"=IF({w}>{g},B{bs}*(1+{g})/({w}-{g}),0)", "C": f"=C{bs}*{mult}"},
    )
    pv = s.row(
        "pv_tv_g",
        "Present value of the terminal value",
        {"B": f"=B{tv}/(1+{w})^{hy}", "C": f"=C{tv}/(1+{w})^{hy}"},
    )
    ev = s.row("ev_g", "Enterprise value", {"B": f"=B{sp}+B{pv}", "C": f"=C{sp}+C{pv}"}, bold=True, total=True)
    s.row(
        "tv_share_g",
        "Terminal value share of enterprise value",
        {"B": f"=IF(B{ev}<>0,B{pv}/B{ev},0)", "C": f"=IF(C{ev}<>0,C{pv}/C{ev},0)"},
        "pct",
    )
    s.row(
        "implied_mult",
        "Cross-check: implied exit multiple | implied perpetual growth",
        {
            "B": f'=IF(C{bs}>0,B{tv}/C{bs},"{NA}")',
            "C": f'=IF(C{tv}+B{bs}<>0,(C{tv}*{w}-B{bs})/(C{tv}+B{bs}),"{NA}")',
        },
        {"B": "x", "C": "pct"},
    )
    s.row("ev_avg", "Enterprise value — average of the two methods", f"=AVERAGE(B{ev},C{ev})", bold=True)
    # the C-column twins the challenger also checks
    for name, src in (("tv_m", "tv_g"), ("pv_tv_m", "pv_tv_g"), ("ev_m", "ev_g"), ("tv_share_m", "tv_share_g")):
        lay.cells[name] = f"{q(lay.sheet)}!C{lay.local[src][1:]}"
    lay.cells["implied_g"] = f"{q(lay.sheet)}!C{lay.local['implied_mult'][1:]}"
    s.blank()
    s.section("Sensitivity: enterprise value (perpetual growth) by WACC and terminal growth")
    hdr = s.r
    ws_, gs_ = s.abs("wacc_step"), s.abs("g_step")
    cols = "BCDEF"
    g_hdr = {c: f"={g}+({k})*{gs_}" for c, k in zip(cols, range(-2, 3), strict=True)}
    s.header({"A": "WACC ↓ · terminal growth →"} | g_hdr)
    for k in range(-2, 3):
        r = s.r
        vals = {"A": f"={w}+({k})*{ws_}"}
        for c in cols:
            wv, gv = f"$A{r}", f"{c}${hdr}"
            vals[c] = (
                f"=IF({wv}>{gv},SUMPRODUCT({fcf_rng}/(1+{wv})^{yr_rng})"
                f'+{fcf_h}*(1+{gv})/({wv}-{gv})/(1+{wv})^{hy},"{NA}")'
            )
        s.row(f"sens_{k + 2}", "", vals, {"A": "pct"} | dict.fromkeys(cols, "usd"), checked=False)
    lay.cells["sens_centre"] = f"{q(lay.sheet)}!D{hdr + 3}"
    lay.local["sens_centre"] = f"D{hdr + 3}"
    end = s.r + 1
    lay.notes[end] = (
        "Free cash flow = operating cash flow + interest × (1 − tax rate) − capital spending. "
        "Cells marked n/a: WACC not above growth."
    )
    lay.width = max(6, 1 + H)
    lay.error_range = f"{q(lay.sheet)}!$A$3:${L(max(6, 1 + H))}${end}"
    return lay


# --------------------------------------------------------------------------- Summary
def _plan_summary(pl: Plan, be: ModuleLayout, dcf: ModuleLayout) -> ModuleLayout:
    H = pl.t.years
    lay = ModuleLayout(
        "Summary",
        f"{pl.brief.model_name} — investor summary",
        "Headline numbers for the selected scenario; every figure links to the model.",
    )
    margin = "=IF({rev}=0,0,{%s}/{rev})"
    rows = [
        StmtRow("rev", "Revenue", "line", "rev", bold=True),
        StmtRow("gp", "Gross profit", "line", "gp"),
        StmtRow("gm", "Gross margin", "formula", margin % "gp", "pct"),
        StmtRow("ebitda", "EBITDA", "line", "ebitda", bold=True, total=True),
        StmtRow("ebitda_m", "EBITDA margin", "formula", margin % "ebitda", "pct"),
        StmtRow("ni", "Net income", "line", "ni"),
        StmtRow("cash", "Year-end cash", "line", "cash_close", bold=True),
        StmtRow("fte", "Team (FTE, year end)", "line", "fte_total", "dec1"),
    ]
    blk = Block("inv", lay.sheet, 6, rows, "Headline financials")
    _layout_block(blk)
    pl.blocks["inv"] = blk
    s = _Sheet(lay, max(blk.placed.values()) + 2)
    s.section("Investment highlights")
    last = L(1 + H)
    r1, rh, hy = f"$B${blk.placed['rev']}", f"${last}${blk.placed['rev']}", f"${last}${blk.year_row}"
    s.row(
        "cagr",
        "Revenue growth per year (CAGR, year 1 to final year)",
        f'=IF(AND({hy}>1,{r1}>0,{rh}>0),({rh}/{r1})^(1/MAX(1,{hy}-1))-1,"{NA}")',
        "pct",
    )

    def xlink(m: ModuleLayout, name: str) -> str:
        return f"={q(m.sheet)}!{m.local[name]}"

    s.row("sum_equity", "Equity raised", _link(pl, "equity"), checked=False)
    s.row("sum_loan", "Loan drawn", _link(pl, "loan_amount"), checked=False)
    s.row("sum_required", "Funding required (incl. cash buffer)", xlink(be, "required"), checked=False)
    s.row("sum_gap", "Funding surplus / (shortfall)", xlink(be, "gap"), bold=True)
    s.row("sum_min_cash", "Lowest cash balance", xlink(be, "min_cash"), checked=False)
    word = pl.t.period_word
    s.row("sum_first_ebitda", f"First {word} with positive EBITDA", xlink(be, "first_ebitda"), INT, checked=False)
    s.row("sum_payback", f"Cash invested paid back ({word} #)", xlink(be, "payback"), INT, checked=False)
    s.row("sum_ev_g", "Enterprise value — perpetual growth", xlink(dcf, "ev_g"), checked=False)
    s.row("sum_ev_m", "Enterprise value — exit multiple", xlink(dcf, "ev_g_c"), checked=False)
    s.row("sum_ev_avg", "Enterprise value — average", xlink(dcf, "ev_avg"), bold=True)
    end = s.r
    kpis = pl.template.kpi_rows(pl.t)
    if kpis:
        kb = Block("inv_kpi", lay.sheet, s.r + 2, list(kpis), pl.template.kpi_title)
        _layout_block(kb)
        pl.blocks["inv_kpi"] = kb
        end = max(kb.placed.values())
    lay.width = max(3, 1 + H)
    lay.error_range = f"{q(lay.sheet)}!$B$3:${L(max(3, 1 + H))}${end}"
    return lay


def plan_modules(pl: Plan) -> None:
    mods = modules_for(pl.brief.goal)
    if "breakeven" in mods:
        pl.modules["breakeven"] = _plan_breakeven(pl)
    if "dcf" in mods:
        pl.modules["dcf"] = _plan_dcf(pl)
    if "summary" in mods:
        pl.modules["summary"] = _plan_summary(pl, pl.modules["breakeven"], pl.modules["dcf"])


# --------------------------------------------------------------------------- checks
def module_checks(pl: Plan) -> list[tuple[str, str, str]]:
    def ok(cond: str, warn: bool = False) -> str:
        return f'=IF({cond},"PASS","{"WARN" if warn else "FAIL"}")'

    def ref(mod: str, name: str) -> str:
        m = pl.modules[mod]
        return f"{q(m.sheet)}!{m.local[name]}"

    def be(name: str) -> str:
        return ref("breakeven", name)

    out = []
    if "breakeven" in pl.modules:
        out.append(
            (
                "Funding table ties to the cash flow",
                ok(f"ABS({be('min_cash')}-({be('sources')}-{be('uses')}))<0.5"),
                "Lowest cash balance = sources of funds − uses of funds up to that point",
            )
        )
    if "dcf" in pl.modules:
        blk, last = pl.blocks["dcf"], L(1 + pl.t.years)
        fcf = f"{q(blk.sheet)}!$B${blk.placed['fcff']}:${last}${blk.placed['fcff']}"
        w, g = ref("dcf", "wacc"), ref("dcf", "tg")
        out += [
            (
                "Valuation: discounting ties to NPV()",
                ok(f"ABS({ref('dcf', 'sum_pv')}-NPV({w},{fcf}))<0.5"),
                "Sum of discounted free cash flows equals Excel's NPV of the same flows",
            ),
            ("Valuation: WACC above terminal growth", ok(f"{w}>{g}"), "The perpetual-growth formula needs WACC > g"),
            (
                "Valuation: sensitivity centre = enterprise value",
                ok(f"ABS({ref('dcf', 'sens_centre')}-{ref('dcf', 'ev_g')})<0.5"),
                "The middle of the WACC × growth table reproduces the headline value",
            ),
            (
                "Valuation: final-year cash flow positive",
                ok(f"{q(blk.sheet)}!${last}${blk.placed['fcff']}>0", warn=True),
                "Business warning: a negative final-year cash flow gives a negative terminal value "
                "(often a 1-year plan still carrying start-up spending)",
            ),
        ]
    if "summary" in pl.modules:
        out.append(
            (
                "Summary ties to period detail",
                ok(f"ABS(SUM({pl.stmt_range('inv', 'rev')})-SUM({pl.grid_range('rev')}))<0.5"),
                "Revenue on the Summary sheet equals the sum of every period",
            )
        )
    return out


# --------------------------------------------------------------------------- writing
def write_modules(wb, pl: Plan) -> None:
    for lay in pl.modules.values():
        ws = wb[lay.sheet]
        st.title(ws, lay.title, lay.sub, lay.width)
        ws.cell(row=3, column=1, value="Scenario shown").font = st.font(bold=True)
        c = ws.cell(row=3, column=2, value=_scenario_label(pl))
        c.font = st.font(st.ORANGE, bold=True)
        for r, text in lay.sections.items():
            st.section(ws, r, text, lay.width)
        for r, cols in lay.headers.items():
            for col, text in cols.items():
                cell = ws[f"{col}{r}"]
                cell.value = text
                st.header(cell, right=col != "A")
                if isinstance(text, str) and text.startswith("="):
                    cell.number_format = FORMATS["pct"]
        for row in lay.rows:
            if row.label:
                ws.cell(row=row.row, column=1, value=row.label).font = st.font(bold=row.bold)
            for col, f in row.values.items():
                cell = ws[f"{col}{row.row}"]
                cell.value = f
                cell.font = st.font(st.GREEN if PURE_LINK.match(f) else "000000", bold=row.bold)
                cell.number_format = row.fmt[col]
                if row.total:
                    cell.border = st.TOTAL_TOP
            if row.note:
                ws.cell(row=row.row, column=max(4, len(row.values) + 2), value=row.note).font = st.font(st.GREY, size=9)
        for r, text in lay.notes.items():
            ws.cell(row=r, column=1, value=text).font = st.font(st.GREY, size=9, italic=True)
        ws.column_dimensions["A"].width = 52
        for i in range(2, lay.width + 2):
            ws.column_dimensions[L(i)].width = max(ws.column_dimensions[L(i)].width or 0, 16)
