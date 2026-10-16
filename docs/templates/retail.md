# Retail / e-commerce template — assumption memo

Template key `retail` (`engine/templates/retail.py`). Sample: `samples/retail-full.xlsx`
(stage *growing*: online + 2 stores, Full tier, monthly, 3 years; rebuild with
`python -m engine.build default:retail:growing samples/retail-full.xlsx --recalc`).

Status: **awaiting CFO review (HUMAN_TODO R1)**. All defaults are illustrative starting points
for the wizard's sample-data path, not market statistics.

## How the model works

**Online channel.** Orders from new customers = non-paid website visits × conversion rate +
paid ads budget ÷ paid cost per order (CAC). Repeat orders = new-customer orders × repeat
multiplier (a steady-state shortcut for returning customers). Online gross sales = orders ×
average order value. Visits, ads budget and AOV change once a year by their growth rates.

**Store channel.** Store gross sales = stores open × selling area × sales per sq ft per year ×
(1 + like-for-like growth)^(year − 1) ÷ 12 per month. Stores open at the start, plus new stores
opened on the first day of each later year. Set the store drivers to zero for a pure
online business, or the visit and ads drivers to zero for a pure store business.

**Seasonality.** One driver: the Nov–Dec uplift. November and December are scaled by
(1 + uplift) and the other ten months by (1 − uplift ÷ 5), so the annual total is unchanged.
Annual columns therefore show exactly the sum of the months (tested).

**Net sales and margin.** Net sales = gross sales − returns & refunds (% of gross).
Product cost = % of net sales; gross profit is after product cost only. Fulfilment &
shipping (per online order) and payment processing (% of net sales) are operating costs, so
inventory (days of product cost) is not inflated by shipping.

**Operating expenses.** Fulfilment, payment processing, paid ads, payroll by role (four roles
with yearly headcount growth), store rent (sq ft × rent per sq ft), store running costs per
store, platform & software, other G&A.

**Capex.** Start-up capex + fit-out for the opening stores in period 1, then fit-out for each
year's new stores in its first period.

**Working capital.** Inventory = product cost × inventory days; receivables and payables from
the shared engine (ADR-003), all flowing through the cash flow statement and balance sheet.

## Retail metrics table (Dashboard in Full, P&L sheet in Light)

Visits, online orders, repeat orders and their share, online gross sales, average order value,
paid ads spend and its % of online sales, stores at year end, store sales, net sales, gross
profit and margin, product cost, year-end inventory and inventory turns
(product cost ÷ year-end inventory). The challenger recomputes online orders, online gross
sales and stores open in plain Python.

## Default drivers by stage (Low / Base / High; one value = same in all scenarios)

| Driver | Unit | Order | Planning | Early | Growing | Established |
|---|---|---|---|---|---|---|
| Website visits per month (year 1, non-paid) | # / month | L ≤ B ≤ H | 4,000 / 5,000 / 6,500 | 16,000 / 20,000 / 25,000 | 65,000 / 80,000 / 100,000 | 200,000 / 250,000 / 300,000 |
| Visit growth per year | % | L ≤ B ≤ H | 10.0% / 25.0% / 40.0% | 10.0% / 25.0% / 40.0% | 10.0% / 25.0% / 40.0% | 10.0% / 25.0% / 40.0% |
| Conversion rate (orders ÷ visits) | % | L ≤ B ≤ H | 1.5% / 2.0% / 2.5% | 1.8% / 2.2% / 2.6% | 2.0% / 2.4% / 2.8% | 2.2% / 2.6% / 3.0% |
| Average order value (before returns) | $ | L ≤ B ≤ H | $55 / $65 / $75 | $60 / $70 / $80 | $65 / $75 / $85 | $70 / $80 / $90 |
| Average order value growth per year | % | L ≤ B ≤ H | 0.0% / 2.0% / 4.0% | 0.0% / 2.0% / 4.0% | 0.0% / 2.0% / 4.0% | 0.0% / 2.0% / 4.0% |
| Repeat orders per new-customer order (returning customers) | x | L ≤ B ≤ H | 0.2x / 0.3x / 0.4x | 0.3x / 0.4x / 0.5x | 0.4x / 0.5x / 0.6x | 0.5x / 0.6x / 0.7x |
| Paid ads budget per month (year 1) | $ / month | — | $4,000 | $15,000 | $50,000 | $120,000 |
| Paid ads budget growth per year | % | — | 20.0% | 20.0% | 20.0% | 20.0% |
| Paid cost per order (CAC) | $ | L ≥ B ≥ H | $40 / $32 / $25 | $38 / $30 / $24 | $36 / $28 / $22 | $34 / $27 / $21 |
| Stores open at start | # | L ≤ B ≤ H | 0 | 0 | 2 | 8 |
| New stores opened each year from year 2 | # / year | L ≤ B ≤ H | 0 | 0 | 1 | 2 |
| Selling area per store | sq ft | — | 0 | 0 | 1,500 | 2,000 |
| Sales per sq ft per year (year 1) | $ / sq ft | L ≤ B ≤ H | $0 | $0 | $300 / $375 / $450 | $325 / $400 / $475 |
| Like-for-like store sales growth per year | % | L ≤ B ≤ H | 0.0% / 2.0% / 4.0% | 0.0% / 2.0% / 4.0% | 0.0% / 2.0% / 4.0% | 0.0% / 2.0% / 4.0% |
| Store rent per sq ft per year | $ / sq ft | — | $0 | $0 | $40 | $45 |
| Other running cost per store per month | $ | — | $0 | $0 | $2,500 | $3,500 |
| Fit-out capex per new store | $ | — | $0 | $0 | $150,000 | $200,000 |
| Seasonality: Nov–Dec sales uplift (annual total unchanged) | % | — | 30.0% | 30.0% | 30.0% | 30.0% |
| Returns & refunds, % of gross sales | % | L ≥ B ≥ H | 12.0% / 10.0% / 8.0% | 12.0% / 10.0% / 8.0% | 12.0% / 10.0% / 8.0% | 12.0% / 10.0% / 8.0% |
| Product cost, % of net sales | % | L ≥ B ≥ H | 45.0% / 42.0% / 39.0% | 45.0% / 42.0% / 39.0% | 45.0% / 42.0% / 39.0% | 45.0% / 42.0% / 39.0% |
| Fulfilment & shipping per online order | $ | L ≥ B ≥ H | $9 / $8 / $7 | $9 / $8 / $7 | $9 / $8 / $7 | $9 / $8 / $7 |
| Payment processing, % of net sales | % | — | 3.0% | 3.0% | 3.0% | 3.0% |
| E-commerce platform & software per month | $ | — | $500 | $1,500 | $4,000 | $12,000 |
| Other G&A per month | $ | — | $1,500 | $3,000 | $8,000 | $25,000 |
| Start-up capex (equipment, systems) | $ | — | $15,000 | $30,000 | $50,000 | $100,000 |
| Operations & fulfilment: headcount (FTE) | FTE | L ≤ B ≤ H | 1 | 2 | 6 | 15 |
| Operations & fulfilment: salary per FTE per year | $ | — | $50,000 | $50,000 | $50,000 | $52,000 |
| Operations & fulfilment: headcount growth per year | % | L ≤ B ≤ H | 50.0% | 30.0% | 20.0% | 10.0% |
| Operations & fulfilment: first month on payroll | month # | — | 1 | 1 | 1 | 1 |
| Marketing & e-commerce: headcount (FTE) | FTE | L ≤ B ≤ H | 1 | 1.5 | 4 | 8 |
| Marketing & e-commerce: salary per FTE per year | $ | — | $60,000 | $65,000 | $70,000 | $75,000 |
| Marketing & e-commerce: headcount growth per year | % | L ≤ B ≤ H | 50.0% | 30.0% | 20.0% | 10.0% |
| Marketing & e-commerce: first month on payroll | month # | — | 1 | 1 | 1 | 1 |
| Store staff: headcount (FTE) | FTE | L ≤ B ≤ H | 0 | 0 | 8 | 40 |
| Store staff: salary per FTE per year | $ | — | $0 | $0 | $38,000 | $40,000 |
| Store staff: headcount growth per year | % | L ≤ B ≤ H | 0.0% | 0.0% | 30.0% | 20.0% |
| Store staff: first month on payroll | month # | — | 1 | 1 | 1 | 1 |
| G&A (finance, admin): headcount (FTE) | FTE | L ≤ B ≤ H | 0.5 | 1 | 3 | 8 |
| G&A (finance, admin): salary per FTE per year | $ | — | $60,000 | $65,000 | $70,000 | $75,000 |
| G&A (finance, admin): headcount growth per year | % | L ≤ B ≤ H | 0.0% | 20.0% | 15.0% | 10.0% |
| G&A (finance, admin): first month on payroll | month # | — | 1 | 1 | 1 | 1 |
| Payroll taxes & benefits, % of salary | % | — | 15.0% | 15.0% | 15.0% | 15.0% |
| Wage growth per year | % | — | 3.0% | 3.0% | 3.0% | 3.0% |
| Equity raised at start | $ | — | $250,000 | $600,000 | $1,500,000 | $1,000,000 |
| Loan drawn at start | $ | — | $0 | $100,000 | $500,000 | $2,000,000 |
| Loan interest rate per year | % | — | 8.0% | 8.0% | 8.0% | 8.0% |
| Loan repayment term | years | — | 5 | 5 | 5 | 5 |
| Customer payment terms (receivable days) | days | — | 2 | 2 | 2 | 2 |
| Inventory held (days of COGS) | days | — | 75 | 75 | 75 | 75 |
| Supplier payment terms (payable days) | days | — | 30 | 30 | 30 | 30 |
| Depreciation period for capex | years | — | 7 | 7 | 7 | 7 |
| Income tax rate | % | — | 21.0% | 21.0% | 21.0% | 21.0% |

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Scenario | Net sales Y1 / Y2 / Y3 | EBITDA margin Y3 | Cash end Y3 | Inventory end Y3 |
|---|---|---|---|---|---|
| planning | Low | $112k / $130k / $151k | -253% | ($622k) | $16k |
| planning | Base | $205k / $256k / $319k | -93% | ($438k) | $32k |
| planning | High | $374k / $506k / $688k | -14% | ($29k) | $66k |
| early | Low | $562k / $651k / $755k | -76% | ($806k) | $79k |
| early | Base | $995k / $1,242k / $1,550k | -11% | $67k | $155k |
| early | High | $1,689k / $2,287k / $3,115k | 22% | $1,533k | $298k |
| growing | Low | $3,376k / $4,164k / $5,018k | -26% | ($2,528k) | $557k |
| growing | Base | $5,515k / $7,179k / $9,150k | 10% | $1,805k | $955k |
| growing | High | $8,858k / $12,317k / $16,914k | 31% | $8,691k | $1,657k |
| established | Low | $13,368k / $15,783k / $18,403k | -11% | ($7,336k) | $2,084k |
| established | Base | $20,890k / $26,321k / $32,801k | 17% | $6,792k | $3,489k |
| established | High | $31,846k / $43,270k / $58,604k | 35% | $29,917k | $5,824k |

*planning* and the Low cases run out of cash inside three years on purpose: the "Funding
sufficient" check turns to WARN and the Dashboard shows the lowest cash point. The Low and High
cases move several drivers together (conversion, AOV, CAC, returns, product cost, fulfilment,
repeat rate), so they are deliberately wide.

## Simplifications to review

1. Repeat purchases are a fixed multiplier on new-customer orders, with no cohort lag.
2. New stores open fully productive on day one (no sales ramp, no pre-opening costs).
3. One blended product-cost %; no category mix, markdowns or shrinkage.
4. Inventory is days of product cost (no seasonal stock build ahead of Q4).
5. Store staff is a headcount role, not tied to the number of stores automatically.
6. Paid CAC is flat as the budget grows (no channel saturation).

## Questions for the CFO review

- Are the stage defaults sensible starting points (conversion, AOV, CAC, repeat, returns,
  product cost, inventory days, store productivity)?
- Should fulfilment and payment fees sit in cost of goods sold instead of operating costs?
- Should inventory build ahead of Q4 (seasonal stock) be modelled?
- Should store staff scale with the number of stores automatically?
