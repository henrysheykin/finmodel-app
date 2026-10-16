# Decisions

Short ADRs. Format: id, date, decision, why, consequences. Append, never rewrite.

## ADR-000 — Working agreement (2026-10-16)
- Code lives in this repo; autonomous scheduled sessions build it task by task
  from `docs/BACKLOG.md` following the protocol in `CLAUDE.md`.
- Agents squash-merge their own PRs when CI is green (approved by Henry).
- Engineering track runs daily, marketing on weekdays, PM review on Mondays.
- The LLM fills a validated brief; deterministic templates build the workbook;
  an independent challenger must pass before any delivery.

## ADR-001 — Stack (2026-10-16)

**Status:** Accepted · **Deciders:** Henry (stack proposed in CLAUDE.md), E01 run

### Context
One-person product run by autonomous agent sessions. Workload: a few orders a
day at first, each a CPU-bound workbook build (openpyxl write → LibreOffice
recalc ×3 scenarios → challenger), 2–10 s per model. Needs: deterministic,
testable engine; cheap single-host deploy; no secrets in the repo; simple
enough that a fresh session can pick up any task from the backlog.

### Decision
- **Python 3.12** everywhere (engine, web, worker) — one language, openpyxl lives here.
- **FastAPI + Jinja2** server-rendered pages + vanilla JS; no SPA framework.
- **SQLAlchemy 2 + Alembic**; SQLite in dev/tests, Postgres in prod.
- **Worker = separate process polling a `jobs` table** (`SELECT … FOR UPDATE SKIP LOCKED`
  on Postgres); no Redis/Celery.
- **openpyxl** writes, **LibreOffice headless** recalculates (`engine/recalc.py`:
  throwaway profile with "always recalc on load", `--convert-to xlsx`, then an
  error scan of every cell).
- **Adapters** with fake/console implementations: payments (Stripe Checkout
  first), email (Resend/Postmark), storage (local/S3), LLM (Anthropic SDK,
  recorded fixtures in tests).
- **pytest + ruff**; GitHub Actions installs LibreOffice and runs everything;
  LibreOffice tests are marked `libreoffice` and are mandatory in CI
  (`REQUIRE_LIBREOFFICE=1`), skippable locally only when soffice is absent.
- **One Docker image** (python:3.12-slim + libreoffice-calc-nogui); web is the
  default command, worker is `python -m worker.main`.

### Options considered
| Option | Complexity | Cost | Fit |
|---|---|---|---|
| A. Python monolith (chosen) | Low | 1 small host | Engine already Python; agents handle one stack |
| B. Next.js front + Python engine service | Medium | 2 deployables | Two stacks, two CIs, more agent context per task |
| C. Celery + Redis queue | Medium | extra service | Unneeded at <1k jobs/day; DB-polled queue is enough |
| D. Recalc via a formula library (pycel/formulas) instead of LibreOffice | Low | none | Not a real spreadsheet engine; would not catch what Excel users see |

### Consequences
- Easier: one image, one language, full engine test in CI on every PR.
- Harder: LibreOffice is slow to start (~1–2 s per call) and is not Excel —
  the formula whitelist (Excel-2007-era functions) is the guard.
- Revisit: if build volume needs parallelism beyond one worker, run more
  worker containers against the same jobs table before adding a broker.

## ADR-002 — Engine framework (2026-10-16, E02)

**Status:** Accepted · **Deciders:** E02 run; economics choices flagged for Henry's CFO review (R1)

### Decision
- **Brief carries values only.** `engine/brief.py` (pydantic, `extra="forbid"`): template, business type,
  goal, stage, horizon 1/3/5, granularity, tier, default scenario, roles, and drivers as
  `{key, low, base, high, note?}`. Labels, units, formats, bounds and Low/Base/High ordering live in
  the template's `DriverSpec`s, so an LLM cannot change presentation or slip past a bound.
- **Template = top half only.** A template supplies driver specs, revenue/COGS lines, opex lines,
  capex lines (in a small formula language, `engine/spec.py`) and a plain-Python twin
  (`reference_top`). The framework (`engine/core.py`) adds headcount by role, P&L tail, fixed assets,
  working capital, debt, cash flow and balance sheet — in both formula and Python form.
- **One formula text per line for every period** (optional `first` for period 1), rendered per
  column — the "same formula across periods" rule holds by construction and is tested.
- **Tiers differ in presentation only.** Light = Inputs (with scenario selector) + P&L (annual summary
  + period detail) + Checks. Full = Dashboard, Inputs, Monthly/Annual, P&L, Cash Flow, Balance Sheet,
  Headcount, Checks. Same calculation lines ⇒ identical numbers (tested), so a Light→Full upgrade
  never changes a figure.
- **Annual granularity computes on annual columns**, with formulas that give the same yearly revenue,
  gross profit, EBITDA and payroll as the monthly model (e.g. the cafe traffic ramp uses the exact
  average of the monthly ramp). Debt timing and tax differ slightly by design (repayments start the
  period after drawdown; tax is assessed per period).
- **Challenger** recomputes every scenario-year from the brief with `reference_run` + the template's
  `reference_top` (no shared code with the formula builder) and requires: 0 formula errors, ≤ $1
  difference on revenue, gross profit, EBITDA, net income, year-end cash and loan (+ total assets and
  CFO in full tier), assets = liabilities + equity, in-file verdict PASS, revenue Low < Base < High.

### Economics defaults (for CFO review)
- Tax: losses carried forward without limit (tax paid when cumulative pre-tax income reaches a new
  high); no tax refunds, no tax payable timing.
- Depreciation: straight line on cumulative capex over `dep_years`, never below zero net book value.
- Loan: drawn in period 1, straight-line principal from period 2 over the term; interest on the
  average balance after drawdown.
- Working capital: AR = revenue × days / 30 (or 360); inventory and AP on COGS days.
- Funding: equity and loan both arrive in period 1; opening balance sheet is empty.

### Consequences
- A new template (E03–E06) is ~150 lines: specs, top-half lines, Python twin, default brief.
- Revisit: multi-vintage depreciation, tax payable timing, revolving credit, and goal modules (E07).
