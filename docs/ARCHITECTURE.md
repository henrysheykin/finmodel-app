# Architecture and background

Detail moved out of `CLAUDE.md` on 2026-10-18 to keep the per-run context small. The rules themselves
stay in `CLAUDE.md`; this file explains them. Decisions with their reasons: `docs/DECISIONS.md` (ADRs).

## Product

A web app that sells custom Excel financial models. The customer answers a short wizard (business type,
goal, stage, horizon, granularity, a few key numbers), pays once, and receives an `.xlsx` with live
formulas, a Low / Base / High scenario switch and a Checks sheet. Reference competitor: getdraftplan.com
(`docs/research/draftplan.md`). Brand **StartupModel**, domain **startup-model.com** (ADR-002; it replaced
the old working name Ledgerline). Owner: Henry Sheykin (CFO, 20+ years, ~200 financial models built).
StartupModel is kept separate from Henry's FinModelsLab brand (D5).

## The core idea

The LLM never writes workbook code. It only fills a validated **brief** (JSON: drivers with
Low/Base/High values). Deterministic Python **templates** build the workbook. LibreOffice recalculates
it. An independent **challenger** recomputes the numbers in plain Python and must match every
scenario-year within $1, and the in-file Checks sheet must not FAIL. A model that fails is never
delivered. The prototype of all three is in `poc/` (cafe template: 894 formulas, 0 errors, all 9
scenario-years match).

Today briefs come from `app/briefing.PrefillBriefSource` (template stage defaults + the customer's key
numbers, no LLM). The LLM brief builder (E08) plugs in behind the same `BriefSource` interface;
`adapters/llm.py` holds its model choice (`BRIEF_MODEL`), prompt-caching layout and per-order token log.

## Stack (ADR-001)

- Python 3.12, FastAPI, Jinja2 server-rendered pages + vanilla JS (no SPA framework).
- SQLAlchemy 2; SQLite in dev/tests, Postgres in prod. Alembic migrations.
- Worker = separate process polling a `jobs` table (no Redis).
- openpyxl to write, LibreOffice headless (`soffice`) to recalculate.
- Adapters with a fake/console implementation for tests: payments (Stripe Checkout), email (Resend or
  Postmark), storage (local disk / S3), LLM (Anthropic API; tests use recorded fixtures, never the live API).
- pytest, ruff; GitHub Actions CI installs LibreOffice and runs everything.
- One Docker image (app + worker commands). Production: one Railway service + Postgres + `/data` volume
  (ADR-008, `docs/DEPLOY.md`).

Repo layout: `engine/` (templates, brief schema, recalc, challenger), `app/` (web, API, wizard, admin),
`worker/`, `adapters/`, `web/` (landing, static), `content/` (copy, SEO pages, emails, legal), `tests/`,
`docs/`, `evals/` (model evals, planned E23), `.claude/agents/` (subagents: scout, implementer, reviewer).

## Design source

- **Design v2 (2026-10-16)** is the source of truth for look, copy and section order:
  `design/landing.dc.html` and `design/tokens.dc.html` (exact colours, type, components). Identity:
  accountant's analysis pad — ink #1B2A2F, pine #0F6E56, pad paper #F7F8F3 with 32 px ruling, red
  auditor tick marks #B8322A, double-underlined totals; Schibsted Grotesk + IBM Plex Sans with tabular
  figures. Canvas: https://claude.ai/artifact/4qNJgJzUU633rZ9A7vhQJj
- Hero spreadsheet (2026-10-18, Henry: "must look like real Excel"): the reference is the live code —
  `app/xlview.py` + `web/static/landing.js` render the real sample workbook in a spreadsheet-app window
  (ribbon, name box, formula bar, gridlines, frozen panes, B4 list, sheet tabs, status bar). It
  supersedes the hero in the canvas.
- Why the competitor palette is banned: the v1 look copied the competitor's visual language too closely
  and was replaced (ADR-005).
- Landing build spec (Russian): Claude Docs
  https://claude.ai/code/artifact/73230182-c0f4-4cb1-a600-8551781f182c — export it to
  `docs/SPEC_LANDING.md` when needed. Its sections 3–5 and 7 are superseded by design v2; sections 6 and
  8–11 (mockup logic, responsive, SEO, accessibility, config, acceptance) still apply.

## Why the token budget and model routing (2026-10-18)

Every scheduled run starts from zero and pays for everything it reads. Most of the cost was long reads
(this background, the full run log, finished backlog tasks, full test and LibreOffice output) and runs
that had nothing to do. So: a slim `CLAUDE.md`, finished tasks in `docs/DONE.md`, the run log capped at
10 recent entries (`docs/runlog/` keeps the rest), an early exit when everything waits on Henry, and each
kind of work on the cheapest model that does it well — opus where a wrong number or a security hole
would reach a customer, sonnet for pattern work, haiku for lookups and log keeping.
