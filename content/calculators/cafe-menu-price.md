---
slug: /calculators/cafe-menu-price
title: Menu Price Calculator: Price From Your Target Food Cost % | StartupModel
description: Enter what a dish or drink costs you and the food cost % you are aiming for. Get the menu price, the rounded price, the real food cost % and the profit per serving.
keyword: menu price calculator
template: cafe
related: [cafe-food-cost-percent, cafe-break-even-covers]
guide: /guides/restaurant-break-even-analysis
---

# Menu price calculator

Work out what to charge for a dish or a drink from what it costs you to make and the food cost percentage you are aiming for. Enter your numbers on the left; the price, the real food cost at the rounded price and the profit per serving update as you type.

```inputs
- key: cost
  label: Ingredient cost per serving
  unit: $
  default: 1.40
  min: 0
  max: 500
  step: 0.05
  format: money2
  hint: Everything in the recipe, plus the cup and lid, at what you pay today.
- key: target_pct
  label: Target food cost
  unit: %
  default: 30
  min: 1
  max: 95
  step: 0.5
  format: percent
  hint: Your own target: the share of the menu price you will spend on ingredients.
- key: step
  label: Round the price to the nearest
  unit: $
  default: 0.25
  min: 0.01
  max: 5
  step: 0.01
  format: money2
  hint: Use 0.05 or 0.25 for drinks, 1 for whole dollars.
```

```outputs
- key: price_exact
  label: Exact price for your target
  formula: cost / (target_pct / 100)
  format: money2
- key: price
  label: Menu price, rounded
  formula: round(price_exact / step) * step
  format: money2
  highlight: true
- key: actual_pct
  label: Food cost % at that price
  formula: cost / price * 100
  format: percent
  note: Rounding moves it a little away from your target.
- key: profit
  label: Gross profit per serving
  formula: price - cost
  format: money2
- key: markup
  label: Price as a multiple of cost
  formula: price / cost
  format: multiple
```

```table
title: What each food cost target does to the price
input: target_pct
values: 25, 28, 30, 32, 35
outputs: price, actual_pct, profit
```

```examples
- name: Latte at a 30% target, rounded to $0.25
  inputs: cost=1.40, target_pct=30, step=0.25
  expect: price_exact=4.666667, price=4.75, actual_pct=29.473684, profit=3.35, markup=3.392857
- name: Cookie at a 25% target, rounded to $0.05
  inputs: cost=0.85, target_pct=25, step=0.05
  expect: price_exact=3.4, price=3.4, actual_pct=25, profit=2.55, markup=4
- name: Lunch special rounded to whole dollars
  inputs: cost=6.20, target_pct=35, step=1
  expect: price_exact=17.714286, price=18, actual_pct=34.444444, profit=11.8, markup=2.903226
- name: A free item has no food cost percentage
  inputs: cost=0, target_pct=30, step=0.25
  expect: price_exact=0, price=0, actual_pct=—, profit=0, markup=—
```

## How the menu price is worked out

The food cost percentage is the ingredient cost divided by the menu price. Turn that around and the price is the ingredient cost divided by the target:

**menu price = ingredient cost ÷ target food cost %**

With the starting numbers, a serving that costs $1.40 to make and a target of 30% gives an exact price of $4.67. Few menus end in 67 cents, so the calculator rounds to the step you choose. Rounded to the nearest $0.25 the price is $4.75, the real food cost is 29.5% and each serving leaves $3.35 after ingredients. These are example values; replace them with your own.

The rounded price matters because the target is a plan and the real food cost is what the till records. Check the second line of the results whenever you change the step.

## Choosing a food cost target

There is no universal right target, and a figure copied from another business tells you little about yours. The target is your assumption: it comes from what your concept can charge, what customers in your neighbourhood will pay, and how much is left for rent, wages and everything else. Work it backwards instead of borrowing it:

1. List your fixed costs (rent, staff, utilities, insurance).
2. Estimate how many customers you can serve and what they will spend.
3. Find the food cost percentage at which that revenue still covers everything and leaves a profit.

The [break-even calculator](/calculators/cafe-break-even-covers) does step 3 for the whole business, and the [restaurant break-even guide](/guides/restaurant-break-even-analysis) explains the method. The table above shows how sensitive the price is: a few points on the target moves the price on every item.

## What to count as ingredient cost

- Everything that goes into the serving, including garnish, sauces and the milk in the coffee.
- Packaging that goes with the serving: the cup, lid, sleeve and bag.
- Waste you cannot avoid: trimmings, spoilage, a spilled shot. Raise the cost per serving to cover it, or the target will be missed even when the price is right.
- Current supplier prices. Refresh the cost whenever an invoice changes.

Leave out labour, rent and utilities. Those sit in the fixed and other costs of the business, not in the food cost of a serving.

## What this calculator leaves out

The price here is a price before sales tax or VAT. If your menu shows tax-inclusive prices, take the tax out first. The calculator also treats each item alone. It does not know how a cheaper item sells next to a dearer one, how a price rise changes the number of customers, or what your fixed costs are. A financial model puts those together, and the promotion below shows what that adds.

## FAQ {#faq}

### What is a good food cost percentage?

It depends on the business. A target is useful only when you know what it leaves for rent, wages and profit, so treat the number as your assumption and test it against your fixed costs.

### Should I round the price up or down?

Either. Rounding up gives a little more margin, and rounding down keeps a price point customers like. The calculator shows the real food cost at the rounded price so you can see what the choice costs.

### Why is my real food cost higher than the calculator says?

Usually waste, portions that drift above the recipe, or supplier prices that rose after you last updated the cost. Weigh a few servings and compare them with the recipe.

### Does the price include tax?

No. It is the price before sales tax or VAT.
