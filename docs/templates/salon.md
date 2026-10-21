# Hair salon / barbershop template — assumption memo

Template key `salon` (`engine/templates/salon.py`, wizard order 90). Samples: `samples/salon-full.xlsx` (stage
*planning*: a new 8-chair salon, Full tier, monthly, 3 years) and `samples/salon-full-5y.xlsx`; rebuild with
`python scripts/build_samples.py salon salon-full-5y`.

Status: **awaiting CFO review (HUMAN_TODO R1)**. No figure below is market data. Every default is marked
**assumption**: an illustrative starting point for the wizard's sample-data path that the customer replaces. For
cross-checking wages, the US Bureau of Labor Statistics publishes pay for the two main occupations:
[barbers, hairstylists and cosmetologists](https://www.bls.gov/ooh/personal-care-and-service/barbers-hairstylists-and-cosmetologists.htm)
and [receptionists](https://www.bls.gov/ooh/office-and-administrative-support/receptionists.htm). The defaults were not
derived from those pages.

For hair salons, barbershops and nail/beauty salons that run on styling chairs, with employed stylists on commission
and/or independent stylists renting a chair.

## How the model works

**Chairs and who works them.** The salon has *styling chairs* (plus a number added each year from year 2). A share
of them (*chairs rented to independent stylists*) is let out to renters; the rest are worked by employed stylists.

**Employed chairs → services.** Bookable hours = employed chairs × days open per month × bookable service hours per
chair per day. Booked hours = bookable hours × *chair utilisation*. Utilisation starts at its year-1 level and gains a
set number of percentage points each year up to a ceiling (a new salon fills its book; a mature one levels off).
Services = booked hours × services per booked hour. Service revenue = services × average service price.

**Retail.** A share of services ends with a retail product sale (attach rate × average product sale).

**Chair rent.** Rented chairs × weekly rent × 52 ÷ 12 × the share of rented chairs actually paying (occupancy).
Renters keep their own client revenue, so it never enters the salon's revenue; the salon earns the rent only, and
pays no commission, backbar supplies or card fees on a renter's services.

**Cost of sales.** Stylist commission (% of service revenue, grossed up for payroll taxes with the model's payroll
tax rate), retail product cost (% of product sales), backbar supplies per service (colour, developer, shampoo; rises
with the yearly price increase), card fees on service and retail sales.

**Operating costs.** Staff payroll through headcount (salon manager, receptionist, shampoo and floor assistants),
marketing, salon rent, utilities, booking software, insurance & licences, towels / laundry / cleaning, other G&A.

**Capex and funding.** Month 1: fit-out, a styling station and chair for every chair not yet equipped, and backwash
units. From year 2, the stations for the chairs added that year (bought in the first period of the year).
Depreciated over 7 years. Equity and an optional loan at the start. Clients pay at the chair, so receivables are two
days of card settlement; about two weeks of product and supply stock.

Monthly and annual versions give the same figures: nothing in the model is seasonal or compounds monthly.

## Drivers (Base value in the planning sample; the other stages are in the template file)

| Driver | Base | Unit | Source |
|---|---:|---|---|
| Styling chairs at start | 8 | # | assumption |
| Chairs added each year (from year 2) | 0 (growing stage: Low 1, Base 1, High 2) | # | assumption |
| Days open per month | 24 | days | assumption (six days a week) |
| Bookable service hours per chair per day | 8 | hours | assumption |
| Chair utilisation, year 1 | 45% (Low 38%, High 52%) | % | assumption (new salon) |
| Utilisation gain per year | 10 pts (Low 8, High 12) | % | assumption |
| Utilisation ceiling | 80% | % | assumption |
| Services per booked hour | 1.0 (Low 0.9, High 1.1) | # | assumption (barbershops run higher, colour-heavy salons lower) |
| Average service price, year 1 | $68 (Low $62, High $74) | $ | assumption (blended cut, colour, styling) |
| Price increase per year | 3% | % | assumption |
| Services with a retail product sale | 20% | % | assumption |
| Average retail product sale | $30 | $ | assumption |
| Chairs rented to independent stylists | 25% of chairs | % | assumption |
| Chair rent per rented chair per week | $200 | $ | assumption |
| Rented chairs paying rent | 90% | % | assumption |
| Stylist commission, % of service revenue | 45% (Low 48%, High 42%) | % | assumption |
| Retail product cost, % of product sales | 50% | % | assumption |
| Backbar supplies per service | $4.00 | $ | assumption |
| Card fees, % of service & product sales | 2.9% | % | assumption |
| Marketing per month / growth | $2,500 / 0% a year (flat across Low, Base, High) | $ | assumption |
| Salon rent per month | $6,500 | $ | assumption (about 2,400 sq ft) |
| Utilities per month | $900 | $ | assumption |
| Booking software per month | $250 | $ | assumption |
| Insurance & licences per month | $650 | $ | assumption |
| Towels, laundry & cleaning per month | $450 | $ | assumption |
| Other G&A per month | $700 | $ | assumption |
| Fit-out & refurbishment | $95,000 | $ | assumption |
| Styling station & chair, per chair | $3,200 | $ | assumption |
| Backwash units to buy / each | 2 / $3,400 | #, $ | assumption |
| Staff (planning) | manager 0.5 FTE $48,000; receptionist 1 FTE $33,000; assistant 1 FTE $29,000 | | assumption |
| Payroll taxes & benefits / wage growth | 12% / 3% | % | assumption |
| Receivable / inventory / payable days | 2 / 3 / 20 | days | assumption (inventory is days of cost of sales; most of a salon's cost of sales is commission, so 3 days approximates about two weeks of retail and backbar stock) |
| Depreciation / income tax | 7 years / 21% | | assumption (21% is the US federal corporate rate) |
| Equity / loan | $150,000 / $70,000 at 8% over 5 years | $ | assumption |

## Salon metrics table (KPIs sheet in Full, P&L sheet in Light; the Dashboard shows three of the rows)

Styling chairs (year end), chairs rented, bookable and booked chair hours, chair utilisation, services performed,
revenue and its three parts (services, retail, chair rent), revenue per service, retail as % of service revenue,
service revenue per employed chair, chair rent per rented chair per month, gross profit and margin, EBITDA and
margin. Every row is recomputed by the independent challenger (line rows from the reference series, ratio rows from
a plain-Python twin). The two KPIs-sheet charts show services with chair utilisation, and revenue by source.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Case | Revenue Y1 | Revenue Y3 | EBITDA margin Y1 → Y3 | Services Y3 | Lowest cash |
|---|---|---:|---:|---:|---:|---:|
| planning | Low | $327,475 | $477,189 | -34% → -13% | 6,718 | $-209,033 |
| planning | Base | $479,059 | $725,289 | -6% → 9% | 8,986 | $53,975 |
| planning | High | $674,091 | $1,054,752 | 12% → 24% | 11,557 | $158,388 |
| early | Low | $425,863 | $528,370 | -18% → -9% | 7,465 | $-131,416 |
| early | Base | $581,357 | $768,700 | 1% → 10% | 9,539 | $64,256 |
| early | High | $774,453 | $1,081,890 | 16% → 24% | 11,861 | $160,291 |
| growing | Low | $700,287 | $939,576 | -20% → -10% | 13,281 | $-291,856 |
| growing | Base | $948,758 | $1,326,233 | -0% → 8% | 16,451 | $101,330 |
| growing | High | $1,255,769 | $2,082,366 | 15% → 25% | 22,810 | $257,722 |
| established | Low | $1,015,706 | $1,090,861 | -14% → -13% | 15,428 | $-366,168 |
| established | Base | $1,367,309 | $1,537,400 | 4% → 7% | 19,077 | $97,894 |
| established | High | $1,799,811 | $2,109,503 | 18% → 21% | 23,114 | $315,242 |

The Low case stacks every pessimistic value (slower ramp, fewer services per hour, lower prices, higher commission
and supply cost), so it is a stress case and runs out of cash; the Checks sheet flags the funding gap. Base cases
are funded throughout.

## Simplifications to review

1. One blended service price and one commission rate; no split between cut, colour and treatments, and no tiered
   commission by stylist seniority or sales.
2. No seasonality (pre-holiday and wedding peaks, January lull); no no-shows or cancellations beyond utilisation.
3. Stylists are paid commission only. A minimum-wage guarantee or hourly floor for employed stylists is not modelled.
4. Tips are excluded from revenue; payroll tax on commission uses the model's single payroll-tax rate.
5. Chair-rent renters are a share of all chairs and pay a flat weekly rent, increased with the yearly price increase;
   renters' own product sales, supplies and card fees are not the salon's.
6. Chairs added in year 2 and later work at the same utilisation as existing chairs from their first day; wash units
   are bought only at the start; no equipment replacement inside the horizon.
7. Marketing is a budget and does not drive utilisation directly; utilisation is the demand driver.
8. Rent, utilities and floor space do not grow with chairs added in years 2+; the growing-stage sample adds only one chair a year for that reason.
9. Rented chairs are chairs × the rented share and can be fractional (for example 3.25 chairs); round the share to whole chairs when you enter your own numbers.

## Questions for the CFO review

1. Is commission on service revenue (employed stylists) plus a chair-rent option the right pair of pay models for
   the wizard, or should hourly pay with a commission threshold be offered?
2. Is a Base commission of 45% and weekly chair rent of $200 a sensible default across US markets?
3. Should the gross-up of commission for payroll taxes use the same 12% as staff payroll?
4. Is a year-1 utilisation of 45% rising 10 points a year a reasonable ramp for a new salon, and the 80% ceiling right?
5. Should the sample show retail as a separate stream (20% attach, $30 ticket), or fold it into the service price?
6. Should the template default include a seasonal profile (December, spring wedding season) in monthly models?
7. Is about 3 days of cost of sales a fair stand-in for retail and backbar stock, given that commission is not stocked?
