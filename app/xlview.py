"""The landing page's spreadsheet: the real cafe workbook rendered the way a spreadsheet app shows it.

`app/data/landing_workbook.json` (written by scripts/build_landing_data.py) holds every sheet of the
built workbook: column widths, row heights, frozen panes, the scenario list on Dashboard!B4 and, per
cell, its style, formula and value in each scenario. This module formats values with the workbook's
own number formats and renders the first sheet on the server; web/static/landing.js renders the same
markup in the browser (tests/test_browser_landing.py checks that both agree).
"""

from __future__ import annotations

import hashlib
import json
import re
from decimal import ROUND_HALF_UP, Decimal
from functools import cache
from pathlib import Path

from markupsafe import Markup, escape

DATA = Path(__file__).resolve().parent / "data" / "landing_workbook.json"

ROW_HEAD_PX = 34
COL_HEAD_PX = 20
DEFAULT_COL_PX = 64
#: blank columns and rows are added so the sheet fills the window like a real spreadsheet does
MIN_GRID_PX = 1600
EXTRA_ROWS = 10
MIN_ROWS = 32


@cache
def workbook() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


@cache
def workbook_version() -> str:
    return hashlib.sha256(DATA.read_bytes()).hexdigest()[:10]


def sheet(name: str) -> dict:
    return next(s for s in workbook()["sheets"] if s["name"] == name)


# ---------- addresses ----------


def col_letter(n: int) -> str:
    """1 -> A, 27 -> AA."""
    s = ""
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def col_px(width: float) -> int:
    """Excel column width (characters of the default font) to pixels at 100% zoom."""
    return int(width * 7 + 5)


def row_px(points: float) -> int:
    return round(points * 4 / 3)


# ---------- number formats ----------


def _split_sections(fmt: str) -> list[str]:
    out, cur, quoted, esc = [], "", False, False
    for ch in fmt:
        if esc:
            cur += "\\" + ch
            esc = False
        elif ch == "\\":
            esc = True
        elif ch == '"':
            quoted = not quoted
            cur += ch
        elif ch == ";" and not quoted:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def _parse_section(sec: str) -> tuple[str, str, int, bool, bool, bool]:
    """(prefix, suffix, decimals, thousands, percent, has_digits) of one number-format section."""
    tokens: list[tuple[str, str]] = []
    i = 0
    while i < len(sec):
        ch = sec[i]
        if ch == '"':
            j = sec.find('"', i + 1)
            j = len(sec) if j < 0 else j
            tokens.append(("lit", sec[i + 1 : j]))
            i = j + 1
        elif ch == "\\":
            tokens.append(("lit", sec[i + 1 : i + 2]))
            i += 2
        elif ch in "0#,.":
            tokens.append(("ph", ch))
            i += 1
        else:
            tokens.append(("lit", ch))
            i += 1
    run = "".join(x for k, x in tokens if k == "ph")
    first = next((n for n, (k, _) in enumerate(tokens) if k == "ph"), len(tokens))
    prefix = "".join(x for k, x in tokens[:first] if k == "lit")
    suffix = "".join(x for k, x in tokens[first:] if k == "lit")
    decimals = len(re.sub(r"[^0#]", "", run.split(".", 1)[1])) if "." in run else 0
    return prefix, suffix, decimals, "," in run, "%" in prefix + suffix, bool(run)


def _fixed(x: float, decimals: int, thousands: bool) -> str:
    """Round half away from zero on the exact binary value (what Number.prototype.toFixed does)."""
    q = Decimal(1).scaleb(-decimals)
    s = f"{Decimal(x).quantize(q, rounding=ROUND_HALF_UP):f}"
    if thousands:
        whole, _, frac = s.partition(".")
        whole = f"{int(whole):,}"
        s = whole + ("." + frac if frac else "")
    return s


def _general(v: float) -> str:
    if float(v).is_integer() and abs(v) < 1e11:
        return str(int(v))
    s = f"{v:.10g}"
    return s


def format_value(v, fmt: str) -> tuple[str, str]:
    """(text, kind) as the spreadsheet shows the value; kind is n(umber), s(tring), b(ool) or e(mpty)."""
    if v is None or v == "":
        return "", "e"
    if isinstance(v, bool):
        return ("TRUE" if v else "FALSE"), "b"
    if isinstance(v, str):
        return v, "s"
    if fmt in ("General", "@"):
        return _general(v), "n"
    sections = _split_sections(fmt)
    if v < 0 and len(sections) > 1:
        sec, x, sign = sections[1], -v, ""
    elif abs(v) < 1e-9 and len(sections) > 2:
        sec, x, sign = sections[2], 0.0, ""
    else:
        sec, x, sign = sections[0], abs(v), "-" if v < 0 else ""
    before, after, decimals, thousands, percent, digits = _parse_section(sec)
    if not digits:
        return before + after, "n"
    if percent:
        x *= 100
    return sign + before + _fixed(x, decimals, thousands) + after, "n"


# ---------- cells ----------


def cell_value(entry: list, case: int):
    v = entry[1] if len(entry) > 1 else None
    return v[case - 1] if isinstance(v, list) else v


def style_classes(style: dict) -> list[str]:
    cls = []
    if style.get("fill"):
        cls.append("f" + style["fill"])
    if style.get("color"):
        cls.append("k-" + style["color"])
    if style.get("b"):
        cls.append("b")
    if style.get("i"):
        cls.append("i")
    if style.get("sz"):
        cls.append(f"z{int(style['sz'])}")
    if style.get("bt"):
        cls.append("bt")
    if style.get("bb"):
        cls.append("bbd" if style["bb"] == "double" else "bb")
    return cls


def cell_view(sh: dict, address: str, case: int = 2) -> dict:
    """Text, classes and formula of one cell, as both renderers show it."""
    wb = workbook()
    entry = sh["cells"].get(address)
    if entry is None:
        return {"a": address, "text": "", "kind": "e", "cls": "c e", "f": None}
    style = wb["styles"][entry[0]]
    text, kind = format_value(cell_value(entry, case), wb["numfmts"][style.get("nf", 0)])
    cls = ["c", *style_classes(style)]
    h = style.get("h")
    if h in ("left", "center", "right"):
        cls.append("h" + h[0])
    elif kind == "n":
        cls.append("hr")
    elif kind == "b":
        cls.append("hc")
    if kind == "e":
        cls.append("e")
    return {"a": address, "text": text, "kind": kind, "cls": " ".join(cls), "f": entry[2] if len(entry) > 2 else None}


def layout(sh: dict) -> tuple[list[int], list[int]]:
    """Pixel sizes of the sheet's columns and rows, padded with blank ones to fill the window."""
    cols = [col_px(w) for w in sh["cols"]]
    while sum(cols) < MIN_GRID_PX or len(cols) < len(sh["cols"]) + 2:
        cols.append(DEFAULT_COL_PX)
    rows = [row_px(p) for p in sh["rows"]]
    while len(rows) < max(MIN_ROWS, len(sh["rows"]) + EXTRA_ROWS):
        rows.append(20)
    return cols, rows


def grid_template(sh: dict) -> tuple[str, str]:
    cols, rows = layout(sh)
    return (
        f"{ROW_HEAD_PX}px " + " ".join(f"{c}px" for c in cols),
        f"{COL_HEAD_PX}px " + " ".join(f"{r}px" for r in rows),
    )


def render_grid(name: str, case: int = 2, active: str | None = None) -> Markup:
    """Server-rendered grid of one sheet (the browser re-renders it identically and adds frozen panes,
    overflowing text and the selection)."""
    sh = sheet(name)
    active = active or sh["start"]
    cols, rows = layout(sh)
    out = ['<div role="row" class="xr">', '<span class="hd hd--corner" aria-hidden="true"></span>']
    for ci in range(1, len(cols) + 1):
        L = col_letter(ci)
        on = " on" if L == re.sub(r"\d", "", active) else ""
        out.append(f'<span role="columnheader" class="hd{on}" data-col="{ci}">{L}</span>')
    out.append("</div>")
    act_row = int(re.sub(r"\D", "", active))
    for ri in range(1, len(rows) + 1):
        on = " on" if ri == act_row else ""
        out.append(f'<div role="row" class="xr"><span role="rowheader" class="rh{on}" data-row="{ri}">{ri}</span>')
        for ci in range(1, len(cols) + 1):
            a = f"{col_letter(ci)}{ri}"
            cv = cell_view(sh, a, case)
            sel = " act" if a == active else ""
            out.append(
                f'<span role="gridcell" id="xc-{a}" class="{cv["cls"]}{sel}" data-r="{ri}" data-c="{ci}">'
                f"{escape(cv['text'])}</span>"
            )
        out.append("</div>")
    return Markup("".join(out))
