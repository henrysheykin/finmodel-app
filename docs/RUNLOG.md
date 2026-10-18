# Run log

Newest first. One entry per scheduled run: date · track · task · result · PR · notes for Henry.

- 2026-10-18 · E · E24 derived goal defaults + fallback usage · DONE · https://github.com/henrysheykin/finmodel-app/pull/42
  `merge` recomputes `cash_buffer` (3 months of costs) after the model's changes unless the model moved it or the customer locked it;
  echoed-unchanged keys don't count; derived value clamped to its range [0, 1e9]. Usage of calls already made is kept on every fallback (`exc.usage`).
  6 new tests; CI green; reviewer PASS (medium clamp + 2 lows fixed before merge). For Henry: nothing new; E23 still waits on A1 (OpenAI key). Next E: none ready besides E23.
- 2026-10-18 · E · E25 brief builder on OpenAI · DONE · https://github.com/henrysheykin/finmodel-app/pull/41
  OpenAI Responses API over httpx (Chat Completions can't do function calls with reasoning on gpt-6; astra can't turn it off):
  strict forced `submit_brief`, reasoning low, store=false, usage uncached/cached/cache-write; no retry on 4xx except 429.
  BRIEF_MODELS gpt-6-luna / gpt-6.1-sol / gpt-6-astra; OPENAI_API_KEY; E23 prices from the OpenAI pricing page (2026-10-18), reference astra;
  fixtures re-recorded, privacy.md names OpenAI. 1017 tests local, CI green, reviewer PASS. For Henry: A1 (key in Railway + cloud env for E23). Next E: E24 (E23 waits on the key).
- 2026-10-18 · E · interactive with Henry: LLM provider → OpenAI (replace Anthropic) · ADR-012
  New E25 (Model: opus) first in track E: OpenAI client, OPENAI_API_KEY, E23 on gpt-6-luna / gpt-6.1-sol / gpt-6-astra, privacy.md. A1 now = OpenAI key.
- 2026-10-18 · E · E23 brief-model eval · harness merged, NEEDS_HENRY (live run) · https://github.com/henrysheykin/finmodel-app/pull/40
  `evals/brief_model_eval.py`: 60 committed cases (6 industries × 10) → prefill → E08 builder → validate → worker build + challenger;
  per model pass share, mean/p95 s, $/order from per-request usage × prices (pricing page 2026-10-18, Haiku >100k surcharge);
  recommendation = cheapest with pass ≥ opus and p95 ≤ 15 s; replay/record modes; 88 tests on fixtures. Memo skeleton, results pending:
  no ANTHROPIC_API_KEY in the sandbox → HUMAN_TODO A1. Skill product-self-knowledge not installed (prices from the docs page). Next E: E24.
- 2026-10-18 · E · E08 brief builder (Claude API) · DONE · https://github.com/henrysheykin/finmodel-app/pull/39
  `engine/brief_builder.py`: prefill brief + customer notes → one forced `submit_brief` tool call that may only change
  driver Low/Base/High (structure, roles, typed key numbers locked); Brief + template validation; errors back as tool_result,
  2 retries, 15 s deadline, no retry on 4xx, then prefill fallback; no call without notes; formula-like text neutralised.
  httpx Messages API client (no SDK dependency). 21 fixture cases → valid briefs, all build + challenger PASS; 4 fallback cases.
  OFF by default: Henry sets ANTHROPIC_API_KEY + BRIEF_MODEL (A1, after E23). Skill product-self-knowledge not installed. Follow-up E24.
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
