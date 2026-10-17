# Home services / trades template — assumption memo

Template key `home_services` (`engine/templates/home_services.py`). Sample: `samples/home_services-full.xlsx`
(stage *growing*: 7 technicians + 2 office FTE, Full tier, monthly, 3 years; rebuild with
`python scripts/build_samples.py home_services`).

Status: **awaiting CFO review (HUMAN_TODO R1)**. All defaults are illustrative starting points for the
wizard's sample-data path, not market statistics.

For plumbing, HVAC, electrical, cleaning, pest control and landscaping businesses that sell jobs done by
their own technicians.

## How the model works

**Technician capacity.** One required role, *field technicians* (`tech`); any other role (dispatch,
office, sales) is overhead. Job capacity = technician FTE on payroll × jobs per technician per working
day × working days per month. FTE comes from the shared headcount engine (start month, yearly
headcount growth), so a technician hired in month 7 adds capacity from month 7.

**Demand.** Jobs demanded = jobs booked from marketing leads + repeat & referral jobs.
Leads = marketing spend ÷ cost per lead; booked jobs = leads × booking rate. The marketing budget and
the repeat & referral volume each grow once a year by their own rate. In monthly models a June–August
busy season applies: those three months get +uplift, the other nine −uplift ÷ 3, so the year's demand
is unchanged; annual models use the yearly total.

**Jobs completed = the lower of demand and capacity.** When demand is above capacity the extra jobs are
turned away (shown on the Dashboard), which is the signal to hire. With a busy season and tight capacity,
the summer cap costs revenue even though the year's demand is the same — the reason monthly and annual
versions of the same business differ only in that case.

**Revenue.** Job revenue = jobs completed × average revenue per job (rises once a year with the price
increase). Maintenance-plan revenue = average plan members (year-1 number, growing yearly) × monthly plan
fee (rises with the same price increase).

**Cost of delivery (COGS).** Technician payroll (salary + payroll taxes & benefits, wage growth),
materials & parts (% of job revenue), vehicles per technician per month, and the cost of plan visits
(% of plan fees). Gross profit is the field margin.

**Operating expenses.** Dispatch, office and other payroll; marketing; field software & phones per
technician; insurance & licences; shop / office rent; other G&A; card processing fees (% of revenue).

**Capex.** Start-up capex in month 1, plus a van & tools for every technician added beyond those already
equipped at the start (*Technicians already equipped at start*: 0 for a new business, the current fleet
for a trading one). Depreciated straight line over the depreciation period.

**Working capital.** Small receivable days (most jobs are paid on completion; commercial work stretches
this), a few days of parts inventory and supplier payable days. Both apply to the whole cost of delivery
in the shared engine, including payroll — see simplifications.

## Home services metrics table (Dashboard in Full, P&L sheet in Light)

Technicians (year end), job capacity, jobs demanded, jobs completed, utilisation, jobs turned away, jobs
booked from leads, marketing spend and marketing cost per booked job, revenue, job revenue, average
revenue per job, revenue per technician, plan members and plan revenue, plans share of revenue, gross
profit and margin, gross profit per job, EBITDA and EBITDA margin. Jobs, technicians, capacity and plan
revenue are recomputed by the independent challenger.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Case | Revenue Y1 | Revenue Y3 | Gross margin Y3 | EBITDA margin Y1 → Y3 | Utilisation Y3 | Cash Y3 |
|---|---|---:|---:|---:|---:|---:|---:|
| planning | Low | $142,558 | $335,938 | 18% | -42% → -23% | 57% | $-191,894 |
| planning | Base | $186,960 | $515,098 | 38% | -14% → 9% | 75% | $33,089 |
| planning | High | $236,700 | $722,035 | 50% | 6% → 27% | 90% | $252,609 |
| early | Low | $373,052 | $608,162 | 29% | -15% → -5% | 73% | $-50,274 |
| early | Base | $488,130 | $861,931 | 43% | 7% → 18% | 89% | $297,477 |
| early | High | $603,651 | $1,113,828 | 51% | 20% → 31% | 100% | $627,538 |
| growing | Low | $1,373,008 | $1,796,473 | 28% | 0% → 3% | 76% | $139,098 |
| growing | Base | $1,710,030 | $2,376,161 | 40% | 16% → 20% | 86% | $948,820 |
| growing | High | $2,056,472 | $3,040,262 | 49% | 26% → 32% | 96% | $1,851,112 |
| established | Low | $4,266,520 | $4,833,456 | 29% | 8% → 8% | 80% | $857,088 |
| established | Base | $5,121,900 | $6,090,765 | 40% | 20% → 22% | 87% | $2,749,029 |
| established | High | $6,055,898 | $7,555,089 | 47% | 29% → 33% | 94% | $4,937,905 |

The Low case stacks every pessimistic value (lower ticket, fewer jobs per day, higher costs per lead and
materials), so it is a stress case rather than a forecast; planning and early Low cases run out of cash,
and the Checks sheet flags the funding gap.

## Simplifications to review

1. Inventory and payable days are applied to the whole cost of delivery (shared engine), which includes
   technician payroll. Defaults are small (5 / 20 days) to keep the effect modest.
2. Plan members grow at a flat yearly rate; they are not linked to jobs completed or to plan churn.
3. One average ticket for all jobs; no split between service calls, repairs and installations.
4. Busy season is fixed to June–August (cooling-led trades). Heating-led or snow businesses would need
   winter months — the uplift can be set to 0.
5. Vans are bought outright; leased vans belong in the vehicle cost per technician instead (set
   *Van & tools per technician added* to the tools only).
6. No warranty callbacks, financing fees for customer financing, or technician commission plans.

## Questions for the CFO review

1. Are the default jobs per technician per day (2.35 / 2.5 / 2.65) and average revenue per job
   ($415 / $440 / $465) sensible starting points for a mixed residential trade?
2. Should technician pay include a commission / spiff on job revenue instead of salary only?
3. Is a 25 % busy-season uplift the right default, or should the default be 0 with seasonality opt-in?
4. Should plan members be driven by an attach rate on jobs with churn (more realistic, more inputs)?
5. Is straight-line 5-year depreciation right for vans and tools in the sample?
