# Run log

Newest first. One entry per scheduled run: date · track · task · result · PR · notes for Henry.

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
- 2026-10-21 · E · E30 Sources & Uses sheet · DONE · [#47](https://github.com/henrysheykin/finmodel-app/pull/47)
  Full only, after Valuation: funding structure (equity / loan, shares, gearing, funding required and surplus from Break-even)
  + doughnut; sources and uses of cash for the first N periods (input, default 12 months / 1 year, capped) + uses bar chart;
  in-file check "Sources & uses balance"; challenger recomputes every amount at the default N. $'000, ink links (report sheet).
- 2026-10-21 · E · E31 KPIs & ratios sheet · DONE · https://github.com/henrysheykin/finmodel-app/pull/50
  engine/kpis.py (Full only, after Valuation): ratios by year (growth, margins, payroll / marketing / opex %, current ratio, D/E,
  ROA, ROE) with "n/a" guards, DuPont + in-file check (FAIL on mismatch, n/a when no comparable year), template KPI table moved
  from the Dashboard ($'000, per-unit rows in $), blank Target input column, 4 charts (2 via new `kpi_charts` hook). Challenger
  recomputes every ratio, DuPont leg, derived KPI and Dashboard industry line (≤ $1); wider `kpi_checked` in all 7 templates;
  DASH_USD_K dropped; funding tile sub-line numeric. Implementer sonnet, reviewer opus PASS (2 rounds), CI green. Build +0.03 s.
  For Henry: nothing. Note: PR #47 (E30) and branch E29 will need a merge of main (sheet order, test sheet lists).
- 2026-10-20 · E · E28 Summary sheet (statements, selected year by month) · PR open (reviewer next) · https://github.com/henrysheykin/finmodel-app/pull/46
  engine/summary.py (Full only): IS / CF / BS with every year linked to the statements (left) and one selected year by month
  (INDEX into the Monthly grid, switch R2) on the right, 3 charts beside the blocks; annual models: years only, charts by year;
  1-year horizon works. New check "Summary ties to statements" + Summary range in "No error values"; challenger covers the
  links; test: Dashboard Core financials = statement cells every year. For Henry: nothing.
- 2026-10-20 · E · E27 Dashboard v2 and the chart kit · PR open (reviewer next) · https://github.com/henrysheykin/finmodel-app/pull/45
  engine/charts.py (bar, hbar, line, combo with secondary axis, doughnut; 14.2 × 8.3 cm grid slots; value-only data labels) +
  engine/dashboard.py: selector + checks verdict, 6 tiles, Core financials rolled up from grid lines (Light too), industry block
  from the new Template hooks `dashboard_metrics` / `dashboard_chart` (all 7 templates), Funding & valuation, 4 charts; KPI table
  moved to row 47. Challenger recomputes every tile, Funding & valuation cell and Core line (`goals.dashboard_reference`).
  Also: ink report links, pine "Scenario shown", italic grey % lines on grid and module sheets. For Henry: nothing.
- 2026-10-20 · E · E26 workbook standard: style kit v2, sheet set by tier, Cover · DONE · https://github.com/henrysheykin/finmodel-app/pull/44
  engine/style.py v2 (ink/pine, Arial 9, yellow inputs, view-switch fill, tab colours, print setup, ◂ Contents links);
  sheets by tier (Light: Cover, Dashboard, Break-even, Inputs, P&L, Checks; Full adds Valuation, statements, grid, Headcount);
  modules by tier, investor Summary retired, goal → Cover purpose line; selector Dashboard!B4 in both tiers; stored pre-ADR
  briefs completed at build (tested). Interim Dashboard until E27. Samples not rebuilt yet (E33).
- 2026-10-20 · E · interactive with Henry: workbook standard v1 (ADR-013) · PR_LINK
  Henry's reference model analysed; two prototype rounds on a real SaaS engine workbook (16,964 engine cells equal in all 3
  scenarios, 0 errors) → approved. docs/WORKBOOK_STANDARD.md + ADR-013 (sheets by tier, goal = Cover line, live Scenarios,
  ink/pine look, yellow inputs), CLAUDE.md Excel rules, D12 closed, E26–E33 queued (priority note in BACKLOG).
  Reference: design/workbook-standard-v1-prototype.xlsx + scripts/prototypes/standard_v1/. Review folder on Henry's PC: Documents\StartupModel-review.
