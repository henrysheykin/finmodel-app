# Release checklist: StartupModel v0.1.0

**Date:** 2026-10-18 · **Prepared by:** scheduled E-track run (E18) · **Deployer:** Henry (Railway)

Release = git tag `v0.1.0` on `main` after the E18 merge. Production deployment and the switch to live
payments are Henry's: `docs/RUNBOOK_GO_LIVE.md`.

## Pre-deploy

- [x] **CI green on `main`** — run 128 (`656caf5`, after E05 #33): lint, tests incl. LibreOffice and
      browser, `audit`, `docker`, `compose` E2E. The E18 PR runs the same jobs before merge.
- [x] **Full suite locally** on the E18 branch (Python 3.12, LibreOffice): see the PR for the count;
      `ruff check` + `ruff format --check` clean.
- [x] **Dependency audit** — `pip-audit -r constraints.txt`: no known vulnerabilities (2026-10-18).
- [x] **Code reviewed** — E17 hardening review `docs/reviews/E17-hardening.md`: 10 findings fixed, no open
      high-severity items. Every change since went through a PR with green CI.
- [x] **No known critical bugs** — no open issues; RUNLOG notes only copy items (below).
- [x] **Database migrations** — 3 Alembic revisions (`0001`–`0003`), applied on every container start
      (`deploy/start.sh`), tested on SQLite and on Postgres 16 in the compose E2E. v0.1.0 adds none.
- [x] **Load** — 50 orders on one worker: 50/50 ready, ~7.8 s per model (`docs/reviews/load-test-50.json`).
- [x] **Feature flags** — the only one is `ALLOW_LIVE_PAYMENTS` (live Stripe keys refused without it).
- [x] **Rollback plan documented** — `docs/RUNBOOK_GO_LIVE.md` "Rollback".
- [x] **Version visible** — `/healthz` → `"version": "0.1.0"`; deploy log `v0.1.0 env=…`.
- [x] **Go-live gaps visible** — `python -m app.manage preflight` in every deploy log and the
      "Before live payments" box on `/admin`.

## Production state observed 2026-10-18 (read-only checks from outside)

- `https://finmodel-app-production.up.railway.app/healthz` → ok (pre-0.1.0 build, no version field).
- `https://startup-model.com/healthz` → ok through Cloudflare (HSTS, CSP present): the domain is connected.
- `https://startup-model.com/sitemap.xml` lists Railway addresses → `PUBLIC_BASE_URL` not switched yet.
- `/privacy` says "being prepared" → legal texts (L1) not added yet.

## Deploy (Henry, runbook steps 1–5)

- [ ] Railway deploys `main`; deploy log shows `v0.1.0` and the preflight
- [ ] Variables: `CLIENT_IP_HEADER`, `ADMIN_EMAIL`, `PUBLIC_BASE_URL`, `EMAIL_FROM` on the verified domain
- [ ] Legal texts published
- [ ] Test-mode order on `https://startup-model.com`: email → download → Checks PASS → refund

## Go live (Henry, runbook steps 6–8)

- [ ] Stripe account activated, public name StartupModel
- [ ] Live webhook + live key + `ALLOW_LIVE_PAYMENTS=1` in one save; preflight `READY for live payments`
- [ ] One real purchase with own card, then refund from `/admin`

## Post-deploy

- [ ] `/admin` Failed = 0 daily for the first week; Stripe webhooks without failures
- [ ] Railway Postgres backups enabled
- [ ] HUMAN_TODO G1 ticked with the date

## Rollback triggers

- A paid order not `ready` within 15 minutes, or any order `failed`
- `/healthz` down or the container restarting in a loop
- Failing Stripe webhook deliveries
- A customer reports formula errors or a Checks FAIL

## Known issues shipped in v0.1.0 (not blocking)

| Item | Owner | Effect |
|---|---|---|
| Failed-build policy D9 (`[FAILED_BUILD_POLICY]` in `content/email/build-failed.md`) | Henry | the customer gets no failure email; admin is alerted and refunds by hand |
| Model-ready email mentions a follow-up note "tomorrow" that is not sent yet (RUNLOG 2026-10-17) | M track | promise without delivery — remove the line or ship the day-1 email |
| Five-model pack and Light→Full upgrade are manual (D11) | Henry | "write to us" on the landing |
| LLM brief builder E08 not built | E track | briefs come from stage defaults + the customer's key numbers; free text is not used |
| Rate-limit counters are per process, reset on restart | — | acceptable for one container (`docs/DEPLOY.md`) |
| No "pause sales" switch; stopping orders means removing the deployment | E track (candidate) | site offline during an emergency stop |
