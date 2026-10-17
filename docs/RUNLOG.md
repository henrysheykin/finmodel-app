# Run log

Newest first. One entry per scheduled run: date · track · task · result · PR · notes for Henry.

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
