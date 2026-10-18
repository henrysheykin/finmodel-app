"""Claude API plumbing for the brief builder (E08): model choice, prompt caching, usage logging.

Nothing here calls the network by itself. ``build_brief_request`` returns the keyword arguments for
``client.messages.create``; ``call_messages`` times one call on any client with that method (the
Anthropic SDK in production, a fake in tests) and returns the response with its token usage.

Model choice (``BRIEF_MODEL``): unset = the LLM path is off and briefs come from the deterministic
prefill (``app.briefing.PrefillBriefSource``), which is how the product works today. Which model
becomes the default is decided by the brief-model eval (BACKLOG E23), not here.
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass
from typing import Any

log = logging.getLogger("llm")

#: the only values BRIEF_MODEL accepts; anything else stops the app at start (app.config.Settings.check)
BRIEF_MODELS: tuple[str, ...] = ("claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5")

#: Minimum cacheable prompt length per model, in tokens. Source: Anthropic prompt-caching docs
#: (https://platform.claude.com/docs/en/build-with-claude/prompt-caching), checked 2026-10-18:
#: 512 tokens for Haiku 5.5, Sonnet 5.5 and Opus 5.5. A shorter prefix is simply not cached by the
#: API (no error), but we do not mark it at all so the request says what actually happens.
MIN_CACHEABLE_TOKENS: dict[str, int] = {m: 512 for m in BRIEF_MODELS}

#: rough characters per token for English prompt text; used only to decide whether the fixed prefix
#: is long enough to be worth a cache breakpoint (a slight over-estimate of tokens is harmless)
CHARS_PER_TOKEN = 4


class LLMConfigError(ValueError):
    pass


def validate_brief_model(value: str) -> str:
    """Return the configured model id, or "" when the LLM path is off. Unknown ids raise: no silent
    fallback to another model."""
    v = (value or "").strip()
    if v and v not in BRIEF_MODELS:
        raise LLMConfigError(f"BRIEF_MODEL={v!r} is not one of {', '.join(BRIEF_MODELS)} (or empty = LLM off)")
    return v


def estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN


def cacheable(model: str, prefix: str) -> bool:
    """True when the fixed prompt prefix reaches the model's minimum cacheable length."""
    return estimate_tokens(prefix) >= MIN_CACHEABLE_TOKENS[model]


def build_brief_request(
    model: str,
    *,
    system_instruction: str,
    template_description: str,
    user_content: str,
    max_tokens: int = 4096,
    **extra: Any,
) -> dict[str, Any]:
    """Keyword arguments for ``messages.create``.

    The fixed part (system instruction + the industry template's description) goes first, in
    ``system``, so every order for the same template shares one cached prefix; the customer's
    answers (the only part that changes per order) go in the user message after it. The last
    fixed block carries ``cache_control`` only when the prefix reaches the model's minimum
    cacheable length (``MIN_CACHEABLE_TOKENS``); below it the API would not cache anyway.
    """
    validate_brief_model(model)
    if not model:
        raise LLMConfigError("BRIEF_MODEL is not set: the LLM brief path is off")
    template_block: dict[str, Any] = {"type": "text", "text": template_description}
    if cacheable(model, system_instruction + template_description):
        template_block["cache_control"] = {"type": "ephemeral"}
    return {
        "model": model,
        "max_tokens": max_tokens,
        "system": [{"type": "text", "text": system_instruction}, template_block],
        "messages": [{"role": "user", "content": user_content}],
        **extra,
    }


@dataclass(frozen=True)
class LLMUsage:
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_input_tokens: int
    cache_creation_input_tokens: int
    latency_ms: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _field(usage: Any, name: str) -> int:
    v = usage.get(name) if isinstance(usage, dict) else getattr(usage, name, 0)
    return int(v or 0)


def usage_from_response(response: Any, model: str, latency_ms: int) -> LLMUsage:
    usage = response.get("usage", {}) if isinstance(response, dict) else getattr(response, "usage", None) or {}
    return LLMUsage(
        model=model,
        input_tokens=_field(usage, "input_tokens"),
        output_tokens=_field(usage, "output_tokens"),
        cache_read_input_tokens=_field(usage, "cache_read_input_tokens"),
        cache_creation_input_tokens=_field(usage, "cache_creation_input_tokens"),
        latency_ms=latency_ms,
    )


def call_messages(client: Any, request: dict[str, Any]) -> tuple[Any, LLMUsage]:
    """One ``messages.create`` call, timed, with its token usage."""
    t0 = time.monotonic()
    response = client.messages.create(**request)
    latency_ms = int((time.monotonic() - t0) * 1000)
    return response, usage_from_response(response, request["model"], latency_ms)


def log_brief_usage(order_id: str, usage: LLMUsage) -> None:
    """One line per order in the app log (Railway log view), searchable by ``brief_llm order=<id>``."""
    log.info(
        "brief_llm order=%s model=%s input_tokens=%d output_tokens=%d cache_read_input_tokens=%d"
        " cache_creation_input_tokens=%d latency_ms=%d",
        order_id,
        usage.model,
        usage.input_tokens,
        usage.output_tokens,
        usage.cache_read_input_tokens,
        usage.cache_creation_input_tokens,
        usage.latency_ms,
    )


__all__ = [
    "BRIEF_MODELS",
    "MIN_CACHEABLE_TOKENS",
    "LLMConfigError",
    "LLMUsage",
    "build_brief_request",
    "cacheable",
    "call_messages",
    "log_brief_usage",
    "usage_from_response",
    "validate_brief_model",
]
