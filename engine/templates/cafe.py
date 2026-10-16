"""Deterministic Excel model builder.

An LLM only has to produce the brief (business type, horizon, driver values for
Low / Base / High). This script turns the brief into a workbook with live
formulas, a scenario switch and a formula-based check sheet. Keeping the
workbook logic in code (not in the LLM) is what makes the output reliable.

Ported unchanged in behaviour from poc/generate_model.py (E01).

Usage: python -m engine.templates.cafe brief.json out.xlsx
"""

import json
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

FONT = "Arial"
NAVY = "1F3864"
BLUE_INPUT = "0000FF"
GREEN_LINK = "008000"
F_USD = "$#,##0;($#,##0);-"
F_USD2 = "$#,##0.00;($#,##0.00);-"
F_PCT = "0.0%;(0.0%);-"
F_INT = "#,##0;(#,##0);-"
F_DEC1 = "#,##0.0;(#,##0.0);-"
FMT = {"usd": F_USD, "usd2": F_USD2, "pct": F_PCT, "int": F_INT, "dec1": F_DEC1}

thin = Side(style="thin", color="D9D9D9")
BOTTOM = Border(bottom=thin)
TOTAL_TOP = Border(top=Side(style="thin", color="000000"))


def font(color="000000", bold=False, size=10, italic=False):
    return Font(name=FONT, color=color, bold=bold, size=size, italic=italic)


def title(ws, text, sub=None, width_cols=8):
    ws["A1"] = text
    ws["A1"].font = Font(name=FONT, size=14, bold=True, color="FFFFFF")
    for c in range(1, width_cols + 1):
        ws.cell(row=1, column=c).fill = PatternFill("solid", fgColor=NAVY)
    ws.row_dimensions[1].height = 24
    if sub:
        ws["A2"] = sub
        ws["A2"].font = font("6B7280", italic=True, size=9)


def section(ws, row, text, ncols):
    ws.cell(row=row, column=1, value=text).font = font("FFFFFF", bold=True)
    for c in range(1, ncols + 1):
        ws.cell(row=row, column=c).fill = PatternFill("solid", fgColor="2F5597")


def build(brief: dict, out_path: str) -> None:
    years = int(brief["horizon_years"])
    months = years * 12
    drivers = brief["drivers"]
    wb = Workbook()

    # ---------------- Dashboard (created first so it is the first tab) ----
    dash = wb.active
    dash.title = "Dashboard"

    # ---------------- Inputs --------------------------------------------
    inp = wb.create_sheet("Inputs")
    title(inp, "Inputs — Low / Base / High", brief.get("assumption_note"), 7)
    hdr = ["Driver", "Low", "Base", "High", "Active", "Unit", "Note"]
    for i, h in enumerate(hdr, 1):
        c = inp.cell(row=4, column=i, value=h)
        c.font = font(bold=True)
        c.border = BOTTOM
        c.alignment = Alignment(horizontal="left" if i in (1, 6, 7) else "right")
    ref = {}
    r = 5
    for d in drivers:
        inp.cell(row=r, column=1, value=d["label"]).font = font()
        for col, k in ((2, "low"), (3, "base"), (4, "high")):
            c = inp.cell(row=r, column=col, value=d[k])
            c.font = font(BLUE_INPUT)
            c.number_format = FMT[d["fmt"]]
        act = inp.cell(row=r, column=5, value=f"=CHOOSE(Dashboard!$B$4,B{r},C{r},D{r})")
        act.font = font(bold=True)
        act.number_format = FMT[d["fmt"]]
        inp.cell(row=r, column=6, value=d["unit"]).font = font("6B7280")
        inp.cell(row=r, column=7, value="User / brief input").font = font("6B7280", size=9)
        ref[d["key"]] = f"Inputs!$E${r}"
        ref[d["key"] + "_row"] = r
        r += 1
    inp.cell(
        row=r + 1,
        column=1,
        value="Legend: blue = input you can change · black = formula · "
        "green = link to another sheet. Column E follows the scenario on the Dashboard.",
    ).font = font("6B7280", size=9, italic=True)
    for col, w in zip("ABCDEFG", (40, 12, 12, 12, 12, 12, 22), strict=True):
        inp.column_dimensions[col].width = w
    inp.freeze_panes = "B5"

    # ---------------- Monthly -------------------------------------------
    mo = wb.create_sheet("Monthly")
    first_col, last_col = 3, 2 + months
    L = get_column_letter
    title(
        mo, "Monthly projection", "All values in $ unless stated. Every month uses the same formula.", min(last_col, 16)
    )

    rows = {
        "month": 3,
        "year": 4,
        "ramp": 6,
        "cust": 7,
        "ticket": 8,
        "days": 9,
        "rev": 10,
        "cogs": 11,
        "gp": 12,
        "rent": 14,
        "payroll": 15,
        "mkt": 16,
        "other": 17,
        "opex": 18,
        "ebitda": 19,
        "dep": 20,
        "ebit": 21,
        "tax": 22,
        "ni": 23,
        "open_cash": 25,
        "ocf": 26,
        "close_cash": 27,
        "pos_flag": 29,
    }
    labels = {
        "month": "Month #",
        "year": "Year #",
        "ramp": "Traffic ramp factor",
        "cust": "Customers per day",
        "ticket": "Average ticket ($)",
        "days": "Operating days",
        "rev": "Revenue",
        "cogs": "COGS",
        "gp": "Gross profit",
        "rent": "Rent",
        "payroll": "Payroll",
        "mkt": "Marketing",
        "other": "Utilities & other",
        "opex": "Total operating expenses",
        "ebitda": "EBITDA",
        "dep": "Depreciation",
        "ebit": "EBIT",
        "tax": "Income tax",
        "ni": "Net income",
        "open_cash": "Opening cash",
        "ocf": "Operating cash flow",
        "close_cash": "Closing cash",
        "pos_flag": "Helper: EBITDA positive (1/0)",
    }
    for k, rr in rows.items():
        mo.cell(row=rr, column=1, value=labels[k]).font = font(bold=k in ("rev", "gp", "ebitda", "ni", "close_cash"))
    section(mo, 5, "Revenue build", min(last_col, 16))
    section(mo, 13, "Operating expenses", min(last_col, 16))
    section(mo, 24, "Cash", min(last_col, 16))

    R = rows
    for m in range(1, months + 1):
        col = first_col + m - 1
        c = L(col)
        prev = L(col - 1)
        wage_idx = f"(1+{ref['wage_g']})^({c}{R['year']}-1)"
        f = {
            "month": m,
            "year": f"=ROUNDUP({c}{R['month']}/12,0)",
            "ramp": f"=MIN(1,{ref['open_pct']}+(1-{ref['open_pct']})*({c}{R['month']}-1)/MAX(1,{ref['ramp_months']}))",
            "cust": f"={ref['cust_full']}*{c}{R['ramp']}*(1+{ref['traffic_g']})^({c}{R['year']}-1)",
            "ticket": f"={ref['ticket']}*(1+{ref['price_g']})^({c}{R['year']}-1)",
            "days": f"={ref['days']}",
            "rev": f"={c}{R['cust']}*{c}{R['ticket']}*{c}{R['days']}",
            "cogs": f"=-{c}{R['rev']}*{ref['cogs_pct']}",
            "gp": f"={c}{R['rev']}+{c}{R['cogs']}",
            "rent": f"=-{ref['rent']}",
            "payroll": f"=-{ref['fte']}*{ref['salary']}/12*(1+{ref['payroll_tax']})*{wage_idx}",
            "mkt": f"=-{c}{R['rev']}*{ref['mkt_pct']}",
            "other": f"=-{ref['other_opex']}",
            "opex": f"=SUM({c}{R['rent']}:{c}{R['other']})",
            "ebitda": f"={c}{R['gp']}+{c}{R['opex']}",
            "dep": f"=IF({c}{R['month']}<={ref['dep_years']}*12,-{ref['capex']}/MAX(1,{ref['dep_years']}*12),0)",
            "ebit": f"={c}{R['ebitda']}+{c}{R['dep']}",
            "tax": f"=-MAX(0,{c}{R['ebit']})*{ref['tax_rate']}",
            "ni": f"={c}{R['ebit']}+{c}{R['tax']}",
            "open_cash": (f"={ref['start_cash']}-{ref['capex']}" if m == 1 else f"={prev}{R['close_cash']}"),
            "ocf": f"={c}{R['ni']}-{c}{R['dep']}",
            "close_cash": f"={c}{R['open_cash']}+{c}{R['ocf']}",
            "pos_flag": f"=IF({c}{R['ebitda']}>0,1,0)",
        }
        for k, v in f.items():
            cell = mo.cell(row=R[k], column=col, value=v)
            is_link = isinstance(v, str) and "Inputs!" in v and k in ("days", "rent", "other")
            cell.font = font(
                BLUE_INPUT if k == "month" else (GREEN_LINK if is_link else "000000"),
                bold=k in ("rev", "gp", "ebitda", "ni", "close_cash"),
            )
            cell.number_format = {
                "month": "0",
                "year": "0",
                "ramp": F_PCT,
                "cust": F_DEC1,
                "ticket": F_USD2,
                "days": F_INT,
                "pos_flag": "0",
            }.get(k, F_USD)
            if k in ("gp", "ebitda", "ni", "close_cash"):
                cell.border = TOTAL_TOP
        mo.column_dimensions[c].width = 11
    mo.column_dimensions["A"].width = 30
    mo.column_dimensions["B"].width = 2
    mo.freeze_panes = mo.cell(row=5, column=first_col)
    mrange = lambda key: f"Monthly!${L(first_col)}${R[key]}:${L(last_col)}${R[key]}"  # noqa: E731

    # ---------------- Annual P&L ----------------------------------------
    pl = wb.create_sheet("P&L")
    title(pl, "Annual P&L and cash", "Rolled up from the Monthly sheet with SUMIF on the year row.", 1 + years)
    pl.cell(row=3, column=1, value="Year #").font = font("6B7280", size=9)
    pl.cell(row=4, column=1, value="").font = font()
    for y in range(1, years + 1):
        col = 1 + y
        pl.cell(row=3, column=col, value=y).font = font("6B7280", size=9)
        h = pl.cell(row=4, column=col, value=f"Year {y}")
        h.font = font(bold=True)
        h.alignment = Alignment(horizontal="right")
        h.border = BOTTOM
    year_rng = f"Monthly!${L(first_col)}${R['year']}:${L(last_col)}${R['year']}"
    pl_rows = [
        ("Revenue", "rev", True),
        ("COGS", "cogs", False),
        ("Gross profit", "gp", True),
        ("Gross margin", "=IF({c}5=0,0,{c}7/{c}5)", False),
        ("Rent", "rent", False),
        ("Payroll", "payroll", False),
        ("Marketing", "mkt", False),
        ("Utilities & other", "other", False),
        ("Total operating expenses", "opex", True),
        ("EBITDA", "ebitda", True),
        ("EBITDA margin", "=IF({c}5=0,0,{c}14/{c}5)", False),
        ("Depreciation", "dep", False),
        ("EBIT", "ebit", False),
        ("Income tax", "tax", False),
        ("Net income", "ni", True),
        ("Net margin", "=IF({c}5=0,0,{c}19/{c}5)", False),
        ("Year-end cash", "=INDEX(Monthly!${a}${r}:${b}${r},{c}3*12)", True),
    ]
    pl_row = {}
    for i, (label, key, bold) in enumerate(pl_rows):
        row = 5 + i
        pl_row[label] = row
        pl.cell(row=row, column=1, value=label).font = font(bold=bold)
        for y in range(1, years + 1):
            c = L(1 + y)
            if key.startswith("="):
                v = key.format(c=c, a=L(first_col), b=L(last_col), r=R["close_cash"])
            else:
                v = f"=SUMIF({year_rng},{c}$3,{mrange(key)})"
            cell = pl.cell(row=row, column=1 + y, value=v)
            cell.font = font(bold=bold)
            cell.number_format = F_PCT if "margin" in label.lower() else F_USD
            if label in ("Gross profit", "EBITDA", "Net income"):
                cell.border = TOTAL_TOP
    pl.column_dimensions["A"].width = 30
    for y in range(1, years + 1):
        pl.column_dimensions[L(1 + y)].width = 14
    pl.freeze_panes = "B5"
    assert pl_row["Gross profit"] == 7 and pl_row["EBITDA"] == 14 and pl_row["Net income"] == 19

    # ---------------- Dashboard -----------------------------------------
    title(
        dash,
        brief["model_name"],
        "Change the scenario in B4 (1 = Low, 2 = Base, 3 = High); every sheet recalculates.",
        1 + years,
    )
    dash["A4"] = "Scenario selector"
    dash["A4"].font = font(bold=True)
    dash["B4"] = int(brief.get("default_scenario", 2))
    dash["B4"].font = font(BLUE_INPUT, bold=True)
    dash["B4"].fill = PatternFill("solid", fgColor="FFFF00")
    dash["B4"].alignment = Alignment(horizontal="center")
    dash["C4"] = '=CHOOSE(B4,"Low","Base","High")'
    dash["C4"].font = font("C55A11", bold=True)
    dv = DataValidation(
        type="list",
        formula1='"1,2,3"',
        allow_blank=False,
        showErrorMessage=True,
        errorTitle="Scenario",
        error="Enter 1, 2 or 3",
    )
    dash.add_data_validation(dv)
    dv.add("B4")
    section(dash, 6, "Key metrics", 1 + years)
    for y in range(1, years + 1):
        h = dash.cell(row=7, column=1 + y, value=f"Year {y}")
        h.font = font(bold=True)
        h.alignment = Alignment(horizontal="right")
        h.border = BOTTOM
    metrics = ["Revenue", "Gross profit", "EBITDA", "EBITDA margin", "Net income", "Year-end cash"]
    for i, mname in enumerate(metrics):
        row = 8 + i
        dash.cell(row=row, column=1, value=mname).font = font(bold=mname in ("Revenue", "EBITDA"))
        for y in range(1, years + 1):
            c = L(1 + y)
            cell = dash.cell(row=row, column=1 + y, value=f"='P&L'!{c}{pl_row[mname]}")
            cell.font = font(GREEN_LINK)
            cell.number_format = F_PCT if "margin" in mname else F_USD
    section(dash, 15, "Health", 1 + years)
    health = [
        ("First month with positive EBITDA", f'=IFERROR(MATCH(1,{mrange("pos_flag")},0),"Not within horizon")', "0"),
        ("Lowest cash balance", f"=MIN({mrange('close_cash')})", F_USD),
        ("Month of lowest cash", f"=MATCH(B17,{mrange('close_cash')},0)", "0"),
        ("Model checks", "=Checks!B13", "@"),
    ]
    for i, (label, formula, fmt) in enumerate(health):
        row = 16 + i
        dash.cell(row=row, column=1, value=label).font = font()
        cell = dash.cell(row=row, column=2, value=formula)
        cell.font = font(bold=True)
        cell.number_format = fmt
    dash.column_dimensions["A"].width = 34
    for y in range(1, years + 1):
        dash.column_dimensions[L(1 + y)].width = 14
    dash.column_dimensions["C"].width = max(dash.column_dimensions["C"].width or 0, 14)

    # ---------------- Checks --------------------------------------------
    ck = wb.create_sheet("Checks")
    title(ck, "Model checks", "Live formulas: they re-run every time an input changes.", 3)
    for i, h in enumerate(["Check", "Result", "What it tests"], 1):
        c = ck.cell(row=3, column=i, value=h)
        c.font = font(bold=True)
        c.border = BOTTOM
    last_y = L(1 + years)
    rv = pl_row["Revenue"]
    ir = lambda key, col: f"Inputs!${col}${ref[key + '_row']}"  # noqa: E731
    checks = [
        (
            "Annual revenue ties to monthly",
            f'=IF(ABS(SUM(\'P&L\'!B{rv}:{last_y}{rv})-SUM({mrange("rev")}))<0.5,"PASS","FAIL")',
            "Sum of annual revenue equals sum of monthly revenue",
        ),
        (
            "Cash roll-forward",
            f'=IF(ABS(Monthly!${L(last_col)}${R["close_cash"]}-(Monthly!${L(first_col)}${R["open_cash"]}+SUM({mrange("ocf")})))<0.5,"PASS","FAIL")',
            "Closing cash = opening cash + all operating cash flow",
        ),
        (
            "EBITDA reconciliation",
            f'=IF(ABS(SUM({mrange("ebitda")})-SUM({mrange("gp")})-SUM({mrange("opex")}))<0.5,"PASS","FAIL")',
            "EBITDA = gross profit − operating expenses, every month",
        ),
        (
            "Scenario selector valid",
            '=IF(AND(ISNUMBER(Dashboard!B4),Dashboard!B4>=1,Dashboard!B4<=3,INT(Dashboard!B4)=Dashboard!B4),"PASS","FAIL")',
            "Dashboard!B4 is 1, 2 or 3",
        ),
        (
            "Scenario ordering on revenue drivers",
            f"=IF(AND({ir('cust_full', 'B')}<={ir('cust_full', 'C')},{ir('cust_full', 'C')}<={ir('cust_full', 'D')},"
            f'{ir("ticket", "B")}<={ir("ticket", "C")},{ir("ticket", "C")}<={ir("ticket", "D")}),"PASS","FAIL")',
            "Low ≤ Base ≤ High for traffic and ticket",
        ),
        (
            "Margins within 0–100%",
            f"=IF(AND(MIN('P&L'!B{pl_row['Gross margin']}:{last_y}{pl_row['Gross margin']})>=0,"
            f'MAX(\'P&L\'!B{pl_row["Gross margin"]}:{last_y}{pl_row["Gross margin"]})<=1),"PASS","FAIL")',
            "Gross margin never negative or above 100%",
        ),
        (
            "No error values",
            f'=IF(SUMPRODUCT(--ISERROR(Monthly!${L(first_col)}$3:${L(last_col)}${R["pos_flag"]}))=0,"PASS","FAIL")',
            "No error values (divide-by-zero, broken references, bad types) in the monthly grid",
        ),
        (
            "Funding sufficient (cash ≥ 0)",
            f'=IF(MIN({mrange("close_cash")})>=0,"PASS","WARN")',
            "Business warning, not an error: cash dips below zero in this scenario",
        ),
    ]
    for i, (name, formula, desc) in enumerate(checks):
        row = 4 + i
        ck.cell(row=row, column=1, value=name).font = font()
        ck.cell(row=row, column=2, value=formula).font = font(bold=True)
        ck.cell(row=row, column=3, value=desc).font = font("6B7280", size=9)
    ck["A13"] = "Overall verdict"
    ck["A13"].font = font(bold=True)
    ck["B13"] = '=IF(COUNTIF(B4:B11,"FAIL")>0,"FAIL",IF(COUNTIF(B4:B11,"WARN")>0,"PASS WITH WARNINGS","PASS"))'
    ck["B13"].font = font(bold=True)
    ck["B13"].border = TOTAL_TOP
    ck.column_dimensions["A"].width = 38
    ck.column_dimensions["B"].width = 22
    ck.column_dimensions["C"].width = 60

    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False
    wb.save(out_path)


if __name__ == "__main__":
    with open(sys.argv[1], encoding="utf-8") as fh:
        build(json.load(fh), sys.argv[2])
    print("written", sys.argv[2])
