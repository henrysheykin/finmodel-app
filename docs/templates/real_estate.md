# Real estate (rental property) template — assumption memo

Template key `real_estate` (`engine/templates/real_estate.py`; Returns sheet `engine/returns.py`, ADR-011).
Sample: `samples/real_estate-full.xlsx` (stage *early*: a 10-unit building bought for $1.85M, Full tier,
monthly, 3 years; rebuild with `python scripts/build_samples.py real_estate`).

Status: **awaiting CFO review (HUMAN_TODO R1)**. All defaults are illustrative starting points for the
wizard's sample-data path, not market statistics.

For investors buying and holding a rental property (houses, small multifamily, apartment buildings): one
purchase at the start, held for the plan horizon, sold at its end.

## How the model works

**Rent roll.** Units × average rent per unit per month (rises once a year by rent growth) = gross
potential rent; less vacancy & credit loss (% of potential rent); plus other income per unit (parking,
laundry, fees), also reduced by vacancy. Revenue = effective gross income.

**Costs.** Direct property costs (cost of sales): repairs & maintenance (% of collected rent) and
owner-paid utilities & common areas. Operating expenses: property tax (% of purchase price per year),
insurance per unit, property management (% of revenue), legal, accounting & other G&A. Fixed costs rise
with operating cost inflation. No staff by default (a role can be added). EBITDA = **net operating income
(NOI)**.

**Purchase, land and depreciation.** Month 1 capex = price + closing costs. The land share of the price is
carried at cost and never depreciated; building and closing costs are depreciated straight-line over the
depreciation period (default 27 years — the input takes whole years; US residential is 27.5). A capital
reserve per unit per year (roofs, appliances, unit turns) is spent every period and depreciated the same
way.

**Mortgage.** Loan drawn at purchase, repaid as an annuity (level payment from Excel `PMT`; interest on
the balance at the start of each period). The amortisation schedule is in the period grid (opening
balance, drawdown, interest, principal, payment, closing balance). Equity covers the rest of the purchase
plus a cash cushion.

**Returns sheet (both tiers).** Year 0 = purchase (all-in cost; levered: less the loan). Years 1..H = NOI −
capital reserves; levered also pays interest and principal. Sale at the end of year H = next-year NOI
(final-year NOI × (1 + rent growth)) ÷ exit cap rate, less selling costs; levered repays the loan
balance left at that date. Results: unlevered and levered IRR, NPV at the discount rate, total profit,
multiple of money, going-in cap rate, DSCR and cash-on-cash by year. Cash flows are **before income tax**.
IRR shows "n/a" when it is not a single meaningful number: the flows change sign more than once (e.g. the
sale does not repay the loan, so equity pays in at the end) or they return less than 25% of the money put
in (a near-total loss).
The challenger recomputes every cell in plain Python (IRR within 0.01 pp); the Checks sheet ties NOI to
EBITDA, the purchase to capex, the loan to zero at sale, and both IRRs back to an NPV of zero, and warns
when DSCR falls below 1.0x.

## Property metrics table (Dashboard in Full, P&L sheet in Light)

Average rent per unit, gross potential rent, vacancy, economic occupancy, revenue, NOI, NOI margin,
operating expense ratio, NOI per unit, NOI ÷ purchase price, debt service, DSCR, year-end loan and loan ÷
price. Potential rent, vacancy and average rent are recomputed by the independent challenger.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Property | Case | NOI Y1 | Going-in cap | DSCR Y1 | Unlevered IRR | Levered IRR |
|---|---|---|---:|---:|---:|---:|---:|
| planning | fourplex, $880k | Low / Base / High | $53k / $61k / $66k | 6.0% / 6.9% / 7.6% | 1.23 / 1.40 / 1.54 | -1.1% / 7.5% / 15.1% | -16.7% / 9.2% / 27.1% |
| early | 10 units, $1.85M | Low / Base / High | $108k / $125k / $140k | 5.9% / 6.8% / 7.5% | 1.19 / 1.38 / 1.53 | -2.3% / 6.9% / 15.0% | -21.3% / 7.7% / 27.1% |
| growing | 30 units, $5.2M | Low / Base / High | $306k / $356k / $398k | 5.9% / 6.8% / 7.7% | 1.19 / 1.39 / 1.55 | -2.1% / 7.3% / 15.6% | -20.6% / 8.8% / 28.5% |
| established | 80 units, $13.6M | Low / Base / High | $809k / $941k / $1,052k | 5.9% / 6.9% / 7.7% | 1.21 / 1.40 / 1.57 | -1.7% / 7.7% / 16.0% | -18.9% / 9.8% / 29.4% |

Loans are 65% of the price at 6.5% over 30 years; exit cap rates 7.25% / 6.75% / 6.25%. A 3-year hold
carries the full closing (3%) and selling (5–6%) costs, so returns are modest; on a 5-year horizon the
Base levered IRR is about 10–12% (10.3–11.6% by stage). The Low case stacks every pessimistic value (lower rent and growth,
higher vacancy, repairs and inflation, a higher exit cap) and shows a loss — a stress case, still funded.

## Simplifications to review

1. One purchase at the start and one sale at the horizon; no refinancing, no value-add renovation phase,
   no lease-up of a vacant building.
2. Average rent for all units (no unit-mix rent roll); vacancy is one rate for the whole plan.
3. Returns are before income tax; depreciation recapture and capital-gains tax on the sale are not
   modelled. The P&L still charges income tax on taxable profit.
4. Loan amount is an input (LTV is shown, not set); no interest-only period, no loan fees.
5. The equity cushion beyond the purchase stays in the business as cash and is not part of the levered
   IRR (equity invested = purchase cost − loan).
6. Exit value uses next-year NOI grown at rent growth (cost inflation is not projected one more year).

## Questions for the CFO review

1. Pre-tax IRR as the headline, or add an after-tax levered IRR (needs capital-gains and recapture rates)?
2. Should LTV (with a DSCR-based loan cap) be the input instead of the loan amount?
3. Are 27-year depreciation and a 20% land share sensible defaults outside the US?
4. Should the default horizon for real estate be 5 years (3-year holds look poor after transaction costs)?
5. Is 8% management and 5–7% repairs right for small owners who self-manage?
6. Add an interest-only period or a refinance at year N?
