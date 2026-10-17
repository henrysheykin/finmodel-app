"""E13: landing page, legal pages, samples, robots / sitemap / llms.txt, and the hero preview data."""

import json
import re
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import landing
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


def test_low_case_shows_the_funding_warning():
    views = landing.sheet_views()
    low = {r["label"]: r for r in views["1"]["chk"]["rows"]}
    assert low["Funding sufficient (cash ≥ 0)"]["result"] == "WARN"
    base = {r["label"]: r for r in views["2"]["chk"]["rows"]}
    assert base["Funding sufficient (cash ≥ 0)"]["result"] == "PASS"


def test_money_and_percent_formats():
    assert landing.money(-27487.4) == "($27,487)"
    assert landing.money(0.2) == "–"
    assert landing.pct(-0.0859) == "(8.6%)"
    assert landing.fmt_input(0.33, "pct") == "33%" and landing.fmt_input(6.5, "usd2") == "$6.50"


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
