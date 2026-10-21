"""Goal-module sheets (E07): Break-even, Valuation and the investor Summary.

``plan_modules`` lays every module out while the plan is built (so the challenger's manifest knows
each cell), ``write_modules`` writes them, ``module_checks`` adds their rows to the Checks sheet. The
numbers come from the period grid (the same calculation every tier shows); this file only rearranges
and discounts them. Economics and their plain-Python twin: ``engine/goals.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

from engine import charts as ch
from engine import style as st
from engine.builder import FIRST_COL, PURE_LINK, Block, Plan, StmtRow, _layout_block, q
from engine.dashboard import YEAR_FMT
from engine.goals import NA, NOT_WITHIN, NOTHING_TO_PAY_BACK, modules_for
from engine.kpis import AXIS
from engine.spec import FORMATS

SHEETS = {"breakeven": "Break-even", "dcf": "Valuation", "sources_uses": "Sources & Uses"}
#: rows shown as key totals (double underline, docs/WORKBOOK_STANDARD.md §4)
#: chart columns on Sources & Uses: right of the tables (A–C) and the E spacer, 9 columns per chart
SU_CHART_COLS = ("F", "O")
KEY_TOTAL_LABELS = ("Funding surplus", "Enterprise value — average")
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
    #: input cells on the sheet (view settings, standard §5): cell -> (min, max) whole number
    inputs: dict[str, tuple[int, int]] = field(default_factory=dict)
    #: chart data rows for the sheet's charts
    charts: dict[str, tuple[int, int]] = field(default_factory=dict)


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

    def row(self, name: str, label: str, values, fmt="usd", checked=True, also: tuple[str, ...] = (), **kw) -> int:
        """One row; ``checked`` registers column B with the challenger, ``also`` further columns (``name_c``)."""
        if not isinstance(values, dict):
            values = {"B": values}
        fmts = fmt if isinstance(fmt, dict) else dict.fromkeys(values, fmt)
        fmts = {c: FORMATS.get(f, f) for c, f in fmts.items()}
        self.lay.rows.append(Row(self.r, label, values, fmts, **kw))
        for col in values:
            key = name if col == "B" else f"{name}_{col.lower()}"
            self.lay.local[key] = f"{col}{self.r}"
            if checked and (col == "B" or col in also):
                self.lay.cells[key] = f"{q(self.lay.sheet)}!{col}{self.r}"
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
        "revenue = operating expenses ÷ gross margin. In a year with zero or negative gross margin there is no "
        "break-even revenue (n/a); the chart line shows 0 there."
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


def _breakeven_chart(ws, pl: Plan, lay: ModuleLayout) -> None:
    """The one large chart (20 x 10.5 cm, standard section 3): revenue bars against the break-even revenue line."""
    blk = pl.blocks["be"]
    last = L(1 + pl.t.years)
    sheet = q(lay.sheet)

    def rng(row: int) -> str:
        return f"{sheet}!$B${row}:${last}${row}"

    rev, be_rev = blk.placed["rev"], blk.placed["be_rev"]
    chart = ch.combo(
        "Revenue vs break-even revenue (EBITDA = 0)",
        rng(blk.year_row),
        [ch.Ser(rng(rev), f"{sheet}!$A${rev}")],
        [ch.Ser(rng(be_rev), f"{sheet}!$A${be_rev}")],
        fmt=AXIS["usd"],
        cat_fmt=YEAR_FMT,
        secondary=False,
        size=ch.LARGE_CM,
    )
    ch.place(ws, chart, f"A{max(lay.notes, default=max(blk.placed.values())) + 2}")


# --------------------------------------------------------------------------- Sources & Uses (E30)
def su_default_periods(pl: Plan) -> int:
    """Default length of the sources-and-uses period: 12 months, or 1 year in an annual model (capped)."""
    return min(12 if pl.t.granularity == "monthly" else 1, pl.t.periods)


def _plan_sources_uses(pl: Plan) -> ModuleLayout:
    word, n = pl.t.period_word, pl.t.periods
    lay = ModuleLayout(
        "Sources & Uses",
        "Sources and uses of funds",
        "Live for the selected scenario. Where the money comes from and where it goes in the period set below.",
    )
    s = _Sheet(lay, 5)
    gr, prow = pl.grid_range, _period_row(pl)
    be = pl.modules["breakeven"]
    s.section("Funding structure ($'000) — raised at the start of the plan")
    s.header({"B": "Amount", "C": "Share"})
    eq, ln = s.r, s.r + 1
    tot = s.r + 2
    share = f"=IF($B${tot}=0,0,B{{r}}/$B${tot})"
    kc = {"B": "usdk", "C": "pct"}
    s.row("su_equity", "Equity", {"B": _link(pl, "equity"), "C": share.format(r=eq)}, kc, also=("C",))
    s.row("su_loan", "Debt (loan)", {"B": _link(pl, "loan_amount"), "C": share.format(r=ln)}, kc, also=("C",))
    s.row(
        "su_funding",
        "Total funding",
        {"B": f"=B{eq}+B{ln}", "C": f"=IF(B{tot}=0,0,1)"},
        kc,
        also=("C",),
        bold=True,
        total=True,
    )
    s.row(
        "su_gearing",
        "Gearing (debt ÷ equity)",
        f'=IF(B{eq}<=0,IF(B{ln}>0,"{NA}",0),B{ln}/B{eq})',
        "x",
        note="n/a: debt without positive equity",
    )
    s.row(
        "su_required",
        "Funding required by the plan (Break-even sheet)",
        f"={q(be.sheet)}!{be.local['required']}",
        "usdk",
    )
    s.row("su_gap", "Funding surplus / (shortfall)", f"={q(be.sheet)}!{be.local['gap']}", "usdk", bold=True)
    s.blank()
    sec = s.r
    s.section(f"Sources and uses of cash in the first {word}s ($'000)")
    n_in = s.row(
        "su_n_in",
        f"Period covered ({word}s from the start)",
        su_default_periods(pl),
        INT,
        checked=False,
        note=f"1 to {n} (capped)",
    )
    nr = s.row("su_n", f"{word.capitalize()}s used", f"=MIN({n},MAX(1,ROUND(B{n_in},0)))", INT)
    lay.inputs[f"B{n_in}"] = (1, n)
    # the band follows the input: "… in the first 12 months ($'000)"
    lay.sections[sec] = (
        f'="Sources and uses of cash in the first "&$B${nr}&IF($B${nr}=1," {word}"," {word}s")&" ($\'000)"'
    )
    cap = f"$B${nr}"

    def cum(key: str, sign: str = "") -> str:
        return f"{sign}SUMPRODUCT(--({prow}<={cap}),{gr(key)})"

    s.header({"A": "Sources", "B": "Amount", "C": "Share"})
    first_src = s.r
    src_tot = first_src + 3
    pct = f"=IF($B${src_tot}=0,0,B{{r}}/$B${src_tot})"
    rows_src = [
        ("su_eq_in", "Equity raised", f"={cum('equity_in')}"),
        ("su_draw", "Loan drawdowns", f"={cum('loan_draw')}"),
        ("su_cfo_in", "Cash generated by operations", f"=MAX(0,{cum('cfo')})"),
    ]
    for i, (name, label, f) in enumerate(rows_src):
        s.row(name, label, {"B": f, "C": pct.format(r=first_src + i)}, {"B": "usdk", "C": "pct"}, also=("C",))
    s.row(
        "su_sources",
        "Total sources",
        {"B": f"=SUM(B{first_src}:B{src_tot - 1})", "C": f"=IF(B{src_tot}=0,0,1)"},
        {"B": "usdk", "C": "pct"},
        also=("C",),
        bold=True,
        total=True,
    )
    s.blank()
    s.header({"A": "Uses", "B": "Amount", "C": "Share"})
    first_use = s.r
    use_tot = first_use + 4
    pct = f"=IF($B${use_tot}=0,0,B{{r}}/$B${use_tot})"
    rows_use = [
        ("su_cfo_out", "Cash used by operations", f"=MAX(0,-{cum('cfo')})"),
        ("su_capex", "Capital spending", f"={cum('cfi', '-')}"),
        ("su_repay", "Loan repayments", f"={cum('loan_repay', '-')}"),
        ("su_cash_end", "Cash at the end of the period", f"=INDEX({gr('cash_close')},{cap})"),
    ]
    for i, (name, label, f) in enumerate(rows_use):
        s.row(name, label, {"B": f, "C": pct.format(r=first_use + i)}, {"B": "usdk", "C": "pct"}, also=("C",))
    s.row(
        "su_uses",
        "Total uses",
        {"B": f"=SUM(B{first_use}:B{use_tot - 1})", "C": f"=IF(B{use_tot}=0,0,1)"},
        {"B": "usdk", "C": "pct"},
        also=("C",),
        bold=True,
        total=True,
    )
    s.row("su_diff", "Sources − uses (must be 0; opening cash is 0)", f"=B{src_tot}-B{use_tot}", "usdk", checked=False)
    lay.charts = {"funding": (eq, ln), "uses": (first_use, use_tot - 1)}
    lay.width = 3
    lay.error_range = f"{q(lay.sheet)}!$B$3:$C${s.r}"
    return lay


def plan_modules(pl: Plan) -> None:
    mods = modules_for(pl.brief.tier)
    if "breakeven" in mods:
        pl.modules["breakeven"] = _plan_breakeven(pl)
    if "dcf" in mods:
        pl.modules["dcf"] = _plan_dcf(pl)
    if "sources_uses" in mods:
        pl.modules["sources_uses"] = _plan_sources_uses(pl)


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
    if "sources_uses" in pl.modules:
        out.append(
            (
                "Sources & uses balance",
                ok(f"ABS({ref('sources_uses', 'su_sources')}-{ref('sources_uses', 'su_uses')})<0.5"),
                "Sources of funds = uses of funds (incl. cash at the end) for the Sources & Uses period",
            )
        )
    return out


# --------------------------------------------------------------------------- writing
def write_modules(wb, pl: Plan) -> None:
    for lay in pl.modules.values():
        ws = wb[lay.sheet]
        st.title(ws, lay.title, lay.sub, lay.width, link_col=lay.width + 2)
        ws.cell(row=3, column=1, value="Scenario shown").font = st.font(bold=True)
        c = ws.cell(row=3, column=2, value=_scenario_label(pl))
        c.font = st.font(st.PINE, bold=True)
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
            all_pct = all(f == FORMATS["pct"] for f in row.fmt.values())  # percentages: italic grey (standard §4)
            if row.label:
                lab = ws.cell(row=row.row, column=1, value=row.label)
                lab.font = st.font(st.GREY, italic=True) if all_pct else st.font(bold=row.bold)
                if row.label.startswith(KEY_TOTAL_LABELS):
                    lab.border = st.KEY_TOTAL
            for col, f in row.values.items():
                cell = ws[f"{col}{row.row}"]
                cell.value = f
                pct = row.fmt[col] == FORMATS["pct"]
                link = isinstance(f, str) and PURE_LINK.match(f)
                link_colour = st.INK if lay.sheet in st.REPORT_SHEETS else st.GREEN
                cell.font = st.font(link_colour if link else st.GREY if pct else "000000", bold=row.bold, italic=pct)
                cell.number_format = row.fmt[col]
                if row.total:
                    cell.border = st.TOTAL_TOP
                if row.label.startswith(KEY_TOTAL_LABELS):
                    cell.border = st.KEY_TOTAL
            if row.note:
                ws.cell(row=row.row, column=max(4, len(row.values) + 2), value=row.note).font = st.font(st.GREY, size=9)
        for r, text in lay.notes.items():
            ws.cell(row=r, column=1, value=text).font = st.font(st.GREY, size=9, italic=True)
        if lay.sheet == SHEETS["breakeven"]:
            _breakeven_chart(ws, pl, lay)
        ws.column_dimensions["A"].width = 52
        for i in range(2, lay.width + 2):
            ws.column_dimensions[L(i)].width = max(ws.column_dimensions[L(i)].width or 0, 16)
        for ref, (lo, hi) in lay.inputs.items():
            st.input_cell(ws[ref])
            dv = DataValidation(
                type="whole",
                operator="between",
                formula1=str(lo),
                formula2=str(hi),
                showInputMessage=True,
                promptTitle="Period",
                prompt=f"A whole number from {lo} to {hi}",
            )
            ws.add_data_validation(dv)
            dv.add(ref)
        if lay.sheet == "Sources & Uses":
            _su_charts(ws, lay)


def _su_charts(ws, lay: ModuleLayout) -> None:
    """Two standard charts side by side (docs/WORKBOOK_STANDARD.md §3), right of the tables."""
    sh = q(lay.sheet)
    (e, ln), (u0, u1) = lay.charts["funding"], lay.charts["uses"]
    ws.column_dimensions["E"].width = 2
    d = ch.doughnut(
        "Funding structure",
        f"{sh}!$A${e}:$A${ln}",
        ch.Ser(f"{sh}!$B${e}:$B${ln}", "Funding"),
        points=2,
    )
    b = ch.bar(
        "Uses of funds",
        f"{sh}!$A${u0}:$A${u1}",
        [ch.Ser(f"{sh}!$B${u0}:$B${u1}", "Uses")],
        horizontal=True,
        labels=True,
    )
    for slot, chart in enumerate((d, b)):
        ch.place(ws, chart, ch.slot_anchor(slot, 5, cols=SU_CHART_COLS))
