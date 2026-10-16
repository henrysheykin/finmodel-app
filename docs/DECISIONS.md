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

## ADR-002 — Brand, domain, pricing, FinModelsLab separation (2026-10-16)

**Status:** Accepted (Full price pending) · **Deciders:** Henry (domain list, price, brands), M track (pick from the list)

### Context
M01/M02 (`docs/marketing/competitors.md`, `docs/marketing/positioning.md`) showed
the working name Ledgerline is weak (crowded "ledger" root, an existing "Ledgerline CPA"
template). Henry supplied six domains he can use: financial-model.net,
financialmodeltemplates.com, financialmodelstartup.com, startup-model.com,
startupfinancialmodels.com, startupfinancialprojection.com — and asked the agent to pick one
and derive the name from it.

### Decision
- **Domain: startup-model.com. Brand: StartupModel** (one word, camel case; "StartupModel.com"
  in the logo lock-up is acceptable). Replaces Ledgerline everywhere.
- **Brands are separate:** no FinModelsLab name, links, copy or cross-promotion on
  StartupModel, and no FinModelsLab -> StartupModel upgrade credit.
- **Light = $149.** Bundles: yes (accountant/advisor credit pack; Light -> Full upgrade
  = pay the difference). **Full price: pending Henry** (M02 recommends $349).

### Why startup-model.com
| Domain | Verdict |
|---|---|
| startup-model.com | **Chosen.** Shortest .com; "model" names exactly what we deliver; "startup" matches all three ICPs (startup SBA/bank loans, E-2/visa new businesses, pre-seed founders); no "templates" in the name, which keeps it distinct from FinModelsLab and from template marketplaces. |
| financial-model.net | Runner-up. Broadest, but .net + hyphen leak traffic to the .com, and it reads close to the existing marketplace eFinancialModels. |
| financialmodeltemplates.com | Rejected: "templates" contradicts "built on your numbers" and competes head-on with FinModelsLab. |
| startupfinancialmodels.com | Rejected: long; plural reads like a template catalogue. |
| startupfinancialprojection.com | Rejected as primary: 30 characters, singular; usable later as a redirect for loan/visa campaigns. |
| financialmodelstartup.com | Rejected: unnatural word order. |

### Consequences
- The name is descriptive, so a word-mark is hard to register; protection comes from a
  logo/stylised mark and from the product. Henry: check TMview / USPTO for "StartupModel" in
  classes 9, 35, 36, 42 and, if affordable, also get startupmodel.com (no hyphen) as a redirect.
- **Collision to check (CAUTION):** a financial-model seller "Startup Models" exists
  (startupmodels.co, not fetchable — robots; press: https://siliconprairienews.com/?p=2966).
  Plural/.co vs our singular/.com, but same field. Henry: check whether it is active and
  whether it holds a mark before spending on the brand. Fallback: financial-model.net.
- Copy must not imply the product is only for startups: the wizard covers established
  businesses too ("for new and growing businesses").
- E track: replace "Ledgerline" in `app/` and the landing build (E13) with StartupModel;
  `design/landing.dc.html` keeps the old name until E13 rebuilds it.
- Prices come from config (E11); tier names stay Light / Full.

### ADR-002 addendum (2026-10-16)
Henry checked startupmodels.co: not active, not a concern. The startup-model.com /
StartupModel choice stands; financial-model.net is no longer needed as a fallback.
Full price is still open, so copy uses `[PRICE_FULL]`.

### ADR-002 addendum 2 (2026-10-16)
Henry approved the M02 prices: **Light $149, Full $349, accountant/adviser pack 5 × Full for
$1,250**; Light -> Full upgrade = pay the difference. **Refund window: 7 days.** E11 reads
prices from config; M08 legal drafts use the 7-day refund window.

## ADR-003 — Engine framework (2026-10-16, E02)

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

## ADR-004 — Payments: Stripe; hosting: Railway (2026-10-16)

**Status:** Accepted · **Deciders:** Henry ("stripe", "vercel/railway"), M track (recorded, picked Railway)

### Decision
- **Payments: Stripe Checkout** (test mode until go-live). No merchant of record, so the
  Lemon Squeezy / Paddle adapter stub in E11 is optional, not required.
- **Hosting: Railway** — the one Docker image from ADR-001 deployed as two services (web,
  `python -m worker.main`) plus a Railway Postgres; secrets only in Railway variables.

### Why Railway, not Vercel
Vercel runs serverless functions and static sites; it does not run a persistent worker
process polling the jobs table, and the LibreOffice recalculation needs a full container.
Railway runs our Dockerfile as-is, including a long-running worker, and offers managed
Postgres. Splitting the landing onto Vercel would break ADR-001's single server-rendered
app for little gain.

### Consequences
- E15 `docs/DEPLOY.md` targets Railway first (other Docker hosts stay as alternatives).
- E11 Stripe webhook URL will be the Railway domain / startup-model.com.
- Henry owns VAT / sales-tax handling (Stripe Tax or own registration) — HUMAN_TODO D2.

## ADR-005 — Own visual identity for the landing, design v2 (2026-10-16)

**Status:** Accepted · **Deciders:** Henry (asked for a distinct look and texts), setup session

- Decision: replace design v1 (same palette, font, section order and signature blocks as
  getdraftplan.com) with design v2 in `design/`, now carrying the StartupModel brand, the
  approved prices (ADR-002) and the M02 positioning ("proof, not AI", three ICPs).
- Why: v1 copy was ours, but its visual language was close enough to read as a copy.
- v2: accountant's analysis-pad identity (ink #1B2A2F, pine #0F6E56, pad paper #F7F8F3
  with ruling, red auditor tick marks, double-underlined totals), Schibsted Grotesk +
  IBM Plex Sans with tabular figures; a dark "checks" section as the differentiator;
  tables instead of cards for the sheet list and the comparison; Light and Full side by
  side; no scroll-reveal animation. Never reintroduce navy #1F3864 + blue #2563EB, DM Sans,
  quote cards, "VS" cards or a single price card.
- Copy: v2 copy follows M02/M03 messaging and guardrails (no Google Sheets/Numbers claim
  until verified, `[DELIVERY_TIME]` placeholder, templates described neutrally). Where
  `content/landing.md` (written for v1 sections) and the design disagree on structure,
  the design wins; `content/landing.md` still owns meta, SEO/JSON-LD notes and placeholders.
- Consequence: SPEC_LANDING sections 3–5 and 7 are superseded; E13 builds from `design/`.
