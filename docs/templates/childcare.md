# Childcare / daycare centre template — assumption memo

Template key `childcare` (`engine/templates/childcare.py`, wizard order 160). Samples: `samples/childcare-full.xlsx`
(stage *planning*: a new 60-place centre, Full tier, monthly, 3 years) and `samples/childcare-full-5y.xlsx`; rebuild
with `python scripts/build_samples.py childcare`.

Status: **awaiting CFO review (HUMAN_TODO R1)**. Sources are given where a default is anchored to a published
figure; every other default is marked **assumption**: an illustrative starting point for the wizard's sample-data
path that the customer replaces. The figures in the tables below were produced by the plain-Python twin
(`python_model`), which the challenger proves equal to the workbook.

For licensed centre-based childcare, daycare and preschool centres that charge monthly tuition per child, may take
subsidy / voucher children and staff to a ratio.

## How the model works

**Places and enrolment.** The centre is licensed for a number of *places* (children), plus places added each year from
year 2. A share of the places is for infants and toddlers, the rest for preschoolers. Enrolment is a % of the
licensed places: it starts at its month-1 level and climbs in a straight line to its full level over *months to
reach full enrolment* (a new centre fills slowly; an established one has no ramp). Annual models use the exact
average of the monthly line, so revenue is the same in a monthly and an annual workbook.

**Tuition.** Children enrolled in each band × the monthly tuition of the band × the months in the period, raised by the
yearly tuition increase. A share of the children is paid by a subsidy / voucher programme at a percentage of the list
tuition (states usually pay below the market rate); the other children pay list tuition less sibling and staff
discounts. Subsidy payments are a separate revenue line so the dependence on public money is visible.

**Registration fees.** One fee per new child. New children = the rise in enrolment over the period above the *children already enrolled at
start* (the opening fill and the ramp-up; places added in year 2+ fill the same way) plus the children who leave and are
replaced (turnover % a year × average enrolment). Children already in the centre at the start (capped at the month-1 enrolment, so a number above it is treated as that) pay no registration fee:
0 in the planning stage, and in the other stages the enrolment at the start (licensed places × month-1 enrolment).

**Staffing by ratio.** Teachers on the floor, per band = children enrolled in the band ÷ children per teacher, rounded up
to whole teachers (`ROUNDUP`). Teachers hired = teachers on the floor × a *coverage factor*, because the centre is open
longer than one shift and teachers take breaks and leave. Cost = teachers hired × salary × (1 + payroll taxes) ×
wage growth. **Teacher payroll is a cost-of-sales line, not a headcount role**: the headcount roles are only the
director, the office & enrolment coordinator and the cook / kitchen assistant, so no teacher is counted twice
(`tests/test_childcare.py::test_teacher_payroll_is_a_cost_of_sales_line_and_not_headcount`).

**Other cost of sales.** Food = children enrolled × cost per child per operating day × operating days per month;
supplies & activities = children enrolled × cost per child per month. Both rise with a yearly cost increase.

**Operating costs.** Headcount payroll, rent (licensed places × square feet per place × rent per square foot a year),
utilities & cleaning (same floor area × cost per square foot), insurance, licensing / background checks / training,
marketing, parent app & software, card / ACH fees (% of parent-paid tuition), other G&A. Rent and utilities grow when
places are added, because the floor area grows with them.

**Capex and funding.** Month 1: build-out per square foot and furniture & equipment per place for every place not yet
built out and equipped, plus the playground. From year 2: build-out and furniture for the places added that year, plus
yearly equipment replacement per licensed place. Depreciated over 10 years. Equity and an optional loan at the start.

**Working capital.** Receivable days are a blend: the subsidy share of children is paid about 45 days late, parents pay
by card or ACH within about 2 days, and the engine applies one receivable-days driver to **all** revenue, so the blend is weighted by the subsidy payments'
share of revenue (about 23% in the Base case: 25% of children at 85% of list tuition, after discounts and with
registration fees): `ar_days` = 23% × 45 + 77% × 2 ≈ 11.9, entered as 12 (if you change the subsidy share or rate, change the receivable days with it;
`test_receivable_days_blend_parent_and_subsidy_collection` checks the defaults). Tuition billed in advance is not
modelled as deferred revenue (conservative). Inventory and payables are taken on **total** cost of sales in
`engine/core.py`, and about four fifths of the centre's cost of sales is teacher pay, which is never stocked. Real stock is
about two weeks of food and supplies, which are about 19% of cost of sales (established, Base, year 3): 14 days × 19%
≈ 2.7, entered as 3 inventory days. Payables: wages are paid about 7 days in arrears, suppliers about 30 days:
(7 × 81% + 30 × 19%) ≈ 11 payable days.

Monthly and annual workbooks give identical revenue, registrations, food, supplies, operating costs and capex in every
year. The only difference is teacher payroll: teachers are rounded up per period, so while enrolment is still ramping up
an annual model (one rounding per year) can differ from the monthly one by less than one teacher per band (in the Base
case up to about 5% of revenue in year 1 of the planning stage), and gross profit and EBITDA move by exactly that amount.
From the first year with full enrolment the two are identical (established: every year; the tests assert all of this,
`tests/test_childcare.py`). Use monthly granularity for a new centre.

## Drivers (Base value in the planning sample; the other stages are in the template file)

| Driver | Base | Unit | Source |
|---|---:|---|---|
| Licensed places at start | 60 (growing 90, established 120) | # | assumption |
| Children already enrolled at start | 0 (planning); early 30, growing 63, established 105.6 (= places × month-1 enrolment; Low and High follow their own month-1 enrolment) | # | assumption; these children pay no registration fee. It does **not** follow the month-1 enrolment automatically: if you change the places or the month-1 enrolment, change this number with them |
| Licensed places added each year (from year 2) | 0 (growing stage: Low 0, Base 10, High 15) | # | assumption |
| Places for infants & toddlers | 35% | % | assumption |
| Enrolment once full | 85% (Low 78%, High 90%) | % of places | assumption (centres typically run below 100% because of age-mix and holiday gaps) |
| Enrolment in month 1 | 20% (Low 15%, High 25%) | % of places | assumption |
| Months to reach full enrolment | 12 (Low 18, High 9) | months | assumption |
| Operating days per month | 21 | days | assumption |
| Children leaving each year | 30% (Low 35%, High 25%) | % of enrolled | assumption |
| Tuition per infant / toddler per month | $1,500 (Low $1,430, High $1,570) | $ | assumption; context: [Child Care Aware of America](https://www.childcareaware.org/price-landscape24) reports a 2024 national average price of child care of $13,128 a year (about $1,094 a month, all ages), infants cost more; the defaults sit above that average to reflect a licensed centre |
| Tuition per preschooler per month | $1,100 (Low $1,040, High $1,160) | $ | assumption (same context) |
| Tuition and fee increase per year | 3% (Low 2.5%, High 4%) | % | assumption |
| Sibling & staff discounts | 5% of parent-paid tuition (Low 6%, High 4%) | % | assumption |
| Registration fee per new child | $150 (Low $100, High $200) | $ | assumption |
| Children paid by subsidy / vouchers | 25% | % of enrolled | assumption (varies from 0% to well over 50% by state and neighbourhood) |
| Subsidy payment | 85% of list tuition (Low 82%, High 88%) | % | assumption (state subsidy rates are usually below market price) |
| Children per teacher, infants & toddlers | 6 | # | assumption. Licensing ratios differ by state and age; 6 is a blend of infants (about 4) and toddlers (about 6 to 8). Replace with your state's rule |
| Children per teacher, preschool | 12 | # | assumption (state rules range from about 10 to 15 for 3 to 5 year olds) |
| Coverage factor | 1.20 (Low 1.25, High 1.15) | x | assumption (opening hours of 10 to 11 hours against an 8-hour shift, breaks, leave) |
| Teacher salary per FTE per year | $35,000 (Low $36,500, High $33,500) | $ | [BLS](https://www.bls.gov/ooh/personal-care-and-service/childcare-workers.htm): childcare workers median $34,980 a year and [preschool teachers](https://www.bls.gov/ooh/education-training-and-library/preschool-teachers.htm) $38,140 (May 2025); the default is close to the childcare-worker median, below the preschool-teacher median, so it suits a staff of mostly aides and assistant teachers; raise it for a staff of lead teachers |
| Food per child per operating day | $4.00 (Low $4.20, High $3.80) | $ | assumption |
| Supplies & activities per child per month | $30 (Low $33, High $27) | $ | assumption |
| Food, supplies & utilities cost increase | 3% | % | assumption |
| Floor area per licensed place | 75 | sq ft | assumption (indoor play space rules are commonly 35 sq ft per child; the rest is kitchen, offices, bathrooms and circulation) |
| Rent per square foot per year | $16 (Low $17, High $15) | $ | assumption (net lease) |
| Rent increase per year | 3% | % | assumption |
| Utilities & cleaning per square foot per year | $6.50 | $ | assumption |
| Insurance per month | $1,800 | $ | assumption (growing $2,600, established $3,400: scales with places) |
| Licensing, background checks & training per month | $600 | $ | assumption |
| Marketing per month | $2,500 (growing $3,000, established $2,000) | $ | assumption (a waitlist reduces the need) |
| Parent app & software per month | $400 | $ | assumption |
| Card / ACH fees | 2.5% of parent-paid tuition | % | assumption |
| Other G&A per month | $1,200 | $ | assumption |
| Build-out per square foot | $60 | $ | assumption (leased shell: bathrooms, kitchen, fencing, finishes) |
| Furniture & equipment per licensed place | $2,200 | $ | assumption |
| Playground & outdoor area | $40,000 | $ | assumption |
| Equipment replacement per place per year | $150 | $ | assumption |
| Staff (planning) | director 1 FTE $62,000; office 0.5 FTE $38,000; cook 0.5 FTE $34,000 | | director: [BLS](https://www.bls.gov/ooh/management/preschool-and-childcare-center-directors.htm) preschool and childcare center directors median $59,300 (May 2025); others assumption |
| Payroll taxes & benefits / wage growth | 12% / 3% | % | assumption |
| Receivable / inventory / payable days | 12 / 3 / 11 | days | assumption, derived above |
| Depreciation / income tax | 10 years / 21% | | assumption (21% is the US federal corporate rate) |
| Equity / loan | $450,000 / $250,000 at 8% over 10 years | $ | assumption |

## Childcare metrics table (KPIs sheet in Full, P&L sheet in Light; the Dashboard shows three of the rows)

Licensed places and place-months, children enrolled (year end) and child-months, occupancy (child-months ÷
place-months), new children, teachers on the floor, revenue and its three parts (parent-paid tuition, subsidy &
vouchers, registration fees), subsidy % of tuition revenue, tuition revenue per child-month, teacher payroll and teacher
payroll as % of revenue, gross profit and margin, EBITDA and margin. Every row is recomputed by the independent
challenger. The two KPIs-sheet charts show children enrolled with occupancy, and revenue by source.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Case | Revenue Y1 | Revenue Y3 | EBITDA margin Y1 → Y3 | Children enrolled, end Y3 | Lowest month-end cash |
|---|---|---:|---:|---:|---:|---:|
| planning | Low | $267,943 | $633,417 | -85% → -14% | 47 | -$321,112 |
| planning | Base | $419,706 | $747,148 | -30% → 8% | 51 | $66,124 |
| planning | High | $567,744 | $861,698 | 1% → 18% | 54 | $175,224 |
| early | Low | $445,888 | $633,417 | -36% → -14% | 47 | -$243,513 |
| early | Base | $586,580 | $747,148 | -6% → 8% | 51 | $52,240 |
| early | High | $710,523 | $861,698 | 12% → 18% | 54 | $99,286 |
| growing | Low | $861,699 | $974,488 | -13% → -11% | 72 | -$235,067 |
| growing | Base | $1,039,524 | $1,403,386 | 5% → 11% | 96 | $88,152 |
| growing | High | $1,187,027 | $1,764,678 | 20% → 28% | 110 | $175,397 |
| established | Low | $1,267,626 | $1,331,800 | -4% → -5% | 98 | -$161,442 |
| established | Base | $1,458,230 | $1,547,037 | 11% → 11% | 106 | $43,488 |
| established | High | $1,628,784 | $1,761,693 | 24% → 25% | 110 | $52,179 |

The lowest cash is the lowest **month-end** balance over the 3 years. Base is funded in every month in all four
stages. The Low case stacks every pessimistic value (slower fill, lower enrolment and tuition, higher wages, rent and
food, a lower subsidy rate), so it is a stress case and runs out of cash; the Checks sheet flags the funding gap. In the
Base case a mature centre earns a gross margin of about 47 to 50% after teacher pay, food and supplies (teacher payroll is
40 to 43% of revenue; with the director, office and kitchen roles total labour is about 56 to 57%, and rent plus utilities and
cleaning about 14%).

## Simplifications to review

1. Two age bands with one enrolment % for both; no separate infant waitlist, no school-age after-school or summer camp
   programme, no part-time or drop-in children (every child pays a full-month tuition).
2. One blended teacher salary and one coverage factor: no lead / assistant split, no overtime, no substitute pool,
   no wage premium for infants. Teachers on the floor are rounded up per period and per band, with no minimum of two adults.
3. Subsidy children are a share of enrolled children at one % of list tuition; no co-payments, no enrolment-based
   (rather than attendance-based) payment rules, no state grants or wage-support programmes.
4. Receivable days are one blended number (see working capital); tuition is not billed in advance and there is no
   deferred revenue or security deposit.
5. No seasonality (summer drop-offs, September fill, holiday closures change the number of tuition-paying months);
   operating days affect food only.
6. No food-programme (USDA CACFP) reimbursement; food is a full cost.
7. Registration fees and tuition rise with the same yearly increase; tuition for places added in year 2+ is the same as
   for existing places and fills at the same enrolment %.
8. Rent is a net rent per square foot of the floor area; no tenant improvement allowance, no property tax and no
   utilities spike for a larger centre beyond the per-square-foot rate.
9. The planning stage has no pre-opening period: rent, staff and the build-out all start in month 1 while only 20% of
   the places are enrolled, so the first months show a deeper loss and cash dip than a real opening (a lease with a
   rent-free fit-out period, or hires timed to enrolment, would soften it). The director, office and kitchen roles can be
   started later with their "first month on payroll" driver.
10. Insurance, licensing, software and other G&A are flat monthly amounts: they do not grow with the yearly cost
    increase or with places added (set the stage's amounts for the size you expect); marketing grows only at its own rate.
11. Owned premises are not modelled (no land line); a centre that buys its building needs the property template.

## Questions for the CFO review

1. Is teacher pay in cost of sales (so gross margin is the margin after direct care) the right presentation, with
   director, office and kitchen in operating expenses?
2. Are the Base ratios (1:6 for infants and toddlers, 1:12 for preschool) and the 1.20 coverage factor a fair national
   starting point, or should the wizard ask for the state?
3. Is a Base enrolment of 85% with a 12-month ramp realistic for a new centre, and a Base EBITDA margin of about 8% in
   year 3 (11% when established) a believable result?
4. Should subsidy / voucher payments get their own collection lag driver (today one blended receivable-days number)?
5. Should tuition be billed in advance (deferred revenue) and a security deposit modelled?
6. Is $60 a square foot of build-out plus $2,200 a place for furniture and a $40,000 playground a fair opening capex for
   a leased 60-place centre (about $442,000)?
7. Should after-school and summer programmes be a second revenue line?
8. Should the template add a seasonal profile (September fill, summer dip) in monthly models?
