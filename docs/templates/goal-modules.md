# Goal modules — assumption memo (E07)

The wizard's "Main goal" now changes the workbook. Every template gets the same modules; the numbers
come from the model's own period grid, so they move with the scenario switch (Low / Base / High).

| Goal in the wizard | Extra sheets |
|---|---|
| Revenue and profit projections / Something else | none |
| Startup costs and break-even | **Break-even** |
| Business valuation (DCF) | **Valuation** |
| Investor-ready pitch model | **Summary** (first sheet) + **Break-even** + **Valuation** |

Sample for review: `samples/cafe-investor_pitch.xlsx` (cafe, Full, monthly, 5 years, all three sheets).
Rebuild: `python scripts/build_samples.py --goal investor_pitch cafe`.

## Break-even sheet

- **Funding need up to the lowest cash point.** Lowest cash point = the period with the minimum closing
  cash. Uses of funds up to it = capital spending + operating cash burn (−operating cash flow, i.e. losses
  and working capital) + loan repayments. Funding required = uses + a **minimum cash buffer** (new input,
  default ≈ 3 months of year-1 operating expenses, rounded to $1,000). Sources = equity + loan from Inputs.
  Funding surplus / (shortfall) = sources − required. In-file check: lowest cash = sources − uses.
- **Timing:** first period with positive EBITDA, first period with positive net income, and the period the
  cash invested is paid back (cumulative operating + investing cash flow back to ≥ 0 after having been
  negative). Texts "Not within horizon" / "No investment to pay back" where they apply.
- **Annual break-even revenue** = operating expenses ÷ gross margin (cost of sales treated as variable,
  operating expenses as fixed), and margin of safety = (revenue − break-even) ÷ revenue.

## Valuation sheet

- **Unlevered free cash flow** per period = operating cash flow + interest × (1 − tax rate) − capital
  spending, summed per year.
- Year-end discounting at the WACC; check: sum of PVs = Excel `NPV()` of the same flows.
- **Terminal value** two ways, side by side: perpetual growth `FCF_final × (1 + g) ÷ (WACC − g)` and exit
  multiple `EBITDA_final × multiple`; enterprise value for each, the terminal share, cross-checks (implied
  multiple of the growth method, implied growth of the multiple method) and the average of the two.
- **Sensitivity**: 5 × 5 table of the perpetual-growth value, WACC ± 2 steps × growth ± 2 steps (steps are
  inputs, default 1 pp and 0.5 pp); centre cell must equal the headline value (in-file check).
- Value date = start of the plan, before the funding raised in period 1 (so the start-up capex is inside
  year-1 free cash flow).
- A brief is refused if WACC − terminal growth < 1 pp in any scenario. WACC is ordered Low ≥ Base ≥ High
  (higher discount rate = pessimistic case). A negative final-year free cash flow gives a WARN in Checks.

Default inputs by stage (illustrative):

| Stage | WACC Low / Base / High | Exit multiple Low / Base / High | Terminal growth |
|---|---|---|---|
| Planning | 30% / 25% / 20% | 3.0x / 4.0x / 5.0x | 1% / 2% / 3% |
| Early | 25% / 20% / 17% | 3.5x / 4.5x / 6.0x | same |
| Growing | 20% / 16% / 13% | 4.0x / 5.5x / 7.0x | same |
| Established | 15% / 12% / 10% | 5.0x / 6.0x / 8.0x | same |

## Summary sheet (investor pitch)

Headline financials by year (revenue, gross profit and margin, EBITDA and margin, net income, year-end
cash, FTE), investment highlights (revenue CAGR, equity / loan, funding required and surplus/shortfall,
lowest cash, first EBITDA-positive period, payback, enterprise value by both methods and the average),
then the template's own KPI table.

## Challenger

`engine/goals.py::reference` recomputes every module value in plain Python from the reference run (no
formulas): funding table, timing, break-even revenue, free cash flow, discount factors, PVs, terminal values,
enterprise values, cross-checks, CAGR and the Summary links. Each must match the workbook in all three
scenarios ($1 for money, 1e-6 for ratios, exact for periods and texts). Tested for every template.

## Questions for the CFO

1. Free cash flow for the terminal value: final-year FCF (current) or a normalised figure, e.g. EBIT × (1 − t)
   with capex = depreciation and no working-capital build? Growing businesses still carry growth capex and
   working capital in the final year, which lowers the perpetual-growth value.
2. Default WACC by stage (20–30% for planning/early small businesses) and exit multiples (3–8x EBITDA): fine
   as illustrative defaults, or would you set them per industry (e.g. SaaS on revenue multiples)?
3. Year-end discounting — switch to mid-year convention?
4. Interest tax shield at the headline tax rate even while losses are carried forward — acceptable?
5. Break-even treats all operating expenses as fixed (marketing as % of revenue is in fact variable). Good
   enough, or should templates mark their variable opex lines?
6. Cash buffer default ≈ 3 months of year-1 operating expenses — right rule of thumb?
