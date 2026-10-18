"""OpenAI API plumbing for the brief builder (E08, ADR-012): model choice, prompt caching, usage logging.

``build_brief_request`` returns the JSON body for the Responses API (``POST /v1/responses``);
``call_responses`` times one call on any client with ``responses.create`` (``OpenAIHTTPClient`` in
production, a fake in tests) and returns the response with its token usage. Only ``OpenAIHTTPClient``
touches the network.

Why the Responses API and not Chat Completions: on the gpt-6 models Chat Completions allows function
calling only with reasoning off, and gpt-6-astra cannot turn reasoning off (model pages on
developers.openai.com, checked 2026-10-18).

Model choice (``BRIEF_MODEL``): unset = the LLM path is off and briefs come from the deterministic
prefill (``app.briefing.PrefillBriefSource``), which is how the product works today. Which model
becomes the default is decided by the brief-model eval (BACKLOG E23), not here.
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass
from typing import Any

import httpx

log = logging.getLogger("llm")

#: the only values BRIEF_MODEL accepts; anything else stops the app at start (app.config.Settings.check).
#: Ids checked on developers.openai.com/api/docs/models on 2026-10-18; all three support function calling
#: and structured outputs on the Responses API.
BRIEF_MODELS: tuple[str, ...] = ("gpt-6-luna", "gpt-6.1-sol", "gpt-6-astra")

#: Reasoning effort for every brief call. "low" is accepted by all three models (gpt-6-astra has no
#: "none") and keeps the answer inside the builder's 15 s deadline; the task is filling numbers, not
#: open-ended reasoning. The E23 eval measures pass share and latency at this setting.
REASONING_EFFORT = "low"

#: Prompt caching is automatic on these models (no request flag); a prefix shorter than this many
#: tokens is not cached. Source: developers.openai.com/api/docs/guides/prompt-caching, 2026-10-18.
MIN_CACHEABLE_TOKENS = 1024

#: rough characters per token for English prompt text (only for the estimate below)
CHARS_PER_TOKEN = 4


class LLMConfigError(ValueError):
    pass


class LLMTransportError(RuntimeError):
    """The API call itself failed (network, timeout, HTTP error). Never carries the API key.

    ``retryable`` is False for errors a retry cannot fix: every 4xx except 429 (bad request, bad key,
    unknown model, no quota)."""

    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


def validate_brief_model(value: str) -> str:
    """Return the configured model id, or "" when the LLM path is off. Unknown ids raise: no silent
    fallback to another model."""
    v = (value or "").strip()
    if v and v not in BRIEF_MODELS:
        raise LLMConfigError(f"BRIEF_MODEL={v!r} is not one of {', '.join(BRIEF_MODELS)} (or empty = LLM off)")
    return v


def estimate_tokens(text: str) -> int:
    return len(text) // CHARS_PER_TOKEN


def cacheable(prefix: str) -> bool:
    """True when the fixed prompt prefix is long enough for the API's automatic cache."""
    return estimate_tokens(prefix) >= MIN_CACHEABLE_TOKENS


def build_brief_request(
    model: str,
    *,
    system_instruction: str,
    template_description: str,
    user_content: str,
    max_tokens: int = 4096,
    cache_key: str = "",
    **extra: Any,
) -> dict[str, Any]:
    """JSON body for ``responses.create``.

    The fixed part (system instruction + the industry template's description) goes first, in
    ``instructions``, so every order for the same template shares one cached prefix (caching is
    automatic); the customer's answers (the only part that changes per order) go in the user input
    after it. ``cache_key`` (e.g. the template key) becomes ``prompt_cache_key``, which keeps orders of
    one template on the same cache.

    ``store`` is false: OpenAI keeps no copy of the conversation for later retrieval. Reasoning items
    then come back encrypted (``include``) so a correction round can send them back with the error.
    """
    validate_brief_model(model)
    if not model:
        raise LLMConfigError("BRIEF_MODEL is not set: the LLM brief path is off")
    request: dict[str, Any] = {
        "model": model,
        "instructions": f"{system_instruction.rstrip()}\n\n{template_description}",
        "input": [{"role": "user", "content": user_content}],
        "max_output_tokens": max_tokens,
        "reasoning": {"effort": REASONING_EFFORT},
        "store": False,
        "include": ["reasoning.encrypted_content"],
    }
    if cache_key:
        request["prompt_cache_key"] = cache_key
    request.update(extra)
    return request


@dataclass(frozen=True)
class LLMUsage:
    """Token usage of one or more calls. ``input_tokens`` are the uncached input tokens only; each input
    token is billed at exactly one rate (uncached, cached read or cache write), so the three add up to
    the API's total input. ``output_tokens`` include reasoning tokens (billed as output)."""

    model: str
    input_tokens: int
    output_tokens: int
    cached_input_tokens: int
    cache_write_tokens: int
    latency_ms: int
    #: API calls behind these numbers (1 + retries); usage of all of them is summed
    calls: int = 1

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def __add__(self, other: LLMUsage) -> LLMUsage:
        return LLMUsage(
            model=self.model,
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cached_input_tokens=self.cached_input_tokens + other.cached_input_tokens,
            cache_write_tokens=self.cache_write_tokens + other.cache_write_tokens,
            latency_ms=self.latency_ms + other.latency_ms,
            calls=self.calls + other.calls,
        )


def _get(obj: Any, name: str) -> Any:
    return obj.get(name) if isinstance(obj, dict) else getattr(obj, name, None)


def _int(obj: Any, name: str) -> int:
    return int(_get(obj, name) or 0) if obj is not None else 0


def usage_from_response(response: Any, model: str, latency_ms: int) -> LLMUsage:
    """Responses API ``usage``: ``input_tokens`` is the total input, of which
    ``input_tokens_details.cached_tokens`` were read from and ``cache_write_tokens`` written to the cache."""
    usage = _get(response, "usage") or {}
    details = _get(usage, "input_tokens_details") or {}
    total_in = _int(usage, "input_tokens")
    cached = _int(details, "cached_tokens")
    written = _int(details, "cache_write_tokens")
    return LLMUsage(
        model=model,
        input_tokens=max(total_in - cached - written, 0),
        output_tokens=_int(usage, "output_tokens"),
        cached_input_tokens=cached,
        cache_write_tokens=written,
        latency_ms=latency_ms,
    )


def call_responses(client: Any, request: dict[str, Any]) -> tuple[Any, LLMUsage]:
    """One ``responses.create`` call, timed, with its token usage."""
    t0 = time.monotonic()
    response = client.responses.create(**request)
    latency_ms = int((time.monotonic() - t0) * 1000)
    return response, usage_from_response(response, request["model"], latency_ms)


def log_brief_usage(order_id: str, usage: LLMUsage) -> None:
    """One line per order in the app log (Railway log view), searchable by ``brief_llm order=<id>``."""
    log.info(
        "brief_llm order=%s model=%s input_tokens=%d output_tokens=%d cached_input_tokens=%d"
        " cache_write_tokens=%d latency_ms=%d calls=%d",
        order_id,
        usage.model,
        usage.input_tokens,
        usage.output_tokens,
        usage.cached_input_tokens,
        usage.cache_write_tokens,
        usage.latency_ms,
        usage.calls,
    )


#: Responses API endpoint
OPENAI_URL = "https://api.openai.com/v1/responses"


class _Responses:
    def __init__(self, owner: OpenAIHTTPClient) -> None:
        self._owner = owner

    def create(self, **request: Any) -> dict[str, Any]:
        return self._owner.post(request)


class OpenAIHTTPClient:
    """Minimal Responses API client over httpx (already a dependency; no SDK), shaped like the SDK:
    ``client.responses.create(**request)`` returns the response JSON as a dict.

    No retries here: the brief builder owns the retry budget. Errors become ``LLMTransportError``
    with the HTTP status and the API's error type/code only (never the request headers).
    """

    def __init__(self, api_key: str, *, timeout: float = 12.0, transport: httpx.BaseTransport | None = None) -> None:
        if not api_key:
            raise LLMConfigError("OPENAI_API_KEY is not set")
        self._http = httpx.Client(
            timeout=timeout,
            transport=transport,
            headers={"authorization": f"Bearer {api_key}", "content-type": "application/json"},
        )
        self.responses = _Responses(self)

    def post(self, request: dict[str, Any]) -> dict[str, Any]:
        try:
            r = self._http.post(OPENAI_URL, json=request)
        except httpx.HTTPError as exc:
            raise LLMTransportError(f"OpenAI API unreachable: {type(exc).__name__}") from None
        if r.status_code != 200:
            try:
                err = r.json().get("error") or {}
                kind = str(err.get("code") or err.get("type") or "")[:60]
            except (ValueError, AttributeError):
                kind = ""
            # 429 is a rate limit (retry) unless the account is out of quota (a retry cannot fix that)
            retryable = (r.status_code == 429 and kind != "insufficient_quota") or r.status_code >= 500
            raise LLMTransportError(f"OpenAI API HTTP {r.status_code} {kind}".strip(), retryable=retryable)
        try:
            return r.json()
        except ValueError:
            raise LLMTransportError("OpenAI API returned a non-JSON body") from None


__all__ = [
    "BRIEF_MODELS",
    "MIN_CACHEABLE_TOKENS",
    "REASONING_EFFORT",
    "LLMConfigError",
    "LLMTransportError",
    "LLMUsage",
    "OpenAIHTTPClient",
    "build_brief_request",
    "cacheable",
    "call_responses",
    "log_brief_usage",
    "usage_from_response",
    "validate_brief_model",
]
