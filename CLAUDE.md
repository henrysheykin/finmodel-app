# finmodel-app — instructions for every Claude session

You are one of several autonomous sessions building this product. No human is
watching your run. Read this file, then `docs/BACKLOG.md`, then do exactly one
task (protocol below). Owner: Henry Sheykin (CFO, 20+ years, ~200 financial
models built). Reports to him are in **Russian**; code, comments, commits and
product copy are in **English**.

## Product

A web app that sells custom Excel financial models. The customer answers a
short wizard (business type, goal, stage, horizon, granularity, a few key
numbers), pays once, and receives an `.xlsx` with live formulas, a Low / Base /
High scenario switch and a Checks sheet. Reference competitor:
getdraftplan.com — see `docs/research/draftplan.md`. Never copy its name, logo,
texts or files. Brand is **StartupModel**, domain **startup-model.com** (ADR-002; replaces the
old working name Ledgerline). Kept separate from Henry's FinModelsLab: never
mention or link it.

## The core idea (do not change without an ADR)

The LLM never writes workbook code. It only fills a validated **brief** (JSON:
drivers with Low/Base/High values). Deterministic Python **templates** build
the workbook. LibreOffice recalculates it. An independent **challenger**
recomputes the numbers in plain Python and must match every scenario-year
within $1, and the in-file Checks sheet must not FAIL. A model that fails is
never delivered. The prototype of all three is in `poc/` (cafe template: 894
formulas, 0 errors, all 9 scenario-years match).

## Stack (ADR-001 in docs/DECISIONS.md)

- Python 3.12, FastAPI, Jinja2 server-rendered pages + vanilla JS (no SPA framework).
- SQLAlchemy 2; SQLite in dev/tests, Postgres in prod. Alembic migrations.
- Worker = separate process polling a `jobs` table (no Redis).
- openpyxl to write, LibreOffice headless (`soffice`) to recalculate.
- Adapters with a fake/console implementation for tests: payments (Stripe
  Checkout first), email (Resend or Postmark), storage (local disk / S3),
  LLM (Anthropic SDK; tests use recorded fixtures, never the live API).
- pytest, ruff; GitHub Actions CI installs LibreOffice and runs everything.
- One Docker image (app + worker commands), deployable to any Docker host.

Repo layout target: `engine/` (templates, brief schema, recalc, challenger),
`app/` (web, API, wizard, admin), `worker/`, `adapters/`, `web/` (landing,
static), `content/` (copy, SEO pages, emails, legal), `tests/`, `docs/`.

## Excel rules (also load the `xlsx` skill before touching workbooks)

Arial; blue font = input, black = formula, green = cross-sheet link; yellow
fill only on the scenario selector. Formats `$#,##0;($#,##0);-`,
`0.0%;(0.0%);-`. Every assumption in its own labelled cell; same formula across
every period; guard every denominator. Only Excel-2007-era functions (INDEX,
MATCH, SUMIF(S), SUMPRODUCT, IFERROR, CHOOSE, IRR, NPV) — never XLOOKUP,
FILTER, SORT, UNIQUE, SEQUENCE, LET, LAMBDA. Zero formula errors after recalc.

## Design source

- **Design v2 (2026-10-16) is the source of truth** for look, copy and section
  order: `design/landing.dc.html` and `design/tokens.dc.html` (exact colours,
  type, components). Identity: accountant's analysis pad — ink #1B2A2F, pine
  #0F6E56, pad paper #F7F8F3 with 32 px ruling, red auditor tick marks
  #B8322A, double-underlined totals; Schibsted Grotesk + IBM Plex Sans with
  tabular figures. Canvas: https://claude.ai/artifact/4qNJgJzUU633rZ9A7vhQJj
- Hero spreadsheet (2026-10-18, Henry: "must look like real Excel"): the reference is the live code —
  `app/xlview.py` + `web/static/landing.js` render the real sample workbook in a spreadsheet-app
  window (ribbon, name box, formula bar, gridlines, frozen panes, B4 list, sheet tabs, status bar).
  It supersedes the hero in the canvas. Keep it faithful to the file; no decoration inside the grid.
- The v1 look copied the competitor's visual language too closely and was
  replaced (ADR-005). Never reintroduce their palette (navy #1F3864 + blue
  #2563EB), DM Sans, quote cards, "VS" cards or single price card.
- Landing build spec (Russian): Claude Docs
  https://claude.ai/code/artifact/73230182-c0f4-4cb1-a600-8551781f182c —
  export it to `docs/SPEC_LANDING.md` when needed. Its sections 3–5 and 7 are
  superseded by design v2; sections 6 and 8–11 (mockup logic, responsive,
  SEO, accessibility, config, acceptance) still apply.

## Run protocol (every scheduled session)

1. Your prompt names your **track** (E = engineering, M = marketing, P = PM).
2. `git pull`. In `docs/BACKLOG.md` pick the first task of your track whose
   status is `TODO` (or `IN_PROGRESS` with a `continue:` note left by a
   previous run) and whose `depends` are all `DONE`. Tasks marked
   `NEEDS_HENRY` or `BLOCKED` are skipped. If nothing is ready, write one
   line to `docs/RUNLOG.md`, report it, and stop.
3. Set it to `IN_PROGRESS` with today's date, commit, push (claims the task).
4. Load every skill the task lists (Skill tool). If a listed skill is not
   available, continue without it and note that in the run log.
5. Work on a branch `<task-id>-<slug>`. Small commits. Tests for all code.
6. Definition of done = the task's `done when` + `ruff` clean + all tests green
   locally. Open a PR, wait for CI; when green, squash-merge it yourself
   (Henry approved auto-merge on green CI). Red CI you cannot fix → leave the
   PR open, set the task `BLOCKED` with the reason.
7. Too big for one run? Finish a coherent slice, merge it, keep the task
   `IN_PROGRESS` and add `continue: <what is left>`.
8. Anything only Henry can do (accounts, keys, money, legal, brand, CFO
   sign-off on a template) → add it to `docs/HUMAN_TODO.md`, set the task
   `NEEDS_HENRY` if it cannot proceed, and move on to the next ready task.
9. Finish: set status `DONE`, append a 3–5 line entry to `docs/RUNLOG.md`
   (date, track, task, what changed, PR link, anything for Henry), push.
10. Last step: a short report to Henry in Russian via `SendUserMessage`
    (what was done, PR link, what needs him). No essays.

## Hard rules

- Never ask for or store secrets in the repo, chat or logs. Code reads them
  from environment variables; `.env.example` lists names only.
- Never create accounts, enter payment details, accept terms, buy anything,
  send email to real people, or deploy to production. Payments only in Stripe
  **test mode** on localhost.
- Never weaken a check, a test or the challenger to make something pass.
- Never edit another track's tasks in BACKLOG.md except to read status.
  Always `git pull --rebase` before pushing; on conflict, re-apply your edit.
- Do not invent facts in marketing copy (no fake testimonials, user counts,
  awards). Unknown numbers stay as placeholders like `[PRICE]`.
- Don't change the core idea, stack or brand without an ADR in
  `docs/DECISIONS.md` and a note to Henry.
