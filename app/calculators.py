"""Calculators (ADR-014, E34): content/calculators/*.md rendered at /calculators/<slug>.

A calculator is one spec file: front matter, fenced ``inputs`` / ``outputs`` / ``table`` / ``examples`` blocks and
the Markdown explanation (format documented in content/README.md). One page template and one vanilla-JS
evaluator (web/static/calc.js) serve every calculator; ``app/calc_expr.py`` is the Python twin of that evaluator.
The page is rendered on the server with the default inputs, so it reads correctly without JavaScript and the
results panel never changes size when the script takes over.

A spec that does not parse, uses an undefined or duplicate key, has a cycle between outputs or an example outside
an input's range fails loudly (at startup and in tests).
"""

from __future__ import annotations

import html as htmllib
import json
import re
from dataclasses import dataclass, field
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from markupsafe import Markup

from app import seo
from app.calc_expr import FORMATS, RESERVED, ExprError, Value, evaluate, format_value, parse, variables
from app.web import templates
from engine.samples import SampleSpec, parse_description
from engine.templates import TEMPLATES

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "calculators"

SLUG_RE = re.compile(r"^/calculators/[a-z0-9]+(?:-[a-z0-9]+)*$")
KEY_RE = re.compile(r"^[a-z][a-z0-9_]{0,39}$")
NUM_RE = re.compile(r"^-?(?:\d+(?:\.\d+)?|\.\d+)$")
LINE_RE = re.compile(r"^([a-z_]+):\s*(.*)$")
BLOCK_RE = re.compile(r"^```(inputs|outputs|table|examples)[ \t]*\n(.*?)\n```[ \t]*$", re.M | re.S)
FAQ_TITLE_RE = re.compile(r"^(faq|frequently asked questions|common questions)$", re.I)
INTRO = (
    "Free calculators for the numbers that decide whether a small business works. "
    "Each one shows its formula and links to a full Excel model you can build on your own numbers."
)

router = APIRouter()


def plain(v: float) -> str:
    """4.5 -> '4.5', 28000.0 -> '28000' (no exponent, no trailing zeros)."""
    return format(Decimal(repr(v)).normalize(), "f")


@dataclass(frozen=True)
class Input:
    key: str
    label: str
    unit: str
    default: float
    min: float
    max: float
    step: float
    format: str
    hint: str = ""

    def clamp(self, v: float) -> float:
        return min(max(v, self.min), self.max)

    @property
    def attrs(self) -> dict[str, str]:
        """value / min / max / step as plain decimal text for the HTML input."""
        return {k: plain(getattr(self, k)) for k in ("default", "min", "max", "step")}


@dataclass(frozen=True)
class Output:
    key: str
    label: str
    formula: str
    format: str
    highlight: bool = False
    note: str = ""
    ast: tuple = field(default=(), repr=False, compare=False)


@dataclass(frozen=True)
class Table:
    title: str
    input: str
    outputs: tuple[str, ...]
    values: tuple[float, ...] | None = None
    relative: tuple[float, ...] | None = None


@dataclass(frozen=True)
class Example:
    name: str
    inputs: dict[str, float]
    expect: dict[str, float | None]


@dataclass(frozen=True)
class Calculator:
    slug: str
    title: str
    description: str
    keyword: str
    h1: str
    intro_html: str  # the h1 and the opening paragraph(s)
    body_html: str  # the explanation, from the first ## heading on
    body_md: str
    words: int
    template: str
    industry: str
    related: tuple[str, ...]
    guide: str
    sample: SampleSpec | None
    inputs: tuple[Input, ...]
    outputs: tuple[Output, ...]  # display order
    order: tuple[str, ...]  # output keys in evaluation order
    table: Table | None
    examples: tuple[Example, ...]
    faq: tuple[tuple[str, str], ...]
    meta: dict = field(default_factory=dict)

    @property
    def name(self) -> str:
        return self.slug.split("/")[2]

    def input(self, key: str) -> Input:
        return next(i for i in self.inputs if i.key == key)

    def output(self, key: str) -> Output:
        return next(o for o in self.outputs if o.key == key)

    # ----- evaluation (the Python twin of calc.js compute / sweep) -----
    def compute(self, values: dict[str, Value] | None = None) -> dict[str, Value]:
        """Every output for the given input values (missing = default; None = not a number). Inputs are clamped."""
        values = values or {}
        env: dict[str, Value] = {}
        for inp in self.inputs:
            v = values.get(inp.key, inp.default)
            env[inp.key] = None if v is None else inp.clamp(v)
        out: dict[str, Value] = {}
        for key in self.order:
            env[key] = out[key] = evaluate(self.output(key).ast, env)
        return out

    def sweep_values(self, values: dict[str, Value] | None = None) -> list[Value]:
        t = self.table
        if t is None:
            return []
        inp = self.input(t.input)
        if t.values is not None:
            return [inp.clamp(v) for v in t.values]
        cur = (values or {}).get(t.input, inp.default)
        return [None if cur is None else inp.clamp(cur * (1 + r / 100)) for r in t.relative or ()]

    def sweep(self, values: dict[str, Value] | None = None) -> list[tuple[Value, dict[str, Value]]]:
        t = self.table
        if t is None:
            return []
        return [(sv, self.compute({**(values or {}), t.input: sv})) for sv in self.sweep_values(values)]

    def client_spec(self) -> dict:
        """What calc.js needs: inputs, outputs in evaluation order and the table."""
        t = self.table
        return {
            "inputs": [
                {k: getattr(i, k) for k in ("key", "label", "default", "min", "max", "step", "format")}
                for i in self.inputs
            ],
            "outputs": [
                {"key": k, "label": o.label, "formula": o.formula, "format": o.format, "highlight": o.highlight}
                for k in self.order
                for o in (self.output(k),)
            ],
            "table": None
            if t is None
            else {"input": t.input, "values": t.values, "relative": t.relative, "outputs": list(t.outputs)},
        }


# ---------- parsing ----------


def parse_items(text: str, where: str) -> list[dict[str, str]]:
    """Strict YAML-like list: ``- key: value`` starts an item, indented ``key: value`` lines continue it."""
    items: list[dict[str, str]] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("- "):
            items.append({})
            body = line[2:]
        elif line.startswith(" ") and items:
            body = line.strip()
        else:
            raise ValueError(f"{where}: unexpected line {raw!r}")
        m = LINE_RE.match(body)
        if not m:
            raise ValueError(f"{where}: expected 'key: value', got {raw!r}")
        key, value = m.group(1), m.group(2).strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
        if key in items[-1]:
            raise ValueError(f"{where}: {key!r} given twice in one item")
        items[-1][key] = value
    return items


def parse_mapping(text: str, where: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = LINE_RE.match(raw.strip())
        if not m or raw[0] == " ":
            raise ValueError(f"{where}: expected 'key: value', got {raw!r}")
        if m.group(1) in out:
            raise ValueError(f"{where}: {m.group(1)!r} given twice")
        val = m.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] == '"':
            val = val[1:-1]
        out[m.group(1)] = val
    return out


def _num(text: str, where: str) -> float:
    if not NUM_RE.match(text.strip()):
        raise ValueError(f"{where}: {text!r} is not a number")
    return float(text)


def _need(item: dict[str, str], allowed: set[str], required: set[str], where: str) -> None:
    extra = set(item) - allowed
    if extra:
        raise ValueError(f"{where}: unknown field(s) {sorted(extra)}")
    missing = required - set(item)
    if missing:
        raise ValueError(f"{where}: missing field(s) {sorted(missing)}")


def _key(text: str, where: str) -> str:
    if not KEY_RE.match(text) or text in RESERVED:
        raise ValueError(
            f"{where}: {text!r} is not a valid key (lowercase letters, digits, underscore; not a function name)"
        )
    return text


def _inputs(text: str, slug: str) -> tuple[Input, ...]:
    out = []
    for n, item in enumerate(parse_items(text, f"{slug} inputs"), 1):
        where = f"{slug} inputs #{n}"
        _need(
            item,
            {"key", "label", "unit", "default", "min", "max", "step", "format", "hint"},
            {"key", "label", "default", "min", "max", "step", "format"},
            where,
        )
        inp = Input(
            key=_key(item["key"], where),
            label=item["label"],
            unit=item.get("unit", ""),
            default=_num(item["default"], where),
            min=_num(item["min"], where),
            max=_num(item["max"], where),
            step=_num(item["step"], where),
            format=item["format"],
            hint=item.get("hint", ""),
        )
        if inp.format not in FORMATS:
            raise ValueError(f"{where}: unknown format {inp.format!r}")
        if inp.step <= 0 or not inp.min <= inp.default <= inp.max:
            raise ValueError(f"{where}: need step > 0 and min <= default <= max")
        out.append(inp)
    if not out:
        raise ValueError(f"{slug}: no inputs")
    return tuple(out)


def _outputs(text: str, slug: str) -> tuple[Output, ...]:
    out = []
    for n, item in enumerate(parse_items(text, f"{slug} outputs"), 1):
        where = f"{slug} outputs #{n}"
        _need(
            item,
            {"key", "label", "formula", "format", "highlight", "note"},
            {"key", "label", "formula", "format"},
            where,
        )
        if item["format"] not in FORMATS:
            raise ValueError(f"{where}: unknown format {item['format']!r}")
        if item.get("highlight", "false") not in ("true", "false"):
            raise ValueError(f"{where}: highlight must be true or false")
        try:
            ast = parse(item["formula"])
        except ExprError as exc:
            raise ValueError(f"{where}: formula {item['formula']!r}: {exc}") from exc
        out.append(
            Output(
                key=_key(item["key"], where),
                label=item["label"],
                formula=item["formula"],
                format=item["format"],
                highlight=item.get("highlight") == "true",
                note=item.get("note", ""),
                ast=ast,
            )
        )
    if not out:
        raise ValueError(f"{slug}: no outputs")
    if sum(o.highlight for o in out) > 1:
        raise ValueError(f"{slug}: at most one output can be highlighted")
    return tuple(out)


def evaluation_order(inputs: tuple[Input, ...], outputs: tuple[Output, ...], slug: str) -> tuple[str, ...]:
    """Output keys so that every output comes after the outputs it uses; rejects duplicates, unknown names, cycles."""
    keys = [i.key for i in inputs] + [o.key for o in outputs]
    dupes = sorted({k for k in keys if keys.count(k) > 1})
    if dupes:
        raise ValueError(f"{slug}: key(s) defined more than once: {dupes}")
    by_key = {o.key: o for o in outputs}
    known = set(keys)
    order: list[str] = []
    state: dict[str, int] = {}

    def visit(key: str, trail: tuple[str, ...]) -> None:
        if state.get(key) == 2:
            return
        if state.get(key) == 1:
            raise ValueError(f"{slug}: outputs depend on each other in a cycle: {' -> '.join((*trail, key))}")
        state[key] = 1
        for dep in sorted(variables(by_key[key].ast)):
            if dep not in known:
                raise ValueError(f"{slug}: output {key!r} uses undefined name {dep!r}")
            if dep in by_key:
                visit(dep, (*trail, key))
        state[key] = 2
        order.append(key)

    for o in outputs:
        visit(o.key, ())
    return tuple(order)


def _table(text: str, slug: str, inputs: tuple[Input, ...], outputs: tuple[Output, ...]) -> Table:
    where = f"{slug} table"
    m = parse_mapping(text, where)
    extra = set(m) - {"title", "input", "values", "relative", "outputs"}
    if extra or not {"title", "input", "outputs"} <= set(m) or ("values" in m) == ("relative" in m):
        raise ValueError(f"{where}: needs title, input, outputs and exactly one of values / relative")
    inp = next((i for i in inputs if i.key == m["input"]), None)
    if inp is None:
        raise ValueError(f"{where}: input {m['input']!r} is not an input")
    cols = tuple(k.strip() for k in m["outputs"].split(",") if k.strip())
    if not 1 <= len(cols) <= 4 or any(k not in {o.key for o in outputs} for k in cols):
        raise ValueError(f"{where}: outputs must be 1-4 output keys")
    nums = tuple(_num(v, where) for v in m.get("values", m.get("relative", "")).split(","))
    if not 2 <= len(nums) <= 9:
        raise ValueError(f"{where}: 2-9 values")
    if "values" in m:
        if any(not inp.min <= v <= inp.max for v in nums):
            raise ValueError(f"{where}: values must lie within the input's min and max")
        return Table(m["title"], inp.key, cols, values=nums)
    return Table(m["title"], inp.key, cols, relative=nums)


def _pairs(text: str, where: str, allow_none: bool) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for part in text.split(","):
        key, sep, val = part.partition("=")
        key, val = key.strip(), val.strip()
        if not sep or not KEY_RE.match(key):
            raise ValueError(f"{where}: expected key=value pairs, got {part!r}")
        if allow_none and val in ("—", "none"):
            out[key] = None
        else:
            out[key] = _num(val, where)
    return out


def _examples(text: str, slug: str, inputs: tuple[Input, ...], outputs: tuple[Output, ...]) -> tuple[Example, ...]:
    out = []
    for n, item in enumerate(parse_items(text, f"{slug} examples"), 1):
        where = f"{slug} examples #{n}"
        _need(item, {"name", "inputs", "expect"}, {"name", "inputs", "expect"}, where)
        given, expect = _pairs(item["inputs"], where, False), _pairs(item["expect"], where, True)
        by_in = {i.key: i for i in inputs}
        for k, v in given.items():
            if k not in by_in or not by_in[k].min <= v <= by_in[k].max:  # type: ignore[operator]
                raise ValueError(f"{where}: input {k!r} unknown or outside its min and max")
        if any(k not in {o.key for o in outputs} for k in expect):
            raise ValueError(f"{where}: expect names a key that is not an output")
        out.append(Example(item["name"], given, expect))  # type: ignore[arg-type]
    if not out:
        raise ValueError(f"{slug}: at least one example is required")
    return tuple(out)


def extract_faq(md_text: str) -> tuple[tuple[str, str], ...]:
    """Questions (### headings) and plain-text answers under a ``## FAQ`` heading."""
    md = seo._markdown()
    tokens = md.parse(md_text)
    faq: list[tuple[str, str]] = []
    in_faq, question, start = False, "", 0

    def flush(end: int) -> None:
        if question:
            rendered = md.renderer.render(tokens[start:end], md.options, {})
            text = re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", rendered))).strip()
            faq.append((question, re.sub(r"\s+([.,;:?!])", r"\1", text)))

    for i, tok in enumerate(tokens):
        if tok.type != "heading_open":
            continue
        flush(i)
        question = ""
        title = tokens[i + 1].content.strip()
        if tok.tag == "h2":
            in_faq = bool(FAQ_TITLE_RE.match(re.sub(r"\s*\{#[a-z0-9-]+\}\s*$", "", title)))
        elif tok.tag == "h3" and in_faq:
            question, start = title, i + 3
    flush(len(tokens))
    return tuple(faq)


def load_calculator(path: Path) -> Calculator:
    meta, rest = seo.parse_front_matter(path.read_text(encoding="utf-8"))
    name = path.name
    allowed = {"slug", "title", "description", "keyword", "template", "industry", "related", "guide", "sample"}
    if set(meta) - allowed:
        raise ValueError(f"{name}: unknown front-matter key(s) {sorted(set(meta) - allowed)}")
    for key in ("slug", "title", "description", "keyword"):
        if not meta.get(key):
            raise ValueError(f"{name}: front matter needs {key!r}")
    slug = meta["slug"]
    if not SLUG_RE.match(slug) or slug.split("/")[2] != path.stem:
        raise ValueError(f"{name}: slug {slug!r} must be /calculators/{path.stem}")
    if not 70 <= len(meta["description"]) <= 200:
        raise ValueError(f"{name}: description must be 70-200 characters")
    template = meta.get("template", "")
    if template and template not in TEMPLATES:
        raise ValueError(f"{name}: unknown template {template!r}")
    sample = None
    if meta.get("sample"):
        sample = parse_description(meta["sample"])
        if sample is None:
            raise ValueError(f"{name}: bad sample description {meta['sample']!r}")
    elif template:
        sample = SampleSpec(key=template)

    blocks: dict[str, str] = {}
    for m in BLOCK_RE.finditer(rest):
        if m.group(1) in blocks:
            raise ValueError(f"{name}: block {m.group(1)!r} given twice")
        blocks[m.group(1)] = m.group(2)
    body_md = BLOCK_RE.sub("", rest)
    for needed in ("inputs", "outputs", "examples"):
        if needed not in blocks:
            raise ValueError(f"{name}: missing ```{needed} block")
    inputs = _inputs(blocks["inputs"], slug)
    outputs = _outputs(blocks["outputs"], slug)
    order = evaluation_order(inputs, outputs, slug)
    table = _table(blocks["table"], slug, inputs, outputs) if "table" in blocks else None
    examples = _examples(blocks["examples"], slug, inputs, outputs)

    body, h1 = seo.render_markdown(body_md)
    if not h1:
        raise ValueError(f"{name}: the body must start with a # heading")
    cut = body.find("<h2")
    if cut < 0:
        raise ValueError(f"{name}: the explanation needs at least one ## section")
    related = tuple(meta.get("related", []))
    guide = meta.get("guide", "")
    industry = meta.get("industry") or (TEMPLATES[template].title if template else "General")
    return Calculator(
        slug=slug,
        title=meta["title"],
        description=meta["description"],
        keyword=meta["keyword"],
        h1=h1,
        intro_html=body[:cut],
        body_html=body[cut:],
        body_md=body_md,
        words=len(re.findall(r"\w+", body_md)),
        template=template,
        industry=industry,
        related=related,
        guide=guide,
        sample=sample,
        inputs=inputs,
        outputs=outputs,
        order=order,
        table=table,
        examples=examples,
        faq=extract_faq(body_md),
        meta=meta,
    )


@lru_cache(maxsize=1)
def calculators() -> dict[str, Calculator]:
    """Every calculator in content/calculators by slug, in file-name order. A broken spec fails loudly."""
    out: dict[str, Calculator] = {}
    for path in sorted(CONTENT.glob("*.md")):
        calc = load_calculator(path)
        if calc.slug in out:
            raise ValueError(f"duplicate slug {calc.slug}")
        out[calc.slug] = calc
    for calc in out.values():
        for rel in calc.related:
            if f"/calculators/{rel}" not in out or f"/calculators/{rel}" == calc.slug:
                raise ValueError(f"{calc.slug}: related calculator {rel!r} does not exist")
        if calc.guide and calc.guide not in seo.pages():
            raise ValueError(f"{calc.slug}: guide {calc.guide!r} does not exist")
    return out


def by_industry() -> list[tuple[str, list[Calculator]]]:
    groups: dict[str, list[Calculator]] = {}
    for calc in calculators().values():
        groups.setdefault(calc.industry, []).append(calc)
    return sorted(groups.items(), key=lambda kv: (kv[0] == "General", kv[0]))


# ---------- copy check ----------

FIGURE_RE = re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)|(\d[\d,]*(?:\.\d+)?)\s?%")
PLACEHOLDER_RE = re.compile(r"\[[A-Z][A-Z_]{2,}\]")


def unsourced_figures(calc: Calculator) -> list[str]:
    """``$`` / ``%`` figures in the explanation that are neither one of the calculator's own numbers (input defaults,
    example inputs and results, the results at the defaults) nor in a sentence with an external link (facts rule)."""
    own: set[float] = {100.0, 0.0}
    for inp in calc.inputs:
        own.add(round(inp.default, 6))
    for ex in calc.examples:
        own |= {round(v, 6) for v in ex.inputs.values()}
        own |= {round(v, 6) for v in ex.expect.values() if v is not None}
    own |= {round(v, 6) for v in calc.compute().values() if v is not None}
    shown: set[str] = set()
    for outs in [calc.compute(), *(calc.compute(ex.inputs) for ex in calc.examples)]:
        shown |= {format_value(outs[o.key], o.format) for o in calc.outputs}
    bad = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", calc.body_md):
        if re.search(r"\]\(https?://", sentence):
            continue
        for m in FIGURE_RE.finditer(sentence):
            raw = (m.group(1) or m.group(2)).replace(",", "")
            if round(float(raw), 6) in own or m.group(0).replace(" ", "") in shown:
                continue
            bad.append(f"{m.group(0)} in: {sentence.strip()[:90]}")
    return bad


# ---------- the model promotion block (shared partial: _model_promo.html) ----------

# Features per tier exactly as the workbook standard (ADR-013, docs/WORKBOOK_STANDARD.md section 1) sets them.
TIER_FEATURES = {
    "light": (
        "Low / Base / High switch on the Dashboard",
        "Break-even sheet: funding need and break-even timing",
        "Inputs and a P&L",
        "Checks sheet",
    ),
    "full": (
        "Everything in Light",
        "Income statement, cash flow and balance sheet, by year and by month",
        "Scenarios sheet: Low, Base and High side by side",
        "Valuation: DCF with a sensitivity table",
        "Sources and uses of cash, KPIs, headcount",
    ),
}


def promo_context(template: str, sample: SampleSpec | None, cfg) -> dict:
    """Data for ``_model_promo.html``: from the template (title, wizard link, sample) and the config (prices)."""
    sample_ok = sample is not None and (ROOT / "samples" / sample.filename).is_file()
    return {
        "template_title": TEMPLATES[template].title if template else "",
        "start_href": f"/start?type={TEMPLATES[template].business_types[0]}" if template else "/start",
        "sample": sample if sample_ok else None,
        "tiers": [
            {"key": k, "name": k.capitalize(), "price": seo._price(cfg.prices[k]), "features": TIER_FEATURES[k]}
            for k in ("light", "full")
        ],
        "price_light": seo._price(cfg.prices["light"]),
        "price_full": seo._price(cfg.prices["full"]),
    }


# ---------- pages ----------


def _json(data) -> Markup:
    return seo._json_script(data)


def structured_data(calc: Calculator, base: str) -> list[dict]:
    url = base + calc.slug
    items = [
        {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": "Calculators", "item": base + "/calculators"},
                {"@type": "ListItem", "position": 3, "name": calc.h1, "item": url},
            ],
        },
        {
            "@context": "https://schema.org",
            "@type": "WebApplication",
            "name": calc.h1,
            "description": calc.description,
            "url": url,
            "applicationCategory": "FinanceApplication",
            "operatingSystem": "Any",
            "browserRequirements": "Requires JavaScript for live results",
            "isAccessibleForFree": True,
            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            "publisher": {"@type": "Organization", "name": "StartupModel", "url": base + "/"},
        },
    ]
    if calc.faq:
        items.append(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in calc.faq
                ],
            }
        )
    return items


def table_view(calc: Calculator) -> dict | None:
    t = calc.table
    if t is None:
        return None
    inp = calc.input(t.input)
    rows = []
    for i, (sv, outs) in enumerate(calc.sweep()):
        base_row = t.relative is not None and t.relative[i] == 0
        rows.append(
            {
                "index": i,
                "sweep": format_value(sv, inp.format),
                "base": base_row,
                "cells": [(k, format_value(outs[k], calc.output(k).format)) for k in t.outputs],
            }
        )
    return {"title": t.title, "input": inp, "columns": [calc.output(k) for k in t.outputs], "rows": rows}


def output_view(calc: Calculator) -> list[dict]:
    res = calc.compute()
    rows = [{"o": o, "text": format_value(res[o.key], o.format)} for o in calc.outputs]
    return sorted(rows, key=lambda r: not r["o"].highlight)  # the highlighted result leads


def sitemap_paths() -> list[str]:
    return ["/calculators", *calculators()]


@router.get("/calculators", response_class=HTMLResponse)
def calculators_index(request: Request) -> HTMLResponse:
    cfg = request.app.state.services.cfg
    return templates.TemplateResponse(
        request,
        "calculator_index.html",
        {
            "title": "Calculators",
            "intro": INTRO,
            "groups": by_industry(),
            "base_url": cfg.public_base_url,
            "support_email": cfg.support_email,
            "price_light": seo._price(cfg.prices["light"]),
        },
    )


@router.get("/calculators/{name}", response_class=HTMLResponse)
def calculator_page(name: str, request: Request) -> HTMLResponse:
    calc = calculators().get(f"/calculators/{name}")
    if calc is None:
        raise HTTPException(404, "not found")
    cfg = request.app.state.services.cfg
    base = cfg.public_base_url
    guide = seo.pages().get(calc.guide) if calc.guide else None
    return templates.TemplateResponse(
        request,
        "calculator_page.html",
        {
            "calc": calc,
            "intro": Markup(calc.intro_html),
            "body": Markup(calc.body_html),
            "outputs": output_view(calc),
            "table": table_view(calc),
            "spec_json": _json(calc.client_spec()),
            "base_url": base,
            "support_email": cfg.support_email,
            "promo": promo_context(calc.template, calc.sample, cfg),
            "related": [calculators()[f"/calculators/{r}"] for r in calc.related],
            "guide": guide,
            "ld_json": [_json(x) for x in structured_data(calc, base)],
        },
    )


def spec_json_text(calc: Calculator) -> str:
    return json.dumps(calc.client_spec(), ensure_ascii=False)
