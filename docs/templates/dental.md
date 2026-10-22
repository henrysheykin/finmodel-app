# Dental practice template — assumption memo

Template key `dental` (`engine/templates/dental.py`). Samples: `samples/dental-full.xlsx` (stage *growing*: a
six-operatory, four-hygiene-room practice with about 3,000 active patients and an associate dentist; Full tier,
monthly, 3 years) and `samples/dental-full-5y.xlsx` (same, 5 years). Rebuild with
`python scripts/build_samples.py dental dental-full-5y`.

Status: **awaiting CFO review (HUMAN_TODO R1)**. Every default is either sourced (link given) or marked
*assumption*: an illustrative starting point for the wizard's sample-data path, not market statistics. The customer
replaces them with their own numbers.

For general and family dental practices (start-ups, acquisitions, owner-dentist practices with associates).
Orthodontic, oral-surgery and DSO structures are out of scope.

## How the model works

**Patients.** The model opens with *active patients*. Each period new patients join (marketing budget ÷ marketing
cost per new patient, plus referrals & walk-ins that grow yearly) and a monthly share of the opening base is
lost. Annual columns compound the monthly loss over 12 months and let the year's new patients join mid-year (the
fitness and SaaS convention).

**Visits and chairs.** Two streams, each the lower of demand and capacity:

* *Doctor visits*: demand = average active patients × treatment visits per patient per year + the exam and first
  treatment of each new patient; capacity = doctor operatories × visits per operatory per working day × working days.
* *Hygiene recall visits*: demand = average active patients × recall visits per year; capacity = hygienists
  (FTE, never more than the hygiene operatories) × visits per hygienist per day × working days.

**Production and collections.** Production is gross, at office fees: visits × fee, with the fee rising once a year.
Insurance mix turns it into revenue: PPO patients (share of production) are written down by the in-network fee
schedule, and a small share of the net is never collected. *Revenue = collections* = production − PPO write-offs −
bad debt. The KPI table shows collections ÷ gross production (about 85 % at Base). This ratio is lower than the
"collection ratio" dental consultants quote (collections ÷ net production, commonly said to be 97–99 %: a rule of thumb that is an *assumption* here, not sourced), because the base here is
gross production before the PPO write-off.

**Cost of sales.** Dental supplies (% of gross production), lab fees (% of doctor production; hygiene needs no lab)
and card & payment processing (% of collections). Clinical payroll sits in operating expenses, so gross margin
(about 86 %) is *not* comparable to a product business; use EBITDA margin and the payroll ratios.

**Operating expenses.** Payroll through roles (owner dentist, hygienists, dental assistants, front desk, office
manager); associate dentists as a share of the collections they produce; marketing; rent (square feet × rent per
square foot ÷ 12, so rent moves with space); utilities & phone; practice software & IT; malpractice insurance;
equipment maintenance, cleaning & compliance; other G&A.

**Owner pay.** The owner dentist is a payroll role with a market-level salary, so EBITDA is *after* the owner's
pay. Buyers and banks often quote "EBITDA before owner compensation": add the owner role's payroll back.

**Capex and funding.** Month 1: fit-out (cost per sq ft net of landlord allowance × sq ft) + equipment for every
operatory (doctor and hygiene) not already equipped + imaging & IT. Afterwards: equipment refresh as a % of
collections each period. All capex is depreciated over 7 years. Equity, plus an optional equipment / build-out loan.

**Working capital** (the engine applies receivable days to revenue, inventory and payable days to the total cost of
sales):

* Receivable days 17 on collections: about 55 % of collections come from insurers paid ~30 days after the claim, the
  rest is paid by the patient at the visit (assumption). Low 22, High 14; insurance AR days are the lever for a
  slow-paying payer mix.
* Inventory 12 days of cost of sales: supplies are about 41 % of cost of sales, so 12 days is about four weeks of
  supplies (the test `test_inventory_is_supplies_only_in_effect` checks it). Lab work is made to order and card fees
  are netted at the processor, so they carry no stock.
* Payable days 25 on cost of sales: supplies and lab (about 90 % of it) are paid on ~30-day terms (assumption).

## Drivers and Base values

Stage-dependent values are shown for *planning / early / growing / established* (the four wizard stages).
Low / High values are in the code (`engine/templates/dental.py`); Low stacks every pessimistic value.

| Driver | Base | Unit | Source / note |
|---|---|---|---|
| Doctor operatories | 3 / 4 / 6 / 8 | # | assumption: about two operatories per dentist |
| Hygiene operatories | 2 / 3 / 4 / 5 | # | assumption: rooms for the hygienists hired by year 3 |
| Doctor visits per operatory per working day | 4.0 | visits | assumption (Low 3.8, High 4.2) |
| Hygiene visits per hygienist per working day | 8 | visits | assumption: one-hour recall appointments in an 8-hour day |
| Working days per month | 18 | days | assumption: four and a half days a week less holidays and CE |
| Active patients at start | 150 / 1,500 / 3,000 / 4,200 | # | assumption (a new practice starts with founder-referred patients) |
| Referral & walk-in new patients per month | 18 / 20 / 24 / 20 | # | assumption; growth per year 20 % / 10 % / 6 % / 3 % |
| Marketing budget per month | $8,000 / 5,500 / 7,000 / 8,000 | $ | 6.0 % / 4.3 % / 3.6 % of year-1 collections in the early / growing / established stages (22 % in the first year of a start-up); benchmark range 3–5 % ([DentiMax overhead report](https://dentimax.com/dental-office-overhead-percentages/), secondary source) |
| Marketing cost per new patient | $220 / 220 / 210 / 200 | $ | assumption (falls with scale and reputation) |
| Active patients lost per month | 1.5 % / 1.5 % / 1.4 % / 1.3 % | % | assumption (about 15–17 % a year) |
| Doctor visits per active patient per year | 1.15 | visits | assumption |
| New-patient doctor visits in the period they join | 1 | visits | assumption |
| Hygiene recall visits per active patient per year | 1.5 | visits | assumption: not every patient keeps two recalls |
| Production per doctor visit (office fee) | $330 | $ | assumption; year 1, rises with fee increase |
| Production per hygiene visit (office fee) | $200 | $ | assumption: prophylaxis or perio maintenance + exam + radiographs |
| Fee increase per year | 3 % | % | assumption |
| Production from PPO patients | 55 % | % | assumption (Low 60 %, High 50 %) |
| PPO fee-schedule write-off | 25 % | % | assumption |
| Bad debt, % of net production | 1.5 % | % | assumption |
| Dental supplies, % of gross production | 5.0 / 5.0 / 4.9 / 4.7 % | % | benchmark 5–8 % of collections ([DentiMax](https://dentimax.com/dental-office-overhead-percentages/)); about 5.9 % of collections at Base |
| Lab fees, % of doctor production | 10.0 / 10.0 / 9.8 / 9.5 % | % | benchmark 6–8 % of collections (same source); about 7 % of collections at Base |
| Card & payment processing, % of collections | 1.2 % | % | assumption (only the patient-paid part goes through cards) |
| Doctor visits seen by associates | 0 / 20 / 40 / 55 % | % | assumption |
| Associate pay, % of collections they produce | 30 % | % | assumption (Low 32 %, High 28 %) |
| Utilities & phone per month | $900 / 1,200 / 1,800 / 2,300 | $ | assumption |
| Practice software & IT per month | $700 / 900 / 1,300 / 1,700 | $ | assumption |
| Malpractice & liability insurance per month | $450 / 650 / 1,100 / 1,500 | $ | assumption (rises with dentists on staff) |
| Equipment maintenance, cleaning & compliance per month | $700 / 900 / 1,400 / 1,800 | $ | assumption |
| Other G&A per month | $1,500 / 2,000 / 3,000 / 4,000 | $ | assumption |
| Practice size | 1,800 / 2,600 / 4,000 / 5,200 | sq ft | assumption: 360–400 sq ft per room |
| Rent per sq ft per year (incl. CAM) | $30 | $ | assumption; rent is 5–7 % of collections once rooms fill (benchmark 7–10 %, DentiMax) |
| Fit-out per sq ft, net of landlord allowance | $110 (planning only) | $ | assumption |
| Equipment per operatory | $45,000 | $ | assumption: chair, delivery unit, light, cabinetry, sterilisation share |
| Operatories already equipped at start | 0 / 7 / 10 / 13 | # | assumption |
| Imaging & IT at start | $70,000 / 30,000 / 60,000 / 0 | $ | assumption: digital radiography, panoramic or CBCT |
| Equipment refresh, % of collections | 1.5 % | % | assumption |
| Owner dentist salary | $150k / 150k / 180k / 200k | $ | ADA HPI: general-practitioner owner net income about $200,000 ([Dental Economics on ADA HPI data](https://www.dentaleconomics.com/macro-op-ed/industry-news/news/55332389/ada-study-reveals-dentists-revenue-net-income-and-hours-worked-in-2025is-the-profession-struggling)); lower while the practice builds |
| Hygienist salary per FTE | $95k–98k | $ | U.S. median pay $98,100 (May 2025), [BLS Occupational Outlook Handbook](https://www.bls.gov/ooh/healthcare/dental-hygienists.htm); many hygienists work part time, so this is a full-time equivalent |
| Dental assistant / front desk / office manager salary | $44–46k / $40–42k / $65–72k | $ | assumption |
| Payroll taxes & benefits | 10 % | % | assumption (light for a practice that offers benefits) |
| Wage growth | 3 % | % | assumption |
| Depreciation | 7 years | years | assumption |
| Income tax | 21 % | % | U.S. federal corporate rate; state tax not modelled |
| Equity / loan | planning $450k / $450k (10 yr, 9 %); early $100k / $60k; growing $100k / $150k; established $150k / – | $ | assumption, sized so that Base cash stays positive in every month |

For orientation, ADA Health Policy Institute data reported by Dental Economics put general-practitioner dentist
gross billings near $698,000 a year and net income near $200,000 (2020–2024 average). That is *per dentist*, and the
model does not count dentists. Read the growing sample (Base, $1.98 million of collections in year 1) as an owner
plus one associate and it is about **$1.0 million of collections per dentist**; the established stage ($2.64 million)
is about $0.9–1.3 million for two to three dentists. That is **above** the cited $698,000 (a national average that
includes part-time and solo owners), so the productivity defaults (4 doctor visits per operatory per day, $330 per
doctor visit, 8 hygiene visits per hygienist per day) are on the high side of that benchmark. See question 8.

## What the defaults produce (plain-Python reference, 3 years, monthly)

Generated from `python_model` / `reference_run` (the challenger's twin), not typed by hand. *Lowest month-end cash*
is the minimum over the 36 month-ends, with the month in brackets. The Low case stacks every pessimistic value
(lower fees and visits, heavier PPO mix, higher attrition, costlier patients, higher costs); it is a **stress case**,
runs out of cash in every stage, and the Checks sheet flags the funding gap. Base is funded in every month in all four
stages.

| Stage | Case | Collections Y1 | Collections Y3 | EBITDA margin Y1 → Y3 | Patients Y3 | Doctor chair use Y3 | Lowest month-end cash |
|---|---|---:|---:|---:|---:|---:|---:|
| planning | Low (stress) | $326,893 | $743,194 | -88% → -6% | 1,260 | 72% | $-378,728 (month 36) |
| planning | Base | $432,231 | $1,107,397 | -44% → 24% | 1,729 | 94% | $43,912 (month 20) |
| planning | High | $557,829 | $1,322,739 | -12% → 34% | 2,281 | 100% | $222,971 (month 13) |
| early | Low (stress) | $838,802 | $1,028,190 | -11% → -8% | 1,746 | 71% | $-277,027 (month 36) |
| early | Base | $1,091,038 | $1,455,364 | 13% → 20% | 2,194 | 87% | $90,794 (month 1) |
| early | High | $1,346,550 | $1,876,019 | 28% → 35% | 2,715 | 100% | $105,605 (month 1) |
| growing | Low (stress) | $1,565,966 | $1,710,591 | -4% → -5% | 2,918 | 77% | $-304,710 (month 36) |
| growing | Base | $1,975,300 | $2,337,329 | 15% → 19% | 3,536 | 91% | $123,032 (month 1) |
| growing | High | $2,442,864 | $2,956,070 | 30% → 34% | 4,248 | 100% | $149,010 (month 1) |
| established | Low (stress) | $2,142,891 | $2,164,227 | 2% → -3% | 3,710 | 72% | $-96,404 (month 36) |
| established | Base | $2,644,298 | $2,906,066 | 19% → 20% | 4,414 | 84% | $67,241 (month 1) |
| established | High | $3,212,197 | $3,780,491 | 32% → 35% | 5,217 | 97% | $100,875 (month 1) |

Sample stage (*growing*, Base), year 1: gross production $2,325,079, collections $1,975,300 (85.0 %), hygiene 39.8 %
of production, cost of sales 13.9 % of collections, payroll 48.0 % (owner dentist included), associates 7.2 %,
marketing 4.3 %, rent 6.1 %, EBITDA 15.3 %, 4,239 doctor and 4,631 hygiene visits, about $262 of production per visit.

Consistency across stages: rooms, square feet, staff and fixed costs grow with the number of chairs; rent falls from
12.5 % of year-1 collections (planning) to 7.1 / 6.1 / 5.9 % (early / growing / established); supplies, lab,
marketing cost per patient and attrition improve with scale. High is merely better: no driver makes High costlier.
The High case is an optimistic stack (EBITDA margins of about 35 %); treat it as an upside, not a forecast.

**Monthly versus annual.** The two granularities agree closely, not exactly: attrition compounding, mid-year joining
and the capacity caps (which bind month by month) interact. At Base the annual model's collections differ from the
monthly one by +0.8 % to -0.9 % in every year of every stage (the tests check all five years of a five-year horizon and allow 2 %). With no attrition and no binding
capacity they agree to the cent (`test_monthly_and_annual_agree_exactly_without_attrition_or_binding_capacity`).

## KPI table (Dashboard in Full, P&L sheet in Light)

Active patients, new patients, patients lost, marketing cost per new patient, doctor and hygiene visits and capacity
and their utilisation, gross production, hygiene share of production, production per visit, collections, collections
÷ gross production, collections per active patient and per operatory, gross margin, EBITDA margin (after owner pay),
collections per square foot. Volumes, production and collections are recomputed by the independent challenger; the
ratio rows through `kpi_reference`.

## Simplifications to review

1. Operatories are fixed for the horizon (no chairs added in year 2 or 3). A practice that outgrows its chairs shows
   rising doctor-chair utilisation, then the cap; model an expansion with a higher operatory count and more square feet.
2. Patients are one pool. No split between new and established patients, no emergency, orthodontic or cosmetic mix,
   no membership plans for the uninsured.
3. The PPO write-off is one average. Medicare Advantage, Medicaid and fee-for-service patients are not separated.
4. Insurance payments are modelled only through receivable days; there are no claim denials or timing shocks.
5. Rent has no escalator; other costs do not inflate except payroll (wage growth). Build-out financing is a plain loan.
6. Dentist capacity is not modelled separately from chairs; assume dentists are staffed to the chairs (the owner's
   salary is a role, associates are paid on collections).
7. Staff cost is high against published benchmarks (question 1): the sample practice has hygiene at about 40 % of
   hygiene collections.
8. No dentist count and no cap on dentist time: dentists are assumed to be staffed to the chairs. Associates are paid on
   collections, so do not also add an associate payroll role while the associate share is above zero (the template
   refuses that combination). For EBITDA before owner pay, add back the owner role's payroll.

## Questions for the CFO review

1. Staff wages at Base (growing, year 1) are about 34.5 % of collections excluding the owner dentist (38 % with 10 %
   payroll taxes & benefits; 48 % including the owner), against a 24–26 % staff benchmark (DentiMax, secondary
   source, which probably excludes dentists). The main driver is the assistants: 4.5 FTE are about 10 % of
   collections in wages (11 % with taxes), ahead of front desk (6 %) and the office manager (3 %); hygienists are
   about 15 %. Should assistants per chair (0.75 per doctor operatory here) or hygienist productivity (8 visits a
   day) be changed?
2. Is it right to treat the owner dentist as a market-rate salary inside EBITDA, or should the headline be EBITDA
   before owner compensation, as buyers and lenders usually quote?
3. Is "collections ÷ gross production" (about 85 %) a clear label for the PPO mix, or should the model show net
   production (after the fee-schedule write-off) and a 97–99 % collection ratio?
4. Are 17 receivable days on collections, 12 inventory days on cost of sales (about four weeks of supplies) and
   25 payable days acceptable simplifications?
5. Should operatories be addable in year 2 or 3 (with space and capex), since capacity binds around 90–100 % in Y3?
6. Are the High margins (about 35 %) too generous for a default upside case?
7. Is 7-year depreciation right for operatory equipment and fit-out together?
8. Collections per dentist are about $1.0 million in the growing sample against the cited $698,000 gross billings per
   general-practitioner dentist (national average). Should visits per chair or fees be lowered so the defaults sit
   nearer the benchmark, or is a busy, well-run practice the right starting point?
