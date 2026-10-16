"""Build a model from a brief.

Usage: python -m engine.build brief.json out.xlsx [--tier light|full]
       [--granularity monthly|annual] [--years 1|3|5]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from engine.brief import Brief
from engine.builder import Manifest, build
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
    a = ap.parse_args(argv)
    brief = Brief.load(a.brief)
    opts = {k: v for k, v in (("tier", a.tier), ("granularity", a.granularity), ("horizon_years", a.years)) if v}
    if opts:
        brief = brief.with_options(**opts)
    man = build_model(brief, a.out)
    print(json.dumps({"written": str(a.out), "sheets": man.sheets, "selector": man.selector}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
