# Backlog

Open tasks only; finished and cancelled ones are one line each in `docs/DONE.md`.
Status values: `TODO` · `IN_PROGRESS (date)` · `BLOCKED: reason` · `NEEDS_HENRY: what`. Protocol and model
routing: see `CLAUDE.md`. Each track edits only its own section. Pick the first ready task in your track.
Every task has `Model: opus|sonnet|haiku` (who does it; reviews are always opus).

Skill names are as shown in the session's skill list (prefixes may differ:
`xlsx` may appear as `anthropic-skills:xlsx`). "(opt)" = use if installed.

---

## Track E — Engineering (daily)

> **Priority:** E08 → E23. All earlier E tasks are done (`docs/DONE.md`).
> New industries are one file each (ADR-009, `docs/templates/ADDING_A_TEMPLATE.md`; follow E21/E22, Model: sonnet).
> Customer login = passwordless magic link by email (ADR-006).

### E08 — Brief builder (Claude API)
- status: TODO
- Model: opus
- note (2026-10-18, token-budget PR): plumbing is ready in `adapters/llm.py` — use it, don't duplicate it.
  `BRIEF_MODEL` (empty = LLM off = today's prefill; unknown id fails at start), `build_brief_request` puts the
  fixed prefix (system instruction + template description) first with `cache_control` when it reaches the
  model's minimum (512 tokens for the 5.5 models), `call_messages` returns token usage + latency, and
  `create_order(..., brief_usage=...)` writes it to the log per order. Keep the default empty: the model is
  chosen by E23. Add the `anthropic` SDK (pinned in constraints.txt) if you call the API through it.
- note (2026-10-18, L1): when the LLM path goes live, add Anthropic to the processors list in
  `content/legal/privacy.md` ("Who processes it for us") in the same PR.
- depends: E02
- skills: product-self-knowledge, engineering:system-design, engineering:testing-strategy
- do: `engine/brief_builder.py`: wizard answers (+ optional free text + key numbers)
  → Brief via Anthropic API with a strict JSON schema (tool use / structured output),
  per-industry/stage default library from templates, server-side validation,
  2 retries, cost+latency logging. Check the current model id and SDK usage with
  product-self-knowledge — do not guess. Tests use recorded fixtures; no network.
  Sample-data path ("prefill") works with no LLM call at all.
- done when: 20 fixture cases produce valid briefs; invalid LLM output is caught.

### E23 — Eval: which model fills the brief
- status: TODO
- Model: sonnet
- depends: E08 (LLM brief builder), BRIEF_MODEL plumbing (token-budget PR, done)
- skills: product-self-knowledge, engineering:testing-strategy
- do: `evals/brief_model_eval.py`: 6 industries × 10 wizard-answer variants (fixed, committed in `evals/cases/`)
  through `claude-haiku-5-5`, `claude-sonnet-5-5` and `claude-opus-5-5` via the E08 builder. Each brief goes
  through the existing brief validation (template `validate`) and the challenger (build → recalc → challenge).
  Per model: share of briefs that pass, mean and p95 response time, mean cost per order in $ from the API's
  token usage (input, output, cache read/write) × current prices — check prices with product-self-knowledge.
  Live API calls only when run by hand with `ANTHROPIC_API_KEY` set; not part of CI (CI tests the script on
  recorded fixtures).
- done when: `docs/memos/brief-model-eval.md` with the table and a recommendation: the cheapest model whose
  pass share is not below the reference and whose p95 ≤ 15 s. Reference = opus pass share (no model is in
  production yet; BRIEF_MODEL is empty). Henry sets `BRIEF_MODEL` from it (add to HUMAN_TODO).

---

## Track M — Marketing & content (weekdays)

_No open M tasks. Henry adds new ones here._
---

## Track P — Project management (weekly, Monday)

P runs every Monday and never "completes": it reviews, it does not build.
- Model: opus
- skills: engineering:standup, docs
- do: read RUNLOG, BACKLOG, open PRs, CI status, HUMAN_TODO. Write
  `docs/STATUS.md` (done last week, in progress, blocked, next week, risks,
  Henry's queue ordered by urgency). Detect stuck tasks (IN_PROGRESS > 3 days,
  same task failing twice) and either split them in BACKLOG with a note or mark
  BLOCKED with the reason. May reorder TODO tasks inside a track; may add tasks
  (prefix the id with the track, next free number). Report to Henry in Russian.
