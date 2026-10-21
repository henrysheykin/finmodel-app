---
slug: /calculators/cafe-food-cost-percent
title: Food Cost Percentage Calculator for a Cafe or Restaurant | StartupModel
description: Enter the menu price and the ingredient cost of a dish or drink to see its food cost %, gross margin and markup, and what it adds up to over a month of sales.
keyword: food cost percentage calculator
template: cafe
related: [cafe-menu-price, cafe-break-even-covers]
guide: /guides/restaurant-break-even-analysis
---

# Food cost percentage calculator

Food cost percentage tells you how much of every dollar a dish brings in goes on its ingredients. Enter the menu price and what the serving costs you to make; the percentage, the margin and a month of sales appear as you type.

```inputs
- key: price
  label: Menu price
  unit: $
  default: 4.50
  min: 0
  max: 1000
  step: 0.05
  format: money2
  hint: The price before sales tax or VAT.
- key: cost
  label: Ingredient cost per serving
  unit: $
  default: 1.30
  min: 0
  max: 1000
  step: 0.05
  format: money2
  hint: Ingredients and the packaging that goes with the serving.
- key: per_day
  label: Servings sold per day
  unit: per day
  default: 150
  min: 0
  max: 5000
  step: 1
  format: int
  hint: An example value; use your own sales count.
- key: days
  label: Days open per month
  unit: days
  default: 26
  min: 1
  max: 31
  step: 1
  format: int
```

```outputs
- key: food_cost_pct
  label: Food cost %
  formula: cost / price * 100
  format: percent
  highlight: true
  note: Ingredient cost as a share of the menu price.
- key: profit
  label: Gross profit per serving
  formula: price - cost
  format: money2
- key: margin_pct
  label: Gross margin %
  formula: profit / price * 100
  format: percent
- key: markup
  label: Price as a multiple of cost
  formula: price / cost
  format: multiple
- key: month_sales
  label: Sales per month
  formula: price * per_day * days
  format: money
- key: month_cost
  label: Ingredient cost per month
  formula: cost * per_day * days
  format: money
- key: month_profit
  label: Gross profit per month
  formula: profit * per_day * days
  format: money
```

```table
title: How the food cost changes with the menu price
input: price
relative: -10, -5, 0, 5, 10
outputs: food_cost_pct, profit, month_profit
```

```examples
- name: Latte at the starting numbers
  inputs: price=4.50, cost=1.30, per_day=150, days=26
  expect: food_cost_pct=28.888889, profit=3.2, margin_pct=71.111111, markup=3.461538, month_sales=17550, month_cost=5070, month_profit=12480
- name: Sandwich
  inputs: price=9.5, cost=3.8, per_day=40, days=30
  expect: food_cost_pct=40, profit=5.7, margin_pct=60, markup=2.5, month_sales=11400, month_cost=4560, month_profit=6840
- name: A free item has no percentage
  inputs: price=0, cost=1.30, per_day=100, days=26
  expect: food_cost_pct=—, profit=-1.3, margin_pct=—, markup=0, month_sales=0, month_cost=3380, month_profit=-3380
- name: No ingredient cost
  inputs: price=3, cost=0, per_day=10, days=20
  expect: food_cost_pct=0, profit=3, margin_pct=100, markup=—, month_sales=600, month_cost=0, month_profit=600
```

## How food cost percentage is calculated

**food cost % = ingredient cost per serving ÷ menu price × 100**

With the starting numbers, a drink that costs $1.30 to make and sells for $4.50 has a food cost of 28.9%. Gross margin is what is left: 71.1%, or $3.20 on every serving. The markup says the same thing as a multiple: the price is 3.46 times the ingredient cost.

The monthly lines multiply the per-serving figures by servings per day and days open. They are there to show how a small difference per serving adds up; the servings and days are example values, not a forecast. Gross profit here means sales less ingredients only. Rent, wages and the other costs of running the place come out of it.

## How to read the result

A low food cost percentage is not automatically good. It can mean a healthy margin, or a price that is high for what the customer gets. A high one can mean a generous recipe that sells well. The percentage is a signal to look at one item, and what counts is the margin you earn across the whole menu, weighted by what people really order.

The sensitivity table moves the menu price up and down from your number while the cost stays the same. It shows why price is the strongest lever: the cost of a serving does not change when the price rises, so the whole increase lands in the gross profit. It also shows what a lower price gives away.

## Keeping the cost figure honest

The percentage is only as good as the cost behind it.

- Recost each recipe when supplier prices change.
- Count packaging and waste, not just the ingredient list.
- Weigh portions now and then; portions drift upward over a busy week.
- Use the yield you actually get from an ingredient, after trimming and cooking, not the weight on the invoice.

If you are setting a new price from a target, use the [menu price calculator](/calculators/cafe-menu-price). To find how many customers the whole business needs, use the [break-even calculator](/calculators/cafe-break-even-covers).

## FAQ {#faq}

### Is food cost the same as cost of goods sold?

Close, but not identical. Food cost is the ingredient cost of what you sell. Cost of goods sold in your accounts is usually calculated from opening stock, purchases and closing stock over a period, so it also reflects waste and stock changes.

### Should I include labour in food cost?

No. Labour is a separate cost. Putting it in the food cost of a serving mixes two things that behave differently as sales change.

### Why does the markup differ from the margin?

They use different bases. Markup compares the price with the cost; margin compares the profit with the price. A price that is 3.46 times the cost adds 2.46 times the cost on top of it, and leaves a margin of 71.1% of the price.

### Does the calculator include sales tax?

No. Enter the menu price before sales tax or VAT.
