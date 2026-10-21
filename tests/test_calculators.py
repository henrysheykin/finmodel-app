"""E34: calculator specs, the expression language (Python and JS twins), the pages, sitemap and llms.txt."""

import json
import os
import random
import re
import shutil
import subprocess
from dataclasses import replace
from pathlib import Path

import pytest

from app import calculators as C
from app import seo
from app.calc_expr import FORMATS, ExprError, evaluate, format_value, parse, variables
from app.web import templates
from engine.templates import TEMPLATES

ROOT = Path(__file__).resolve().parents[1]
CALCS = list(C.calculators().values())
IDS = [c.name for c in CALCS]
EXAMPLES = [(c, ex) for c in CALCS for ex in c.examples]


def close(a, b, rel=1e-9):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= rel * max(1.0, abs(a), abs(b))


# --------------------------------------------------------------------------- specs
def test_the_reference_calculators_exist():
    assert {"cafe-menu-price", "cafe-food-cost-percent", "cafe-break-even-covers"} <= set(IDS)
    assert len(IDS) == len(set(IDS))


@pytest.mark.parametrize("calc", CALCS, ids=IDS)
def test_spec_is_well_formed(calc):
    assert 70 <= len(calc.description) <= 200
    assert calc.title.endswith("| StartupModel") and 30 <= len(calc.title) <= 90
    assert calc.slug == f"/calculators/{calc.name}"
    keys = [i.key for i in calc.inputs] + [o.key for o in calc.outputs]
    assert len(keys) == len(set(keys)), "every key is defined once"
    assert sorted(calc.order) == sorted(o.key for o in calc.outputs)
    seen = {i.key for i in calc.inputs}  # evaluation order: every dependency comes first
    for key in calc.order:
        assert variables(calc.output(key).ast) <= seen, key
        seen.add(key)
    assert sum(o.highlight for o in calc.outputs) <= 1
    assert calc.template in ("", *TEMPLATES)
    for rel in calc.related:
        assert f"/calculators/{rel}" in C.calculators()
    if calc.guide:
        assert calc.guide in seo.pages()


def test_every_output_is_covered_by_an_example_and_a_dash_case_exists():
    for calc in CALCS:
        covered = {k for ex in calc.examples for k in ex.expect}
        assert covered == {o.key for o in calc.outputs}, calc.name
    assert any(v is None for _, ex in EXAMPLES for v in ex.expect.values()), "a division-by-zero example"


@pytest.mark.parametrize(("calc", "ex"), EXAMPLES, ids=[f"{c.name}:{e.name[:30]}" for c, e in EXAMPLES])
def test_examples_match_in_python(calc, ex):
    got = calc.compute(ex.inputs)
    for key, want in ex.expect.items():
        assert close(got[key], want, 1e-6), (key, got[key], want)


def _spec(tmp_path, inputs=None, outputs=None, extra="", front="", name="x"):
    inputs = inputs or "- key: a\n  label: A\n  unit: $\n  default: 2\n  min: 0\n  max: 10\n  step: 1\n  format: int"
    outputs = outputs or "- key: b\n  label: B\n  formula: a * 2\n  format: int"
    text = (
        f"---\nslug: /calculators/{name}\ntitle: Test calculator for the spec checks | StartupModel\n"
        "description: A test calculator used only by the unit tests, to check how the loader rejects a broken spec"
        " and accepts a good one.\n"
        f"keyword: test\n{front}---\n\n# Test\n\nIntro.\n\n```inputs\n{inputs}\n```\n\n```outputs\n{outputs}\n```\n\n"
        f"```examples\n- name: one\n  inputs: a=2\n  expect: b=4\n```\n{extra}\n## Section\n\nText.\n"
    )
    path = tmp_path / f"{name}.md"
    path.write_text(text)
    return path


def test_a_minimal_spec_loads(tmp_path):
    calc = C.load_calculator(_spec(tmp_path))
    assert calc.compute() == {"b": 4.0} and calc.template == "" and calc.industry == "General"


@pytest.mark.parametrize(
    ("outputs", "message"),
    [
        ("- key: a\n  label: A\n  formula: 1\n  format: int", "more than once"),
        (
            "- key: b\n  label: B\n  formula: c + 1\n  format: int\n"
            "- key: c\n  label: C\n  formula: b + 1\n  format: int",
            "cycle",
        ),
        ("- key: b\n  label: B\n  formula: b + 1\n  format: int", "cycle"),
        ("- key: b\n  label: B\n  formula: zz + 1\n  format: int", "undefined name"),
        ("- key: b\n  label: B\n  formula: 1 +\n  format: int", "formula"),
        ("- key: b\n  label: B\n  formula: a\n  format: bogus", "unknown format"),
        ("- key: min\n  label: B\n  formula: a\n  format: int", "valid key"),
        ("- key: b\n  label: B\n  formula: a\n  format: int\n  colour: red", "unknown field"),
    ],
)
def test_broken_outputs_are_rejected(tmp_path, outputs, message):
    with pytest.raises(ValueError, match=message):
        C.load_calculator(_spec(tmp_path, outputs=outputs))


@pytest.mark.parametrize(
    ("inputs", "message"),
    [
        ("- key: a\n  label: A\n  default: 20\n  min: 0\n  max: 10\n  step: 1\n  format: int", "min <= default <= max"),
        ("- key: a\n  label: A\n  default: x\n  min: 0\n  max: 10\n  step: 1\n  format: int", "not a number"),
        ("- key: a\n  label: A\n  default: 1\n  min: 0\n  max: 10\n  format: int", "missing"),
        ("not a list", "unexpected line"),
    ],
)
def test_broken_inputs_are_rejected(tmp_path, inputs, message):
    with pytest.raises(ValueError, match=message):
        C.load_calculator(_spec(tmp_path, inputs=inputs))


def test_front_matter_and_examples_are_validated(tmp_path):
    with pytest.raises(ValueError, match="unknown template"):
        C.load_calculator(_spec(tmp_path, front="template: nope\n"))
    with pytest.raises(ValueError, match="description"):
        p = _spec(tmp_path, name="y")
        p.write_text(re.sub(r"description: .*", "description: Short", p.read_text()))
        C.load_calculator(p)
    with pytest.raises(ValueError, match="slug"):
        p = _spec(tmp_path, name="z")
        p.write_text(p.read_text().replace("/calculators/z", "/guides/z"))
        C.load_calculator(p)
    p = _spec(tmp_path, name="w")
    p.write_text(p.read_text().replace("inputs: a=2", "inputs: a=99"))
    with pytest.raises(ValueError, match="outside its min and max"):
        C.load_calculator(p)


def test_table_blocks(tmp_path):
    ok = "\n```table\ntitle: Sweep\ninput: a\nvalues: 1, 2, 3\noutputs: b\n```\n"
    calc = C.load_calculator(_spec(tmp_path, extra=ok))
    assert [v for v, _ in calc.sweep()] == [1.0, 2.0, 3.0] and [o["b"] for _, o in calc.sweep()] == [2.0, 4.0, 6.0]
    rel = ok.replace("values: 1, 2, 3", "relative: -50, 0, 50")
    calc = C.load_calculator(_spec(tmp_path, extra=rel, name="r"))
    assert [v for v, _ in calc.sweep()] == [1.0, 2.0, 3.0]
    assert [v for v, _ in calc.sweep({"a": 4})] == [2.0, 4.0, 6.0]
    assert [v for v, _ in calc.sweep({"a": None})] == [None, None, None]
    for bad in ("values: 1, 2\nrelative: 1, 2", "values: 1", "values: 1, 20", "values: 1, 2\noutputs: zzz"):
        text = (
            f"\n```table\ntitle: Sweep\ninput: a\n{bad}\noutputs: b\n```\n"
            if "outputs" not in bad
            else (f"\n```table\ntitle: Sweep\ninput: a\n{bad}\n```\n")
        )
        with pytest.raises(ValueError, match="table"):
            C.load_calculator(_spec(tmp_path, extra=text, name="t"))


def test_inputs_are_clamped_and_invalid_inputs_give_dashes(tmp_path):
    calc = C.load_calculator(_spec(tmp_path))
    assert calc.compute({"a": 100}) == {"b": 20.0} and calc.compute({"a": -5}) == {"b": 0.0}
    assert calc.compute({"a": None}) == {"b": None}


# --------------------------------------------------------------------------- the expression language
EXPR_CASES = [
    ("1+2*3", {}, 7),
    ("(1+2)*3", {}, 9),
    ("2^3^2", {}, 512),
    ("-2^2", {}, -4),
    ("2^-1", {}, 0.5),
    ("2^0.5", {}, 2**0.5),
    ("10/4", {}, 2.5),
    ("1/0", {}, None),
    ("0/0", {}, None),
    ("1/(2-2)", {}, None),
    ("1 + 1/0", {}, None),
    ("0 * (1/0)", {}, None),
    ("if(1/0 > 0, 1, 2)", {}, None),
    ("if(0, 1/0, 5)", {}, 5),
    ("if(1, 5, 1/0)", {}, 5),
    ("if(2 > 1, 10, 20)", {}, 10),
    ("min(3, 1, 2)", {}, 1),
    ("max(3, 1, 2)", {}, 3),
    ("min(1, 1/0)", {}, None),
    ("round(2.5)", {}, 3),
    ("round(-2.5)", {}, -3),
    ("round(2.4)", {}, 2),
    ("round(-2.4)", {}, -2),
    ("round(1234.5678, 2)", {}, 1234.57),
    ("round(-1234.5678, 2)", {}, -1234.57),
    ("round(1.005, 2)", {}, 1.0),
    ("round(5, 10)", {}, None),
    ("round(5, 1.5)", {}, None),
    ("round(5, -1)", {}, None),
    ("abs(-3)", {}, 3),
    ("abs(3 - 5)", {}, 2),
    ("3 > 2", {}, 1),
    ("2 >= 3", {}, 0),
    ("2 == 2", {}, 1),
    ("2 != 2", {}, 0),
    ("1 < 2 + 3", {}, 1),
    ("2 × 3 ÷ 4 − 1", {}, 0.5),
    ("(-8)^0.5", {}, None),
    ("0^-1", {}, None),
    ("0^0", {}, 1),
    ("10^400", {}, None),
    ("(-2)^3", {}, -8),
    (".5 + 1", {}, 1.5),
    ("  1\t+\n2 ", {}, 3),
    ("x * y", {"x": 3, "y": 4}, 12),
    ("x / y", {"x": 3, "y": 0}, None),
    ("x + 1", {"x": None}, None),
    ("if(x > 1, 1, 2)", {"x": None}, None),
    ("round(x / 3, 1)", {"x": 10}, 3.3),
    ("100 - a - b", {"a": 30, "b": 8}, 62),
]
EXPR_ERRORS = [
    "",
    "1 +",
    "foo(1)",
    "min(1)",
    "abs(1, 2)",
    "if(1, 2)",
    "round()",
    "round(1, 2, 3)",
    "1 2",
    "(1",
    "1)",
    "x y",
    "min",
    "1.",
    "$5",
    "1e3",
    "__import__('os')",
    "2 ** 3",
    "a.b",
    "1 = 1",
    "1,2",
    "min(1,)",
    "x",
    "A + 1",
    "(" * 60 + "1" + ")" * 60,
    "-" * 60 + "1",
    "1+" * 300 + "1",
]


@pytest.mark.parametrize(("src", "env", "want"), EXPR_CASES, ids=[c[0][:30] for c in EXPR_CASES])
def test_expression_values(src, env, want):
    got = evaluate(parse(src), env)
    assert close(got, want), (src, got, want)


@pytest.mark.parametrize("src", EXPR_ERRORS, ids=[s[:20] or "empty" for s in EXPR_ERRORS])
def test_expression_errors(src):
    with pytest.raises(ExprError):
        evaluate(parse(src), {})


def test_variables_and_no_python_execution():
    assert variables(parse("if(a > b, min(c, 2), d ^ 2)")) == {"a", "b", "c", "d"}
    for evil in ("__import__('os').system('true')", "().__class__", "open('x')", "lambda: 1", "a if b else c"):
        with pytest.raises(ExprError):
            parse(evil)


FORMAT_CASES = [
    (1234.5, "money", "$1,235"),
    (1234.5, "money2", "$1,234.50"),
    (-1234.567, "money2", "-$1,234.57"),
    (0.125, "number2", "0.13"),
    (2.5, "int", "3"),
    (-2.5, "int", "-3"),
    (-0.001, "money2", "$0.00"),
    (0, "money", "$0"),
    (28.8888, "percent", "28.9%"),
    (30, "percent0", "30%"),
    (3.4615, "multiple", "3.46x"),
    (1234567.891, "number1", "1,234,567.9"),
    (None, "money", "—"),
    (1e15, "int", "—"),
    (999999999999999, "int", "999,999,999,999,999"),
    (0.5, "int", "1"),
    (1.005, "number2", "1.00"),
]


@pytest.mark.parametrize(("v", "fmt", "want"), FORMAT_CASES)
def test_format_value(v, fmt, want):
    assert format_value(v, fmt) == want


# --------------------------------------------------------------------------- JS parity
def _node():
    exe = shutil.which("node")
    if exe:
        return exe
    if os.environ.get("CI"):
        pytest.fail("CI is set but node is not installed: the JS evaluator parity test must run in CI")
    pytest.skip("node is not installed (local run); CI always runs this test")


def _fuzz_cases(calc, rng):
    cases = [{}, {i.key: i.min for i in calc.inputs}, {i.key: i.max for i in calc.inputs}]
    cases += [dict(ex.inputs) for ex in calc.examples]
    for _ in range(40):
        row = {}
        for inp in calc.inputs:
            pick = rng.random()
            if pick < 0.12:
                row[inp.key] = None
            elif pick < 0.22:
                row[inp.key] = inp.max * 2 + 1  # out of range: clamped
            elif pick < 0.30:
                row[inp.key] = inp.min - 1
            elif pick < 0.40:
                row[inp.key] = 0.0
            else:
                row[inp.key] = round(rng.uniform(inp.min, inp.max), rng.choice([0, 1, 2, 6]))
        cases.append(row)
    return cases


def test_js_evaluator_gives_the_same_results_as_python():
    node = _node()
    rng = random.Random(34)
    specs = [{"slug": c.slug, "spec": c.client_spec(), "cases": _fuzz_cases(c, rng)} for c in CALCS]
    exprs = [{"src": s, "env": e} for s, e, _ in EXPR_CASES] + [{"src": s, "env": {}} for s in EXPR_ERRORS]
    formats = [{"v": v, "fmt": f} for v, f, _ in FORMAT_CASES]
    for v in (0, 1, -1, 0.5, 1.5, 2.5, 1234.565, 0.045, 99.995, 1e-7, -1e-7, 123456789.125, 4.675):
        formats += [{"v": v, "fmt": f} for f in FORMATS]
    proc = subprocess.run(
        [node, str(ROOT / "tests" / "js" / "calc_runner.js")],
        input=json.dumps({"specs": specs, "exprs": exprs, "formats": formats}),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr[-2000:]
    out = json.loads(proc.stdout)

    for case, res in zip(exprs, out["exprs"], strict=True):
        try:
            want = {"v": evaluate(parse(case["src"]), case["env"])}
        except ExprError:
            want = {"error": True}
        assert ("error" in res) == ("error" in want), (case, res, want)
        if "v" in want:
            assert close(res["v"], want["v"]), (case, res, want)
    for case, text in zip(formats, out["formats"], strict=True):
        assert text == format_value(case["v"], case["fmt"]), case
    for spec, res in zip(specs, out["specs"], strict=True):
        calc = C.calculators()[spec["slug"]]
        for values, js in zip(spec["cases"], res["cases"], strict=True):
            want = calc.compute(values)
            for key, w in want.items():
                assert close(js["outputs"][key], w), (calc.name, values, key, js["outputs"][key], w)
                assert js["formatted"][key] == format_value(w, calc.output(key).format), (calc.name, values, key)
            rows = calc.sweep(values)
            assert len(js["rows"]) == len(rows)
            for jr, (sv, outs) in zip(js["rows"], rows, strict=True):
                assert close(jr["value"], sv)
                for key, w in outs.items():
                    assert close(jr["outputs"][key], w), (calc.name, values, key)
    # and the JS results agree with the hand-checked expectations of every example
    for spec, res in zip(specs, out["specs"], strict=True):
        calc = C.calculators()[spec["slug"]]
        for ex, js in zip(calc.examples, res["cases"][3 : 3 + len(calc.examples)], strict=True):
            for key, want in ex.expect.items():
                assert close(js["outputs"][key], want, 1e-6), (calc.name, ex.name, key)


# --------------------------------------------------------------------------- pages
class _Doc:
    def __init__(self, html):
        from html.parser import HTMLParser

        outer = self
        self.hrefs, self.ids, self.headings = [], set(), []

        class P(HTMLParser):
            def handle_starttag(self, tag, attrs):
                a = dict(attrs)
                if tag == "a" and a.get("href"):
                    outer.hrefs.append(a["href"])
                if a.get("id"):
                    outer.ids.add(a["id"])
                if re.fullmatch(r"h[1-6]", tag):
                    outer.headings.append(int(tag[1]))

        P().feed(html)


def _ld(html):
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


@pytest.mark.parametrize("calc", CALCS, ids=IDS)
def test_page_renders_with_seo_basics(client, calc):
    r = client.get(calc.slug)
    assert r.status_code == 200
    html = r.text
    doc = _Doc(html)
    assert doc.headings.count(1) == 1
    for prev, cur in zip(doc.headings, doc.headings[1:], strict=False):
        assert cur <= prev + 1, doc.headings
    assert f"<title>{calc.title.replace('&', '&amp;')}</title>" in html
    assert f'<meta name="description" content="{calc.description}">' in html
    assert f'<link rel="canonical" href="http://testserver{calc.slug}">' in html
    assert 'property="og:title"' in html and "noindex" not in html
    assert f"<h1>{calc.h1}</h1>" in html
    assert "{#" not in html and "**" not in html and not re.search(r"\[[A-Z][A-Z_]{2,}\]", html)
    assert 'src="/static/calc.js?v=' in html
    for href in doc.hrefs:
        if href.startswith(("mailto:", "http")):
            continue
        if href.startswith("#"):
            assert href[1:] in doc.ids, href
            continue
        r2 = client.get(href.split("#")[0].split("?")[0])
        assert r2.status_code == 200, (calc.slug, href)


@pytest.mark.parametrize("calc", CALCS, ids=IDS)
def test_page_is_complete_without_javascript(client, calc):
    """Inputs hold their defaults and the results are already filled in, so nothing moves when the script starts."""
    html = client.get(calc.slug).text
    res = calc.compute()
    for inp in calc.inputs:
        assert re.search(rf'id="in-{inp.key}"[^>]*value="{re.escape(inp.attrs["default"])}"', html), inp.key
    for o in calc.outputs:
        assert f'data-out="{o.key}">{format_value(res[o.key], o.format)}</dd>' in html, o.key
    if calc.table:
        assert html.count("data-row=") == len(calc.sweep())
    spec = json.loads(re.search(r'<script type="application/json" data-calc-spec>(.*?)</script>', html, re.S).group(1))
    assert spec == json.loads(json.dumps(calc.client_spec()))
    assert len(spec["outputs"]) == len(calc.outputs)


@pytest.mark.parametrize("calc", CALCS, ids=IDS)
def test_structured_data(client, calc):
    blocks = {b["@type"]: b for b in _ld(client.get(calc.slug).text)}
    assert blocks["BreadcrumbList"]["itemListElement"][-1]["item"] == "http://testserver" + calc.slug
    assert blocks["WebApplication"]["offers"]["price"] == "0"
    if calc.faq:
        faq = blocks["FAQPage"]["mainEntity"]
        assert [q["name"] for q in faq] == [q for q, _ in calc.faq]
        assert all(q["acceptedAnswer"]["text"] and "<" not in q["acceptedAnswer"]["text"] for q in faq)
    else:
        assert "FAQPage" not in blocks


def test_faq_extraction():
    md = (
        "# T\n\n## Other\n\n### Not a question\n\nx\n\n## FAQ {#faq}\n\n"
        "### Q one?\n\nAnswer **one** with [a link](/x).\n\n"
        "### Q two?\n\nTwo.\n\nMore.\n\n## After\n\n### Nope\n\ny\n"
    )
    faq = C.extract_faq(md)
    assert faq == (("Q one?", "Answer one with a link."), ("Q two?", "Two. More."))
    assert C.extract_faq("# T\n\n## Section\n\ntext\n") == ()


@pytest.mark.parametrize("calc", CALCS, ids=IDS)
def test_model_promotion_block(client, services, calc):
    html = client.get(calc.slug).text
    cfg = services.cfg
    light, full = (f"${cfg.prices[t] / 100:,.0f}" for t in ("light", "full"))
    block = re.search(r'<aside class="promo cta".*?</aside>', html, re.S).group(0)
    assert f"Light <span>{light}</span>" in block and f"Full <span>{full}</span>" in block
    start = f"/start?type={TEMPLATES[calc.template].business_types[0]}" if calc.template else "/start"
    assert f'href="{start}"' in block
    assert "Get a Restaurant / cafe model built on your numbers" in block
    sample = f"/samples/{calc.sample.filename}"
    assert f'href="{sample}"' in block and client.get(sample).content[:2] == b"PK"
    tiers = re.findall(r'<div class="promo__tier.*?</div>', block, re.S)
    light_block = next(t for t in tiers if "Light" in t)
    assert not re.search(r"statement|valuation|DCF|balance sheet|cash flow", light_block, re.I)
    full_block = next(t for t in tiers if "Full" in t)
    assert re.search(r"statement", full_block, re.I) and re.search(r"Valuation", full_block)
    assert "Checks sheet" in block


def test_promo_without_a_template_is_generic(services):
    promo = C.promo_context("", None, services.cfg)
    html = templates.env.get_template("_model_promo.html").render(promo=promo)
    assert "Get a financial model built on your numbers" in html and 'href="/start"' in html
    assert "Download the sample" not in html and "$149" in html and "$349" in html


def test_index_sitemap_and_llms_list_every_calculator(client):
    idx = client.get("/calculators")
    assert idx.status_code == 200 and client.get("/calculators/").status_code == 200
    assert '<link rel="canonical" href="http://testserver/calculators">' in idx.text
    assert "<h2>Restaurant / cafe</h2>" in idx.text
    sm = client.get("/sitemap.xml").text
    llms = client.get("/llms.txt").text
    assert "<loc>http://testserver/calculators</loc>" in sm and "## Calculators" in llms
    for calc in CALCS:
        assert f'href="{calc.slug}"' in idx.text
        assert f"<loc>http://testserver{calc.slug}</loc>" in sm
        assert f"[{calc.h1}](http://testserver{calc.slug}): {calc.description}" in llms
    assert 'href="/calculators"' in client.get("/").text  # footer


def test_unknown_calculator_is_404(client):
    assert client.get("/calculators/nope").status_code == 404


def test_groups_are_by_industry_with_general_last():
    groups = C.by_industry()
    assert groups[0][0] == "Restaurant / cafe" and len(groups[0][1]) >= 3


# --------------------------------------------------------------------------- copy rules and design
@pytest.mark.parametrize("calc", CALCS, ids=IDS)
def test_copy_follows_the_facts_rule(calc):
    assert not C.PLACEHOLDER_RE.search(calc.body_md + calc.intro_html), "no [UPPER] placeholders"
    assert C.unsourced_figures(calc) == []
    assert not re.search(r"FinModelsLab|getdraftplan|Ledgerline", calc.body_md, re.I)
    assert calc.words >= 500


def test_unsourced_figure_helper_flags_and_accepts():
    calc = C.calculators()["/calculators/cafe-menu-price"]
    bad = C.unsourced_figures(replace(calc, body_md="Typical cafes run 31.7% food cost.\n"))
    assert bad and "31.7%" in bad[0]
    sourced = "Typical cafes run 31.7% food cost, says [a survey](https://example.com/survey).\n"
    assert C.unsourced_figures(replace(calc, body_md=sourced)) == []
    own = "The default is 30% and the price is $4.75.\n"
    assert C.unsourced_figures(replace(calc, body_md=own)) == []


def test_calculator_assets_keep_to_design_v2():
    css = (ROOT / "web" / "static" / "site.css").read_text()
    js = (ROOT / "web" / "static" / "calc.js").read_text()
    for banned in ("#1F3864", "#2563EB", "DM Sans"):
        assert banned.lower() not in css.lower() and banned.lower() not in js.lower()
    assert not re.search(r"\beval\s*\(|new Function|Function\s*\(", js)
    src = (ROOT / "app" / "calc_expr.py").read_text()
    assert not re.search(r"(?<![\w.])(eval|exec|compile)\s*\(|import ast", src)
