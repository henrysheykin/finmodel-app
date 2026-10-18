"""Wizard answers → validated Brief.

``PrefillBriefSource`` needs no LLM: it starts from the template's stage defaults and
overrides the drivers the customer typed in the wizard's "key numbers" step.
``LLMBriefSource`` (E08, on when ``BRIEF_MODEL`` is set) starts from that same prefill brief and lets
the model tailor the drivers to the customer's notes (``engine.brief_builder``); if the model gives no
valid brief, the prefill brief is used. Whatever produces the brief, the template's own validation is
the gate.
"""

from __future__ import annotations

import logging
from typing import Any, Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field

from adapters.llm import LLMUsage
from engine.brief import Brief, BriefError, BusinessType, Goal, Stage
from engine.brief_builder import BriefBuildError, CustomerInput
from engine.brief_builder import build_brief as llm_build_brief
from engine.goals import apply_goal
from engine.templates import get_template, template_for_business_type

#: wizard business type → template key, from the template catalog (ADR-009)
TEMPLATE_FOR: dict[str, str] = template_for_business_type()


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


log = logging.getLogger("briefing")


class BriefSource(Protocol):
    def build_brief(self, answers: Answers) -> Brief: ...


def build_with_usage(source: BriefSource, answers: Answers) -> tuple[Brief, LLMUsage | None]:
    """The brief plus the LLM token usage behind it (None when no model was called)."""
    fn = getattr(source, "build_brief_with_usage", None)
    if fn is not None:
        return fn(answers)
    return source.build_brief(answers), None


def supported_business_types() -> list[str]:
    return sorted(TEMPLATE_FOR)


class PrefillBriefSource:
    """Stage defaults + key numbers. Deterministic, no network."""

    def build_brief(self, answers: Answers) -> Brief:
        key = TEMPLATE_FOR.get(answers.business_type)
        if key is None:
            raise BriefError(f"business type {answers.business_type!r} is not available yet")
        tpl = get_template(key)
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
        brief = apply_goal(Brief.model_validate(data))
        tpl.validate(brief)
        return brief

    def build_brief_with_usage(self, answers: Answers) -> tuple[Brief, LLMUsage | None]:
        return self.build_brief(answers), None


def make_brief_source(brief_model: str, api_key: str) -> BriefSource:
    """Prefill when ``BRIEF_MODEL`` is empty, otherwise the LLM source on the Claude API."""
    if not brief_model:
        return PrefillBriefSource()
    from adapters.llm import AnthropicHTTPClient

    return LLMBriefSource(AnthropicHTTPClient(api_key), brief_model)


class LLMBriefSource:
    """Prefill brief tailored by a Claude model; falls back to the prefill brief if the model fails.

    Answers the prefill rejects (unknown business type, out-of-range key numbers) are rejected here too,
    before any API call.
    """

    def __init__(self, client: Any, model: str, prefill: PrefillBriefSource | None = None) -> None:
        self.client = client
        self.model = model
        self.prefill = prefill or PrefillBriefSource()

    def build_brief_with_usage(self, answers: Answers) -> tuple[Brief, LLMUsage | None]:
        start = self.prefill.build_brief(answers)
        inp = CustomerInput(business_name=answers.business_name, notes=answers.notes, locked=set(answers.key_numbers))
        try:
            res = llm_build_brief(self.client, self.model, start, inp)
        except BriefBuildError as exc:
            log.warning("brief_llm fallback to prefill (%s): %s", start.template, exc)
            return start, exc.usage
        return res.brief, res.usage

    def build_brief(self, answers: Answers) -> Brief:
        return self.build_brief_with_usage(answers)[0]
