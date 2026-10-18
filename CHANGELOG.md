# Changelog

Versions follow `app.__version__` (= `[project].version` in `pyproject.toml`); `/healthz` and the first
deploy-log line report the running version. Each release is a git tag `vX.Y.Z` on `main`.

## v0.1.0 — 2026-10-18 (release candidate)

First version that can take a real order end to end. Not live yet: going live is Henry's checklist in
`docs/RUNBOOK_GO_LIVE.md`.

**Customer path.** Landing page from design v2 with the real sample workbook in a spreadsheet window (#25,
#27, #30) → wizard: business type, goal, stage, horizon, granularity, key numbers, plan, email (E10, #19)
→ Stripe Checkout, signed webhooks, refunds (E11, #20) → build worker: brief → workbook → LibreOffice
recalculation → independent challenger → stored file (E09, #18) → emails through Resend or Postmark (E12,
#22) → magic-link sign-in and "My models" downloads (E19, #21).

**Models.** Seven industries — cafe/restaurant, SaaS (#12), retail/e-commerce (#14), professional services
(#16), home services, fitness (#25), real estate with annuity mortgage and IRR/NPV Returns sheet (#33);
Light and Full plans, monthly or annual, 1/3/5 years, Low/Base/High scenarios, Checks sheet; goal modules
break-even and funding need, DCF valuation, investor summary (E07, #26). New industries are one file each
(template catalog, ADR-009). A model that does not match the challenger within $1 or fails a check is
never delivered.

**Operations.** One Docker container on Railway (migrations + worker + web, ADR-008), Postgres, volume
for files (#25); admin panel with orders, re-build, refund, re-send, download (E14, #23); rate limits,
security headers, CSP, cross-site POST refusal, docker compose stack with an end-to-end test in CI (#31);
hardening review with 10 fixes and a load test of 50 builds on one worker (E17, #32); SEO pages engine
with engine-built samples (E16, #29).

**This release (E18).** Version 0.1.0 shown by `/healthz` and `python -m app.manage check`; go-live
preflight (`python -m app.manage preflight`, run in every deploy log, and a "Before live payments" box at
the top of `/admin`) that lists what still blocks live payments; go-live runbook
`docs/RUNBOOK_GO_LIVE.md`; release checklist `docs/reviews/E18-release-checklist.md`.

**Known gaps (not blocking the tag).** Legal texts (HUMAN_TODO L1) and the failed-build policy (D9) are
Henry's; five-model pack and Light→Full upgrade are manual (D11); LLM brief builder (E08) not started —
briefs come from stage defaults plus the customer's key numbers; follow-up emails (day 1, day 7,
abandoned checkout) are written but not sent.
