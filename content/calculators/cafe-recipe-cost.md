---
slug: /calculators/cafe-recipe-cost
title: Recipe Cost Calculator: Cost Per Portion and Food Cost % | StartupModel
description: Enter up to five ingredients with their pack price, pack size and amount used, plus waste and portions. Get the cost per portion, the food cost % at your menu price and a target price.
keyword: recipe cost calculator
template: cafe
related: [cafe-food-cost-percent, cafe-menu-price, cafe-prime-cost]
guide: /guides/restaurant-break-even-analysis
---

# Recipe cost calculator: cost per portion

The cost of a recipe is the cost of what goes into the pot, divided by the portions that come out. Enter up to five ingredients, how you buy each one and how much the recipe uses, and the calculator gives the cost per portion, the food cost percentage at your menu price and the price a target would need.

Use the same unit for the pack size and the amount used on each row (grams, milliliters or pieces). Enter 0 as the amount used for a row you do not need.

```inputs
- key: p1
  label: Ingredient 1, pack price
  unit: $
  default: 12.50
  min: 0
  max: 100000
  step: 0.01
  format: money2
  hint: What you pay for one pack, tub or case.
- key: s1
  label: Ingredient 1, pack size
  default: 5000
  min: 0
  max: 10000000
  step: 1
  format: number1
  hint: Grams, milliliters or pieces in the pack.
- key: u1
  label: Ingredient 1, amount used
  default: 300
  min: 0
  max: 10000000
  step: 1
  format: number1
  hint: In the same unit as the pack size.
- key: p2
  label: Ingredient 2, pack price
  unit: $
  default: 18
  min: 0
  max: 100000
  step: 0.01
  format: money2
- key: s2
  label: Ingredient 2, pack size
  default: 2000
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: u2
  label: Ingredient 2, amount used
  default: 200
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: p3
  label: Ingredient 3, pack price
  unit: $
  default: 6
  min: 0
  max: 100000
  step: 0.01
  format: money2
- key: s3
  label: Ingredient 3, pack size
  default: 3000
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: u3
  label: Ingredient 3, amount used
  default: 250
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
  default: 4
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: p5
  label: Ingredient 5, pack price
  unit: $
  default: 3
  min: 0
  max: 100000
  step: 0.01
  format: money2
- key: s5
  label: Ingredient 5, pack size
  default: 1000
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: u5
  label: Ingredient 5, amount used
  default: 600
  min: 0
  max: 10000000
  step: 1
  format: number1
- key: waste
  label: Waste and trimming
  unit: "%"
  default: 5
  min: 0
  max: 100
  step: 0.5
  format: percent
  hint: Extra cost to cover what is lost in preparation. Your assumption.
- key: portions
  label: Portions the recipe makes
  default: 8
  min: 1
  max: 10000
  step: 1
  format: int
- key: price
  label: Menu price per portion
  unit: $
  default: 3.50
  min: 0
  max: 1000
  step: 0.05
  format: money2
  hint: The price before sales tax or VAT.
- key: target
  label: Target food cost
  unit: "%"
  default: 30
  min: 1
  max: 95
  step: 0.5
  format: percent
  hint: Your own target: the share of the menu price you will spend on ingredients.
```

```outputs
- key: c1
  label: Ingredient 1, cost in the recipe
  formula: if(u1 == 0, 0, p1 * u1 / s1)
  format: money2
- key: c2
  label: Ingredient 2, cost in the recipe
  formula: if(u2 == 0, 0, p2 * u2 / s2)
  format: money2
- key: c3
  label: Ingredient 3, cost in the recipe
  formula: if(u3 == 0, 0, p3 * u3 / s3)
  format: money2
- key: c4
  label: Ingredient 4, cost in the recipe
  formula: if(u4 == 0, 0, p4 * u4 / s4)
  format: money2
- key: c5
  label: Ingredient 5, cost in the recipe
  formula: if(u5 == 0, 0, p5 * u5 / s5)
  format: money2
- key: batch
  label: Cost of the whole recipe, with waste
  formula: (c1 + c2 + c3 + c4 + c5) * (1 + waste / 100)
  format: money2
- key: portion_cost
  label: Cost per portion
  formula: batch / portions
  format: money2
  highlight: true
- key: food_pct
  label: Food cost % at your menu price
  formula: portion_cost / price * 100
  format: percent
- key: price_target
  label: Menu price for your target food cost
  formula: portion_cost / (target / 100)
  format: money2
- key: top_share
  label: Share of the costliest ingredient
  formula: max(c1, c2, c3, c4, c5) * (1 + waste / 100) / batch * 100
  format: percent
  note: A high share shows which supplier price matters most.
```

```table
title: How waste changes the cost of a portion
input: waste
values: 0, 2, 5, 8, 10
outputs: portion_cost, food_pct
```

```examples
- name: A banana bread loaf cut into portions
  inputs: p1=12.5, s1=5000, u1=300, p2=18, s2=2000, u2=200, p3=6, s3=3000, u3=250, p4=9, s4=30, u4=4, p5=3, s5=1000, u5=600, waste=5, portions=8, price=3.5, target=30
  expect: c1=0.75, c2=1.8, c3=0.5, c4=1.2, c5=1.8, batch=6.3525, portion_cost=0.794063, food_pct=22.6875, price_target=2.646875, top_share=29.752066
- name: Two ingredients only
  inputs: p1=4.2, s1=1000, u1=150, p2=2.4, s2=1000, u2=500, p3=0, s3=0, u3=0, p4=0, s4=0, u4=0, p5=0, s5=0, u5=0, waste=0, portions=4, price=6, target=25
  expect: c1=0.63, c2=1.2, c3=0, c4=0, c5=0, batch=1.83, portion_cost=0.4575, food_pct=7.625, price_target=1.83, top_share=65.57377
- name: Nothing used gives no answer
  inputs: p1=12.5, s1=5000, u1=0, p2=18, s2=2000, u2=0, p3=6, s3=3000, u3=0, p4=9, s4=30, u4=0, p5=3, s5=1000, u5=0, waste=5, portions=8, price=3.5, target=30
  expect: c1=0, c2=0, c3=0, c4=0, c5=0, batch=0, portion_cost=0, food_pct=0, price_target=0, top_share=—
- name: A free item
  inputs: p1=12.5, s1=5000, u1=300, p2=18, s2=2000, u2=200, p3=6, s3=3000, u3=250, p4=9, s4=30, u4=4, p5=3, s5=1000, u5=600, waste=5, portions=8, price=0, target=30
  expect: c1=0.75, c2=1.8, c3=0.5, c4=1.2, c5=1.8, batch=6.3525, portion_cost=0.794063, food_pct=—, price_target=2.646875, top_share=29.752066
```

## How the cost of a recipe is calculated

Every ingredient row works the same way. You buy a pack at a price, the pack holds a known amount, and the recipe uses part of it:

**ingredient cost = pack price × amount used ÷ pack size**

Add the five rows, add the waste allowance, and divide by the portions the recipe makes:

**cost per portion = (sum of ingredient costs) × (1 + waste %) ÷ portions**

The example is a banana bread cut into 8 slices. The flour costs $0.75 (300 g from a pack of 5,000 g at $12.50), the butter $1.80, the sugar $0.50, the eggs $1.20 and the bananas $1.80. With 5% waste added the whole recipe costs $6.35, which is $0.79 a slice. At a menu price of $3.50 the food cost is 22.7%. If you want a 30% food cost, the price would be $2.65. These are example values to show the mechanics; replace every one with your own invoice prices.

## How to read the result

The first number to look at is the **cost per portion**. It is what you compare with the menu price, and it is the figure the [food cost percentage calculator](/calculators/cafe-food-cost-percent) and the [menu price calculator](/calculators/cafe-menu-price) start from.

The last line, the share of the costliest ingredient, tells you where to look when a supplier raises a price. In the example the bananas and the butter together are over half of the recipe, so a change in either moves the cost of every slice, while a change in the sugar price barely registers. Put your attention where the money is.

The table shows the effect of the waste allowance. Waste is easy to leave out because it never appears on an invoice, and the table shows how quickly it adds to the cost of a portion.

## Working with the rows

- **Same unit on both fields of a row.** If the pack size is in kilograms and the amount used is in grams, the result is wrong by a factor of a thousand. Convert first.
- **Count what you actually use.** For eggs, a pack of 30 and four used gives 4 ÷ 30 of the pack price.
- **Unused rows.** Enter 0 as the amount used. The row then costs nothing, whatever is in its other fields.
- **More than five ingredients.** Add the small ones (salt, oil, a pinch of spice) into one row as a single line cost, or into the waste allowance.

## Typical mistakes

- **Costing the ingredient list but not the yield.** A kilogram of raw meat does not give a kilogram of cooked portions. Use the amount you start with, and put the loss into the waste allowance.
- **Forgetting that recipes are scaled.** If the batch is doubled, double the amounts used and the portions.
- **Using last year's prices.** Update the pack prices whenever a supplier invoice changes.

## What this calculator cannot do

It prices one recipe at one moment. It does not know how many portions you will sell, what the labor and rent are, or how a price change moves demand. A financial model puts cost per portion into the whole business month by month, with cash, Low / Base / High scenarios for supplier prices and sales, lender-ready statements and a Checks sheet that confirms the arithmetic. The [restaurant break-even guide](/guides/restaurant-break-even-analysis) shows how recipe cost feeds the rest.

## FAQ {#faq}

### Does the recipe cost include labor?

No. It is the cost of ingredients and anything you buy that goes with the portion. Labor is counted separately, for example in the [prime cost calculator](/calculators/cafe-prime-cost).

### How do I enter an ingredient bought by the piece?

Put the number of pieces in the pack as the pack size and the number the recipe uses as the amount used. A pack of 30 eggs with 4 used is entered as 30 and 4.

### What waste percentage should I use?

Use your own. Weigh what goes in and what comes out for a few batches, and use the difference. There is no figure that fits every kitchen.

### Why is the result a dash?

A dash means the calculation has no answer. The usual cause is a pack size of zero on a row that is used, or a menu price of zero when the food cost percentage is calculated.
