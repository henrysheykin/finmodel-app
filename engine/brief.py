"""The validated brief: the only thing an LLM (or the wizard) is allowed to produce.

A brief names a template and gives Low / Base / High values for that template's
drivers. Labels, units, formats, bounds and scenario-ordering rules are NOT in
the brief: they belong to the template (``DriverSpec``), so an LLM cannot change
how a number is presented or bypass a bound. ``validate_for_template`` checks a
brief against its template; ``Brief`` alone checks the shape.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

#: snake_case business-type id; the allowed set comes from the template catalog (engine/templates, ADR-009)
BusinessType = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{1,39}$")]
Goal = Literal["revenue_profit", "startup_breakeven", "dcf_valuation", "investor_pitch", "other"]
Stage = Literal["planning", "early", "growing", "established"]
Tier = Literal["light", "full"]
Granularity = Literal["monthly", "annual"]

KEY_RE = re.compile(r"^[a-z][a-z0-9_]{0,39}$")


class BriefError(ValueError):
    """The brief is well-formed JSON but not acceptable for its template."""


class DriverValue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    low: float
    base: float
    high: float
    note: str | None = Field(default=None, max_length=200)

    @field_validator("key")
    @classmethod
    def _key(cls, v: str) -> str:
        if not KEY_RE.match(v):
            raise ValueError(f"driver key {v!r} must be snake_case, max 40 chars")
        return v


class Role(BaseModel):
    """A headcount line. Its numbers live in drivers ``<key>_fte``, ``<key>_salary``, ``<key>_start``."""

    model_config = ConfigDict(extra="forbid")

    key: str
    title: str = Field(min_length=1, max_length=60)

    @field_validator("key")
    @classmethod
    def _key(cls, v: str) -> str:
        if not KEY_RE.match(v) or len(v) > 24:
            raise ValueError(f"role key {v!r} must be snake_case, max 24 chars")
        return v


class Brief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model_name: str = Field(min_length=1, max_length=80)
    template: str
    business_type: BusinessType
    goal: Goal = "revenue_profit"
    stage: Stage = "planning"
    horizon_years: Literal[1, 3, 5] = 3
    granularity: Granularity = "monthly"
    tier: Tier = "full"
    default_scenario: Literal[1, 2, 3] = 2
    currency: Literal["USD"] = "USD"
    assumption_note: str = Field(default="", max_length=300)
    roles: list[Role] = Field(default_factory=list, max_length=12)
    drivers: list[DriverValue] = Field(min_length=1, max_length=120)

    @field_validator("business_type")
    @classmethod
    def _known_business_type(cls, v: str) -> str:
        from engine.templates import known_business_types  # lazy: the registry imports this module

        known = known_business_types()
        if v not in known:
            raise ValueError(f"unknown business type {v!r}; known: {sorted(known)}")
        return v

    @model_validator(mode="after")
    def _unique(self) -> Brief:
        keys = [d.key for d in self.drivers]
        dupes = sorted({k for k in keys if keys.count(k) > 1})
        if dupes:
            raise ValueError(f"duplicate driver keys: {dupes}")
        rkeys = [r.key for r in self.roles]
        if len(set(rkeys)) != len(rkeys):
            raise ValueError("duplicate role keys")
        return self

    # -- helpers ---------------------------------------------------------
    def values(self, scenario: int) -> dict[str, float]:
        """Driver values for scenario 1 = Low, 2 = Base, 3 = High."""
        attr = {1: "low", 2: "base", 3: "high"}[int(scenario)]
        return {d.key: getattr(d, attr) for d in self.drivers}

    def driver(self, key: str) -> DriverValue:
        for d in self.drivers:
            if d.key == key:
                return d
        raise KeyError(key)

    def with_options(self, **kw) -> Brief:
        """Copy with e.g. tier / granularity / horizon_years changed (re-validated)."""
        return Brief.model_validate({**self.model_dump(), **kw})

    @classmethod
    def load(cls, path: str | Path) -> Brief:
        return cls.model_validate(json.loads(Path(path).read_text(encoding="utf-8")))
