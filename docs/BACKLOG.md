# Backlog

Status values: `TODO` · `IN_PROGRESS (date)` · `DONE (date, PR)` ·
`BLOCKED: reason` · `NEEDS_HENRY: what`. Protocol: see `CLAUDE.md`.
Each track edits only its own section. Pick the first ready task in your track.

Skill names are as shown in the session's skill list (prefixes may differ:
`xlsx` may appear as `anthropic-skills:xlsx`). "(opt)" = use if installed.

---

## Track E — Engineering (daily)

### E01 — Repo scaffold, CI, port the prototype
- status: DONE (2026-10-16, https://github.com/henrysheykin/finmodel-app/pull/1)
- depends: —
- skills: engineering:architecture, engineering:testing-strategy, xlsx
- do: pyproject (Python 3.12, ruff, pytest), layout from CLAUDE.md, `.env.example`,
  Dockerfile with LibreOffice, GitHub Actions CI (install LibreOffice, ruff, pytest).
  Write `engine/recalc.py` — our own headless LibreOffice recalculation (the
  prototype used a sandbox-only script; do not depend on `/mnt/skills`). Port
  `poc/generate_model.py` and `poc/challenger.py` into `engine/` unchanged in
  behaviour. Write ADR-001 (stack) in docs/DECISIONS.md.
- done when: CI green on main; a test generates the cafe model, recalculates it
  (0 errors) and the challenger passes all 3 scenarios.

### E02 — Engine framework: brief schema, template base, tiers, 3 statements
- status: TODO
- depends: E01
- skills: xlsx, engineering:system-design, engineering:testing-strategy
- do: pydantic `Brief` schema (business_type, goal, stage, horizon 1/3/5,
  granularity monthly/annual, tier light/full, drivers with low/base/high, units,
  formats, ordering rules). `Template` base class + shared style kit + common
  sheet builders (Dashboard, Inputs, Checks). Tiers: **light** = one P&L sheet
  + Inputs + Checks; **full** = Dashboard, Inputs, Monthly, P&L, Cash Flow,
  Balance Sheet (must balance every period — add as a Check), Headcount, Checks.
  Annual granularity variant. Challenger generalised: each template ships a
  pure-Python reference model. Migrate cafe to the framework.
- done when: cafe light+full × monthly+annual × 1/3/5 years all generate, recalc
  with 0 errors, balance sheet balances, challenger PASS; golden tests in CI.

### E03 — Template: SaaS / Software
- status: TODO
- depends: E02
- skills: xlsx, engineering:testing-strategy
- do: subscription build (new customers by channel, CAC, churn, ARPA, expansion,
  MRR/ARR waterfall), COGS/hosting, headcount-driven opex, deferred revenue
  simplified, runway. Defaults for planning/early/growing/established stages.
  Produce `samples/saas-full.xlsx` + `docs/templates/saas.md` (assumption memo).
- done when: generator+challenger tests pass for all tier/horizon combos; then
  add "CFO review: SaaS template" to HUMAN_TODO (does not block next tasks).

### E04 — Template: Retail / E-commerce
- status: TODO
- depends: E02
- skills: xlsx
- do: traffic × conversion × AOV (e-com) or stores × sales/sqft (retail), returns,
  COGS, inventory days & working capital in cash flow, fulfilment, ad spend/CAC.
  Sample + assumption memo; HUMAN_TODO CFO review.
- done when: as E03.

### E05 — Template: Real estate (rental property investment)
- status: TODO
- depends: E02
- skills: xlsx
- do: purchase price, closing costs, LTV/rate/term loan with amortisation
  schedule, rent roll, vacancy, opex, NOI, cap rate, cash-on-cash, DSCR, exit
  value, levered/unlevered IRR (IRR function), NPV. Sample + memo; HUMAN_TODO.
- done when: as E03; challenger checks IRR within 0.01 pp.

### E06 — Template: Professional services
- status: TODO
- depends: E02
- skills: xlsx
- do: billable headcount, utilisation, rate card, retainer vs project mix,
  receivable days, contractor vs employee cost. Sample + memo; HUMAN_TODO.
- done when: as E03.

### E07 — Goal modules: break-even & startup costs, DCF valuation
- status: TODO
- depends: E02
- skills: xlsx
- do: add-on sheets any template can include based on `goal`: startup cost table
  + funding sources + months-to-break-even; DCF (FCF from the model, WACC input,
  terminal growth vs exit multiple, NPV, sensitivity table WACC × g).
  "Investor-ready pitch model" = full tier + Summary sheet with KPI table.
- done when: modules render in every template, recalc clean, challenger covers them.

### E08 — Brief builder (Claude API)
- status: TODO
- depends: E02
- skills: product-self-knowledge, engineering:system-design, engineering:testing-strategy
- do: `engine/brief_builder.py`: wizard answers (+ optional free text + key numbers)
  → Brief via Anthropic API with a strict JSON schema (tool use / structured output),
  per-industry/stage default library from templates, server-side validation,
  2 retries, cost+latency logging. Check the current model id and SDK usage with
  product-self-knowledge — do not guess. Tests use recorded fixtures; no network.
  Sample-data path ("prefill") works with no LLM call at all.
- done when: 20 fixture cases produce valid briefs; invalid LLM output is caught.

### E09 — Orders, jobs and the delivery pipeline
- status: TODO
- depends: E02, E08
- skills: engineering:system-design, engineering:architecture, engineering:testing-strategy
- do: models (Order, Job, Artifact), Alembic, state machine
  `draft → awaiting_payment → paid → building → checking → ready | failed`,
  worker loop (brief → generate → recalc → challenger → store → notify),
  idempotency, retries with backoff, failed jobs alert the admin and never reach
  the customer, storage adapter (local + S3-compatible), signed expiring links.
- done when: an end-to-end test drives a fake paid order to `ready` with a
  downloadable, checked file, and a broken template ends in `failed`.

### E10 — Wizard + checkout UI
- status: TODO
- depends: E09
- skills: frontend-design
- do: server-rendered multi-step wizard reproducing the competitor's flow as
  documented in docs/research/draftplan.md (type → goal → stage → horizon &
  granularity → **key numbers step with sensible defaults** → plan → email),
  live order summary, sample-data toggle. Use design tokens from
  `design/tokens.dc.html`. Accessible (labels, keyboard), works at 360 px.
- done when: Playwright test completes the wizard and creates an order in
  `awaiting_payment` (Chromium is preinstalled; see environment notes).

### E11 — Payments
- status: TODO
- depends: E10
- skills: engineering:system-design, engineering:code-review
- do: payment adapter interface; Stripe Checkout implementation (test mode),
  webhook with signature verification, `paid` transition, refunds from admin,
  prices from config. Keep a second adapter stub (Lemon Squeezy / Paddle) until
  Henry decides (HUMAN_TODO D2). Fake adapter for tests.
- done when: tests cover success, cancel, duplicate webhook, bad signature.

### E12 — Email delivery
- status: TODO
- depends: E09
- skills: engineering:testing-strategy
- do: email adapter (console + Resend/Postmark), templates from `content/email/`
  (fallback plain copy if M07 not done): order received, model ready (signed link,
  7-day expiry, re-send), build failed (apology + refund note), refund issued.
- done when: tests render every template and send through the console adapter.

### E13 — Landing page and static pages
- status: TODO
- depends: E01
- skills: frontend-design, small-business:seo-ai-visibility
- do: build the landing exactly per `docs/SPEC_LANDING.md` (export it first — see
  CLAUDE.md) and `design/landing.dc.html`, served by the app; copy from
  `content/landing.md` if M03 is DONE, else from the design file. Privacy /
  Terms / Refund pages render `content/legal/*.md` when present. SEO tech
  (meta, OG, JSON-LD, sitemap, robots). Interactive Excel mockup.
- done when: Lighthouse mobile ≥ 95 on all four categories (run headless
  Chromium), axe 0 critical, no horizontal scroll at 360 px.

### E14 — Admin panel
- status: TODO
- depends: E09, E11
- skills: frontend-design, engineering:code-review
- do: password-protected admin (env var credentials, rate-limited login):
  orders list & filters, order detail with brief JSON and check report, re-run
  build, download, refund, re-send email, simple revenue/orders counters.
- done when: tests for auth and every action.

### E15 — Ops: logging, health, backups, deploy docs
- status: TODO
- depends: E09
- skills: engineering:deploy-checklist, engineering:documentation
- do: structured logs, `/healthz`, error alert email to admin, DB backup script,
  rate limiting on public endpoints, security headers, `docs/DEPLOY.md` for a
  single Docker host (Railway / Render / Fly.io / VPS — options, not a choice).
- done when: `docker compose up` runs app+worker+postgres locally and the E2E test
  passes against it.

### E16 — Seo pages engine and sample files on the site
- status: TODO
- depends: E13, E03
- skills: frontend-design, small-business:seo-ai-visibility
- do: render `content/seo/*.md` into industry pages with a shared layout,
  internal links, a CTA and a downloadable sample generated by the engine
  (no third-party files). Add to sitemap.
- done when: every page in content/seo builds and passes the SEO tests.

### E17 — Hardening: end-to-end, security, performance
- status: TODO
- depends: E10, E11, E12, E14, E15
- skills: engineering:code-review, engineering:testing-strategy, engineering:tech-debt
- do: full E2E (landing → wizard → Stripe test → worker → email → download) in CI,
  security review of auth/webhooks/uploads/links, dependency audit, load test of
  50 concurrent builds on one worker. Fix what is found.
- done when: report in `docs/reviews/` with no open high-severity items.

### E18 — Release candidate v0.1.0
- status: TODO
- depends: E17, E03, E04, E05, E06, E07
- skills: engineering:deploy-checklist, engineering:documentation
- do: run the deploy checklist, tag `v0.1.0`, write the go-live runbook for Henry
  (env vars, DNS, webhooks, first-order test). Deployment itself is Henry's.
- done when: tag pushed, runbook merged, HUMAN_TODO lists the exact go-live steps.

---

## Track M — Marketing & content (weekdays)

### M01 — Competitor & market map
- status: DONE (2026-10-16, PR #2)
- depends: —
- skills: deep-research, marketing:competitive-brief (opt)
- do: AI model builders, template marketplaces, planning SaaS, freelancers. Note
  that Henry's own FinModelsLab sells templates — flag overlap / cannibalisation
  risk explicitly. Prices, delivery, formats, proof, gaps. Sources linked.
- done when: `docs/marketing/competitors.md` with a comparison table + 5 gaps we can own.

### M02 — ICP, positioning, brand name options
- status: TODO
- depends: M01
- skills: deep-research, marketing:brand-review (opt)
- do: 2–3 ICPs, positioning statement, message house, 8 name candidates with
  rationale (flag obvious trademark collisions found by web search; domain
  availability must be checked by Henry). Price recommendation with reasoning.
- done when: `docs/marketing/positioning.md`; HUMAN_TODO gets "pick name + price".

### M03 — Final landing copy (EN)
- status: TODO
- depends: M02
- skills: small-business:seo-ai-visibility, marketing:content-creation (opt)
- do: `content/landing.md`, one heading per landing section in the design, same
  structure and lengths; meta title/description; 6 FAQ; no invented claims;
  prices and name as placeholders until Henry decides.
- done when: file merged; E13 can consume it.

### M04 — SEO keyword plan
- status: TODO
- depends: M01
- skills: small-business:seo-ai-visibility, marketing:seo-audit (opt)
- do: use the Ahrefs connector if available (keywords-explorer tools), else web
  research: clusters like "<industry> financial model", "<industry> business plan
  excel", "startup financial model template"; volume, difficulty, intent;
  pick 15 target pages mapped to our templates.
- done when: `docs/marketing/seo-plan.md` with the 15 pages and target keywords.

### M05 — SEO pages, batch 1 (5 pages)
- status: TODO
- depends: M04
- skills: small-business:seo-ai-visibility, marketing:content-creation (opt)
- do: 5 pages in `content/seo/` (front matter: slug, title, description, keyword,
  template). Practical, numbers-based, written as an experienced CFO; no
  FinModelsLab branding or text; no fabricated statistics — cite or omit.
- done when: 5 files merged, each 900–1400 words.

### M06 — SEO pages, batch 2 (5 pages)
- status: TODO
- depends: M05
- skills: same as M05
- done when: 5 more files merged.

### M07 — Email copy
- status: TODO
- depends: M02
- skills: marketing:email-sequence (opt)
- do: `content/email/`: order received, model ready, build failed, refund issued,
  "how to use your model" (day 1), feedback request (day 7), abandoned checkout
  (1 reminder only). Plain, short, no dark patterns.
- done when: files merged with subject + preheader + body each.

### M08 — Legal drafts (for lawyer review)
- status: TODO
- depends: M02
- skills: docs (opt, for a review copy)
- do: privacy policy (GDPR — Henry is based in Spain, EU customers likely),
  terms of service, refund policy, cookie notice, in `content/legal/`. Clearly
  marked DRAFT. Add "lawyer review" to HUMAN_TODO.
- done when: drafts merged; HUMAN_TODO updated.

### M09 — Launch plan (first 30 days)
- status: TODO
- depends: M02, M03
- skills: small-business:social-content-engine, marketing:campaign-plan (opt)
- do: channels (Reddit/IndieHackers/Product Hunt, LinkedIn from Henry's personal
  profile, accountants & incubators outreach), 30-day calendar, 10 ready LinkedIn
  post drafts in Henry's voice (do NOT use the FinModelsLab branded skill unless
  Henry says so), success metrics. Nothing is posted or sent.
- done when: `docs/marketing/launch-plan.md` + `content/social/`.

### M10 — Analytics & funnel spec
- status: TODO
- depends: M03
- skills: dataviz
- do: event list (landing view → wizard steps → checkout → paid → downloaded),
  privacy-friendly tool options (Plausible vs GA4 with consent), KPI definitions,
  weekly funnel report spec. Hand the event list to E-track via HUMAN_TODO note.
- done when: `docs/marketing/analytics.md`.

---

## Track P — Project management (weekly, Monday)

P runs every Monday and never "completes": it reviews, it does not build.
- skills: engineering:standup, docs
- do: read RUNLOG, BACKLOG, open PRs, CI status, HUMAN_TODO. Write
  `docs/STATUS.md` (done last week, in progress, blocked, next week, risks,
  Henry's queue ordered by urgency). Detect stuck tasks (IN_PROGRESS > 3 days,
  same task failing twice) and either split them in BACKLOG with a note or mark
  BLOCKED with the reason. May reorder TODO tasks inside a track; may add tasks
  (prefix the id with the track, next free number). Report to Henry in Russian.
