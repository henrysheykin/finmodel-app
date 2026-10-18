# Backlog

Open tasks only; finished and cancelled ones are one line each in `docs/DONE.md`.
Status values: `TODO` · `IN_PROGRESS (date)` · `BLOCKED: reason` · `NEEDS_HENRY: what`. Protocol and model
routing: see `CLAUDE.md`. Each track edits only its own section. Pick the first ready task in your track.
Every task has `Model: opus|sonnet|haiku` (who does it; reviews are always opus).

Skill names are as shown in the session's skill list (prefixes may differ:
`xlsx` may appear as `anthropic-skills:xlsx`). "(opt)" = use if installed.

---

## Track E — Engineering (daily)

> **Priority:** E23 → E24. All earlier E tasks are done (`docs/DONE.md`).
> New industries are one file each (ADR-009, `docs/templates/ADDING_A_TEMPLATE.md`; follow E21/E22, Model: sonnet).
> Customer login = passwordless magic link by email (ADR-006).

### E23 — Eval: which model fills the brief
- status: IN_PROGRESS (2026-10-18)
- Model: sonnet
- depends: E08 (LLM brief builder, done #39), BRIEF_MODEL plumbing (token-budget PR, done)
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

### E24 — LLM brief: refresh derived goal defaults, count usage on every fallback
- status: TODO
- Model: sonnet
- depends: E08
- skills: engineering:testing-strategy
- do: (from the E08 review, low) (1) `apply_goal` defaults that are computed from other drivers (e.g.
  `cash_buffer` ≈ 3 months of costs) are set before the model changes costs in `engine/brief_builder.merge`;
  recompute them after the merge for goal keys the model did not change and the customer did not lock.
  (2) `app/briefing.LLMBriefSource`: on an unexpected exception the usage of calls already made is lost
  (logged as none); carry the running usage on the error so `brief_llm order=…` stays complete.
- done when: tests show a cost change moves `cash_buffer` Base and that usage is logged on every fallback.

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
