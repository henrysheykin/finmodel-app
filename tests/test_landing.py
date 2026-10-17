"""E13: landing page, legal pages, samples, robots / sitemap / llms.txt, and the hero preview data."""

import json
import re
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import landing, xlview
from app.main import create_app
from engine.brief import Brief
from engine.challenger import python_model

ROOT = Path(__file__).resolve().parents[1]


def test_landing_renders_with_seo_basics(client):
    r = client.get("/")
    assert r.status_code == 200
    html = r.text
    assert len(re.findall(r"<h1[\s>]", html)) == 1
    assert '<link rel="canonical" href="http://testserver/"' in html or 'rel="canonical"' in html
    assert 'name="description"' in html and 'property="og:title"' in html
    assert 'href="/start?plan=light"' in html and 'href="/start?plan=full"' in html
    assert "noindex" not in html
    # no unfinished copy on the public page
    assert not re.search(r"\[[A-Z][A-Z_]{3,}\]", html), re.findall(r"\[[A-Z][A-Z_]{3,}\]", html)
    assert "FinModelsLab" not in html and "Ledgerline" not in html


def test_structured_data_matches_prices(client, services):
    html = client.get("/").text
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    types = {b["@type"] for b in blocks}
    assert {"Organization", "Product", "FAQPage"} <= types
    product = next(b for b in blocks if b["@type"] == "Product")
    prices = {o["name"]: o["price"] for o in product["offers"]}
    assert prices == {
        "Light": f"{services.cfg.prices['light'] / 100:.2f}",
        "Full": f"{services.cfg.prices['full'] / 100:.2f}",
    }
    faq = next(b for b in blocks if b["@type"] == "FAQPage")
    assert len(faq["mainEntity"]) == len(landing.FAQ)
    for q, _ in landing.FAQ:  # the same questions are visible on the page
        assert f"<dt>{q.replace(chr(39), '&#39;')}</dt>" in html


def test_industries_come_from_the_catalog(client):
    html = client.get("/").text
    for label in landing.available_industries():
        assert label in html
    assert "coming soon" not in html.lower()


@pytest.mark.parametrize("scenario", ["1", "2", "3"])
def test_preview_numbers_match_the_independent_python_model(scenario):
    """The hero preview is real engine output: it must equal the challenger's Python model to the dollar."""
    data = landing.sheet_data()
    brief = Brief.load(ROOT / "engine" / "briefs" / "cafe.json").with_options(
        tier="full", granularity="monthly", horizon_years=data["years"]
    )
    ref = python_model(brief, int(scenario))
    summary = {r["label"]: r["values"] for r in data["scenarios"][scenario]["summary"]}
    pl = {r["label"]: r["values"] for r in data["scenarios"][scenario]["pl"]}
    pairs = [
        (summary["Revenue"], "rev"),
        (summary["Gross profit"], "gp"),
        (summary["EBITDA"], "ebitda"),
        (summary["Net income"], "ni"),
        (summary["Year-end cash"], "cash_close"),
        (summary["Year-end loan balance"], "loan_close"),
        (pl["Revenue"], "rev"),
        (pl["Net income"], "ni"),
    ]
    for shown, key in pairs:
        for y, v in enumerate(shown, start=1):
            assert abs(v - ref[key][y]) <= 1.0, (scenario, key, y, v, ref[key][y])
    verdict = next(c for c in data["scenarios"][scenario]["checks"] if c["label"] == "Overall verdict")
    assert verdict["result"].startswith("PASS")


def _sheet(name: str) -> dict:
    return xlview.sheet(name)


def _text(sheet: str, address: str, case: int = 2) -> str:
    return xlview.cell_view(_sheet(sheet), address, case)["text"]


def test_low_case_shows_the_funding_warning():
    assert _text("Checks", "B14", 1) == "WARN" and _text("Checks", "B14", 2) == "PASS"
    assert _text("Checks", "B16", 1) == "PASS WITH WARNINGS" and _text("Checks", "B16", 2) == "PASS"


@pytest.mark.parametrize("case", [1, 2, 3])
def test_spreadsheet_shows_the_same_numbers_as_the_checked_rows(case):
    """The hero spreadsheet and the rows checked against the Python model come from the same recalculation."""
    data = landing.sheet_data()
    summary = {r["label"]: r["values"] for r in data["scenarios"][str(case)]["summary"]}
    for row, label in ((8, "Revenue"), (10, "EBITDA"), (12, "Net income"), (13, "Year-end cash")):
        for i, col in enumerate("BCD"):
            assert _text("Dashboard", f"{col}{row}", case) == landing.money(summary[label][i]).replace("–", "-"), (
                case,
                label,
                col,
            )
    assert _text("Dashboard", "C4", case) == ["Low", "Base", "High"][case - 1]


def test_spreadsheet_is_the_whole_workbook():
    """Every sheet of the delivered file, every formula, the frozen panes and the scenario list on B4."""
    wb = xlview.workbook()
    data = landing.sheet_data()
    assert [s["name"] for s in wb["sheets"]] == data["stats"]["sheets"]
    formulas = sum(1 for s in wb["sheets"] for c in s["cells"].values() if len(c) > 2)
    assert formulas == data["stats"]["formulas"]
    for s in wb["sheets"]:
        for a, c in s["cells"].items():
            assert len(c) < 3 or c[2].startswith("="), (s["name"], a)
            values = c[1] if len(c) > 1 and isinstance(c[1], list) else [c[1] if len(c) > 1 else None]
            errors = {"#DIV/0!", "#N/A", "#VALUE!", "#REF!", "#NAME?", "#NUM!", "#NULL!"}
            assert not any(v in errors for v in values), (s["name"], a, values)
        assert s["start"] in s["cells"], s["name"]
    dash = _sheet("Dashboard")
    assert dash["lists"]["B4"]["options"] == ["1", "2", "3"] and dash["lists"]["B4"]["prompt"]
    assert dash["cells"]["C4"][2] == '=CHOOSE(B4,"Low","Base","High")'
    assert _sheet("Inputs")["cells"]["E7"][2].startswith("=CHOOSE(Dashboard!$B$4,")
    assert _sheet("Monthly")["freeze"] == [5, 2]


def test_preview_claims_match_the_build():
    data = landing.sheet_data()
    assert all(data["scenarios"][s]["formula_errors"] == 0 for s in "123")  # "0 formula errors" stamp
    assert data["stats"]["formulas"] > 1000 and "Checks" in data["stats"]["sheets"]


def test_hero_spreadsheet_is_server_rendered(client):
    html = client.get("/").text
    assert 'id="xl-grid"' in html and 'aria-activedescendant="xc-B4"' in html
    assert 'id="xc-B10"' in html and "$54,410" in html  # Dashboard in the Base case
    for name in xlview.workbook()["sheets"]:
        assert f'data-sheet="{name["name"].replace("&", "&amp;")}"' in html
    assert "0 formula errors in all three cases" in html
    assert 'id="demo"' in html and 'id="demo-data"' in html
    src = re.search(r'data-src="([^"]+)"', html).group(1)
    r = client.get(src)
    assert r.status_code == 200 and "immutable" in r.headers["cache-control"]
    assert r.json()["sheets"][0]["name"] == "Dashboard"
    assert "no-cache" in client.get("/preview/workbook.json").headers["cache-control"]


@pytest.mark.parametrize(
    ("value", "fmt", "text"),
    [
        (1234.5, "$#,##0;($#,##0);-", "$1,235"),
        (-27487.2, "$#,##0;($#,##0);-", "($27,487)"),
        (0, "$#,##0;($#,##0);-", "-"),
        (0.1333, "0.0%;(0.0%);-", "13.3%"),
        (-0.05, "0.0%;(0.0%);-", "(5.0%)"),
        (6.5, "$#,##0.00;($#,##0.00);-", "$6.50"),
        (3.5, "#,##0.0;(#,##0.0);-", "3.5"),
        (-1234.4, "#,##0;(#,##0);-", "(1,234)"),
        (2.5, "0", "3"),
        (0.35, "General", "0.35"),
        (36, "General", "36"),
        (1234.5, '\\$#,##0;"($"#,##0\\);\\-', "$1,235"),
        (-5, '\\$#,##0;"($"#,##0\\);\\-', "($5)"),
        ("PASS", "General", "PASS"),
        (True, "General", "TRUE"),
        (None, "General", ""),
    ],
)
def test_number_formats_follow_the_workbook(value, fmt, text):
    assert xlview.format_value(value, fmt)[0] == text


def test_start_prefills_from_the_demo_link(client):
    html = client.get("/start?type=restaurant_cafe&goal=dcf_valuation&horizon=5&granularity=annual&sample=1").text
    for name, value in (
        ("business_type", "restaurant_cafe"),
        ("goal", "dcf_valuation"),
        ("horizon_years", "5"),
        ("granularity", "annual"),
    ):
        assert re.search(rf'name="{name}" value="{value}"\s+checked', html), name
    assert re.search(r'name="sample_data" value="1"\s+checked', html)
    ignored = client.get("/start?goal=nonsense&horizon=7").text  # unknown values fall back to defaults
    assert re.search(r'name="goal" value="revenue_profit"\s+checked', ignored)


def test_money_and_percent_formats():
    assert landing.money(-27487.4) == "($27,487)"
    assert landing.money(0.2) == "–"
    assert landing.pct(-0.0859) == "(8.6%)"


def test_views_json_cannot_break_out_of_its_script_tag():
    out = str(landing._json_script({"x": "</script><b>&"}))
    assert "</script>" not in out and "<b>" not in out


def test_legal_pages_placeholder_until_text_exists(client, tmp_path, monkeypatch):
    monkeypatch.setattr(landing, "LEGAL", tmp_path)
    for page in ("privacy", "terms", "refunds"):
        r = client.get(f"/{page}")
        assert r.status_code == 200 and "being prepared" in r.text and "noindex" in r.text
    (tmp_path / "terms.md").write_text(
        "# Terms\n\n## Payment\n\nYou pay **once**.\n\n- one\n- two\n\n<script>x</script>"
    )
    r = client.get("/terms")
    assert "<h2>Terms</h2>" in r.text and "<h3>Payment</h3>" in r.text and "<strong>once</strong>" in r.text
    assert (
        "<li>one</li>" in r.text
        and "<script>x</script>" not in r.text
        and "&lt;script&gt;" in r.text
        and "noindex" not in r.text
    )
    assert "/terms" in client.get("/sitemap.xml").text


def test_samples_download_and_unknown_is_404(client):
    r = client.get("/samples/cafe.xlsx")
    assert r.status_code == 200 and r.content[:2] == b"PK"
    assert "startupmodel-sample-cafe.xlsx" in r.headers["content-disposition"]
    assert client.get("/samples/../../etc/passwd.xlsx").status_code == 404
    assert client.get("/samples/nope.xlsx").status_code == 404


def test_robots_sitemap_llms(client):
    robots = client.get("/robots.txt").text
    assert "Disallow: /admin" in robots and "Sitemap: " in robots
    sm = client.get("/sitemap.xml")
    assert sm.headers["content-type"].startswith("application/xml") and "<loc>" in sm.text
    llms = client.get("/llms.txt").text
    assert "StartupModel" in llms and "$149" in llms and "$349" in llms


def test_contact_link_uses_support_email(services):
    services.cfg = replace(services.cfg, support_email="support@startup-model.com")
    with TestClient(create_app(services)) as c:
        html = c.get("/").text
    assert 'href="mailto:support@startup-model.com"' in html


def test_no_competitor_palette_or_font():
    for folder in ("web", "app/templates"):
        for p in (ROOT / folder).rglob("*"):
            if p.is_file() and p.suffix in (".css", ".html", ".js"):
                text = p.read_text(encoding="utf-8")
                assert not re.search(r"1F3864|2563EB|DM Sans", text, re.I), p
