# Run log

Newest first. One entry per scheduled run: date · track · task · result · PR · notes for Henry.

- 2026-10-22 · E · no ready task (E32 PR #51, E38 PR #63, E42 PR #65 active in other sessions; E40, E41 IN_PROGRESS without continue:; E33 waits on E32; E23 NEEDS_HENRY A1) · early exit
- 2026-10-22 · M · M13 Business-model pages, 7 industries · DONE · https://github.com/henrysheykin/finmodel-app/pull/58
  content/business-models/ for cafe, saas, retail, services, home services, fitness, real estate (1,200–1,500 words, figures via
  {{num}}, SBA/IRS links only). Reviewer opus PASS + 13 copy fixes (claims checked against the template drivers).
- 2026-10-22 · M · M15 Calculators batch 1 · DONE · https://github.com/henrysheykin/finmodel-app/pull/62
  23 calculators (cafe 3, SaaS 3, retail 3, services 2, home services 2, fitness 2, real estate 4, cross-industry 4), worked
  examples hand-checked, two cited benchmarks only (LTV:CAC, DSCR). Reviewer opus PASS + 7 copy fixes.
- 2026-10-22 · E · E36 Bakery template (retail counter + wholesale) · DONE · https://github.com/henrysheykin/finmodel-app/pull/54
  engine/templates/bakery.py: daily customers × ticket with a year-neutral holiday peak, wholesale accounts × weekly order,
  waste on unsold production, delivery; Base cash-positive every month; app/bizmodel.py reads kpi_reference for KPI rows.
  Reviewer opus: FAIL → fixes (memo figures from the twin, monthly = annual incl. year 1, established headcount, equity) → PASS.
  For Henry: R1 CFO review (HUMAN_TODO).
- 2026-10-22 · E · no ready task (E32, E36, E38, E40, E41, E42 IN_PROGRESS in other sessions; E33 waits on E32; E23 NEEDS_HENRY A1) · early exit
- 2026-10-22 · E · E45 Guest house / B&B template · DONE · https://github.com/henrysheykin/finmodel-app/pull/61
  engine/templates/guest_house.py: rooms × nights × occupancy (ramp, season, cap 100 %) × ADR, breakfast and extras, cleaning
  per stay, OTA commission, housekeeper payroll; property loan as an annuity (level payment, second annuity template after real
  estate). CI fix: length of stay 1–60 nights, divided by MAX(1, …); loan test now follows loan_style, annuity set pinned.
  Reviewer opus PASS. For Henry: R1 CFO review (HUMAN_TODO).
- 2026-10-22 · E · E44 Pet grooming & boarding template · DONE · https://github.com/henrysheykin/finmodel-app/pull/60
  engine/templates/pet_care.py: grooms/day capped by the lower of tables and groomer FTE capacity × price, retail per groom; boarding
  runs × nights × occupancy (cap 100 %, Jun–Aug + Dec peak netting to zero) × nightly rate; groomer base + commission in cost of sales;
  tables/tubs, kennel build-out, optional land; samples full + full-5y; memo with 11 CFO questions. Implementer sonnet, reviewer opus
  PASS, 3 lows fixed (ramp × season gap bounded by a test and sized in the memo). For Henry: R1 CFO review (HUMAN_TODO).
- 2026-10-22 · E · E43 Auto repair shop template · DONE · https://github.com/henrysheykin/finmodel-app/pull/59
  engine/templates/auto_repair.py: repair orders × billed hours, capped by the lower of bays and technicians; labor at an
  effective rate, parts revenue per billed hour × parts margin, shop supplies fee; technician payroll in cost of sales; lifts,
  diagnostic tools, optional land as capex; samples full + full-5y; memo. Reviewer opus PASS, 3 lows fixed. CI test job hit the
  30-min cap at 89% with no failure → timeout raised to 45 min (suite now ~30 min). For Henry: R1 CFO review (HUMAN_TODO).
- 2026-10-21 · E · E39 Car wash template (express tunnel + memberships) · DONE · https://github.com/henrysheykin/finmodel-app/pull/57
  engine/templates/car_wash.py: retail cars/day × price with ramp and growth, unlimited members (adds − churn) × fee, tunnel
  capacity cap, cost per wash, optional owned land (ADR-011, not depreciated); samples full + full-5y. Reviewer opus PASS after
  fixes (monthly cash low in memo, cars_g, land, working-capital days). test_real_estate land check generalised per ADR-011.
  For Henry: R1 CFO review (HUMAN_TODO).
- 2026-10-21 · E · E37 Salon template (hair salon / barbershop) · DONE · https://github.com/henrysheykin/finmodel-app/pull/56
  engine/templates/salon.py: chairs × utilisation × hours × services/hour × price, retail attach, chair rent from renters,
  commission + payroll tax in cost of sales; E31 KPI hooks; samples full + full-5y. Implementer sonnet, reviewer opus PASS after
  fixes (inventory days, growing-stage chairs, flat marketing growth, 5-year stage test). For Henry: R1 CFO review (HUMAN_TODO).
- 2026-10-21 · E · E35 Business-model pages engine (ADR-014) · DONE · https://github.com/henrysheykin/finmodel-app/pull/55
  /business-models/ from content/business-models/*.md ({{table}}, {{chart}}, {{num}}): six tables + two SVG charts from the
  sample brief via the reference, every cell checked against the rebuilt and the committed <key>-full-5y.xlsx (all templates);
  cafe page; copy rule (cited figures, 900–1,500 words). Reviewer opus PASS + 6 lows fixed. For Henry: glance at the SBA link.
- 2026-10-21 · E · E34 Calculator engine (ADR-014) · DONE · https://github.com/henrysheykin/finmodel-app/pull/53
  /calculators section: spec files in content/calculators/, hand-written JS + Python evaluators (no eval), Node parity test
  in CI, model promotion block (tier features per ADR-013, configured prices), three cafe calculators. Implementer sonnet,
  reviewer opus PASS (7 lows → follow-up PR). For Henry: optional read of the three cafe calculator texts.
- 2026-10-21 · E · E29 Scenarios sheet, live Low / Base / High · DONE · [#52](https://github.com/henrysheykin/finmodel-app/pull/52)
  engine/scenarios.py: the period calculation copied 3× on a new "Scenario calc" sheet (Full, between Headcount and Checks),
  each copy reading Inputs B / C / D; Scenarios sheet: key drivers, 10 outputs Low / Base / High / Active, per-year tables,
  4 line charts 2×2; check "Scenarios: Active = selected scenario"; challenger recomputes every Low / Base / High cell.
  Build time per Full monthly 5-year model: build 0.4→1.0 s, LibreOffice recalc 2.0→2.6 s (formulas ×3.3). ADR-013 note added.
