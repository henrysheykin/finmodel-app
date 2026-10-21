---
slug: /calculators/saas-mrr-growth-churn
title: MRR Growth and Churn Calculator: MRR After N Months | StartupModel
description: Enter your MRR today, new MRR per month, churn and expansion. See net MRR change, growth this month, MRR and ARR after N months, the gap to a target and the level MRR levels off at.
keyword: MRR growth calculator
template: saas
related: [saas-ltv-cac, saas-runway]
---

# MRR growth and churn calculator

Monthly recurring revenue grows when new subscriptions and upgrades arrive faster than cancellations take revenue away. Enter your MRR today and the monthly flows; the calculator rolls the revenue forward month by month and shows where MRR stands after the number of months you choose.

```inputs
- key: mrr0
  label: MRR today
  unit: $
  default: 20000
  min: 0
  max: 10000000
  step: 100
  format: money
  hint: Monthly recurring revenue from all paying customers now.
- key: new
  label: New MRR added each month
  unit: $
  default: 2500
  min: 0
  max: 10000000
  step: 50
  format: money
  hint: MRR from newly won customers, as a fixed amount every month.
- key: churn
  label: Churned MRR per month
  unit: "%"
  default: 3
  min: 0
  max: 30
  step: 0.1
  format: percent
  hint: The share of MRR lost to cancellations and downgrades each month.
- key: expansion
  label: Expansion MRR per month
  unit: "%"
  default: 1
  min: 0
  max: 20
  step: 0.1
  format: percent
  hint: Upgrades and extra seats from existing customers, as a share of MRR.
- key: months
  label: Months to look ahead
  unit: months
  default: 12
  min: 1
  max: 120
  step: 1
  format: int
- key: target
  label: MRR target
  unit: $
  default: 50000
  min: 0
  max: 100000000
  step: 500
  format: money
  hint: The MRR you want to reach.
```

```outputs
- key: net_churn
  label: Net churn per month
  formula: churn - expansion
  format: percent
  note: Churn less expansion; negative means existing customers grow on their own.
- key: change_now
  label: Net new MRR this month
  formula: new - mrr0 * net_churn / 100
  format: money
- key: growth_now
  label: MRR growth this month
  formula: change_now / mrr0 * 100
  format: percent
- key: mrr_n
  label: MRR after the chosen months
  formula: if(net_churn == 0, mrr0 + new * months, mrr0 * (1 - net_churn / 100) ^ months + new * (1 - (1 - net_churn / 100) ^ months) / (net_churn / 100))
  format: money
  highlight: true
- key: arr_n
  label: Annualised run rate at that point
  formula: mrr_n * 12
  format: money
- key: gap
  label: Gap to the MRR target at that point
  formula: target - mrr_n
  format: money
  note: Negative means you are past the target.
- key: steady
  label: MRR where growth stops
  formula: new / max(net_churn / 100, 0)
  format: money
  note: With constant new MRR and positive net churn, MRR levels off here.
```

```table
title: MRR as the months pass
input: months
values: 3, 6, 12, 24, 36
outputs: mrr_n, arr_n, gap
```

```examples
- name: The starting numbers
  inputs: mrr0=20000, new=2500, churn=3, expansion=1, months=12, target=50000
  expect: net_churn=2, change_now=2100, growth_now=10.5, mrr_n=42604.744008, arr_n=511256.928094, gap=7395.255992, steady=125000
- name: No new customers and rising churn
  inputs: mrr0=30000, new=0, churn=5, expansion=0, months=12, target=30000
  expect: net_churn=5, change_now=-1500, growth_now=-5, mrr_n=16210.80263, arr_n=194529.631559, gap=13789.19737, steady=0
- name: Expansion matches churn
  inputs: mrr0=10000, new=1000, churn=2, expansion=2, months=24, target=40000
  expect: net_churn=0, change_now=1000, growth_now=10, mrr_n=34000, arr_n=408000, gap=6000, steady=—
- name: Expansion beats churn
  inputs: mrr0=15000, new=1200, churn=1.5, expansion=3, months=18, target=60000
  expect: net_churn=-1.5, change_now=1425, growth_now=9.5, mrr_n=44197.360404, arr_n=530368.324849, gap=15802.639596, steady=—
- name: Starting from zero
  inputs: mrr0=0, new=2000, churn=4, expansion=0, months=12, target=20000
  expect: net_churn=4, change_now=2000, growth_now=—, mrr_n=19364.512134, arr_n=232374.145602, gap=635.487866, steady=50000
```

## How the MRR roll-forward works

Each month the same three things happen to monthly recurring revenue:

1. **Churn** takes away a share of the MRR you had at the start of the month.
2. **Expansion** adds a share back, from upgrades and extra seats.
3. **New MRR** from newly won customers arrives as a fixed amount.

Churn less expansion is the **net churn**. Next month's MRR is this month's MRR times (1 − net churn), plus the new MRR. The calculator repeats this for the number of months you choose and shows the result in closed form, so the answer is the same as if you had filled in a spreadsheet row by row.

With the starting numbers (example values, not benchmarks) MRR is $20,000, new MRR is $2,500 a month, churn is 3% and expansion 1%, so net churn is 2.0%. In the first month the business adds $2,100 net, which is 10.5% growth. After 12 months MRR is $42,605. That is an annualised run rate of $511,257, and it is still $7,395 short of the $50,000 target. Because the churn is a share of a growing base, the gains slow: with these numbers MRR would level off at $125,000, which is the new MRR divided by the net churn rate.

## Reading the table instead of a "months to target" number

The calculator does not solve for the month at which you reach a target, because the answer needs a logarithm and the page keeps to simple arithmetic. The table does the job by eye: it shows MRR, run rate and the gap to your target at 3, 6, 12, 24 and 36 months. Where the gap changes sign, you cross the target. Change the months field to narrow it down.

## How to read the result

Look at three lines together. **Net churn** shows whether the existing base is shrinking or growing by itself; if expansion is higher than churn it is negative, and every new dollar of MRR compounds. **MRR growth this month** compares the new MRR with what churn takes away. **MRR where growth stops** shows the ceiling that a constant flow of new customers can support at your churn: a business with high churn needs ever more new MRR just to stand still.

Other cases on this page show the extremes. With no new customers and 5% churn, $30,000 of MRR falls to $16,211 in 12 months. When expansion equals churn, MRR grows by exactly the new MRR each month, so $10,000 with $1,000 of new MRR reaches $34,000 in 24 months, and there is no level where growth stops, so that line shows a dash.

## Typical mistakes

- **Mixing MRR and revenue.** MRR counts recurring subscriptions only. One-off setup fees and usage spikes belong elsewhere.
- **Treating new MRR as constant for years.** A fixed monthly amount is a simplification. In practice it depends on spend and on how well the sales process scales.
- **Using logo churn for MRR churn.** If your biggest customers cancel, revenue churn is higher than customer churn.
- **Forgetting downgrades.** Include them in churn or net them in expansion, but be consistent.
- **Reading far-out months as a forecast.** Thirty-six months of a constant assumption is an illustration.

## What this calculator cannot do

It rolls one revenue line forward with constant assumptions. It cannot link new MRR to the marketing spend that produces it, hold prices or plans apart, or show what the growth costs in cash. A financial model does: monthly revenue by plan, churn and expansion as separate drivers, costs and headcount, cash and the balance sheet, and Low / Base / High scenarios so you can see what happens if churn is worse than planned. It also carries a Checks sheet and statements an investor or lender can read. The [LTV to CAC calculator](/calculators/saas-ltv-cac) covers the cost of winning customers, and the [runway calculator](/calculators/saas-runway) the cash.

## FAQ {#faq}

### What is net churn?

Net churn is the share of MRR lost to cancellations and downgrades, less the share gained from upgrades by existing customers. If it is negative, the existing customers grow without any new sales.

### Why is there no "months to target" result?

Solving for the month needs a logarithm, which the page does not use. Use the sensitivity table, or change the months field until the gap flips from positive to negative.

### Is ARR just MRR times twelve?

In this calculator, yes. It is the annualised run rate at that point, not the revenue you will book over the next year.

### What does the dash on "MRR where growth stops" mean?

If net churn is zero or negative, MRR keeps growing and never levels off, so there is no such level.
