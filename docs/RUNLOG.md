# Run log

Newest first. One entry per scheduled run: date · track · task · result · PR · notes for Henry.

- 2026-10-18 · E · interactive with Henry: token budget + model routing · https://github.com/henrysheykin/finmodel-app/pull/38
  Subagents `.claude/agents/` (scout haiku, implementer sonnet, reviewer opus); CLAUDE.md 115 → 90 lines with Model routing
  and Token budget, background moved to docs/ARCHITECTURE.md; finished tasks → docs/DONE.md, RUNLOG kept at 10 (rest in
  docs/runlog/archive-2026-10.md); `Model:` on every open task; new E23 brief-model eval. BRIEF_MODEL = empty (LLM off):
  no Claude API call exists yet (E08 TODO), so there was no current model to keep; `adapters/llm.py` has caching + token log.
- 2026-10-18 · M · M12 SEO pages batch 4 · DONE · PR https://github.com/henrysheykin/finmodel-app/pull/37
  5 new pages (rental pro forma, DCF, fitness, home services, break-even), 4 older pages refreshed; test_seo 99 passed.
  New templates still await CFO review (R1); no public sample with Valuation/Break-even sheets.
- 2026-10-18 · E · interactive with Henry: L1 legal texts · https://github.com/henrysheykin/finmodel-app/pull/35
  privacy/terms/refunds written from what the app does; seller StartupModels LLC (Wyoming), Wyoming law (Henry gives no address/tax ID).
  Legal pages with unfilled [PLACEHOLDERS] are never published. D9 decided (PR #36): failed build → only Henry gets the alert, no customer email; refunds.md: full refund if a passing model can't be delivered.
  D13 (EU withdrawal checkbox): Henry — ignore. Retention purge (`manage purge`, every start). E18 set DONE (tag optional, G0).
  Henry done today: Resend domain, Stripe name + activation, PUBLIC_BASE_URL, CLIENT_IP_HEADER, EMAIL_FROM. Verified live: /healthz 0.1.0; /privacy, /terms, /refunds published and in the sitemap.
  Left before live money: R1 CFO review, test order on the domain (G1.6), live keys (G1.8), first real order (G1.9).
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
- 2026-10-18 · E · interactive with Henry: hero looks like real Excel
  Henry: the hero preview "isn't Excel, it's a parody". Now the whole sample workbook (8 sheets) in a spreadsheet window:
  ribbon following the selection, name box, formula bar, gridlines, frozen panes, B4 list + input message, F2 precedents, range sums.
  app/xlview.py + landing.js render the same cells (browser test compares); data /preview/workbook.json?v=<hash>.
  Engine: scenario-cell validation now has an input message. PR https://github.com/henrysheykin/finmodel-app/pull/30 (669 tests).
  For Henry: workbook title/section bands are still navy (#1F3864 / #2F5597); the site shows them in ink/pine (ADR-005). Switch the files too?
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
- 2026-10-17 · E · interactive with Henry: stale CSS after deploy
  Returning visitors saw hero v3 unstyled: Cloudflare cached /static/site.css for 4 h under a fixed URL.
  Fix: asset() adds a content hash (?v=…) to CSS/JS links; versioned static files are immutable, plain ones revalidate.
  PR https://github.com/henrysheykin/finmodel-app/pull/28 (575 tests green), verified live.
- 2026-10-17 · E · interactive with Henry: landing hero v3
  Hero is now a clickable spreadsheet of the real cafe workbook: Dashboard / Inputs / P&L / Checks tabs, formula bar, B4 Low/Base/High switch, keyboard navigation; numbers tested against the independent Python model.
  How it works: interactive 3-question demo brief that opens a prefilled /start; pipeline and sample file card.
  PR https://github.com/henrysheykin/finmodel-app/pull/27 (571 tests green).
  For Henry: "how-to" guide pages are E16 (SEO pages engine), still TODO.
