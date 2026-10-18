"""BRIEF_MODEL setting, prompt caching layout and per-order token logging (no network, no LibreOffice)."""

import logging
import subprocess
import sys
from types import SimpleNamespace

import pytest

from adapters.llm import (
    BRIEF_MODELS,
    MIN_CACHEABLE_TOKENS,
    LLMConfigError,
    LLMUsage,
    build_brief_request,
    call_messages,
    validate_brief_model,
)
from app.briefing import Answers, PrefillBriefSource
from app.config import load_settings
from app.db import session_scope
from app.orders import create_order
from tests.conftest import ANSWERS

LONG = "Fixed system instruction for the brief builder. " * 80  # ~3,900 chars ≈ 960 tokens
SHORT = "Fill the brief."


def test_brief_model_default_is_off(monkeypatch):
    """Today no model is in use: unset means the LLM path is off and briefs come from the prefill."""
    monkeypatch.delenv("BRIEF_MODEL", raising=False)
    assert load_settings().brief_model == ""


@pytest.mark.parametrize("model", BRIEF_MODELS)
def test_brief_model_accepts_the_three_ids(monkeypatch, model):
    monkeypatch.setenv("BRIEF_MODEL", model)
    assert load_settings().brief_model == model


@pytest.mark.parametrize("bad", ["claude-sonnet-5", "gpt-5", "opus", "claude-fable-5-1"])
def test_unknown_brief_model_fails_at_start(monkeypatch, bad):
    monkeypatch.setenv("BRIEF_MODEL", bad)
    with pytest.raises(RuntimeError, match="BRIEF_MODEL"):
        load_settings()
    with pytest.raises(LLMConfigError):
        validate_brief_model(bad)


def test_unknown_brief_model_stops_the_container_check(monkeypatch):
    """`python -m app.manage check` is the first line of deploy/start.sh: it must exit non-zero."""
    env = {"BRIEF_MODEL": "claude-nonexistent", "APP_ENV": "dev", "PATH": ""}
    r = subprocess.run([sys.executable, "-m", "app.manage", "check"], env=env, capture_output=True, text=True)
    assert r.returncode != 0 and "BRIEF_MODEL" in r.stderr


@pytest.mark.parametrize("model", BRIEF_MODELS)
def test_fixed_prefix_first_and_cached(model):
    req = build_brief_request(
        model, system_instruction=LONG, template_description="SaaS template drivers…", user_content='{"stage": "early"}'
    )
    assert req["model"] == model
    first, last = req["system"]
    assert first == {"type": "text", "text": LONG}
    assert last["cache_control"] == {"type": "ephemeral"}
    # the per-order part comes after the cached prefix and is never marked
    assert req["messages"] == [{"role": "user", "content": '{"stage": "early"}'}]


def test_short_prefix_is_not_marked_for_cache():
    model = BRIEF_MODELS[0]
    assert len(SHORT) // 4 < MIN_CACHEABLE_TOKENS[model]
    req = build_brief_request(model, system_instruction=SHORT, template_description="x", user_content="{}")
    assert all("cache_control" not in block for block in req["system"])


def test_request_needs_a_model():
    with pytest.raises(LLMConfigError, match="off"):
        build_brief_request("", system_instruction=LONG, template_description="", user_content="{}")


class _FakeClient:
    def __init__(self, usage):
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)
        self._usage = usage

    def _create(self, **kw):
        self.calls.append(kw)
        return SimpleNamespace(usage=SimpleNamespace(**self._usage), content=[])


def test_call_records_usage_and_latency():
    client = _FakeClient(
        dict(input_tokens=120, output_tokens=900, cache_read_input_tokens=1500, cache_creation_input_tokens=0)
    )
    req = build_brief_request("claude-sonnet-5-5", system_instruction=LONG, template_description="", user_content="{}")
    _, usage = call_messages(client, req)
    assert client.calls == [req]
    assert (usage.model, usage.input_tokens, usage.output_tokens, usage.cache_read_input_tokens) == (
        "claude-sonnet-5-5",
        120,
        900,
        1500,
    )
    assert usage.latency_ms >= 0


def test_order_log_has_tokens_and_latency(services, caplog):
    brief = PrefillBriefSource().build_brief(Answers(**ANSWERS))
    usage = LLMUsage("claude-haiku-5-5", 120, 900, 1500, 0, 3456)
    with caplog.at_level(logging.INFO, logger="llm"), session_scope(services.sessions) as s:
        order = create_order(s, services.cfg, "a@example.com", brief, ANSWERS, brief_usage=usage)
        oid = order.id
    line = next(r.getMessage() for r in caplog.records if r.name == "llm")
    assert f"order={oid}" in line
    for part in (
        "model=claude-haiku-5-5",
        "input_tokens=120",
        "output_tokens=900",
        "cache_read_input_tokens=1500",
        "latency_ms=3456",
    ):
        assert part in line


def test_prefill_orders_log_no_llm_usage(services, caplog):
    brief = PrefillBriefSource().build_brief(Answers(**ANSWERS))
    with caplog.at_level(logging.INFO, logger="llm"), session_scope(services.sessions) as s:
        create_order(s, services.cfg, "a@example.com", brief, ANSWERS)
    assert not [r for r in caplog.records if r.name == "llm"]
