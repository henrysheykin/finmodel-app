# Backlog

Status values: `TODO` · `IN_PROGRESS (date)` · `DONE (date, PR)` ·
`BLOCKED: reason` · `NEEDS_HENRY: what`. Protocol: see `CLAUDE.md`.
Each track edits only its own section. Pick the first ready task in your track.

Skill names are as shown in the session's skill list (prefixes may differ:
`xlsx` may appear as `anthropic-skills:xlsx`). "(opt)" = use if installed.

---

## Track E — Engineering (daily)

> **Priority (Henry, 2026-10-17, go-live within days):** E-track runs pick tasks in THIS order
> (overrides file order): **E05 → E21 → E22 → E07 → E17 → E18**, then E16, E15 (rest), E08.
> Done in the interactive session on 2026-10-17: E13 landing, E15 deploy slice, E20 template catalog.
> New industries are one file each (ADR-009, `docs/templates/ADDING_A_TEMPLATE.md`).
> Customer login = passwordless magic link by email (ADR-006).

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
- status: DONE (2026-10-16, https://github.com/henrysheykin/finmodel-app/pull/6)
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
- status: DONE (2026-10-16, https://github.com/henrysheykin/finmodel-app/pull/12)
- depends: E02
- skills: xlsx, engineering:testing-strategy
- do: subscription build (new customers by channel, CAC, churn, ARPA, expansion,
  MRR/ARR waterfall), COGS/hosting, headcount-driven opex, deferred revenue
  simplified, runway. Defaults for planning/early/growing/established stages.
  Produce `samples/saas-full.xlsx` + `docs/templates/saas.md` (assumption memo).
- done when: generator+challenger tests pass for all tier/horizon combos; then
  add "CFO review: SaaS template" to HUMAN_TODO (does not block next tasks).

### E04 — Template: Retail / E-commerce
- status: DONE (2026-10-16, https://github.com/henrysheykin/finmodel-app/pull/14)
- depends: E02
- skills: xlsx
- do: traffic × conversion × AOV (e-com) or stores × sales/sqft (retail), returns,
  COGS, inventory days & working capital in cash flow, fulfilment, ad spend/CAC.
  Sample + assumption memo; HUMAN_TODO CFO review.
- done when: as E03.

### E05 — Template: Real estate (rental property investment)
- status: TODO
- note: reset 2026-10-17 by Henry's request — the 2026-10-16 claim left no branch, PR or continue: note.
- note (2026-10-17): follow `docs/templates/ADDING_A_TEMPLATE.md`; `key = "real_estate"`, business type
  `real_estate` (remove it from `PLANNED`); the landing lists the sample automatically.
- depends: E02, E20
- skills: xlsx
- do: purchase price, closing costs, LTV/rate/term loan with amortisation
  schedule, rent roll, vacancy, opex, NOI, cap rate, cash-on-cash, DSCR, exit
  value, levered/unlevered IRR (IRR function), NPV. Sample + memo; HUMAN_TODO.
- done when: as E03; challenger checks IRR within 0.01 pp.

### E06 — Template: Professional services
- status: DONE (2026-10-17, https://github.com/henrysheykin/finmodel-app/pull/16)
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
- status: DONE (2026-10-17, https://github.com/henrysheykin/finmodel-app/pull/18)
- depends: E02
- note (2026-10-17): build briefs from wizard answers via the template stage defaults + key numbers
  ("prefill", no LLM); E08 plugs the LLM brief builder into the same interface later.
- skills: engineering:system-design, engineering:architecture, engineering:testing-strategy
- do: models (Order, Job, Artifact), Alembic, state machine
  `draft → awaiting_payment → paid → building → checking → ready | failed`,
  worker loop (brief → generate → recalc → challenger → store → notify),
  idempotency, retries with backoff, failed jobs alert the admin and never reach
  the customer, storage adapter (local + S3-compatible), signed expiring links.
- done when: an end-to-end test drives a fake paid order to `ready` with a
  downloadable, checked file, and a broken template ends in `failed`.

### E10 — Wizard + checkout UI
- status: DONE (2026-10-17, https://github.com/henrysheykin/finmodel-app/pull/19)
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
- status: DONE (2026-10-17, https://github.com/henrysheykin/finmodel-app/pull/20)
- depends: E10
- skills: engineering:system-design, engineering:code-review
- do: payment adapter interface; Stripe Checkout implementation (test mode),
  webhook with signature verification, `paid` transition, refunds from admin,
  prices from config. Keep a second adapter stub (Lemon Squeezy / Paddle) until
  Henry decides (HUMAN_TODO D2). Fake adapter for tests.
- done when: tests cover success, cancel, duplicate webhook, bad signature.

### E12 — Email delivery
- status: DONE (2026-10-17, https://github.com/henrysheykin/finmodel-app/pull/22)
- depends: E09
- skills: engineering:testing-strategy
- do: email adapter (console + Resend/Postmark), templates from `content/email/`
  (fallback plain copy if M07 not done): order received, model ready (signed link,
  7-day expiry, re-send), build failed (apology + refund note), refund issued.
- done when: tests render every template and send through the console adapter.

### E13 — Landing page and static pages
- status: IN_PROGRESS (2026-10-17, interactive session with Henry; PR #25 open — merge pending Henry)
- depends: E01
- skills: frontend-design, small-business:seo-ai-visibility
- do: build the landing from **design v2**: `design/landing.dc.html` (layout,
  copy, interactive sheet logic) and `design/tokens.dc.html` (exact tokens),
  served by the app. Page copy comes from the design file (v2 already carries
  StartupModel, the approved prices and the M02/M03 messaging); take meta,
  JSON-LD, robots/llms.txt notes and placeholders from `content/landing.md`
  (ADR-005). Use `docs/SPEC_LANDING.md` only for sections 6, 8–11
  (see CLAUDE.md). No scroll-reveal animation. Privacy / Terms / Refund pages
  render `content/legal/*.md` when present. SEO tech (meta, OG, JSON-LD,
  sitemap, robots).
- done when: matches design v2 at 1440 and 360 px; Lighthouse mobile ≥ 95 on
  all four categories (run headless Chromium), axe 0 critical, no horizontal
  scroll at 360 px; `grep -ri "1F3864\|2563EB\|DM Sans"` in web/ is empty.

### E20 — Template catalog: a new industry is one file
- status: IN_PROGRESS (2026-10-17, interactive session with Henry; PR open — merge pending Henry)
- depends: E02
- do: ADR-009 — registry discovers templates; catalog data on the template (order, key numbers, samples);
  `PLANNED` "coming soon" list; wizard / briefing / brief schema / landing derive from it;
  `scripts/build_samples.py`; `tests/test_catalog.py`; `docs/templates/ADDING_A_TEMPLATE.md`.
- done when: adding a template needs no edits outside its own file, tests, sample and memo.

### E21 — Template: Home services / trades
- status: TODO
- depends: E02, E20
- skills: xlsx, engineering:testing-strategy
- do: follow `docs/templates/ADDING_A_TEMPLATE.md`; `key = "home_services"`, business type `home_services`
  (remove it from `PLANNED`). Plumbing, HVAC, electrical, cleaning, landscaping. Revenue: technicians
  (headcount role) × billable jobs per technician per day × working days × average ticket, with monthly
  seasonality (12 factors averaging 1, default flat); leads from a marketing budget ÷ cost per lead ×
  booking rate cap the job count (jobs = min(capacity, booked leads + repeat customers)); service
  agreements (maintenance plan members × monthly fee, monthly churn, new members as % of jobs).
  Costs: materials % of job revenue, technician payroll, vehicle cost per technician per month,
  insurance & licences, dispatcher/office roles, marketing. Capex: van + tools per new technician,
  depreciated. Receivable days small (default 10). KPIs: revenue per technician, jobs per month,
  gross margin per job, plan members and plan MRR, marketing cost per booked job, utilisation.
  Stage defaults ×4. Sample + memo; HUMAN_TODO R1 CFO review.
- done when: as E03.

### E22 — Template: Fitness studio / gym
- status: TODO
- depends: E02, E20
- skills: xlsx, engineering:testing-strategy
- do: follow `docs/templates/ADDING_A_TEMPLATE.md`; `key = "fitness"`, business type `fitness`
  (remove it from `PLANNED`). Members: opening members (presale), new members per month from a marketing
  budget ÷ cost per lead × conversion plus referrals, monthly churn, capacity cap (max members);
  membership fee per month with yearly increase, joining fee, personal training (sessions per month ×
  rate, trainer payout %), class packs / drop-ins, retail & drinks with their own cost %. Costs: rent,
  utilities, instructors per class × classes per week (contractors), front-desk and manager roles,
  software & payment fees % of revenue, marketing, equipment maintenance. Capex: fit-out + equipment,
  replacement after N years. KPIs: members, membership MRR, churn, average revenue per member, LTV,
  break-even members, revenue per square foot (sq ft input). Stage defaults ×4. Sample + memo;
  HUMAN_TODO R1 CFO review.
- done when: as E03.

### E19 — Customer accounts: magic-link login, "My models", downloads
- status: DONE (2026-10-17, https://github.com/henrysheykin/finmodel-app/pull/21)
- depends: E09, E11
- skills: engineering:system-design, engineering:code-review, engineering:testing-strategy
- do: passwordless login (ADR-006): email → single-use, hashed, 15-minute magic-link token sent
  through the email adapter (console in dev/tests) → secure session cookie (HttpOnly, Secure in
  prod, SameSite=Lax, 30-day expiry, server-side revocation). Rate limit per email and per IP;
  same response whether or not the email exists. Orders are linked to the customer by checkout
  email; after payment the customer can sign in and see "My models": order list, status,
  download (fresh short-lived signed link per click), re-build history. Logout, "sign out
  everywhere". No passwords stored anywhere.
- done when: tests cover login flow, expired/reused token, rate limit, another customer's
  order is 404, download works only for the owner and only for `ready` orders; Playwright
  happy path: sign in by link → My models → download the .xlsx.

### E14 — Admin panel
- status: DONE (2026-10-17, https://github.com/henrysheykin/finmodel-app/pull/23)
- depends: E09, E11
- skills: frontend-design, engineering:code-review
- do: password-protected admin (env var credentials, rate-limited login):
  orders list & filters, order detail with brief JSON and check report, re-run
  build, download, refund, re-send email, simple revenue/orders counters.
- done when: tests for auth and every action.

### E15 — Ops: logging, health, backups, deploy docs
- status: IN_PROGRESS (2026-10-17, interactive session with Henry)
- continue: done in PR #24 — one Railway container (deploy/start.sh: migrations + worker + web), Postgres URL,
  logging, security headers/HSTS, docs/DEPLOY.md, verified on Postgres 16 with a volume (ADR-008).
  Left: rate limiting on `/start` POST and `/api/orders`, `docker-compose.yml` (app + postgres) for local runs
  and an E2E test against it, a backup note for Railway Postgres in DEPLOY.md is already there.
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
- status: DONE (2026-10-16, PR #3)
- depends: M01
- skills: deep-research, marketing:brand-review (opt)
- do: 2–3 ICPs, positioning statement, message house, 8 name candidates with
  rationale (flag obvious trademark collisions found by web search; domain
  availability must be checked by Henry). Price recommendation with reasoning.
- done when: `docs/marketing/positioning.md`; HUMAN_TODO gets "pick name + price".

### M03 — Final landing copy (EN)
- status: DONE (2026-10-16, PR #5)
- depends: M02
- skills: small-business:seo-ai-visibility, marketing:content-creation (opt)
- do: `content/landing.md`, one heading per landing section in the design, same
  structure and lengths; meta title/description; 6 FAQ; no invented claims;
  prices and name as placeholders until Henry decides.
- done when: file merged; E13 can consume it.

### M04 — SEO keyword plan
- status: DONE (2026-10-16, PR #9)
- depends: M01
- skills: small-business:seo-ai-visibility, marketing:seo-audit (opt)
- do: use the Ahrefs connector if available (keywords-explorer tools), else web
  research: clusters like "<industry> financial model", "<industry> business plan
  excel", "startup financial model template"; volume, difficulty, intent;
  pick 15 target pages mapped to our templates.
- done when: `docs/marketing/seo-plan.md` with the 15 pages and target keywords.

### M05 — SEO pages, batch 1 (5 pages)
- status: DONE (2026-10-16, PR #10)
- depends: M04
- skills: small-business:seo-ai-visibility, marketing:content-creation (opt)
- do: 5 pages in `content/seo/` (front matter: slug, title, description, keyword,
  template). Practical, numbers-based, written as an experienced CFO; no
  FinModelsLab branding or text; no fabricated statistics — cite or omit.
- done when: 5 files merged, each 900–1400 words.

### M06 — SEO pages, batch 2 (5 pages)
- status: DONE (2026-10-16, PR #11)
- depends: M05
- skills: same as M05
- done when: 5 more files merged.

### M07 — Email copy
- status: DONE (2026-10-16, PR #15)
- depends: M02
- skills: marketing:email-sequence (opt)
- do: `content/email/`: order received, model ready, build failed, refund issued,
  "how to use your model" (day 1), feedback request (day 7), abandoned checkout
  (1 reminder only). Plain, short, no dark patterns.
- done when: files merged with subject + preheader + body each.

### M08 — Legal drafts (for lawyer review)
- status: CANCELLED (Henry, 2026-10-17: not needed)
- depends: M02
- skills: docs (opt, for a review copy)
- do: privacy policy (GDPR — Henry is based in Spain, EU customers likely),
  terms of service, refund policy, cookie notice, in `content/legal/`. Clearly
  marked DRAFT. Add "lawyer review" to HUMAN_TODO.
- done when: drafts merged; HUMAN_TODO updated.

### M09 — Launch plan (first 30 days)
- status: CANCELLED (Henry, 2026-10-17: not needed)
- depends: M02, M03
- skills: small-business:social-content-engine, marketing:campaign-plan (opt)
- do: channels (Reddit/IndieHackers/Product Hunt, LinkedIn from Henry's personal
  profile, accountants & incubators outreach), 30-day calendar, 10 ready LinkedIn
  post drafts in Henry's voice (do NOT use the FinModelsLab branded skill unless
  Henry says so), success metrics. Nothing is posted or sent.
- done when: `docs/marketing/launch-plan.md` + `content/social/`.

### M10 — Analytics & funnel spec
- status: CANCELLED (Henry, 2026-10-17: not needed)
- depends: M03
- skills: dataviz
- do: event list (landing view → wizard steps → checkout → paid → downloaded),
  privacy-friendly tool options (Plausible vs GA4 with consent), KPI definitions,
  weekly funnel report spec. Hand the event list to E-track via HUMAN_TODO note.
- done when: `docs/marketing/analytics.md`.

### M11 — SEO pages, batch 3 (templates now built)
- status: DONE (2026-10-17, PR #17)
- depends: M06
- skills: small-business:seo-ai-visibility
- do: added on Henry's request (2026-10-17). 5 pages in `content/seo/` for templates that now
  exist: SaaS with scenarios (#4), professional services (#5), financial model for investors
  (#11), e-commerce for investors (#12), retail store projections (#13). Facts from
  `engine/templates/*.py` and `docs/templates/*.md`; samples from `samples/`.
- done when: 5 files merged, each 900–1400 words.

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
