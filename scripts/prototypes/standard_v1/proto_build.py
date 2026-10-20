"""Prototype of workbook standard v1 on top of a real engine-built SaaS model.

Usage: python proto_build.py <raw engine workbook> <out.xlsx> [snapshot.json]
Keeps every engine cell (formulas and addresses) and adds presentation sheets + a new look.
"""

from __future__ import annotations

import json
import re
import sys

from openpyxl import load_workbook
from openpyxl.chart import BarChart, DoughnutChart, LineChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.drawing.line import LineProperties
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter as L
from openpyxl.worksheet.datavalidation import DataValidation

RAW, OUT = sys.argv[1], sys.argv[2]
SNAP = json.load(open(sys.argv[3])) if len(sys.argv) > 3 else None

# ---------------------------------------------------------------- tokens
INK, PINE, SAGE, PAPER, RED, AMBER, GREY, MUTED = (
    "1B2A2F", "0F6E56", "7FB5A3", "F7F8F3", "B8322A", "D9A21B", "A3ABA8", "6B7280")
BLUE, GREEN, BLACK, WHITE = "0000FF", "008000", "000000", "FFFFFF"
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
SELECT_FILL = PatternFill("solid", fgColor="FFE08A")
CALC_FILL = PatternFill("solid", fgColor="F1F3EE")
PAPER_FILL = PatternFill("solid", fgColor=PAPER)
BAND_FILL = PatternFill("solid", fgColor=PINE)
NOFILL = PatternFill(fill_type=None)
thin_g = Side(style="thin", color="C9CEC9")
thin_ink = Side(style="thin", color=INK)
med_ink = Side(style="medium", color=INK)
dbl_ink = Side(style="double", color=INK)
MONEY = '$#,##0;($#,##0);"-"'
PCT = '0.0%;(0.0%);"-"'
MULT = '0.0"x";(0.0"x");"-"'
NUM = '#,##0;(#,##0);"-"'
MONEY_K = '$#,##0,;($#,##0,);"-"'
TILE_M = '$#,##0.0,,"M";($#,##0.0,,"M");"-"'


def F(color=BLACK, bold=False, size=9, italic=False, underline=None):
    return Font(name="Arial", size=size, bold=bold, italic=italic, color=color, underline=underline)


wb = load_workbook(RAW)

# ---------------------------------------------------------------- 1. re-plan sheets
old_dash, old_sum = wb["Dashboard"], wb["Summary"]
old_dash.title = "KPIs"  # formulas elsewhere keep "Dashboard!$B$4" -> the new Dashboard (selector stays at B4)
wb.remove(old_sum)
for dv in list(old_dash.data_validations.dataValidation):
    old_dash.data_validations.dataValidation.remove(dv)

pl, cf, bs, inp, mon = wb["P&L"], wb["Cash Flow"], wb["Balance Sheet"], wb["Inputs"], wb["Monthly"]
be, val, chk, hc, kpi = wb["Break-even"], wb["Valuation"], wb["Checks"], wb["Headcount"], old_dash
MODEL_NAME = "SaaS company — financial model"
YEARS = 5
YC = ["B", "C", "D", "E", "F"]


def mrow(ws, r):
    """Monthly row behind an annual statement row (last Monthly!$C$n reference in its formula)."""
    hits = re.findall(r"Monthly!\$C\$(\d+):\$BJ\$\d+", str(ws[f"B{r}"].value))
    return int(hits[-1])


def find(ws, label, col=1, exact=False):
    for r in range(1, ws.max_row + 1):
        v = ws.cell(r, col).value
        if isinstance(v, str) and (v.strip() == label if exact else v.strip().startswith(label)):
            return r
    raise KeyError(f"{ws.title}: {label}")


R = {  # statement rows
    "rev": find(pl, "Revenue", exact=True), "cogs": find(pl, "Hosting"), "gp": find(pl, "Gross profit"),
    "gm": find(pl, "Gross margin"), "pay": find(pl, "Payroll"), "mkt": find(pl, "Paid marketing"),
    "opex": find(pl, "Total operating"), "ebitda": find(pl, "EBITDA"), "ebitdam": find(pl, "EBITDA margin"),
    "dep": find(pl, "Depreciation"), "ebit": find(pl, "EBIT", exact=True), "int": find(pl, "Interest"),
    "pbt": find(pl, "Pre-tax"), "tax": find(pl, "Income tax"), "ni": find(pl, "Net income"),
    "nm": find(pl, "Net margin"),
    "cfo": find(cf, "Operating cash flow"), "capex": find(cf, "Capital spending"), "eq": find(cf, "Equity raised"),
    "draw": find(cf, "Loan drawdown"), "repay": find(cf, "Loan repayment"), "cff": find(cf, "Financing cash flow"),
    "net": find(cf, "Net change"), "close": find(cf, "Closing cash"),
    "cash": find(bs, "Cash", exact=True), "ar": find(bs, "Accounts receivable"), "inv": find(bs, "Inventory"),
    "fa": find(bs, "Net fixed"), "ta": find(bs, "Total assets"), "ap": find(bs, "Accounts payable"),
    "dr": find(bs, "Deferred"), "loan": find(bs, "Loan", exact=True), "tl": find(bs, "Total liabilities", exact=True),
    "pic": find(bs, "Paid-in"), "re": find(bs, "Retained"), "te": find(bs, "Total equity"),
    "tle": find(bs, "Total liabilities &"),
}
M = {k: mrow(ws, R[k]) for ws, keys in (
    (pl, "rev cogs gp pay mkt opex ebitda dep ebit int pbt tax ni".split()),
    (cf, "cfo capex eq draw repay cff net close".split()),
    (bs, "cash ar inv fa ta ap dr loan tl pic re te tle".split())) for k in keys}
MCLOSE = M["close"]
K = {  # KPI rows on the renamed sheet
    "cust": find(kpi, "Customers (year end)"), "arr": find(kpi, "ARR"), "ltvcac": find(kpi, "LTV"),
    "payback": find(kpi, "CAC payback"), "cac": find(kpi, "Blended CAC"), "runway": find(kpi, "Runway"),
}

# ---------------------------------------------------------------- helpers
def title_block(ws, title, sub, link_col):
    ws["A1"], ws["A2"] = title, sub
    ws["A1"].font, ws["A2"].font = F(INK, True, 14), F(MUTED, size=9)
    ws["A1"].fill = ws["A2"].fill = NOFILL
    for c in range(2, 30):
        if ws.cell(1, c).fill.fgColor.rgb in ("FF1F3864", "001F3864"):
            ws.cell(1, c).fill = NOFILL
    ws.row_dimensions[1].height = 22
    c = ws[f"{link_col}1"]
    if ws.title != "Cover":
        c.value = '=HYPERLINK("#\'Cover\'!A1","◂ Contents")'
        c.font = F(PINE, size=8, underline="single")


def band(ws, r, c1, c2, text):
    ws.cell(r, c1, text)
    for c in range(c1, c2 + 1):
        x = ws.cell(r, c)
        x.fill, x.font = BAND_FILL, F(WHITE, True, 9)
        x.alignment = Alignment(vertical="center")
    ws.row_dimensions[r].height = 16


def header_row(ws, r, c1, c2):
    for c in range(c1, c2 + 1):
        x = ws.cell(r, c)
        x.font = F(INK, True)
        x.border = Border(bottom=med_ink)
        if c > c1:
            x.alignment = Alignment(horizontal="right")


def put(ws, ref, value, fmt=None, color=BLACK, bold=False, italic=False, fill=None, align=None, size=9):
    c = ws[ref]
    c.value = value
    c.font = F(color, bold, size, italic)
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    if align:
        c.alignment = Alignment(horizontal=align, vertical="center")
    return c


def total(ws, r, c1, c2, double=False):
    for c in range(c1, c2 + 1):
        x = ws.cell(r, c)
        x.font = F(x.font.color.rgb[-6:] if x.font.color is not None and x.font.color.type == "rgb" else BLACK, True)
        x.border = Border(top=thin_ink, bottom=dbl_ink if double else None)


def link_color(v):
    return GREEN if isinstance(v, str) and "!" in v else BLACK


def setup(ws, tab, landscape=True, zoom=100):
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = zoom
    ws.sheet_properties.tabColor = tab
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.oddFooter.left.text, ws.oddFooter.right.text = "&A", "Page &P of &N"
    ws.oddFooter.left.size = ws.oddFooter.right.size = 8


from openpyxl.chart.text import RichText, Text  # noqa: E402
from openpyxl.chart.title import Title  # noqa: E402
from openpyxl.drawing.text import CharacterProperties, Paragraph, ParagraphProperties, RegularTextRun  # noqa: E402
from openpyxl.drawing.text import Font as DFont  # noqa: E402


def _cp(sz, bold=False, color=MUTED):
    return CharacterProperties(sz=sz, b=bold, solidFill=color, latin=DFont(typeface="Arial"))


def _rich(sz, color=MUTED):
    return RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=_cp(sz, color=color)), endParaRPr=_cp(sz, color=color))])


def ctitle(text):
    cp = _cp(1000, True, INK)
    return Title(tx=Text(rich=RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp),
                                                   r=[RegularTextRun(rPr=cp, t=text)])])), overlay=False)


def style_chart(ch, title, w=10.2, h=7.4, legend=True):
    ch.title = ctitle(title)
    ch.width, ch.height = w, h
    ch.style = 2
    ch.graphical_properties = GraphicalProperties(ln=LineProperties(noFill=True))
    if legend:
        ch.legend.position = "b"
        ch.legend.txPr = _rich(800)
    else:
        ch.legend = None
    if not hasattr(ch, "x_axis"):
        return ch
    for ax in (ch.x_axis, ch.y_axis):
        ax.delete = False
        ax.txPr = _rich(800)
    ch.y_axis.majorGridlines.spPr = GraphicalProperties(ln=LineProperties(solidFill="E3E6E1"))
    ch.y_axis.spPr = GraphicalProperties(ln=LineProperties(noFill=True))
    ch.x_axis.spPr = GraphicalProperties(ln=LineProperties(solidFill="9AA3A0"))
    ch.x_axis.tickLblPos = "low"  # year labels stay below the plot when values go negative
    return ch


def color_series(ch, colors, line=False):
    for s, col in zip(ch.series, colors):
        if line:
            s.graphicalProperties.line.solidFill = col
            s.graphicalProperties.line.width = 28000
            s.marker.symbol = "circle"
            s.marker.size = 6
            s.marker.graphicalProperties = GraphicalProperties(solidFill=col, ln=LineProperties(solidFill=col))
            s.smooth = False
        else:
            s.graphicalProperties = GraphicalProperties(solidFill=col, ln=LineProperties(noFill=True))


def labels(ch, fmt=None, pos=None):
    d = DataLabelList()
    d.showVal = True
    d.showSerName = d.showCatName = d.showLegendKey = d.showPercent = False
    if fmt:
        d.numFmt = fmt
    if pos:
        d.position = pos
    ch.dataLabels = d


def yfmt(ch, fmt):
    ch.y_axis.number_format = fmt
    ch.y_axis.numFmt.sourceLinked = False if ch.y_axis.numFmt is not None else None


def bar(ws, rows, cats, title, colors, fmt='$#,##0.0,,"M"', stacked=False, w=10.2, h=7.4):
    ch = BarChart()
    ch.type, ch.gapWidth = "col", 60
    if stacked:
        ch.grouping, ch.overlap = "stacked", 100
    for r in rows:
        ch.add_data(Reference(ws, min_col=1, max_col=1 + YEARS, min_row=r, max_row=r), titles_from_data=True,
                    from_rows=True)
    ch.set_categories(cats)
    style_chart(ch, title, w, h)
    color_series(ch, colors)
    ch.y_axis.number_format = fmt
    return ch


def line(ws, rows, cats, title, colors, fmt='$#,##0.0,,"M"', w=10.2, h=7.4):
    ch = LineChart()
    for r in rows:
        ch.add_data(Reference(ws, min_col=1, max_col=1 + YEARS, min_row=r, max_row=r), titles_from_data=True,
                    from_rows=True)
    ch.set_categories(cats)
    style_chart(ch, title, w, h)
    color_series(ch, colors, line=True)
    ch.y_axis.number_format = fmt
    return ch


def secondary_line(base, ws, r, color, fmt):
    ln = LineChart()
    ln.add_data(Reference(ws, min_col=1, max_col=1 + YEARS, min_row=r, max_row=r), titles_from_data=True,
                from_rows=True)
    ln.y_axis.axId = 200
    ln.y_axis.crosses = "max"
    ln.y_axis.delete = False
    ln.y_axis.number_format = fmt
    ln.y_axis.majorGridlines = None
    ln.y_axis.spPr = GraphicalProperties(ln=LineProperties(noFill=True))
    ln.y_axis.txPr = _rich(800)
    color_series(ln, [color], line=True)
    base += ln
    return base


def year_cats(ws, r):
    return Reference(ws, min_col=2, max_col=1 + YEARS, min_row=r, max_row=r)


# ---------------------------------------------------------------- 2. restyle engine sheets
TOTALS = ("Gross profit", "Total operating expenses", "EBITDA", "EBIT", "Pre-tax income", "Operating cash flow",
          "Financing cash flow", "Net change in cash", "Total assets", "Total liabilities", "Total equity",
          "Total uses of funds", "Total sources of funds", "Funding required", "Enterprise value",
          "Customers — closing", "Closing MRR", "Net cash flow", "Total FTE")
KEY_TOTALS = ("Net income", "Closing cash", "Total liabilities & equity", "Funding surplus")


def restyle(ws, ncols):
    for row in ws.iter_rows():
        for c in row:
            f = c.font
            col = f.color.rgb[-6:] if f.color is not None and f.color.type == "rgb" and f.color.rgb else BLACK
            fill = c.fill.fgColor.rgb[-6:] if c.fill.fill_type == "solid" and c.fill.fgColor.type == "rgb" else None
            if fill == "2F5597":  # engine section band -> pine band
                c.fill, c.font = BAND_FILL, F(WHITE, True)
                continue
            if fill == "1F3864":
                c.fill = NOFILL
            c.font = F(col if col != "FFFFFF" else INK, f.bold, 9 if (f.sz or 10) <= 11 else f.sz, f.italic)
            if c.border.bottom is not None and c.border.bottom.style == "thin" and f.bold:
                c.border = Border(bottom=med_ink)
    for r in range(1, ws.max_row + 1):
        a = ws.cell(r, 1).value
        if not isinstance(a, str) or ws.title == "Checks":
            continue
        if a.startswith(("Year #", "Period #")):
            for c in range(1, ncols + 1):
                ws.cell(r, c).font = F(GREY, size=7)
        if a.endswith("margin") or a.startswith(("Gross margin", "EBITDA margin", "Net margin")):
            for c in range(1, ncols + 1):
                ws.cell(r, c).font = F(MUTED, italic=True)
        elif ws.title == "Cash Flow" and a == "Net income":
            pass
        elif any(a.startswith(t) for t in KEY_TOTALS):
            total(ws, r, 1, ncols, double=True)
        elif any(a.startswith(t) for t in TOTALS):
            total(ws, r, 1, ncols)


SHEET_COLS = {pl: 6, cf: 6, bs: 6, be: 6, val: 6, chk: 3, inp: 7, mon: 62, hc: 62, kpi: 6}
for ws, n in SHEET_COLS.items():
    restyle(ws, n)
for ws in (pl, cf, bs):
    title_block(ws, ws["A1"].value, ws["A2"].value, "H")
    header_row(ws, 4, 1, 6)
for ws in (be, val):
    title_block(ws, ws["A1"].value, ws["A2"].value, "H")
title_block(chk, chk["A1"].value, chk["A2"].value, "E")
for ws in (mon, hc):
    title_block(ws, ws["A1"].value, ws["A2"].value, "D")
    header_row(ws, 3, 1, 62)

# year header rows on goal sheets
for ws, r in ((be, find(be, "Year #") + 1), (val, find(val, "Year #") + 1)):
    header_row(ws, r, 1, 6)
header_row(val, find(val, "Enterprise value") + 1, 1, 3)
header_row(chk, 3, 1, 3)

# Inputs: yellow input cells with blue figures, grey active column
title_block(inp, "Inputs", "Every assumption lives here once, with Low / Base / High values. Change the yellow "
            "cells; the active scenario is chosen on the Dashboard.", "I")
header_row(inp, 5, 1, 7)
inp["G5"] = "Source / comment"
inp["G5"].font = F(INK, True)
for r in range(6, inp.max_row + 1):
    a = inp.cell(r, 1).value
    if inp.cell(r, 2).value is None or isinstance(inp.cell(r, 2).value, str):
        continue
    for c in (2, 3, 4):
        x = inp.cell(r, c)
        x.fill, x.font = INPUT_FILL, F(BLUE)
        x.border = Border(left=thin_g, right=thin_g, top=thin_g, bottom=thin_g)
    inp.cell(r, 5).fill = CALC_FILL
    inp.cell(r, 5).font = F(BLACK, True)
    inp.cell(r, 6).font = F(MUTED, italic=True)
    if a and inp.cell(r, 7).value is None:
        inp.cell(r, 7).border = Border(bottom=thin_g)
leg = find(inp, "Legend")
inp.cell(leg, 1).value = ("Legend: yellow cell with blue figure = input you can change · black = formula · "
                          "green = link to another sheet · grey = active value used by the model")
inp.cell(leg, 1).font = F(MUTED, italic=True, size=8)
inp.column_dimensions["G"].width = 34
inp.freeze_panes = "B6"

# Checks: verdict colours, new Sources & Uses check, wider error scan
chk["B17"] = chk["B17"].value.replace("Summary!$B$8:$F$8", "Summary!$B$7:$F$7")
b18 = chk["B18"].value
b18 = b18.replace("Dashboard!$B$25:$F$44", "KPIs!$B$4:$F$44")
b18 = re.sub(r"\+SUMPRODUCT\(--ISERROR\(Summary![^)]*\)\)", "", b18)
i18 = b18.rfind("=0,")
b18 = (b18[:i18] + "+SUMPRODUCT(--ISERROR(Summary!$B$5:$S$55))+SUMPRODUCT(--ISERROR(Dashboard!$A$6:$W$45))"
       "+SUMPRODUCT(--ISERROR(Scenarios!$B$5:$F$60))+SUMPRODUCT(--ISERROR('Sources & Uses'!$B$5:$G$30))" + b18[i18:])
chk["B18"] = b18
chk["A21"], chk["C21"] = "Sources & uses balance", "Sources of funds = uses of funds (incl. closing cash) for the period"
chk["B21"] = "=IF(ABS('Sources & Uses'!B21-'Sources & Uses'!F21)<0.5,\"PASS\",\"FAIL\")"
for c in ("A21", "C21"):
    chk[c].font = F()
chk["B22"] = chk["B22"].value.replace("B4:B20", "B4:B21")
for ref in ("B4:B22",):
    chk.conditional_formatting.add(ref, FormulaRule(formula=['ISNUMBER(SEARCH("FAIL",B4))'],
                                                    fill=PatternFill("solid", fgColor="F6D5D2"), font=F(RED, True)))
    chk.conditional_formatting.add(ref, FormulaRule(formula=['ISNUMBER(SEARCH("WARN",B4))'],
                                                    fill=PatternFill("solid", fgColor="FBEFCF"), font=F("8A6100", True)))
    chk.conditional_formatting.add(ref, FormulaRule(formula=['B4="PASS"'],
                                                    fill=PatternFill("solid", fgColor="DCEFE8"), font=F(PINE, True)))
total(chk, 22, 1, 3, double=True)

# ---------------------------------------------------------------- 3. KPIs & ratios (renamed engine Dashboard)
for r in range(1, K["cust"] - 3):
    for c in range(1, 8):
        kpi.cell(r, c).value = None
        kpi.cell(r, c).fill, kpi.cell(r, c).border, kpi.cell(r, c).font = NOFILL, Border(), F()
title_block(kpi, "KPIs & ratios", "Industry metrics and financial ratios for the active scenario.", "I")
sec = K["cust"] - 3
band(kpi, sec, 1, 7, "SaaS metrics")
header_row(kpi, sec + 2, 1, 7)
kpi.cell(sec + 2, 7, "Target").font = F(INK, True)
for r in range(sec + 3, K["runway"] + 1):
    kpi.cell(r, 7).fill = INPUT_FILL
    kpi.cell(r, 7).border = Border(left=thin_g, right=thin_g, top=thin_g, bottom=thin_g)
r0 = 4
band(kpi, r0, 1, 7, "Financial ratios")
for i, c in enumerate(["", *[f"='P&L'!{x}4" for x in YC], "Target"]):
    kpi.cell(r0 + 1, 1 + i, c)
header_row(kpi, r0 + 1, 1, 7)
ratios = [
    ("Revenue growth", lambda x, p: "-" if p is None else f"=IF('P&L'!{p}{R['rev']}=0,0,'P&L'!{x}{R['rev']}/'P&L'!{p}{R['rev']}-1)", PCT),
    ("Gross margin", lambda x, p: f"='P&L'!{x}{R['gm']}", PCT),
    ("EBITDA margin", lambda x, p: f"='P&L'!{x}{R['ebitdam']}", PCT),
    ("Net margin", lambda x, p: f"='P&L'!{x}{R['nm']}", PCT),
    ("Payroll, % of revenue", lambda x, p: f"=IF('P&L'!{x}{R['rev']}=0,0,-'P&L'!{x}{R['pay']}/'P&L'!{x}{R['rev']})", PCT),
    ("Paid marketing, % of revenue", lambda x, p: f"=IF('P&L'!{x}{R['rev']}=0,0,-'P&L'!{x}{R['mkt']}/'P&L'!{x}{R['rev']})", PCT),
    ("Operating expenses, % of revenue", lambda x, p: f"=IF('P&L'!{x}{R['rev']}=0,0,-'P&L'!{x}{R['opex']}/'P&L'!{x}{R['rev']})", PCT),
    ("Current ratio (current assets ÷ current liabilities)",
     lambda x, p: f"=IF(('Balance Sheet'!{x}{R['ap']}+'Balance Sheet'!{x}{R['dr']})=0,0,('Balance Sheet'!{x}{R['cash']}+'Balance Sheet'!{x}{R['ar']}+'Balance Sheet'!{x}{R['inv']})/('Balance Sheet'!{x}{R['ap']}+'Balance Sheet'!{x}{R['dr']}))", MULT),
    ("Debt ÷ equity", lambda x, p: f"=IF('Balance Sheet'!{x}{R['te']}<=0,0,'Balance Sheet'!{x}{R['loan']}/'Balance Sheet'!{x}{R['te']})", MULT),
    ("Return on assets (net income ÷ year-end assets)", lambda x, p: f"=IF('Balance Sheet'!{x}{R['ta']}=0,0,'P&L'!{x}{R['ni']}/'Balance Sheet'!{x}{R['ta']})", PCT),
    ("Return on equity (net income ÷ year-end equity)", lambda x, p: f"=IF('Balance Sheet'!{x}{R['te']}<=0,0,'P&L'!{x}{R['ni']}/'Balance Sheet'!{x}{R['te']})", PCT),
]
rr = r0 + 2
for name, fn, fmt in ratios:
    kpi.cell(rr, 1, name).font = F()
    for i, x in enumerate(YC):
        put(kpi, f"{x}{rr}", fn(x, YC[i - 1] if i else None), fmt, color=GREEN, align="right")
    kpi.cell(rr, 7).fill = INPUT_FILL
    kpi.cell(rr, 7).border = Border(left=thin_g, right=thin_g, top=thin_g, bottom=thin_g)
    kpi.cell(rr, 7).number_format = fmt
    rr += 1
roe_row = rr - 1
rr += 1
band(kpi, rr, 1, 7, "DuPont analysis — return on equity = net margin × asset turnover × equity multiplier")
rr += 1
for i, c in enumerate(["", *[f"='P&L'!{x}4" for x in YC]]):
    kpi.cell(rr, 1 + i, c)
header_row(kpi, rr, 1, 6)
d0 = rr + 1
dup = [("Net margin", lambda x: f"='P&L'!{x}{R['nm']}", PCT),
       ("× Asset turnover (revenue ÷ assets)", lambda x: f"=IF('Balance Sheet'!{x}{R['ta']}=0,0,'P&L'!{x}{R['rev']}/'Balance Sheet'!{x}{R['ta']})", MULT),
       ("× Equity multiplier (assets ÷ equity)", lambda x: f"=IF('Balance Sheet'!{x}{R['te']}<=0,0,'Balance Sheet'!{x}{R['ta']}/'Balance Sheet'!{x}{R['te']})", MULT),
       ("Return on equity (product of the three)", lambda x: f"={x}{d0}*{x}{d0 + 1}*{x}{d0 + 2}", PCT)]
for j, (name, fn, fmt) in enumerate(dup):
    kpi.cell(d0 + j, 1, name).font = F()
    for x in YC:
        put(kpi, f"{x}{d0 + j}", fn(x), fmt, color=GREEN if j < 3 else BLACK, align="right")
total(kpi, d0 + 3, 1, 6, double=True)
assert d0 + 3 < sec, (d0, sec)
kpi.column_dimensions["A"].width = 41
kpi.column_dimensions["G"].width = 11
for x in YC:
    kpi.column_dimensions[x].width = 10.5
kpi.column_dimensions["H"].width = 2
for c in range(9, 25):
    kpi.column_dimensions[L(c)].width = 9
gm_row = r0 + 3
KW, KH = 14.2, 8.3
ch = line(kpi, [gm_row, gm_row + 1, gm_row + 2], year_cats(kpi, r0 + 1), "Margins", [PINE, AMBER, INK], fmt="0%",
          w=KW, h=KH)
kpi.add_chart(ch, "I4")
ch = bar(kpi, [K["ltvcac"]], year_cats(kpi, sec + 2), "LTV ÷ CAC", [PINE], fmt='0.0"x"', w=KW, h=KH)
labels(ch, None, "outEnd")
ch.legend = None
kpi.add_chart(ch, "Q4")
nc, lc = find(kpi, "New customers in the year"), find(kpi, "Customers lost in the year")
ch = bar(kpi, [nc, lc], year_cats(kpi, sec + 2), "Customers won and lost", [PINE, RED], fmt="#,##0", w=KW, h=KH)
kpi.add_chart(ch, "I21")
ch = line(kpi, [roe_row - 1, roe_row], year_cats(kpi, r0 + 1), "Return on assets and equity", [SAGE, INK], fmt="0%",
          w=KW, h=KH)
kpi.add_chart(ch, "Q21")

# Break-even: one large chart — revenue against the revenue needed for EBITDA = 0
be_hdr = find(be, "Year #") + 1
be_rev, be_ber = find(be, "Revenue", exact=True), find(be, "Break-even revenue")
ch = bar(be, [be_rev], year_cats(be, be_hdr), "Revenue vs break-even revenue (EBITDA = 0)", [PINE], w=20, h=10.5)
ln = LineChart()
ln.add_data(Reference(be, min_col=1, max_col=6, min_row=be_ber, max_row=be_ber), titles_from_data=True, from_rows=True)
color_series(ln, [AMBER], line=True)
ln.series[0].marker.size = 10
ch += ln
be.add_chart(ch, "H5")

# ---------------------------------------------------------------- 4. new sheets
cover = wb.create_sheet("Cover")
dash = wb.create_sheet("Dashboard")
summ = wb.create_sheet("Summary")
scen = wb.create_sheet("Scenarios")
su = wb.create_sheet("Sources & Uses")

# ---- Dashboard: one 68 px grid — A = 3 grid cells, B:F years, G gap, H:O and P:W chart columns
title_block(dash, "Dashboard", MODEL_NAME, "W")
dash.column_dimensions["A"].width = 28.4
for c in range(2, 24):
    dash.column_dimensions[L(c)].width = 9
dash.column_dimensions["G"].width = 2
put(dash, "A4", "Active scenario", bold=True, color=INK)
sel = put(dash, "B4", 2, "0", color=BLUE, bold=True, fill=SELECT_FILL, align="center", size=11)
sel.border = Border(left=med_ink, right=med_ink, top=med_ink, bottom=med_ink)
dv = DataValidation(type="list", formula1='"1,2,3"', allow_blank=False, showInputMessage=True,
                    promptTitle="Scenario", prompt="1 = Low, 2 = Base, 3 = High")
dash.add_data_validation(dv)
dv.add("B4")
put(dash, "C4", '=CHOOSE(B4,"Low","Base","High")', color=PINE, bold=True, size=11)
put(dash, "D4", "1 = Low · 2 = Base · 3 = High — every sheet follows this cell", color=MUTED, italic=True, size=8)
put(dash, "S4", "Model checks", color=INK, bold=True, align="right")
dash.merge_cells("T4:W4")
put(dash, "T4", "=Checks!B22", bold=True, align="center")
for rule in (('ISNUMBER(SEARCH("FAIL",$T$4))', "F6D5D2", RED), ('ISNUMBER(SEARCH("WARN",$T$4))', "FBEFCF", "8A6100"),
             ('$T$4="PASS"', "DCEFE8", PINE)):
    dash.conditional_formatting.add("T4:W4", FormulaRule(formula=[rule[0]], fill=PatternFill("solid", fgColor=rule[1]),
                                                         font=F(rule[2], True)))
dash.row_dimensions[4].height = 20

tiles = [  # (range, label, value, fmt, sub) — six tiles of 272 px each
    ("A:B", "REVENUE · YEAR 5", f"='P&L'!F{R['rev']}", TILE_M,
     f"=IF('P&L'!B{R['rev']}>0,\"CAGR \"&TEXT(('P&L'!F{R['rev']}/'P&L'!B{R['rev']})^(1/4)-1,\"0%\"),\"\")"),
    ("C:F", "EBITDA MARGIN · YEAR 5", f"='P&L'!F{R['ebitdam']}", '0.0%;(0.0%);"-"',
     f"=\"EBITDA \"&TEXT('P&L'!F{R['ebitda']}/1000000,\"$0.0\")&\"M\""),
    ("H:K", "NET INCOME · YEAR 5", f"='P&L'!F{R['ni']}", TILE_M,
     f"=\"Net margin \"&TEXT('P&L'!F{R['nm']},\"0%\")"),
    ("L:O", "LOWEST CASH BALANCE", f"=MIN(Monthly!$C${MCLOSE}:$BJ${MCLOSE})", TILE_M,
     f"=\"in month \"&MATCH(MIN(Monthly!$C${MCLOSE}:$BJ${MCLOSE}),Monthly!$C${MCLOSE}:$BJ${MCLOSE},0)"),
    ("P:S", "FUNDING REQUIRED", "='Break-even'!B12", TILE_M,
     "=IF('Break-even'!B17>=0,\"Covered by funding raised\",\"Shortfall \"&TEXT(-'Break-even'!B17/1000000,\"$0.0\")&\"M\")"),
    ("T:W", "ENTERPRISE VALUE (DCF)", "=Valuation!B30", TILE_M, "=\"Average of 2 methods\""),
]
for rng, lab, v, fmt, sub in tiles:
    a, b = rng.split(":")
    for r, text, font in ((6, lab, F(MUTED, True, 7)), (7, v, F(INK, True, 18)), (8, sub, F(PINE, size=8))):
        dash.merge_cells(f"{a}{r}:{b}{r}")
        c = dash[f"{a}{r}"]
        c.value, c.font = text, font
        c.alignment = Alignment(horizontal="center", vertical="center")
        if r == 7:
            c.number_format = fmt
        for col in range(dash[f"{a}1"].column, dash[f"{b}1"].column + 1):
            x = dash.cell(r, col)
            x.fill = PAPER_FILL
            x.border = Border(top=Side(style="thick", color=PINE) if r == 6 else None,
                              left=Side(style="thin", color="FFFFFF"), right=Side(style="thin", color="FFFFFF"))
dash.row_dimensions[6].height, dash.row_dimensions[7].height, dash.row_dimensions[8].height = 16, 30, 15


def year_header(r):
    for x in YC:
        dash[f"{x}{r}"] = f"='P&L'!{x}4"
    header_row(dash, r, 1, 6)


band(dash, 10, 1, 6, "Core financials ($'000) — active scenario")
year_header(11)
core = [
    ("Revenue", "P&L", R["rev"], MONEY_K, None), ("Gross profit", "P&L", R["gp"], MONEY_K, "t"),
    ("Gross margin", "P&L", R["gm"], PCT, "%"), ("Operating expenses", "P&L", R["opex"], MONEY_K, None),
    ("EBITDA", "P&L", R["ebitda"], MONEY_K, "t"), ("EBITDA margin", "P&L", R["ebitdam"], PCT, "%"),
    ("Net income", "P&L", R["ni"], MONEY_K, "tt"), ("Net margin", "P&L", R["nm"], PCT, "%"),
    ("Operating cash flow", "Cash Flow", R["cfo"], MONEY_K, None), ("Investing cash flow", "Cash Flow", R["capex"], MONEY_K, None),
    ("Financing cash flow", "Cash Flow", R["cff"], MONEY_K, None), ("Net change in cash", "Cash Flow", R["net"], MONEY_K, "t"),
    ("Year-end cash", "Balance Sheet", R["cash"], MONEY_K, "tt"),
]
D = {}
r = 12
for name, sh, row, fmt, kind in core:
    dash.cell(r, 1, name).font = F(MUTED, italic=True) if kind == "%" else F()
    for x in YC:
        put(dash, f"{x}{r}", f"='{sh}'!{x}{row}", fmt, color=GREEN, align="right", italic=kind == "%")
    if kind == "t":
        total(dash, r, 1, 6)
    if kind == "tt":
        total(dash, r, 1, 6, double=True)
    D[name] = r
    r += 1
r += 1  # 25 blank
band(dash, r, 1, 6, "SaaS metrics")
year_header(r + 1)
r += 2
for name, ref, fmt in (("Paying customers (year end)", K["cust"], NUM), ("ARR (year-end MRR × 12)", K["arr"], MONEY_K),
                       ("LTV ÷ CAC", K["ltvcac"], MULT)):
    dash.cell(r, 1, name).font = F()
    for x in YC:
        put(dash, f"{x}{r}", f"=KPIs!{x}{ref}", fmt, color=GREEN, align="right")
    D[name] = r
    r += 1
dash.cell(r, 1, "Team (FTE, year end)").font = F()
for i, x in enumerate(YC):
    put(dash, f"{x}{r}", f"=INDEX(Headcount!$C$12:$BJ$12,{12 * (i + 1)})", '#,##0.0', color=GREEN, align="right")
r += 2
band(dash, r, 1, 6, "Funding & valuation ($'000) — active scenario")
r += 1
eq_r, ln_r = find(inp, "Equity raised"), find(inp, "Loan drawn")
low = f"MIN(Monthly!$C${MCLOSE}:$BJ${MCLOSE})"
fund = [
    ("Equity raised", f"=Inputs!E{eq_r}", MONEY_K, None),
    ("Loan drawn", f"=Inputs!E{ln_r}", MONEY_K, None),
    ("Funding required (incl. cash buffer)", "='Break-even'!B12", MONEY_K, None),
    ("Funding surplus / (shortfall)", "='Break-even'!B17", MONEY_K, "t"),
    (f'="Lowest cash balance (month "&MATCH({low},Monthly!$C${MCLOSE}:$BJ${MCLOSE},0)&")"', f"={low}", MONEY_K, None),
    ("First month with positive EBITDA", "='Break-even'!B21", '"Month "0', None),
    ("Cash invested paid back", "=IF(ISNUMBER('Break-even'!B23),\"Month \"&'Break-even'!B23,'Break-even'!B23)", None, None),
    ("Enterprise value — perpetual growth", "=Valuation!B27", MONEY_K, None),
    ("Enterprise value — exit multiple", "=Valuation!C27", MONEY_K, None),
    ("Enterprise value — average", "=Valuation!B30", MONEY_K, "tt"),
]
for lab, v, fmt, kind in fund:
    put(dash, f"A{r}", lab)
    put(dash, f"F{r}", v, fmt, color=GREEN, align="right")
    for col in range(2, 7):
        dash.cell(r, col).border = Border(bottom=thin_g)
    if kind:
        total(dash, r, 1, 6, kind == "tt")
    r += 1
dash_last = r - 1

CW, CH = 14.2, 8.3  # standard chart size: 8 grid cells × 16 rows
cats = year_cats(dash, 11)
c1 = bar(dash, [D["Revenue"], D["EBITDA"]], cats, "Revenue & EBITDA", [PINE, SAGE], w=CW, h=CH)
c1 = secondary_line(c1, dash, D["EBITDA margin"], AMBER, "0%")
dash.add_chart(c1, "H10")
c2 = bar(dash, [D["Operating cash flow"], D["Investing cash flow"], D["Financing cash flow"]], cats,
         "Cash flow by activity", [PINE, GREY, AMBER], w=CW, h=CH)
dash.add_chart(c2, "P10")
c3 = bar(dash, [D["Year-end cash"]], cats, "Year-end cash", [INK], w=CW, h=CH)
labels(c3, None, "outEnd")
c3.legend = None
dash.add_chart(c3, "H27")
c4 = bar(dash, [D["ARR (year-end MRR × 12)"]], cats, "ARR & paying customers", [SAGE], w=CW, h=CH)
c4 = secondary_line(c4, dash, D["Paying customers (year end)"], INK, "#,##0")
dash.add_chart(c4, "P27")

# ---- Summary
title_block(summ, "Financial statements summary", MODEL_NAME, "U")
summ.column_dimensions["A"].width = 30
for x in YC:
    summ.column_dimensions[x].width = 11.5
summ.column_dimensions["G"].width = 2
for c in range(8, 20):
    summ.column_dimensions[L(c)].width = 9.2
put(summ, "P2", "Select detailed year:", color=INK, bold=True, align="right")
summ.merge_cells("R2:S2")
ys = put(summ, "R2", 1, '"Year "0', color=BLUE, bold=True, fill=SELECT_FILL, align="center")
ys.border = Border(left=med_ink, right=med_ink, top=med_ink, bottom=med_ink)
dv2 = DataValidation(type="list", formula1='"1,2,3,4,5"', showInputMessage=True, promptTitle="Detailed year",
                     prompt="Pick the year shown month by month on the right")
summ.add_data_validation(dv2)
dv2.add("R2")
MON = [L(c) for c in range(8, 20)]


def mref(row, k):
    return f"INDEX(Monthly!$C${row}:$BJ${row},($R$2-1)*12+{k})"


def block(top, title_l, title_r, lines):
    band(summ, top, 1, 6, title_l)
    band(summ, top, 8, 19, title_r)
    for x in YC:
        summ[f"{x}{top + 1}"] = f"='P&L'!{x}4"
    for k, x in enumerate(MON, start=1):
        summ[f"{x}{top + 1}"] = f"=INDEX(Monthly!$C$3:$BJ$3,($R$2-1)*12+{k})"
    header_row(summ, top + 1, 1, 6)
    header_row(summ, top + 1, 8, 19)
    rows = {}
    r = top + 2
    for name, sheet, srow, mrow_, kind in lines:
        rows[name] = r
        summ.cell(r, 1, name).font = F(MUTED, italic=True) if kind == "%" else F()
        for x in YC:
            put(summ, f"{x}{r}", f"='{sheet}'!{x}{srow}", PCT if kind == "%" else MONEY_K, color=GREEN, align="right",
                italic=kind == "%")
        for k, x in enumerate(MON, start=1):
            if kind == "%":
                num, den = mrow_
                v = f"=IF({x}{rows[den]}=0,0,{x}{rows[num]}/{x}{rows[den]})"
                put(summ, f"{x}{r}", v, PCT, italic=True, color=MUTED, align="right")
            else:
                sign = "-" if kind == "neg" else ""
                put(summ, f"{x}{r}", f"={sign}{mref(mrow_, k)}", MONEY_K, align="right")
        if kind in ("t", "tt"):
            total(summ, r, 1, 6, kind == "tt")
            total(summ, r, 8, 19, kind == "tt")
        r += 1
    return rows, r


ISL = [("Revenue", "P&L", R["rev"], M["rev"], None), ("Cost of revenue", "P&L", R["cogs"], M["cogs"], None),
       ("Gross profit", "P&L", R["gp"], M["gp"], "t"), ("Gross margin", "P&L", R["gm"], ("Gross profit", "Revenue"), "%"),
       ("Operating expenses", "P&L", R["opex"], M["opex"], None), ("EBITDA", "P&L", R["ebitda"], M["ebitda"], "t"),
       ("EBITDA margin", "P&L", R["ebitdam"], ("EBITDA", "Revenue"), "%"),
       ("Depreciation", "P&L", R["dep"], M["dep"], None), ("EBIT", "P&L", R["ebit"], M["ebit"], "t"),
       ("Interest", "P&L", R["int"], M["int"], None), ("Pre-tax income", "P&L", R["pbt"], M["pbt"], None),
       ("Income tax", "P&L", R["tax"], M["tax"], None), ("Net income", "P&L", R["ni"], M["ni"], "tt"),
       ("Net margin", "P&L", R["nm"], ("Net income", "Revenue"), "%")]
is_rows, nxt = block(5, "Income statement ($\'000) — 5 years", '="Income statement ($\'000) — Year "&$R$2&", by month"', ISL)
# Monthly depreciation row is stored negative as a credit to fixed assets; the P&L shows it as an expense too
CFL = [("Operating cash flow", "Cash Flow", R["cfo"], M["cfo"], "t"), ("Capital spending", "Cash Flow", R["capex"], M["capex"], None),
       ("Equity raised", "Cash Flow", R["eq"], M["eq"], None), ("Loan drawdown", "Cash Flow", R["draw"], M["draw"], None),
       ("Loan repayment", "Cash Flow", R["repay"], M["repay"], None), ("Financing cash flow", "Cash Flow", R["cff"], M["cff"], "t"),
       ("Net change in cash", "Cash Flow", R["net"], M["net"], "t"), ("Closing cash", "Cash Flow", R["close"], M["close"], "tt")]
IS_TOP = 5
CF_TOP = max(nxt + 1, IS_TOP + 17)
cf_rows, nxt = block(CF_TOP, "Cash flow ($\'000) — 5 years", '="Cash flow ($\'000) — Year "&$R$2&", by month"', CFL)
BSL = [("Cash", "Balance Sheet", R["cash"], M["cash"], None), ("Accounts receivable", "Balance Sheet", R["ar"], M["ar"], None),
       ("Inventory", "Balance Sheet", R["inv"], M["inv"], None), ("Net fixed assets", "Balance Sheet", R["fa"], M["fa"], None),
       ("Total assets", "Balance Sheet", R["ta"], M["ta"], "t"), ("Accounts payable", "Balance Sheet", R["ap"], M["ap"], None),
       ("Deferred revenue", "Balance Sheet", R["dr"], M["dr"], None), ("Loan", "Balance Sheet", R["loan"], M["loan"], None),
       ("Total liabilities", "Balance Sheet", R["tl"], M["tl"], "t"), ("Paid-in capital", "Balance Sheet", R["pic"], M["pic"], None),
       ("Retained earnings", "Balance Sheet", R["re"], M["re"], None), ("Total equity", "Balance Sheet", R["te"], M["te"], "t"),
       ("Total liabilities & equity", "Balance Sheet", R["tle"], M["tle"], "tt")]
BS_TOP = max(nxt + 1, CF_TOP + 17)
bs_rows, nxt = block(BS_TOP, "Balance sheet at year end ($\'000)", '="Balance sheet at month end ($\'000) — Year "&$R$2', BSL)
assert is_rows["Revenue"] == 7, is_rows  # Checks!B17 points here
summ.freeze_panes = "B5"
from openpyxl.chart import Series  # noqa: E402

summ.column_dimensions["T"].width = 2
for c in range(21, 37):
    summ.column_dimensions[L(c)].width = 9
MCATS = lambda top: Reference(summ, min_col=8, max_col=19, min_row=top + 1, max_row=top + 1)  # noqa: E731


def mseries(row, name):
    return Series(Reference(summ, min_col=8, max_col=19, min_row=row, max_row=row), title=name)


def mchart(kind, rows_names, colors, title, top, line_rows=(), line_colors=(), secondary=False, stacked=False):
    ch = BarChart()
    ch.type, ch.gapWidth = "col", 40
    if stacked:
        ch.grouping, ch.overlap = "stacked", 100
    for row, nm in rows_names:
        ch.series.append(mseries(row, nm))
    style_chart(ch, title, 14.2, 8.3)
    color_series(ch, colors)
    ch.set_categories(MCATS(top))
    ch.y_axis.number_format = '$#,##0,"K"'
    if line_rows:
        ln = LineChart()
        for row, nm in line_rows:
            ln.series.append(mseries(row, nm))
        color_series(ln, line_colors, line=True)
        if secondary:
            ln.y_axis.axId = 200
            ln.y_axis.crosses = "max"
            ln.y_axis.delete = False
            ln.y_axis.number_format = '$#,##0,"K"'
            ln.y_axis.majorGridlines = None
            ln.y_axis.txPr = _rich(800)
        ch += ln
    summ.add_chart(ch, f"U{top}")


mchart("bar", [(is_rows["Revenue"], "Revenue")], [PINE], "Income statement by month", IS_TOP,
       [(is_rows["EBITDA"], "EBITDA"), (is_rows["Net income"], "Net income")], [AMBER, INK])
mchart("bar", [(cf_rows["Operating cash flow"], "Operating cash flow"), (cf_rows["Capital spending"], "Capital spending"),
               (cf_rows["Financing cash flow"], "Financing cash flow")], [PINE, GREY, AMBER], "Cash flow by month", CF_TOP,
       [(cf_rows["Closing cash"], "Closing cash (right axis)")], [INK], secondary=True)
mchart("bar", [(bs_rows["Cash"], "Cash"), (bs_rows["Accounts receivable"], "Receivables"),
               (bs_rows["Net fixed assets"], "Fixed assets")], [PINE, SAGE, GREY], "Assets and equity at month end", BS_TOP,
       [(bs_rows["Total equity"], "Total equity")], [INK], stacked=True)

# ---- Scenarios
title_block(scen, "Scenario analysis", MODEL_NAME, "I")
scen.column_dimensions["A"].width = 40
for x in "BCDEF":
    scen.column_dimensions[x].width = 13
scen.column_dimensions["G"].width = 2
put(scen, "A3", "Low / Base / High columns: values the model engine computed for each scenario when the file was built "
    "(prototype snapshot — the production version keeps them live). Active = live, follows Dashboard!B4.",
    color=MUTED, italic=True, size=8)
band(scen, 5, 1, 6, "Key drivers by scenario (from Inputs)")
for i, h in enumerate(["Driver", "Low", "Base", "High", "Active", "Unit"]):
    scen.cell(6, 1 + i, h)
header_row(scen, 6, 1, 6)
drivers = ["Average MRR per new customer", "Customer churn per month", "Organic / referral new customers",
           "Paid customer acquisition cost", "Price increase per year", "Expansion MRR", "Hosting & payment fees",
           "Discount rate (WACC)", "Exit multiple"]
r = 7
for dname in drivers:
    ir = find(inp, dname)
    unit = inp.cell(ir, 6).value
    fmt = PCT if unit == "%" else (MULT if unit == "x" else '#,##0.##;(#,##0.##);"-"')
    put(scen, f"A{r}", f"=Inputs!A{ir}", color=GREEN)
    for x, src in zip("BCDE", "BCDE"):
        put(scen, f"{x}{r}", f"=Inputs!{src}{ir}", fmt, color=GREEN, align="right", bold=x == "E",
            fill=CALC_FILL if x == "E" else None)
    put(scen, f"F{r}", f"=Inputs!F{ir}", color=MUTED, italic=True)
    r += 1
r += 1
band(scen, r, 1, 6, "Outputs by scenario")
r += 1
for i, h in enumerate(["", "Low", "Base", "High", "Active", ""]):
    scen.cell(r, 1 + i, h)
header_row(scen, r, 1, 6)
r += 1
outs = [  # (label, key in snapshot, live formula, fmt)
    ("Revenue — 5-year total", "rev_total", f"=SUM('P&L'!B{R['rev']}:F{R['rev']})", MONEY_K),
    ("Revenue — year 5", "rev_y5", f"='P&L'!F{R['rev']}", MONEY_K),
    ("EBITDA — 5-year total", "ebitda_total", f"=SUM('P&L'!B{R['ebitda']}:F{R['ebitda']})", MONEY_K),
    ("EBITDA margin — year 5", "ebitdam_y5", f"='P&L'!F{R['ebitdam']}", PCT),
    ("Net income — 5-year total", "ni_total", f"=SUM('P&L'!B{R['ni']}:F{R['ni']})", MONEY_K),
    ("Year-end cash — year 5", "cash_y5", f"='Balance Sheet'!F{R['cash']}", MONEY_K),
    ("Lowest cash balance", "min_cash", f"=MIN(Monthly!$C${MCLOSE}:$BJ${MCLOSE})", MONEY_K),
    ("Funding required (incl. buffer)", "funding", "='Break-even'!B12", MONEY_K),
    ("Enterprise value (DCF, average)", "ev", "=Valuation!B30", MONEY_K),
]
for lab, key, live, fmt in outs:
    scen.cell(r, 1, lab).font = F()
    for j, x in enumerate("BCD", start=1):
        v = SNAP[str(j)][key] if SNAP else 0
        put(scen, f"{x}{r}", v, fmt, color=INK, align="right")
    put(scen, f"E{r}", live, fmt, color=GREEN, bold=True, align="right", fill=CALC_FILL)
    r += 1
r += 1
series_rows = {}
for metric, key in (("Revenue", "rev"), ("EBITDA", "ebitda"), ("Net income", "ni"), ("Year-end cash", "cash")):
    band(scen, r, 1, 6, f"{metric} by year and scenario ($\'000)")
    r += 1
    scen.cell(r, 1, "")
    for x in YC:
        scen[f"{x}{r}"] = f"='P&L'!{x}4"
    header_row(scen, r, 1, 6)
    hdr = r
    r += 1
    rows_ = []
    for j, name in ((1, "Low"), (2, "Base"), (3, "High")):
        scen.cell(r, 1, f"{metric} — {name}").font = F()
        for i, x in enumerate(YC):
            put(scen, f"{x}{r}", SNAP[str(j)][key][i] if SNAP else 0, MONEY_K, color=INK, align="right")
        rows_.append(r)
        r += 1
    series_rows[metric] = (hdr, rows_)
    r += 1
for c in range(8, 24):
    scen.column_dimensions[L(c)].width = 9
for k, (metric, (hdr, rows_)) in enumerate(series_rows.items()):
    ch = line(scen, rows_, year_cats(scen, hdr), f"{metric} by scenario", [GREY, PINE, AMBER])
    ch.width, ch.height = 14.2, 8.3
    scen.add_chart(ch, f"{'HP'[k % 2]}{5 + 17 * (k // 2)}")

# ---- Sources & Uses
title_block(su, "Sources and uses of funds", MODEL_NAME, "I")
su.column_dimensions["A"].width = 44
for x, w in zip("BCDEFG", (14, 9, 3, 30, 14, 9)):
    su.column_dimensions[x].width = w
band(su, 5, 1, 7, "Funding structure ($\'000) — raised at the start of the plan")
for i, h in enumerate(["", "Amount", "Share"]):
    su.cell(6, 1 + i, h)
header_row(su, 6, 1, 3)
eq_r, ln_r = find(inp, "Equity raised"), find(inp, "Loan drawn")
put(su, "A7", "Equity")
put(su, "B7", f"=Inputs!E{eq_r}", MONEY_K, GREEN, align="right")
put(su, "A8", "Debt (loan)")
put(su, "B8", f"=Inputs!E{ln_r}", MONEY_K, GREEN, align="right")
put(su, "A9", "Total funding", bold=True)
put(su, "B9", "=B7+B8", MONEY_K, bold=True, align="right")
for rr_ in (7, 8, 9):
    put(su, f"C{rr_}", f"=IF($B$9=0,0,B{rr_}/$B$9)", PCT, align="right", bold=rr_ == 9)
total(su, 9, 1, 3)
put(su, "A10", "Gearing (debt ÷ equity)")
put(su, "B10", "=IF(B7=0,0,B8/B7)", MULT, align="right")
put(su, "A11", "Funding required by the plan (Break-even sheet)")
put(su, "B11", "='Break-even'!B12", MONEY_K, GREEN, align="right")
put(su, "A12", "Surplus / (shortfall)", bold=True)
put(su, "B12", "='Break-even'!B17", MONEY_K, GREEN, bold=True, align="right")
total(su, 12, 1, 3, double=True)

band(su, 14, 1, 7, '="Sources and uses — first "&$B$15&" months ($\'000)"')
put(su, "A15", "Period covered (months from the start)", color=INK, bold=True)
pm = put(su, "B15", 12, "0", color=BLUE, bold=True, fill=INPUT_FILL, align="center")
pm.border = Border(left=thin_g, right=thin_g, top=thin_g, bottom=thin_g)
dv3 = DataValidation(type="whole", operator="between", formula1="1", formula2="60", showInputMessage=True,
                     promptTitle="Months", prompt="1 to 60")
su.add_data_validation(dv3)
dv3.add("B15")
for i, h in enumerate(["Sources", "Amount", "Share", "", "Uses", "Amount", "Share"]):
    su.cell(16, 1 + i, h)
header_row(su, 16, 1, 3)
header_row(su, 16, 5, 7)


def cum(row, sign=""):
    return f"{sign}SUMPRODUCT(--(Monthly!$C$4:$BJ$4<=$B$15),Monthly!$C${row}:$BJ${row})"


src = [("Equity raised", "=" + cum(M["eq"])), ("Loan drawdowns", "=" + cum(M["draw"])),
       ("Cash generated by operations", f"=MAX(0,{cum(M['cfo'])})")]
use = [("Cash used by operations", f"=MAX(0,-{cum(M['cfo'])})"), ("Capital spending", "=" + cum(M["capex"], "-")),
       ("Loan repayments", "=" + cum(M["repay"], "-")), ("Cash at the end of the period",
                                                          f"=INDEX(Monthly!$C${MCLOSE}:$BJ${MCLOSE},$B$15)")]
for i in range(4):
    r_ = 17 + i
    if i < len(src):
        put(su, f"A{r_}", src[i][0])
        put(su, f"B{r_}", src[i][1], MONEY_K, align="right")
        put(su, f"C{r_}", f"=IF($B$21=0,0,B{r_}/$B$21)", PCT, align="right")
    put(su, f"E{r_}", use[i][0])
    put(su, f"F{r_}", use[i][1], MONEY_K, align="right")
    put(su, f"G{r_}", f"=IF($F$21=0,0,F{r_}/$F$21)", PCT, align="right")
put(su, "A21", "Total sources", bold=True)
put(su, "B21", "=SUM(B17:B20)", MONEY_K, bold=True, align="right")
put(su, "C21", "=IF(B21=0,0,1)", PCT, bold=True, align="right")
put(su, "E21", "Total uses", bold=True)
put(su, "F21", "=SUM(F17:F20)", MONEY_K, bold=True, align="right")
put(su, "G21", "=IF(F21=0,0,1)", PCT, bold=True, align="right")
total(su, 21, 1, 3, True)
total(su, 21, 5, 7, True)
put(su, "A22", "Sources − uses (must be 0; opening cash is 0)", color=MUTED, italic=True, size=8)
put(su, "B22", "=B21-F21", MONEY_K, color=MUTED, italic=True, align="right")
d = DoughnutChart()
d.add_data(Reference(su, min_col=2, min_row=7, max_row=8))
d.set_categories(Reference(su, min_col=1, min_row=7, max_row=8))
style_chart(d, "Funding structure", 9.5, 6.5)
d.holeSize = 55
from openpyxl.chart.series import DataPoint  # noqa: E402

for idx, col in enumerate((PINE, AMBER)):
    pt = DataPoint(idx=idx)
    pt.graphicalProperties = GraphicalProperties(solidFill=col)
    d.series[0].dPt.append(pt)
labels(d)
d.dataLabels.showVal, d.dataLabels.showPercent = False, True
su.add_chart(d, "I4")
ub = BarChart()
ub.type, ub.gapWidth = "bar", 50
ub.add_data(Reference(su, min_col=6, min_row=17, max_row=20))
ub.set_categories(Reference(su, min_col=5, min_row=17, max_row=20))
style_chart(ub, "Uses of funds", 13, 6.5, legend=False)
color_series(ub, [PINE])
labels(ub, '$#,##0.0,,"M"', "outEnd")
ub.y_axis.number_format = '$#,##0.0,,"M"'
su.add_chart(ub, "A25")

# ---- Cover with contents
cover.column_dimensions["A"].width = 3
cover.column_dimensions["B"].width = 5
cover.column_dimensions["C"].width = 26
cover.column_dimensions["D"].width = 70
put(cover, "B2", MODEL_NAME, color=INK, bold=True, size=20)
put(cover, "B3", "5-year financial model · monthly detail · Low / Base / High scenarios · US dollars", color=MUTED, size=10)
put(cover, "B5", "Active scenario", color=INK, bold=True)
put(cover, "D5", '=Dashboard!C4&"  (change on the Dashboard, cell B4)"', color=PINE, bold=True)
put(cover, "B6", "Model checks", color=INK, bold=True)
put(cover, "D6", "=Checks!B22", bold=True)
for rule in (('ISNUMBER(SEARCH("FAIL",$D$6))', "F6D5D2", RED), ('ISNUMBER(SEARCH("WARN",$D$6))', "FBEFCF", "8A6100"),
             ('$D$6="PASS"', "DCEFE8", PINE)):
    cover.conditional_formatting.add("D6", FormulaRule(formula=[rule[0]], fill=PatternFill("solid", fgColor=rule[1]),
                                                       font=F(rule[2], True)))
put(cover, "B7", "Prepared", color=INK, bold=True)
put(cover, "D7", "20 October 2026", color=BLACK)
band(cover, 9, 2, 4, "Contents")
contents = [
    ("Presentation", None), ("Dashboard", "Scenario switch, key numbers, core financials, 4 charts"),
    ("Summary", "Income statement, cash flow, balance sheet — 5 years and any year by month"),
    ("Scenarios", "Low / Base / High side by side: drivers, outputs, charts"),
    ("Break-even", "Startup costs, funding need, break-even timing and revenue"),
    ("Valuation", "Free cash flow, DCF (perpetual growth and exit multiple), WACC × growth sensitivity"),
    ("Sources & Uses", "Funding structure, sources and uses of cash for the first months"),
    ("KPIs", "Industry metrics, financial ratios, DuPont analysis"),
    ("Inputs", None), ("Inputs", "Every assumption, Low / Base / High, with units and comments"),
    ("Statements", None), ("P&L", "Annual profit & loss"), ("Cash Flow", "Annual cash flow statement"),
    ("Balance Sheet", "Balance sheet at year end"),
    ("Calculations", None), ("Monthly", "Month-by-month engine of the model"), ("Headcount", "Team and payroll by month"),
    ("Control", None), ("Checks", "Live integrity checks; overall verdict"),
]
r = 10
n = 0
for name, desc in contents:
    if desc is None:
        put(cover, f"C{r}", "Inputs" if name == "Inputs" else name, color=PINE, bold=True, size=8)
        cover[f"C{r}"].value = name.upper()
        r += 1
        continue
    n += 1
    put(cover, f"B{r}", n, "0", color=MUTED, align="right")
    c = put(cover, f"C{r}", f'=HYPERLINK("#\'{name}\'!A1","{name}")', color=PINE, bold=True)
    c.font = F(PINE, True, underline="single")
    put(cover, f"D{r}", desc, color=BLACK)
    for col in "BCD":
        cover[f"{col}{r}"].border = Border(bottom=thin_g)
    r += 1
r += 1
put(cover, f"B{r}", "How to read this file", color=INK, bold=True)
legend = [(INPUT_FILL, BLUE, "1,000", "Input you can change (yellow cell, blue figure) — on Inputs, plus the two view "
           "switches"),
          (None, BLACK, "1,000", "Formula — calculated, do not overwrite"),
          (None, GREEN, "1,000", "Link to another sheet"), (CALC_FILL, BLACK, "1,000", "Active value the model uses")]
for fill, col, sample, text in legend:
    r += 1
    c = put(cover, f"C{r}", sample, color=col, align="center", fill=fill)
    c.border = Border(left=thin_g, right=thin_g, top=thin_g, bottom=thin_g)
    put(cover, f"D{r}", text)
r += 2
put(cover, f"B{r}", "Prototype of workbook standard v1 (internal review). Numbers come from the production engine; "
    "the Scenarios sheet's Low / Base / High columns are a build-time snapshot.", color=MUTED, italic=True, size=8)

# presentation sheets read as a report: cross-sheet links in ink (colour coding stays on Inputs and calculations)
for ws in (dash, summ, scen, su, kpi):
    for row in ws.iter_rows():
        for c in row:
            if c.font.color is not None and c.font.color.type == "rgb" and c.font.color.rgb[-6:] == GREEN:
                f = c.font
                c.font = F(INK, f.bold, f.sz or 9, f.italic)

# ---------------------------------------------------------------- 5. order, tabs, page setup
order = ["Cover", "Dashboard", "Summary", "Scenarios", "Break-even", "Valuation", "Sources & Uses", "KPIs", "Inputs",
         "P&L", "Cash Flow", "Balance Sheet", "Monthly", "Headcount", "Checks"]
wb._sheets = [wb[n] for n in order]
TAB = {"Cover": PINE, "Dashboard": PINE, "Summary": PINE, "Scenarios": PINE, "Break-even": PINE, "Valuation": PINE,
       "Sources & Uses": PINE, "KPIs": PINE, "Inputs": "E0B43C", "P&L": INK, "Cash Flow": INK, "Balance Sheet": INK,
       "Monthly": GREY, "Headcount": GREY, "Checks": RED}
for n in order:
    setup(wb[n], TAB[n], landscape=n not in ("Cover",), zoom=90 if n in ("Monthly", "Headcount") else 100)
wb.active = 0
for ws in wb.worksheets:
    ws.sheet_view.tabSelected = ws.title == "Cover"
wb.properties.creator = ""
wb.properties.title = MODEL_NAME
wb.save(OUT)
print("saved", OUT, "rows", R["rev"], M["rev"], "is_rev_row", is_rows["Revenue"])
