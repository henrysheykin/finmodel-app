"""SEO pages (E16): content/seo/*.md rendered at their front-matter slug with a shared layout.

Each page gets canonical and Open Graph tags, JSON-LD (breadcrumbs plus Article for guides or Product for
model pages), a call to action that opens the wizard on the page's template, the page's sample workbook
(built by the engine: ``python scripts/build_samples.py --seo``) and links to related pages. Pages are
listed in the sitemap, on the /models and /guides indexes and in llms.txt.

Markdown is rendered with markdown-it (CommonMark + tables, raw HTML disabled). ``{#id}`` at the end of
a heading sets its anchor; other headings get a slug of their text.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from markdown_it import MarkdownIt
from markupsafe import Markup

from app.web import templates
from engine.samples import SampleSpec, parse_description
from engine.templates import TEMPLATES

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content" / "seo"

SECTIONS = {
    "models": ("Financial models", "Custom Excel financial models by industry and purpose, built on your numbers."),
    "guides": ("Guides", "Practical guides to building and checking financial projections."),
}
SLUG_RE = re.compile(r"^/(models|guides)/[a-z0-9]+(?:-[a-z0-9]+)*$")
ATTR_ID_RE = re.compile(r"\s*\{#([a-z0-9][a-z0-9-]*)\}\s*$")

router = APIRouter()


@dataclass(frozen=True)
class SeoPage:
    slug: str
    title: str
    description: str
    keyword: str
    h1: str
    body: str  # rendered HTML
    words: int
    template: str = ""  # template key from the catalog, "" for "any"
    sample: SampleSpec | None = None
    meta: dict = field(default_factory=dict)

    @property
    def section(self) -> str:
        return self.slug.split("/")[1]

    @property
    def name(self) -> str:
        return self.slug.split("/")[2]


def parse_front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError("missing front matter")
    meta: dict = {}
    for line in m.group(1).splitlines():
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"bad front-matter line: {line!r}")
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            meta[key.strip()] = [v.strip() for v in value[1:-1].split(",") if v.strip()]
        else:
            meta[key.strip()] = value
    return meta, text[m.end() :]


def page_sample(meta: dict) -> SampleSpec | None:
    """``sample: cafe, full, monthly, 3 years`` or ``template: any (sample: cafe, full, monthly, 3 years)``."""
    text = meta.get("sample") or ""
    if not text:
        m = re.search(r"\(sample:\s*([^)]*)\)", meta.get("template", ""))
        text = m.group(1) if m else ""
    if not text:
        return None
    spec = parse_description(text)
    if spec is None:
        raise ValueError(f"bad sample description {text!r}")
    return spec


def page_template(meta: dict) -> str:
    first = re.split(r"[\s(,]", meta.get("template", "").strip(), maxsplit=1)[0]
    return first if first in TEMPLATES else ""


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def _markdown() -> MarkdownIt:
    return MarkdownIt("commonmark", {"html": False, "typographer": False}).enable("table")


def render_markdown(md_text: str) -> tuple[str, str]:
    """(HTML, h1 text). Headings get ids; tables get a focusable scroll wrapper for narrow screens."""
    md = _markdown()
    tokens = md.parse(md_text)
    used: set[str] = set()
    h1 = ""
    for i, tok in enumerate(tokens):
        if tok.type != "heading_open":
            continue
        inline = tokens[i + 1]
        explicit = ""
        last = inline.children[-1] if inline.children else None
        if last is not None and last.type == "text":
            m = ATTR_ID_RE.search(last.content)
            if m:
                explicit = m.group(1)
                last.content = last.content[: m.start()]
                inline.content = ATTR_ID_RE.sub("", inline.content)
        text = "".join(c.content for c in inline.children or [] if c.type in ("text", "code_inline"))
        if tok.tag == "h1":
            h1 = h1 or text
            continue
        anchor = explicit or slugify(text) or f"section-{i}"
        base, n = anchor, 2
        while anchor in used:
            anchor, n = f"{base}-{n}", n + 1
        used.add(anchor)
        tok.attrSet("id", anchor)
    html = md.renderer.render(tokens, md.options, {})
    html = html.replace("<table>", '<div class="table-wrap" role="region" aria-label="Table" tabindex="0"><table>')
    html = html.replace("</table>", "</table></div>")
    return html, h1


def load_page(path: Path) -> SeoPage:
    meta, body_md = parse_front_matter(path.read_text(encoding="utf-8"))
    for key in ("slug", "title", "description", "keyword"):
        if not meta.get(key):
            raise ValueError(f"{path.name}: front matter needs {key!r}")
    if not SLUG_RE.match(meta["slug"]):
        raise ValueError(f"{path.name}: slug {meta['slug']!r} must be /models/<name> or /guides/<name>")
    body, h1 = render_markdown(body_md)
    if not h1:
        raise ValueError(f"{path.name}: the body must start with a # heading")
    return SeoPage(
        slug=meta["slug"],
        title=meta["title"],
        description=meta["description"],
        keyword=meta["keyword"],
        h1=h1,
        body=body,
        words=len(re.findall(r"\w+", body_md)),
        template=page_template(meta),
        sample=page_sample(meta),
        meta=meta,
    )


@lru_cache(maxsize=1)
def pages() -> dict[str, SeoPage]:
    """Every page in content/seo by slug, in file-name order. A broken page fails loudly at startup/tests."""
    out: dict[str, SeoPage] = {}
    for path in sorted(CONTENT.glob("*.md")):
        page = load_page(path)
        if page.slug in out:
            raise ValueError(f"duplicate slug {page.slug}")
        out[page.slug] = page
    return out


def sample_path(spec: SampleSpec) -> Path:
    return ROOT / "samples" / spec.filename


def related(page: SeoPage, limit: int = 4) -> list[SeoPage]:
    """Pages on the same template first, then the hub, then the other section, then the rest."""
    others = [p for p in pages().values() if p.slug != page.slug]

    def rank(p: SeoPage) -> tuple[int, str]:
        if page.template and p.template == page.template:
            r = 0
        elif p.slug == "/models/custom-financial-model":
            r = 1
        elif p.section != page.section:
            r = 2
        else:
            r = 3
        return r, p.slug

    return sorted(others, key=rank)[:limit]


def _json_script(data) -> Markup:
    s = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return Markup(s.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026"))


def structured_data(page: SeoPage, base: str, prices: dict[str, int]) -> list[dict]:
    url = base + page.slug
    section_title = SECTIONS[page.section][0]
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": base + "/"},
            {"@type": "ListItem", "position": 2, "name": section_title, "item": f"{base}/{page.section}"},
            {"@type": "ListItem", "position": 3, "name": page.h1, "item": url},
        ],
    }
    publisher = {"@type": "Organization", "name": "StartupModel", "url": base + "/"}
    if page.section == "guides":
        main = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page.h1,
            "description": page.description,
            "mainEntityOfPage": url,
            "author": publisher,
            "publisher": publisher,
        }
    else:
        main = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": page.h1,
            "description": page.description,
            "url": url,
            "brand": {"@type": "Brand", "name": "StartupModel"},
            "offers": [
                {
                    "@type": "Offer",
                    "name": name,
                    "price": f"{prices[tier] / 100:.2f}",
                    "priceCurrency": "USD",
                    "url": f"{base}/start?plan={tier}",
                }
                for tier, name in (("light", "Light"), ("full", "Full"))
            ],
        }
    return [crumbs, main]


def _price(cents: int) -> str:
    return f"${cents / 100:,.0f}"


def start_link(page: SeoPage) -> str:
    if page.template:
        return f"/start?type={TEMPLATES[page.template].business_types[0]}"
    return "/start"


def _seo_page(request: Request, section: str, name: str) -> HTMLResponse:
    page = pages().get(f"/{section}/{name}")
    if page is None:
        raise HTTPException(404, "not found")
    cfg = request.app.state.services.cfg
    base = cfg.public_base_url
    sample = page.sample if page.sample and sample_path(page.sample).is_file() else None
    return templates.TemplateResponse(
        request,
        "seo_page.html",
        {
            "page": page,
            "body": Markup(page.body),
            "section_title": SECTIONS[section][0],
            "base_url": base,
            "support_email": cfg.support_email,
            "price_light": _price(cfg.prices["light"]),
            "price_full": _price(cfg.prices["full"]),
            "start_href": start_link(page),
            "template_title": TEMPLATES[page.template].title if page.template else "",
            "sample": sample,
            "related": related(page),
            "ld_json": [_json_script(x) for x in structured_data(page, base, cfg.prices)],
        },
    )


def _index(request: Request, section: str) -> HTMLResponse:
    cfg = request.app.state.services.cfg
    title, intro = SECTIONS[section]
    return templates.TemplateResponse(
        request,
        "seo_index.html",
        {
            "section": section,
            "title": title,
            "intro": intro,
            "items": [p for p in pages().values() if p.section == section],
            "other": next(s for s in SECTIONS if s != section),
            "other_title": SECTIONS[next(s for s in SECTIONS if s != section)][0],
            "base_url": cfg.public_base_url,
            "support_email": cfg.support_email,
            "price_light": _price(cfg.prices["light"]),
        },
    )


@router.get("/models", response_class=HTMLResponse)
def models_index(request: Request) -> HTMLResponse:
    return _index(request, "models")


@router.get("/guides", response_class=HTMLResponse)
def guides_index(request: Request) -> HTMLResponse:
    return _index(request, "guides")


@router.get("/models/{name}", response_class=HTMLResponse)
def model_page(name: str, request: Request) -> HTMLResponse:
    return _seo_page(request, "models", name)


@router.get("/guides/{name}", response_class=HTMLResponse)
def guide_page(name: str, request: Request) -> HTMLResponse:
    return _seo_page(request, "guides", name)


def sitemap_paths() -> list[str]:
    return [f"/{s}" for s in SECTIONS] + list(pages())
