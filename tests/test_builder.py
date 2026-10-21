"""Workbook structure and Excel rules — no LibreOffice needed."""

import itertools
import re

import pytest
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

from engine.builder import FIRST_COL, plan
from engine.spec import Line
from engine.templates import get_template

FORBIDDEN = re.compile(r"\b(XLOOKUP|XMATCH|FILTER|SORT|UNIQUE|SEQUENCE|LET|LAMBDA)\s*\(", re.I)
COMBOS = list(itertools.product(["light", "full"], ["monthly", "annual"], [1, 3, 5]))


def variants(brief):
    for tier, g, y in COMBOS:
        yield (tier, g, y), brief.with_options(tier=tier, granularity=g, horizon_years=y)


def test_sheets_per_tier(build, cafe_brief):
    # docs/WORKBOOK_STANDARD.md §1 — the order is copied verbatim
    full = load_workbook(build(cafe_brief.with_options(tier="full"), "f.xlsx"))
    assert full.sheetnames == [
        "Cover",
        "Dashboard",
        "Summary",
        "Break-even",
        "Valuation",
        "KPIs",
        "Inputs",
        "P&L",
        "Cash Flow",
        "Balance Sheet",
        "Monthly",
        "Headcount",
        "Checks",
    ]
    annual = load_workbook(build(cafe_brief.with_options(granularity="annual"), "a.xlsx"))
    assert annual.sheetnames[10] == "Annual"
    light = load_workbook(build(cafe_brief.with_options(tier="light"), "l.xlsx"))
    assert light.sheetnames == ["Cover", "Dashboard", "Break-even", "Inputs", "P&L", "Checks"]
    assert light["Dashboard"]["B4"].value == 2 and light["Inputs"]["B3"].value is None
    assert full["Dashboard"]["B4"].value == 2


@pytest.mark.parametrize("tier,g,years", COMBOS)
def test_excel_rules(build, any_brief, tier, g, years):
    brief = any_brief.with_options(tier=tier, granularity=g, horizon_years=years)
    wb = load_workbook(build(brief))
    switches, inputs, formulas = [], [], 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                rgb = c.fill.fgColor.rgb if c.fill.fill_type == "solid" else ""
                assert not rgb.endswith("FFFF00"), f"old bright yellow at {ws.title}!{c.coordinate}"
                if rgb.endswith("FFE08A"):
                    switches.append(f"{ws.title}!{c.coordinate}")
                if rgb.endswith("FFF2CC") and ws.title != "Cover":  # the Cover legend shows a sample input
                    inputs.append((ws.title, c))
                if c.value is None:
                    continue
                assert c.font.name == "Arial", f"{ws.title}!{c.coordinate}"
                if isinstance(c.value, str) and c.value.startswith("="):
                    formulas += 1
                    assert not FORBIDDEN.search(c.value), f"{ws.title}!{c.coordinate}: {c.value}"
                    assert "{" not in c.value, f"unrendered token in {ws.title}!{c.coordinate}: {c.value}"
                    color = c.font.color.rgb if c.font.color else ""
                    assert not color.endswith("0000FF"), f"formula in blue at {ws.title}!{c.coordinate}"
    # the scenario selector, both tiers (ADR-013), and the Summary's detailed year (Full, monthly: E28)
    assert switches == ["Dashboard!B4"] + (["Summary!R2"] if tier == "full" and g == "monthly" else [])
    for sheet, c in inputs:  # input fill only on typed numbers on Inputs (Low / Base / High) ...
        if sheet == "KPIs":  # ... and the blank Target column of the KPIs sheet (E31, standard §5)
            assert c.value is None and c.column == 2 + brief.horizon_years, f"{sheet}!{c.coordinate}"
            continue
        assert sheet == "Inputs" and c.column_letter in "BCD", f"{sheet}!{c.coordinate}"
        assert not (isinstance(c.value, str) and c.value.startswith("=")), f"formula on input fill {c.coordinate}"
    assert formulas > 50
    inp = wb["Inputs"]
    pl = plan(brief, get_template(brief.template))
    for key, r in pl.input_row.items():
        for col in "BCD":
            assert inp[f"{col}{r}"].font.color.rgb.endswith("0000FF"), key
            assert inp[f"{col}{r}"].fill.fgColor.rgb.endswith("FFF2CC"), key
        assert inp[f"E{r}"].value.startswith("=CHOOSE(")


def _shape(formula: str, col: int) -> str:
    """Replace this/previous column letters so equal-shaped formulas compare equal."""
    cur, prev = get_column_letter(col), get_column_letter(col - 1)
    f = re.sub(rf"(?<![A-Z$]){cur}(?=\$?\d)", "<C>", formula)
    return re.sub(rf"(?<![A-Z$]){prev}(?=\$?\d)", "<P>", f)


@pytest.mark.parametrize("g", ["monthly", "annual"])
def test_same_formula_across_periods(build, any_brief, g):
    brief = any_brief.with_options(granularity=g, horizon_years=5)
    wb = load_workbook(build(brief))
    pl = plan(brief, get_template(brief.template))
    n = pl.t.periods
    for key, (sheet, row) in pl.line_at.items():
        ws = wb[sheet]
        shapes = {_shape(ws.cell(row=row, column=FIRST_COL + p - 1).value, FIRST_COL + p - 1) for p in range(2, n + 1)}
        assert len(shapes) == 1, (key, shapes)


def test_denominators_guarded(any_brief):
    """Every division is by a constant, a timing token, or MAX(1, ...) — never a bare input."""
    pl = plan(any_brief, get_template(any_brief.template))
    allowed = ("MAX(1,", "{mpp}", "{ppy}", "{dpp}")
    for ln in pl.lines.values():
        for text in filter(None, (ln.formula, ln.first)):
            for i, ch in enumerate(text):
                if ch == "/":
                    rest = text[i + 1 :]
                    assert rest[:1].isdigit() or rest.startswith(allowed), (ln.key, text)


def test_render_errors(cafe_brief):
    pl = plan(cafe_brief, get_template("cafe"))
    sheet = pl.calc_sheet
    with pytest.raises(KeyError, match="unknown line"):
        pl.render(Line("x", "x", "={nope}", "top"), 2, sheet)
    with pytest.raises(ValueError, match="before period 1"):
        pl.render(Line("x", "x", "={rev[-1]}", "top"), 1, sheet)
    assert pl.render(Line("x", "x", "={rev[-1]}*{mpp}", "top"), 2, sheet).endswith("*1")


def test_payroll_links_green_in_full(build, cafe_brief):
    wb = load_workbook(build(cafe_brief))
    pl = plan(cafe_brief, get_template("cafe"))
    sheet, row = pl.line_at["payroll"]
    c = wb[sheet].cell(row=row, column=FIRST_COL)
    assert c.value.startswith("=Headcount!")
    assert c.font.color.rgb.endswith("008000")


def test_saas_sheets_and_kpis(build, saas_brief):
    wb = load_workbook(build(saas_brief))
    dash = wb["Dashboard"]
    labels = [dash.cell(row=r, column=1).value for r in range(1, dash.max_row + 1)]
    assert "SaaS metrics" in labels and "ARR (year-end MRR × 12)" in labels and "LTV ÷ CAC" in labels
    bs = [c.value for c in wb["Balance Sheet"]["A"]]
    assert "Deferred revenue (annual plans, ~6 months unearned)" in bs
    light = load_workbook(build(saas_brief.with_options(tier="light"), "l.xlsx"))
    assert "SaaS metrics" in [c.value for c in light["P&L"]["A"]]
