# finmodel-app — instructions for every Claude session

Autonomous sessions build this product; no human watches a run. Reports to Henry Sheykin (owner, CFO) in
**Russian**; code, comments, commits and product copy in **English**. Background and reasons:
`docs/ARCHITECTURE.md`, ADRs in `docs/DECISIONS.md`.

## Product
StartupModel (startup-model.com) sells custom Excel financial models: the customer answers a short wizard,
pays once, gets an `.xlsx` with live formulas, a Low / Base / High switch and a Checks sheet. Reference
competitor getdraftplan.com (`docs/research/draftplan.md`): never copy its name, logo, texts or files.
Never mention or link Henry's FinModelsLab.

## Architecture (change only with an ADR)
- The LLM never writes workbook code; it only fills a validated **brief** (drivers Low/Base/High).
  Deterministic **templates** build the workbook, LibreOffice recalculates, an independent **challenger**
  recomputes in Python (every scenario-year within $1, Checks sheet not FAIL). A failing model is never delivered.
- Python 3.12, FastAPI + Jinja2 + vanilla JS, SQLAlchemy 2 (SQLite dev / Postgres prod), Alembic, DB-polled
  worker, openpyxl + headless `soffice`, adapters with fakes for tests (LLM tests use fixtures, never the live
  API), pytest + ruff, one Docker image on Railway.
- Layout: `engine/` `app/` `worker/` `adapters/` `web/` `content/` `tests/` `docs/` `evals/` `.claude/agents/`.

## Excel rules (load the `xlsx` skill before touching workbooks)
Arial; blue font = input, black = formula, green = cross-sheet link; yellow fill only on the scenario
selector. Formats `$#,##0;($#,##0);-`, `0.0%;(0.0%);-`. Every assumption in its own labelled cell; same
formula across every period; guard every denominator. Only Excel-2007 functions (INDEX, MATCH, SUMIF(S),
SUMPRODUCT, IFERROR, CHOOSE, IRR, NPV) — never XLOOKUP, FILTER, SORT, UNIQUE, SEQUENCE, LET, LAMBDA. Zero
formula errors after recalc.

## Design rules
- Design v2 is the source of truth for look, copy and section order: `design/landing.dc.html`,
  `design/tokens.dc.html` (details and the landing spec link: `docs/ARCHITECTURE.md`).
- The landing hero = live code `app/xlview.py` + `web/static/landing.js` rendering the real sample
  workbook; keep it faithful to the file, no decoration inside the grid.
- Never reintroduce the competitor's palette (navy #1F3864 + blue #2563EB), DM Sans, quote cards, "VS" cards
  or a single price card (ADR-005).

## Model routing
| Model | Work |
|---|---|
| opus | engine core, new financial logic (E05, E07 and alike), security and E2E, releases, weekly PM review, review of every PR |
| sonnet | a new industry following E21/E22, wizard, emails, landing, admin, SEO engine, all marketing |
| haiku | searches, test and log summaries, RUNLOG/STATUS updates |
| fable | only after opus failed the same task twice; record that in RUNLOG |

Each open BACKLOG task has `Model:`. The main run is the **dispatcher**: it picks the task, hands it to the
`implementer` subagent (sonnet) or does it itself when the task says `Model: opus`, then calls the
`reviewer` subagent (opus). Merge only after the reviewer's `PASS` **and** green CI; on `FAIL` fix and
review again. Subagents: `.claude/agents/` (`scout`, `implementer`, `reviewer`).

## Token budget
1. Early exit: first check whether any task of your track is ready (protocol step 2). If every candidate
   waits on Henry (HUMAN_TODO / `NEEDS_HENRY` / `BLOCKED`), append one line to RUNLOG and stop — nothing else.
2. One task per run, small PR.
3. Tests: `pytest -q 2>&1 | tail -n 30`; read only the tail and the failing tests. Never read full LibreOffice logs.
4. Read only the files the task needs. Hand wide searches to `scout`.
5. Ahrefs and other external sources: cap rows (`limit` ≤ 50).
6. Don't create subagents without need: each one starts from zero.

## Run protocol (every scheduled session)
1. Your prompt names your **track** (E = engineering, M = marketing, P = PM).
2. `git pull`. In `docs/BACKLOG.md` pick the first task of your track (mind the track's priority note) whose
   status is `TODO` (or `IN_PROGRESS` with a `continue:` note) and whose `depends` are all done
   (`docs/DONE.md`). Skip `NEEDS_HENRY` / `BLOCKED`. Nothing ready → early exit (Token budget 1).
3. Set it `IN_PROGRESS` with today's date, commit, push (claims the task).
4. Load every skill the task lists (Skill tool); a missing skill is noted in the run log.
5. Branch `<task-id>-<slug>`. Small commits. Tests for all code. Dispatch per Model routing.
6. Done = the task's `done when` + `ruff check .` and `ruff format --check .` clean + all tests green
   locally + reviewer `PASS`. Open a PR, wait for CI; green → squash-merge it yourself (Henry approved
   auto-merge on green CI). Red CI you cannot fix → leave the PR open, set the task `BLOCKED` with the reason.
7. Too big for one run? Merge a coherent slice, keep `IN_PROGRESS`, add `continue: <what is left>`.
8. Only Henry can do it (accounts, keys, money, legal, brand, CFO sign-off) → `docs/HUMAN_TODO.md`, set the
   task `NEEDS_HENRY` if it cannot proceed, move on to the next ready task.
9. Finish: remove the task from BACKLOG and add one line to `docs/DONE.md` (id, title, PR). Prepend a
   3–5 line entry to `docs/RUNLOG.md` (date, track, task, what changed, PR, anything for Henry). If RUNLOG
   then has more than 15 entries, keep the newest 10 and move the rest to `docs/runlog/archive-YYYY-MM.md`
   (newest first, month of the run). Push.
10. Last step: a short report to Henry in Russian via `SendUserMessage` (what was done, PR link, what needs
    him). No essays.

## Hard rules
- Never ask for or store secrets in the repo, chat or logs. Code reads them from environment variables;
  `.env.example` lists names only.
- Never create accounts, enter payment details, accept terms, buy anything, send email to real people, or
  deploy to production. Payments only in Stripe **test mode** on localhost.
- Never weaken a check, a test or the challenger to make something pass.
- Never edit another track's tasks in BACKLOG.md except to read status. Always `git pull --rebase` before
  pushing; on conflict, re-apply your edit.
- Do not invent facts in marketing copy (no fake testimonials, user counts, awards). Unknown numbers stay
  as placeholders like `[PRICE]`.
- Don't change the core idea, stack or brand without an ADR in `docs/DECISIONS.md` and a note to Henry.
