"""Build the downloadable sample workbooks from the template catalog.

    python scripts/build_samples.py            # every template with a sample_title
    python scripts/build_samples.py fitness    # one template
    python scripts/build_samples.py --goal investor_pitch cafe   # goal-module review file (E07)

Each sample is the template's ``sample_stage`` defaults as a Full, monthly, 3-year workbook,
recalculated in LibreOffice and checked by the challenger. A sample that fails is not written.
Output: samples/<key>-full.xlsx (served at /samples/<key>.xlsx and listed on the landing page).
With ``--goal``: samples/<key>-<goal>.xlsx with the goal modules (for review; not served).
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engine.build import build_model  # noqa: E402
from engine.challenger import challenge  # noqa: E402
from engine.goals import apply_goal  # noqa: E402
from engine.recalc import recalc  # noqa: E402
from engine.templates import TEMPLATES  # noqa: E402


def build_sample(key: str, goal: str = "") -> Path:
    tpl = TEMPLATES[key]
    brief = tpl.default_brief(tpl.sample_stage).with_options(tier="full", granularity="monthly", horizon_years=3)
    if goal:
        brief = apply_goal(brief.with_options(horizon_years=5), goal)
    out = ROOT / "samples" / f"{key}-{goal or 'full'}.xlsx"
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / out.name
        build_model(brief, path)
        report = challenge(brief, path)
        if not report["verdict"].startswith("PASS"):
            raise SystemExit(f"{key}: challenger {report['verdict']}: {report['problems'][:3]}")
        res = recalc(path, 120)  # leave cached values in the file so it opens with numbers everywhere
        if res.errors:
            raise SystemExit(f"{key}: formula errors {res.errors}")
        out.parent.mkdir(exist_ok=True)
        shutil.copy(path, out)
    return out


def main(argv: list[str]) -> int:
    goal = ""
    if argv[:1] == ["--goal"]:
        goal, argv = argv[1], argv[2:]
    keys = argv or [k for k, t in TEMPLATES.items() if t.sample_title]
    for key in keys:
        if key not in TEMPLATES:
            raise SystemExit(f"unknown template {key!r}; known: {sorted(TEMPLATES)}")
        print("wrote", build_sample(key, goal).relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
