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

## ADR-003 — Payments: Stripe; hosting: Railway (2026-10-16)

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
