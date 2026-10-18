# Run log

Newest first. One entry per scheduled run: date · track · task · result · PR · notes for Henry.

- 2026-10-18 · E · E18 release candidate v0.1.0 · NEEDS_HENRY (tag only) · https://github.com/henrysheykin/finmodel-app/pull/34
  Version 0.1.0 (/healthz, deploy log). Go-live preflight `app/golive.py`: domain, Stripe live, webhook, sender domain, support,
  admin, client IP, legal texts, email copy. It runs in every deploy log and shows as a box on /admin. docs/RUNBOOK_GO_LIVE.md
  (variables, steps 0–9, rollback), CHANGELOG.md, docs/reviews/E18-release-checklist.md, HUMAN_TODO G1.1–G1.9. 800 tests local, CI green.
  Tag v0.1.0 NOT pushed: the sandbox git proxy refuses tag pushes → HUMAN_TODO G0. Observed: startup-model.com already serves the
  app, but PUBLIC_BASE_URL is still the Railway URL (sitemap). Next E by priority: E08 (brief builder; needs A1 key only for live use).
- 2026-10-18 · E · E05 real estate template · DONE · https://github.com/henrysheykin/finmodel-app/pull/33
  Took over the stale E05 claim (no branch/PR since 2026-10-17 13:33; it blocked E18). Framework (ADR-011): annuity mortgage
  (PMT), land excluded from depreciation, Returns sheet in both tiers — purchase at year 0, NOI − reserves, sale at next-year
  NOI ÷ exit cap, unlevered/levered IRR, NPV, multiple, DSCR, cash-on-cash; challenger recomputes every cell (IRR ±0.01 pp).
  Template: rent roll, vacancy, property costs, 4 stage defaults, sample + memo. 787 tests local; 200-case random LO sweep clean.
  For Henry: R1 CFO review of real estate (6 questions in the memo). Next E: E18 release candidate (all depends DONE).
- 2026-10-18 · E · E17 hardening · DONE · https://github.com/henrysheykin/finmodel-app/pull/32
  Fixed: a webhook delivered twice at the same moment could build/receipt twice (conditional UPDATE claim); blocking Stripe/email/DB
  work ran on the event loop (one slow email froze the site); admin login global cap; one client-address rule for all limits;
  cross-site POSTs refused; CSP; tokens redacted from access logs; 1 MB body cap; pinned deps + pip-audit job (clean).
  New: browser journey E2E with the real engine and real email copy; load test 50 orders / one worker = 50 ready, 7.8 s per model.
  Report docs/reviews/E17-hardening.md. 714 tests local. For Henry: A6 still open. E05 skipped again (stale claim, no continue:).
- 2026-10-17 · E · E15 ops (rest) · DONE · https://github.com/henrysheykin/finmodel-app/pull/31
  Per-IP rate limits: wizard + /api/orders share 30/10 min, checkout sessions 30/10 min (RATE_LIMIT_PER_10MIN), 429 + Retry-After,
  answers kept. docker-compose.yml (production image + Postgres 16); compose E2E (wizard → test payment → build → Checks PASS) in CI.
  668 tests (666 local + 2 compose). For Henry: set CLIENT_IP_HEADER=X-Real-IP in Railway (HUMAN_TODO A6). E05 skipped again (stale claim, no continue:),
  please reset to TODO; E17 is now unblocked.
- 2026-10-17 · E · E16 SEO pages engine · DONE · https://github.com/henrysheykin/finmodel-app/pull/29
  All 15 content/seo pages live at /models/… and /guides/… (shared layout, breadcrumbs, CTA to the wizard on the page's template,
  sample download, related links, canonical/OG, JSON-LD); /models and /guides indexes; sitemap + llms.txt list them. Sample names
  `<key>-<tier>[-Ny]` served at /samples/; built missing cafe-light and cafe-full-5y (pages linked to 404s). 76 new tests; 648 local green.
  For M: 9 titles exceed ~70 chars (Google truncates), tests allow ≤ 90. For Henry/P: E05 claimed 13:33 with no branch/PR/continue: —
  skipped a 2nd time per protocol; please reset to TODO. E17 waits on E15 (IN_PROGRESS). frontend-design skill not installed.
- 2026-10-17 · E · interactive with Henry: production check on Railway (test mode) — healthz, landing, wizard, Stripe test payment,
  webhook, build, Resend email, download, Checks PASS all OK. Left: custom domain + Resend domain (A5), Stripe account name "FRANCHISE"
  → StartupModel before go-live. Copy issues for M/E: model-ready email promises a "tomorrow" note that is not sent yet, and says the
  scenario switch is on Inputs (Full tier has it on Dashboard).
- 2026-10-17 · E · E07 goal modules · DONE · https://github.com/henrysheykin/finmodel-app/pull/26
  The wizard goal now adds sheets (every template, both tiers): Break-even (funding need to the lowest cash point + cash buffer,
  EBITDA/NI-positive period, payback, annual break-even revenue), Valuation (unlevered FCF, NPV-tied discounting, perpetual-growth and
  exit-multiple EV, WACC × g sensitivity), investor Summary. Challenger recomputes every module cell; ADR-010; 561 tests.
  For Henry: R1 CFO review of goal modules (samples/cafe-investor_pitch.xlsx, 6 questions in docs/templates/goal-modules.md); D12.
  Note: E05 claimed 2026-10-17 13:33 by a scheduled run with no branch/PR/continue: note — skipped per protocol; needs reset to TODO.
- 2026-10-17 · E · interactive session with Henry (go-live request) · PR https://github.com/henrysheykin/finmodel-app/pull/25
  E15 slice: Railway deploy — one container (migrations + worker + web), Postgres URL, logging, security headers, docs/DEPLOY.md, ADR-008;
  verified on Postgres 16 with a volume (full customer path). E13: landing from design v2 with a live preview of real engine output,
  legal pages from content/legal, samples, robots/sitemap/llms.txt, self-hosted fonts; Lighthouse mobile 98/100/100/100, axe 0.
  E20: template catalog (ADR-009) — a new industry is one file. E21 home services and E22 fitness templates (samples, memos).
  E05 real estate left for the E track with the framework extensions it needs (note in BACKLOG). Priority: E05 → E07 → E17 → E18.
  For Henry: merge #25; Railway/Stripe/Resend per docs/DEPLOY.md; L1 legal texts; R1 CFO reviews (now 5 templates); D9, D11.
- 2026-10-17 · E · E14 admin panel · DONE · https://github.com/henrysheykin/finmodel-app/pull/23
  /admin: env credentials (off when unset, 12+ chars), per-IP login limit, signed 12 h cookie (Strict, /admin), CSRF on every action;
  orders list/filters/counters, detail (timeline, jobs, answers, brief, check report), download, re-send, re-build, refund with confirmation.
  Fixed: re-build could mark an unpaid order paid. App-first priority list (ADR-006) is now complete: wizard, payments, accounts, downloads, email, admin.
  For Henry: A2 (Stripe test keys), A3 (email provider), A4 (Railway), D9 + SUPPORT_EMAIL, ADMIN_USER/ADMIN_PASSWORD in env. Next E: E05, E07, E08, E13, E15.
- 2026-10-17 · E · E12 email delivery · DONE · https://github.com/henrysheykin/finmodel-app/pull/22
  Console/Resend/Postmark senders; content/email rendered to text + escaped HTML; receipt (once), model ready, refund, sign-in, admin alerts.
  Build-failed email is held while its copy has the [FAILED_BUILD_POLICY] placeholder (D9) — admin gets an alert instead. New content/email/sign-in.md (M may polish).
  Scheduled day-1/day-7/abandoned emails not triggered yet (need consent/unsubscribe, M08). For Henry: D9, A3, SUPPORT_EMAIL.
- 2026-10-17 · E · E19 customer accounts · DONE · https://github.com/henrysheykin/finmodel-app/pull/21
  Magic-link sign-in (single-use, hashed, 15 min, confirm button against mail scanners), hashed server sessions (30 days, HttpOnly/Lax/Secure),
  rate limits per email/IP with identical responses, My models + 10-minute download links, owner-only 404s, sign out / everywhere. Playwright download test.
- 2026-10-17 · E · E11 payments · DONE · https://github.com/henrysheykin/finmodel-app/pull/20
  Stripe Checkout over httpx (test mode; live keys refused without ALLOW_LIVE_PAYMENTS=1), signed webhooks with replay window,
  amount/currency checks, idempotent paid, automatic refund of a duplicate payment, refunds service, success/cancel pages, dev test-payment page.
  For Henry: HUMAN_TODO A2 — test keys + webhook endpoint, steps in docs/PAYMENTS.md. No second provider stub (D2 = Stripe).
- 2026-10-17 · E · E10 wizard + checkout · DONE · https://github.com/henrysheykin/finmodel-app/pull/19
  /start: 7 steps (type, goal, stage, period, key numbers with stage defaults, plan, email), live summary, progressive enhancement,
  /checkout/{id} summary with masked email. Playwright at 360 px. CI installs Chromium. frontend-design skill not installed; design v2 tokens used.
- 2026-10-17 · E · E09 orders, jobs, delivery pipeline · DONE · https://github.com/henrysheykin/finmodel-app/pull/18
  Order state machine + audit, idempotent mark_paid, DB-polled worker (atomic claim, stale reclaim, 30/60 s backoff, fail on 3rd),
  generate → recalc → challenger → store → notify; rejected models fail + admin alert, never delivered. Local/S3 storage, HMAC links (7 days),
  order API, Alembic, prefill briefs (no LLM). ADR-007. 278 tests incl. LibreOffice end-to-end. Nothing new for Henry.
- 2026-10-17 · E · re-plan (Henry): app first — order E09 → E10 → E11 → E19 (new: magic-link accounts, My models, downloads) → E12 → E14, then templates. E09 no longer waits for E08. ADR-006. E05 back to TODO.
- 2026-10-17 · M · M11 SEO pages batch 3 · DONE · PR https://github.com/henrysheykin/finmodel-app/pull/17
  Henry cancelled M08 (legal), M09 (launch plan), M10 (analytics); added M11. 5 pages: SaaS with scenarios, professional services, investors, e-commerce for investors, retail store for a bank loan.
  Publish only with CFO-signed templates (R1). Left for later: rental pro forma (after E05), DCF for owners (after E07).
- 2026-10-17 · E · E05 reset to TODO (Henry's request): abandoned claim from 2026-10-16, no branch/PR. Next E run picks it up.
- 2026-10-17 · E · E06 Professional services template · DONE · https://github.com/henrysheykin/finmodel-app/pull/16
  Billable FTE × available hours × utilisation (senior / consultant roles) + contractor hours; rate card with yearly increase;
  retainer (discount) vs project (realisation) mix; billable payroll + contractors in cost of delivery; 45 receivable days default;
  KPI table incl. employee vs contractor cost per hour; stage defaults ×4; monthly = annual exactly. 229 tests. Sample samples/services-full.xlsx.
  For Henry: HUMAN_TODO R1 — CFO review of services (memo docs/templates/services.md). Note for P: E05 (real estate) claimed 2026-10-16 20:15 UTC
  with no branch, PR or continue: note — looks abandoned; skipped per protocol, needs reset to TODO or a continue: note.
- 2026-10-16 · M · M07 email copy · DONE · PR https://github.com/henrysheykin/finmodel-app/pull/15
  `content/email/`: 7 emails (order received, model ready, build failed, refund issued, day-1 how-to, day-7 feedback, one abandoned-checkout reminder) + README with variables/triggers for E12.
  For Henry: HUMAN_TODO D9 (failed-build policy; support email address). marketing:email-sequence not installed.
  Note for M track: E03 (SaaS) and E04 (retail) templates now exist — deferred SEO pages #4, #12, #13 can be written in a later batch.
- 2026-10-16 · E · E04 Retail / e-commerce template · DONE · https://github.com/henrysheykin/finmodel-app/pull/14
  Online (visits × conversion + paid orders via CAC, repeat multiplier, AOV) and stores (stores × sq ft × sales/sq ft,
  yearly openings + fit-out capex); Nov–Dec seasonality keeping the year; returns, product cost, fulfilment, payment fees,
  inventory days in WC; retail metrics; stage defaults ×4. Monthly = annual exactly. 177 tests. Sample samples/retail-full.xlsx.
  For Henry: HUMAN_TODO R1 — CFO review of retail (memo docs/templates/retail.md); not blocking. Note: full suite now ~3 min in CI.
- 2026-10-16 · M · decision D8 recorded · PR https://github.com/henrysheykin/finmodel-app/pull/13
  No StartupModel branding in delivered workbooks (all customers); 5-model pack valid 12 months. ADR-002 addendum 3; accountants/E-2 pages updated.
- 2026-10-16 · E · E03 SaaS template · DONE · https://github.com/henrysheykin/finmodel-app/pull/12
  Customers by channel (organic + paid/CAC), churn, ARPA, expansion, MRR waterfall, hosting/support COGS, role payroll,
  simplified deferred revenue, SaaS metrics (ARR, CAC, LTV/CAC, payback, runway); stage defaults ×4. Framework: liability
  and KPI hooks, per-role headcount growth. 131 tests (SaaS 12-combo + 4-stage LibreOffice matrix). Sample samples/saas-full.xlsx.
  For Henry: HUMAN_TODO R1 — CFO review of SaaS (memo docs/templates/saas.md, questions at the end); not blocking.
- 2026-10-16 · M · M06 SEO pages batch 2 · DONE · PR https://github.com/henrysheykin/finmodel-app/pull/11
  5 pages: restaurant break-even guide, E-2 visa projections (B2B), AI generators vs verified model, projections for accountants (B2B), 20-point model review checklist.
  All cafe-backed; pages needing SaaS/services/rental/retail/DCF templates wait for E03–E07. Sources: 9 FAM 402.9-6(E), Ankura (Apr 2026), quoted verbatim.
  For Henry: HUMAN_TODO D8 (pack validity, branding/white-label in delivered files).
- 2026-10-16 · M · M05 SEO pages batch 1 · DONE · PR https://github.com/henrysheykin/finmodel-app/pull/10
  5 pages in `content/seo/` (hub, SBA loan, restaurant/coffee shop, bank-loan guide, restaurant pro forma), 1,060–1,220 words each; index + E16 notes in `docs/marketing/seo-pages.md`.
  SaaS/services pages deferred (templates not built), break-even page deferred (E07). Henry closed D6 (no volumes) and D7 (no brand risk).
  marketing:content-creation not installed; seo-ai-visibility used.
- 2026-10-16 · M · M04 SEO keyword plan · DONE · PR https://github.com/henrysheykin/finmodel-app/pull/9
  `docs/marketing/seo-plan.md`: 15 pages in 3 waves; wave 1 = custom-model hub, SBA loan projections, restaurant/coffee shop for bank loan, SaaS with scenarios, professional services.
  Ahrefs returned "Insufficient plan" → no volumes measured; difficulty is qualitative from ranking domains. HUMAN_TODO D6 (volumes), D7 (startupmodels.io brand risk).
  marketing:seo-audit not installed; seo-ai-visibility + deep-research used.
- 2026-10-16 · setup · design v2 (ADR-005): own visual identity replacing the v1 look that was too close to the competitor; StartupModel brand, prices $149/$349, 7-day refund and M02 ICPs applied in `design/`. E13 builds from design v2; content/landing.md keeps meta/SEO notes.
- 2026-10-16 · M · decisions D2/D4 recorded · PR https://github.com/henrysheykin/finmodel-app/pull/8
  ADR-004: Stripe Checkout; Railway (web + worker + Postgres). Vercel not used (no persistent worker / LibreOffice container). VAT handling flagged for Henry.
- 2026-10-16 · E · E02 engine framework · DONE · https://github.com/henrysheykin/finmodel-app/pull/6
  Strict Brief schema (values only), Template base + formula line language, shared core (headcount, P&L tail, fixed assets,
  working capital, loan, cash flow, balance sheet) with a Python twin; Light/Full × monthly/annual × 1/3/5 all build, 0 errors,
  BS balances, challenger PASS (12-combo matrix in CI, 83 tests). Cafe migrated: revenue/EBITDA equal the prototype. ADR-003.
  For Henry: HUMAN_TODO R0 (non-blocking) — glance at shared economics defaults (tax loss carry-forward, loan timing, WC days).
- 2026-10-16 · M · prices final (Henry) · PR https://github.com/henrysheykin/finmodel-app/pull/7
  Light $149, Full $349, pack 5 × Full $1,250, refund 7 days: recorded in landing copy, HUMAN_TODO D3, ADR-002 addendum 2.
- 2026-10-16 · M · M03 landing copy (EN) · DONE · PR https://github.com/henrysheykin/finmodel-app/pull/5
  `content/landing.md`: all design sections, meta/OG, 6 FAQ, notes for E13 (placeholders, corrected claims, JSON-LD).
  Removed the design's "three AI agents build it" claim (contradicts the core idea); Sheets/Numbers compatibility marked [VERIFY].
  Henry cleared startupmodels.co (inactive). Open for Henry: [PRICE_FULL], [PACK_PRICE], [REFUND_WINDOW]. marketing:content-creation not installed.
- 2026-10-16 · M · decisions from Henry recorded · PR https://github.com/henrysheykin/finmodel-app/pull/4
  ADR-002: domain startup-model.com, brand StartupModel (picked from Henry's 6 domains); Light $149 + bundles; separate from FinModelsLab.
  Open for Henry: Full price, pack price; check "Startup Models" (startupmodels.co) collision + TMview/USPTO. E13 must replace Ledgerline in app/ and landing.
- 2026-10-16 · M · M02 ICP, positioning, names, price · DONE · PR https://github.com/henrysheykin/finmodel-app/pull/3
  `docs/marketing/positioning.md`: 3 ICPs (SBA/bank loan applicants, pre-seed SaaS founders, small advisory firms + E-2 plan writers), positioning, message house, 8 screened names, price recommendation.
  Ledgerline = CAUTION (Framer "Ledgerline CPA" template, crowded "ledger" root); Tickmark, Provable rejected. Recommended Light $149 / Full $349 / accountant pack 5 for $1,250.
  For Henry: HUMAN_TODO D1 (pick name, legal + domain check) and D3 (pick price). marketing:brand-review not installed; deep-research used.
- 2026-10-16 · M · M01 competitor & market map · DONE · PR https://github.com/henrysheykin/finmodel-app/pull/2
  `docs/marketing/competitors.md`: table of AI builders, templates, planning SaaS, freelancers; FinModelsLab overlap; 5 gaps; price bands.
  Main finding: nobody combines the buyer's own numbers, a live-formula .xlsx, a one-cell scenario switch, a Checks sheet and an independent recompute at a one-off price.
  FinModelsLab ($99 x 2,000 templates) overlaps on headline features: price Ledgerline clearly above $99. New HUMAN_TODO D5.
  Skill marketing:competitive-brief not installed; deep-research used. Reddit/G2 review text could not be fetched (blocked).
- 2026-10-16 · E · E01 · DONE · https://github.com/henrysheykin/finmodel-app/pull/1
  Scaffold (pyproject 3.12, ruff, pytest, app/worker skeletons, .env.example), own headless LibreOffice
  recalc `engine/recalc.py`, cafe template + challenger ported to `engine/` (output identical to poc, challenger
  stricter on non-numeric/missing results), Dockerfile + CI (pytest with LibreOffice required, in-image smoke test), ADR-001.
  Skills loaded: xlsx, engineering:architecture, engineering:testing-strategy. Nothing new for Henry.
- 2026-10-16 · setup · repo created; prototype, design, research, backlog and agent rules added. Scheduled tasks: E daily 07:50, M weekdays 10:50, P Mondays 17:51 (Europe/Madrid); first E and M runs fired manually right after setup.

## 2026-10-17 — interactive session (Henry) — landing hero v3
- Hero is now a clickable spreadsheet of the real cafe workbook: Dashboard / Inputs / P&L / Checks tabs, formula bar, B4 Low/Base/High switch, keyboard navigation; numbers tested against the independent Python model.
- How it works: interactive 3-question demo brief that opens a prefilled /start; pipeline and sample file card.
- PR https://github.com/henrysheykin/finmodel-app/pull/27 (571 tests green).
- For Henry: "how-to" guide pages are E16 (SEO pages engine), still TODO.

## 2026-10-17 — interactive session (Henry) — stale CSS after deploy
- Returning visitors saw hero v3 unstyled: Cloudflare cached /static/site.css for 4 h under a fixed URL.
- Fix: asset() adds a content hash (?v=…) to CSS/JS links; versioned static files are immutable, plain ones revalidate.
- PR https://github.com/henrysheykin/finmodel-app/pull/28 (575 tests green), verified live.

## 2026-10-18 — interactive session (Henry) — hero looks like real Excel
- Henry: the hero preview "isn't Excel, it's a parody". Now the whole sample workbook (8 sheets) in a spreadsheet window:
  ribbon following the selection, name box, formula bar, gridlines, frozen panes, B4 list + input message, F2 precedents, range sums.
- app/xlview.py + landing.js render the same cells (browser test compares); data /preview/workbook.json?v=<hash>.
- Engine: scenario-cell validation now has an input message. PR https://github.com/henrysheykin/finmodel-app/pull/30 (669 tests).
- For Henry: workbook title/section bands are still navy (#1F3864 / #2F5597); the site shows them in ink/pine (ADR-005). Switch the files too?
