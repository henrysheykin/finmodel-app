# Fitness studio / gym template — assumption memo

Template key `fitness` (`engine/templates/fitness.py`). Sample: `samples/fitness-full.xlsx` (stage *planning*:
a new 4,000 sq ft studio with a 120-member presale, Full tier, monthly, 3 years; rebuild with
`python scripts/build_samples.py fitness`).

Status: **awaiting CFO review (HUMAN_TODO R1)**. All defaults are illustrative starting points for the
wizard's sample-data path, not market statistics.

For boutique studios, independent gyms, CrossFit boxes, yoga and pilates studios with memberships.

## How the model works

**Member base.** Opens with *members at start* (the presale for a new studio, the current base for a
trading one). Each period: new members from marketing (spend ÷ cost per lead × leads that join) plus
referrals & walk-ins; a monthly share of the opening base cancels. The base never exceeds the studio's
capacity; joins above it are counted as *lost to the capacity limit* — the signal to add classes, space
or a second site. Annual models compound the monthly cancellation rate over 12 months and assume the
year's new members join mid-year (the same convention as the SaaS template), so annual and monthly
versions agree closely but not to the dollar.

**Revenue.** Membership fees on the average base; a joining fee per member who actually joins;
personal training (members buying PT × sessions per month × price per session); retail & drinks per
member. Membership fee, PT price and retail rise once a year with the price increase.

**Cost of sales.** Group-class instructors paid per class (classes per week × 52 ÷ 12, with wage
growth), trainer payouts (% of PT revenue) and the cost of retail & drinks.

**Operating expenses.** Staff payroll (studio manager, front desk & sales, any other role), marketing
(grows yearly), rent, utilities, equipment maintenance & cleaning, booking software & payment fees
(% of revenue), insurance & other G&A.

**Capex and funding.** Fit-out & equipment in month 1, depreciated over 7 years. Equity and an optional
loan at the start. Members pay up front, so receivable days are 0; a few days of retail stock.

## Membership metrics table (Dashboard in Full, P&L sheet in Light)

Members at year end, new members, cancellations, joins lost to capacity, capacity used, membership fees
per month at year end, revenue split, marketing cost per new member, gross margin, member lifetime value
(fee × gross margin ÷ monthly cancellation rate), EBITDA margin and revenue per square foot. Members, new
members and lost joins are recomputed by the independent challenger.

## What the defaults produce (plain-Python reference, 3 years, monthly)

| Stage | Case | Revenue Y1 | Revenue Y3 | EBITDA margin Y1 → Y3 | Members Y3 / capacity | Lowest cash |
|---|---|---:|---:|---:|---:|---:|
| planning | Low | $256,826 | $515,887 | -122% → -21% | 385 / 450 | $-449,314 |
| planning | Base | $393,075 | $722,638 | -47% → 11% | 450 / 450 | $20,107 |
| planning | High | $570,691 | $822,654 | -3% → 22% | 450 / 450 | $188,487 |
| early | Low | $476,942 | $731,469 | -49% → -5% | 542 / 550 | $-274,207 |
| early | Base | $668,658 | $881,509 | -8% → 12% | 550 / 550 | $49,792 |
| early | High | $848,338 | $1,003,717 | 14% → 22% | 550 / 550 | $198,387 |
| growing | Low | $965,252 | $1,367,835 | -44% → -11% | 1,117 / 1,200 | $-711,712 |
| growing | Base | $1,295,390 | $1,766,780 | -9% → 12% | 1,200 / 1,200 | $40,958 |
| growing | High | $1,666,706 | $2,030,362 | 14% → 24% | 1,200 / 1,200 | $347,171 |
| established | Low | $1,979,094 | $2,402,169 | -15% → -1% | 1,938 / 2,000 | $-407,281 |
| established | Base | $2,604,808 | $2,938,396 | 11% → 16% | 2,000 / 2,000 | $281,960 |
| established | High | $3,069,304 | $3,383,937 | 24% → 27% | 2,000 / 2,000 | $640,133 |

The Low case stacks every pessimistic value (higher cancellations, lower conversion and prices, higher
instructor cost), so it is a stress case; it runs out of cash in every stage and the Checks sheet flags the
funding gap. Base cases are funded throughout.

## Simplifications to review

1. One membership tier and one price; no class packs, annual prepay discounts or freezes.
2. No seasonality (January sign-ups, summer slowdown); monthly cancellation rate is constant.
3. Personal training is sold to a fixed share of members; trainers are paid a share of PT revenue (no
   salaried trainers unless added as a role).
4. Instructor cost does not change with membership — classes per week is an input.
5. No equipment replacement capex inside the horizon; maintenance is an operating cost.

## Questions for the CFO review

1. Are monthly cancellation rates of 4.5–6 % (Base) a sensible default for independent studios?
2. Should the default include January seasonality for sign-ups?
3. Is 7-year depreciation right for fit-out and equipment combined?
4. Should the membership fee have a presale discount in the first months for a new studio?
5. Is revenue per square foot the right density metric, or members per 1,000 sq ft?
