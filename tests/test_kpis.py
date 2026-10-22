"""KPIs & ratios sheet (E31, docs/WORKBOOK_STANDARD.md §1, §3, §5): ratios, DuPont, the moved KPI table, Target."""

import pytest
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter as L

from engine import kpis as K
from engine.builder import manifest_for, plan
from engine.challenger import challenge
from engine.recalc import recalc
from engine.templates import TEMPLATES, get_template

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")
lo = pytest.mark.libreoffice


def _brief(key="saas", **kw):
    tpl = TEMPLATES[key]
    return tpl.default_brief(tpl.sample_stage).with_options(**kw)


def _labels(ws):
    return {r: ws.cell(row=r, column=1).value for r in range(1, ws.max_row + 1) if ws.cell(row=r, column=1).value}


def _values(path, sheet="KPIs"):
    return load_workbook(path, data_only=True)[sheet]


# --------------------------------------------------------------------------- layout
@pytest.fixture
def saas(build):
    brief = _brief("saas", tier="full", horizon_years=5)
    return load_workbook(build(brief)), plan(brief, get_template("saas"))


def test_sheet_position_and_light_has_none(build):
    full = plan(_brief("saas", tier="full"), get_template("saas")).sheets
    # standard §1: … Valuation, Sources & Uses, KPIs, [industry sheets], Inputs …
    assert full[full.index("Sources & Uses") + 1] == "KPIs" and full[full.index("KPIs") + 1] == "Inputs"
    assert "KPIs" not in plan(_brief("saas", tier="light"), get_template("saas")).sheets
    re_full = plan(_brief("real_estate", tier="full"), get_template("real_estate")).sheets
    assert re_full.index("Returns") == re_full.index("KPIs") + 1  # industry sheets come after KPIs (standard §1)


def test_tables_titles_and_target_column(saas):
    wb, pl = saas
    ws, lay = wb["KPIs"], pl.kpis
    lab = _labels(ws)
    assert ws["A1"].value == "KPIs & ratios" and ws["I1"].value == '=HYPERLINK("#\'Cover\'!A1","◂ Contents")'
    assert lab[4] == "Financial ratios" and lab[lay.dp_band].startswith("DuPont analysis")
    assert [lab[r] for r in lay.ratios.values()] == [
        "Revenue growth",
        "Gross margin",
        "EBITDA margin",
        "Net margin",
        "Payroll, % of revenue",
        "Marketing, % of revenue",
        "Operating expenses, % of revenue",
        "Current ratio (current assets ÷ current liabilities)",
        "Debt ÷ equity (loan ÷ total equity)",
        "Return on assets (net income ÷ year-end assets)",
        "Return on equity (net income ÷ year-end equity)",
    ]
    kpi = pl.blocks["kpi"]
    assert kpi.sheet == "KPIs" and kpi.start_row == K.block_start(pl.template)
    assert lab[kpi.start_row - 1] == "SaaS metrics ($'000; per-unit rows in $)"
    for row in pl.template.kpi_rows(pl.t):  # the whole KPI table moved here
        assert lab[kpi.placed[row.key]] == K.row_label(pl.template, row)
    assert ws.sheet_properties.tabColor.rgb[-6:] == "0F6E56"


def test_target_column_is_blank_yellow_input_beside_ratios_and_kpi_rows(saas):
    wb, pl = saas
    ws, lay = wb["KPIs"], pl.kpis
    assert lay.target_col == 7 and ws.cell(row=K.HDR, column=7).value == "Target"
    rows = [*lay.ratios.values(), *pl.blocks["kpi"].placed.values()]
    for r in rows:
        c = ws.cell(row=r, column=7)
        assert c.value is None  # left blank: never an invented benchmark
        assert c.fill.fgColor.rgb[-6:] == "FFF2CC" and c.font.color.rgb[-6:] == "0000FF"
    assert ws.cell(row=pl.blocks["kpi"].year_row + 1, column=7).value == "Target"
    yellow = {
        c.coordinate
        for row in ws.iter_rows()
        for c in row
        if c.fill.fill_type == "solid" and c.fill.fgColor.rgb[-6:] == "FFF2CC"
    }
    assert yellow == {f"G{r}" for r in rows}  # nothing else on the sheet is an input


def test_four_charts_two_by_two_right_of_the_tables(saas):
    wb, pl = saas
    ws = wb["KPIs"]
    anchors = [(c.anchor._from.col, c.anchor._from.row) for c in ws._charts]
    assert anchors == [(8, 3), (16, 3), (8, 20), (16, 20)]  # I4 Q4 I21 Q21
    titles = [c.title.tx.rich.p[0].r[0].t for c in ws._charts]
    assert titles[:2] == ["Margins", "Return on assets and return on equity"]
    assert titles[2:] == [s.title for s in pl.template.kpi_charts(pl.t)]


def test_target_column_moves_with_the_horizon(build):
    brief = _brief("saas", tier="full", horizon_years=1)
    ws = load_workbook(build(brief))["KPIs"]
    assert ws["C5"].value == "Target" and ws["B5"].number_format == '"Year "0'
    assert [(c.anchor._from.col, c.anchor._from.row) for c in ws._charts][:2] == [(4, 3), (12, 3)]  # E4, M4


@pytest.mark.parametrize("key", sorted(TEMPLATES))
def test_every_template_has_two_resolving_kpi_charts_and_a_kpi_table(build, key):
    brief = _brief(key, tier="full")
    tpl = get_template(key)
    pl = plan(brief, tpl)
    charts = tpl.kpi_charts(pl.t)
    assert len(charts) == 2 and "kpi" in pl.blocks
    rows = {r.key for r in tpl.kpi_rows(pl.t)}
    for spec in charts:
        assert set(spec.bars + spec.lines) <= rows, (key, spec)
    ws = load_workbook(build(brief))["KPIs"]
    assert len(ws._charts) == 4
    assert "Costs, % of revenue" not in [c.title.tx.rich.p[0].r[0].t for c in ws._charts]  # all 7 override the default


def test_default_charts_use_ratios_and_drop_unknown_keys():
    from engine.spec import Timing
    from engine.templates.base import Template

    charts = Template.kpi_charts(get_template("saas"), Timing("monthly", 3))
    assert [c.title for c in charts] == ["Costs, % of revenue", "Liquidity and leverage"]
    assert all(k.startswith("r:") for c in charts for k in c.bars + c.lines)


def test_dashboard_no_longer_holds_the_kpi_table(build):
    brief = _brief("saas", tier="full")
    ws = load_workbook(build(brief))["Dashboard"]
    labels = {str(c.value) for row in ws.iter_rows(min_col=1, max_col=1) for c in row if c.value}
    assert "Runway at year-end burn (months; - = not burning)" not in labels  # a KPI-table-only row
    assert ws.max_row < 47
    assert all("[>=1000000]" not in c.number_format for row in ws.iter_rows() for c in row)  # DASH_USD_K is gone


def test_marketing_ratio_is_left_out_where_there_is_no_marketing_line():
    assert "mkt_pct" not in K.ratio_keys(get_template("real_estate"))
    assert "mkt_pct" in K.ratio_keys(get_template("retail")) and get_template("retail").marketing_key == "ads"


# --------------------------------------------------------------------------- formulas
def test_ratio_formulas_link_to_the_statements_and_guard_denominators(saas):
    wb, pl = saas
    ws, lay = wb["KPIs"], pl.kpis
    r0 = pl.stmt_cell("pl", "rev", 0, "KPIs")  # year 1 reads the label column: same formula in every year
    assert ws["B6"].value == f'=IF(N({r0})<=0,"n/a",{pl.stmt_cell("pl", "rev", 1, "KPIs")}/{r0}-1)'
    rev1, rev2 = pl.stmt_cell("pl", "rev", 1, "KPIs"), pl.stmt_cell("pl", "rev", 2, "KPIs")
    assert ws["C6"].value == f'=IF(N({rev1})<=0,"n/a",{rev2}/{rev1}-1)' and rev1.startswith("'P&L'!")
    f = ws.cell(row=lay.ratios["roe"], column=3).value
    assert f.startswith("=IF('Balance Sheet'!C") and '<=0,"n/a"' in f and "'P&L'!C" in f
    dp = ws.cell(row=lay.dupont["dp_roe"], column=3).value
    assert dp.startswith("=IF(AND(ISNUMBER(C") and dp.endswith('"n/a")')
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.startswith("="):
                for banned in ("XLOOKUP", "FILTER(", "LET(", "LAMBDA", "SEQUENCE", "UNIQUE(", "SORT("):
                    assert banned not in c.value


# --------------------------------------------------------------------------- the plain-Python twin
def _ann(**series):
    base = {
        "rev": {1: 100.0, 2: 150.0},
        "gp": {1: 60.0, 2: 90.0},
        "ebitda": {1: 10.0, 2: 30.0},
        "ni": {1: 5.0, 2: 15.0},
        "opex_total": {1: -50.0, 2: -60.0},
        "payroll_total": {1: -20.0, 2: -25.0},
        "opex_mkt": {1: -5.0, 2: -6.0},
        "paid_in": {1: 100.0, 2: 100.0},
        "retained": {1: 5.0, 2: 20.0},
        "loan_close": {1: 50.0, 2: 40.0},
        "total_assets": {1: 200.0, 2: 230.0},
        "total_le": {1: 200.0, 2: 230.0},
        "cash_close": {1: 80.0, 2: 90.0},
        "ar": {1: 20.0, 2: 30.0},
        "inv": {1: 0.0, 2: 0.0},
    }
    base.update(series)
    return base


def test_reference_ratios_and_dupont_identity():
    from engine.spec import Timing

    out = K.reference(get_template("saas"), _ann(), Timing("annual", 2))
    assert out["kpi_r_growth"] == {1: "n/a", 2: 0.5}
    assert out["kpi_r_gm"][1] == pytest.approx(0.6) and out["kpi_r_payroll_pct"][2] == pytest.approx(25 / 150)
    assert out["kpi_r_mkt_pct"][1] == pytest.approx(0.05)
    assert out["kpi_r_current"][1] == pytest.approx(
        100 / (200 - 105 - 50)
    )  # current liabilities = TL&E - equity - loan
    assert out["kpi_r_debt_eq"][2] == pytest.approx(40 / 120)
    for y in (1, 2):
        assert out["kpi_dp_roe"][y] == pytest.approx(out["kpi_r_roe"][y])  # net margin x turnover x multiplier = ROE
        assert out["kpi_dp_nm"][y] * out["kpi_dp_turn"][y] * out["kpi_dp_mult"][y] == pytest.approx(out["kpi_r_roe"][y])


def test_reference_shows_n_a_for_zero_or_negative_denominators():
    from engine.spec import Timing

    ann = _ann(
        rev={1: 0.0, 2: 150.0},
        paid_in={1: 10.0, 2: 10.0},
        retained={1: -30.0, 2: -40.0},  # equity -20, -30
        total_assets={1: 0.0, 2: 230.0},
    )
    out = K.reference(get_template("saas"), ann, Timing("annual", 2))
    for name in ("kpi_r_gm", "kpi_r_ebitda_m", "kpi_r_ni_m", "kpi_r_payroll_pct", "kpi_r_opex_pct", "kpi_dp_nm"):
        assert out[name][1] == "n/a", name  # revenue = 0
    assert out["kpi_r_growth"][2] == "n/a"  # prior revenue is zero
    assert out["kpi_r_roa"][1] == "n/a" and out["kpi_dp_turn"][1] == "n/a"  # assets = 0
    for y in (1, 2):  # equity <= 0
        for name in ("kpi_r_roe", "kpi_r_debt_eq", "kpi_dp_mult", "kpi_dp_roe"):
            assert out[name][y] == "n/a", (name, y)
        assert out["kpi_dp_diff"][y] == 0.0
    assert out["kpi_r_roa"][2] == pytest.approx(15 / 230)


# --------------------------------------------------------------------------- KPI rows the challenger recomputes
EXPECTED_ROWS = {  # E27 review: every KPI row shown on the Dashboard industry block and named in the E31 task
    "saas": {"arr", "ltv_cac", "cust_end"},
    "real_estate": {"noi", "occ", "ds", "dscr"},
    "services": {"util", "eff_rate", "rev_fte", "hours"},
    "home_services": {"util", "rev_job", "jobs"},
    "fitness": {"cap_use", "mrr", "members_end"},
    "retail": {"store_sales", "online_sales", "orders", "stores_end"},
    "cafe": {"cust", "ticket"},
    "bakery": {"rev_retail", "rev_ws", "cust_day", "accounts_end"},
    "car_wash": {"members_end", "washes_day", "cap_use", "rev_per_wash"},
    "auto_repair": {"billed_h", "cap_use", "rev_ro", "rev_hour"},
    "pet_care": {"grooms", "groom_use", "occ_rate", "revpan"},
    "guest_house": {"occ_rate", "adr_eff", "revpar", "stays"},
    "salon": {"util", "services", "ticket"},
    "childcare": {"occ", "enr_end", "rev_child", "care_pct"},
}


@pytest.mark.parametrize("key", sorted(TEMPLATES))
def test_kpi_rows_are_checked_or_derived(key):
    tpl = get_template(key)
    rows = {r.key for r in tpl.kpi_rows(Timing_(3))}
    checked = set(tpl.kpi_checked) | set(tpl.kpi_derived)
    assert checked <= rows and not set(tpl.kpi_checked) & set(tpl.kpi_derived)
    assert EXPECTED_ROWS[key] <= checked, (key, EXPECTED_ROWS[key] - checked)
    for m in tpl.dashboard_metrics(Timing_(3)):  # every KPI row shown on the Dashboard
        if m.src.startswith("kpi:"):
            assert m.src[4:] in checked, (key, m.key)


def Timing_(years):
    from engine.spec import Timing

    return Timing("monthly", years)


@pytest.mark.parametrize("key", sorted(TEMPLATES))
def test_manifest_lists_ratios_derived_rows_and_dashboard_metrics(key):
    brief = _brief(key, tier="full")
    tpl = get_template(key)
    man = manifest_for(plan(brief, tpl), "")
    assert {f"kpi_r_{k}" for k in K.ratio_keys(tpl)} <= set(man.kpi_years)
    assert {f"kpi_{k}" for k, *_ in K.DUPONT} <= set(man.kpi_years)
    assert {f"kpi_row_{k}" for k in tpl.kpi_derived} <= set(man.kpi_years)
    assert all(set(v) == {1, 2, 3} for v in man.kpi_years.values())
    assert any(n.startswith("dash_m_") for n in man.dash_years)
    light = manifest_for(plan(brief.with_options(tier="light"), tpl), "")
    assert set(light.kpi_years) == {f"kpi_row_{k}" for k in tpl.kpi_derived}  # no ratios on Light


# --------------------------------------------------------------------------- recalculated file
@lo
def test_dupont_check_in_the_file_and_values(build):
    brief = _brief("saas", tier="full", horizon_years=3)
    path = build(brief)
    assert recalc(path).ok
    wb = load_workbook(path, data_only=True)
    checks = {r[0].value: r[1].value for r in wb["Checks"].iter_rows(min_col=1, max_col=2) if r[0].value}
    assert checks["DuPont ties to return on equity"] == "PASS"
    pl = plan(brief, get_template("saas"))
    ws, lay = wb["KPIs"], pl.kpis
    for y in (1, 2, 3):
        roe, dp = ws.cell(row=lay.ratios["roe"], column=1 + y).value, ws.cell(row=lay.dupont["dp_roe"], column=1 + y)
        assert isinstance(roe, float) and dp.value == pytest.approx(roe)
    assert ws["B6"].value == "n/a" and isinstance(ws["C6"].value, float)


@lo
def test_negative_equity_shows_n_a_and_the_model_passes(build):
    """A planning-stage model that burns through its equity: equity-based ratios are n/a, nothing breaks."""
    tpl = get_template("saas")
    brief = tpl.default_brief("planning").with_options(tier="full", horizon_years=3)
    drivers = [
        d.model_copy(update={"low": 20_000.0, "base": 20_000.0, "high": 20_000.0}) if d.key == "equity" else d
        for d in brief.drivers
    ]
    brief = brief.model_copy(update={"drivers": drivers})
    path = build(brief)
    assert recalc(path).ok
    wb = load_workbook(path, data_only=True)
    pl = plan(brief, tpl)
    ws, lay = wb["KPIs"], pl.kpis
    bs = wb["Balance Sheet"]
    eq_row = pl.blocks["bs"].placed["total_equity"]
    equity = [bs.cell(row=eq_row, column=1 + y).value for y in (1, 2, 3)]
    assert equity[-1] <= 0, equity  # the scenario does what the test needs
    for y, eq in zip((1, 2, 3), equity, strict=True):
        if eq <= 0:
            for k in ("roe", "debt_eq"):
                assert ws.cell(row=lay.ratios[k], column=1 + y).value == "n/a"
            for k in ("dp_mult", "dp_roe"):
                assert ws.cell(row=lay.dupont[k], column=1 + y).value == "n/a"
            assert ws.cell(row=lay.dupont["dp_diff"], column=1 + y).value == 0
    checks = {r[0].value: r[1].value for r in wb["Checks"].iter_rows(min_col=1, max_col=2) if r[0].value}
    assert checks["DuPont ties to return on equity"] in ("PASS", "n/a") and checks["No error values"] == "PASS"
    report = challenge(brief, path)
    assert report["problems"] == [] and report["verdict"] == "PASS"


@lo
@pytest.mark.parametrize("key", sorted(TEMPLATES))
@pytest.mark.parametrize("granularity", ["monthly", "annual"])
def test_every_template_passes_with_the_kpis_sheet(build, key, granularity):
    brief = _brief(key, tier="full", granularity=granularity, horizon_years=3)
    path = build(brief)
    res = recalc(path)
    assert res.ok, res.errors
    report = challenge(brief, path)
    assert report["problems"] == [] and report["verdict"] == "PASS"


@lo
@pytest.mark.parametrize(
    "key,find,replace,needle",
    [
        ("saas", "roa", "=0.5", "kpi_r_roa"),  # a wrong ratio
        ("saas", "dp_turn", "=1", "kpi_dp_turn"),  # a wrong DuPont leg
        ("real_estate", "dscr", '="n/a"', "dscr"),  # a template KPI row (derived)
        ("retail", "store_sales", "=1", "store_sales"),  # a KPI row that is a roll-up
    ],
)
def test_challenger_catches_a_wrong_cell(build, key, find, replace, needle):
    brief = _brief(key, tier="full", horizon_years=3)
    path = build(brief)
    pl = plan(brief, get_template(key))
    if find in pl.kpis.ratios:
        row = pl.kpis.ratios[find]
    elif find in pl.kpis.dupont:
        row = pl.kpis.dupont[find]
    else:
        row = pl.blocks["kpi"].placed[find]
    wb = load_workbook(path)
    wb["KPIs"].cell(row=row, column=3, value=replace)  # year 2
    wb.save(path)
    report = challenge(brief, path)
    assert report["verdict"] == "FAIL" and any(needle in p for p in report["problems"]), report["problems"]


@lo
def test_dashboard_industry_lines_are_checked(build):
    brief = _brief("saas", tier="full", horizon_years=3)
    path = build(brief)
    pl = plan(brief, get_template("saas"))
    row = next(r for m, r in pl.dash.metrics if m.key == "arr")
    wb = load_workbook(path)
    wb["Dashboard"].cell(row=row, column=3, value=1.0)
    wb.save(path)
    report = challenge(brief, path)
    assert report["verdict"] == "FAIL" and any("dash_m_arr" in p for p in report["problems"])


def test_tile_sub_lines_are_numeric_not_text_rounded(build):
    """The funding tile's shortfall is a number shown through a cell format, so an x.x5 value cannot fail a model."""
    brief = _brief("saas", tier="full")
    ws = load_workbook(build(brief))["Dashboard"]
    sub = ws["P8"]  # tile 5, FUNDING REQUIRED
    assert "TEXT(" not in sub.value and sub.number_format == '"Shortfall "$#,##0.0,,"M"'
    for name, ref in manifest_for(plan(brief, get_template("saas")), "").dash_cells.items():
        if name.endswith("_sub"):
            cell = ws[ref.split("!")[1]]
            assert "TEXT(" not in str(cell.value), name


def test_column_letters_helper_matches_layout():
    lay = K.KpiLayout(5)
    assert L(lay.target_col) == "G" and lay.chart_cols == ("I", "Q")


def test_money_rows_are_thousands_and_per_unit_rows_are_dollars(saas):
    wb, pl = saas
    ws, kpi = wb["KPIs"], pl.blocks["kpi"]
    money, unit = '$#,##0,;($#,##0,);"-"', "$#,##0;($#,##0);-"
    assert ws.cell(row=kpi.placed["arr"], column=2).number_format == money
    assert ws.cell(row=kpi.placed["mrr_end"], column=7).number_format == money  # Target follows the row
    for key in ("arpa", "cac", "ltv"):
        assert ws.cell(row=kpi.placed[key], column=2).number_format == unit
        assert ws.cell(row=kpi.placed[key], column=1).value.endswith("($)")
    assert ws.cell(row=kpi.placed["arr"], column=2).font.color.rgb[-6:] == "1B2A2F"  # ink, not black
    for key in TEMPLATES:  # no usd2 row is left in thousands
        tpl = get_template(key)
        for r in tpl.kpi_rows(Timing_(3)):
            if r.fmt == "usd2":
                assert K.row_format(tpl, r) == "$#,##0.00;($#,##0.00);-" and K.is_unit_row(tpl, r)


@lo
def test_dupont_check_flags_a_one_sided_na_and_is_neutral_when_nothing_is_compared(build):
    brief = _brief("saas", tier="full", horizon_years=3)
    path = build(brief)
    pl = plan(brief, get_template("saas"))
    lay = pl.kpis

    def verdict(edit):
        wb = load_workbook(path)
        edit(wb["KPIs"])
        p2 = path.with_name("edited.xlsx")
        wb.save(p2)
        assert recalc(p2).ok
        v = load_workbook(p2, data_only=True)["Checks"]
        return {r[0].value: r[1].value for r in v.iter_rows(min_col=1, max_col=2) if r[0].value}[
            "DuPont ties to return on equity"
        ]

    assert verdict(lambda ws: None) == "PASS"
    assert (
        verdict(lambda ws: ws.cell(row=lay.dupont["dp_roe"], column=3, value='="n/a"')) == "FAIL"
    )  # product n/a, ROE not
    assert (
        verdict(lambda ws: ws.cell(row=lay.ratios["roe"], column=3, value='="n/a"')) == "FAIL"
    )  # ROE n/a, product not

    def nothing(ws):
        for y in (1, 2, 3):
            ws.cell(row=lay.ratios["roe"], column=1 + y, value='="n/a"')
            ws.cell(row=lay.dupont["dp_roe"], column=1 + y, value='="n/a"')

    assert verdict(nothing) == "n/a"
