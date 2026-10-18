"""E23 brief-model eval harness: cases, cost / statistics math, recommendation rule, replay on fixtures.

No live API anywhere. Tests that build real workbooks need LibreOffice (``libreoffice`` marker); the rest
inject fake build / check functions.
"""

import json
from decimal import Decimal
from pathlib import Path

import pytest

from app.briefing import Answers, PrefillBriefSource
from engine.templates import get_template
from evals import brief_model_eval as ev
from evals.brief_model_eval import CallUsage, CaseResult

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "brief_eval"
H, S, OP = ev.DEFAULT_MODELS
INDUSTRIES = ["cafe", "saas", "retail", "services", "home_services", "fitness"]


def case(cid: str) -> dict:
    industry, n = cid.rsplit("-", 1)
    return json.loads((ROOT / "evals" / "cases" / industry / f"{n}.json").read_text(encoding="utf-8"))


FIXTURE_CASES = ["cafe-01", "saas-05", "home_services-07"]


def ok_generate(brief, path):
    path.write_bytes(b"x")


def ok_check(brief, path):
    return {"verdict": "PASS"}


# --------------------------------------------------------------------------- committed cases
def test_sixty_cases_six_industries_ten_each():
    cases = ev.load_cases()
    assert len(cases) == 60
    for ind in INDUSTRIES:
        files = sorted((ROOT / "evals" / "cases" / ind).glob("*.json"))
        assert [f.stem for f in files] == [f"{i:02d}" for i in range(1, 11)], ind
    assert len({c["id"] for c in cases}) == 60


@pytest.mark.parametrize("c", ev.load_cases(), ids=lambda c: c["id"])
def test_case_gives_a_valid_prefill_brief_for_its_template(c):
    answers = Answers(**c["answers"])  # extra="forbid": exactly the wizard shape
    assert answers.notes.strip(), "notes are required, otherwise the builder makes no call"
    assert c["id"].startswith(c["industry"])
    _, start, inp = ev.prefill_for(c)
    get_template(start.template).validate(start)
    assert start.template == c["industry"]
    assert start == PrefillBriefSource().build_brief(answers)
    assert inp.locked == set(answers.key_numbers)


def test_cases_are_varied_and_include_the_hard_ones():
    cases = ev.load_cases()
    a = [c["answers"] for c in cases]
    assert {x["stage"] for x in a} == {"planning", "early", "growing", "established"}
    assert {x["horizon_years"] for x in a} == {1, 3, 5}
    assert {x["granularity"] for x in a} == {"monthly", "annual"}
    assert {x["tier"] for x in a} == {"light", "full"}
    assert len({x["goal"] for x in a}) >= 4
    assert sum(bool(x["key_numbers"]) for x in a) >= 18
    assert any(len(x["notes"]) > 700 for x in a) and any(len(x["notes"]) < 140 for x in a)
    tags = [t for c in cases for t in c["tags"]]
    for t in ("impossible-numbers", "foreign-language", "injection", "formula-like"):
        assert tags.count(t) >= 6, t
    assert any("=HYPERLINK" in x["notes"] for x in a)


def test_case_files_match_the_generator():
    from evals import make_cases

    for ind, cases in make_cases.build().items():
        for c in cases:
            f = ROOT / "evals" / "cases" / ind / f"{c['id'].rsplit('-', 1)[1]}.json"
            assert json.loads(f.read_text(encoding="utf-8")) == c


# --------------------------------------------------------------------------- cost and statistics
def test_cost_exact_standard_rates():
    # 1000 in, 3000 cache write, 2000 cache read, 500 out on haiku:
    # 1000*0.10 + 3000*0.125 + 2000*0.01 + 500*0.50 = 745 micro-dollars
    c = CallUsage(input_tokens=1000, output_tokens=500, cache_read=2000, cache_write=3000)
    assert ev.cost_usd(H, [c]) == Decimal("0.000745")
    # sonnet: 1000*2 + 3000*2.5 + 2000*0.1 + 500*10 = 14700
    assert ev.cost_usd(S, [c]) == Decimal("0.0147")
    # opus: 1000*4 + 3000*5 + 2000*0.2 + 500*20 = 29400
    assert ev.cost_usd(OP, [c]) == Decimal("0.0294")


def test_cost_sums_over_retries():
    a = CallUsage(2000, 300, 0, 1500)
    b = CallUsage(2400, 320, 1500, 0)
    assert ev.cost_usd(OP, [a, b]) == ev.cost_usd(OP, [a]) + ev.cost_usd(OP, [b])
    assert ev.cost_usd(OP, []) == 0


def test_haiku_long_prompt_surcharge_is_per_request():
    # total input 90,000 + 5,000 + 10,000 = 105,000 > 100,000: long rates 0.50 / 0.625 / 0.05 / 2.50
    long_call = CallUsage(input_tokens=90_000, output_tokens=1000, cache_read=10_000, cache_write=5_000)
    # by hand, in micro-dollars: 45,000 + 3,125 + 500 + 2,500 = 51,125
    assert ev.cost_usd(H, [long_call]) == Decimal("0.051125")
    # exactly 100,000 is not surcharged
    edge = CallUsage(input_tokens=100_000, output_tokens=0)
    assert ev.cost_usd(H, [edge]) == Decimal("0.01")
    assert ev.cost_usd(H, [CallUsage(input_tokens=100_001)]) == Decimal("100001") * Decimal("0.5") / 1_000_000
    # a short retry next to a long first request keeps the standard rate
    short = CallUsage(input_tokens=3000, output_tokens=200)
    assert ev.cost_usd(H, [long_call, short]) == Decimal("0.051125") + ev.cost_usd(H, [short])
    assert ev.cost_usd(H, [short]) == Decimal("0.0004")
    # sonnet and opus have no long-prompt rate in the price table
    assert ev.cost_usd(S, [long_call]) == Decimal(90_000 * 2 + 5_000 * 2.5 + 10_000 * 0.1 + 1000 * 10) / 1_000_000


def test_price_table_is_complete():
    assert set(ev.PRICES_PER_MTOK) == set(ev.DEFAULT_MODELS)
    for p in ev.PRICES_PER_MTOK.values():
        assert {"input", "cache_write", "cache_read", "output"} <= set(p)


def test_percentile95_nearest_rank():
    assert ev.percentile95([]) == 0.0
    assert ev.percentile95([3.0]) == 3.0
    xs = [float(i) for i in range(1, 101)]
    assert ev.percentile95(xs) == 95.0
    assert ev.percentile95(list(reversed(xs))) == 95.0
    assert ev.percentile95([float(i) for i in range(1, 61)]) == 57.0  # ceil(0.95 * 60) = 57th value
    assert ev.percentile95([1.0, 2.0, 100.0]) == 100.0  # ceil(2.85) = 3


def _res(model, passed, latency_ms, *, cid="x-01", calls=None):
    calls = calls if calls is not None else [CallUsage(1000, 100, 0, 0, latency_ms)]
    return CaseResult(cid, "x", model, passed, "ok" if passed else "bad", "done", calls)


def test_summarize_pass_share_latency_cost_calls():
    results = [
        _res(S, True, 2000, calls=[CallUsage(1000, 100, 0, 0, 1500), CallUsage(1000, 100, 0, 0, 500)]),
        _res(S, True, 4000),
        _res(S, False, 6000),
        _res(S, True, 8000),
    ]
    s = ev.summarize(results)[S]
    assert (s["cases"], s["passed"], s["pass_share"]) == (4, 3, 0.75)
    assert s["mean_s"] == pytest.approx((2 + 4 + 6 + 8) / 4)
    assert s["p95_s"] == 8.0
    assert s["mean_calls"] == pytest.approx(5 / 4)
    one = ev.cost_usd(S, [CallUsage(1000, 100)])
    assert s["mean_cost_usd"] == (one * 5) / 4


# --------------------------------------------------------------------------- recommendation
def _s(pass_share, p95, cost):
    return {"cases": 60, "passed": round(pass_share * 60), "pass_share": pass_share, "mean_s": p95 / 2, "p95_s": p95,
            "mean_cost_usd": Decimal(str(cost)), "mean_calls": 1.0}  # fmt: skip


def test_recommend_cheapest_qualifying():
    summary = {H: _s(0.95, 6, 0.0009), S: _s(0.97, 9, 0.011), OP: _s(0.95, 12, 0.02)}
    r = ev.recommend(summary)
    assert r["model"] == H  # haiku equals the reference pass share and is cheapest
    summary[H] = _s(0.95, 6, 0.03)
    assert ev.recommend(summary)["model"] == S  # now sonnet is cheaper than haiku and opus


def test_recommend_excludes_slow_models():
    summary = {H: _s(0.97, 15.1, 0.0009), S: _s(0.97, 15.0, 0.011), OP: _s(0.95, 12, 0.02)}
    assert ev.recommend(summary)["model"] == S  # p95 15.0 is allowed, 15.1 is not


def test_recommend_excludes_below_reference():
    summary = {H: _s(0.90, 5, 0.0009), S: _s(0.93, 8, 0.011), OP: _s(0.95, 12, 0.02)}
    assert ev.recommend(summary)["model"] == OP


def test_recommend_none_when_nobody_qualifies():
    summary = {H: _s(0.80, 5, 0.0009), S: _s(0.90, 8, 0.011), OP: _s(0.97, 16.5, 0.02)}
    r = ev.recommend(summary)
    assert r["model"] is None and "no model" in r["reason"]


def test_recommend_needs_the_reference_model():
    r = ev.recommend({H: _s(0.9, 5, 0.001)})
    assert r["model"] is None and "reference" in r["reason"]


# --------------------------------------------------------------------------- replay on fixtures
def _replay(cids, models=ev.DEFAULT_MODELS, **kw):
    return ev.run_eval(
        [case(c) for c in cids], list(models), make_client=ev.replay_client_factory(FIXTURES), **kw
    )  # fmt: skip


def by(results):
    return {(r.model, r.case_id): r for r in results}


def test_replay_pass_fallback_retry_and_transport_error():
    r = by(_replay(FIXTURE_CASES, generate=ok_generate, check=ok_check))
    assert len(r) == 9
    # plain pass: one call, usage and latency from the recording
    p = r[(S, "cafe-01")]
    assert p.passed and len(p.calls) == 1 and p.latency_s == 2.4
    assert p.calls[0] == CallUsage(2100, 380, 0, 1700, 2400)
    # one retry: the first answer breaks the bounds, the second is accepted; usage and latency are summed
    q = r[(H, "saas-05")]
    assert q.passed and len(q.calls) == 2
    assert q.latency_s == pytest.approx(1.8)
    assert sum(c.input_tokens + c.cache_read for c in q.calls) == 2300 + 1800 + 2700 + 1800
    # a retryable transport error counts as a call, with its wall time but no tokens
    t = r[(OP, "saas-05")]
    assert t.passed and len(t.calls) == 2 and t.calls[0].total_input == 0
    assert t.latency_s == pytest.approx(0.3 + 4.6)
    # all retries invalid: the production path would fall back to the prefill brief -> not a pass
    f = r[(H, "home_services-07")]
    assert not f.passed and f.stage == "builder" and "fallback to prefill" in f.reason and len(f.calls) == 3
    assert f.cost > 0  # failed orders still cost money


def test_replay_summary_and_recommendation():
    results = _replay(FIXTURE_CASES, generate=ok_generate, check=ok_check)
    s = ev.summarize(results)
    assert s[H]["passed"] == 2 and s[S]["passed"] == 3 and s[OP]["passed"] == 3
    assert ev.recommend(s)["model"] == S  # haiku misses the reference pass share, sonnet is cheaper than opus
    assert "| claude-sonnet-5-5 | 100% (3/3) |" in ev.results_table(s)


def test_challenger_failure_is_a_fail_with_reason():
    from worker.pipeline import BuildRejected

    def bad_check(brief, path):
        raise BuildRejected("challenger: scenario 1: in-file checks 'FAIL'")

    r = ev.run_eval([case("cafe-01")], [S], make_client=ev.replay_client_factory(FIXTURES), generate=ok_generate,
                    check=bad_check)[0]  # fmt: skip
    assert not r.passed and r.stage == "check" and "in-file checks" in r.reason


def test_build_error_is_a_fail():
    from worker.pipeline import BuildRejected

    def bad_generate(brief, path):
        raise BuildRejected("formula errors after recalculation: {'Sheet': ['#DIV/0!']}")

    r = ev.run_eval([case("cafe-01")], [S], make_client=ev.replay_client_factory(FIXTURES), generate=bad_generate,
                    check=ok_check)[0]  # fmt: skip
    assert not r.passed and r.stage == "build"


def test_missing_recording_is_a_fail_not_a_crash():
    r = _replay(["cafe-02"], [S], generate=ok_generate, check=ok_check)[0]
    assert not r.passed and r.stage == "recorded" and "no recording" in r.reason


def test_case_without_notes_is_rejected():
    c = case("cafe-01")
    c["answers"]["notes"] = "   "
    with pytest.raises(ValueError, match="notes are required"):
        ev.run_case(c, S, ev.ReplayClient([]))


def test_record_then_replay_roundtrip(tmp_path):
    src = ev.replay_client_factory(FIXTURES)
    first = ev.run_eval(
        [case(c) for c in FIXTURE_CASES], [H, OP], make_client=src, record_dir=tmp_path / "rec",
        generate=ok_generate, check=ok_check,
    )  # fmt: skip
    files = sorted((tmp_path / "rec").rglob("*.json"))
    assert len(files) == 6
    text = "".join(f.read_text() for f in files).lower()
    assert "x-api-key" not in text and "anthropic-version" not in text and "authorization" not in text
    second = ev.run_eval(
        [case(c) for c in FIXTURE_CASES], [H, OP], make_client=ev.replay_client_factory(tmp_path / "rec"),
        generate=ok_generate, check=ok_check,
    )  # fmt: skip
    assert [r.as_dict() for r in first] == [r.as_dict() for r in second]


# --------------------------------------------------------------------------- CLI
def test_missing_key_exits_before_any_network(monkeypatch, capsys):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    def boom(*_a, **_k):
        raise AssertionError("must not create a client or touch the network")

    monkeypatch.setattr(ev, "live_client_factory", boom)
    monkeypatch.setattr(ev, "load_cases", boom)
    assert ev.main([]) == 2
    err = capsys.readouterr().err
    assert "ANTHROPIC_API_KEY" in err and "--replay" in err
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    assert ev.main(["--models", OP]) == 2


def test_cli_replay_writes_results_json_and_never_prints_a_key(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-secret-123")
    monkeypatch.setattr(ev, "run_case", _patched_run_case(ev.run_case))
    out = tmp_path / "res.json"
    pattern = str(ROOT / "evals" / "cases" / "cafe" / "01.json")
    assert ev.main(["--replay", str(FIXTURES), "--cases", pattern, "--out", str(out)]) == 0
    printed = capsys.readouterr()
    assert "sk-ant-test-secret-123" not in printed.out + printed.err
    data = json.loads(out.read_text())
    assert set(data["summary"]) == set(ev.DEFAULT_MODELS)
    assert len(data["cases"]) == 3 and data["mode"] == "replay of fixtures"
    assert "sk-ant-test-secret-123" not in out.read_text()
    assert data["cases"][0]["per_call"][0]["input_tokens"] == 2100


def _patched_run_case(real):
    def run(c, model, client, **kw):
        return real(c, model, client, generate=ok_generate, check=ok_check)

    return run


def test_live_mode_uses_the_key_only_to_build_the_client(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-secret-456")
    seen = {}

    def fake_factory(key):
        seen["key"] = key
        return ev.replay_client_factory(FIXTURES)

    monkeypatch.setattr(ev, "live_client_factory", fake_factory)
    monkeypatch.setattr(ev, "run_case", _patched_run_case(ev.run_case))
    pattern = str(ROOT / "evals" / "cases" / "cafe" / "01.json")
    assert ev.main(["--cases", pattern, "--models", S, "--record", str(tmp_path / "rec")]) == 0
    assert seen["key"] == "sk-ant-test-secret-456"
    printed = capsys.readouterr()
    assert "sk-ant-test-secret-456" not in printed.out + printed.err
    assert json.loads((tmp_path / "rec" / "meta.json").read_text())["live"] is True
    assert (tmp_path / "rec" / S / "cafe-01.json").exists()


def test_replay_and_record_together_is_refused(tmp_path):
    assert ev.main(["--replay", str(FIXTURES), "--record", str(tmp_path)]) == 2


# --------------------------------------------------------------------------- memo
def test_memo_skeleton_and_rewrite(tmp_path):
    memo = ROOT / "docs" / "memos" / "brief-model-eval.md"
    text = memo.read_text(encoding="utf-8")
    assert "Not run yet: needs ANTHROPIC_API_KEY (HUMAN_TODO A1)" in text
    assert "| Model | Pass share | Mean s | p95 s | Mean $/order | Calls/order |" in text
    assert "Pending" in text and "2026-10-18" in text and "platform.claude.com/docs/en/about-claude/pricing" in text
    copy = tmp_path / "memo.md"
    copy.write_text(text, encoding="utf-8")
    results = _replay(FIXTURE_CASES, generate=ok_generate, check=ok_check)
    ev.write_memo(copy, ev.summarize(results), mode="live", n_cases=3, today="2026-11-01")
    new = copy.read_text(encoding="utf-8")
    assert "Not run yet" not in new and "| claude-opus-5-5 | 100% (3/3) |" in new
    assert "Use `claude-sonnet-5-5`" in new and "Run 2026-11-01, live, 3 cases per model." in new
    assert new.split(ev.RESULTS_START)[0] == text.split(ev.RESULTS_START)[0]  # the rest is untouched


def test_memo_from_fixture_replay_is_refused(tmp_path):
    pattern = str(ROOT / "evals" / "cases" / "cafe" / "01.json")
    assert ev.main(["--replay", str(FIXTURES), "--cases", pattern, "--memo"]) == 2


# --------------------------------------------------------------------------- real pipeline (LibreOffice)
@pytest.mark.libreoffice
def test_replay_through_the_real_pipeline():
    r = by(_replay(FIXTURE_CASES, [S, OP]))
    assert r[(S, "home_services-07")].passed  # tailored brief builds, recalculates and passes the challenger
    assert r[(S, "cafe-01")].passed and r[(OP, "cafe-01")].passed
    bad = r[(OP, "home_services-07")]  # valid for the template but Checks FAIL: never counted as a pass
    assert not bad.passed and bad.stage == "check" and "in-file checks" in bad.reason
