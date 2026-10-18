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
    cacheable,
    call_responses,
    usage_from_response,
    validate_brief_model,
)
from app.briefing import Answers, PrefillBriefSource
from app.config import load_settings
from app.db import session_scope
from app.orders import create_order
from tests.conftest import ANSWERS

LONG = "Fixed system instruction for the brief builder. " * 90  # ~4,400 chars ≈ 1,100 tokens
SHORT = "Fill the brief."


def test_brief_model_default_is_off(monkeypatch):
    """Today no model is in use: unset means the LLM path is off and briefs come from the prefill."""
    monkeypatch.delenv("BRIEF_MODEL", raising=False)
    assert load_settings().brief_model == ""


@pytest.mark.parametrize("model", BRIEF_MODELS)
def test_brief_model_accepts_the_three_ids(monkeypatch, model):
    monkeypatch.setenv("BRIEF_MODEL", model)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-real")
    assert load_settings().brief_model == model


@pytest.mark.parametrize("bad", ["claude-sonnet-5-5", "gpt-5", "gpt-6", "gpt-6-luna-mini", "GPT-6-LUNA"])
def test_unknown_brief_model_fails_at_start(monkeypatch, bad):
    monkeypatch.setenv("BRIEF_MODEL", bad)
    with pytest.raises(RuntimeError, match="BRIEF_MODEL"):
        load_settings()
    with pytest.raises(LLMConfigError):
        validate_brief_model(bad)


def test_unknown_brief_model_stops_the_container_check(monkeypatch):
    """`python -m app.manage check` is the first line of deploy/start.sh: it must exit non-zero."""
    env = {"BRIEF_MODEL": "gpt-nonexistent", "APP_ENV": "dev", "PATH": ""}
    r = subprocess.run([sys.executable, "-m", "app.manage", "check"], env=env, capture_output=True, text=True)
    assert r.returncode != 0 and "BRIEF_MODEL" in r.stderr


def test_brief_model_without_key_fails_at_start(monkeypatch):
    monkeypatch.setenv("BRIEF_MODEL", BRIEF_MODELS[0])
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        load_settings()


@pytest.mark.parametrize("model", BRIEF_MODELS)
def test_fixed_prefix_first_then_the_order(model):
    req = build_brief_request(
        model,
        system_instruction=LONG,
        template_description="SaaS template drivers…",
        user_content='{"stage": "early"}',
        cache_key="brief-saas",
    )
    assert req["model"] == model
    # the fixed, cacheable part is the whole of `instructions`, the same for every order of a template
    assert req["instructions"].startswith(LONG.rstrip()) and req["instructions"].endswith("SaaS template drivers…")
    assert req["prompt_cache_key"] == "brief-saas"
    # the per-order part comes after the prefix
    assert req["input"] == [{"role": "user", "content": '{"stage": "early"}'}]
    # nothing kept by OpenAI; reasoning comes back encrypted so a correction round can send it back
    assert req["store"] is False and req["include"] == ["reasoning.encrypted_content"]
    assert req["reasoning"] == {"effort": "low"} and req["max_output_tokens"] == 4096


def test_prefix_length_against_the_cache_minimum():
    assert cacheable(LONG) and not cacheable(SHORT)
    assert MIN_CACHEABLE_TOKENS == 1024
    req = build_brief_request(BRIEF_MODELS[0], system_instruction=SHORT, template_description="x", user_content="{}")
    assert "prompt_cache_key" not in req  # no key given, none sent


def test_request_needs_a_model():
    with pytest.raises(LLMConfigError, match="off"):
        build_brief_request("", system_instruction=LONG, template_description="", user_content="{}")


class _FakeClient:
    def __init__(self, usage):
        self.calls = []
        self.responses = SimpleNamespace(create=self._create)
        self._usage = usage

    def _create(self, **kw):
        self.calls.append(kw)
        return {"output": [], "usage": self._usage}


def test_call_records_usage_and_latency():
    client = _FakeClient(
        {
            "input_tokens": 1720,
            "input_tokens_details": {"cached_tokens": 1500, "cache_write_tokens": 100},
            "output_tokens": 900,
            "output_tokens_details": {"reasoning_tokens": 300},
        }
    )
    req = build_brief_request("gpt-6.1-sol", system_instruction=LONG, template_description="", user_content="{}")
    _, usage = call_responses(client, req)
    assert client.calls == [req]
    # the API's input_tokens is the total; each token is billed at one rate, so the parts add up to it
    assert (usage.model, usage.input_tokens, usage.cached_input_tokens, usage.cache_write_tokens) == (
        "gpt-6.1-sol",
        120,
        1500,
        100,
    )
    assert usage.output_tokens == 900  # reasoning tokens are part of output (billed as output)
    assert usage.latency_ms >= 0


def test_usage_without_details_or_usage():
    u = usage_from_response({"usage": {"input_tokens": 50, "output_tokens": 7}}, "gpt-6-luna", 1)
    assert (u.input_tokens, u.cached_input_tokens, u.cache_write_tokens, u.output_tokens) == (50, 0, 0, 7)
    u = usage_from_response({"output": []}, "gpt-6-luna", 1)
    assert (u.input_tokens, u.output_tokens) == (0, 0)
    # inconsistent numbers never give a negative uncached count
    u = usage_from_response({"usage": {"input_tokens": 10, "input_tokens_details": {"cached_tokens": 20}}}, "m", 1)
    assert u.input_tokens == 0


def test_order_log_has_tokens_and_latency(services, caplog):
    brief = PrefillBriefSource().build_brief(Answers(**ANSWERS))
    usage = LLMUsage("gpt-6-luna", 120, 900, 1500, 40, 3456)
    with caplog.at_level(logging.INFO, logger="llm"), session_scope(services.sessions) as s:
        order = create_order(s, services.cfg, "a@example.com", brief, ANSWERS, brief_usage=usage)
        oid = order.id
    line = next(r.getMessage() for r in caplog.records if r.name == "llm")
    assert f"order={oid}" in line
    for part in (
        "model=gpt-6-luna",
        "input_tokens=120",
        "output_tokens=900",
        "cached_input_tokens=1500",
        "cache_write_tokens=40",
        "latency_ms=3456",
    ):
        assert part in line


def test_prefill_orders_log_no_llm_usage(services, caplog):
    brief = PrefillBriefSource().build_brief(Answers(**ANSWERS))
    with caplog.at_level(logging.INFO, logger="llm"), session_scope(services.sessions) as s:
        create_order(s, services.cfg, "a@example.com", brief, ANSWERS)
    assert not [r for r in caplog.records if r.name == "llm"]
