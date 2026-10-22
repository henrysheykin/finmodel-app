---
slug: /calculators/services-project-price
title: Project Price Calculator: Fixed Fee From Hours and Margin | StartupModel
description: Enter estimated hours, your cost per hour, expenses, contingency and target margin. Get a fixed project price, the profit, the effective rate and what an overrun does to the margin.
keyword: project price calculator
template: services
related: [services-utilization-hourly-rate]
---

# Project price calculator: a fixed fee from hours and margin

A fixed fee is a bet on your estimate. Price it from the hours you expect, what an hour costs you, the expenses of the job, a cushion for surprises and the margin you want to keep. Enter your numbers; the price, the profit and the effect of an overrun update as you type.

```inputs
- key: hours
  label: Estimated hours
  unit: hours
  default: 120
  min: 0
  max: 100000
  step: 1
  format: int
  hint: Your honest estimate of the work, before any cushion.
- key: cost_rate
  label: Cost per hour
  unit: $
  default: 55
  min: 0
  max: 10000
  step: 1
  format: money
  hint: What an hour of the people doing the work costs you, with payroll costs and overhead.
- key: expenses
  label: Direct expenses
  unit: $
  default: 1500
  min: 0
  max: 100000000
  step: 100
  format: money
  hint: Software, travel, subcontractors and anything bought for this job.
- key: contingency
  label: Contingency on the hours
  unit: "%"
  default: 10
  min: 0
  max: 200
  step: 1
  format: percent
  hint: Extra time you add for revisions and surprises. Your assumption.
- key: margin
  label: Profit margin you want
  unit: "%"
  default: 30
  min: 0
  max: 90
  step: 1
  format: percent
  hint: Profit as a share of the price. Your own target.
- key: overrun
  label: Overrun to test
  unit: "%"
  default: 20
  min: 0
  max: 300
  step: 5
  format: percent
  hint: How much longer than your estimate the work takes, for the stress test.
```

```outputs
- key: hours_plan
  label: Hours in the price
  formula: hours * (1 + contingency / 100)
  format: number1
- key: cost
  label: Cost of delivering the project
  formula: hours_plan * cost_rate + expenses
  format: money
- key: price
  label: Project price
  formula: cost / (1 - margin / 100)
  format: money
  highlight: true
- key: profit
  label: Profit if it goes to plan
  formula: price - cost
  format: money
- key: rate_eff
  label: Price per hour of work, excluding expenses
  formula: (price - expenses) / hours_plan
  format: money2
  note: Compare this with the rate you charge on time-and-materials work.
- key: profit_over
  label: Profit if the work runs over
  formula: price - (hours * (1 + overrun / 100) * cost_rate + expenses)
  format: money
  note: Measured against the hours you estimated, not the hours in the price.
- key: margin_over
  label: Margin if the work runs over
  formula: profit_over / price * 100
  format: percent
```

```table
title: Price at different target margins
input: margin
values: 20, 25, 30, 35, 40
outputs: price, profit, rate_eff
```

```examples
- name: The starting numbers
  inputs: hours=120, cost_rate=55, expenses=1500, contingency=10, margin=30, overrun=20
  expect: hours_plan=132, cost=8760, price=12514.285714, profit=3754.285714, rate_eff=83.441558, profit_over=3094.285714, margin_over=24.726027
- name: A short design job
  inputs: hours=40, cost_rate=48, expenses=300, contingency=15, margin=35, overrun=50
  expect: hours_plan=46, cost=2508, price=3858.461538, profit=1350.461538, rate_eff=77.35786, profit_over=678.461538, margin_over=17.583732
- name: A long project with a large overrun
  inputs: hours=400, cost_rate=62, expenses=8000, contingency=5, margin=25, overrun=40
  expect: hours_plan=420, cost=34040, price=45386.666667, profit=11346.666667, rate_eff=89.015873, profit_over=2666.666667, margin_over=5.875441
- name: An empty project has no margin
  inputs: hours=0, cost_rate=55, expenses=0, contingency=10, margin=30, overrun=20
  expect: hours_plan=0, cost=0, price=0, profit=0, rate_eff=—, profit_over=0, margin_over=—
```

## How the project price is built

A fixed fee has to cover the cost of doing the work and still leave the margin you want. The calculator builds it from the cost up:

1. **Hours in the price** = estimated hours × (1 + contingency).
2. **Cost of the project** = hours in the price × cost per hour + direct expenses.
3. **Price** = cost ÷ (1 − target margin).

The last step matters. A margin is a share of the price, so adding the margin to the cost (cost × 1.30 for 30%) gives a price that earns less than the margin you wanted. Dividing by (1 − margin) gets it right.

With the starting numbers (example values, not benchmarks) an estimate of 120 hours plus 10% contingency is 132 hours. At $55 an hour, with $1,500 of expenses added, the cost is $8,760. At a margin of 30% the price is $12,514 and the profit if everything goes to plan is $3,754. Taking out the expenses, the price per hour of work is $83.44, which you can compare with the rate you charge when you bill by the hour.

## The overrun test

An estimate is a guess, and fixed fees turn every hour over the estimate into your cost. The last two results test that. If the work takes 20% longer than your estimate of 120 hours, the cost rises to 144 hours at $55 plus the expenses, the profit drops to $3,094, and the margin falls from 30% to 24.7%. The contingency of 10% absorbs half of that overrun, which is why it is in the price.

The second example, a short design job of 40 hours, shows a larger effect. At a 50% overrun, the profit drops from $1,350 to $678 and the margin to 17.6%. The third, a long project of 400 hours with a 5% contingency, shows the danger of a thin cushion: a 40% overrun leaves a profit of $2,667, a margin of only 5.9%.

## How to read the result

Use the price as a floor for your quote, not the quote itself. What the client will pay depends on the value of the result to them, on what competitors charge and on how much risk you take. The calculator tells you what the price has to be for the work to earn your margin; it does not tell you what you can ask. If you cannot charge that price, change the scope, not the estimate: a price based on fewer hours than you really need is a loss you have agreed to in advance.

Use the overrun line to decide how much contingency the job deserves. Work you have done many times can carry a small contingency. New kinds of work, unclear scope or a difficult client deserve a bigger one, and a clause that makes extra requests billable.

## Typical mistakes

- **Estimating only the doing.** Meetings, revisions, project management and handover take time.
- **Pricing at the wage rate.** The cost per hour should include payroll costs and a share of overhead, not just the wage.
- **Forgetting expenses and subcontractors.** Software, travel and outside help belong in the cost.
- **Adding the margin to the cost.** Divide by (1 − margin) as the calculator does.
- **Not recording actual hours.** Without actuals, next year's estimates are guesses again.

## What this calculator cannot do

It prices one project in isolation. It does not know whether you have the people free, how the project's payments line up with your costs, or how a portfolio of projects behaves over months. A financial model puts projects, utilization and cash into a monthly forecast, shows when clients pay, and runs Low / Base / High scenarios, with statements and a Checks sheet you can share with a lender. The [utilization and hourly rate calculator](/calculators/services-utilization-hourly-rate) shows what the same logic means for the whole team.

## FAQ {#faq}

### Should I quote a fixed fee or bill by the hour?

A fixed fee suits work with a clear scope; hourly billing suits work that is hard to define. This calculator helps you price the first and test the risk in it.

### What contingency should I use?

Use your own record. Compare past estimates with the hours you actually spent and set the contingency to cover the typical difference.

### Does the price include sales tax?

No. It is the price before any sales tax or VAT.

### Why does the margin show a dash?

If the hours and the expenses are both zero, the price is zero and a margin cannot be calculated.
