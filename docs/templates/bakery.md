# Bakery (retail counter + wholesale) template — assumption memo

Template key `bakery` (`engine/templates/bakery.py`). Samples: `samples/bakery-full.xlsx` (stage *growing*: Full
tier, monthly, 3 years) and `samples/bakery-full-5y.xlsx` (same, 5 years); rebuild with
`python scripts/build_samples.py bakery bakery-full-5y`.

Status: **awaiting CFO review (HUMAN_TODO R1)**. All defaults are illustrative starting points for the wizard's
sample-data path, not market statistics. Source key used below: **assumption** = our own illustrative choice,
no published figure behind it; **benchmark** = a directional range from a public vendor article, linked here:
[Metrobi, "Bakery Profit Margins"](https://metrobi.com/blog/profitable-bakery/) (cost of goods sold typically
25–35% of revenue, labor close to 30% of revenue in a staffed bakery, net margin 5–10%; vendor-compiled and
self-reported, so directional only); **rule** = a statutory figure (federal corporate income tax 21%,
[IRC §11](https://www.law.cornell.edu/uscode/text/26/11)).

For a neighborhood bakery that sells over its own counter and also delivers bread and pastry to cafes, restaurants
and shops on a standing weekly order.

## How the model works

**Retail counter.** Customers per day at full traffic × average ticket × opening days. A new shop opens at a
share of full traffic and ramps linearly to full traffic over a set number of months (same ramp as the cafe
template; annual columns use the exact average of the monthly ramp). Traffic and prices then grow once a year.
Opening days = opening days per week × 52 ÷ 12 per month (so 6 days a week is 26 days a month).

**Holiday peak.** In monthly models a season factor is *added* to the ramp: customers per day = customers at full
traffic × (ramp + season factor − 1), where the season factor is 1 + uplift in November and December and
1 − uplift ÷ 5 in the other ten months. The twelve (factor − 1) terms sum to zero, so the peak moves sales between
months but leaves the year's retail sales exactly unchanged, also in the ramp-up year; annual columns equal the sum of
the months (tested for every stage, scenario and year). The peak is therefore a fixed share of *full* traffic, not of
the ramped traffic (an opening-year bakery still gets a holiday crowd), and a month cannot go below zero customers.
It applies to the retail counter only; set the uplift to 0 to switch it off.

**Wholesale.** Accounts × order value per account per week × 52 ÷ 12 per month. Accounts at full ramp are a
year-1 number that grows once a year; they follow the same opening ramp as the counter (a new bakery also needs
time to win accounts). Order values rise with the yearly price increase. Wholesale does not depend on the
counter's opening days: the bakery bakes and delivers on its own schedule.

**Cost of sales.** (1) Ingredients of the items sold, excluding waste: a separate % of retail and of wholesale sales (wholesale carries a lower price,
so a higher ingredient share). (2) Waste: the share of retail production that is baked but not sold. If a share
*w* of what is baked goes unsold, baking cost per unit sold is 1 ÷ (1 − *w*) times higher, so the model books
retail ingredient cost × *w* ÷ (1 − *w*) as waste. Revenue is not reduced: waste is a cost, not lost sales.
Wholesale is baked to order and carries no waste. (3) Packaging: % of all sales. Gross profit is after these
three lines only; payroll sits in operating expenses.

**Operating expenses.** Payroll (from the headcount roles below), rent, utilities (ovens: gas, power, water, a
fixed monthly amount), wholesale delivery (accounts × deliveries per account per week × 52 ÷ 12 × cost per
drop), equipment repairs & cleaning, marketing (% of revenue), card processing fees (% of retail sales),
insurance, licences & other G&A.

**Headcount.** Three roles from the shared headcount engine, each with FTE, salary, first month on payroll and
yearly headcount growth: *bakers & production* (early-morning shifts; their salary is the premium for the hours),
*counter staff* and *manager*. Payroll taxes & benefits and wage growth are the standard drivers.

**Capex.** Fit-out and equipment (ovens, mixers, proofers, display cases) in month 1; a yearly replacement
budget from year 2, spread evenly over the months (so monthly and annual models spend the same). Depreciated
straight line over the depreciation period.

**Working capital.** Receivable days apply to *revenue*: counter sales are paid on the spot and wholesale accounts
pay in about 30 days, so the default is wholesale share × 30 days (6 / 7 / 9 / 10 days for planning / early / growing
/ established, whose Year-3 Base wholesale shares are 20 / 24 / 32 / 35%). Inventory (a few days of flour, butter and
packaging, 3 days) and payables (18 days) apply to the whole cost of sales in the shared engine — see simplifications.

## Bakery metrics table (Dashboard in Full, P&L sheet in Light)

Opening days, retail transactions, customers per day, average ticket, wholesale accounts (year end; the annual model shows the year's average), revenue,
retail counter revenue, wholesale revenue and its share, retail revenue per opening day, waste cost and waste
as % of retail revenue, wholesale delivery cost, gross profit and margin, cost of sales, payroll, prime cost
(cost of sales + payroll, % of revenue), EBITDA and EBITDA margin. Opening days, transactions, retail and
wholesale revenue, year-end accounts, waste cost and delivery cost are recomputed by the independent
challenger. The Dashboard shows retail and wholesale revenue (stacked chart), customers per day and wholesale
accounts.

## Default drivers by stage (Low / Base / High; one value = same in all scenarios)

Source for every driver in the table: **assumption**, except where the Notes below the table say otherwise.

| Driver | Unit | Planning | Early | Growing | Established |
|---|---|---|---|---|---|
| Customers per day at full traffic | # | 205 / 220 / 235 | 245 / 260 / 275 | 300 / 320 / 340 | 420 / 440 / 460 |
| Months to reach full traffic | months | 11 / 9 / 7 | 7 / 6 / 5 | 3 / 2 / 1 | 1 |
| Opening traffic, % of full | % | 40% / 45% / 50% | 60% / 65% / 70% | 85% / 90% / 95% | 100% |
| Traffic growth per year (after year 1) | % | 1% / 3% / 5% | 1% / 3% / 5% | 1% / 3% / 5% | 1% / 3% / 5% |
| Average ticket per customer (year 1) | $ | $11.00 / $11.50 / $12.00 | same | same | same |
| Price increase per year | % | 2% / 3% / 4% | same | same | same |
| Opening days per week | days | 6 | 6 | 6 | 6 |
| Holiday uplift, Nov–Dec (monthly models) | % | 20% | 20% | 20% | 20% |
| Wholesale accounts at full ramp (year 1) | # | 5 / 6 / 7 | 7.5 / 9 / 10.5 | 13 / 16 / 19 | 22 / 26 / 30 |
| Wholesale accounts growth per year | % | 8% / 12% / 16% | same | same | same |
| Order value per account per week (year 1) | $ | $500 / $540 / $580 | same | same | same |
| Deliveries per account per week | # | 5 | 5 | 5 | 5 |
| Delivery cost per drop (driver, fuel, van) | $ | $9.50 / $9.00 / $8.50 | same | same | same |
| Ingredients of items sold, % of retail sales (excl. waste) | % | 25.5% / 24% / 22.5% | same | same | same |
| Ingredients of items sold, % of wholesale sales | % | 34.5% / 33% / 31.5% | same | same | same |
| Retail production baked but not sold (waste) | % | 11% / 9% / 7% | same | same | same |
| Packaging, % of sales | % | 3.7% / 3.5% / 3.3% | same | same | same |
| Rent per month | $ | $8,500 | $9,500 | $12,000 | $16,000 |
| Utilities per month (gas, power, water) | $ | $2,800 | $3,200 | $4,000 | $5,600 |
| Equipment repairs & cleaning per month | $ | $600 | $700 | $1,000 | $1,600 |
| Marketing, % of revenue | % | 2.2% / 2.0% / 1.8% | same | same | same |
| Card processing fees, % of retail sales | % | 2.9% / 2.8% / 2.7% | same | same | same |
| Insurance, licences & other G&A per month | $ | $1,800 | $2,000 | $2,800 | $4,200 |
| Fit-out & equipment (month 1) | $ | $240,000 | $40,000 | $90,000 | $60,000 |
| Equipment replacement per year (from year 2) | $ | $6,000 | $8,000 | $14,000 | $24,000 |
| Payroll taxes & benefits, % of salary | % | 12% | 12% | 12% | 12% |
| Wage growth per year | % | 3% | 3% | 3% | 3% |
| Equity raised at start | $ | $200,000 | $90,000 | $60,000 | $50,000 |
| Loan drawn at start | $ | $150,000 | $0 | $80,000 | $0 |
| Loan interest rate / term | % / years | 9% / 7 | none | 8.5% / 5 | none |
| Receivable days (on revenue) | days | 6 | 7 | 9 | 10 |
| Inventory / payable days (on cost of sales) | days | 3 / 18 | same | same | same |
| Depreciation period for capex | years | 7 | 7 | 7 | 7 |
| Income tax rate | % | 21% | 21% | 21% | 21% |

| Role (Base; same in all scenarios) | Planning | Early | Growing | Established |
|---|---|---|---|---|
| Bakers & production | 3 FTE × $42,000, +4%/yr | 3.5 FTE × $42,000, +4%/yr | 5 FTE × $44,000, +6%/yr | 7.5 FTE × $44,000, +3%/yr |
| Counter staff | 4.5 FTE × $30,000, +4%/yr | 5 FTE × $30,000, +4%/yr | 7 FTE × $31,000, +6%/yr | 9 FTE × $31,000, +3%/yr |
| Manager | 1 FTE × $58,000 | 1 FTE × $58,000 | 1.5 FTE × $62,000 | 2 FTE × $62,000 |

Yearly headcount growth is set close to traffic growth (3%/yr Base) in the planning and early stages; the growing
stage's 6% is a deliberate step-up for a bakery that is adding wholesale volume.

Notes on sources:

- Ingredients, packaging, waste and the resulting gross margin (66–71%): **assumption**, sized so cost of sales
  lands near the 25–35% **benchmark** range (Base about 31–32% of revenue including waste and packaging).
- Payroll: Base payroll including taxes is 48 / 37 / 36% of revenue in years 1 / 2 / 3 of the planning sample,
  37 / 33 / 33% (early), 38 / 37 / 37% (growing) and 36 / 34 / 33% (established). That is **above** the "close to
  30%" labor **benchmark** (a vendor figure that may exclude owner pay and payroll taxes), so the samples are a
  cautious, labour-heavy bakery; salary levels and FTE counts are **assumptions**, not wage data. See question 3.
- Income tax 21%: **rule** (federal only; no state tax in the sample). Payroll taxes & benefits 12% of salary:
  **assumption** (employer Social Security and Medicare alone are 7.65%; the rest stands for unemployment tax,
  workers' compensation and a small benefits allowance).
- Everything else (traffic, ticket, wholesale accounts and order values, delivery cost per drop, rent, utilities,
  capex, funding, working-capital days, depreciation): **assumption**. No published source is claimed.
- Base EBITDA margin, years 1 → 3: planning -7% → 12%, early 8% → 17%, growing 9% → 12%, established 12% → 16%.
  Part of the gap to the 5–10% net-margin **benchmark** is that EBITDA is before depreciation, interest and tax.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Case | Revenue Y1 | Revenue Y3 | Gross margin Y3 | EBITDA margin Y1 → Y3 | Wholesale share Y3 | Cash Y3 |
|---|---|---:|---:|---:|---:|---:|---:|
| planning | Low | $583,492 | $904,455 | 67% | -29% → -2% | 17% | $-208,967 |
| planning | Base | $738,335 | $1,112,644 | 69% | -7% → 12% | 20% | $171,861 |
| planning | High | $909,133 | $1,356,442 | 71% | 8% → 23% | 23% | $535,731 |
| early | Low | $897,728 | $1,129,031 | 66% | -5% → 4% | 21% | $64,116 |
| early | Base | $1,064,570 | $1,386,283 | 69% | 8% → 17% | 24% | $431,209 |
| early | High | $1,245,309 | $1,688,657 | 71% | 18% → 27% | 27% | $862,983 |
| growing | Low | $1,333,410 | $1,502,898 | 66% | -3% → -3% | 27% | $-165,923 |
| growing | Base | $1,577,472 | $1,890,163 | 68% | 9% → 12% | 32% | $399,361 |
| growing | High | $1,838,308 | $2,351,962 | 70% | 19% → 24% | 35% | $1,029,196 |
| established | Low | $2,013,440 | $2,223,953 | 66% | 2% → 3% | 31% | $34,501 |
| established | Base | $2,308,800 | $2,748,449 | 68% | 12% → 16% | 35% | $738,516 |
| established | High | $2,627,040 | $3,370,556 | 70% | 20% → 27% | 39% | $1,570,709 |

The Low case stacks every pessimistic value (fewer customers and accounts, lower ticket, higher ingredient, waste
and delivery costs), so it is a stress case rather than a forecast; the planning, growing and established Low
cases dip below zero cash (lowest balances -$209k, -$166k and -$9k), the early Low case stays barely positive
($1k), and the Checks sheet flags the funding gap. The Base case is funded in every stage (lowest cash balance
$18k planning, $110k early, $126k growing, $167k established).

## Simplifications to review

1. Inventory and payable days apply to the whole cost of sales (shared engine); defaults are small (3 / 18 days).
   Receivable days apply to revenue.
2. Payroll sits in operating expenses, not in cost of sales, so "gross margin" here is after ingredients,
   waste and packaging only. Prime cost (cost of sales + payroll) is shown in the metrics table for comparison with
   restaurant-style benchmarks.
3. One average ticket for the counter; no split between bread, pastry, cakes and coffee, and no custom-order
   deposits. Wholesale is one average weekly order per account, no minimums, returns or price tiers.
4. Wholesale accounts follow the counter's opening ramp and a flat yearly growth rate; they are not capacity-capped
   by oven hours or bakers.
5. The holiday peak is fixed to November–December and hits the counter only; wholesale and farmers-market or
   catering events have no seasonality.
6. Waste is one rate on retail ingredient cost; it is not linked to opening hours, day-old discounting or
   donations to food banks.
7. Delivery is a cost per drop; the van itself is not bought (it sits in the cost per drop, as a lease/fuel mix).
8. Utilities are a fixed monthly amount and do not scale with output; no state or local sales tax is modelled.

## Questions for the CFO review

1. Are 26 opening days a month (6 days a week), a $11.50 average ticket and 320 customers a day sensible
   starting points for a neighborhood bakery, or should the sample be a smaller shop?
2. Should the ingredient defaults (24% of retail, 33% of wholesale) and a 9% waste share be the Base, given the
   25–35% cost-of-goods range quoted by the one public source we found?
3. Should baker payroll be moved into cost of sales (as in many bakery P&Ls) instead of operating expenses, so
   gross margin is comparable with the benchmarks that include labor? And should the default staffing be leaner:
   Base payroll is 33-38% of revenue from year 2, above the roughly 30% benchmark?
4. Is a flat $9 per drop and 5 deliveries a week per account the right way to model delivery, or should it be
   a van (lease + driver FTE) with a capacity limit?
5. Should wholesale accounts have their own ramp and churn, instead of sharing the counter's opening ramp?
6. Is a 20% November–December counter uplift the right default, or should seasonality default to 0 with opt-in?
7. Is a 7-year straight-line life right for ovens, mixers and display cases, and are the yearly replacement
   budgets in the table ($6,000–$24,000) enough?
