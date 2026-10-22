# Food truck template — assumption memo

Template key `food_truck` (`engine/templates/food_truck.py`). Samples: `samples/food_truck-full.xlsx` (stage *planning*: one
new truck bought and built out in month 1, Full tier, monthly, 3 years) and `samples/food_truck-full-5y.xlsx` (same,
5 years); rebuild with `python -m scripts.build_samples food_truck food_truck-full-5y`.

Status: **awaiting CFO review (HUMAN_TODO R1)**. Every default below is marked *assumption*. The author could not open
any external source during the build (the page-fetch tool was rate limited), so no figure is attributed to a source it was
not checked against. A web search for food-truck startup costs, commissary rents and tickets returned these pages, which
are worth checking against the defaults before the CFO signs off (no figure in this memo is quoted from them):
[Toast, food truck monthly expenses](https://pos.toasttab.com/blog/on-the-line/food-truck-monthly-expenses),
[Restroworks, food truck cost guide](https://www.restroworks.com/blog/how-much-does-a-food-truck-cost-to-operate/),
[ProjectionHub, food truck income](https://projectionhub.com/post/how-much-money-can-my-food-truck-make),
[WebstaurantStore, commissary kitchens](https://www.webstaurantstore.com/article/259/commissary-kitchens.html).

For one or a few trucks selling at street spots, markets and events, with optional catering (not a brick-and-mortar
restaurant with a food-truck side line, and not a franchise).

## How the model works

**Fleet and service days.** Trucks in operation (start count plus trucks added each year) × street service days per truck per
month. In monthly models model month 1 is January: December-February run below the average by the *winter dip*, the other nine
months above it by a third of the dip, so the year's street days are unchanged. Annual models carry no seasonality. Events and
catering carry no season (private bookings and festivals fill the winter gap).

**Ramp-up.** A new truck needs time to build a following. Meals per street day and event bookings rise in a straight line from
*volume in month 1* to 100 % over *months to reach mature volume*; the truck still goes out every scheduled day. An annual model uses
the average of the months in the year.

**Street sales** = street service days × meals per street day (growing each year) × average ticket (rising with the price increase).

**Events and catering** = event days per truck per month (growing each year, on the ramp) × revenue per event (rising with the price
increase). Meals served per event day drive packaging only; revenue per event is its own input (catering is quoted per job, not per
plate).

**Cost of sales.** Food cost as a percentage of all sales; packaging per meal (street and event meals, with the cost increase);
card and POS fees as a percentage of revenue; event and festival fees = a percentage of event revenue plus a booth fee per event day.

**Operating expenses.** Payroll (owner-operator, cooks, cashiers, with payroll taxes and wage growth); commissary kitchen, permits and
licences, insurance and truck maintenance, each *per truck per month*; fuel, propane and generator *per service day* (street and event
days); POS and ordering software; marketing; accounting, bank fees and other G&A. Fixed costs rise with the cost increase.

**Capex and funding.** Month 1: trucks to buy × (truck purchase + build-out) plus POS hardware and smallwares. From year 2: trucks added
× (purchase + build-out) and a yearly equipment refresh per truck. A truck already owned (stages early to established) is not bought
again (*trucks to buy in month 1* = 0). One blended depreciation life. Equity and an optional equipment / vehicle loan at the start
(the standard equal-principal loan).

**Working capital.** Receivables are card settlement plus a few invoiced catering jobs. Inventory and payables are taken on **total**
cost of sales by the engine; food and packaging are about 88 % of it (the rest is card and event fees, which are not stocked), so 3 days
of cost of sales is roughly 3-4 days of perishable food and dry goods. Suppliers are paid weekly.

**People.** Headcount is entered as roles and does not move with the truck count by itself. If you add trucks (*trucks added each
year*), raise the cook and cashier headcount growth to match. The stage defaults are consistent: about 1.2 cook and 1.0 cashier FTE
per truck, plus the owner.

## Drivers (Base value of the sample = stage *planning*)

**Fleet & service days**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Food trucks in operation at start | 1 | # | assumption |
| Trucks added each year (from year 2) | 0 | # | assumption (a growth lever; 0 in every stage) |
| Street service days per truck per month (year average) | 18 | days | assumption (about four and a half days a week; the rest is prep, shopping, maintenance and events) |
| Winter dip in street service days, December-February | 25% | % | assumption (weather; the other nine months give it back so the year is unchanged) |

**Ramp-up**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Months to reach mature volume | 6 | months | assumption |
| Volume in month 1, % of mature | 50% | % | assumption |

**Street sales**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Meals per street service day at maturity (year 1) | 88 | meals | assumption (about 10 meals an hour over a 9-hour service) |
| Meals per day growth per year | 3% | % | assumption |
| Average ticket per meal (year 1) | $14.00 | $ | assumption (one entree plus a drink or side, before tax and tips) |
| Price increase per year | 3% | % | assumption |

**Events & catering**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Event and catering days per truck per month (year 1) | 3 | days | assumption |
| Event days growth per year | 5% | % | assumption |
| Revenue per event or catering day (year 1) | $1,400 | $ | assumption (about 100 meals at the street ticket; private catering and festival days vary widely) |
| Meals served per event or catering day | 100 | meals | assumption |

**Cost of sales**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Food cost, % of sales | 33% | % | assumption (mid of a typical 28-35 % range for limited menus; later stages buy better) |
| Packaging & disposables per meal (year 1) | $0.45 | $ | assumption |
| Card & POS processing fees, % of revenue | 2.9% | % | assumption (typical US card-acceptance cost; some catering is paid by invoice or ACH) |
| Event & festival fees, % of event revenue | 4% | % | assumption (blended: private catering has no fee, festivals charge a share) |
| Event booth or vendor fee per event day (year 1) | $100 | $ | assumption |
| Cost increase per year (packaging, fuel, fixed costs) | 3% | % | assumption |

**Operating costs**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Commissary kitchen rent per truck per month | $950 | $ | assumption (shared commissary station; check the local rate) |
| Permits & licences per truck per month | $380 | $ | assumption ($4,560 a year: health permit, business licence, fire inspection, parking and vending permits; varies strongly by city) |
| Insurance per truck per month | $450 | $ | assumption ($5,400 a year: commercial auto, general liability, workers' compensation share) |
| Fuel, propane & generator per service day | $38 | $ | assumption |
| Truck maintenance & repairs per truck per month | $500 | $ | assumption |
| POS & ordering software per month | $120 | $ | assumption |
| Marketing budget per month (year 1) | $700 | $ | assumption (social ads, event listings, loyalty) |
| Marketing budget growth per year | 0% | % | assumption |
| Accounting, bank fees & other G&A per month | $350 | $ | assumption |

**Capital spending**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Trucks to buy and build out in month 1 | 1 | # | assumption (0 when the truck is already owned) |
| Truck purchase, each | $95,000 | $ | assumption (a used step van or trailer; new builds cost more) |
| Kitchen build-out, equipment & wrap, per truck | $40,000 | $ | assumption |
| POS hardware & smallwares (month 1) | $3,000 | $ | assumption |
| Equipment refresh per truck per year (from year 2) | $2,500 | $ | assumption |

**Headcount**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Owner-operator: headcount (FTE) | 1 | FTE | assumption |
| Owner-operator: salary per FTE per year | $36,000 | $ | assumption (optional: set 0 if the owner takes only profit; a draw below market wage understates cost) |
| Cooks: headcount (FTE) | 1.2 | FTE | assumption |
| Cooks: salary per FTE per year | $34,000 | $ | assumption |
| Cashiers & service staff: headcount (FTE) | 1 | FTE | assumption |
| Cashiers & service staff: salary per FTE per year | $29,000 | $ | assumption |
| Headcount growth per year, first month on payroll (each role) | 0%, month 1 | | assumption |
| Payroll taxes & benefits, % of salary | 12% | % | assumption |
| Wage growth per year | 3% | % | assumption |

**Funding**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Equity raised at start | $100,000 | $ | assumption (sized so the Base case never runs out of cash) |
| Loan drawn at start | $90,000 | $ | assumption (equipment / vehicle loan for the truck; set 0 for none) |
| Loan interest rate per year | 9% | % | assumption |
| Loan repayment term | 5 years | years | assumption (equal principal payments) |

**Working capital and tax**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Customer payment terms (receivable days) | 3 | days | assumption (card settlement plus a few invoiced catering jobs on about 15-day terms) |
| Inventory held (days of cost of sales) | 3 | days | assumption: the days apply to all cost of sales, of which about 88 % is food and packaging |
| Supplier payment terms (payable days) | 7 | days | assumption (weekly distributor terms; card fees are settled at once) |
| Depreciation period for capex | 7 | years | assumption, blended (vehicle and kitchen equipment) |
| Income tax rate | 21% | % | assumption (US federal corporate rate; state tax not modelled) |

Low / High values for every driver are in the template (`engine/templates/food_truck.py`). The Low case stacks every pessimistic
value (fewer days, fewer meals, lower ticket, higher food cost and fees, slower ramp), so it is a **stress case** and can run out
of cash (shown in the Checks sheet); Base is funded in every month in all four stages.

## Stage defaults

| Stage | Trucks | Street days / truck / month | Meals / street day | Ticket | Food cost | Owner / cook / cashier FTE | Funding |
|---|---:|---:|---:|---:|---:|---|---|
| planning | 1 (bought) | 18 | 88 | $14.00 | 33.0% | 1 / 1.2 / 1.0 | $100k equity + $90k loan |
| early | 1 (owned) | 19 | 90 | $14.00 | 32.5% | 1 / 1.2 / 1.0 | $35k equity |
| growing | 2 | 20 | 85 | $14.50 | 31.5% | 1 / 3.0 / 2.6 | $40k equity |
| established | 3 | 20 | 88 | $14.50 | 30.5% | 1 / 4.6 / 3.9 | $40k equity |

Costs scale with the fleet (commissary, permits, insurance, maintenance per truck; fuel per service day; payroll with the stage's
FTE). Mature stages show scale economies in food cost and in commissary and insurance per truck. Growing and established have a bit
fewer meals per day per truck than early because service days and fleet size rise.

## Food truck metrics table (Dashboard in Full, P&L sheet in Light)

Trucks (year end), service days, meals, meals per service day, revenue (street and events), events share, revenue per meal,
revenue per service day, revenue per truck, food and packaging (amount and % of revenue), payroll, prime cost (food, packaging and
payroll, % of revenue), gross margin and EBITDA margin. Every line item is recomputed by the independent challenger.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Case | Revenue Y1 | Revenue Y3 | EBITDA margin Y1 → Y3 | Meals Y3 | Lowest month-end cash (36 months) |
|---|---|---:|---:|---:|---:|---:|
| planning | Low | $181,040 | $254,228 | -39% → -16% | 18,912 | $-174,741 |
| planning | Base | $273,896 | $358,461 | -3% → 9% | 24,135 | $9,872 |
| planning | High | $370,257 | $484,865 | 17% → 26% | 29,716 | $43,192 |
| early | Low | $234,427 | $272,730 | -17% → -11% | 20,280 | $-71,954 |
| early | Base | $319,268 | $382,286 | 7% → 13% | 25,739 | $22,685 |
| early | High | $412,797 | $514,486 | 22% → 28% | 31,542 | $31,602 |
| growing | Low | $570,900 | $593,964 | -5% → -7% | 42,600 | $-87,841 |
| growing | Base | $730,800 | $828,665 | 12% → 15% | 53,869 | $34,797 |
| growing | High | $914,940 | $1,111,125 | 25% → 30% | 65,856 | $42,921 |
| established | Low | $896,652 | $932,877 | -1% → -3% | 65,952 | $-47,091 |
| established | Base | $1,141,920 | $1,295,092 | 15% → 18% | 83,095 | $35,801 |
| established | High | $1,423,764 | $1,729,809 | 28% → 33% | 101,284 | $48,469 |

Planning Base, year 1: revenue $273,896 (street $230,846, events $43,050 = 16 %), food and packaging $99,189, payroll $118,496, EBITDA
-$7,306; capex $138,000 in month 1. The planning Base case keeps only $9,872 of cash at its lowest month-end: tight, as is usual for a
new truck.

Monthly and annual versions agree to the dollar for revenue, cost of sales, payroll, capex and EBITDA when there is no winter dip
(tested for all four stages). With a dip the season and the ramp interact in year 1, so the annual version is close (within 5 %) but
not exact; from year 2 (ramp over, season neutral) the revenue is exact again. Annual balance-sheet items use period-end revenue and
differ slightly from monthly ones.

## Simplifications to review

1. One average ticket for street sales; no menu mix, daypart or location tiers, no tips or sales tax.
2. Meals per day is a demand input; there is no service-capacity limit (meals per hour × hours).
3. A truck added in year 2+ starts at mature volume (no new-truck ramp), and headcount does not follow the truck count automatically.
4. Seasonality is a winter dip in street days only; heat, rain and festival season are not modelled. Model month 1 = January.
5. Event and catering revenue is a flat amount per event day; no deposits, deferred revenue or cancellation.
6. Food cost is a flat % of sales; a rise in commodity prices is not separated from menu price increases.
7. Permits, insurance and commissary are flat per truck per month; real permits are annual lump sums and some cities cap permits.
8. One blended depreciation life; no bonus depreciation or section 179, no state or local taxes, no sales tax payable.
9. No pre-opening period: in *planning* the build-out spend, wages and first sales all start in month 1.
10. Tips, delivery-app commissions and third-party ordering fees are not modelled.

## Questions for the CFO review

1. Are 18 street days and 3 event days per truck per month (about 21 service days) a sensible Base, or should days be driven by a
   weekly schedule?
2. Is 88 meals per street day at a $14 ticket (about $1,230 a day) a fair mature Base for a single truck, and are the revenue
   ranges (about $0.27-0.36 M per truck-year) in line with what you see?
3. Should meals per day follow a capacity limit (meals per hour × service hours), as the car wash does for its tunnel?
4. Is a 33 % food cost with $0.45 packaging per meal reasonable, or should food cost be per meal rather than a percentage?
5. Is the owner-operator salary of $36,000 a good default, or should it default to 0 (owner takes profit) for the planning stage?
6. Are commissary $950, permits $380 and insurance $450 per truck per month fair planning defaults? (All are unsourced assumptions
   until checked against local rates.)
7. Should the planning stage get a pre-opening period (truck build, permits) with costs but no sales?
8. Should added trucks follow their own ramp and bring their own staff automatically?
9. Are 3 days of inventory and 7 days of supplier credit on total cost of sales acceptable, or should food and packaging be modelled
   separately from card and event fees?
10. Is a winter dip of 25 % (with the other months giving it back) a fair seasonality, or does your climate need a summer peak too?
