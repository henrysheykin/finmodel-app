# Professional services template — assumption memo

Template key `services` (`engine/templates/services.py`). Sample: `samples/services-full.xlsx`
(stage *growing*: 4 partners/seniors + 12 consultants + contractors, Full tier, monthly, 3 years;
rebuild with `python scripts/build_samples.py services`).

Status: **awaiting CFO review (HUMAN_TODO R1)**. All defaults are illustrative starting points
for the wizard's sample-data path, not market statistics.

## How the model works

**Billable capacity.** Two billable employee roles are required: *partners & senior
consultants* (`senior`) and *consultants* (`staff`). Any other role is non-billable overhead.
Billable hours per role = FTE on payroll × available hours per FTE per year ÷ 12 × utilisation.
FTE comes from the shared headcount engine (start month, yearly headcount growth), so a hire who
joins in month 7 bills nothing before month 7. Contractor hours are a separate input (hours per
month in year 1, growing yearly).

**Rate card.** Each hour is valued at its rate (senior, consultant, contractor bill rate); the
whole rate card rises once a year by one rate increase. This gives *fees at rate card*.

**Retainer vs project mix.** A share of billable hours is retainer work, billed at the rate card
less a retainer discount (the price of predictable volume). The rest is project work, billed at
the rate card × realisation (write-downs, over-runs, non-billable scope). Fee revenue =
retainer fees + project fees. Setting the retainer share to 0% or 100% gives a pure project or
pure retainer firm.

**Cost of delivery (COGS).** Billable staff payroll (salary + payroll taxes & benefits, with wage
growth), contractor cost per hour (grows with wage growth) and non-rebillable delivery costs
(% of fees: travel, project software, subcontracted extras). Gross profit is therefore the
delivery margin — the number partners manage to.

**Operating expenses.** Non-billable payroll (business development, operations & admin),
marketing & business development spend, software & tools per FTE (all FTE), office & rent,
other G&A.

**Working capital.** Receivable days (customer payment terms) apply to all fee revenue and are
the main cash driver of a services firm: the defaults use 45 days. No inventory. Payable days
apply to the whole cost of delivery, including billable payroll — the 15-day default
approximates salaries paid monthly in arrears plus contractor invoices. Everything else comes
from the shared engine (ADR-003).

**Capex.** Start-up capex in period 1 (equipment, fit-out), depreciated straight-line.

**Monthly vs annual.** Rates change yearly and hours follow average FTE, so annual columns show
exactly the sum of the months (tested).

## Services metrics table (Dashboard in Full, P&L sheet in Light)

Billable FTE at year end; billable hours split employees / contractors; available hours and
utilisation of billable employees; contractor share of hours; fees at rate card, fee revenue,
retainer fees and their share; realisation vs rate card across all work; effective rate per
billable hour; revenue per billable FTE; billable staff payroll and contractor cost, each per
billable hour (the **contractor vs employee cost** comparison); gross profit and margin;
year-end receivables. The challenger recomputes billable hours, billable FTE and retainer fees
in plain Python, on top of the standard P&L, cash and balance-sheet metrics.

## Default drivers by stage (Low / Base / High; one value = same in all scenarios)

| Driver | Unit | Order | Planning | Early | Growing | Established |
|---|---|---|---|---|---|---|
| Available hours per billable FTE per year | hours | — | 1,800 | 1,800 | 1,800 | 1,800 |
| Utilisation — partners & senior consultants | % | L ≤ B ≤ H | 50.0% / 55.0% / 60.0% | 50.0% / 55.0% / 60.0% | 50.0% / 55.0% / 60.0% | 50.0% / 55.0% / 60.0% |
| Utilisation — consultants | % | L ≤ B ≤ H | 68.0% / 75.0% / 80.0% | 68.0% / 75.0% / 80.0% | 68.0% / 75.0% / 80.0% | 68.0% / 75.0% / 80.0% |
| Contractor billable hours per month (year 1) | hours | L ≤ B ≤ H | 20 / 40 / 60 | 100 / 150 / 200 | 300 / 400 / 500 | 800 / 1000 / 1200 |
| Contractor hours growth per year | % | L ≤ B ≤ H | 10.0% / 20.0% / 30.0% | 10.0% / 20.0% / 30.0% | 10.0% / 20.0% / 30.0% | 10.0% / 20.0% / 30.0% |
| Hourly rate — partners & senior consultants | $ / hour | L ≤ B ≤ H | $300 / $350 / $400 | $300 / $350 / $400 | $300 / $350 / $400 | $300 / $350 / $400 |
| Hourly rate — consultants | $ / hour | L ≤ B ≤ H | $150 / $175 / $200 | $150 / $175 / $200 | $150 / $175 / $200 | $150 / $175 / $200 |
| Hourly rate billed for contractor hours | $ / hour | L ≤ B ≤ H | $140 / $150 / $165 | $140 / $150 / $165 | $140 / $150 / $165 | $140 / $150 / $165 |
| Rate card increase per year | % | L ≤ B ≤ H | 2.0% / 3.0% / 4.0% | 2.0% / 3.0% / 4.0% | 2.0% / 3.0% / 4.0% | 2.0% / 3.0% / 4.0% |
| Share of billable hours under retainers | % | — | 40.0% | 40.0% | 40.0% | 40.0% |
| Retainer discount vs rate card | % | L ≥ B ≥ H | 12.0% / 10.0% / 8.0% | 12.0% / 10.0% / 8.0% | 12.0% / 10.0% / 8.0% | 12.0% / 10.0% / 8.0% |
| Project realisation (billed ÷ rate-card value) | % | L ≤ B ≤ H | 88.0% / 92.0% / 95.0% | 88.0% / 92.0% / 95.0% | 88.0% / 92.0% / 95.0% | 88.0% / 92.0% / 95.0% |
| Contractor cost per hour (year 1) | $ / hour | L ≥ B ≥ H | $95 / $90 / $85 | $95 / $90 / $85 | $95 / $90 / $85 | $95 / $90 / $85 |
| Non-rebillable delivery costs, % of fees | % | L ≥ B ≥ H | 4.0% / 3.0% / 2.5% | 4.0% / 3.0% / 2.5% | 4.0% / 3.0% / 2.5% | 4.0% / 3.0% / 2.5% |
| Software & tools per FTE per month | $ | — | $200 | $200 | $200 | $200 |
| Marketing & business development per month | $ | — | $1,000 | $3,000 | $8,000 | $20,000 |
| Office & rent per month | $ | — | $0 | $2,500 | $8,000 | $25,000 |
| Other G&A per month (insurance, legal, accounting) | $ | — | $1,000 | $2,500 | $6,000 | $15,000 |
| Start-up capex (equipment, fit-out) | $ | — | $10,000 | $25,000 | $60,000 | $150,000 |
| Partners & senior consultants: headcount (FTE) | FTE | L ≤ B ≤ H | 1 | 2 | 4 | 10 |
| Partners & senior consultants: salary per FTE per year | $ | — | $140,000 | $150,000 | $160,000 | $175,000 |
| Partners & senior consultants: headcount growth per year | % | L ≤ B ≤ H | 0.0% | 25.0% | 20.0% | 10.0% |
| Partners & senior consultants: first month on payroll | month # | — | 1 | 1 | 1 | 1 |
| Consultants: headcount (FTE) | FTE | L ≤ B ≤ H | 1 | 3 | 12 | 40 |
| Consultants: salary per FTE per year | $ | — | $85,000 | $90,000 | $95,000 | $100,000 |
| Consultants: headcount growth per year | % | L ≤ B ≤ H | 100.0% | 50.0% | 30.0% | 10.0% |
| Consultants: first month on payroll | month # | — | 4 | 1 | 1 | 1 |
| Business development: headcount (FTE) | FTE | L ≤ B ≤ H | 0.5 | 1 | 2 | 5 |
| Business development: salary per FTE per year | $ | — | $70,000 | $80,000 | $85,000 | $90,000 |
| Business development: headcount growth per year | % | L ≤ B ≤ H | 100.0% | 0.0% | 20.0% | 10.0% |
| Business development: first month on payroll | month # | — | 7 | 1 | 1 | 1 |
| Operations & admin: headcount (FTE) | FTE | L ≤ B ≤ H | 0.5 | 1 | 3 | 8 |
| Operations & admin: salary per FTE per year | $ | — | $60,000 | $60,000 | $65,000 | $70,000 |
| Operations & admin: headcount growth per year | % | L ≤ B ≤ H | 0.0% | 0.0% | 15.0% | 10.0% |
| Operations & admin: first month on payroll | month # | — | 1 | 1 | 1 | 1 |
| Payroll taxes & benefits, % of salary | % | — | 20.0% | 20.0% | 20.0% | 20.0% |
| Wage growth per year | % | — | 3.0% | 3.0% | 3.0% | 3.0% |
| Equity raised at start | $ | — | $100,000 | $250,000 | $300,000 | $500,000 |
| Loan drawn at start | $ | — | $0 | $0 | $200,000 | $0 |
| Loan interest rate per year | % | — | 0.0% | 0.0% | 8.0% | 0.0% |
| Loan repayment term | years | — | 1 | 1 | 5 | 1 |
| Customer payment terms (receivable days) | days | — | 45 | 45 | 45 | 45 |
| Inventory held (days of COGS) | days | — | 0 | 0 | 0 | 0 |
| Supplier payment terms (payable days) | days | — | 15 | 15 | 15 | 15 |
| Depreciation period for capex | years | — | 5 | 5 | 5 | 5 |
| Income tax rate | % | — | 21.0% | 21.0% | 21.0% | 21.0% |

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Scenario | Revenue Y1 / Y2 / Y3 | Gross margin Y3 | EBITDA margin Y3 | Cash end Y3 |
|---|---|---|---|---|---|
| planning | Low | $388k / $605k / $957k | 29% | 2% | $41k |
| planning | Base | $543k / $850k / $1,350k | 47% | 28% | $550k |
| planning | High | $719k / $1,134k / $1,811k | 58% | 43% | $1,143k |
| early | Low | $1,108k / $1,513k / $2,093k | 24% | 9% | $226k |
| early | Base | $1,525k / $2,117k / $2,967k | 42% | 32% | $1,436k |
| early | High | $1,992k / $2,820k / $4,021k | 54% | 47% | $2,865k |
| growing | Low | $3,333k / $4,232k / $5,391k | 21% | 2% | ($86k) |
| growing | Base | $4,506k / $5,836k / $7,570k | 40% | 27% | $3,191k |
| growing | High | $5,791k / $7,661k / $10,147k | 53% | 43% | $6,952k |
| established | Low | $10,021k / $11,244k / $12,616k | 17% | -3% | ($1,755k) |
| established | Base | $13,420k / $15,374k / $17,628k | 37% | 23% | $6,990k |
| established | High | $17,087k / $20,011k / $23,519k | 51% | 40% | $16,611k |

The Low cases of *growing* and *established* dip below zero cash on purpose: utilisation, rates,
realisation, retainer discount, contractor cost and delivery costs all move together, so the
range is deliberately wide and the "Funding sufficient" check turns to WARN.

## Simplifications to review

1. Utilisation is one rate per billable role for the whole horizon — no ramp-up for new hires,
   no seasonality (holidays, August, December).
2. Available hours per FTE are the same for seniors and consultants.
3. Demand is assumed to absorb the capacity: revenue follows billable capacity, not a sales
   pipeline or client count.
4. Retainer and project work share the same rate card and the same AR days; retainers are not
   billed in advance (no deferred revenue).
5. Contractor cost grows with wage growth; contractor bill rate grows with the rate card.
6. Payable days apply to billable payroll as well as contractor and delivery costs.
7. No WIP / unbilled time: billed fees are recognised in the period the hours are worked.

## Questions for the CFO review

- Are the stage defaults sensible (available hours 1,800, utilisation 55% senior / 75%
  consultants, rates $350 / $175, realisation 92%, retainer discount 10%, 45 receivable days)?
- Should billable payroll sit in cost of delivery (current) or in operating expenses?
- Should retainers be billed in advance (deferred revenue, lower receivables)?
- Is a WIP / unbilled-time balance needed for the target customers (accountants, advisory
  firms), or are receivable days enough?
- Should new hires ramp up utilisation over their first months?
