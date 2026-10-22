# Pet grooming and boarding template — assumption memo

Template key `pet_care` (`engine/templates/pet_care.py`). Samples: `samples/pet_care-full.xlsx` (stage *planning*: a new
shop with 4 grooming stations and 30 kennel runs, Full tier, monthly, 3 years) and `samples/pet_care-full-5y.xlsx` (same,
5 years); rebuild with `python scripts/build_samples.py pet_care pet_care-full-5y`.

Status: **awaiting CFO review (HUMAN_TODO R1)**. **No default below has a citable external source: every figure is an
assumption** chosen to give a plausible independent grooming-and-boarding shop; the customer replaces all of them. They are
not market benchmarks; check them against the shop's own appointment and kennel records before relying on a result.

For a single-site shop that grooms dogs and boards them overnight (daycare is not a separate line; see Simplifications).

## How the model works

**Grooming demand.** Appointments per operating day at maturity (growing at the *volume growth per year*) × operating days per
month × a ramp-up factor = grooms demanded. The ramp rises in a straight line from *volume in month 1* to 100 % over *months to
reach mature volume* (0 = already mature) and applies to both grooming and boarding; an annual model uses the mean of the months
in the year. Grooming has no seasonality.

**Grooming capacity: two limits, the lower one binds.**
- *Station limit* = grooming tables / tub stations × grooms one station can turn per operating day × operating days.
- *Groomer limit* = groomer FTE (Headcount sheet) × grooms one groomer can finish per day × operating days.

Grooms completed = the lower of demand and capacity. Grooms lost to the limit and the share of capacity used are KPIs: the
signal to add a station or hire a groomer.

**Boarding.** Available run-nights = kennel runs × calendar nights per month. Occupancy = occupancy at maturity × (1 + occupancy
growth)^(year-1) × ramp × season, **capped at 100 %** (a run can only be sold once a night). Boarded run-nights = available ×
occupancy. The season (monthly models only) raises June, July, August and December by the *peak-season uplift* and lowers the
other eight months by half of it, so the year's average is unchanged; annual models use 1. Because the ramp and the season are
both monthly shapes, a monthly model that ramps up through a peak season differs slightly from the annual model for the same
year (annual models see only the mean ramp): at the defaults about 1-1.5 % of boarded nights and under 1 % of revenue in
the ramp year (planning stage), nil once the ramp ends. With no ramp, or no uplift, monthly and annual agree exactly while no cap binds.

**Revenue.** Grooming revenue = grooms × average price per groom. Boarding revenue = boarded run-nights × average nightly rate.
Retail revenue = grooms × retail sales per groom (shampoo, treats, accessories). Prices, nightly rate and retail spend rise once
a year with the price increase.

**Cost of sales.** Groomers get a small guaranteed base (Headcount sheet, with payroll taxes and wage growth) plus a commission on
grooming revenue (the commission is a flat percentage; add taxes into it if you want it loaded). Also: grooming supplies per groom,
food / cleaning / laundry per boarded night, and retail cost of goods (retail sales × (1 − retail margin)). Supply and food costs
grow with the cost increase per year.

**Operating expenses.** Kennel attendants, manager & front desk (Headcount), shop rent (own yearly escalator), insurance,
utilities / software / vet-on-call / other G&A, marketing (a yearly growth rate; opening-heavy budgets use a negative one), card
processing fees on all revenue.

**Capex and funding.** Grooming tables, tubs and dryers (cost per station × stations), kennel run build-out (cost per run × runs)
and leasehold improvements in month 1; an optional land / building purchase (carried at cost, never depreciated; 0 for a leased
shop) and a refresh amount at the start of every year from year 2. One blended depreciation life. Equity and an optional loan at the
start (equal principal payments).

## Drivers (Base value of the sample = stage *planning*)

**Grooming demand**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Grooming appointments per operating day at maturity (year 1) | 16 | grooms | assumption (a 4-station shop; replace with the booked-appointment count) |
| Grooming volume growth per year | 3% | % | assumption |
| Operating days per month | 26 | days | assumption (six days a week less holidays) |
| Months to reach mature volume (0 = already mature) | 10 | months | assumption (a new shop takes most of a year to fill its book) |
| Volume in month 1, % of mature (grooming and boarding) | 40% | % | assumption |

**Grooming capacity**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Grooming tables / tub stations | 4 | stations | assumption |
| Grooms one station can turn per operating day | 6 | grooms | assumption (small and medium dogs; large breeds take longer) |
| Grooms one groomer can finish per operating day | 5.5 | grooms | assumption (mix of full grooms and quick baths) |

**Grooming prices & retail**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Average price per groom (year 1) | $75 | $ | assumption (blend of baths, full grooms and add-ons; not a posted price) |
| Price increase per year | 3% | % | assumption (applies to grooming, boarding and retail) |
| Retail sales per groom (year 1) | $8 | $ | assumption |
| Retail gross margin | 40% | % | assumption |

**Boarding**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Kennel runs / suites | 30 | runs | assumption |
| Average boarding occupancy at maturity (year 1) | 62% | % | assumption (annual average across the season) |
| Occupancy growth per year (capped at 100%) | 3% | % | assumption |
| Peak-season uplift, June-August and December (monthly models) | 20% | % | assumption (summer travel and holidays; replace with the shop's booking calendar) |
| Calendar nights per month | 30.4 | nights | 365 ÷ 12 |
| Average nightly rate per run (year 1) | $55 | $ | assumption (standard run; no suites, add-ons or holiday surcharge) |

**Cost of sales**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Groomer commission, % of grooming revenue | 35% | % | assumption (paid on top of the small base) |
| Shampoo, blades & supplies per groom (year 1) | $4.50 | $ | assumption |
| Food, cleaning & laundry per boarded night (year 1) | $6.00 | $ | assumption (pets on house food; owner-supplied food would lower it) |

**Shop costs**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Shop rent or land cost per month | $9,000 | $ | assumption (about 3,500 sq ft; replace with the signed lease) |
| Rent increase per year | 3% | % | assumption (typical lease escalator) |
| Insurance (care, custody, liability) per month | $2,500 | $ | assumption |
| Utilities, software, vet-on-call & other G&A per month | $4,500 | $ | assumption (kennels use a lot of water, heat and laundry) |
| Marketing budget per month (year 1) | $3,500 | $ | assumption (opening-heavy, falls in year 2) |
| Marketing budget growth per year | -20% | % | assumption |
| Card processing fees, % of revenue | 3% | % | assumption (typical US card-acceptance cost) |
| Cost increase per year (insurance, utilities, supplies, food) | 3% | % | assumption |

**Capital spending**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Grooming table, tub & dryer per station (month 1) | $6,000 | $ | assumption (hydraulic table, tub, high-velocity dryer, tools) |
| Kennel run build-out per run (month 1) | $2,500 | $ | assumption (partitions, drains, doors; multiplied by the number of runs) |
| Leasehold improvements, flooring, HVAC & signage (month 1) | $90,000 | $ | assumption |
| Land or building purchase (month 1; never depreciated, 0 = leased shop) | $0 | $ | assumption (0 = leased; enter the price for an owned site) |
| Equipment & kennel refresh per year (from year 2) | $10,000 | $ | assumption |

**Headcount**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Groomers: headcount (FTE) / guaranteed base per FTE per year | 4 / $10,000 | FTE / $ | assumption (commission is on top; headcount also sets the groomer limit) |
| Kennel attendants & daycare: headcount (FTE) / salary | 3 / $33,000 | FTE / $ | assumption |
| Manager & front desk: headcount (FTE) / salary | 1 / $60,000 | FTE / $ | assumption (include owner compensation here if the owner works in the shop) |
| Headcount growth per year; first month on payroll (every role) | 0%; month 1 | % / month # | assumption |
| Payroll taxes & benefits, % of salary | 15% | % | assumption |
| Wage growth per year | 3% | % | assumption |

**Funding**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Equity raised at start | $330,000 | $ | assumption (sized so the Base case stays funded) |
| Loan drawn at start | $100,000 | $ | assumption (equipment / build-out loan; optional, set 0 for none) |
| Loan interest rate per year | 9% | % | assumption |
| Loan repayment term | 5 | years | assumption (equal principal payments) |

**Working capital**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Customer payment terms (receivable days) | 2 | days | assumption (card settlement; most services are paid at pickup) |
| Inventory held (days of cost of sales) | 6 | days | assumption: applies to all cost of sales, including payroll, so it is a small amount of retail and supplies stock |
| Supplier payment terms (payable days) | 25 | days | assumption (blended) |

**Tax & depreciation**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Depreciation period for capex | 8 | years | assumption, blended equipment and leasehold life |
| Income tax rate | 21% | % | assumption (US federal corporate rate; state tax not modelled) |

Low / High values for every driver are in the template; the Low case stacks every pessimistic value (slower ramp, fewer grooms,
lower occupancy and prices, higher costs), so it is a stress case.

## Pet care metrics table (Dashboard in Full, P&L sheet in Light)

Groomers (year end), grooms completed, grooming capacity and capacity used, grooms lost to the limit, boarded and available
run-nights, boarding occupancy, revenue split (grooming / boarding / retail), boarding share, revenue per groom, boarding revenue
per available run-night, revenue per groomer, gross margin and EBITDA margin. Every line item is recomputed by the independent
challenger.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Case | Revenue Y1 | Revenue Y3 | EBITDA margin Y1 → Y3 | Grooms Y3 | Occupancy Y3 | Capacity used Y3 | Lowest month-end cash (36 months) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| planning | Low | $331,698 | $585,276 | -73% → -15% | 4,056 | 50% | 65% | $-270,554 |
| planning | Base | $574,502 | $886,368 | -11% → 16% | 5,296 | 66% | 77% | $147,500 |
| planning | High | $832,793 | $1,226,562 | 16% → 33% | 6,661 | 79% | 89% | $220,781 |
| early | Low | $508,859 | $585,276 | -22% → -16% | 4,056 | 50% | 65% | $-212,520 |
| early | Base | $740,638 | $886,368 | 8% → 16% | 5,296 | 66% | 77% | $84,287 |
| early | High | $986,188 | $1,226,562 | 26% → 33% | 6,661 | 79% | 89% | $103,982 |
| growing | Low | $908,016 | $926,267 | -2% → -6% | 6,552 | 58% | 70% | $-28,408 |
| growing | Base | $1,219,037 | $1,372,037 | 18% → 21% | 8,606 | 72% | 84% | $173,545 |
| growing | High | $1,526,515 | $1,805,360 | 31% → 35% | 10,319 | 82% | 92% | $189,283 |
| established | Low | $983,376 | $1,003,142 | 2% → -2% | 7,176 | 62% | 77% | $74,124 |
| established | Base | $1,277,035 | $1,422,108 | 20% → 22% | 8,764 | 76% | 85% | $135,933 |
| established | High | $1,590,240 | $1,843,835 | 31% → 35% | 10,461 | 85% | 93% | $151,944 |

At the *planning* Base defaults the groomer limit (4 groomers × 5.5 = 22 grooms a day) is lower than the station limit (4 × 6 = 24), so
hiring, not buying tables, is the first constraint. The Low cases of *planning*, *early* and *growing* run out of cash and the Checks sheet
flags the funding gap; Base cases are funded throughout.

## Simplifications to review

1. One average price per groom and one grooms-per-groomer rate; no split by breed size, service type or add-ons.
2. One nightly rate for every run; no suite tiers, holiday surcharges or minimum stays. Occupancy is an average, not a booking-by-booking calendar.
3. No daycare line (day visits, training); attendants' headcount is a fixed number, not tied to occupancy.
4. Groomers: a small fixed base plus a flat commission percentage; no tips, no booth-rental model, no commission payroll tax.
5. Grooming has no seasonality; only boarding does, in monthly models, as a simple peak (June-August, December) with the other months giving it back.
6. Demand is exogenous (appointments per day); marketing spend is a cost, not a driver of volume. No cancellations / no-shows.
7. Retail is a spend per groom with one margin; no product catalogue.
8. Land is a single month-1 purchase (0 by default, a leased shop); one blended depreciation life; no state tax.
9. No pre-opening period: in the *planning* stage the capex, the crew, the rent and the first bookings all start in month 1.

## Questions for the CFO review

1. Is "appointments per day × price per groom" the right grooming driver, or should demand come from a client base (clients × visits per year)?
2. Should grooming capacity be the lower of a station limit and a groomer limit, as built, and are 6 grooms per station-day and 5.5 per groomer-day sensible defaults?
3. Are a $75 average groom, a $55 nightly rate and 62 % average occupancy fair planning defaults? (All are assumptions; none has a citable source.)
4. Is the simple seasonal shape (June-August and December +20 %, other months -10 %) acceptable, or should the user enter a 12-month profile?
5. Should groomers be commission-only (no base), as many shops pay, or keep the small base as built?
6. Should kennel attendants flex with boarded nights instead of being a fixed headcount?
7. Should daycare become its own revenue line (day visits × price) sharing the kennel space?
8. Is a blended 8-year depreciation acceptable, or do you want tables / dryers and the kennel build-out separately?
9. Are working-capital days of 6 (stock) and 25 (suppliers) on total cost of sales reasonable?
10. Should the planning stage get a pre-opening period (build-out months with capex and rent but no revenue)?
11. In the planning, early and growing stages the Low case runs out of cash (flagged on Checks). Should Low equity be sized to
    stay funded, or is a visible funding gap the right stress signal?
