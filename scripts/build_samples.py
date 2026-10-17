"""Build the downloadable sample workbooks from the template catalog.

    python scripts/build_samples.py            # <key>-full for every template with a sample_title
    python scripts/build_samples.py fitness    # one template (<key>-full)
    python scripts/build_samples.py cafe-light cafe-full-5y   # named samples (engine/samples.py grammar)
    python scripts/build_samples.py --seo      # every sample the content/seo pages offer (E16)
    python scripts/build_samples.py --goal investor_pitch cafe   # goal-module review file (E07)

Each sample is the template's ``sample_stage`` defaults built with the options its name encodes
(default: Full, monthly, 3 years), recalculated in LibreOffice and checked by the challenger. A sample
that fails is not written. Output: samples/<name>.xlsx, served at /samples/<name>.xlsx (the landing
page links to /samples/<key>.xlsx, an alias of <key>-full).
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
from engine.samples import SampleSpec, parse_name  # noqa: E402
from engine.templates import TEMPLATES  # noqa: E402


def build_sample(key: str, goal: str = "", spec: SampleSpec | None = None) -> Path:
    spec = spec or SampleSpec(key=key)
    tpl = TEMPLATES[spec.key]
    brief = tpl.default_brief(tpl.sample_stage).with_options(
        tier=spec.tier, granularity=spec.granularity, horizon_years=spec.horizon_years
    )
    if goal:
        brief = apply_goal(brief.with_options(horizon_years=5), goal)
    out = ROOT / "samples" / (f"{spec.key}-{goal}.xlsx" if goal else spec.filename)
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / out.name
        build_model(brief, path)
        report = challenge(brief, path)
        if not report["verdict"].startswith("PASS"):
            raise SystemExit(f"{out.name}: challenger {report['verdict']}: {report['problems'][:3]}")
        res = recalc(path, 120)  # leave cached values in the file so it opens with numbers everywhere
        if res.errors:
            raise SystemExit(f"{out.name}: formula errors {res.errors}")
        out.parent.mkdir(exist_ok=True)
        shutil.copy(path, out)
    return out


def seo_samples() -> list[SampleSpec]:
    from app.seo import pages  # imported late: the app is not needed for plain sample builds

    seen: dict[str, SampleSpec] = {}
    for page in pages().values():
        if page.sample:
            seen.setdefault(page.sample.name, page.sample)
    return list(seen.values())


def main(argv: list[str]) -> int:
    goal = ""
    if argv[:1] == ["--goal"]:
        goal, argv = argv[1], argv[2:]
    if argv == ["--seo"]:
        specs = seo_samples()
    else:
        specs = []
        for arg in argv or [k for k, t in TEMPLATES.items() if t.sample_title]:
            spec = SampleSpec(key=arg) if arg in TEMPLATES else parse_name(arg)
            if spec is None:
                raise SystemExit(f"unknown template or sample name {arg!r}; templates: {sorted(TEMPLATES)}")
            specs.append(spec)
    for spec in specs:
        print("wrote", build_sample(spec.key, goal, spec).relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
