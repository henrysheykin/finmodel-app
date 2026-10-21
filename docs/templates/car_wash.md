# Car wash (express tunnel) template — assumption memo

Template key `car_wash` (`engine/templates/car_wash.py`). Samples: `samples/car_wash-full.xlsx` (stage *planning*: a new
express tunnel with a 250-member presale, Full tier, monthly, 3 years) and `samples/car_wash-full-5y.xlsx` (same,
5 years); rebuild with `python scripts/build_samples.py car_wash car_wash-full-5y`.

Status: **awaiting CFO review (HUMAN_TODO R1)**. Every default below is either sourced (link in the Source column) or
marked *assumption*. The two web sources are trade/consultant articles, not audited statistics; treat them as
ranges to sanity-check against the customer's own site, not as benchmarks.

For express tunnel washes with retail customers and unlimited-plan members (not in-bay automatics, full-service or
detail shops).

## How the model works

**Retail cars.** Retail cars per operating day at maturity (growing at the *retail cars growth per year*) × operating days per month ×
a ramp-up factor × a winter factor. The ramp rises in a straight line from *volume in month 1* to 100 % over *months to reach mature volume*; an
annual model uses the average of the months in the year, so annual and monthly volumes agree exactly when there is no winter dip (with a dip during the ramp-up the two
interact, so annual is close but not exact). In monthly models model
month 1 is treated as January; December-February run below the average and the other nine months above it by a third of
the dip, so the year's volume is unchanged. Annual models carry no seasonality.

**Unlimited members.** Opening members (the presale for a new site, the current base for a trading one) + new members −
cancellations. New members come from a share of retail cars that sign up for a plan plus direct sign-ups (online, promotions;
ramped like retail volume and growing yearly). A fixed share of the opening base cancels each month. Annual models compound the
monthly cancellation rate over 12 months and assume new members join mid-year (the SaaS and fitness convention), so annual and
monthly versions agree closely but not to the dollar.

**Revenue.** Retail washes × average price per wash; add-on revenue per retail car; unlimited plan fees = average members ×
monthly fee. A member pays the fee however often they wash: **member washes drive variable cost, not revenue**. Prices (and
the plan fee) rise once a year with the price increase.

**Tunnel capacity.** Capacity per month = rated cars per hour × hours open × practical share of the rated speed × operating days.
If retail cars plus member washes demanded exceed it, both are scaled down in the same proportion: retail revenue and variable
cost fall, plan fees do not (members still pay). Washes lost to the limit are shown as a KPI: the signal to add a lane, hours or
a second site. New members are driven by retail demand (before the limit) so the roll-forward has no circular reference.

**Cost of sales.** Chemicals, water and sewer (gallons per wash × rate per 1,000 gallons), electricity, each per wash served,
growing with the cost increase, plus card processing fees on all revenue.

**Operating expenses.** Site payroll (site manager and wash attendants, with payroll taxes and wage growth), site lease or land
cost (own yearly escalator), equipment maintenance & repairs, insurance, property tax, software & other G&A, marketing
(a yearly growth rate; opening-heavy budgets use a negative one).

**Capex and funding.** Tunnel equipment, building & site works and pay stations/signage/vacuums in month 1; an optional
land purchase (carried at cost, never depreciated; 0 for a leased site) and an equipment refresh amount at the start of every
year from year 2. One blended depreciation life. Equity and an optional loan at the start
(equal principal payments). Receivable days cover card settlement; plans are billed monthly in the month used, so no deferred
revenue is modelled.

## Drivers (Base value of the sample = stage *planning*)

**Retail volume**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Retail cars per operating day at maturity (year 1) | 240 | cars | assumption (a mid-size express site; replace with the site's traffic study) |
| Retail cars growth per year | 3% | % | assumption (traffic growth and local awareness after the ramp-up; 0 = flat) |
| Operating days per month | 29 | days | assumption (daily opening less weather closures) |
| Months to reach mature retail volume (0 = already mature) | 9 | months | assumption (new sites take most of a year to mature) |
| Retail volume in month 1, % of mature | 45% | % | assumption |
| Winter volume dip, December-February (monthly models) | 15% | % | assumption (weather, December-February; the other nine months give it back so the year is unchanged) |

**Tunnel capacity**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Rated tunnel speed | 140 | cars/hour | assumption (express tunnels are rated at roughly 100-150 cars per hour; check the vendor spec) |
| Hours open per day | 11 | hours | assumption |
| Practical throughput, % of rated speed over open hours | 55% | % | assumption (queueing and the peak-hour pattern keep an average day well below the rated speed) |

**Unlimited members**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Unlimited members at start (presale or current base) | 250 | # | assumption (presale for a new site) |
| Direct sign-ups per month at maturity (year 1) | 50 | # | assumption |
| Direct sign-ups growth per year | 5% | % | assumption |
| Retail cars that sign up for an unlimited plan | 0.8% | % | assumption |
| Members who cancel per month | 4% | % | [Beancount.io car-wash bookkeeping guide](https://beancount.io/blog/2026/05/22/car-wash-bookkeeping-unlimited-wash-club-membership-deferred-revenue-asc-606-cost-per-car-water-power-chemicals-tunnel-equipment-15-year-macrs-cost-segregation-bonus-depreciation-churn-rate-guide): below 3% a month is healthy, above 5% concerning; Base 4% is an assumption inside that range |
| Washes per member per month | 3.5 | washes | [Beancount.io car-wash bookkeeping guide](https://beancount.io/blog/2026/05/22/car-wash-bookkeeping-unlimited-wash-club-membership-deferred-revenue-asc-606-cost-per-car-water-power-chemicals-tunnel-equipment-15-year-macrs-cost-segregation-bonus-depreciation-churn-rate-guide): average members wash 3-5 times a month |

**Prices**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Average price per retail wash (year 1) | $13 | $ | assumption (single washes are quoted at $15-25 in the [Beancount.io car-wash bookkeeping guide](https://beancount.io/blog/2026/05/22/car-wash-bookkeeping-unlimited-wash-club-membership-deferred-revenue-asc-606-cost-per-car-water-power-chemicals-tunnel-equipment-15-year-macrs-cost-segregation-bonus-depreciation-churn-rate-guide); Base is a blended average after tiers and discounts) |
| Add-on revenue per retail car (wax, ceramic, tire shine) | $1.50 | $ | assumption |
| Unlimited plan fee per member per month (year 1) | $35 | $ | [Beancount.io car-wash bookkeeping guide](https://beancount.io/blog/2026/05/22/car-wash-bookkeeping-unlimited-wash-club-membership-deferred-revenue-asc-606-cost-per-car-water-power-chemicals-tunnel-equipment-15-year-macrs-cost-segregation-bonus-depreciation-churn-rate-guide): unlimited plans about $35-45 a month |
| Price increase per year | 2% | % | assumption |

**Variable cost per wash**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Chemicals per wash | $0.85 | $ | [Beancount.io car-wash bookkeeping guide](https://beancount.io/blog/2026/05/22/car-wash-bookkeeping-unlimited-wash-club-membership-deferred-revenue-asc-606-cost-per-car-water-power-chemicals-tunnel-equipment-15-year-macrs-cost-segregation-bonus-depreciation-churn-rate-guide): express chemicals $0.50-1.25 per car |
| Fresh water per wash (after reclaim) | 40 | gallons | [Beancount.io car-wash bookkeeping guide](https://beancount.io/blog/2026/05/22/car-wash-bookkeeping-unlimited-wash-club-membership-deferred-revenue-asc-606-cost-per-car-water-power-chemicals-tunnel-equipment-15-year-macrs-cost-segregation-bonus-depreciation-churn-rate-guide): 90-200 litres (about 24-53 gallons) per car; Base 40 gallons assumes a reclaim system |
| Water and sewer rate per 1,000 gallons | $9 | $ | assumption (the guide's $4 per 1,000 gallons example is water only; Base adds sewer) |
| Electricity per wash | $0.42 | $ | [Beancount.io car-wash bookkeeping guide](https://beancount.io/blog/2026/05/22/car-wash-bookkeeping-unlimited-wash-club-membership-deferred-revenue-asc-606-cost-per-car-water-power-chemicals-tunnel-equipment-15-year-macrs-cost-segregation-bonus-depreciation-churn-rate-guide): electricity $0.40-0.45 per car |
| Card processing fees, % of revenue | 3% | % | assumption (typical US card-acceptance cost) |
| Cost increase per year (per-wash costs, maintenance, other) | 3% | % | assumption |

**Site costs**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Site lease or land cost per month | $30,000 | $ | assumption (ground lease or rent for a 1-2 acre site; replace with the signed terms) |
| Lease increase per year | 3% | % | assumption (typical annual lease escalator) |
| Equipment maintenance & repairs per month | $5,500 | $ | assumption |
| Insurance, property tax, software & other G&A per month | $9,500 | $ | assumption |
| Marketing budget per month (year 1) | $12,000 | $ | assumption (grand-opening heavy, falls in year 2) |
| Marketing budget growth per year | -20% | % | assumption |

**Capital spending**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Tunnel equipment (month 1) | $1,650,000 | $ | [MMCG Invest tunnel build example](https://www.mmcginvest.com/post/tunnel-car-wash-construction-cost-breakdown-and-why-a-feasibility-study-is-essential): equipment and systems $1,651,000 |
| Building & site works (month 1) | $2,300,000 | $ | assumption; the [MMCG Invest tunnel build example](https://www.mmcginvest.com/post/tunnel-car-wash-construction-cost-breakdown-and-why-a-feasibility-study-is-essential) shows $3.2M hard cost including site work for a larger site, the [Beancount.io car-wash bookkeeping guide](https://beancount.io/blog/2026/05/22/car-wash-bookkeeping-unlimited-wash-club-membership-deferred-revenue-asc-606-cost-per-car-water-power-chemicals-tunnel-equipment-15-year-macrs-cost-segregation-bonus-depreciation-churn-rate-guide) puts a new tunnel project at $3-7M including land |
| Pay stations, signage & vacuums (month 1) | $150,000 | $ | assumption |
| Land purchase (month 1; never depreciated, 0 = leased site) | $0 | $ | assumption (0 = leased site; enter the purchase price for an owned site: carried at cost, never depreciated) |
| Equipment refresh & upgrades per year (from year 2) | $40,000 | $ | assumption |

**Headcount**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Site manager: headcount (FTE) | 1 | FTE | assumption |
| Site manager: salary per FTE per year | $72,000 | $ | assumption |
| Site manager: headcount growth per year | 0% | % | assumption |
| Site manager: first month on payroll | 1 | month # | assumption |
| Wash attendants & customer service: headcount (FTE) | 10 | FTE | assumption |
| Wash attendants & customer service: salary per FTE per year | $32,000 | $ | assumption |
| Wash attendants & customer service: headcount growth per year | 0% | % | assumption |
| Wash attendants & customer service: first month on payroll | 1 | month # | assumption |
| Payroll taxes & benefits, % of salary | 12% | % | assumption |
| Wage growth per year | 3% | % | assumption |

**Funding**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Equity raised at start | $2,100,000 | $ | assumption (sized so the Base case stays funded) |
| Loan drawn at start | $3,000,000 | $ | assumption (equipment / project loan; optional, set 0 for none) |
| Loan interest rate per year | 8.5% | % | assumption |
| Loan repayment term | 10 | years | assumption (equal principal payments) |

**Working capital**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Customer payment terms (receivable days) | 2 | days | assumption (card settlement) |
| Inventory held (days of COGS) | 7 | days | assumption: the days apply to all cost of sales (also water, power and card fees, which are not stocked), so 7 days on the total is roughly 2-3 weeks of chemical stock |
| Supplier payment terms (payable days) | 20 | days | assumption: chemical suppliers on about 30-day terms, utilities and card fees paid within days; blended 20 days on cost of sales |

**Tax & depreciation**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Depreciation period for capex | 12 | years | assumption, blended; the [Beancount.io car-wash bookkeeping guide](https://beancount.io/blog/2026/05/22/car-wash-bookkeeping-unlimited-wash-club-membership-deferred-revenue-asc-606-cost-per-car-water-power-chemicals-tunnel-equipment-15-year-macrs-cost-segregation-bonus-depreciation-churn-rate-guide) gives 5-7 year MACRS for equipment and 15-year for the tunnel structure and site improvements |
| Income tax rate | 21% | % | assumption (US federal corporate rate; state tax not modelled) |

Low / High values for every driver are in the template (`engine/templates/car_wash.py`); the Low case stacks every pessimistic value
(slower ramp, more cancellations, lower prices, higher unit costs), so it is a stress case.

## Car wash metrics table (Dashboard in Full, P&L sheet in Light)

Members (year end), new members, cancellations, washes (retail and member), member share of washes, washes per operating day,
tunnel capacity and capacity used, washes lost to the capacity limit, revenue split (plan fees vs retail), revenue per wash, plan fee
revenue per member wash, chemicals/water/electricity per wash, gross margin and EBITDA margin. Every line item is recomputed by the
independent challenger.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Case | Revenue Y1 | Revenue Y3 | EBITDA margin Y1 → Y3 | Members Y3 | Washes per day Y3 | Lowest month-end cash (36 months) |
|---|---|---:|---:|---:|---:|---:|---:|
| planning | Low | $723,754 | $1,373,353 | -74% → -2% | 1,222 | 346 | $-1,288,612 |
| planning | Base | $1,180,182 | $2,170,292 | -10% → 31% | 2,125 | 485 | $179,017 |
| planning | High | $1,713,972 | $3,275,561 | 22% → 52% | 3,372 | 644 | $777,911 |
| early | Low | $1,256,806 | $1,520,633 | -6% → 6% | 1,417 | 390 | $86,963 |
| early | Base | $1,783,692 | $2,389,063 | 23% → 36% | 2,428 | 541 | $219,257 |
| early | High | $2,385,900 | $3,587,019 | 41% → 55% | 3,807 | 711 | $252,103 |
| growing | Low | $1,601,853 | $1,668,956 | 6% → 3% | 1,642 | 433 | $194,072 |
| growing | Base | $2,161,939 | $2,603,394 | 29% → 35% | 2,754 | 595 | $444,377 |
| growing | High | $2,813,541 | $3,842,676 | 45% → 54% | 4,233 | 767 | $478,731 |
| established | Low | $1,869,706 | $1,776,472 | 10% → 1% | 1,868 | 469 | $108,737 |
| established | Base | $2,505,027 | $2,730,994 | 31% → 33% | 3,040 | 633 | $142,174 |
| established | High | $3,241,131 | $4,021,754 | 47% → 52% | 4,591 | 810 | $181,528 |

Washes per day divide the year's washes by 348 operating days. Tunnel capacity at the defaults is about 850 washes per day, so the
High case approaches it in year 3 of the mature stages. The planning Low case runs out of cash and the Checks sheet flags the
funding gap; Base cases are funded throughout.

## Simplifications to review

1. One plan, one fee, one retail price; no tiers, good/better/best mix, fleet or corporate accounts, gift cards or free-wash promotions.
2. Members wash a constant number of times a month; no first-month discount, no failed-payment or freeze losses, no plan upgrades.
3. New members come from retail-to-plan conversion and direct sign-ups; marketing spend is a cost, not a driver of volume.
4. Seasonality is a winter dip only; rain days are inside the average and no weather shock is modelled. Model month 1 = January.
5. Labor is a fixed crew (FTE), not a function of washes; no hourly flexing.
6. Land is a single month-1 purchase (0 by default, a leased site); no sale-and-leaseback, no phased purchase.
7. One blended depreciation life; no bonus depreciation or cost segregation, no state tax.
8. Free vacuums, vending and fleet revenue are not separate revenue lines.
9. No construction or pre-opening period: in the *planning* stage the capex, the crew, the lease and the first revenue all start in month 1.
10. Retail volume grows at one rate per year after the ramp-up; no step changes (a competitor opening, road works).

## Questions for the CFO review

1. Are a 4 % monthly cancellation rate (Base), 3.5 washes per member and a $35 plan fee sensible defaults? The source article gives
   under 3 % as healthy and over 5 % as concerning.
2. Is a retail-to-plan conversion of 0.8 % of retail cars per month plus direct sign-ups the right way to grow the base, or should
   new members follow marketing spend (spend ÷ cost per sign-up) as in the fitness template?
3. Is rated speed × hours open × a practical 55 % a sensible way to cap tunnel volume?
4. Should the model split member washes into peak and off-peak, or add a member-wash cap per plan?
5. Is a site lease of $30,000 a month and $2.3 M of building and site works a fair planning default for an express tunnel on leased land?
6. Should payroll be modelled as crew hours per wash rather than fixed FTE, so labor flexes with volume?
7. Is a blended 12-year depreciation acceptable, or do you want equipment (7 years) and building (15-39 years) separately?
8. New members convert from retail cars *demanded*, not cars actually washed, so the capacity limit does not reduce sign-ups. Is that acceptable,
   or should conversion follow cars washed (it would make the roll-forward circular and needs a different construction)?
9. Should the planning stage get a pre-opening period (construction months with capex and lease but no revenue)?
10. Are working-capital days of 7 (stock) and 20 (suppliers) on total cost of sales reasonable, or should chemicals be modelled separately?
