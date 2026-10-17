"""Names of the downloadable sample workbooks (E13, E16).

A sample is a template's ``sample_stage`` defaults built with fixed options. Its name encodes them:

    <key>-<tier>[-<N>y][-annual]      e.g. cafe-full, cafe-light, cafe-full-5y, saas-full-1y-annual

Defaults are 3 years, monthly. The file lives at ``samples/<name>.xlsx`` and is served at
``/samples/<name>.xlsx``; ``scripts/build_samples.py`` writes it after recalculation and a challenger PASS.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from engine.templates import TEMPLATES

NAME_RE = re.compile(r"^(?P<key>[a-z][a-z_]*)-(?P<tier>full|light)(?:-(?P<years>[135])y)?(?:-(?P<annual>annual))?$")


@dataclass(frozen=True)
class SampleSpec:
    key: str
    tier: str = "full"
    granularity: str = "monthly"
    horizon_years: int = 3

    @property
    def name(self) -> str:
        out = f"{self.key}-{self.tier}"
        if self.horizon_years != 3:
            out += f"-{self.horizon_years}y"
        if self.granularity == "annual":
            out += "-annual"
        return out

    @property
    def filename(self) -> str:
        return f"{self.name}.xlsx"


def parse_name(name: str) -> SampleSpec | None:
    """The spec for a sample name, or None if the name is not a valid sample of a registered template."""
    m = NAME_RE.match(name)
    if not m or m["key"] not in TEMPLATES:
        return None
    spec = SampleSpec(
        key=m["key"],
        tier=m["tier"],
        granularity="annual" if m["annual"] else "monthly",
        horizon_years=int(m["years"] or 3),
    )
    return spec if spec.name == name else None  # one canonical spelling per file (no "-3y")


def parse_description(text: str) -> SampleSpec | None:
    """Spec from a content front-matter description such as ``cafe, light, monthly, 3 years``."""
    parts = [p.strip().lower() for p in text.split(",")]
    if len(parts) != 4:
        return None
    key, tier, gran, horizon = parts
    m = re.fullmatch(r"([135]) years?", horizon)
    if key not in TEMPLATES or tier not in ("full", "light") or gran not in ("monthly", "annual") or not m:
        return None
    return SampleSpec(key=key, tier=tier, granularity=gran, horizon_years=int(m.group(1)))
