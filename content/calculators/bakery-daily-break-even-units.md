---
slug: /calculators/bakery-daily-break-even-units
title: Bakery Break-Even Calculator: Units to Sell Per Day | StartupModel
description: Enter fixed costs, the average price and cost per unit, and the share left unsold. Get the units a bakery must sell each day to break even, the daily sales and the monthly profit now.
keyword: bakery break even calculator
template: bakery
related: [bakery-recipe-cost-unit-price]
---

# Bakery break-even calculator: units per day

A bakery bakes before it knows what it will sell, so some of what it makes is lost. Each unit sold therefore carries the cost of the units that were not. Enter your fixed costs, the average price and cost of a unit, and the share that goes unsold; the calculator shows the units you must sell every day to cover your costs.

```inputs
- key: fixed
  label: Fixed costs per month
  unit: $
  default: 21000
  min: 0
  max: 100000000
  step: 250
  format: money
  hint: Rent, bakers and counter staff on the rota, utilities, insurance, equipment loan, software.
- key: price
  label: Average price per unit sold
  unit: $
  default: 3.9
  min: 0
  max: 1000
  step: 0.05
  format: money2
  hint: Blend the counter and wholesale prices, weighted by the units you sell at each.
- key: unit_cost
  label: Ingredient and packaging cost per unit made
  unit: $
  default: 1.35
  min: 0
  max: 1000
  step: 0.05
  format: money2
- key: unsold
  label: Units made but not sold
  unit: "%"
  default: 6
  min: 0
  max: 95
  step: 0.5
  format: percent
  hint: Units made that are thrown away, given away or sold at a loss. Your assumption.
- key: days
  label: Days open per month
  unit: days
  default: 26
  min: 1
  max: 31
  step: 1
  format: int
- key: now
  label: Units sold per day today
  default: 520
  min: 0
  max: 1000000
  step: 5
  format: int
```

```outputs
- key: cost_sold
  label: Cost of each unit sold
  formula: unit_cost / (1 - unsold / 100)
  format: money2
  note: The cost of a unit made, spread over the units that sell.
- key: contrib
  label: Contribution per unit sold
  formula: price - cost_sold
  format: money2
- key: be_month
  label: Units to sell per month to break even
  formula: fixed / max(contrib, 0)
  format: int
- key: be_day
  label: Units to sell per day to break even
  formula: be_month / days
  format: int
  highlight: true
  note: Round up in practice.
- key: made_day
  label: Units to bake per day at break-even
  formula: be_day / (1 - unsold / 100)
  format: int
- key: be_sales_day
  label: Sales per day at break-even
  formula: be_day * price
  format: money
- key: safety
  label: Margin of safety today
  formula: (now - be_day) / now * 100
  format: percent
- key: profit_now
  label: Profit per month at today's volume
  formula: contrib * now * days - fixed
  format: money
  note: Before tax and before the owner's pay if it is not in the fixed costs.
```

```table
title: Units to sell at different prices
input: price
relative: -10, -5, 0, 5, 10
outputs: contrib, be_day, profit_now
```

```examples
- name: The starting numbers
  inputs: fixed=21000, price=3.9, unit_cost=1.35, unsold=6, days=26, now=520
  expect: cost_sold=1.43617, contrib=2.46383, be_month=8523.316062, be_day=327.819849, made_day=348.74452, be_sales_day=1278.497409, safety=36.957721, profit_now=12310.978723
- name: A small neighbourhood bakery
  inputs: fixed=12000, price=4.6, unit_cost=1.5, unsold=10, days=26, now=300
  expect: cost_sold=1.666667, contrib=2.933333, be_month=4090.909091, be_day=157.342657, made_day=174.825175, be_sales_day=723.776224, safety=47.552448, profit_now=10880
- name: A wholesale-heavy bakery at a low average price
  inputs: fixed=34000, price=2.4, unit_cost=0.95, unsold=3, days=28, now=950
  expect: cost_sold=0.979381, contrib=1.420619, be_month=23933.236575, be_day=854.758449, made_day=881.194277, be_sales_day=2051.420278, safety=10.025426, profit_now=3788.453608
- name: Waste takes all the margin
  inputs: fixed=21000, price=1.4, unit_cost=1.35, unsold=6, days=26, now=520
  expect: cost_sold=1.43617, contrib=-0.03617, be_month=—, be_day=—, made_day=—, be_sales_day=—, safety=—, profit_now=-21489.021277
- name: Nothing sold today
  inputs: fixed=21000, price=3.9, unit_cost=1.35, unsold=6, days=26, now=0
  expect: cost_sold=1.43617, contrib=2.46383, be_month=8523.316062, be_day=327.819849, made_day=348.74452, be_sales_day=1278.497409, safety=—, profit_now=-21000
```
## How the break-even is calculated

The calculator works out what a unit sold earns after the units that were not sold, and then divides the fixed costs by it:

1. **Cost of each unit sold** = cost per unit made ÷ (1 − share not sold).
2. **Contribution per unit sold** = average price − cost of each unit sold.
3. **Units to sell per month** = fixed costs ÷ contribution per unit sold.
4. **Units to sell per day** = units per month ÷ days open.
5. **Units to bake per day** = units to sell per day ÷ (1 − share not sold).

With the starting numbers (example values, not benchmarks) a unit costs $1.35 to make, and with 6% not sold each unit sold costs $1.44. At an average price of $3.90 the contribution is $2.46. Fixed costs of $21,000 need 8,523 units a month, which is 328 a day over 26 days, or $1,278 of sales a day. To sell 328 units the bakery must bake 349. Today it sells 520 units a day, which is 37.0% above the break-even, and earns a profit of $12,311 a month.

## How to read the result

The margin of safety is how far sales can fall before the bakery loses money. The starting bakery can lose more than a third of its volume, while the wholesale-heavy bakery in the third example sells 855 units a day to break even and sells 950, a cushion of only 10.0%. Its average price is $2.40, so each unit sold leaves $1.42, and the large fixed costs of $34,000 need a lot of units.

The table changes the average price by a few percent either way. Because the fixed costs are spread over a small contribution, a small change in price changes the break-even by much more than the change in price. If the bakery sells at a blended price, check how the mix of counter and wholesale units shifts it.

## Typical mistakes

- **Counting units made as units sold.** The bakery pays for everything it bakes, and only some of it sells.
- **Treating the bakers as variable.** A bakery needs its team to open whatever the volume, so put them in the fixed costs.
- **Using the counter price for wholesale units.** Blend the prices, weighted by the units sold at each.
- **Leaving out the owner.** The profit here is before the owner's pay unless it is in the fixed costs.
- **Using one day for the whole week.** Weekends and weekdays can differ widely; run the calculator for each if they do.

## What this calculator cannot do

It treats every unit as the same average unit. It does not show the product mix, the days of the week, the seasons, the first months of building a customer base, or the cash needed to equip the bakery. A financial model for a bakery splits the retail counter and the wholesale accounts, builds the forecast month by month with cash, runs Low / Base / High scenarios for volume and price, and ends in lender-ready statements with a Checks sheet. To set the price of a product from its recipe, use the [recipe cost and unit price calculator](/calculators/bakery-recipe-cost-unit-price).

## FAQ {#faq}

### What counts as a unit not sold?

Anything you made and could not sell at full price: thrown away, given away or sold at a loss. A day-old discount counts as partly unsold; enter the share you estimate.

### Which costs are fixed and which are per unit?

Per unit: ingredients and packaging. Fixed: rent, the team you need to open, utilities, insurance and loan payments. If a cost rises with volume only in steps, treat it as fixed at the current level.

### Is the break-even the same as a profit?

No. At the break-even the bakery covers its costs and earns nothing. The profit line shows what remains at your current sales, before tax.

### Why does the result show a dash?

If the average price is no higher than the cost of a unit sold, each unit loses money, and no volume covers the fixed costs. The calculator shows a dash instead of an impossible number. The margin of safety also shows a dash when today's sales are zero.
