"""E23: which Claude model fills the brief best? (``python -m evals.brief_model_eval``)

For every committed case (``evals/cases/<industry>/<nn>.json``) and every model the script runs the same
path as production: wizard answers → prefill brief (``app.briefing.PrefillBriefSource``) → the E08 builder
(``engine.brief_builder.build_brief``) → template ``validate`` → ``worker.pipeline.generate`` (build +
LibreOffice recalculation) → ``worker.pipeline.check`` (independent challenger). Nothing is relaxed.

A case passes only if the model's brief was accepted by the builder (no ``BriefBuildError``, i.e. the
production path would not have fallen back to the prefill brief) AND the build passes the challenger.

Modes
- live: needs ``ANTHROPIC_API_KEY`` (never printed or logged). ``--record DIR`` saves every raw API response.
- replay: ``--replay DIR`` feeds recorded responses through the same code, offline. No key, no network.
Without a key and without ``--replay`` the script exits with status 2 before doing anything.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import statistics
import sys
import tempfile
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = "evals/cases/*/*.json"
DEFAULT_MEMO = ROOT / "docs" / "memos" / "brief-model-eval.md"
DEFAULT_MODELS = ("claude-haiku-5-5", "claude-sonnet-5-5", "claude-opus-5-5")
REFERENCE_MODEL = "claude-opus-5-5"
#: the recommendation rule's latency ceiling (the customer waits on the form post; builder DEADLINE_S is 15)
P95_LIMIT_S = 15.0
LONG_PROMPT_TOKENS = 100_000

#: USD per million tokens. Source: https://platform.claude.com/docs/en/about-claude/pricing, checked 2026-10-18.
#: ``cache_write`` is the 5-minute cache-write rate: the adapter marks the prefix ``{"type": "ephemeral"}``
#: without a ``ttl`` (adapters/llm.py ``build_brief_request``), and the default TTL is 5 minutes.
#: ``*_long`` apply to a request whose total input (input + cache read + cache write tokens) exceeds
#: 100,000 tokens; the surcharge is applied per request (see ``cost_usd``).
PRICES_PER_MTOK: dict[str, dict[str, Decimal]] = {
    "claude-haiku-5-5": {
        "input": Decimal("0.10"),
        "cache_write": Decimal("0.125"),
        "cache_read": Decimal("0.01"),
        "output": Decimal("0.50"),
        "input_long": Decimal("0.50"),
        "cache_write_long": Decimal("0.625"),
        "cache_read_long": Decimal("0.05"),
        "output_long": Decimal("2.50"),
    },
    "claude-sonnet-5-5": {
        "input": Decimal("2"),
        "cache_write": Decimal("2.50"),
        "cache_read": Decimal("0.10"),
        "output": Decimal("10"),
    },
    "claude-opus-5-5": {
        "input": Decimal("4"),
        "cache_write": Decimal("5"),
        "cache_read": Decimal("0.20"),
        "output": Decimal("20"),
    },
}


# --------------------------------------------------------------------------- cost and statistics
@dataclass(frozen=True)
class CallUsage:
    """Token usage and wall time of one API request."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_read: int = 0
    cache_write: int = 0
    latency_ms: int = 0

    @property
    def total_input(self) -> int:
        return self.input_tokens + self.cache_read + self.cache_write


def cost_usd(model: str, calls: list[CallUsage]) -> Decimal:
    """Dollar cost of the requests of one order. Exact (Decimal). The >100k-input surcharge, where the
    model has one, is applied per request, so a retry with a short prompt is not surcharged."""
    p = PRICES_PER_MTOK[model]
    total = Decimal(0)
    for c in calls:
        long = c.total_input > LONG_PROMPT_TOKENS and "input_long" in p
        suffix = "_long" if long else ""
        total += (
            c.input_tokens * p["input" + suffix]
            + c.cache_write * p["cache_write" + suffix]
            + c.cache_read * p["cache_read" + suffix]
            + c.output_tokens * p["output" + suffix]
        ) / Decimal(1_000_000)
    return total


def percentile95(values: list[float]) -> float:
    """Nearest-rank 95th percentile: the smallest value with at least 95% of the sample at or below it."""
    if not values:
        return 0.0
    s = sorted(values)
    return s[max(0, math.ceil(0.95 * len(s)) - 1)]


@dataclass
class CaseResult:
    case_id: str
    industry: str
    model: str
    passed: bool
    reason: str  # "ok" or why not
    stage: str  # "builder" | "validate" | "build" | "check" | "recorded" | "done"
    calls: list[CallUsage] = field(default_factory=list)

    @property
    def latency_s(self) -> float:
        return sum(c.latency_ms for c in self.calls) / 1000

    @property
    def cost(self) -> Decimal:
        return cost_usd(self.model, self.calls)

    def as_dict(self) -> dict[str, Any]:
        return {
            "case": self.case_id,
            "industry": self.industry,
            "model": self.model,
            "passed": self.passed,
            "reason": self.reason,
            "stage": self.stage,
            "calls": len(self.calls),
            "latency_s": round(self.latency_s, 3),
            "input_tokens": sum(c.input_tokens for c in self.calls),
            "output_tokens": sum(c.output_tokens for c in self.calls),
            "cache_read_tokens": sum(c.cache_read for c in self.calls),
            "cache_write_tokens": sum(c.cache_write for c in self.calls),
            "cost_usd": float(self.cost),
            "per_call": [c.__dict__ for c in self.calls],
        }


def summarize(results: list[CaseResult]) -> dict[str, dict[str, Any]]:
    """Aggregates per model: pass share, mean and p95 latency (s), mean cost and calls per order."""
    out: dict[str, dict[str, Any]] = {}
    for model in dict.fromkeys(r.model for r in results):
        rs = [r for r in results if r.model == model]
        lat = [r.latency_s for r in rs]
        out[model] = {
            "cases": len(rs),
            "passed": sum(r.passed for r in rs),
            "pass_share": sum(r.passed for r in rs) / len(rs),
            "mean_s": statistics.fmean(lat),
            "p95_s": percentile95(lat),
            "mean_cost_usd": sum((r.cost for r in rs), Decimal(0)) / len(rs),
            "mean_calls": statistics.fmean(len(r.calls) for r in rs),
        }
    return out


def recommend(summary: dict[str, dict[str, Any]], *, p95_limit: float = P95_LIMIT_S) -> dict[str, Any]:
    """Cheapest model (mean cost per order) whose pass share >= the reference model's and p95 <= limit.

    The reference is Opus's pass share. Returns ``{"model": name | None, "reason": text}``."""
    ref = summary.get(REFERENCE_MODEL)
    if ref is None:
        return {"model": None, "reason": f"no recommendation: {REFERENCE_MODEL} (the reference) was not run"}
    ok = [
        m
        for m, s in summary.items()
        if s["pass_share"] >= ref["pass_share"] and s["p95_s"] <= p95_limit and s["cases"] > 0
    ]
    if not ok:
        return {
            "model": None,
            "reason": (
                f"no model reaches the reference pass share ({ref['pass_share']:.0%}) with p95 <= {p95_limit:g} s"
            ),
        }
    best = min(ok, key=lambda m: (summary[m]["mean_cost_usd"], -summary[m]["pass_share"], m))
    return {
        "model": best,
        "reason": (
            f"cheapest model with pass share >= {REFERENCE_MODEL} ({ref['pass_share']:.0%}) and p95 <= {p95_limit:g} s"
        ),
    }


# --------------------------------------------------------------------------- cases
def load_cases(pattern: str = DEFAULT_CASES) -> list[dict[str, Any]]:
    pat = pattern if os.path.isabs(pattern) else str(ROOT / pattern)
    files = sorted(glob.glob(pat))
    if not files:
        raise SystemExit(f"no case files match {pattern!r}")
    return [json.loads(Path(f).read_text(encoding="utf-8")) for f in files]


def prefill_for(case: dict[str, Any]):
    """(answers, prefill brief, CustomerInput) exactly as ``app.briefing.LLMBriefSource`` builds them."""
    from app.briefing import Answers, PrefillBriefSource
    from engine.brief_builder import CustomerInput

    answers = Answers(**case["answers"])
    start = PrefillBriefSource().build_brief(answers)
    inp = CustomerInput(business_name=answers.business_name, notes=answers.notes, locked=set(answers.key_numbers))
    return answers, start, inp


# --------------------------------------------------------------------------- clients
class RecordingClient:
    """Wraps any client with ``messages.create``; keeps every call (response or error) for usage and
    for ``--record``. Latency comes from the inner client's ``last_latency_ms`` when it has one (replay
    of a recorded latency), otherwise it is measured here."""

    def __init__(self, inner: Any) -> None:
        self.inner = inner
        self.messages = self
        self.entries: list[dict[str, Any]] = []
        self.calls: list[CallUsage] = []

    def create(self, **request: Any) -> Any:
        from adapters.llm import LLMTransportError, usage_from_response

        t0 = time.monotonic()
        try:
            response = self.inner.messages.create(**request)
        except LLMTransportError as exc:
            ms = self._latency(t0)
            self.entries.append({"raise": str(exc), "retryable": exc.retryable, "latency_ms": ms})
            self.calls.append(CallUsage(latency_ms=ms))
            raise
        ms = self._latency(t0)
        u = usage_from_response(response, request["model"], ms)
        self.entries.append({"response": response, "latency_ms": ms})
        self.calls.append(
            CallUsage(u.input_tokens, u.output_tokens, u.cache_read_input_tokens, u.cache_creation_input_tokens, ms)
        )
        return response

    def _latency(self, t0: float) -> int:
        recorded = getattr(self.inner, "last_latency_ms", None)
        return int(recorded) if recorded is not None else int((time.monotonic() - t0) * 1000)


class ReplayClient:
    """Feeds recorded entries (``{"response", "latency_ms"}`` or ``{"raise", "retryable"}``) in order."""

    def __init__(self, entries: list[dict[str, Any]]) -> None:
        self.entries = list(entries)
        self.messages = self
        self.last_latency_ms: int | None = None

    def create(self, **_request: Any) -> Any:
        from adapters.llm import LLMTransportError

        if not self.entries:
            self.last_latency_ms = 0
            raise LLMTransportError("replay: more calls than recorded", retryable=False)
        e = self.entries.pop(0)
        self.last_latency_ms = e.get("latency_ms", 0)
        if "raise" in e:
            raise LLMTransportError(e["raise"], retryable=e.get("retryable", True))
        return e["response"]


def _safe(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", name)


def recording_path(root: Path, model: str, case_id: str) -> Path:
    return root / _safe(model) / f"{_safe(case_id)}.json"


# --------------------------------------------------------------------------- one case
def run_case(
    case: dict[str, Any],
    model: str,
    client: Any,
    *,
    generate: Callable[..., None] | None = None,
    check: Callable[..., dict] | None = None,
) -> tuple[CaseResult, RecordingClient]:
    """Run one case on one model through the production pipeline. ``generate`` / ``check`` default to
    ``worker.pipeline.generate`` / ``check`` (tests may inject fakes to skip LibreOffice)."""
    from engine.brief import BriefError
    from engine.brief_builder import BriefBuildError, build_brief
    from engine.templates import get_template
    from worker.pipeline import BuildRejected
    from worker.pipeline import check as prod_check
    from worker.pipeline import generate as prod_generate

    generate = generate or prod_generate
    check = check or prod_check
    rec = RecordingClient(client)
    base = {"case_id": case["id"], "industry": case["industry"], "model": model}

    def result(passed: bool, reason: str, stage: str) -> tuple[CaseResult, RecordingClient]:
        return CaseResult(**base, passed=passed, reason=reason, stage=stage, calls=list(rec.calls)), rec

    _answers, start, inp = prefill_for(case)
    if not inp.notes.strip():
        raise ValueError(f"{case['id']}: notes are required (without notes the builder makes no call)")
    try:
        built = build_brief(rec, model, start, inp)
    except BriefBuildError as exc:
        return result(False, f"fallback to prefill: {exc}"[:300], "builder")
    except Exception as exc:
        return result(False, f"builder crashed: {type(exc).__name__}: {exc}"[:300], "builder")
    brief = built.brief
    try:
        get_template(brief.template).validate(brief)
    except BriefError as exc:
        return result(False, f"template validation: {exc}"[:300], "validate")
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "model.xlsx"
        try:
            generate(brief, path)
        except (BuildRejected, BriefError) as exc:
            return result(False, f"build: {exc}"[:300], "build")
        except Exception as exc:
            return result(False, f"build crashed: {type(exc).__name__}: {exc}"[:300], "build")
        try:
            check(brief, path)
        except BuildRejected as exc:
            return result(False, str(exc)[:300], "check")
        except Exception as exc:
            return result(False, f"challenger crashed: {type(exc).__name__}: {exc}"[:300], "check")
    return result(True, "ok", "done")


# --------------------------------------------------------------------------- the whole run
def run_eval(
    cases: list[dict[str, Any]],
    models: list[str],
    *,
    make_client: Callable[[str, dict[str, Any]], Any],
    record_dir: Path | None = None,
    generate: Callable[..., None] | None = None,
    check: Callable[..., dict] | None = None,
    progress: Callable[[str], None] | None = None,
) -> list[CaseResult]:
    results: list[CaseResult] = []
    for model in models:
        for case in cases:
            try:
                client = make_client(model, case)
            except FileNotFoundError as exc:
                miss = CaseResult(case["id"], case["industry"], model, False, f"no recording: {exc}", "recorded")
                results.append(miss)
                continue
            res, rec = run_case(case, model, client, generate=generate, check=check)
            results.append(res)
            if record_dir is not None:
                p = recording_path(record_dir, model, case["id"])
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(json.dumps({"calls": rec.entries}, indent=1) + "\n", encoding="utf-8")
            if progress:
                progress(f"{model} {case['id']}: {'PASS' if res.passed else 'FAIL ' + res.reason[:80]}")
    return results


def replay_client_factory(root: Path) -> Callable[[str, dict[str, Any]], ReplayClient]:
    def make(model: str, case: dict[str, Any]) -> ReplayClient:
        p = recording_path(root, model, case["id"])
        return ReplayClient(json.loads(p.read_text(encoding="utf-8"))["calls"])  # FileNotFoundError = no recording

    return make


def live_client_factory(api_key: str) -> Callable[[str, dict[str, Any]], Any]:
    from adapters.llm import AnthropicHTTPClient

    client = AnthropicHTTPClient(api_key)  # the same client and timeout as production

    def make(_model: str, _case: dict[str, Any]) -> Any:
        return client

    return make


# --------------------------------------------------------------------------- output
def _fmt_money(d: Decimal) -> str:
    return f"${d:.4f}"


def results_table(summary: dict[str, dict[str, Any]]) -> str:
    rows = ["| Model | Pass share | Mean s | p95 s | Mean $/order | Calls/order |", "|---|---|---|---|---|---|"]
    for model, s in summary.items():
        rows.append(
            f"| {model} | {s['pass_share']:.0%} ({s['passed']}/{s['cases']}) | {s['mean_s']:.1f} | {s['p95_s']:.1f} "
            f"| {_fmt_money(s['mean_cost_usd'])} | {s['mean_calls']:.2f} |"
        )
    return "\n".join(rows)


RESULTS_START, RESULTS_END = "<!-- RESULTS:START -->", "<!-- RESULTS:END -->"
RECO_START, RECO_END = "<!-- RECOMMENDATION:START -->", "<!-- RECOMMENDATION:END -->"


def _replace_block(text: str, start: str, end: str, body: str) -> str:
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pat.search(text):
        raise SystemExit(f"memo is missing the {start} ... {end} markers")
    return pat.sub(lambda _m: f"{start}\n{body}\n{end}", text)


def write_memo(path: Path, summary: dict[str, dict[str, Any]], *, mode: str, n_cases: int, today: str) -> None:
    reco = recommend(summary)
    text = path.read_text(encoding="utf-8")
    results = f"{results_table(summary)}\n\nRun {today}, {mode}, {n_cases} cases per model."
    if reco["model"]:
        advice = f"**Use `{reco['model']}` as the default `BRIEF_MODEL`.** {reco['reason'].capitalize()}."
    else:
        advice = f"**No model recommended.** {reco['reason'].capitalize()}. Keep the prefill path (BRIEF_MODEL unset)."
    text = _replace_block(text, RESULTS_START, RESULTS_END, results)
    text = _replace_block(text, RECO_START, RECO_END, advice)
    path.write_text(text, encoding="utf-8")


def _json_default(o: Any) -> Any:
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError(type(o).__name__)


# --------------------------------------------------------------------------- CLI
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="python -m evals.brief_model_eval", description=__doc__.split("\n\n")[0])
    ap.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS), help="model ids (default: all three)")
    ap.add_argument("--cases", default=DEFAULT_CASES, help=f"glob of case files (default {DEFAULT_CASES})")
    ap.add_argument("--out", type=Path, help="write the full results (per case and aggregates) as JSON")
    ap.add_argument("--memo", action="store_true", help="rewrite the results table and recommendation in the memo")
    ap.add_argument("--memo-path", type=Path, default=DEFAULT_MEMO, help=argparse.SUPPRESS)
    ap.add_argument("--replay", type=Path, help="feed recorded responses from this directory (offline, no key)")
    ap.add_argument("--record", type=Path, help="live mode: save raw API responses here so the run can be replayed")
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.replay and args.record:
        print("--record is for live runs; do not combine it with --replay", file=sys.stderr)
        return 2
    live_meta = None
    if args.replay:
        if not args.replay.is_dir():
            print(f"--replay: {args.replay} is not a directory", file=sys.stderr)
            return 2
        make = replay_client_factory(args.replay)
        meta_file = args.replay / "meta.json"
        live_meta = json.loads(meta_file.read_text()) if meta_file.exists() else {}
        mode = "replay of a live run" if live_meta.get("live") else "replay of fixtures"
    else:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            print(
                "ANTHROPIC_API_KEY is not set: the live run needs it (set it in your shell; it is never printed).\n"
                "For an offline run on recorded responses use --replay <dir>.",
                file=sys.stderr,
            )
            return 2
        make = live_client_factory(key)
        mode = "live"
    if args.memo and args.replay and not live_meta.get("live"):
        print("--memo from a replay needs a recording of a live run (meta.json live=true)", file=sys.stderr)
        return 2
    cases = load_cases(args.cases)
    if args.record:
        # written first so an interrupted live run still leaves a usable recording
        args.record.mkdir(parents=True, exist_ok=True)
        (args.record / "meta.json").write_text(
            json.dumps({"live": True, "recorded_at": date.today().isoformat(), "models": args.models}) + "\n"
        )
    results = run_eval(
        cases, args.models, make_client=make, record_dir=args.record, progress=lambda m: print(m, flush=True)
    )
    summary = summarize(results)
    print()
    print(results_table(summary))
    reco = recommend(summary)
    print(f"\nRecommendation: {reco['model'] or 'none'} ({reco['reason']})")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "date": date.today().isoformat(),
            "mode": mode,
            "summary": summary,
            "recommendation": reco,
            "cases": [r.as_dict() for r in results],
        }
        args.out.write_text(json.dumps(payload, indent=1, default=_json_default) + "\n", encoding="utf-8")
    if args.memo:
        write_memo(args.memo_path, summary, mode=mode, n_cases=len(cases), today=date.today().isoformat())
        print(f"memo updated: {args.memo_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
