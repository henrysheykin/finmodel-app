# Run log

Newest first. One entry per scheduled run: date · track · task · result · PR · notes for Henry.

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
- 2026-10-19 · P · weekly PM review · STATUS.md rewritten
  E 24/25 done, M 12/12 closed (3 cancelled); no open PRs, CI on main green, startup-model.com /healthz 0.1.0.
  No stuck tasks (nothing IN_PROGRESS); only E23 open, NEEDS_HENRY (A1). E and M scheduled tasks are switched off since 2026-10-18.
  For Henry: R1 sign-offs are the critical path to live payments; then VAT (G1.1), G1.6, G1.8–G1.9; A1 + switch E back on for E23.

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
