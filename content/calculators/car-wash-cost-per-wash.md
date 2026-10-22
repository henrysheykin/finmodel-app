---
slug: /calculators/car-wash-cost-per-wash
title: Cost Per Car Wash Calculator: Full Cost and Profit Per Wash | StartupModel
description: Enter monthly washes, chemical and water cost per wash and your fixed costs. Get the full cost per wash, profit per wash at your average price and the washes a month needed to break even.
keyword: cost per car wash calculator
template: car_wash
related: [car-wash-membership-break-even]
---

# Cost per wash calculator

The cost of a wash is not only the water and chemicals. Every wash also carries a share of the lease, the staff, the equipment loan and the insurance, and that share shrinks as volume grows. Enter your monthly washes and costs; the calculator shows the full cost of one wash, what you earn on it and the volume you need.

```inputs
- key: washes
  label: Washes per month
  default: 9000
  min: 0
  max: 100000000
  step: 100
  format: int
  hint: All washes, members and single washes together.
- key: var_wash
  label: Chemicals, water and power per wash
  unit: $
  default: 0.95
  min: 0
  max: 100
  step: 0.05
  format: money2
  hint: The cost that rises with each wash.
- key: labour
  label: Labor per month
  unit: $
  default: 15000
  min: 0
  max: 100000000
  step: 250
  format: money
  hint: Wages and payroll costs for the attendants and the manager.
- key: rent
  label: Rent or property cost per month
  unit: $
  default: 11000
  min: 0
  max: 100000000
  step: 250
  format: money
- key: other_fixed
  label: Other fixed costs per month
  unit: $
  default: 8000
  min: 0
  max: 100000000
  step: 250
  format: money
  hint: Equipment loan, insurance, marketing, maintenance, software.
- key: avg_price
  label: Average revenue per wash
  unit: $
  default: 8.5
  min: 0
  max: 1000
  step: 0.25
  format: money2
  hint: Total sales divided by the washes, across members and single washes.
```

```outputs
- key: fixed
  label: Fixed costs per month
  formula: labour + rent + other_fixed
  format: money
- key: fixed_per_wash
  label: Fixed cost per wash
  formula: fixed / washes
  format: money2
- key: cost_wash
  label: Full cost per wash
  formula: var_wash + fixed_per_wash
  format: money2
  highlight: true
- key: profit_wash
  label: Profit per wash
  formula: avg_price - cost_wash
  format: money2
- key: profit_month
  label: Profit per month
  formula: profit_wash * washes
  format: money
- key: be_washes
  label: Washes per month to break even
  formula: fixed / max(avg_price - var_wash, 0)
  format: int
  note: Round up in practice.
```

```table
title: How volume changes the cost of a wash
input: washes
relative: -20, -10, 0, 10, 20
outputs: fixed_per_wash, cost_wash, profit_month
```

```examples
- name: The starting numbers
  inputs: washes=9000, var_wash=0.95, labour=15000, rent=11000, other_fixed=8000, avg_price=8.5
  expect: fixed=34000, fixed_per_wash=3.777778, cost_wash=4.727778, profit_wash=3.772222, profit_month=33950, be_washes=4503.311258
- name: A quieter site
  inputs: washes=5000, var_wash=1, labour=12000, rent=9000, other_fixed=7000, avg_price=8
  expect: fixed=28000, fixed_per_wash=5.6, cost_wash=6.6, profit_wash=1.4, profit_month=7000, be_washes=4000
- name: A high-volume tunnel
  inputs: washes=20000, var_wash=0.85, labour=26000, rent=18000, other_fixed=14000, avg_price=7.5
  expect: fixed=58000, fixed_per_wash=2.9, cost_wash=3.75, profit_wash=3.75, profit_month=75000, be_washes=8721.804511
- name: No washes gives no unit cost
  inputs: washes=0, var_wash=0.95, labour=15000, rent=11000, other_fixed=8000, avg_price=8.5
  expect: fixed=34000, fixed_per_wash=—, cost_wash=—, profit_wash=—, profit_month=—, be_washes=4503.311258
- name: Price below the cost of a wash
  inputs: washes=9000, var_wash=0.95, labour=15000, rent=11000, other_fixed=8000, avg_price=0.9
  expect: fixed=34000, fixed_per_wash=3.777778, cost_wash=4.727778, profit_wash=-3.827778, profit_month=-34450, be_washes=—
```

## How the cost of a wash is calculated

A wash has a variable cost, the chemicals, water and electricity it uses, and a share of the fixed costs of running the site:

1. **Fixed costs per month** = labor + rent + other fixed costs.
2. **Fixed cost per wash** = fixed costs ÷ washes per month.
3. **Full cost per wash** = variable cost per wash + fixed cost per wash.
4. **Profit per wash** = average revenue per wash − full cost per wash.
5. **Washes to break even** = fixed costs ÷ (average revenue per wash − variable cost per wash).

With the starting numbers (example values, not benchmarks) a site that does 9,000 washes a month has $34,000 of fixed costs, which is $3.78 per wash. Add $0.95 of chemicals, water and power and the full cost is $4.73. At an average revenue of $8.50 per wash, the profit is $3.77 a wash and $33,950 a month. The site needs 4,503 washes a month to break even.

## How to read the result

The fixed cost per wash is the number that explains the business. The variable cost hardly changes with volume, so almost all of the difference between a good site and a poor one is how many washes share the fixed costs. The table shows this: when volume falls, the fixed cost per wash rises faster than it falls when volume increases, and the profit per month moves much more than the volume does.

The quieter site in the examples does 5,000 washes at $8.00. Its fixed costs of $28,000 come to $5.60 per wash and the full cost is $6.60, leaving $1.40 a wash and $7,000 a month. It needs 4,000 washes to break even, which is most of what it does now. The high-volume tunnel does 20,000 washes at $7.50 with fixed costs of $58,000: $2.90 of fixed cost, a full cost of $3.75, and a profit of $3.75 a wash. It earns the same profit per wash on a lower price because its volume spreads the costs.

Use the average revenue per wash, which blends members and single washes. A member who washes often brings less revenue per wash than a single wash does, so a rising share of members pulls the average down even when the site is healthy. The [membership break-even calculator](/calculators/car-wash-membership-break-even) shows that side.

## Typical mistakes

- **Costing only the chemicals.** The water bill is a small part of the picture; labor and rent matter far more.
- **Using peak-day volume.** Use the average over the month, with the rainy days.
- **Leaving out maintenance and replacement.** Equipment wears, and the cost belongs in the fixed costs.
- **Mixing months with different numbers of days.** Use a typical month.
- **Treating the break-even as safe.** Weather can take a week of washes away. Check how close you are.

## What this calculator cannot do

It shows a steady month at a fixed price. It cannot say how weather and seasons move volume, how your prices and plan mix change the average revenue, or how the equipment loan and the opening costs weigh on cash. A financial model for a car wash builds washes, members, labor and the loan month by month, runs Low / Base / High scenarios for volume and price, and produces lender-ready statements with a Checks sheet. Use the [break-even calculator](/calculators/break-even-calculator) for the general method.

## FAQ {#faq}

### What should be in the fixed costs?

Everything you pay whatever the volume: rent, the staff you need to open, insurance, the equipment loan, maintenance contracts, marketing and software.

### Why is the cost per wash higher in a quiet month?

The fixed costs are the same, but fewer washes share them.

### Does the calculator include sales tax?

No. Enter the average revenue per wash before tax.

### Why does the result show a dash?

With no washes there is no unit cost to calculate. If the revenue per wash is not above the variable cost, no volume breaks even.
