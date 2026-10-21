---
slug: /calculators/retail-markup-vs-margin
title: Markup vs Margin Calculator: Retail Price and Gross Margin | StartupModel
description: Enter what a product costs and your markup to get the selling price and gross margin. Enter a target margin to see the markup and price it needs. Markup and margin are not the same number.
keyword: markup vs margin calculator
template: retail
related: [retail-inventory-turnover, retail-store-break-even]
---

# Markup vs margin calculator

Markup and margin both describe the gap between what a product costs and what it sells for, but they measure it against different things, and mixing them up is one of the commonest pricing errors in retail. Enter a cost and a markup to see the price and the margin. Enter a margin you want, and the calculator shows the markup and price that deliver it.

```inputs
- key: cost
  label: Cost of the product
  unit: $
  default: 45
  min: 0
  max: 1000000
  step: 0.5
  format: money2
  hint: What you pay for one unit, delivered, before any discount you do not get.
- key: markup
  label: Markup on cost
  unit: "%"
  default: 60
  min: 0
  max: 1000
  step: 1
  format: percent
  hint: The amount you add to the cost, as a share of the cost.
- key: target_margin
  label: Gross margin you want
  unit: "%"
  default: 40
  min: 0
  max: 99
  step: 0.5
  format: percent
  hint: The share of the selling price you want to keep after the cost of the product.
```

```outputs
- key: price
  label: Selling price at that markup
  formula: cost * (1 + markup / 100)
  format: money2
- key: profit
  label: Gross profit per unit
  formula: price - cost
  format: money2
- key: margin
  label: Gross margin at that markup
  formula: profit / price * 100
  format: percent
  highlight: true
  note: Profit as a share of the selling price.
- key: margin_price
  label: Price for your target margin
  formula: cost / (1 - target_margin / 100)
  format: money2
- key: margin_markup
  label: Markup for your target margin
  formula: target_margin / (100 - target_margin) * 100
  format: percent
  note: Always higher than the margin.
- key: margin_profit
  label: Gross profit per unit at that price
  formula: margin_price - cost
  format: money2
```

```table
title: What each markup means as a margin
input: markup
values: 30, 40, 50, 60, 100
outputs: price, profit, margin
```

```examples
- name: The starting numbers
  inputs: cost=45, markup=60, target_margin=40
  expect: price=72, profit=27, margin=37.5, margin_price=75, margin_markup=66.666667, margin_profit=30
- name: A clothing item at double the cost
  inputs: cost=18, markup=100, target_margin=55
  expect: price=36, profit=18, margin=50, margin_price=40, margin_markup=122.222222, margin_profit=22
- name: A low-margin grocery line
  inputs: cost=2.4, markup=25, target_margin=20
  expect: price=3, profit=0.6, margin=20, margin_price=3, margin_markup=25, margin_profit=0.6
- name: A free item has no margin
  inputs: cost=0, markup=60, target_margin=40
  expect: price=0, profit=0, margin=—, margin_price=0, margin_markup=66.666667, margin_profit=0
```

## Markup and margin: the two formulas

Both numbers start from the same two amounts, the cost of a product and its selling price. They differ in what they divide by:

**markup = (price − cost) ÷ cost × 100**

**gross margin = (price − cost) ÷ price × 100**

Markup is the amount you add on top of the cost. Margin is the share of the selling price you keep. Because the price is always larger than the cost, the margin is always smaller than the markup.

With the starting numbers (example values, not benchmarks) a product that costs $45 and carries a 60% markup sells for $72.00. The gross profit is $27.00, which is a margin of 37.5%. The two numbers describe the same sale; one is just measured against a smaller base.

## Going the other way: from a margin to a price

Most budgets and lender models are written in margins, while many shops price in markups, so the calculator also works backwards. If you want to keep 40% of the selling price, the price is the cost divided by (1 − 0.40), which is $75.00, and the gross profit is $30.00. The markup that gets you there is 66.7%, not 40%. Adding 40% to the cost would give a margin well below 40%, and that gap is where the confusion costs money.

The same effect is larger at higher numbers. In the second example a clothing item costing $18 with a markup of 100%, a doubling of the cost, sells for $36 and leaves a margin of 50.0%. To reach a margin of 55% you would need a markup of 122.2% and a price of $40.00.

## How to read the result

Use the margin when you are checking a business against its costs, because rent, wages and every other cost are paid out of the share of sales you keep. Use the markup when you are setting a price from a supplier's invoice, because it is applied to the cost you can see. The sensitivity table shows both together: the price and margin at several markups, so you can read off the margin each markup delivers.

The calculator shows gross profit only. It is what is left after the cost of the product, before rent, wages, card fees, shrinkage and discounts. A healthy-looking margin on the shelf can be much smaller after markdowns, theft and waste.

## Typical mistakes

- **Treating a 40% markup as a 40% margin.** The markup gives a smaller margin than the number suggests.
- **Using the list cost, not the landed cost.** Include freight, duty and handling in the cost of the product.
- **Ignoring discounts.** If a share of your sales is sold on promotion, the average price is below the shelf price. Use the average.
- **Applying one markup to everything.** Fast sellers can carry a thin margin and slow sellers a thick one. The overall margin depends on the mix.
- **Rounding the price without re-checking the margin.** A rounded price changes the margin a little. Enter the rounded price back in as a markup to check.

## What this calculator cannot do

It prices one product at a time and stops at gross profit. It does not know how many units you will sell, how the mix between products shifts the average margin, what your fixed costs are, or when the cash is spent and returned. A financial model for a shop puts the margin into a monthly forecast with stock purchases and cash, Low / Base / High scenarios for sales and margin, lender-ready statements and a Checks sheet that confirms the totals. The [inventory turnover calculator](/calculators/retail-inventory-turnover) shows how fast the stock sells, and the [store break-even calculator](/calculators/retail-store-break-even) turns a margin into the sales you need.

## FAQ {#faq}

### Is markup the same as margin?

No. Markup is profit divided by cost; margin is profit divided by price. For the same sale the markup is always the larger number.

### How do I convert markup to margin?

Divide the markup by 100 plus the markup, and multiply by 100. A markup of 100% becomes a margin of 50%. The calculator does this when you enter a markup and reads the answer from the margin line.

### How do I convert margin to markup?

Divide the margin by 100 minus the margin, and multiply by 100. The second block of results does this for the margin you enter.

### Why does the margin show a dash?

If the cost is zero, the selling price is zero too, and a margin cannot be worked out from a price of zero.
