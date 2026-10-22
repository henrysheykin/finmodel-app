---
slug: /calculators/bakery-recipe-cost-unit-price
title: Bakery Recipe Cost and Unit Price Calculator | StartupModel
description: Enter four ingredients, the units a batch makes, unsold share, labor, energy and packaging. Get the cost of each unit sold and the price that earns your target margin, with the ingredient share.
keyword: bakery recipe cost calculator
template: bakery
related: [bakery-daily-break-even-units]
---

# Bakery recipe cost and unit price calculator

A batch of dough costs more than its flour and butter. The baker's time, the oven, the packaging and the units that never sell all go into the cost of each one that does. Enter one batch: the ingredients you use, what the batch makes and what else it costs; the calculator gives the cost of a unit sold and the price that earns the margin you want.

Use the same unit for the pack size and the amount used on each ingredient row (grams, milliliters or pieces). Enter 0 as the amount used for a row you do not need.

```inputs
- key: p1
  label: Ingredient 1, pack price
  unit: $
  default: 22
  min: 0
  max: 100000
  step: 0.01
  format: money2
  hint: What you pay for one sack, block or case.
- key: s1
  label: Ingredient 1, pack size
  default: 25000
  min: 0
  max: 10000000
  step: 1
  format: number1
  hint: Grams, milliliters or pieces in the pack.
- key: u1
  label: Ingredient 1, amount used
  default: 2000
  min: 0
  max: 10000000
  step: 1
  format: number1
  hint: In the same unit as the pack size.
- key: p2
  label: Ingredient 2, pack price
  unit: $
  default: 14
  min: 0
  max: 100000
  step: 0.01
  format: money2
- key: s2
  label: Ingredient 2, pack size
  default: 1000
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: u2
  label: Ingredient 2, amount used
  default: 800
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: p3
  label: Ingredient 3, pack price
  unit: $
  default: 5
  min: 0
  max: 100000
  step: 0.01
  format: money2
- key: s3
  label: Ingredient 3, pack size
  default: 1000
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: u3
  label: Ingredient 3, amount used
  default: 300
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: p4
  label: Ingredient 4, pack price
  unit: $
  default: 9
  min: 0
  max: 100000
  step: 0.01
  format: money2
- key: s4
  label: Ingredient 4, pack size
  default: 30
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: u4
  label: Ingredient 4, amount used
  default: 3
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: units
  label: Units the batch makes
  default: 24
  min: 1
  max: 100000
  step: 1
  format: int
- key: unsold
  label: Units not sold
  unit: "%"
  default: 8
  min: 0
  max: 95
  step: 0.5
  format: percent
  hint: Units that are burnt, broken, stale or left at closing. Your assumption.
- key: minutes
  label: Baker minutes for the batch
  unit: min
  default: 90
  min: 0
  max: 10000
  step: 5
  format: int
  hint: Mixing, shaping, proofing attention, baking and cleaning for the batch.
- key: wage
  label: Labor cost per hour
  unit: $
  default: 20
  min: 0
  max: 1000
  step: 0.5
  format: money2
  hint: Wage plus payroll taxes and benefits.
- key: energy
  label: Oven and energy cost for the batch
  unit: $
  default: 1.8
  min: 0
  max: 10000
  step: 0.1
  format: money2
- key: pack
  label: Packaging per unit
  unit: $
  default: 0.12
  min: 0
  max: 100
  step: 0.01
  format: money2
- key: margin
  label: Gross margin you want
  unit: "%"
  default: 55
  min: 0
  max: 95
  step: 1
  format: percent
  hint: The share of the price left after the costs of making the unit. Your own target.
```

```outputs
- key: c1
  label: Ingredient 1, cost in the batch
  formula: if(u1 == 0, 0, p1 * u1 / s1)
  format: money2
- key: c2
  label: Ingredient 2, cost in the batch
  formula: if(u2 == 0, 0, p2 * u2 / s2)
  format: money2
- key: c3
  label: Ingredient 3, cost in the batch
  formula: if(u3 == 0, 0, p3 * u3 / s3)
  format: money2
- key: c4
  label: Ingredient 4, cost in the batch
  formula: if(u4 == 0, 0, p4 * u4 / s4)
  format: money2
- key: ingredients
  label: Ingredients in the batch
  formula: c1 + c2 + c3 + c4
  format: money2
- key: batch_cost
  label: Total cost of the batch
  formula: ingredients + energy + minutes / 60 * wage + pack * units
  format: money2
  note: Ingredients, energy, baker time and packaging for every unit made.
- key: sellable
  label: Units sold from the batch
  formula: units * (1 - unsold / 100)
  format: number1
- key: cost_unit
  label: Cost per unit sold
  formula: batch_cost / sellable
  format: money2
- key: price
  label: Price for your target margin
  formula: cost_unit / (1 - margin / 100)
  format: money2
  highlight: true
- key: ingredient_pct
  label: Ingredients as a share of the price
  formula: ingredients / (sellable * price) * 100
  format: percent
```

```table
title: Price at different target margins
input: margin
values: 40, 45, 50, 55, 60
outputs: price, ingredient_pct
```

```examples
- name: A batch of butter croissants
  inputs: p1=22, s1=25000, u1=2000, p2=14, s2=1000, u2=800, p3=5, s3=1000, u3=300, p4=9, s4=30, u4=3, units=24, unsold=8, minutes=90, wage=20, energy=1.8, pack=0.12, margin=55
  expect: c1=1.76, c2=11.2, c3=1.5, c4=0.9, ingredients=15.36, batch_cost=50.04, sellable=22.08, cost_unit=2.266304, price=5.036232, ingredient_pct=13.81295
- name: A batch of simple bread rolls
  inputs: p1=22, s1=25000, u1=3000, p2=6, s2=1000, u2=60, p3=4, s3=1000, u3=50, p4=0, s4=0, u4=0, units=40, unsold=5, minutes=60, wage=18, energy=1.5, pack=0.05, margin=58
  expect: c1=2.64, c2=0.36, c3=0.2, c4=0, ingredients=3.2, batch_cost=24.7, sellable=38, cost_unit=0.65, price=1.547619, ingredient_pct=5.441296
- name: Nothing used
  inputs: p1=22, s1=25000, u1=0, p2=14, s2=1000, u2=0, p3=5, s3=1000, u3=0, p4=9, s4=30, u4=0, units=24, unsold=8, minutes=0, wage=20, energy=0, pack=0, margin=55
  expect: c1=0, c2=0, c3=0, c4=0, ingredients=0, batch_cost=0, sellable=22.08, cost_unit=0, price=0, ingredient_pct=—
- name: Almost everything unsold
  inputs: p1=22, s1=25000, u1=2000, p2=14, s2=1000, u2=800, p3=5, s3=1000, u3=300, p4=9, s4=30, u4=3, units=24, unsold=95, minutes=90, wage=20, energy=1.8, pack=0.12, margin=55
  expect: c1=1.76, c2=11.2, c3=1.5, c4=0.9, ingredients=15.36, batch_cost=50.04, sellable=1.2, cost_unit=41.7, price=92.666667, ingredient_pct=13.81295
```
## How the price is calculated

The calculator costs one batch and then spreads the cost over the units that actually sell:

1. **Ingredient cost** of each row = pack price × amount used ÷ pack size.
2. **Batch cost** = ingredients + oven and energy + baker minutes ÷ 60 × labor cost per hour + packaging per unit × units made.
3. **Units sold** = units made × (1 − share not sold).
4. **Cost per unit sold** = batch cost ÷ units sold.
5. **Price** = cost per unit sold ÷ (1 − gross margin you want).

With the starting numbers (example values, not benchmarks) the four rows are a sack of flour, butter, sugar and eggs. The batch of 24 croissants uses ingredients worth $15.36: $1.76, $11.20, $1.50 and $0.90 for the four rows. Add the oven and energy, 90 minutes of baker time at $20 an hour and the packaging, and the batch costs $50.04. With 8% of the units not sold, 22.1 are sold, so each one costs $2.27. A gross margin of 55% gives a price of $5.04, and the ingredients are 13.8% of it.

The second example, a batch of 40 simple rolls, costs $3.20 in ingredients and $24.70 for the whole batch, so a roll sold costs $0.65. A margin of 58% gives a price of $1.55, and ingredients are 5.4% of it.

## How to read the result

The price is the lowest one that earns the margin you chose, not a price the market has to accept. Compare it with what customers pay for a similar product. If the market price is lower, the table shows what each margin means, and the cost side shows what can change: a shorter batch time, a better yield or fewer units wasted.

Look at where the cost sits. In the croissant example most of the cost is baker time, not the ingredients, so a cheaper flour barely moves the price, while a batch that makes more units in the same time does. In the roll example the ingredient share is much lower still.

Waste works on every unit. In the last example nearly all of the batch is not sold, and the cost of a unit sold rises to $41.70. A smaller share left over is worth as much as a cheaper ingredient, and baking to order or in smaller batches can be cheaper than baking too much.

## Typical mistakes

- **Mixing units.** The pack size and the amount used must be in the same unit, such as grams on both rows.
- **Leaving out baker time.** It is a real cost even when the owner bakes; value it at what you would pay someone to do it.
- **Ignoring waste.** Units burnt, broken or left at closing are paid for by the units that sell.
- **Confusing margin with markup.** A margin of 55% is a share of the price, not 55% added to the cost.
- **Using last year's prices.** Update the pack prices whenever the supplier changes them.

## What this calculator cannot do

It prices one batch. It does not spread the rent, the equipment or the shop staff over the products, it does not mix the counter and wholesale channels, and it does not show months, cash or seasons. A financial model for a bakery combines the retail counter and the wholesale accounts in a monthly forecast with cash, runs Low / Base / High scenarios, and ends in lender-ready statements with a Checks sheet. To see how many units you must sell a day once the price is set, use the [bakery break-even calculator](/calculators/bakery-daily-break-even-units).

## FAQ {#faq}

### Should I include rent in the cost of a unit?

Not here. This calculator prices the cost of making the unit. Rent and other fixed costs are covered by the margin, and the break-even calculator shows how many units you must sell to cover them.

### How do I enter an ingredient I buy by the piece?

Enter the price of the pack, the number of pieces in it and the pieces used. In the example the pack is 30 eggs and 3 are used.

### What should I enter for units not sold?

The share of the units you make that you cannot sell at full price: burnt, broken, stale or left at closing. Track it for a few weeks before you trust the number.

### Why does the ingredient share show a dash?

If the batch costs nothing, the price is zero and a share of zero is undefined, so the calculator shows a dash.
