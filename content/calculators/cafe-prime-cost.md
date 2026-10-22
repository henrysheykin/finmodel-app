---
slug: /calculators/cafe-prime-cost
title: Prime Cost Calculator: Food Plus Labor as a % of Sales | StartupModel
description: Add up cost of goods and total labor for a month and divide by sales. See your prime cost %, what is left for rent and profit, and how far you are from your own prime cost target.
keyword: prime cost calculator
template: cafe
related: [cafe-food-cost-percent, cafe-break-even-covers, cafe-table-turnover-revenue]
guide: /guides/restaurant-break-even-analysis
---

# Prime cost calculator: food and labor against sales

Prime cost is the sum of the two biggest costs of a restaurant or cafe: the cost of the food and drink you sell, and everything you pay for labor. Divide it by sales and you have one number to watch every week. Enter a month's figures; the percentages and what is left for the rest of the business appear as you type.

```inputs
- key: sales
  label: Sales for the month
  unit: $
  default: 60000
  min: 0
  max: 100000000
  step: 500
  format: money
  hint: Net sales, before sales tax or VAT.
- key: cogs
  label: Cost of food and drink sold
  unit: $
  default: 18000
  min: 0
  max: 100000000
  step: 100
  format: money
  hint: Opening stock plus purchases less closing stock for the month.
- key: wages
  label: Wages and salaries
  unit: $
  default: 16000
  min: 0
  max: 100000000
  step: 100
  format: money
  hint: Everyone on the payroll, managers included.
- key: payroll_costs
  label: Payroll taxes and benefits
  unit: $
  default: 2400
  min: 0
  max: 100000000
  step: 100
  format: money
  hint: Employer taxes, insurance and benefits that go with the wages.
- key: target
  label: Your target prime cost
  unit: "%"
  default: 60
  min: 1
  max: 100
  step: 0.5
  format: percent
  hint: Your own target, set from what your rent and other costs allow.
```

```outputs
- key: labour
  label: Total labor
  formula: wages + payroll_costs
  format: money
- key: prime
  label: Prime cost
  formula: cogs + labour
  format: money
- key: prime_pct
  label: Prime cost % of sales
  formula: prime / sales * 100
  format: percent
  highlight: true
- key: cogs_pct
  label: Food and drink cost %
  formula: cogs / sales * 100
  format: percent
- key: labour_pct
  label: Labor cost %
  formula: labour / sales * 100
  format: percent
- key: left
  label: Left for rent, other costs and profit
  formula: sales - prime
  format: money
- key: prime_target
  label: Prime cost at your target
  formula: sales * target / 100
  format: money
- key: over
  label: Over (+) or under (-) your target
  formula: prime - prime_target
  format: money
```

```table
title: How wages move the prime cost
input: wages
relative: -10, -5, 0, 5, 10
outputs: prime_pct, left, over
```

```examples
- name: The starting numbers
  inputs: sales=60000, cogs=18000, wages=16000, payroll_costs=2400, target=60
  expect: labour=18400, prime=36400, prime_pct=60.666667, cogs_pct=30, labour_pct=30.666667, left=23600, prime_target=36000, over=400
- name: A quiet month
  inputs: sales=38000, cogs=12500, wages=14500, payroll_costs=2100, target=62
  expect: labour=16600, prime=29100, prime_pct=76.578947, cogs_pct=32.894737, labour_pct=43.684211, left=8900, prime_target=23560, over=5540
- name: A strong month
  inputs: sales=85000, cogs=24000, wages=19000, payroll_costs=2900, target=55
  expect: labour=21900, prime=45900, prime_pct=54, cogs_pct=28.235294, labour_pct=25.764706, left=39100, prime_target=46750, over=-850
- name: No sales gives no percentage
  inputs: sales=0, cogs=500, wages=3000, payroll_costs=400, target=60
  expect: labour=3400, prime=3900, prime_pct=—, cogs_pct=—, labour_pct=—, left=-3900, prime_target=0, over=3900
```

## How prime cost is calculated

Prime cost has two parts, both taken from your books for the same period:

1. **Cost of food and drink sold**: opening stock plus purchases, less closing stock.
2. **Total labor**: wages and salaries plus the payroll taxes and benefits that go with them.

**prime cost % = (cost of food and drink + total labor) ÷ sales × 100**

With the starting numbers (example values, not benchmarks) a month of $60,000 sales has $18,000 of food and drink cost, 30.0% of sales, and $18,400 of labor, 30.7% of sales ($16,000 of wages and $2,400 of payroll costs). The prime cost is $36,400, or 60.7% of sales, and $23,600 is left to pay rent, utilities, insurance, marketing, software, loan interest and anything the owner takes home.

The last two lines compare the month with a target of your own. A target of 60% of sales means a prime cost of $36,000, so the month is $400 over.

## How to read the result

Prime cost works because it is the part of a restaurant's costs that you can change in days. You cannot renegotiate a lease on Tuesday, but you can change a rota, a portion size or an order. Watching the one combined percentage also shows trade-offs that the two parts hide: a kitchen can cut food cost by using more prepared ingredients and pay for it in labor, and the combined number tells you whether it helped.

Read it together with what is left. The money left after prime cost has to cover every other cost of the business. If the amount left is smaller than your rent and other fixed costs, the month lost money however good each part looks alone. The [break-even calculator](/calculators/cafe-break-even-covers) turns that around and finds the sales you need.

The sensitivity table moves wages up and down while sales and food cost stay put. It shows how much of the month's result rests on the rota.

## A quiet month and a strong one

The two other examples on this page show the range. A quiet month with $38,000 of sales and nearly the same wages gives a prime cost of 76.6%, and only $8,900 is left for everything else. A strong month with $85,000 of sales gives 54.0%, and $39,100 is left. The wages did not change much; the sales did. Labor is largely fixed in the short run, which is why a quiet month hurts so much.

## Typical mistakes

- **Leaving the owner's pay out.** If you work in the business, include a fair wage for yourself, or the labor percentage flatters the business.
- **Using purchases instead of cost of goods.** Without the stock count, a big order inflates one month and flatters the next.
- **Leaving out payroll taxes and benefits.** They are part of the price of labor.
- **Copying a target.** A target is your assumption, built from your rent and your other costs. A number from another venue tells you little about yours.

## What this calculator cannot do

It looks at one period that has already happened. It cannot say what next quarter looks like, how a new hire or a price change affects the figures, or whether you have the cash to cover a slow month. A financial model does: months and years, cash flow, Low / Base / High scenarios for sales and wages, lender-ready statements and a Checks sheet that flags errors. The [restaurant break-even guide](/guides/restaurant-break-even-analysis) covers how prime cost fits into the plan, and the [recipe cost calculator](/calculators/cafe-recipe-cost) works on the food side.

## FAQ {#faq}

### What should a prime cost target be?

That depends on your concept, your rent and your other costs, so treat any target as your own assumption. Work backwards: decide the profit you need, subtract the other costs, and see what prime cost allows it.

### Is prime cost the same as gross profit?

No. Gross profit usually takes away only the cost of food and drink. Prime cost also takes away labor, so what is left is smaller.

### Should I include the manager's salary?

Yes if the manager works in the business every week. Include anyone you could not do without on the payroll.

### Why does the result show a dash?

With zero sales the percentages cannot be calculated, so they show a dash. The money figures are still shown.
