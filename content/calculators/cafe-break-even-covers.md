---
slug: /calculators/cafe-break-even-covers
title: Cafe Break-Even Calculator: Customers Needed Per Day | StartupModel
description: Find how many customers a day a cafe or restaurant needs to cover its fixed costs, from rent and wages, average spend and the costs that rise with sales.
keyword: break even calculator restaurant
template: cafe
related: [cafe-menu-price, cafe-food-cost-percent]
guide: /guides/restaurant-break-even-analysis
---

# Cafe break-even calculator: customers per day

A cafe breaks even on the day its sales, less the costs that rise with sales, cover its fixed costs. This calculator turns that into a number you can watch on the floor: how many customers you need each day. Enter your costs and your average spend; the results update as you type.

```inputs
- key: fixed
  label: Fixed costs per month
  unit: $
  default: 28000
  min: 0
  max: 10000000
  step: 100
  format: money
  hint: Rent, wages, utilities, insurance, software, loan interest. An example value.
- key: check
  label: Average spend per customer
  unit: $
  default: 14
  min: 0
  max: 1000
  step: 0.25
  format: money2
  hint: Total sales divided by the number of paying customers.
- key: food_pct
  label: Food and drink cost
  unit: "%"
  default: 30
  min: 0
  max: 100
  step: 0.5
  format: percent
  hint: Ingredient cost as a share of sales. Your assumption.
- key: other_pct
  label: Other costs that rise with sales
  unit: "%"
  default: 8
  min: 0
  max: 100
  step: 0.5
  format: percent
  hint: Card fees, packaging, delivery commissions. Your assumption.
- key: days
  label: Days open per month
  unit: days
  default: 26
  min: 1
  max: 31
  step: 1
  format: int
- key: now
  label: Customers per day today
  unit: per day
  default: 150
  min: 0
  max: 10000
  step: 1
  format: int
  hint: What you serve now, or expect to serve once open.
```

```outputs
- key: contrib_pct
  label: Contribution margin
  formula: 100 - food_pct - other_pct
  format: percent
  note: What is left of each sales dollar after the costs that rise with sales.
- key: contrib
  label: Contribution per customer
  formula: check * contrib_pct / 100
  format: money2
- key: be_month
  label: Break-even customers per month
  formula: fixed / max(contrib, 0)
  format: int
- key: be_day
  label: Customers needed per day
  formula: be_month / days
  format: number1
  highlight: true
  note: Round up in practice.
- key: be_sales_month
  label: Break-even sales per month
  formula: fixed / max(contrib_pct, 0) * 100
  format: money
- key: be_sales_day
  label: Break-even sales per day
  formula: be_sales_month / days
  format: money
- key: safety
  label: Margin of safety today
  formula: (now - be_day) / now * 100
  format: percent
  note: How far today's customers are above break-even; negative means below.
- key: profit_now
  label: Profit per month at today's customers
  formula: contrib * now * days - fixed
  format: money
  note: Before interest on debt and tax if those are not in your fixed costs.
```

```table
title: Customers needed per day at different average spends
input: check
relative: -10, -5, 0, 5, 10
outputs: be_day, profit_now
```

```examples
- name: The starting numbers
  inputs: fixed=28000, check=14, food_pct=30, other_pct=8, days=26, now=150
  expect: contrib_pct=62, contrib=8.68, be_month=3225.806452, be_day=124.069479, be_sales_month=45161.290323, be_sales_day=1736.972705, safety=17.287014, profit_now=5852
- name: A smaller place with a lower spend
  inputs: fixed=12000, check=6.5, food_pct=28, other_pct=7, days=30, now=120
  expect: contrib_pct=65, contrib=4.225, be_month=2840.236686, be_day=94.674556, be_sales_month=18461.538462, be_sales_day=615.384615, safety=21.104537, profit_now=3210
- name: Costs that rise with sales take everything
  inputs: fixed=10000, check=12, food_pct=60, other_pct=40, days=26, now=100
  expect: contrib_pct=0, contrib=0, be_month=—, be_day=—, be_sales_month=—, be_sales_day=—, safety=—, profit_now=-10000
- name: Costs above sales
  inputs: fixed=10000, check=12, food_pct=70, other_pct=40, days=26, now=100
  expect: contrib_pct=-10, contrib=-1.2, be_month=—, be_day=—, be_sales_month=—, be_sales_day=—, safety=—, profit_now=-13120
- name: Nobody comes in today
  inputs: fixed=28000, check=14, food_pct=30, other_pct=8, days=26, now=0
  expect: contrib_pct=62, contrib=8.68, be_month=3225.806452, be_day=124.069479, be_sales_month=45161.290323, be_sales_day=1736.972705, safety=—, profit_now=-28000
```

## How break-even works

The costs of a cafe come in two kinds. **Fixed costs** are paid whether you serve ten customers or a hundred: rent, the core rota, utilities, insurance, software and loan interest. **Costs that rise with sales** are the ingredients, card fees, packaging and any commission on delivery orders.

Each customer brings in an average spend. Take away the costs that rise with sales and what is left is the **contribution** that customer makes towards the fixed costs. The calculator works in three steps:

1. **Contribution margin** = 100% − food and drink cost % − other costs %.
2. **Contribution per customer** = average spend × contribution margin.
3. **Break-even customers** = fixed costs ÷ contribution per customer, divided by the days you are open for the daily figure.

With the starting numbers (example values, not benchmarks) the contribution margin is 62%, each customer contributes $8.68, and the cafe needs about 124 customers a day, or $1,737 in sales a day, to cover $28,000 of fixed costs. At 150 customers a day it clears break-even by 17.3% and makes about $5,852 a month before interest and tax.

If costs that rise with sales reach 100% of sales, no number of customers breaks even, and the results show a dash instead of a figure.

## Reading the sensitivity table

The table moves the average spend up and down from your number. The effect is larger than most people expect: a small rise in spend lowers the customers you need and raises the profit at today's traffic. This is why the menu price and the mix of what people order matter as much as footfall. The [menu price calculator](/calculators/cafe-menu-price) and the [food cost percentage calculator](/calculators/cafe-food-cost-percent) work on that side.

## What this calculator does not tell you

- **Cash.** Break-even in the profit sense is not the same as the point where the business stops using cash. Opening costs, stock, loan repayments and the weeks before you reach steady trade all use cash that this calculator does not see. The [break-even guide](/guides/restaurant-break-even-analysis) explains the cash view.
- **Ramp-up.** Customers rarely arrive at their steady level on day one. A model with monthly figures shows how long the climb takes and how much funding it needs.
- **Busy and quiet days.** The calculator uses one average. A weekend and a wet Tuesday are different businesses.
- **Staffing steps.** Fixed costs are assumed flat. In reality you add hours when you get busy.

## FAQ {#faq}

### What is a cover?

A cover is one customer served, counted once however many items they buy. For a cafe it is one paying customer or one order.

### What should I include in fixed costs?

Everything you must pay whatever the sales: rent, the staff you need on the rota, utilities, insurance, software, accounting and loan interest. Leave out ingredients and the other costs that rise with sales, which have their own fields.

### Why does the result show a dash?

The calculation cannot be done. This happens when the costs that rise with sales reach or pass 100% of sales, or when the average spend is zero: each extra customer then adds nothing towards the fixed costs, so no number of customers breaks even.

### How do I lower the break-even point?

Three levers: raise the average spend, lower the costs that rise with sales, or lower the fixed costs. The sensitivity table shows the first; change the others in the fields and watch the headline figure.
