"""Lines every template shares: headcount, P&L tail, fixed assets, working
capital, debt, cash flow and balance sheet — plus their plain-Python twin used
by the challenger.

Sign convention in the grid: revenue and balances positive, costs negative.
Templates supply ``rev``, ``cogs`` (negative), opex lines (negative) and
``capex`` (positive spend per period).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from engine.brief import Role
from engine.spec import DriverSpec, Line, Timing

HEADCOUNT_DRIVERS: list[DriverSpec] = [
    DriverSpec("payroll_tax", "Payroll taxes & benefits, % of salary", "%", "pct", 0, 1, section="Headcount"),
    DriverSpec("wage_g", "Wage growth per year", "%", "pct", -0.2, 0.5, section="Headcount"),
]


# --------------------------------------------------------------------------- grid lines
def headcount_lines(roles: list[Role]) -> list[Line]:
    out: list[Line] = []
    for i, r in enumerate(roles):
        k = r.key
        out.append(
            Line(
                f"hc_{k}_fte",
                f"{r.title} — FTE",
                group="headcount",
                fmt="dec1",
                agg="last",
                # FTE on payroll in the period (average over the period for annual columns),
                # stepping up by the role's growth rate each year
                formula=(
                    f"={{in:{k}_fte}}*(1+{{in:{k}_fte_g}})^({{y}}-1)"
                    f"*MAX(0,MIN({{mpp}},{{p}}*{{mpp}}-{{in:{k}_start}}+1))/{{mpp}}"
                ),
                section="Headcount (FTE)" if i == 0 else None,
            )
        )
    fte_sum = "+".join(f"{{hc_{r.key}_fte}}" for r in roles) or "0"
    out.append(Line("fte_total", "Total FTE", f"={fte_sum}", "headcount", "dec1", agg="last", bold=True, total=True))
    for i, r in enumerate(roles):
        k = r.key
        out.append(
            Line(
                f"hc_{k}_cost",
                f"{r.title} — payroll cost",
                group="headcount",
                formula=(
                    f"=-{{hc_{k}_fte}}*{{in:{k}_salary}}/12*{{mpp}}*(1+{{in:payroll_tax}})*(1+{{in:wage_g}})^({{y}}-1)"
                ),
                section="Payroll cost (salary + taxes & benefits)" if i == 0 else None,
            )
        )
    cost_sum = "+".join(f"{{hc_{r.key}_cost}}" for r in roles) or "0"
    out.append(Line("payroll_total", "Total payroll", f"={cost_sum}", "headcount", bold=True, total=True))
    return out


def pnl_head_lines() -> list[Line]:
    return [Line("gp", "Gross profit", "={rev}+{cogs}", "core", bold=True, total=True)]


def pnl_tail_lines(opex_keys: list[str], liab_keys: list[str] = ()) -> list[Line]:
    opex_sum = "+".join(f"{{{k}}}" for k in opex_keys) or "0"
    liab_terms = "".join(f"+{{d_{k}}}" for k in liab_keys)
    return [
        Line("opex_total", "Total operating expenses", f"={opex_sum}", "core", bold=True, total=True),
        Line("ebitda", "EBITDA", "={gp}+{opex_total}", "core", bold=True, total=True),
        Line("ebit", "EBIT", "={ebitda}+{dep}", "core", bold=True, section="Profit after depreciation, interest, tax"),
        Line(
            "interest",
            "Interest on loan (average balance after drawdown)",
            "=-({loan_open}+{loan_draw}+{loan_close})/2*{in:loan_rate}/{ppy}",
            "core",
        ),
        Line("ebt", "Pre-tax income", "={ebit}+{interest}", "core", bold=True, total=True),
        Line(
            "cum_ebt", "Helper: cumulative pre-tax income", "={cum_ebt[-1]}+{ebt}", "core", first="={ebt}", agg="none"
        ),
        Line(
            "tax_peak",
            "Helper: cumulative taxable income (losses carried forward)",
            "=MAX({tax_peak[-1]},{cum_ebt})",
            "core",
            first="=MAX(0,{cum_ebt})",
            agg="none",
        ),
        Line(
            "tax",
            "Income tax",
            "=-({tax_peak}-{tax_peak[-1]})*{in:tax_rate}",
            "core",
            first="=-{tax_peak}*{in:tax_rate}",
        ),
        Line("ni", "Net income", "={ebt}+{tax}", "core", bold=True, total=True),
        Line("ppe_gross", "Fixed assets at cost", "={ppe_gross[-1]}+{capex}", "core", first="={capex}", agg="last"),
        Line(
            "dep",
            "Depreciation",
            "=-MIN({ppe_gross}/MAX(1,{in:dep_years}*{ppy}),{ppe_net[-1]}+{capex})",
            "core",
            first="=-MIN({ppe_gross}/MAX(1,{in:dep_years}*{ppy}),{capex})",
        ),
        Line("acc_dep", "Accumulated depreciation", "={acc_dep[-1]}+{dep}", "core", first="={dep}", agg="last"),
        Line("ppe_net", "Net fixed assets", "={ppe_gross}+{acc_dep}", "core", agg="last", bold=True),
        Line(
            "loan_open", "Loan — opening balance", "={loan_close[-1]}", "core", first="=0", agg="first", section="Debt"
        ),
        Line("loan_draw", "Loan drawdown", "=IF({p}=1,{in:loan_amount},0)", "core"),
        Line(
            "loan_repay",
            "Loan repayment",
            "=-MIN({loan_open},{in:loan_amount}/MAX(1,{in:loan_term_years}*{ppy}))",
            "core",
        ),
        Line(
            "loan_close",
            "Loan — closing balance",
            "={loan_open}+{loan_draw}+{loan_repay}",
            "core",
            agg="last",
            bold=True,
        ),
        Line("ar", "Accounts receivable", "={rev}*{in:ar_days}/{dpp}", "core", agg="last", section="Working capital"),
        Line("inv", "Inventory", "=-{cogs}*{in:inv_days}/{dpp}", "core", agg="last"),
        Line("ap", "Accounts payable", "=-{cogs}*{in:ap_days}/{dpp}", "core", agg="last"),
        Line("d_ar", "(Increase) / decrease in receivables", "={ar[-1]}-{ar}", "core", first="=-{ar}"),
        Line("d_inv", "(Increase) / decrease in inventory", "={inv[-1]}-{inv}", "core", first="=-{inv}"),
        Line("d_ap", "Increase / (decrease) in payables", "={ap}-{ap[-1]}", "core", first="={ap}"),
        Line(
            "cfo",
            "Operating cash flow",
            f"={{ni}}-{{dep}}+{{d_ar}}+{{d_inv}}+{{d_ap}}{liab_terms}",
            "core",
            bold=True,
            section="Cash flow",
        ),
        Line("cfi", "Investing cash flow (capex)", "=-{capex}", "core"),
        Line("equity_in", "Equity raised", "=IF({p}=1,{in:equity},0)", "core"),
        Line("cff", "Financing cash flow", "={equity_in}+{loan_draw}+{loan_repay}", "core"),
        Line("net_cf", "Net cash flow", "={cfo}+{cfi}+{cff}", "core", bold=True, total=True),
        Line("cash_open", "Opening cash", "={cash_close[-1]}", "core", first="=0", agg="first"),
        Line("cash_close", "Closing cash", "={cash_open}+{net_cf}", "core", agg="last", bold=True, total=True),
        Line("pos_flag", "Helper: EBITDA positive (1/0)", "=IF({ebitda}>0,1,0)", "core", fmt="int", agg="none"),
    ]


def liability_delta_lines(liabs: list[Line]) -> list[Line]:
    """Cash-flow effect of template working-capital liabilities (e.g. deferred revenue)."""
    return [
        Line(
            f"d_{ln.key}",
            f"Increase / (decrease) in {ln.label[0].lower() + ln.label[1:]}",
            f"={{{ln.key}}}-{{{ln.key}[-1]}}",
            "core",
            first=f"={{{ln.key}}}",
        )
        for ln in liabs
    ]


def balance_sheet_lines(liab_keys: list[str] = ()) -> list[Line]:
    liab = "".join(f"+{{{k}}}" for k in liab_keys)
    return [
        Line(
            "paid_in",
            "Paid-in capital",
            "={paid_in[-1]}+{equity_in}",
            "bs",
            first="={equity_in}",
            agg="last",
            section="Balance sheet",
        ),
        Line("retained", "Retained earnings", "={retained[-1]}+{ni}", "bs", first="={ni}", agg="last"),
        Line("total_assets", "Total assets", "={cash_close}+{ar}+{inv}+{ppe_net}", "bs", agg="last", bold=True),
        Line("total_liab", "Total liabilities", f"={{ap}}+{{loan_close}}{liab}", "bs", agg="last"),
        Line("total_equity", "Total equity", "={paid_in}+{retained}", "bs", agg="last"),
        Line("total_le", "Total liabilities & equity", "={total_liab}+{total_equity}", "bs", agg="last", bold=True),
        Line("bs_diff", "Check: assets − liabilities − equity", "={total_assets}-{total_le}", "bs", agg="last"),
    ]


# --------------------------------------------------------------------------- python twin
@dataclass
class HC:
    """Headcount results the framework hands to a template's reference model."""

    payroll: float  # negative, total payroll cost in the period
    fte: float  # total FTE on payroll in the period


@dataclass
class Top:
    """What a template's reference model returns for one period."""

    rev: float
    cogs: float  # negative
    opex: dict[str, float]  # negative
    capex: float  # positive
    liabilities: dict[str, float] = field(default_factory=dict)  # working-capital balances, e.g. deferred revenue
    kpis: dict[str, float] = field(default_factory=dict)  # extra series checked by the challenger


TopFn = Callable[[dict, int, int, Timing, HC], Top]


def reference_run(d: dict, roles: list[Role], t: Timing, top: TopFn) -> dict[str, list[float]]:
    """Run the whole model in plain Python. Returns per-period series (index 0 = period 1).

    ``top(d, p, y, timing, hc)`` is the template's own revenue/cost logic;
    ``hc`` (payroll cost and FTE) is computed here from the roles.
    """
    s: dict[str, list[float]] = {
        k: []
        for k in (
            "rev",
            "cogs",
            "gp",
            "opex_total",
            "ebitda",
            "dep",
            "ebit",
            "interest",
            "ebt",
            "tax",
            "ni",
            "ar",
            "inv",
            "ap",
            "capex",
            "ppe_net",
            "loan_close",
            "cash_close",
            "paid_in",
            "retained",
            "total_assets",
            "total_le",
            "payroll_total",
            "fte_total",
            "cfo",
            "cfi",
            "cff",
        )
    }
    ppe_gross = acc_dep = loan = cash = cum_ebt = peak = paid_in = retained = 0.0
    ar0 = inv0 = ap0 = 0.0
    liab0: dict[str, float] = {}
    for p in range(1, t.periods + 1):
        y = t.year_of(p)
        fte_total = payroll = 0.0
        for r in roles:
            months_on = max(0.0, min(t.mpp, p * t.mpp - d[f"{r.key}_start"] + 1))
            fte = d[f"{r.key}_fte"] * (1 + d[f"{r.key}_fte_g"]) ** (y - 1) * months_on / t.mpp
            fte_total += fte
            payroll -= fte * d[f"{r.key}_salary"] / 12 * t.mpp * (1 + d["payroll_tax"]) * (1 + d["wage_g"]) ** (y - 1)
        tp = top(d, p, y, t, HC(payroll, fte_total))
        gp = tp.rev + tp.cogs
        opex = sum(tp.opex.values())
        ebitda = gp + opex
        ppe_gross += tp.capex
        net_before = ppe_gross + acc_dep
        dep = -min(ppe_gross / max(1, d["dep_years"] * t.ppy), net_before)
        acc_dep += dep
        loan_open = loan
        draw = d["loan_amount"] if p == 1 else 0.0
        repay = -min(loan_open, d["loan_amount"] / max(1, d["loan_term_years"] * t.ppy))
        loan = loan_open + draw + repay
        interest = -(loan_open + draw + loan) / 2 * d["loan_rate"] / t.ppy
        ebit = ebitda + dep
        ebt = ebit + interest
        cum_ebt += ebt
        new_peak = max(peak, cum_ebt)
        tax = -(new_peak - peak) * d["tax_rate"]
        peak = new_peak
        ni = ebt + tax
        ar = tp.rev * d["ar_days"] / t.dpp
        inv = -tp.cogs * d["inv_days"] / t.dpp
        ap = -tp.cogs * d["ap_days"] / t.dpp
        d_liab = sum(v - liab0.get(k, 0.0) for k, v in tp.liabilities.items())
        liab0 = dict(tp.liabilities)
        cfo = ni - dep + (ar0 - ar) + (inv0 - inv) + (ap - ap0) + d_liab
        ar0, inv0, ap0 = ar, inv, ap
        equity_in = d["equity"] if p == 1 else 0.0
        cfi = -tp.capex
        cff = equity_in + draw + repay
        cash += cfo + cfi + cff
        paid_in += equity_in
        retained += ni
        ppe_net = ppe_gross + acc_dep
        row = {
            "rev": tp.rev,
            "cogs": tp.cogs,
            "gp": gp,
            "opex_total": opex,
            "ebitda": ebitda,
            "dep": dep,
            "ebit": ebit,
            "interest": interest,
            "ebt": ebt,
            "tax": tax,
            "ni": ni,
            "ar": ar,
            "inv": inv,
            "ap": ap,
            "capex": tp.capex,
            "ppe_net": ppe_net,
            "loan_close": loan,
            "cash_close": cash,
            "paid_in": paid_in,
            "retained": retained,
            "total_assets": cash + ar + inv + ppe_net,
            "total_le": ap + loan + sum(tp.liabilities.values()) + paid_in + retained,
            "payroll_total": payroll,
            "fte_total": fte_total,
            "cfo": cfo,
            "cfi": cfi,
            "cff": cff,
        }
        row.update(tp.liabilities)
        row.update(tp.kpis)
        for k, v in row.items():
            s.setdefault(k, []).append(v)
    return s


FLOW_KEYS = {
    "rev",
    "cogs",
    "gp",
    "opex_total",
    "ebitda",
    "dep",
    "ebit",
    "interest",
    "ebt",
    "tax",
    "ni",
    "capex",
    "payroll_total",
    "cfo",
    "cfi",
    "cff",
}


def annualise(series: dict[str, list[float]], t: Timing, extra_flows=()) -> dict[str, dict[int, float]]:
    """Per-year values: flows summed, balances taken at year end."""
    flows = FLOW_KEYS | set(extra_flows)
    out: dict[str, dict[int, float]] = {}
    for k, vals in series.items():
        out[k] = {}
        for y in range(1, t.years + 1):
            chunk = vals[(y - 1) * t.ppy : y * t.ppy]
            out[k][y] = sum(chunk) if k in flows else chunk[-1]
    return out
