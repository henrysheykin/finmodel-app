---
slug: /calculators/break-even-calculator
title: Break-Even Calculator: Units and Sales to Cover Your Costs | StartupModel
description: Enter fixed costs, price and variable cost per unit. Get the units and sales needed to break even, the contribution margin, the margin of safety and the units needed for a profit target.
keyword: break even calculator
guide: /guides/startup-costs-and-break-even-analysis
related: [startup-cost-calculator, payback-period-calculator, loan-payment-calculator]
---

# Break-even calculator

The break-even point is the volume at which a business stops losing money: the contribution from its sales equals its fixed costs. Enter your fixed costs, your price and the cost that rises with each unit sold. The units and sales you need appear as you type, and you can add a profit target to see what it takes to earn one.

```inputs
- key: fixed
  label: Fixed costs per month
  unit: $
  default: 12000
  min: 0
  max: 1000000000
  step: 100
  format: money
  hint: Costs you pay whatever you sell: rent, salaries, insurance, software.
- key: price
  label: Price per unit
  unit: $
  default: 40
  min: 0
  max: 1000000
  step: 0.5
  format: money2
  hint: What a customer pays for one unit, a sale or an hour, before sales tax.
- key: unit_cost
  label: Variable cost per unit
  unit: $
  default: 22
  min: 0
  max: 1000000
  step: 0.5
  format: money2
  hint: Materials, packaging, card fees and commission for one unit.
- key: units_now
  label: Units sold per month today
  default: 800
  min: 0
  max: 1000000000
  step: 10
  format: int
  hint: What you sell now, or expect to sell once open.
- key: target_profit
  label: Monthly profit you want
  unit: $
  default: 3000
  min: 0
  max: 1000000000
  step: 100
  format: money
```

```outputs
- key: contrib
  label: Contribution per unit
  formula: price - unit_cost
  format: money2
  note: What each unit adds towards the fixed costs.
- key: contrib_pct
  label: Contribution margin
  formula: contrib / price * 100
  format: percent
- key: be_units
  label: Break-even units per month
  formula: fixed / max(contrib, 0)
  format: number1
  highlight: true
  note: Round up in practice.
- key: be_revenue
  label: Break-even sales per month
  formula: be_units * price
  format: money
- key: safety
  label: Margin of safety today
  formula: (units_now - be_units) / units_now * 100
  format: percent
  note: How far today's sales are above break-even; negative means below.
- key: profit_now
  label: Profit per month at today's sales
  formula: contrib * units_now - fixed
  format: money
- key: units_target
  label: Units needed for your profit target
  formula: (fixed + target_profit) / max(contrib, 0)
  format: number1
```

```table
title: Break-even at different prices
input: price
relative: -10, -5, 0, 5, 10
outputs: be_units, be_revenue, profit_now
```

```examples
- name: The starting numbers
  inputs: fixed=12000, price=40, unit_cost=22, units_now=800, target_profit=3000
  expect: contrib=18, contrib_pct=45, be_units=666.666667, be_revenue=26666.666667, safety=16.666667, profit_now=2400, units_target=833.333333
- name: A consulting hour
  inputs: fixed=8000, price=120, unit_cost=30, units_now=70, target_profit=2500
  expect: contrib=90, contrib_pct=75, be_units=88.888889, be_revenue=10666.666667, safety=-26.984127, profit_now=-1700, units_target=116.666667
- name: A product sold below its cost
  inputs: fixed=12000, price=20, unit_cost=22, units_now=800, target_profit=3000
  expect: contrib=-2, contrib_pct=-10, be_units=—, be_revenue=—, safety=—, profit_now=-13600, units_target=—
- name: Nothing sold today
  inputs: fixed=12000, price=40, unit_cost=22, units_now=0, target_profit=3000
  expect: contrib=18, contrib_pct=45, be_units=666.666667, be_revenue=26666.666667, safety=—, profit_now=-12000, units_target=833.333333
```

## How break-even is calculated

Costs come in two kinds. **Fixed costs** are paid whatever you sell: rent, salaries, insurance, software. **Variable costs** rise with each unit: materials, packaging, card fees, commission. The difference between the price and the variable cost is the **contribution**, the amount each unit adds towards the fixed costs.

1. **Contribution per unit** = price − variable cost per unit.
2. **Contribution margin** = contribution ÷ price × 100.
3. **Break-even units** = fixed costs ÷ contribution per unit.
4. **Break-even sales** = break-even units × price.
5. **Units for a profit target** = (fixed costs + target profit) ÷ contribution per unit.

With the starting numbers (example values, not benchmarks) fixed costs are $12,000 a month, the price is $40.00 and the variable cost is $22.00, so each unit contributes $18.00, a contribution margin of 45.0%. The business has to sell 666.7 units, or $26,667 of sales, to break even. At 800 units today it is 16.7% above break-even and makes $2,400 a month. To earn $3,000 a month it would need to sell 833.3 units.

## How to read the result

The break-even point is a boundary, not a goal. Below it you lose money on every month; just above it you are working for no profit. Read it together with the margin of safety, which says how far sales can fall before you cross the line. A business with a large margin of safety can survive a bad season; one with a small margin of safety is exposed.

The table shows the effect of price, which is usually the strongest lever. Because the variable cost does not change when the price rises, the whole increase goes to the contribution, so the break-even units fall faster than the price rises. A price cut works in reverse and costs more units than it seems.

Other cases show the range. A consulting hour sold at $120 with a variable cost of $30 contributes $90, a margin of 75.0%, and the business needs 88.9 hours a month to cover $8,000 of fixed costs. If the price is below the variable cost, as when a $20 product costs $22 to make, each unit adds a loss, and no volume breaks even.

## Typical mistakes

- **Putting a cost in the wrong group.** Wages for the staff you must have are fixed. Commissions and per-order packaging are variable.
- **Using the list price.** Use the average price after discounts.
- **Leaving out the owner's pay.** If you need a wage from the business, include it in the fixed costs.
- **Assuming one product.** With several products, use the average price and variable cost for your mix, and re-check when the mix changes.
- **Treating break-even as a forecast.** It tells you what you need, not what you will get.

## What this calculator cannot do

It works on one steady month and ignores time. It does not show how long it takes to reach break-even, how much cash you burn on the way, or what the loan and the stock you must buy do to the cash balance. A financial model shows the months before break-even, the funding you need to reach the lowest cash point, and Low / Base / High scenarios for price, volume and costs. It ends in lender-ready statements with a Checks sheet that confirms the arithmetic. The [startup costs and break-even guide](/guides/startup-costs-and-break-even-analysis) explains the cash view, and the [startup cost calculator](/calculators/startup-cost-calculator) adds up what you need to open.

## FAQ {#faq}

### What is the break-even point?

It is the sales volume at which total revenue equals total costs, so the profit is zero.

### What is the contribution margin?

It is the share of each sale left after the variable costs. In the example it is 45.0%.

### Can I use it for a service business?

Yes. Treat one hour or one job as a unit, and put the cost of delivering it in the variable cost.

### Why does the result show a dash?

If the price is not above the variable cost, a unit adds nothing to the fixed costs, so no number of units breaks even. The margin of safety also shows a dash when no units are sold today.
