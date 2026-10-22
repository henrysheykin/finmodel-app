# Auto repair shop template — assumption memo

Template key `auto_repair` (`engine/templates/auto_repair.py`). Samples: `samples/auto_repair-full.xlsx` (stage *planning*:
a new 6-bay general repair shop, Full tier, monthly, 3 years) and `samples/auto_repair-full-5y.xlsx` (same, 5 years);
rebuild with `python scripts/build_samples.py auto_repair auto_repair-full-5y`.

Status: **awaiting CFO review (HUMAN_TODO R1)**. **No default below has a citable external source: every figure is an
assumption** chosen to give a plausible independent general-repair shop, and the customer replaces all of them. They are
not market benchmarks; check them against the shop's own repair-order data before relying on a result.

For independent general mechanical repair (brakes, maintenance, diagnostics), not collision/body, tire-only or dealer service.

## How the model works

**Demand.** Repair orders per operating day at maturity (growing at the *orders growth per year*) × operating days per month ×
a ramp-up factor × billed labor hours per repair order = billed hours demanded. The ramp rises in a straight line from
*volume in month 1* to 100 % over *months to reach mature volume* (0 = already mature); an annual model uses the mean of the
months in the year, so annual and monthly volumes agree exactly. No seasonality is modelled.

**Capacity: two limits, the lower one binds.**
- *Bay limit* = service bays × billed hours one bay can carry per operating day × operating days.
- *Technician limit* = technician FTE (from the Headcount sheet) × paid hours per technician per day × efficiency (billed hours
  per paid hour) × operating days.

Billed hours = the lower of demand and capacity. Hours lost to the limit and the share of capacity used are KPIs; the signal
to add a bay or hire a technician. Repair orders completed = orders demanded × the share of demand served.

**Revenue.** Labor revenue = billed hours × effective labor rate (the average realised per billed hour after discounts, not the posted
rate). Parts revenue = billed hours × parts sales per billed hour. A shop supplies fee = a share of labor revenue. Labor rate and parts
sales per hour rise once a year with the price increase.

**Cost of sales.** Technician payroll (with payroll taxes and wage growth; from the Headcount sheet), parts cost
(= parts revenue × (1 − parts margin)), shop supplies & waste disposal (share of labor revenue), and comebacks / warranty rework
(share of labor revenue: free re-work the shop absorbs).

**Operating expenses.** Advisors, manager and other payroll, shop rent (own yearly escalator), insurance, shop software /
diagnostic subscriptions / utilities / other G&A, marketing (a yearly growth rate; opening-heavy budgets use a negative one),
card processing fees on all revenue.

**Capex and funding.** Lifts and bay equipment (a cost per bay × bays), diagnostic tools and scan equipment, and leasehold
improvements in month 1; an optional land or building purchase (carried at cost, never depreciated; 0 for a leased shop) and a
tool refresh amount at the start of every year from year 2. One blended depreciation life. Equity and an optional loan at the start
(equal principal payments). Receivable days cover card settlement and fleet accounts; inventory days apply to all cost of sales
(see Working capital).

## Drivers (Base value of the sample = stage *planning*)

**Repair orders**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Repair orders per operating day at maturity (year 1) | 13.5 | orders | assumption (a 6-bay general shop; replace with the shop's repair-order count) |
| Repair orders growth per year | 3% | % | assumption |
| Billed labor hours per repair order | 2.0 | hours | assumption (mix of quick maintenance jobs and larger repairs) |
| Operating days per month | 25 | days | assumption (six days a week less holidays) |
| Months to reach mature order volume (0 = already mature) | 12 | months | assumption (a new shop takes about a year to fill its bays) |
| Order volume in month 1, % of mature | 40% | % | assumption |

**Shop capacity**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Service bays (lifts) | 6 | bays | assumption |
| Billed hours one bay can carry per operating day | 6.5 | hours | assumption (below a full day because bays wait for parts, approvals and clean-up) |
| Paid hours per technician per operating day | 8 | hours | assumption |
| Technician efficiency (billed hours per paid hour) | 88% | % | assumption (flat-rate shops can exceed 100%; check the shop's own billed ÷ clocked hours) |

**Labor prices**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Effective labor rate per billed hour (year 1) | $125 | $ | assumption (realised average, after discounts and warranty work at lower rates) |
| Price increase per year | 3% | % | assumption |
| Shop supplies fee, % of labor revenue | 5% | % | assumption (some states cap or restrict this fee; confirm local rules) |

**Parts & supplies**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Parts sales per billed labor hour (year 1) | $100 | $ | assumption |
| Parts gross margin, % of parts sales | 47% | % | assumption (matrix pricing: lower markup on expensive parts, higher on cheap ones) |

**Cost of sales**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Shop supplies & waste disposal cost, % of labor revenue | 3.5% | % | assumption |
| Comebacks & warranty rework, % of labor revenue | 3% | % | assumption |
| Card processing fees, % of revenue | 3% | % | assumption (typical US card-acceptance cost) |
| Cost increase per year (insurance, software & other) | 3% | % | assumption |

**Shop costs**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Shop rent or land cost per month | $18,000 | $ | assumption (about 5,000 sq ft of light-industrial space; replace with the signed lease) |
| Rent increase per year | 3% | % | assumption (typical lease escalator) |
| Insurance (garage liability, property) per month | $4,500 | $ | assumption |
| Shop software, diagnostic subscriptions, utilities & other G&A per month | $9,000 | $ | assumption |
| Marketing budget per month (year 1) | $7,000 | $ | assumption (opening-heavy, falls in year 2) |
| Marketing budget growth per year | -20% | % | assumption |

**Capital spending**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Lift & bay equipment per bay (month 1) | $22,000 | $ | assumption (lift, air, tooling per bay; multiplied by the number of bays) |
| Diagnostic tools & scan equipment (month 1) | $70,000 | $ | assumption (scan tools, alignment rack, brake and AC machines) |
| Leasehold improvements & signage (month 1) | $180,000 | $ | assumption |
| Land or building purchase (month 1; never depreciated, 0 = leased shop) | $0 | $ | assumption (0 = leased; enter the price for an owned site) |
| Equipment & tool refresh per year (from year 2) | $20,000 | $ | assumption |

**Headcount**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Technicians: headcount (FTE) / salary per FTE per year | 5 / $78,000 | FTE / $ | assumption (also sets the technician limit on capacity) |
| Service advisors & front desk: headcount (FTE) / salary | 2 / $50,000 | FTE / $ | assumption |
| Shop manager: headcount (FTE) / salary | 1 / $85,000 | FTE / $ | assumption (include owner compensation here if the owner works in the shop) |
| Headcount growth per year; first month on payroll (every role) | 0%; month 1 | % / month # | assumption |
| Payroll taxes & benefits, % of salary | 15% | % | assumption |
| Wage growth per year | 3% | % | assumption |

**Funding**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Equity raised at start | $480,000 | $ | assumption (sized so the Base case stays funded) |
| Loan drawn at start | $250,000 | $ | assumption (equipment loan; optional, set 0 for none) |
| Loan interest rate per year | 9% | % | assumption |
| Loan repayment term | 7 | years | assumption (equal principal payments) |

**Working capital**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Customer payment terms (receivable days) | 3 | days | assumption (card settlement; fleet accounts would need more) |
| Inventory held (days of cost of sales) | 8 | days | assumption: the days apply to all cost of sales, including technician payroll, which is not stocked, so 8 days on the total is roughly 3-4 weeks of parts stock |
| Supplier payment terms (payable days) | 25 | days | assumption (parts suppliers on about 30-day terms; blended) |

**Tax & depreciation**

| Driver | Base (sample) | Unit | Source |
|---|---:|---|---|
| Depreciation period for capex | 8 | years | assumption, blended equipment and leasehold life |
| Income tax rate | 21% | % | assumption (US federal corporate rate; state tax not modelled) |

Low / High values for every driver are in the template (`engine/templates/auto_repair.py`); the Low case stacks every pessimistic value
(slower ramp, fewer orders, lower rate and efficiency, thinner parts margin, higher costs), so it is a stress case.

## Auto repair metrics table (Dashboard in Full, P&L sheet in Light)

Technicians (year end), repair orders, billed hours, billed-hour capacity and capacity used, bay capacity used, hours lost to the limit,
revenue split (labor vs parts), parts share, revenue per repair order, revenue per billed hour, revenue per technician, parts gross
margin, gross margin and EBITDA margin. Every line item is recomputed by the independent challenger.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Case | Revenue Y1 | Revenue Y3 | EBITDA margin Y1 → Y3 | Repair orders Y3 | Capacity used Y3 | Lowest month-end cash (36 months) |
|---|---|---:|---:|---:|---:|---:|---:|
| planning | Low | $766,148 | $1,445,637 | -78% → -12% | 3,300 | 67% | $-784,670 |
| planning | Base | $1,264,359 | $2,108,219 | -18% → 16% | 4,297 | 81% | $83,558 |
| planning | High | $1,874,160 | $2,877,019 | 12% → 32% | 5,393 | 95% | $316,876 |
| early | Low | $1,251,818 | $1,445,637 | -19% → -12% | 3,300 | 67% | $-500,372 |
| early | Base | $1,756,055 | $2,108,219 | 8% → 15% | 4,297 | 81% | $91,467 |
| early | High | $2,288,448 | $2,877,019 | 24% → 32% | 5,393 | 95% | $130,605 |
| growing | Low | $1,803,648 | $1,839,901 | -9% → -13% | 4,200 | 61% | $-510,979 |
| growing | Base | $2,497,500 | $2,810,958 | 14% → 18% | 5,729 | 78% | $310,414 |
| growing | High | $3,255,120 | $3,881,613 | 29% → 34% | 7,277 | 91% | $350,146 |
| established | Low | $2,061,312 | $2,102,744 | -7% → -11% | 4,800 | 67% | $-456,564 |
| established | Base | $2,775,000 | $3,062,935 | 14% → 17% | 6,242 | 80% | $218,617 |
| established | High | $3,403,080 | $3,981,122 | 27% → 31% | 7,463 | 89% | $251,857 |

At the *planning* Base defaults the technician limit (5 technicians × 8 h × 88 % = 35 billed hours a day) is lower than the bay limit
(6 bays × 6.5 h = 39), so hiring, not building, is the first constraint. The Low cases run out of cash and the Checks sheet flags the
funding gap; Base cases are funded throughout.

## Simplifications to review

1. One labor rate, one hours-per-order and one parts sales ratio for the whole shop; no split between maintenance, diagnostics and
   heavy repair, and no tire, alignment or inspection lines.
2. Parts sales per billed hour is a fixed ratio; parts are not tracked as a price × quantity or by supplier.
3. Technicians are paid a fixed salary (FTE), not a flat-rate share of billed hours; there is no overtime or bonus.
4. Demand is exogenous (repair orders per day); marketing spend is a cost, not a driver of volume, and there is no seasonality.
5. Comebacks and shop supplies are percentages of labor revenue; no separate cost for recalls or customer goodwill.
6. No fleet / commercial accounts with different rates or long payment terms; no towing, sublet or core charges.
7. Land is a single month-1 purchase (0 by default, a leased shop); one blended depreciation life; no state tax.
8. No construction or pre-opening period: in the *planning* stage the capex, the crew, the rent and the first orders all start in month 1.
9. Orders grow at one rate per year after the ramp-up; no step changes (a competitor opening, a new bay).

## Questions for the CFO review

1. Is "repair orders per day × billed hours per order" the right demand driver, or should demand come from cars in the market
   (customers × visits per year)?
2. Should capacity be the lower of a bay limit and a technician limit, as built, and is 6.5 billed hours per bay-day a sensible default?
3. Are an effective labor rate of $125, 88 % technician efficiency and parts sales of $100 per billed hour a fair planning default for a
   general repair shop? (All are assumptions; none has a citable source.)
4. Should technicians be paid flat-rate (a share of labor revenue) rather than a fixed salary, so payroll flexes with billed hours?
5. Is a 47 % parts margin and a 5 % shop supplies fee reasonable, or should parts be modelled by price band?
6. Should the shop-supplies and comebacks costs be separate drivers (as built) or folded into one cost-of-sales percentage?
7. Is a blended 8-year depreciation acceptable, or do you want lifts, tools and leasehold improvements separately?
8. Are working-capital days of 8 (stock) and 25 (suppliers) on total cost of sales reasonable, or should parts be modelled separately
   from technician payroll?
9. Should the planning stage get a pre-opening period (build-out months with capex and rent but no revenue)?
10. Should the owner's own pay be a separate role from the shop manager?
