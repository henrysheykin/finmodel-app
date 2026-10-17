"""Regenerate the landing page's live sheet preview and the cafe sample from the real engine.

    python scripts/build_landing_data.py

Builds the cafe brief as a Full, monthly, 3-year workbook, recalculates it in LibreOffice once per
scenario and writes:
  - app/data/landing_sheet.json     (numbers and check results quoted on the page)
  - app/data/landing_workbook.json  (every sheet, cell, formula and style for the hero spreadsheet)
  - samples/cafe-full.xlsx       (the downloadable sample, Base case)
tests/test_landing.py checks the JSON against the engine's independent Python model, so the
marketing preview cannot drift from what the product actually builds.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.brief import Brief  # noqa: E402
from engine.build import build_model  # noqa: E402
from engine.recalc import recalc  # noqa: E402
from engine.templates import get_template  # noqa: E402

INPUT_KEYS = ["cust_full", "ticket", "traffic_g", "cogs_pct", "rent", "staff_fte", "staff_salary"]

# The hero shows the whole workbook as a spreadsheet: every sheet, cell, formula and style.
FILL_KINDS = {"1F3864": "t", "2F5597": "s", "FFFF00": "y"}
FONT_KINDS = {"0000FF": "in", "008000": "ln", "6B7280": "mu", "FFFFFF": "wh", "C55A11": "or"}
DEFAULT_ROW_PT = 15.0
DEFAULT_COL_W = 8.43


def _rgb(color) -> str | None:
    rgb = getattr(color, "rgb", None)
    return rgb[-6:].upper() if isinstance(rgb, str) else None


def _style_key(c) -> tuple:
    fill = _rgb(c.fill.fgColor) if c.fill is not None and c.fill.fill_type == "solid" else None
    f = c.font
    return (
        FILL_KINDS.get(fill) if fill else None,
        FONT_KINDS.get(_rgb(f.color)) if f is not None and f.color is not None else None,
        bool(f.bold) if f is not None else False,
        bool(f.italic) if f is not None else False,
        float(f.sz) if f is not None and f.sz and f.name == "Arial" else 10.0,
        c.alignment.horizontal if c.alignment is not None and c.alignment.horizontal != "general" else None,
        getattr(getattr(c.border, "top", None), "style", None),
        getattr(getattr(c.border, "bottom", None), "style", None),
        c.number_format or "General",
    )


def _workbook_preview(wb, values: list) -> dict:
    """Every sheet of the workbook for the hero spreadsheet: sizes, frozen panes, the scenario list and,
    per non-empty or styled cell, [style, value, formula]; a formula's value is [low, base, high] when
    the scenarios differ."""
    styles: list[dict] = []
    style_ids: dict[tuple, int] = {}
    numfmts: list[str] = []
    sheets = []
    for ws in wb.worksheets:
        cells = {}
        first_formula = None
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                key = _style_key(c)
                styled = key[0] or key[6] or key[7]
                if v is None and not styled:
                    continue
                nf = key[8]
                if nf not in numfmts:
                    numfmts.append(nf)
                skey = (*key[:8], numfmts.index(nf))
                if skey not in style_ids:
                    style_ids[skey] = len(styles)
                    fill, color, bold, italic, size, h, bt, bb, nfi = skey
                    styles.append(
                        {
                            k: x
                            for k, x in {
                                "fill": fill,
                                "color": color,
                                "b": bold or None,
                                "i": italic or None,
                                "sz": size if size != 10.0 else None,
                                "h": h,
                                "bt": bt,
                                "bb": bb,
                                "nf": nfi,
                            }.items()
                            if x
                        }
                    )
                entry: list = [style_ids[skey]]
                if isinstance(v, str) and v.startswith("="):
                    first_formula = first_formula or c.coordinate
                    vals = [_clean(wv[ws.title][c.coordinate].value) for wv in values]
                    entry += [vals[0] if vals.count(vals[0]) == 3 else vals, v]
                else:
                    entry.append(_clean(v))
                cells[c.coordinate] = entry
        cols = []
        for ci in range(1, ws.max_column + 1):
            letter = ws.cell(1, ci).column_letter
            dim = ws.column_dimensions.get(letter)
            cols.append(round(dim.width, 2) if dim is not None and dim.width else DEFAULT_COL_W)
        rows = []
        for r in range(1, ws.max_row + 1):
            dim = ws.row_dimensions.get(r)
            rows.append(dim.height if dim is not None and dim.height else DEFAULT_ROW_PT)
        fp = ws.freeze_panes
        freeze = None
        if fp:
            fr = ws[fp]
            freeze = [fr.row - 1, fr.column - 1]
        lists = {}
        for dv in ws.data_validations.dataValidation:
            if dv.type == "list":
                opts = dv.formula1.strip('"').split(",")
                for rng in str(dv.sqref).split():
                    lists[rng] = {"options": opts, "title": dv.promptTitle or "", "prompt": dv.prompt or ""}
        sheets.append(
            {
                "name": ws.title,
                "cols": cols,
                "rows": rows,
                "freeze": freeze,
                "grid": bool(ws.sheet_view.showGridLines),
                "start": "B4" if ws.title == "Dashboard" else (first_formula or "A1"),
                "lists": lists,
                "cells": cells,
            }
        )
    return {"styles": styles, "numfmts": numfmts, "sheets": sheets}


def _workbook_stats(wb_formulas) -> dict:
    n = sum(
        1
        for ws in wb_formulas.worksheets
        for row in ws.iter_rows()
        for c in row
        if isinstance(c.value, str) and c.value.startswith("=")
    )
    return {"sheets": wb_formulas.sheetnames, "formulas": n}


def _clean(v):
    if isinstance(v, float):
        v = round(v, 6)
        return int(v) if v.is_integer() and abs(v) < 1e15 else v
    return v


FORMULA_CELLS = {
    "sum": ("Dashboard", "B8"),
    "inp": ("Inputs", None),  # first formula in the Inputs sheet
    "pl": ("P&L", "B5"),
    "chk": ("Checks", "B16"),
}


def _rows(ws, first: int, last: int, years: int) -> list[dict]:
    out = []
    for r in range(first, last + 1):
        label = ws.cell(r, 1).value
        if not label:
            continue
        vals = [ws.cell(r, 2 + i).value for i in range(years)]
        if all(v is None for v in vals):
            continue
        out.append({"label": str(label), "values": [round(v, 4) if isinstance(v, float) else v for v in vals]})
    return out


def _checks(ws) -> list[dict]:
    out = []
    for r in range(4, ws.max_row + 1):
        label, result, what = (ws.cell(r, c).value for c in (1, 2, 3))
        if label:
            out.append({"label": str(label), "result": str(result), "what": what or ""})
    return out


def main() -> int:
    brief = Brief.load(ROOT / "engine" / "briefs" / "cafe.json").with_options(
        tier="full", granularity="monthly", horizon_years=3
    )
    tpl = get_template(brief.template)
    specs = {s.key: s for s in tpl.all_specs(brief.roles)}
    drivers = {d.key: d for d in brief.drivers}
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "cafe.xlsx"
        build_model(brief, src)
        formulas = load_workbook(src)
        fcells = {}
        for tab, (sheet, cell) in FORMULA_CELLS.items():
            ws = formulas[sheet]
            if cell is None:
                cell = next(
                    c.coordinate
                    for row in ws.iter_rows()
                    for c in row
                    if isinstance(c.value, str) and c.value[:1] == "="
                )
            fcells[tab] = {"cell": f"{sheet}!{cell}", "formula": str(ws[cell].value)}
        stats = _workbook_stats(formulas)
        recalculated = []
        scenarios = {}
        for scen in (1, 2, 3):
            path = Path(tmp) / f"s{scen}.xlsx"
            shutil.copy(src, path)
            wb = load_workbook(path)
            wb["Dashboard"]["B4"] = scen
            wb.save(path)
            res = recalc(path, 120)
            if res.errors:
                raise SystemExit(f"scenario {scen}: formula errors {res.errors}")
            wv = load_workbook(path, data_only=True)
            scenarios[str(scen)] = {
                "summary": _rows(wv["Dashboard"], 8, 14, brief.horizon_years),
                "pl": _rows(wv["P&L"], 5, 22, brief.horizon_years),
                "checks": _checks(wv["Checks"]),
                "formula_errors": len(res.errors),
            }
            recalculated.append(wv)
            if scen == 2:
                (ROOT / "samples").mkdir(exist_ok=True)
                shutil.copy(path, ROOT / "samples" / "cafe-full.xlsx")
    data = {
        "title": "Neighborhood cafe, three-year plan",
        "template": brief.template,
        "years": brief.horizon_years,
        "inputs": [
            {
                "key": k,
                "label": specs[k].label,
                "unit": specs[k].unit,
                "fmt": specs[k].fmt,
                "values": [drivers[k].low, drivers[k].base, drivers[k].high],
            }
            for k in INPUT_KEYS
        ],
        "formulas": fcells,
        "file": "neighborhood-cafe-plan.xlsx",
        "stats": stats,
        "scenarios": scenarios,
    }
    preview = _workbook_preview(formulas, recalculated)
    preview["file"] = data["file"]
    wb_out = ROOT / "app" / "data" / "landing_workbook.json"
    wb_out.write_text(json.dumps(preview, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    out = ROOT / "app" / "data" / "landing_sheet.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)} and samples/cafe-full.xlsx")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
