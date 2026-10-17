"""Build a model from a brief.

Usage: python -m engine.build brief.json out.xlsx [--tier light|full]
       [--granularity monthly|annual] [--years 1|3|5] [--goal GOAL] [--recalc]
       python -m engine.build default:saas:early out.xlsx ...   (template stage defaults)
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.brief import Brief
from engine.builder import Manifest, build
from engine.goals import apply_goal
from engine.templates import get_template


def build_model(brief: Brief, out_path: str | Path) -> Manifest:
    return build(brief, get_template(brief.template), out_path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("out")
    ap.add_argument("--tier", choices=["light", "full"])
    ap.add_argument("--granularity", choices=["monthly", "annual"])
    ap.add_argument("--years", type=int, choices=[1, 3, 5])
    ap.add_argument("--goal", choices=["revenue_profit", "startup_breakeven", "dcf_valuation", "investor_pitch"])
    ap.add_argument("--recalc", action="store_true", help="recalculate in LibreOffice so values show on open")
    a = ap.parse_args(argv)
    if a.brief.startswith("default:"):
        _, tkey, stage = a.brief.split(":")
        brief = get_template(tkey).default_brief(stage)
    else:
        brief = Brief.load(a.brief)
    opts = {k: v for k, v in (("tier", a.tier), ("granularity", a.granularity), ("horizon_years", a.years)) if v}
    if opts:
        brief = brief.with_options(**opts)
    if a.goal:
        brief = apply_goal(brief, a.goal)
    man = build_model(brief, a.out)
    if a.recalc:
        from engine.recalc import recalc

        res = recalc(a.out)
        if not res.ok:
            raise SystemExit(f"recalc found errors: {res.errors}")
    print(json.dumps({"written": str(a.out), "sheets": man.sheets, "selector": man.selector}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
