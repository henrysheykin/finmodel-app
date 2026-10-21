# Backlog

Open tasks only; finished and cancelled ones are one line each in `docs/DONE.md`.
Status values: `TODO` · `IN_PROGRESS (date)` · `BLOCKED: reason` · `NEEDS_HENRY: what`. Protocol and model
routing: see `CLAUDE.md`. Each track edits only its own section. Pick the first ready task in your track.
Every task has `Model: opus|sonnet|haiku` (who does it; reviews are always opus).

Skill names are as shown in the session's skill list (prefixes may differ:
`xlsx` may appear as `anthropic-skills:xlsx`). "(opt)" = use if installed.

---

## Track E — Engineering (daily)

> **Priority (Henry, 2026-10-21, ADR-014):** in parallel with the workbook standard: E34, E35 and the templates
> E36–E45 (any order, one per PR). Workbook standard: E29, E30 (PR #47), E32, then E33 after all of them (E31 done).
>
> **Earlier priority (Henry, 2026-10-20):** workbook standard v1 (ADR-013, `docs/WORKBOOK_STANDARD.md`): E26, E27, E28 (done) →
> E30, E31, E32 (any order) → E29 → E33. E23 still waits on the OpenAI key (A1).
> Visual reference for every E26–E33 task: `design/workbook-standard-v1-prototype.xlsx` (compare your build with it).
>
> Earlier: **E23** (waits on the OpenAI key, A1). (E25 OpenAI done #41; E24 done #42.) All earlier E tasks are done (`docs/DONE.md`).
> New industries are one file each (ADR-009, `docs/templates/ADDING_A_TEMPLATE.md`; follow E21/E22, Model: sonnet).
> Customer login = passwordless magic link by email (ADR-006).

### E29 — Scenarios sheet, live Low / Base / High
- status: IN_PROGRESS (2026-10-21) — branch E29-live-scenarios (dispatcher session)
- Model: opus
- depends: E26, E27
- skills: xlsx, engineering:testing-strategy
- do: ADR-013 §1. Full only. Parallel calculation chains for scenarios 1/2/3 that read the inputs' B / C / D
  columns directly (e.g. one "Scenario calc" grid sheet with three stacked copies of the annual-relevant lines,
  generated from the same Line formulas with a scenario-specific `{in:…}` resolver). Scenarios sheet: key drivers
  table (template hook), outputs Low / Base / High / Active, per-year tables (revenue, EBITDA, net income, cash),
  4 charts 2×2. Challenger: recompute every Low / Base / High cell with the Python reference for that scenario,
  independent of the selector.
- done when: changing an input on Inputs updates all three columns after recalc; the Active column equals the
  matching scenario column for each selector value; challenger covers it; all templates PASS; build time per
  model measured and noted in the RUNLOG (worker budget).


### E32 — Break-even chart and Valuation layout
- status: IN_PROGRESS (2026-10-21)
- Model: sonnet
- depends: E27
- skills: xlsx
- do: ADR-013 §1. Break-even: one large chart (revenue bars + break-even revenue line). Valuation: layout and
  formats to the standard, assumptions stay links to Inputs, no chart.
- done when: chart present after recalc in both tiers; all templates PASS.

### E34 — Calculator engine (ADR-014)
- status: IN_PROGRESS (2026-10-21) — implementer agent of the dispatcher session
- Model: sonnet
- depends: —
- skills: frontend-design, engineering:testing-strategy
- do: site section `/calculators/` and `/calculators/<slug>`. A calculator is one spec file in
  `content/calculators/<slug>.md`: front matter (slug, title, description 70–200 chars, keyword, optional template key —
  without one the page shows the generic promotion block and the wizard opens without a preset — related calculators) + YAML-like blocks for `inputs` (key, label, unit, default, min, max, step, format),
  `outputs` (key, label, formula, format, optional "highlight"), optional `table` (one input swept over values →
  outputs) and `examples` (inputs → expected outputs), then the Markdown explanation. Formulas use a small safe
  expression language (numbers, input / output keys, + − × ÷ ^, parentheses, comparisons, `min`, `max`, `round`,
  `abs`, `if(cond, a, b)`), evaluated by `web/static/calc.js` and by a Python twin `app/calc_expr.py`, both hand-written parsers
  (never `eval` / `Function` / `ast` execution); `round` is half away from zero in both; inputs are clamped to
  min / max; any non-finite result (÷ 0, NaN, ∞, negative base ^ fraction) shows "—"; JS and Python must agree
  within 1e-9 relative. Tests: every spec parses, every output key is
  defined once with no cycles, every example matches in Python, and the JS evaluator gives the same results on
  the same examples (node in CI via `actions/setup-node`, or the Playwright browser tests that
  already run in CI — either way the parity test must run in CI, not skip). Page: inputs left, live
  results right (mobile: stacked), the optional sensitivity table, the explanation, FAQ JSON-LD when the body has
  a FAQ section, related calculators, and the **model promotion block** (partial template, data from the
  template: title, what the full model adds with features per tier as ADR-013 sets them (Light never promised
  statements or valuation), the sample download, CTA to the wizard on that template, the configured tier
  prices (`app/config.py`, as tests/test_seo.py reads them)). Default input values
  are "example values" unless cited. Index page grouped by industry; add both new sections to the sitemap and
  llms.txt (not automatic); canonical per page; a calculator links to (never duplicates) the SEO guide on the same
  topic; the E35 cited-figure copy check also runs on `content/calculators/`; design tokens of design v2 (no competitor palette). Ship three cafe
  calculators as the reference specs: menu price (target food-cost %), food cost %, break-even covers per day.
- review focus: parser safety (no code execution path, deep nesting / huge input handled), JS = Python parity.
- done when: the three pages render and work without JS errors (Playwright test fills inputs, reads results);
  Python and JS evaluators agree on every example; Lighthouse-style basics (title, description, canonical, h1,
  no layout shift from the results panel); all tests green.

### E35 — Business-model pages engine (ADR-014)
- status: IN_PROGRESS (2026-10-21) — implementer agent of the dispatcher session
- Model: sonnet
- depends: —
- skills: dataviz, frontend-design
- do: section `/business-models/` and `/business-models/<slug>`: Markdown in `content/business-models/<key>.md`
  (front matter as SEO pages + `template`) with table placeholders `{{table:<name>}}`, chart placeholders
  `{{chart:<name>}}` and inline figures `{{num:<table>.<cell>}}` — every model figure in the prose uses `num`, so a
  sample rebuild never leaves a stale number. Tables computed by `app/bizmodel.py` from the template's sample brief (Base scenario,
  stage = `sample_stage`, Full, monthly, 5 years — exactly the sample `<key>-full-5y.xlsx`, which this task adds
  to the built and committed samples for every template; the page offers that file and the test compares against it) through the engine's plain-Python reference (`reference_run`,
  `annualise`, `engine/goals.py` break-even / funding): `drivers` (key numbers Low / Base / High with units),
  `startup` (capital spending lines by item, then the Break-even funding lines exactly as the workbook labels
  them: capital spending up to the lowest cash point, operating cash burn, loan repayments, cash buffer, funding
  required, sources, surplus / shortfall),
  `pnl` (revenue, cost of sales, gross margin, operating expenses by line, EBITDA, net income — 5 years),
  `costs` (year-1 and year-5 cost structure as % of revenue), `unit` (the template's KPI rows, annual),
  `breakeven` (first EBITDA-positive month, lowest cash month, funding required, payback). Charts as inline SVG
  (revenue vs costs by year; cost structure bars) from the same data. Cached per template; a test rebuilds the
  sample workbook, recalculates it and checks every table cell against the workbook (within $1). Page: H1, intro,
  the tables with a caption "Illustrative Base case of the sample model — your model uses your numbers", the
  sample download, CTA to the wizard, links to the industry's calculators (by `template`) and SEO page. Index page
  with one card per template; sitemap + llms.txt; JSON-LD Article + breadcrumbs. Copy test for `content/business-models/`: no unknown placeholders, no
  `[UPPER]` placeholders except prices, every `$` or `%` figure outside a placeholder sits in a sentence with an
  external link, 900–1,500 words. Update `docs/templates/ADDING_A_TEMPLATE.md` §4 (business-model and calculator
  pages may go live before the CFO sign-off, ADR-014). `/business-models/<key>` explains the business; the
  `/models/…` SEO pages sell the model — cross-link them, distinct titles and canonicals. Ship one reference page
  (`cafe`) with real copy.
- review focus: every page figure equals the committed 5-year sample (no tolerance looser than $1).
- done when: the cafe page renders with all six tables and both charts; the table-vs-workbook test passes for
  every registered template; all tests green.

### E36–E45 — Ten local-business templates (ADR-014)
One task per template, each one file + tests + sample + memo per `docs/templates/ADDING_A_TEMPLATE.md`
(dashboard hooks, KPI rows with `kpi_checked`, `key_numbers`, stage defaults, R1 line in HUMAN_TODO).
- Model: sonnet · depends: — · skills: xlsx · samples: `<key>-full` and `<key>-full-5y` (ADR-014 pages)
- done when (each): the tier × granularity × horizon matrix PASSes the challenger; four stage defaults PASS;
  monthly = annual; the memo lists every assumption with its source or "assumption" and the CFO questions.

| id | key | business | revenue drivers (minimum) | status |
|---|---|---|---|---|
| E36 | `bakery` | Bakery (retail counter + wholesale) | daily customers × ticket, wholesale accounts × order, production waste % | IN_PROGRESS (2026-10-21) |
| E37 | `salon` | Hair salon / barbershop | chairs × utilisation × services per hour × price, retail product attach, commission vs chair rent | IN_PROGRESS (2026-10-21) |
| E38 | `dental` | Dental practice | operatories × patient visits × fee per visit, hygiene recall, insurance mix / collection rate | TODO |
| E39 | `car_wash` | Car wash (express + memberships) | cars per day × price, unlimited-plan members × fee, chemicals & utilities per car | IN_PROGRESS (2026-10-21) |
| E40 | `laundromat` | Laundromat (self-service + wash & fold) | machines × turns per day × price, wash & fold lbs × price, utilities per cycle | TODO |
| E41 | `childcare` | Childcare / daycare centre | licensed capacity × enrollment % × tuition, staff-to-child ratio payroll | TODO |
| E42 | `food_truck` | Food truck | service days × meals per day × ticket, events / catering, food cost %, permits | TODO |
| E43 | `auto_repair` | Auto repair shop | bays × billed hours × labor rate, parts revenue × margin, technician productivity | TODO |
| E44 | `pet_care` | Pet grooming & boarding | grooms per day × price, kennel runs × occupancy × nightly rate | TODO |
| E45 | `guest_house` | Guest house / B&B | rooms × occupancy × ADR, breakfast / extras, cleaning per stay, property loan (annuity) | TODO |

### E33 — Roll-out: samples, golden tests, site, copy
- status: TODO
- Model: sonnet
- depends: E26, E27, E28, E29, E30, E31, E32
- skills: xlsx, frontend-design (opt)
- do: rebuild every sample (`scripts/build_samples.py`, `--seo`, goal review files), golden tests, the landing
  preview (`app/xlview.py` + `web/static/landing.js`: new sheet set; charts shown as a labelled placeholder or a
  static rendering — keep it faithful to the file), wizard / landing / SEO / email copy that describes sheets or
  says the goal adds sheets, `docs/templates/*.md` (sheet list; real_estate.md keeps "Returns in both tiers"),
  HUMAN_TODO R1 line for the new sheets
  (Scenarios, Sources & Uses, ratios) and refresh `Documents\StartupModel-review` guidance in the RUNLOG.
- done when: CI green with the new samples; landing tests pass; no copy promises sheets a tier does not have.

### E23 — Eval: which model fills the brief
- status: NEEDS_HENRY: live run needs `OPENAI_API_KEY` in the cloud environment (HUMAN_TODO A1); E25 (OpenAI) done. continue: harness merged (PR #40), on OpenAI since E25;
  run `python -m evals.brief_model_eval --record evals/runs/<date> --memo`, commit the filled memo, then DONE.
- Model: sonnet
- depends: E08 (LLM brief builder, done #39), BRIEF_MODEL plumbing (token-budget PR, done), E25 (OpenAI, done #41)
- skills: engineering:testing-strategy
- do: `evals/brief_model_eval.py`: 6 industries × 10 wizard-answer variants (fixed, committed in `evals/cases/`)
  through `gpt-6-luna`, `gpt-6.1-sol` and `gpt-6-astra` (ADR-012) via the E08 builder. Each brief goes
  through the existing brief validation (template `validate`) and the challenger (build → recalc → challenge).
  Per model: share of briefs that pass, mean and p95 response time, mean cost per order in $ from the API's
  token usage (input, output, cached input, cache write) × current prices (developers.openai.com pricing).
  Live API calls only when run by hand with `OPENAI_API_KEY` set; not part of CI (CI tests the script on
  recorded fixtures).
- done when: `docs/memos/brief-model-eval.md` with the table and a recommendation: the cheapest model whose
  pass share is not below the reference and whose p95 ≤ 15 s. Reference = gpt-6-astra pass share (no model is in
  production yet; BRIEF_MODEL is empty). Henry sets `BRIEF_MODEL` from it (add to HUMAN_TODO).

---

## Track M — Marketing & content (weekdays)

> Priority (Henry, 2026-10-21, ADR-014): M13 → M15 (need E34/E35) → M14 → M16 (need the new templates).
> Facts rule: no invented numbers. Benchmarks and market figures only with a cited source (link in the page);
> everything else is "the sample's assumption". Skills: use web research for sources, `small-business:seo-ai-visibility`
> (opt) for search intent, `docs` (opt) for structure.

### M13 — Business-model pages, existing 7 industries
- status: TODO
- Model: sonnet
- depends: E35
- skills: small-business:seo-ai-visibility (opt), dataviz (opt)
- do: `content/business-models/<key>.md` for cafe (refine the E35 reference page), saas, retail, services,
  home_services, fitness, real_estate: how the business makes money, revenue model and drivers, cost structure,
  startup investment and funding, unit economics, break-even and what moves it, risks, how to use the model
  (Low / Base / High), FAQ. Uses every table placeholder; 900–1,500 words each; links to the industry's SEO page and
  calculators.
- done when: 7 pages render; the E35 copy test passes (placeholders, cited figures, 900–1,500 words).

### M14 — Business-model pages, the 10 new industries
- status: TODO
- Model: sonnet
- depends: E35, E36–E45 (each page after its template)
- skills: as M13
- do: as M13 for bakery, salon, dental, car_wash, laundromat, childcare, food_truck, auto_repair, pet_care,
  guest_house. Ship in batches as templates merge.
- done when: 10 pages render; copy test passes.

### M15 — Calculators, existing industries + cross-industry
- status: TODO
- Model: sonnet
- depends: E34
- skills: as M13, frontend-design (opt)
- do: spec files (with worked examples and 400–900 words of explanation: what it computes, formula in words,
  how to read the result, typical mistakes, FAQ) for: cafe / restaurant (table turnover revenue, recipe cost,
  prime cost — beyond the three E34 ones), SaaS (LTV ÷ CAC, MRR growth & churn, runway), retail (markup vs margin,
  inventory turnover, store break-even), services (billable utilisation & rate, project price), home services
  (job price, technician capacity), fitness (membership break-even, churn → members), real estate (cap rate,
  cash-on-cash, DSCR, mortgage payment), cross-industry (break-even, startup cost, loan payment, payback).
  Every page ends with the model promotion block (E34) and explains what the calculator cannot do that the model
  does (time, cash, scenarios, lender-ready statements).
- done when: all specs pass the E34 tests; pages render; examples hand-checked in the PR description.

### M16 — Calculators, the 10 new industries
- status: TODO
- Model: sonnet
- depends: E34, E36–E45 (each after its template)
- skills: as M15
- do: 2–3 calculators per new industry, e.g. bakery (recipe cost & unit price, daily break-even units), salon
  (service price, chair rent vs commission), dental (chair-hour revenue, new-patient value), car wash (membership
  MRR, cost per wash), laundromat (revenue per machine, machine payback), childcare (enrollment break-even, ratio
  payroll), food truck (break-even meals per day, event vs street day), auto repair (effective labor rate, parts
  margin), pet care (grooming price, boarding occupancy revenue), guest house (ADR / occupancy / RevPAR,
  break-even occupancy).
- done when: as M15.
---

## Track P — Project management (weekly, Monday)

P runs every Monday and never "completes": it reviews, it does not build.
- Model: opus
- skills: engineering:standup, docs
- do: read RUNLOG, BACKLOG, open PRs, CI status, HUMAN_TODO. Write
  `docs/STATUS.md` (done last week, in progress, blocked, next week, risks,
  Henry's queue ordered by urgency). Detect stuck tasks (IN_PROGRESS > 3 days,
  same task failing twice) and either split them in BACKLOG with a note or mark
  BLOCKED with the reason. May reorder TODO tasks inside a track; may add tasks
  (prefix the id with the track, next free number). Report to Henry in Russian.
