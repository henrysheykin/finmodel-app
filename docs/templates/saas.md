# SaaS / software template — assumption memo

Template key `saas` (`engine/templates/saas.py`). Sample: `samples/saas-full.xlsx`
(stage *early*, Full tier, monthly, 3 years; rebuild with
`python -m engine.build default:saas:early samples/saas-full.xlsx --recalc`).

Status: **awaiting CFO review (HUMAN_TODO R1)**. All defaults below are illustrative
starting points for the wizard's sample-data path, not market statistics; the customer
replaces them with their own numbers.

## How the model works

**Customers.** New customers per period = organic/referral adds (input per month, growing
once a year) + paid adds (paid marketing spend ÷ paid CAC). Monthly columns:
`closing = opening × (1 − churn) + new`. Annual columns compound the same monthly rate
over 12 months and treat customers won during the year as joining mid-year:
`closing = opening × (1 − churn)^12 + new × (1 − churn)^6`.

**MRR waterfall.** Opening MRR → + new MRR (new customers × MRR per new customer, which
rises once a year by the price increase) → + expansion (% of opening MRR per month) →
− churned MRR (churn % of opening MRR) → closing MRR. Annual columns compound
`(1 − churn + expansion)` the same way and show expansion less churn as one line.

**Revenue** = average of opening and closing MRR × months in the period (mid-period
convention for adds and losses).

**Cost of revenue** = hosting & payment fees (% of revenue) + support & onboarding cost per
average customer per month. Typical gross margin with the defaults: ~88%.

**Operating expenses** = payroll by role (Headcount sheet: FTE × salary × (1 + payroll taxes)
× wage growth; each role's FTE steps up once a year by its headcount growth rate) + paid
marketing + software & tools per FTE + office + other G&A.

**Deferred revenue (simplified).** Share of MRR billed annually in advance × closing MRR × 6:
on average half of an annual prepayment is unearned at any date. It sits in liabilities and
its increase adds to operating cash flow.

**Shared engine** (ADR-003): depreciation, loan, tax loss carry-forward, receivable /
payable days, cash flow and balance sheet are the same for every template.

## SaaS metrics table (Dashboard in Full, P&L sheet in Light)

| Metric | Definition |
|---|---|
| Customers, MRR (year end) | Closing values of the last period of the year |
| ARR | Year-end MRR × 12 |
| Average MRR per customer | Year-end MRR ÷ year-end customers |
| Blended CAC | Paid marketing spend ÷ all new customers (organic included) |
| LTV | Average MRR per customer × gross margin ÷ monthly churn (0 when churn is 0) |
| LTV ÷ CAC | LTV ÷ blended CAC |
| CAC payback | Blended CAC ÷ (average MRR per customer × gross margin), months |
| Net burn per month | −(operating + investing cash flow) ÷ months in the period, last period of the year |
| Runway | Year-end cash ÷ net burn (0 when not burning or out of cash) |

The challenger recomputes year-end customers, year-end MRR and new customers per year in
plain Python, on top of the standard P&L / cash / balance-sheet checks.

## Default drivers by stage (Low / Base / High; one value = same in all scenarios)

| Driver | Unit | Order | Planning | Early | Growing | Established |
|---|---|---|---|---|---|---|
| Paying customers at start | # | L ≤ B ≤ H | 0 | 30 | 300 | 3,000 |
| Average MRR per new customer (ARPA) | $ / month | L ≤ B ≤ H | $59 / $79 / $99 | $79 / $99 / $119 | $99 / $129 / $149 | $230 / $250 / $270 |
| Price increase per year for new customers | % | L ≤ B ≤ H | 0.0% / 3.0% / 5.0% | 0.0% / 3.0% / 5.0% | 0.0% / 3.0% / 5.0% | 0.0% / 3.0% / 5.0% |
| Customer churn per month | % | L ≥ B ≥ H | 5.0% / 3.5% / 2.5% | 4.5% / 3.0% / 2.0% | 3.0% / 2.0% / 1.5% | 2.0% / 1.5% / 1.0% |
| Expansion MRR per month, % of opening MRR | % | L ≤ B ≤ H | 0.0% / 0.5% / 1.0% | 0.0% / 0.5% / 1.0% | 0.0% / 0.5% / 1.0% | 0.0% / 0.5% / 1.0% |
| Organic / referral new customers per month (year 1) | # / month | L ≤ B ≤ H | 3 / 5 / 8 | 8 / 12 / 18 | 20 / 30 / 45 | 30 / 40 / 50 |
| Growth of organic new customers per year | % | L ≤ B ≤ H | 10.0% / 30.0% / 50.0% | 10.0% / 30.0% / 50.0% | 10.0% / 30.0% / 50.0% | 10.0% / 30.0% / 50.0% |
| Paid marketing budget per month (year 1) | $ / month | — | $3,000 | $8,000 | $30,000 | $60,000 |
| Paid marketing budget growth per year | % | — | 20.0% | 20.0% | 20.0% | 20.0% |
| Paid customer acquisition cost (CAC) | $ | L ≥ B ≥ H | $500 / $400 / $300 | $600 / $450 / $350 | $900 / $700 / $550 | $1,200 / $1,000 / $800 |
| Share of MRR billed annually in advance | % | — | 20.0% | 20.0% | 20.0% | 20.0% |
| Hosting & payment fees, % of revenue | % | L ≥ B ≥ H | 12.0% / 10.0% / 8.0% | 12.0% / 10.0% / 8.0% | 12.0% / 10.0% / 8.0% | 12.0% / 10.0% / 8.0% |
| Support & onboarding cost per customer per month | $ | L ≥ B ≥ H | $3 / $2 / $1.50 | $3 / $2 / $1.50 | $3 / $2 / $1.50 | $3 / $2 / $1.50 |
| Software & tools per FTE per month | $ | — | $150 | $150 | $150 | $150 |
| Office & rent per month | $ | — | $0 | $1,500 | $6,000 | $20,000 |
| Other G&A per month (legal, accounting, insurance) | $ | — | $1,500 | $3,000 | $8,000 | $25,000 |
| Start-up capex (equipment) | $ | — | $10,000 | $20,000 | $60,000 | $150,000 |
| Engineering & product: headcount (FTE) | FTE | L ≤ B ≤ H | 2 | 3 | 6 | 20 |
| Engineering & product: salary per FTE per year | $ | — | $120,000 | $125,000 | $130,000 | $135,000 |
| Engineering & product: headcount growth per year | % | L ≤ B ≤ H | 50.0% | 50.0% | 40.0% | 20.0% |
| Engineering & product: first month on payroll | month # | — | 1 | 1 | 1 | 1 |
| Sales & marketing: headcount (FTE) | FTE | L ≤ B ≤ H | 1 | 1.5 | 3 | 14 |
| Sales & marketing: salary per FTE per year | $ | — | $90,000 | $95,000 | $100,000 | $105,000 |
| Sales & marketing: headcount growth per year | % | L ≤ B ≤ H | 100.0% | 50.0% | 40.0% | 20.0% |
| Sales & marketing: first month on payroll | month # | — | 4 | 1 | 1 | 1 |
| Customer success: headcount (FTE) | FTE | L ≤ B ≤ H | 0.5 | 1 | 2 | 8 |
| Customer success: salary per FTE per year | $ | — | $60,000 | $60,000 | $65,000 | $65,000 |
| Customer success: headcount growth per year | % | L ≤ B ≤ H | 100.0% | 50.0% | 40.0% | 20.0% |
| Customer success: first month on payroll | month # | — | 7 | 1 | 1 | 1 |
| G&A (finance, ops): headcount (FTE) | FTE | L ≤ B ≤ H | 0.5 | 0.5 | 1 | 6 |
| G&A (finance, ops): salary per FTE per year | $ | — | $75,000 | $80,000 | $85,000 | $90,000 |
| G&A (finance, ops): headcount growth per year | % | L ≤ B ≤ H | 0.0% | 50.0% | 30.0% | 15.0% |
| G&A (finance, ops): first month on payroll | month # | — | 1 | 1 | 1 | 1 |
| Payroll taxes & benefits, % of salary | % | — | 20.0% | 20.0% | 20.0% | 20.0% |
| Wage growth per year | % | — | 4.0% | 4.0% | 4.0% | 4.0% |
| Equity raised at start | $ | — | $500,000 | $3,000,000 | $3,000,000 | $1,000,000 |
| Loan drawn at start | $ | — | $0 | $0 | $0 | $0 |
| Loan interest rate per year | % | — | 0.0% | 0.0% | 0.0% | 0.0% |
| Loan repayment term | years | — | 1 | 1 | 1 | 1 |
| Customer payment terms (receivable days) | days | — | 5 | 5 | 5 | 5 |
| Inventory held (days of COGS) | days | — | 0 | 0 | 0 | 0 |
| Supplier payment terms (payable days) | days | — | 30 | 30 | 30 | 30 |
| Depreciation period for capex | years | — | 3 | 3 | 3 | 3 |
| Income tax rate | % | — | 21.0% | 21.0% | 21.0% | 21.0% |

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Scenario | Revenue Y1 / Y2 / Y3 | EBITDA Y3 | Cash end Y3 | Customers end Y3 |
|---|---|---|---|---|---|
| planning | Low | $32k / $81k / $119k | ($1,364k) | ($2,127k) | 189 |
| planning | Base | $64k / $183k / $304k | ($1,195k) | ($1,814k) | 345 |
| planning | High | $122k / $387k / $725k | ($805k) | ($1,129k) | 628 |
| early | Low | $126k / $280k / $403k | ($1,681k) | ($557k) | 479 |
| early | Base | $225k / $591k / $979k | ($1,156k) | $412k | 886 |
| early | High | $378k / $1,133k / $2,128k | ($84k) | $2,277k | 1,535 |
| growing | Low | $641k / $1,147k / $1,613k | ($2,622k) | ($2,968k) | 1,538 |
| growing | Base | $1,067k / $2,316k / $3,756k | ($665k) | $715k | 2,602 |
| growing | High | $1,570k / $3,979k / $7,279k | $2,642k | $5,952k | 4,154 |
| established | Low | $8,589k / $9,318k / $10,311k | ($2,453k) | ($1,953k) | 3,931 |
| established | Base | $10,217k / $12,946k / $16,448k | $3,294k | $8,187k | 5,357 |
| established | High | $12,150k / $17,948k / $26,042k | $12,450k | $21,968k | 7,372 |

*planning* and the Low cases run out of cash inside three years on purpose: the
"Funding sufficient" check turns to WARN and the Dashboard shows the lowest cash point, which
is the funding gap the founder has to raise.

## Simplifications to review

1. Monthly churn and expansion are constant over the horizon (no cohort curves).
2. Paid CAC is flat; no channel saturation as budget grows.
3. One ARPA for all new customers; no plan mix or seat-based pricing.
4. Deferred revenue uses a fixed 6-month average unearned balance; no billing calendar.
5. Headcount grows in yearly steps, not hire by hire.
6. Sales commissions are not modelled separately (sit inside sales & marketing payroll).
7. Annual columns use compounding with a mid-year convention for new customers, so they
   differ from a monthly build of the same inputs by a few percent (tested ≤ 8% on revenue).

## Questions for the CFO review

- Are the stage defaults sensible as starting points (ARPA, churn, CAC, team size, equity)?
- Should revenue use closing MRR rather than the average of opening and closing?
- Should payroll for sales roles carry a commission % of new ARR?
- Deferred revenue: is the 6-month convention acceptable for a planning model?
