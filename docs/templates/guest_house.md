# Guest house / bed and breakfast template — assumption memo

Template key `guest_house` (`engine/templates/guest_house.py`). Samples: `samples/guest_house-full.xlsx` (stage *planning*: a
purchased house converted to 10 lettable rooms, Full tier, monthly, 3 years) and `samples/guest_house-full-5y.xlsx` (same,
5 years); rebuild with `python scripts/build_samples.py guest_house`.

Status: **awaiting CFO review (HUMAN_TODO R1)**. **No default below has a citable external source: every figure is an
assumption** chosen to give a plausible small owner-run guest house; the customer replaces all of them. They are not market
benchmarks; check them against the property's own booking and cost records before relying on a result.

For a single property that sells rooms by the night with breakfast (no restaurant, events or spa; see Simplifications).

## How the model works

**Rooms and occupancy.** Available room-nights = lettable rooms × calendar nights per month. Occupancy = occupancy at maturity
× (1 + occupancy growth)^(year-1) × opening ramp × season, **capped at 100 %**. Occupied room-nights = available × occupancy.
The ramp rises in a straight line from *occupancy in month 1* to 100 % of maturity over *months to reach mature occupancy*
(0 = already mature); an annual model uses the mean of the months in the year. The season (monthly models only) raises June,
July and August by the *peak-season uplift* and lowers the other nine months by one third of it, so the year's average is
unchanged; annual models use 1. A monthly model that ramps up through a summer differs slightly from the annual model for the
same year (annual models see only the mean ramp); with no ramp, or no uplift, they agree exactly while no cap binds.

**Revenue.** Room revenue = occupied room-nights × average daily rate (ADR). Breakfast & extras revenue = occupied room-nights ×
a spend per night. Both rise once a year with the rate increase.

**Stays and cleaning.** Stays = occupied room-nights ÷ average length of stay (0 if the length is 0). Cleaning and linen is a cost
per stay (turnover work scales with arrivals, not with nights), so longer stays lower it.

**Cost of sales.** Housekeeping payroll (Headcount sheet, with payroll taxes and wage growth); OTA / booking commission = room
revenue × OTA share × commission rate; breakfast & extras cost (% of that revenue); cleaning & linen per stay; guest supplies per
occupied room-night. Per-stay and per-night costs grow with the cost increase per year.

**Operating expenses.** Host / manager / front desk and kitchen & maintenance payroll (Headcount), building rent (0 if owned, own
escalator), property tax, insurance, utilities, repairs & maintenance (% of revenue), marketing (a yearly growth rate;
opening-heavy budgets use a negative one), other G&A, card processing fees on all revenue.

**Capex and funding.** In month 1: an optional property purchase (the land share is carried at cost and never depreciated,
ADR-011), room furnishing and bathroom fit-out (cost per room × rooms), building works / kitchen / signage. Every period: an FF&E
replacement reserve (per room per year, growing with costs). One blended depreciation life. Equity at the start and an optional
property loan, repaid as an **annuity** (level monthly payment, interest on the opening balance; `loan_style = "annuity"`).

## Drivers (Base value of the sample = stage *planning*)

**Rooms & occupancy**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Lettable rooms | 10 | rooms | assumption |
| Average occupancy at maturity (year 1) | 62% | % | assumption (annual average across the season) |
| Occupancy growth per year (capped at 100%) | 2% | % | assumption |
| Months to reach mature occupancy (0 = already mature) | 10 | months | assumption (a new property needs a season of reviews) |
| Occupancy in month 1, % of mature | 40% | % | assumption |
| Peak-season uplift, June-August (monthly models) | 25% | % | assumption (replace with the booking calendar) |
| Calendar nights per month | 30.4 | nights | 365 ÷ 12 |
| Average length of stay | 2.2 | nights | assumption |

**Rates & extras**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Average daily rate per occupied room (year 1) | $155 | $ | assumption (blend of room types and seasons; not a posted rate) |
| Rate increase per year (rooms and extras) | 3% | % | assumption |
| Breakfast & extras revenue per occupied room-night (year 1) | $12 | $ | assumption (breakfast charged separately, extra beds, drinks) |

**Cost of sales**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Breakfast & extras cost, % of that revenue | 50% | % | assumption |
| Cleaning & linen per stay (year 1) | $22 | $ | assumption (laundry service, consumables; in-house labour is in Housekeeping payroll) |
| Guest supplies per occupied room-night (year 1) | $4.00 | $ | assumption (toiletries, coffee, water) |
| Share of room revenue booked through OTAs | 55% | % | assumption |
| OTA / booking commission, % of OTA room revenue | 15% | % | assumption (check the platform's current contract) |

**Property costs**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Building rent per month (0 = owned property) | $0 | $ | assumption (0 in the sample: owned) |
| Rent increase per year | 3% | % | assumption |
| Property tax per year (0 if leased or included in rent) | $8,000 | $ | assumption (about 1.1 % of the purchase price; use the tax bill) |
| Insurance (property, liability) per month | $700 | $ | assumption |
| Utilities per month | $1,800 | $ | assumption |
| Repairs & maintenance, % of revenue | 4% | % | assumption |
| Software, accounting & other G&A per month | $1,200 | $ | assumption |
| Marketing budget per month (year 1) | $1,500 | $ | assumption (opening-heavy, falls in year 2) |
| Marketing budget growth per year | -20% | % | assumption |
| Card processing fees, % of revenue | 2.7% | % | assumption |
| Cost increase per year (insurance, utilities, supplies, cleaning, tax) | 3% | % | assumption |

**Capital spending**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Property purchase (month 1; 0 = leased building) | $720,000 | $ | assumption |
| Land share of the property purchase (never depreciated) | 25% | % | assumption (use the appraisal or tax-assessment split) |
| Furnishing & bathroom fit-out per room (month 1) | $7,500 | $ | assumption |
| Building works, kitchen, signage & systems (month 1) | $70,000 | $ | assumption |
| FF&E replacement per room per year | $900 | $ | assumption (mattresses, linen stock, soft furnishings) |

**Headcount**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Housekeeping staff: headcount (FTE) / salary | 1.5 / $32,000 | FTE / $ | assumption |
| Host, manager & front desk: headcount (FTE) / salary | 1 / $40,000 | FTE / $ | assumption (include owner compensation here if the owner works on site) |
| Breakfast kitchen & maintenance: headcount (FTE) / salary | 0.6 / $30,000 | FTE / $ | assumption |
| Headcount growth per year; first month on payroll (every role) | 0%; month 1 | % / month # | assumption |
| Payroll taxes & benefits, % of salary | 15% | % | assumption |
| Wage growth per year | 3% | % | assumption |

**Funding**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Equity raised at start | $430,000 | $ | assumption (sized so the Base case stays funded) |
| Loan drawn at start | $500,000 | $ | assumption (property loan; set 0 for none) |
| Loan interest rate per year | 7% | % | assumption |
| Loan repayment term | 25 | years | assumption (annuity: level payment) |

**Working capital**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Customer payment terms (receivable days) | 3 | days | assumption (card and OTA payouts arrive within days) |
| Inventory held (days of cost of sales) | 3 | days | assumption: applies to all cost of sales, including payroll, so it is a small stock of food and linen |
| Supplier payment terms (payable days) | 25 | days | assumption |

**Tax & depreciation**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Depreciation period for capex | 15 | years | assumption, blended building, fit-out and furnishings |
| Income tax rate | 21% | % | assumption (US federal corporate rate; state tax not modelled) |

Low / High values for every driver are in the template; the Low case stacks every pessimistic value (slower ramp, lower
occupancy, rate and extras, higher costs and OTA dependence), so it is a stress case.

## Guest house metrics table (Dashboard in Full, P&L sheet in Light)

Available and occupied room-nights, occupancy, guest stays, revenue split (rooms / breakfast & extras), extras share, ADR
(room revenue ÷ occupied room-nights), RevPAR (room revenue ÷ available room-nights), total revenue per available room-night,
revenue per stay, gross margin and EBITDA margin. Every line item is recomputed by the independent challenger.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Case | Revenue Y1 | Revenue Y3 | EBITDA margin Y1 → Y3 | Occupancy Y3 | Lowest month-end cash (36 months) |
|---|---|---:|---:|---|---:|---:|
| planning | Low | $151,574 | $267,935 | -62% → -10% | 50% | ($230,147) |
| planning | Base | $274,944 | $416,906 | 4% → 27% | 65% | $22,904 |
| planning | High | $386,298 | $542,083 | 29% → 42% | 74% | $54,906 |
| early | Low | $234,080 | $267,935 | -47% → -40% | 50% | ($238,068) |
| early | Base | $356,074 | $416,906 | -2% → 6% | 65% | $79,435 |
| early | High | $457,981 | $542,083 | 20% → 26% | 74% | $103,339 |
| growing | Low | $365,617 | $372,966 | -8% → -13% | 58% | ($48,573) |
| growing | Base | $497,120 | $548,702 | 20% → 22% | 71% | $149,002 |
| growing | High | $599,293 | $687,671 | 34% → 38% | 79% | $154,253 |
| established | Low | $471,803 | $481,286 | 0% → -5% | 62% | ($39,506) |
| established | Base | $632,476 | $698,102 | 25% → 27% | 75% | $39,503 |
| established | High | $756,887 | $859,485 | 38% → 41% | 82% | $45,913 |

EBITDA is before debt service. At the *planning* Base defaults the annual loan payment (about $42,000) is covered from year 2
on; the Low cases of every stage run out of cash and the Checks sheet flags the funding gap. Base cases are funded throughout.

## Simplifications to review

1. One ADR for all rooms; no room types, weekday / weekend rates, minimum stays or last-minute discounting. Occupancy is an
   average, not a booking-by-booking calendar.
2. Season: one simple peak (June-August) with the other nine months giving it back; a southern-hemisphere, ski or two-peak
   property needs its own profile. Model month 1 is treated as January for the season.
3. Demand is exogenous (occupancy %); marketing spend is a cost, not a driver of bookings. No cancellations, no-shows or
   refunds.
4. OTA mix is one share and one commission rate; direct bookings carry no cost besides card fees. Card fees apply to all
   revenue, including OTA bookings where the OTA may collect payment (see CFO question 4).
5. Staff are fixed headcounts, not tied to occupancy. The owner's own labour is not separated unless entered as the host role.
6. Breakfast & extras is a spend per occupied room-night (guests per room are not modelled); no restaurant, events, spa or
   tourist-tax pass-through (occupancy taxes collected for the government are excluded from revenue).
7. Property is a single month-1 purchase with a fixed land share; no revaluation or sale at the horizon (no Returns sheet).
8. One blended depreciation life; no state tax; FF&E replacement is a smooth reserve, not lumpy refits.
9. No pre-opening period: in the *planning* stage the purchase, the crew and the first bookings all start in month 1.

## Questions for the CFO review

1. Are rooms × occupancy × ADR the right drivers, or should room types (standard / suite) with their own rates be separate?
2. Is the summer-only seasonal shape (June-August +25 %, other months about -8 %) acceptable, or should the user enter a 12-month profile?
3. Are $155 ADR, 62 % occupancy and a 2.2-night stay fair planning defaults? (All are assumptions; none has a citable source.)
4. Should OTA commission apply to a share of room revenue (as built) or to the whole of it, and should it also cover breakfast? Card fees are charged on all revenue, OTA bookings included; should they apply only to
   direct room revenue and extras?
5. Should cleaning be per stay (as built) or per room-night, and should housekeeping staff flex with occupancy instead of being fixed?
6. Is a land share on the purchase and a 15-year blended life acceptable, or do you want building and furnishings depreciated separately?
7. Should the owned-property case add a Returns sheet (sale at the horizon, IRR) like the real-estate template?
8. Is the annuity loan (level monthly payment, rate and term as inputs) the right default for the planning stage?
9. Are working-capital days of 3 (stock) and 25 (suppliers) on total cost of sales reasonable?
10. In every stage the Low case runs out of cash (flagged on Checks). Should Low equity be sized to stay funded, or is a visible
    funding gap the right stress signal?
