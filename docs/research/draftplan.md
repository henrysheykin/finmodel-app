# DraftPlan — product research (15.10.2026)

## What the product actually is
- Landing + checkout wizard at getdraftplan.com/checkout.html.
- Wizard asks only categorical questions: business type (SaaS / Software, Restaurant / Cafe,
  Retail / E-commerce, Real Estate, Professional Services, Other), goal (Revenue & profit
  projections, Startup costs & break-even, Business valuation (DCF), Investor-ready pitch
  model, Other), stage (Planning, Early — first year, Growing — 1-3 years, Established — 3+
  years), horizon (1/3/5 y), granularity (monthly/annual), "prefill with sample data" toggle.
  No numeric inputs at all.
- Plans: Light $49 (single-tab P&L, 3 scenarios, validation report), Full $59 (multi-tab:
  P&L, cash flow, balance sheet, headcount, executive dashboard).
- Step 3: email + optional first name, button "Get My Model — $59". Live order summary on
  the right ("Delivered within 60 minutes as a formatted .xlsx file", "Revision if output
  doesn't match brief").
- No payment provider is loaded. The pay button shows "Payment processor temporarily
  unavailable", saves the lead to /api/leads and promises a payment link by email
  => fake-door demand test.
- Delivery promise inconsistent: landing "under 5 minutes", checkout "within 60 minutes",
  success state "checkout link within 2 hours".
- Analytics: Google tag + own /stats/script.js. SEO pages: coffee-shop-financial-model.html
  (~1,100 words guide + sample download + CTA), how-to-build-a-financial-model.html.
- No public footprint found (Product Hunt, Reddit search: nothing).

## Their sample files (inspected in-browser)
- Both made with openpyxl 3.1.5 on 2026-03-11, recalculated, number formats
  `$#,##0;($#,##0);-`, `0.0%;(0.0%);-`, `0.0x`.
- Coffee shop: 1 sheet, 101 cells, 42 formulas, no scenario switch, no validation tab.
- Real estate: 4 sheets (Dashboard, Assumptions, Properties, Portfolio), 625 formulas,
  CHOOSE scenario selector with data validation, no validation tab.

## Implication for us
- Their samples are weaker than their claims; a verifiable Checks sheet and an independent
  challenger are a real differentiator.
- A key-numbers step in the wizard (with defaults) makes the model actually "custom".

## Our prototype (poc/)
- brief JSON -> deterministic openpyxl generator -> LibreOffice recalc -> independent Python
  reviewer across 3 scenarios. Cafe model: 5 sheets, 894 formulas, 0 errors, workbook
  matches the Python recomputation to $1 in all 9 scenario-years.
