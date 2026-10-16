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
