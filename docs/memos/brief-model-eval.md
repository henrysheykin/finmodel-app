# Brief model eval (E23): which OpenAI model should fill the brief?

Status: harness done, live run pending (needs `OPENAI_API_KEY`). Provider: OpenAI (ADR-012, E25).

## Purpose

`BRIEF_MODEL` (see `adapters/llm.py`) selects the model that tailors a customer's driver values from the wizard
answers and notes (E08 builder). Unset means the deterministic prefill path. This eval decides which of
`gpt-6-luna`, `gpt-6.1-sol` and `gpt-6-astra` should become the default: the cheapest one that
is as reliable as the best one and fast enough for a customer waiting on a form post.

## Method

**Cases.** 60 committed files, `evals/cases/<industry>/<nn>.json`: six industries (cafe, saas, retail, services,
home_services, fitness) times ten situations. Each file holds the wizard answers in exactly the shape the app
consumes (`app.briefing.Answers`) and the customer notes (required, otherwise the builder makes no call). The ten
situations per industry: short note with concrete numbers; early stage with two locked key numbers; long detailed
note with a valuation goal; established business with a locked number; a note asking for impossible or out-of-range
values; a note in another language (Spanish, German, French, Italian); a formula-like and prompt-injection string
in the note; locked numbers that the note contradicts; a vague note with no numbers; a financing and opening-date
note. Stage, horizon (1, 3, 5 years), granularity, tier and goal vary across them. The files come from
`evals/make_cases.py` (run once, output committed); the benchmark does not change between runs.

**Pipeline** (the production functions, nothing relaxed). Wizard answers -> prefill brief
(`PrefillBriefSource`) -> `engine.brief_builder.build_brief` (with its retries and checks) -> template `validate` ->
`worker.pipeline.generate` (build workbook + LibreOffice recalculation, any formula error rejects) ->
`worker.pipeline.check` (independent challenger: every scenario-year within $1, Checks sheet not FAIL).

**A case passes** only if the model's brief was accepted by the builder (no `BriefBuildError`, i.e. the app would
not have fallen back to the prefill brief) and the built workbook passes the challenger with Checks not FAIL.
The reason for each failure is kept in the JSON results.

**Metrics per model.**

- Pass share: passed cases / 60.
- Mean and p95 latency in seconds per order: the sum of the wall time of all API requests of the order (retries
  and failed requests included). p95 is the nearest-rank 95th percentile over the 60 orders.
- Mean cost per order in USD: token usage of every request (uncached input, cached input, cache write, output incl. reasoning) times the
  prices below, averaged over all 60 orders, failed orders included (they were paid for).
- Calls per order: API requests made, including transport errors and retries.

**Prices** (`PRICES_PER_MTOK` in `evals/brief_model_eval.py`), USD per million tokens, Standard tier, from
https://developers.openai.com/api/docs/pricing and the model pages, checked 2026-10-18:

| Model | Input | Cached input | Cache write | Output |
|---|---|---|---|---|
| gpt-6-luna | 0.10 | 0.01 | 0.125 | 0.50 |
| gpt-6.1-sol | 2 | 0.10 | 2.50 | 10 |
| gpt-6-astra | 10 | 1 | 12.50 | 50 |

Each input token is billed at one rate only: uncached, cached (read) or cache write; the API reports
`input_tokens` (total) with `input_tokens_details.cached_tokens` and `cache_write_tokens`, and the adapter splits
them. Caching is automatic (prefix of at least 1,024 tokens; the adapter adds `prompt_cache_key` = the template).
Reasoning tokens are billed as output and are included in `output_tokens`. Long-context rates apply to the whole
request when its input exceeds 272,000 tokens (2x input and cache rates, 1.5x output); the harness applies them per
request, though our prompts are around 2-5k tokens so it should never trigger.

**Settings under test.** OpenAI Responses API, forced `submit_brief` function call with a strict JSON schema,
`reasoning.effort` = `low` (all three models accept it; gpt-6-astra cannot switch reasoning off), `store` = false.

**Recommendation rule.** Reference = the pass share of `gpt-6-astra` (the strongest of the three). Among the models whose pass share is at
least the reference and whose p95 latency is at most 15 s, pick the cheapest by mean cost per order. If no model
qualifies, no model is recommended and the prefill path stays the default.

## How to run by hand

```
OPENAI_API_KEY=... python -m evals.brief_model_eval --record evals/runs/<date> --memo
```

Live mode needs the key and refuses to start without it (exit status 2); the key is never printed or logged.
Options: `--models` (default all three), `--cases` (glob, default `evals/cases/*/*.json`), `--out results.json`
(per-case results and aggregates), `--memo` (rewrite the table and recommendation below), `--record DIR` (save the
raw API responses, no headers or key, so the run can be replayed). A run makes up to 3 x 60 builder sessions
(each up to 3 requests) and rebuilds 180 workbooks in LibreOffice: rough guess, not measured: about an hour and a few dollars.
Recordings in `evals/runs/` are git-ignored; commit only the updated memo.

Offline: `python -m evals.brief_model_eval --replay <dir>` runs the whole pipeline on recorded responses. CI does
this on the small fixtures in `tests/fixtures/brief_eval/`. `--memo` accepts a replay only of a recording made by a
live run (`meta.json`).

## Results

<!-- RESULTS:START -->
| Model | Pass share | Mean s | p95 s | Mean $/order | Calls/order |
|---|---|---|---|---|---|
| gpt-6-luna | — | — | — | — | — |
| gpt-6.1-sol | — | — | — | — | — |
| gpt-6-astra | — | — | — | — | — |

Not run yet: needs OPENAI_API_KEY (HUMAN_TODO A1)
<!-- RESULTS:END -->

## Recommendation

<!-- RECOMMENDATION:START -->
Pending: the live run has not been done.
<!-- RECOMMENDATION:END -->
