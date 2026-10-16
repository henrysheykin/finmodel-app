# Run log

Newest first. One entry per scheduled run: date · track · task · result · PR · notes for Henry.

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
