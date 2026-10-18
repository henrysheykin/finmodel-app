"""Property Returns sheet (E05): a purchase at the start, yearly cash flows, a sale at the horizon.

A template opts in with ``returns = True`` (the real-estate template does). It must define the drivers in
``REQUIRED_DRIVERS`` and a ``capex_buy`` capex line (the purchase incl. closing costs, period 1). The sheet
is built from the period grid, so it shows exactly the numbers of the P&L and cash flow:

- **Year 0** = the purchase: price + closing costs (unlevered), less the loan drawn (levered).
- **Years 1..H** = NOI (the model's EBITDA) − capital reserves (capex other than the purchase); levered
  adds interest and principal from the loan schedule.
- **Exit** at the end of year H: next-year NOI (final-year NOI × (1 + rent growth)) ÷ exit cap rate, less
  selling costs; levered also repays the loan balance left at that date.
- **Returns**: unlevered and levered IRR (Excel ``IRR``), NPV at the discount rate (year-0 flow + ``NPV``
  of years 1..H), equity multiple, going-in cap rate, cash-on-cash and DSCR by year.

Cash flows are before income tax (the usual way property returns are quoted). ``reference`` is the
plain-Python twin the challenger compares cell by cell (money within $1, IRR within 0.01 pp).
"""

from __future__ import annotations

from openpyxl.utils import get_column_letter as L

from engine.builder import FIRST_COL, Plan, q
from engine.goal_sheets import ModuleLayout, _link, _Sheet
from engine.goals import NA
from engine.spec import Timing

SHEET = "Returns"
REQUIRED_DRIVERS = ("price", "closing_pct", "rent_g", "exit_cap", "sell_pct", "disc_rate")
REQUIRED_LINES = ("capex_buy",)
MULT = "0.00x"
#: challenger tolerances by cell-name prefix (default $1)
TOLERANCE = {
    "irr_u": 1e-4,
    "irr_l": 1e-4,
    "ltv": 1e-6,
    "cap_in": 1e-6,
    "eq_mult_u": 1e-6,
    "eq_mult_l": 1e-6,
    "dscr": 1e-6,
    "coc": 1e-6,
}

# rows of the yearly table, in order: name -> label
TABLE = (
    ("purchase", "Purchase incl. closing costs"),
    ("noi", "Net operating income (NOI = EBITDA)"),
    ("reserves", "Capital reserves (capex other than the purchase)"),
    ("sale", "Sale proceeds, net of selling costs"),
    ("ucf", "Unlevered cash flow (property, before tax)"),
    ("loan_in", "Loan drawn"),
    ("interest", "Interest"),
    ("principal", "Principal repaid"),
    ("payoff", "Loan balance repaid at sale"),
    ("lcf", "Levered cash flow (equity, before tax)"),
    ("dscr", "Debt service coverage (NOI ÷ debt service)"),
    ("coc", "Cash-on-cash return (levered cash flow before sale ÷ equity invested)"),
    ("sign_u", "Helper: sign of the unlevered cash flow (a zero keeps the previous sign)"),
    ("sign_l", "Helper: sign of the levered cash flow (a zero keeps the previous sign)"),
)
#: IRR is shown only when the flows return at least this share of the money put in (see ``irr``)
MIN_RECOVERY = 0.25
#: debt service below this ($) counts as none for DSCR (rounding left on a fully repaid loan)
MIN_DEBT_SERVICE = 0.5


def _cols(t: Timing) -> list[str]:
    """Column letters for year 0..H (year 0 in column B)."""
    return [L(2 + y) for y in range(t.years + 1)]


def plan_returns(pl: Plan) -> None:
    missing = [k for k in REQUIRED_DRIVERS if k not in pl.input_row] + [k for k in REQUIRED_LINES if k not in pl.lines]
    if missing:
        raise ValueError(f"template {pl.template.key!r} has returns=True but lacks {missing}")
    t, H = pl.t, pl.t.years
    lay = ModuleLayout(
        SHEET,
        "Property returns — purchase, hold and sale",
        f"Live for the selected scenario. Year 0 = purchase; sale at the end of year {H}. "
        "Cash flows before income tax.",
    )
    s = _Sheet(lay, 5)
    s.section("Purchase (active scenario, from the Inputs sheet)")
    price = s.row("price", "Purchase price", _link(pl, "price"), checked=False)
    closing = s.row("closing", "Closing costs", f"=B{price}*{pl.input_ref('closing_pct')}")
    cost = s.row("total_cost", "All-in purchase cost", f"=B{price}+B{closing}", bold=True, total=True)
    loan = s.row("loan", "Loan drawn at purchase", _link(pl, "loan_amount"), checked=False)
    eq = s.row("equity_in", "Equity invested in the property", f"=B{cost}-B{loan}", bold=True)
    s.row("ltv", "Loan-to-value at purchase", f"=IF(B{price}>0,B{loan}/B{price},0)", "pct")
    s.blank()

    # ---- yearly table -----------------------------------------------------------------
    s.section("Cash flows by year")
    cols = _cols(t)
    s.header({c: f"Year {y}" for y, c in enumerate(cols)})
    yr = s.r
    s.row("yr", "Year #", {c: ("=0" if y == 0 else f"={cols[y - 1]}{yr}+1") for y, c in enumerate(cols)}, "0", False)
    last = cols[-1]
    hy = f"${last}${yr}"
    g = next(g for g in pl.grids if g.sheet == pl.calc_sheet)
    gy = f"{q(g.sheet)}!${L(FIRST_COL)}${g.year_row}:${L(FIRST_COL + t.periods - 1)}${g.year_row}"
    rows = {name: s.r + i for i, (name, _) in enumerate(TABLE)}

    def sumif(c: str, key: str) -> str:
        return f"SUMIF({gy},{c}${yr},{pl.grid_range(key)})"

    def at(name: str, c: str) -> str:
        return f"{c}{rows[name]}"

    # exit and purchase cells are laid out below the table; their rows are known once the table is placed
    exit_row = rows[TABLE[-1][0]] + 3  # blank, section header, then the exit rows
    net_sale_ref, payoff_ref = f"$B${exit_row + 4}", f"$B${exit_row + 5}"
    formulas = {
        "purchase": lambda c: f"=-IF({c}${yr}=0,$B${cost},0)",
        "noi": lambda c: f"={sumif(c, 'ebitda')}",
        "reserves": lambda c: f"=-({sumif(c, 'capex')}-{sumif(c, 'capex_buy')})",
        "sale": lambda c: f"=IF({c}${yr}={hy},{net_sale_ref},0)",
        "ucf": lambda c: f"={at('purchase', c)}+{at('noi', c)}+{at('reserves', c)}+{at('sale', c)}",
        "loan_in": lambda c: f"=IF({c}${yr}=0,$B${loan},0)",
        "interest": lambda c: f"={sumif(c, 'interest')}",
        "principal": lambda c: f"={sumif(c, 'loan_repay')}",
        "payoff": lambda c: f"=-IF({c}${yr}={hy},{payoff_ref},0)",
        "lcf": lambda c: (
            f"={at('ucf', c)}+{at('loan_in', c)}+{at('interest', c)}+{at('principal', c)}+{at('payoff', c)}"
        ),
        "dscr": lambda c: (
            f"=IF(-({at('interest', c)}+{at('principal', c)})>{MIN_DEBT_SERVICE},"
            f'{at("noi", c)}/-({at("interest", c)}+{at("principal", c)}),"{NA}")'
        ),
        "coc": lambda c: (
            f"=IF(AND({c}${yr}>0,$B${eq}>0),({at('noi', c)}+{at('reserves', c)}+{at('interest', c)}"
            f'+{at("principal", c)})/$B${eq},"{NA}")'
        ),
    }
    first = cols[0]

    def sign(src: str, c: str) -> str:
        if c == first:
            return f"=SIGN({at(src, c)})"
        prev = cols[cols.index(c) - 1]
        return f"=IF({at(src, c)}=0,{prev}{rows['sign_' + src[0]]},SIGN({at(src, c)}))"

    formulas["sign_u"] = lambda c: sign("ucf", c)
    formulas["sign_l"] = lambda c: sign("lcf", c)
    fmts = {"dscr": MULT, "coc": "pct", "sign_u": "0", "sign_l": "0"}
    for name, label in TABLE:
        bold = name in ("ucf", "lcf")
        s.row(name, label, {c: formulas[name](c) for c in cols}, fmts.get(name, "usd"), False, bold=bold, total=bold)
        for y, c in enumerate(cols):
            lay.cells[f"{name}_{y}"] = f"{q(SHEET)}!{c}{rows[name]}"
    s.blank()

    # ---- exit -------------------------------------------------------------------------
    s.section(f"Sale at the end of year {H}")
    assert s.r == exit_row, (s.r, exit_row)
    noi_next = s.row(
        "noi_next",
        f"Year {H + 1} NOI (year {H} NOI × (1 + rent growth))",
        f"={last}{rows['noi']}*(1+{pl.input_ref('rent_g')})",
    )
    cap = s.row("exit_cap", "Exit cap rate", _link(pl, "exit_cap"), "pct", checked=False)
    gross = s.row("gross_sale", "Sale price (next-year NOI ÷ exit cap rate)", f"=IF(B{cap}>0,B{noi_next}/B{cap},0)")
    costs = s.row("sell_costs", "Selling costs", f"=-B{gross}*{pl.input_ref('sell_pct')}")
    net = s.row("net_sale", "Net sale proceeds", f"=B{gross}+B{costs}", bold=True, total=True)
    pay = s.row(
        "loan_payoff", f"Loan balance at the end of year {H}", f"=INDEX({pl.grid_range('loan_close')},{t.periods})"
    )
    assert f"$B${net}" == net_sale_ref and f"$B${pay}" == payoff_ref
    s.row("equity_sale", "Net proceeds to equity", f"=B{net}-B{pay}", bold=True)
    s.blank()

    # ---- returns ----------------------------------------------------------------------
    s.section("Returns")
    s.header({"B": "Unlevered", "C": "Levered"})
    u_rng = f"$B${rows['ucf']}:${last}${rows['ucf']}"
    l_rng = f"$B${rows['lcf']}:${last}${rows['lcf']}"
    u1 = f"$C${rows['ucf']}:${last}${rows['ucf']}"
    l1 = f"$C${rows['lcf']}:${last}${rows['lcf']}"
    irr_row, guess_row, ok_row = s.r, s.r + 1, s.r + 2

    def irr_formula(col: str, rng: str) -> str:
        # start Excel's IRR search near the answer (it can miss a strongly negative IRR from its 10% default)
        g, ok = f"{col}{guess_row}", f"{col}{ok_row}"
        return f'=IF({ok}=1,IFERROR(IRR({rng},{g}),IFERROR(IRR({rng}),"{NA}")),"{NA}")'

    def ok_formula(rng: str, sign_row: int) -> str:
        sp = f"${first}${sign_row}:${cols[-2]}${sign_row}"
        sn = f"${cols[1]}${sign_row}:${last}${sign_row}"
        inflow, outflow = f'SUMIF({rng},">0")', f'-SUMIF({rng},"<0")'
        return f"=IF(AND(SUMPRODUCT(--({sp}*{sn}<0))=1,{inflow}>={MIN_RECOVERY}*{outflow}),1,0)"

    def guess_formula(rng: str) -> str:
        inflow, outflow = f'SUMIF({rng},">0")', f'-SUMIF({rng},"<0")'
        return f"=IF(AND({inflow}>0,{outflow}>0),MAX(-0.99,({inflow}/({outflow}))^(1/{hy})-1),0.1)"

    irr = s.row(
        "irr_u",
        "Internal rate of return (IRR)",
        {"B": irr_formula("B", u_rng), "C": irr_formula("C", l_rng)},
        "pct",
    )
    s.row(
        "irr_guess",
        "Helper: IRR starting estimate ((inflows ÷ outflows) ^ (1 ÷ years) − 1)",
        {"B": guess_formula(u_rng), "C": guess_formula(l_rng)},
        "pct",
        checked=False,
    )
    s.row(
        "irr_ok",
        f"Helper: IRR defined (1 = one sign change and inflows ≥ {MIN_RECOVERY:.0%} of outflows)",
        {"B": ok_formula(u_rng, rows["sign_u"]), "C": ok_formula(l_rng, rows["sign_l"])},
        "0",
        checked=False,
    )
    assert irr == irr_row
    disc = s.row("disc_rate", "Discount rate for NPV", _link(pl, "disc_rate"), "pct", checked=False)
    npv = s.row(
        "npv_u",
        "Net present value at the discount rate",
        {"B": f"=$B${rows['ucf']}+NPV($B${disc},{u1})", "C": f"=$B${rows['lcf']}+NPV($B${disc},{l1})"},
        bold=True,
    )
    prof = s.row("profit_u", "Total profit (sum of cash flows)", {"B": f"=SUM({u_rng})", "C": f"=SUM({l_rng})"})
    mult = s.row(
        "eq_mult_u",
        "Multiple of money invested (inflows ÷ year-0 outflow)",
        {
            "B": f'=IF($B${rows["ucf"]}<0,SUM({u1})/-$B${rows["ucf"]},"{NA}")',
            "C": f'=IF($B${rows["lcf"]}<0,SUM({l1})/-$B${rows["lcf"]},"{NA}")',
        },
        MULT,
    )
    for name, row in (("irr_l", irr), ("npv_l", npv), ("profit_l", prof), ("eq_mult_l", mult)):
        lay.cells[name] = f"{q(SHEET)}!C{row}"
    s.row(
        "cap_in",
        "Going-in cap rate (year-1 NOI ÷ purchase price)",
        f"=IF(B{price}>0,C{rows['noi']}/B{price},0)",
        "pct",
    )
    end = s.r + 1
    lay.notes[end] = (
        "IRR and NPV use yearly flows with the purchase at year 0 and the sale at the end of the final year. "
        "n/a = no debt service or no equity invested; IRR n/a = the flows change sign more than once (IRR not "
        f"unique) or return less than {MIN_RECOVERY:.0%} of the money put in."
    )
    lay.width = max(4, len(cols) + 1)
    lay.error_range = f"{q(SHEET)}!$A$3:${L(lay.width)}${end}"
    lay.local["irr_u"], lay.local["irr_l"] = f"B{irr}", f"C{irr}"
    lay.local.update({f"row_{k}": str(v) for k, v in rows.items()})
    pl.modules["returns"] = lay


def returns_checks(pl: Plan) -> list[tuple[str, str, str]]:
    lay = pl.modules["returns"]
    rows = {k[4:]: int(v) for k, v in lay.local.items() if k.startswith("row_")}
    cols = _cols(pl.t)
    first, last = cols[0], cols[-1]
    yr = rows["purchase"] - 1

    def rng(name: str) -> str:
        return f"{q(SHEET)}!${first}${rows[name]}:${last}${rows[name]}"

    def ok(cond: str, warn: bool = False) -> str:
        return f'=IF({cond},"PASS","{"WARN" if warn else "FAIL"}")'

    years = f"{q(SHEET)}!${first}${yr}:${last}${yr}"

    def irr_ties(cell: str, flows: str) -> str:
        c = f"{q(SHEET)}!{cell}"
        return ok(f"IF(ISNUMBER({c}),ABS(SUMPRODUCT({flows}/(1+{c})^{years}))<1,TRUE)")

    ds = f"{q(SHEET)}!${cols[1]}${rows['dscr']}:${last}${rows['dscr']}"
    return [
        (
            "Returns: NOI ties to EBITDA",
            ok(f"ABS(SUM({rng('noi')})-SUM({pl.grid_range('ebitda')}))<0.5"),
            "NOI on the Returns sheet equals EBITDA summed over every period",
        ),
        (
            "Returns: purchase ties to capital spending",
            ok(f"ABS(SUM({rng('purchase')})+SUM({pl.grid_range('capex_buy')}))<0.5"),
            "Purchase price + closing costs equals the purchase in the capex line",
        ),
        (
            "Returns: loan fully repaid at sale",
            ok(f"ABS(SUM({rng('loan_in')})+SUM({rng('principal')})+SUM({rng('payoff')}))<0.5"),
            "Drawdown = principal repaid + balance repaid from the sale",
        ),
        (
            "Returns: IRR discounts cash flows to zero",
            irr_ties(lay.local["irr_u"], rng("ucf")),
            "NPV of the unlevered cash flows at their IRR is zero",
        ),
        (
            "Returns: levered IRR discounts cash flows to zero",
            irr_ties(lay.local["irr_l"], rng("lcf")),
            "NPV of the levered cash flows at their IRR is zero",
        ),
        (
            "Debt service covered (DSCR ≥ 1.0x)",
            ok(f"SUMPRODUCT(--ISNUMBER({ds}),--({ds}<1))=0", warn=True),
            "Business warning: NOI does not cover the loan payments in at least one year",
        ),
    ]


# --------------------------------------------------------------------------- python twin
def sign_changes(flows: list[float]) -> int:
    """Sign changes in a cash-flow series; a zero keeps the previous sign (as the sheet's helper rows)."""
    out, prev = 0, None
    for f in flows:
        sg = (f > 0) - (f < 0)
        if sg == 0:
            continue
        if prev is not None and sg != prev:
            out += 1
        prev = sg
    return out


def irr(flows: list[float]) -> float | str:
    """IRR of conventional flows by bisection; ``NA`` unless the flows change sign exactly once (so the IRR is
    unique) and inflows are at least ``MIN_RECOVERY`` of outflows (near-total losses, where a numeric IRR
    search is unreliable, are not shown). The sheet applies the same rule before calling Excel's IRR."""
    inflow, outflow = sum(f for f in flows if f > 0), -sum(f for f in flows if f < 0)
    if sign_changes(flows) != 1 or inflow < MIN_RECOVERY * outflow:
        return NA

    def npv(r: float) -> float:
        return sum(f / (1 + r) ** i for i, f in enumerate(flows))

    lo, hi = -0.9999, 100.0
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        return NA
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if f_lo * f_mid <= 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
        if hi - lo < 1e-12:
            break
    return (lo + hi) / 2


def reference(d: dict, s: dict[str, list[float]], t: Timing) -> dict:
    """Plain-Python Returns sheet for one scenario (``s`` = per-period series from ``reference_run``)."""
    H, ppy = t.years, t.ppy

    def ysum(key: str, y: int) -> float:
        return sum(s[key][(y - 1) * ppy : y * ppy]) if y > 0 else 0.0

    cells: dict[str, float | str] = {}
    price = d["price"]
    closing = price * d["closing_pct"]
    cost = price + closing
    loan = d["loan_amount"]
    eq = cost - loan
    cells.update(closing=closing, total_cost=cost, equity_in=eq, ltv=loan / price if price > 0 else 0.0)
    noi = {y: ysum("ebitda", y) for y in range(H + 1)}
    noi_next = noi[H] * (1 + d["rent_g"])
    gross = noi_next / d["exit_cap"] if d["exit_cap"] > 0 else 0.0
    sell = -gross * d["sell_pct"]
    net = gross + sell
    payoff = s["loan_close"][t.periods - 1]
    cells.update(
        noi_next=noi_next, gross_sale=gross, sell_costs=sell, net_sale=net, loan_payoff=payoff, equity_sale=net - payoff
    )
    ucf, lcf = [], []
    for y in range(H + 1):
        row = {
            "purchase": -cost if y == 0 else 0.0,
            "noi": noi[y],
            "reserves": -(ysum("capex", y) - ysum("capex_buy", y)),
            "sale": net if y == H else 0.0,
            "loan_in": loan if y == 0 else 0.0,
            "interest": ysum("interest", y),
            "principal": ysum("loan_repay", y),
            "payoff": -payoff if y == H else 0.0,
        }
        row["ucf"] = row["purchase"] + row["noi"] + row["reserves"] + row["sale"]
        row["lcf"] = row["ucf"] + row["loan_in"] + row["interest"] + row["principal"] + row["payoff"]
        ds = -(row["interest"] + row["principal"])
        row["dscr"] = row["noi"] / ds if ds > MIN_DEBT_SERVICE else NA
        row["coc"] = (
            (row["noi"] + row["reserves"] + row["interest"] + row["principal"]) / eq if y > 0 and eq > 0 else NA
        )
        for k, v in row.items():
            cells[f"{k}_{y}"] = v
        ucf.append(row["ucf"])
        lcf.append(row["lcf"])
        for tag, flows in (("u", ucf), ("l", lcf)):
            nz = [f for f in flows if f != 0]
            cells[f"sign_{tag}_{y}"] = float((nz[-1] > 0) - (nz[-1] < 0)) if nz else 0.0
    r = d["disc_rate"]
    for tag, flows in (("u", ucf), ("l", lcf)):
        cells[f"irr_{tag}"] = irr(flows)
        cells[f"npv_{tag}"] = flows[0] + sum(f / (1 + r) ** i for i, f in enumerate(flows) if i > 0)
        cells[f"profit_{tag}"] = sum(flows)
        cells[f"eq_mult_{tag}"] = sum(flows[1:]) / -flows[0] if flows[0] < 0 else NA
    cells["cap_in"] = noi[1] / price if price > 0 else 0.0
    return {"cells": cells, "years": {}}
