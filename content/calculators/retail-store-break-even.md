---
slug: /calculators/retail-store-break-even
title: Retail Store Break-Even Calculator: Sales You Need | StartupModel
description: Enter rent, wages, other fixed costs, gross margin and average basket. Get the monthly and daily sales a shop needs to break even, the sales it needs per day and the margin of safety today.
keyword: retail break even calculator
template: retail
related: [retail-markup-vs-margin, retail-inventory-turnover]
guide: /guides/startup-costs-and-break-even-analysis
---

# Retail store break-even calculator

A shop breaks even when the gross profit from its sales covers its fixed costs. Because every sale earns only a part of its price as gross profit, break-even sales are much larger than the fixed costs. Enter your rent, wages and other fixed costs and the gross margin on your sales; the sales you need, per month and per day, appear as you type.

```inputs
- key: rent
  label: Rent and occupancy per month
  unit: $
  default: 6000
  min: 0
  max: 10000000
  step: 100
  format: money
  hint: Rent, service charges, business rates or property tax on the premises.
- key: wages
  label: Wages per month
  unit: $
  default: 9000
  min: 0
  max: 10000000
  step: 100
  format: money
  hint: Staff you need whatever the sales, with payroll taxes.
- key: other_fixed
  label: Other fixed costs per month
  unit: $
  default: 2500
  min: 0
  max: 10000000
  step: 100
  format: money
  hint: Utilities, insurance, software, accounting, loan interest.
- key: gm
  label: Gross margin on sales
  unit: "%"
  default: 42
  min: 0
  max: 100
  step: 0.5
  format: percent
  hint: The share of each sale left after the cost of the goods. Your assumption.
- key: basket
  label: Average sale per transaction
  unit: $
  default: 38
  min: 0
  max: 100000
  step: 0.5
  format: money2
  hint: Sales divided by the number of transactions.
- key: days
  label: Days open per month
  unit: days
  default: 30
  min: 1
  max: 31
  step: 1
  format: int
- key: sales_now
  label: Sales per month today
  unit: $
  default: 52000
  min: 0
  max: 100000000
  step: 500
  format: money
  hint: What the shop sells now, or what you expect once open.
```

```outputs
- key: fixed
  label: Fixed costs per month
  formula: rent + wages + other_fixed
  format: money
- key: be_sales
  label: Break-even sales per month
  formula: fixed / max(gm, 0) * 100
  format: money
  highlight: true
- key: be_day
  label: Break-even sales per day
  formula: be_sales / days
  format: money
- key: be_tx_day
  label: Transactions needed per day
  formula: be_day / basket
  format: number1
  note: Round up in practice.
- key: safety
  label: Margin of safety today
  formula: (sales_now - be_sales) / sales_now * 100
  format: percent
  note: How far today's sales are above break-even; negative means below.
- key: profit_now
  label: Profit per month at today's sales
  formula: sales_now * gm / 100 - fixed
  format: money
  note: Before tax, and before interest if it is not in your fixed costs.
```

```table
title: Break-even at different gross margins
input: gm
values: 36, 40, 42, 45, 50
outputs: be_sales, be_tx_day, profit_now
```

```examples
- name: The starting numbers
  inputs: rent=6000, wages=9000, other_fixed=2500, gm=42, basket=38, days=30, sales_now=52000
  expect: fixed=17500, be_sales=41666.666667, be_day=1388.888889, be_tx_day=36.549708, safety=19.871795, profit_now=4340
- name: A small gift shop
  inputs: rent=3200, wages=4500, other_fixed=1300, gm=55, basket=27, days=26, sales_now=24000
  expect: fixed=9000, be_sales=16363.636364, be_day=629.370629, be_tx_day=23.310023, safety=31.818182, profit_now=4200
- name: A shop selling below break-even
  inputs: rent=8000, wages=12000, other_fixed=3000, gm=35, basket=60, days=28, sales_now=45000
  expect: fixed=23000, be_sales=65714.285714, be_day=2346.938776, be_tx_day=39.115646, safety=-46.031746, profit_now=-7250
- name: No gross margin means no break-even
  inputs: rent=6000, wages=9000, other_fixed=2500, gm=0, basket=38, days=30, sales_now=52000
  expect: fixed=17500, be_sales=—, be_day=—, be_tx_day=—, safety=—, profit_now=-17500
```

## How store break-even is calculated

Each sale earns its gross margin, and that gross profit has to pay the fixed costs. The calculator works in four steps:

1. **Fixed costs per month** = rent and occupancy + wages + other fixed costs.
2. **Break-even sales per month** = fixed costs ÷ gross margin.
3. **Break-even sales per day** = break-even sales ÷ days open.
4. **Transactions per day** = daily break-even sales ÷ average sale.

With the starting numbers (example values, not benchmarks) the fixed costs are $17,500 a month. At a gross margin of 42% the shop has to sell $41,667 a month to cover them, which is $1,389 a day, or about 36.5 transactions at an average sale of $38.00. Today's sales of $52,000 are 19.9% above break-even and produce a profit of $4,340 a month before tax.

The calculation explains why a shop needs so much more in sales than it pays in costs. With a margin of 42%, every dollar of fixed cost needs more than two dollars of sales behind it.

## How to read the result

Read the sales line first, then the transactions. A daily transaction count can be checked against the till and the footfall counter; a sales figure alone cannot say whether the problem is traffic, conversion or the size of the basket. The three levers are the same ones the table above lets you play with: the gross margin, the average sale and the fixed costs.

The margin of safety says how far sales can fall before the shop makes a loss. A small margin of safety is not a failure, but it means a quiet month can wipe out the profit. The sensitivity table shows break-even sales and profit at several gross margins, so you can see what a better buying price or less discounting is worth.

Two other examples show the range. A small gift shop with $9,000 of fixed costs and a margin of 55% breaks even at $16,364 a month and sits 31.8% above it. A larger shop with $23,000 of fixed costs and a margin of 35% needs $65,714 a month, so selling $45,000 puts it far below break-even and the month ends in a loss.

## Typical mistakes

- **Using the wrong margin.** Use the margin after discounts, markdowns and shrinkage, not the margin on the price tag.
- **Treating wages as variable.** Staff you need to open the doors are fixed, whatever you sell. Extra hours on busy days can be treated as a cost that moves with sales instead.
- **Leaving out the owner's pay.** If you take a wage from the shop, include it.
- **Forgetting card fees and online costs.** If they are a share of sales, take them out of the gross margin.
- **Forgetting that sales are seasonal.** The calculator uses one month. A shop with a strong December needs to be judged over the year.

## What this calculator cannot do

It finds a point on a single average month. It does not show the months it takes to reach that point, the cash tied up in stock and the fit-out before you open, or what a lease, a loan or a seasonal peak does to your cash. A financial model for a shop forecasts sales month by month, includes stock purchases and payment terms, and shows the funding you need to the lowest cash point. It runs Low / Base / High scenarios for sales and margin, and gives you lender-ready statements and a Checks sheet. The [startup costs and break-even guide](/guides/startup-costs-and-break-even-analysis) explains the cash view, the [markup vs margin calculator](/calculators/retail-markup-vs-margin) helps set the margin, and the [inventory turnover calculator](/calculators/retail-inventory-turnover) looks at the stock.

## FAQ {#faq}

### What should I include in fixed costs?

Everything you pay whatever you sell: rent and service charges, the staff you need to open, utilities, insurance, software, accounting and loan interest. Leave out the cost of the goods themselves, which is already in the gross margin.

### Is gross margin the same as profit?

No. Gross margin is what is left of a sale after the cost of the goods. Profit is what remains after the fixed costs too.

### How do I lower my break-even point?

Raise the gross margin by buying better or discounting less, raise the average sale, or reduce the fixed costs. The table above shows the first lever.

### Why does the result show a dash?

With a gross margin of zero, sales never cover the fixed costs, so there is no break-even point.
