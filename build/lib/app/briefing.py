"""Wizard answers → validated Brief.

``PrefillBriefSource`` needs no LLM: it starts from the template's stage defaults and
overrides the drivers the customer typed in the wizard's "key numbers" step. E08 adds an
LLM-backed source behind the same ``BriefSource`` interface; whatever produces the brief,
the template's own validation is the gate.
"""

from __future__ import annotations

from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from engine.brief import Brief, BriefError, BusinessType, Goal, Stage
from engine.templates import get_template

#: wizard business type → template key (real estate / other arrive with E05 and later)
TEMPLATE_FOR: dict[str, str] = {
    "saas": "saas",
    "restaurant_cafe": "cafe",
    "retail_ecommerce": "retail",
    "professional_services": "services",
}


class Answers(BaseModel):
    """What the wizard collects (docs/research/draftplan.md flow)."""

    model_config = ConfigDict(extra="forbid")

    business_type: BusinessType
    goal: Goal = "revenue_profit"
    stage: Stage = "planning"
    horizon_years: Literal[1, 3, 5] = 3
    granularity: Literal["monthly", "annual"] = "monthly"
    tier: Literal["light", "full"] = "full"
    business_name: str = Field(default="", max_length=60)
    #: driver key → Base value typed by the customer; Low/High keep the default spread
    key_numbers: dict[str, float] = Field(default_factory=dict, max_length=30)
    notes: str = Field(default="", max_length=2000)


class BriefSource(Protocol):
    def build_brief(self, answers: Answers) -> Brief: ...


def supported_business_types() -> list[str]:
    return sorted(TEMPLATE_FOR)


class PrefillBriefSource:
    """Stage defaults + key numbers. Deterministic, no network."""

    def build_brief(self, answers: Answers) -> Brief:
        key = TEMPLATE_FOR.get(answers.business_type)
        if key is None:
            raise BriefError(f"business type {answers.business_type!r} is not available yet")
        tpl = get_template(key)
        if key == "cafe":
            from pathlib import Path

            base = Brief.load(Path(__file__).resolve().parents[1] / "engine" / "briefs" / "cafe.json")
        else:
            base = tpl.default_brief(answers.stage)
        data = base.model_dump()
        known = {d["key"]: d for d in data["drivers"]}
        unknown = sorted(set(answers.key_numbers) - set(known))
        if unknown:
            raise BriefError(f"unknown key numbers for {key}: {unknown}")
        for k, v in answers.key_numbers.items():
            d = known[k]
            b = d["base"]
            if b:
                d.update(low=d["low"] / b * v, base=v, high=d["high"] / b * v)
            else:
                d.update(low=v, base=v, high=v)
            d["note"] = "Your number (Base); Low / High keep the default spread."
        name = answers.business_name.strip() or tpl.title
        data.update(
            model_name=f"{name} — financial model"[:80],
            goal=answers.goal,
            stage=answers.stage,
            horizon_years=answers.horizon_years,
            granularity=answers.granularity,
            tier=answers.tier,
        )
        brief = Brief.model_validate(data)
        tpl.validate(brief)
        return brief
