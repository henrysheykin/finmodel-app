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

### ADR-003 addendum (2026-10-16, E03)
- Template hooks added: `liability_lines` (working-capital liabilities such as deferred revenue —
  they flow into operating cash flow, the cash flow statement and the balance sheet),
  `extra_lines` (helper rows), `kpi_rows` (annual KPI table on the Dashboard in Full, on the P&L
  sheet in Light), `kpi_checked` (KPIs the challenger recomputes), `default_brief(stage)`.
- Every headcount role gets a fourth driver `<role>_fte_g` (headcount growth per year, applied in
  yearly steps), so staff can grow with the business. Cafe brief sets it to 0 (numbers unchanged).


### ADR-002 addendum 3 (2026-10-16)
Henry decided: **delivered workbooks carry no StartupModel branding** (no name or logo in any
sheet, file properties or footer), for all customers, so firms can pass files on as their own
work. **The 5 × Full pack ($1,250) is valid for 12 months** from purchase. E-track consequences:
the builder must not write the brand into workbooks or document properties; E11/E14 track pack
credits with a 12-month expiry.

## ADR-006 — Customer accounts by magic link; app before more templates (2026-10-17)

**Decision (Henry).** Customers sign in with a passwordless magic link sent to their email; no
passwords. The account shows "My models" (orders, status, re-download). The guest path stays:
the "model ready" email still carries a signed download link, so nobody has to sign in to get
the file they paid for.

**Priority.** The E track builds the working app first — orders and build pipeline (E09),
wizard and checkout (E10), Stripe test-mode payments (E11), customer accounts and downloads
(E19), email (E12), admin (E14) — then returns to templates (E05 real estate, E07 goal modules)
and the LLM brief builder (E08). E09 starts from template defaults + the wizard's key numbers
(no LLM call), behind an interface E08 implements later.

**Why magic link.** Customers buy rarely (one model, maybe an upgrade): a password is one more
thing to forget and a liability to store. Email is already the delivery channel, so login adds
no new dependency. Trade-off: sign-in depends on email deliverability (HUMAN_TODO A3), and
links must be single-use, short-lived and hashed at rest.


## ADR-007 — Delivery pipeline: DB-polled jobs, order state machine, signed links (2026-10-17, E09)

**Context.** One worker process, low volume at launch (tens of orders a day), Postgres in prod,
SQLite in dev. A model must never reach a customer unless the challenger passes.

**Decision.**
- `orders` (state machine `draft → awaiting_payment → paid → building → checking → ready | failed`,
  every change audited in `order_events`), `jobs` (one build job per order and round, unique
  `idempotency_key`), `artifacts` (model .xlsx + check report). Alembic owns the schema.
- Worker polls `jobs`: claims with a conditional `UPDATE … WHERE status='queued'` (atomic on SQLite
  and Postgres, no Redis), reclaims jobs stuck in `running` past 15 minutes.
- Deterministic failures (invalid brief, formula errors, challenger mismatch) fail the order at
  once and alert the admin; infrastructure errors retry with backoff 30 s → 60 s → fail on the 3rd.
- Payment is applied once per provider reference (`orders.payment_ref` unique); duplicate
  webhooks are no-ops.
- Storage adapter: local disk or S3-compatible (boto3 only when `STORAGE_BACKEND=s3`).
- Download links: `artifact.expires.HMAC-SHA256` with `SECRET_KEY`, 7-day TTL, nothing stored;
  only `model_xlsx` artifacts of `ready` orders are served. Rotating the key revokes all links.
- Briefs come from `BriefSource`; today `PrefillBriefSource` (stage defaults + key numbers, no LLM).

**Options considered.** Redis/RQ or Celery (extra service, not needed at this volume);
Postgres `SKIP LOCKED` (not portable to SQLite tests — the conditional update gives the same
guarantee for one or a few workers); storing tokens in the DB (revocable per link, but more state —
E19 sessions will be DB-backed, download links stay stateless).

**Consequences.** Throughput is bounded by LibreOffice (~15–20 s per Light build incl. challenger);
E17 load-tests 50 concurrent builds. Customer-facing failure messages wait for D9 / E12.

## ADR-008 — Deploy shape: one Railway service running web + worker (2026-10-17, E15)

**Context.** Henry wants the site live within days on accounts he already has (Railway,
Cloudflare, Stripe). The web app and the worker share built files; on Railway a volume attaches to
one service only, and Railway's `railway.json` (config as code) is deprecated for new services.

**Decision.**
- One Railway service from the repo `Dockerfile`. `deploy/start.sh` (the image `CMD`) fixes the
  volume ownership as root, drops to the `app` user, runs `python -m app.manage check` and
  `migrate`, then starts `worker.main` and uvicorn (`--proxy-headers`) in the same container. If
  either process exits, the container exits and Railway restarts it.
- Railway Postgres; a volume mounted at `/data` (`STORAGE_DIR=/data/storage`, set in the image).
- No `railway.json`: healthcheck path and volume are set once in the Railway UI (`docs/DEPLOY.md`),
  so nothing depends on the deprecated format.
- Cloudflare: registrar + DNS, apex CNAME (flattened) to Railway, proxied, SSL mode Full.
- `DATABASE_URL` from Railway (`postgresql://`) is normalised to `postgresql+psycopg://`.
- App and worker log through `app.logs.configure_logging` (uvicorn alone drops app INFO events).

**Options considered.** Separate web and worker services with Cloudflare R2 for files (cleaner
scaling, but one more account and keys to set up before launch — the S3 adapter already exists, so
this is a later switch of env vars); Vercel (no long-running worker or LibreOffice).

**Consequences.** One container builds models and serves pages; a long build cannot block requests
(separate processes), but scaling out means moving files to R2 first. Worker and web restart together.

## ADR-009 — Template catalog: one file per industry (2026-10-17, E20)

**Context.** Henry wants new models added over time. Adding an industry used to touch seven places
(template file, registry tuple, `BusinessType` literal, briefing map, wizard list, wizard key numbers,
landing samples), which invites drift between the wizard, the schema and the site.

**Decision.**
- `engine/templates/__init__.py` discovers every concrete `Template` subclass in the package; the
  registry is sorted by the template's `order`.
- Catalog data lives on the template: `title` (wizard and landing label), `business_types`, `order`,
  `key_numbers` (wizard step 5), `sample_title` / `sample_desc` / `sample_stage` (landing samples,
  `scripts/build_samples.py`).
- `PLANNED` announces industries before their template exists ("(coming soon)" in the wizard); an entry
  disappears automatically once a template serves its business type.
- `Brief.business_type` is a snake_case string validated against the catalog (served + planned +
  `other`) instead of a hand-written `Literal`.
- The cafe template's `default_brief(stage)` returns `engine/briefs/cafe.json` (the briefing special case
  is gone).
- `tests/test_catalog.py` checks every registered template automatically (discovery, key numbers exist,
  stage defaults validate, wizard/briefing/landing consistency, samples present).

**Consequences.** A new industry is its template file + tests + sample + memo
(`docs/templates/ADDING_A_TEMPLATE.md`). E08's LLM brief builder must take the business-type enum from
`known_business_types()` when it builds its JSON schema.

## ADR-010 — Goal modules: the wizard's goal adds sheets (2026-10-17, E07)

**Context.** The wizard asks for a main goal (break-even, DCF valuation, investor pitch), but the workbook
was the same for every goal.

**Decision.**
- `engine/goals.py` maps a goal to modules: `startup_breakeven` → Break-even sheet, `dcf_valuation` →
  Valuation sheet, `investor_pitch` → Summary (first sheet) + both. `revenue_profit` / `other` add nothing.
- Modules work in every template and both tiers; they read the period grid only (plus a few helper lines
  appended to it: net-income flag, cash flow before financing and its running minimum, payback flag,
  unlevered free cash flow), so they never change an existing number.
- A module's inputs are ordinary drivers with Low / Base / High (`cash_buffer`; `wacc`, `tg`, `exit_mult`,
  `wacc_step`, `g_step`), required only for goals that use them (`Template.all_specs(roles, goal)`).
  `apply_goal(brief, goal)` adds the stage defaults (the wizard's prefill path calls it) and drops unused
  ones. Brief validation refuses WACC − g < 1 pp.
- `engine/goal_sheets.py` lays the sheets out at plan time, so the manifest carries every module cell
  (`goal_cells`, `goal_years`); the challenger compares them with `goals.reference` (plain Python). New
  in-file checks: funding table ties to cash, discounting ties to `NPV()`, WACC > g, sensitivity centre =
  enterprise value, Summary ties to period detail; WARN when final-year free cash flow ≤ 0.
- Assumptions and CFO questions: `docs/templates/goal-modules.md`.

**Consequences.** The LLM brief builder (E08) must fill the goal drivers or call `apply_goal`. Light-plan
customers who pick "Investor-ready pitch model" get the Summary, Break-even and Valuation sheets on top of
Light (HUMAN_TODO D12 asks whether that goal should require Full).

## ADR-011 — Property economics: annuity loans, land, Returns sheet (2026-10-18, E05)

**Context.** A rental-property model needs three things the shared engine did not have: a mortgage with a
level payment, land that is never depreciated, and investor returns (IRR / NPV with a sale at the horizon).

**Decision.**
- `Template.loan_style`: `"straight"` (default, unchanged: equal principal, interest on the average balance)
  or `"annuity"` (level payment from Excel `PMT`, interest on the balance after drawdown at the start of the
  period, principal = payment − interest, capped at the balance). Grid lines `loan_pmt` and `debt_service`
  appear only for annuity loans. `engine.core.reference_run(..., loan_style)` is the plain-Python twin.
- Land: a template whose capex includes a `capex_land` line gets a `land` line (at cost); depreciation runs
  on fixed assets less land and stops at the building value. `Top.land` carries it in the twin.
- `Template.returns = True` adds the **Returns** sheet (`engine/returns.py`, both tiers, before goal
  sheets): year 0 = purchase (price + closing costs, less the loan for equity), years 1..H = NOI (EBITDA) −
  capital reserves (capex other than `capex_buy`) and, levered, interest + principal; sale at the end of
  year H = next-year NOI ÷ exit cap rate less selling costs, levered repays the loan balance. Unlevered and
  levered IRR (Excel `IRR` with a starting estimate (inflows ÷ outflows)^(1/H) − 1; "n/a" unless the flows
  change sign exactly once and return at least 25% of the money put in, so the IRR is unique and Excel's
  search is reliable — the twin applies the same rule), NPV at a discount rate,
  multiple, going-in cap rate, DSCR and cash-on-cash by year. Cash flows are before income tax.
- The challenger recomputes every Returns cell (`returns.reference`; IRR by bisection, within 0.01 pp;
  ratios 1e-6; money $1). New in-file checks: NOI ties to EBITDA, purchase ties to capex, loan fully repaid
  at sale, both IRRs discount their flows to zero; WARN when DSCR < 1.0x in any year.

**Consequences.** Existing templates build byte-for-byte the same formulas (straight loans, no land, no
Returns sheet). If Excel's IRR cannot find the root the bisection finds (e.g. flows with several sign
changes) the cell shows "n/a", the challenger fails the model and it is not delivered.

## ADR-012 — Brief builder LLM provider: OpenAI instead of Anthropic (2026-10-18, Henry)

**Context.** E08 (PR #39) and the E23 eval harness (PR #40) call the Claude API (`ANTHROPIC_API_KEY`,
`BRIEF_MODEL`, off by default). Henry, 2026-10-18: there will be OpenAI API keys; asked "add a provider or
replace Anthropic?", he chose **replace**.

**Decision.**
- The brief builder talks to the OpenAI API only. Env: `OPENAI_API_KEY` + `BRIEF_MODEL` (an OpenAI model id;
  empty = LLM off, prefill only, as today). `ANTHROPIC_API_KEY` and the Anthropic client are removed.
- Nothing else in the architecture changes: the LLM still only fills the validated brief through one forced
  tool / function call that may change driver Low/Base/High only; same validation, retries, 15 s deadline,
  prefill fallback, usage log line, fixtures in tests (never the live API).
- E23 compares OpenAI models instead (candidates from the pricing page 2026-10-18: `gpt-6-luna`,
  `gpt-6.1-sol`, `gpt-6-astra`; reference = the strongest model; check function-calling support and prices
  when implementing).
- `content/legal/privacy.md` names OpenAI instead of Anthropic as the processor of wizard answers and notes.

**Consequences.** Task E25 does the switch before E23's live run. Agent sessions themselves still run on
Claude (Claude Code); this ADR is about the product's runtime LLM only.

## ADR-013 — Workbook standard v1: one sheet set, layout and look for every model (2026-10-20, Henry)

**Context.** Delivered workbooks differed by goal (ADR-010 added Summary / Break-even / Valuation only for some
goals), had no charts, and still used the v1 navy look in the files. Henry shared his own reference model and asked
for one standard for the whole library: a visual dashboard, scenarios side by side, statements summary with
charts, break-even, valuation, sources & uses, ratios. Two prototype rounds on a real engine workbook
(`design/workbook-standard-v1-prototype.xlsx`); Henry approved the result and the Light / Full split on 2026-10-20.

**Decision.** `docs/WORKBOOK_STANDARD.md` is binding for every template and tier:
- Sheet set by **tier**, not by goal. Light ($149): Cover, Dashboard, Inputs, P&L, Break-even, Checks.
  Full ($349): Cover, Dashboard, Summary, Scenarios, Break-even, Valuation, Sources & Uses, KPIs, [industry
  sheets], Inputs, P&L, Cash Flow, Balance Sheet, calculation sheets, Checks.
- The wizard goal sets the Cover's purpose line only (supersedes the "goal adds sheets" part of ADR-010; the
  module code and its challenger coverage stay, driven by the tier). The investor Summary sheet is retired: its
  content moves to the Dashboard (tiles, Funding & valuation). Closes HUMAN_TODO D12.
- The scenario selector is Dashboard!B4 in both tiers (Light used Inputs!B3).
- Scenarios shows Low / Base / High **live** (parallel calculation chains on the inputs' B / C / D columns),
  recomputed by the challenger like the active scenario.
- Look: Arial 9, ink / pine palette (the site's identity, ADR-005; ends the navy bands in files), yellow input cells
  with blue figures, presentation sheets in $'000 with ink links, native charts in a two-column grid of one size.

**Consequences.**
- CLAUDE.md Excel rules change: yellow fill marks inputs (was: only the scenario selector); green links on
  Inputs and calculation sheets only.
- Engine work E26–E33 (BACKLOG); samples, golden tests, landing preview and SEO samples are rebuilt at the end
  (E33). Customer-facing copy that says "the goal adds sheets" is updated in the same task.
- Light → Full upgrade still never changes a figure (same calculation lines; Full adds sheets).
- The R1 CFO reviews of template logic stay valid; the new sheets (Scenarios, Sources & Uses, ratios) get their
  own R1 line after E33.
