---
slug: /calculators/auto-repair-effective-labor-rate
title: Effective Labor Rate Calculator for Auto Repair Shops | StartupModel
description: Enter your posted labor rate, technician hours, productivity, efficiency and discounts. See the effective labor rate per paid hour, labor revenue, labor gross profit and the rate you would need.
keyword: effective labor rate calculator
template: auto_repair
related: [auto-repair-parts-margin-per-order]
---

# Effective labor rate calculator

The posted labor rate on the wall is what you charge for an hour of book time. It is not what each hour you pay a technician actually earns. Some paid hours are spent waiting for parts or cleaning the bay, some jobs are done faster or slower than book time, and some labor is discounted or given away. The effective labor rate is the revenue per paid hour after all of that.

```inputs
- key: rate
  label: Posted labor rate per hour
  unit: $
  default: 120
  min: 0
  max: 1000
  step: 1
  format: money
  hint: The rate you charge for one hour of book time.
- key: techs
  label: Technicians
  default: 5
  min: 1
  max: 500
  step: 1
  format: int
- key: hours
  label: Paid hours per technician per month
  unit: hours
  default: 168
  min: 1
  max: 300
  step: 1
  format: int
  hint: The hours you pay for, including time that is not on a repair order.
- key: productive
  label: Share of paid hours on repair orders
  unit: "%"
  default: 85
  min: 1
  max: 100
  step: 1
  format: percent
  hint: Time on repair orders as a share of paid hours. Your assumption.
- key: efficiency
  label: Hours billed per hour worked
  unit: "%"
  default: 105
  min: 1
  max: 250
  step: 1
  format: percent
  hint: Book hours billed divided by hours actually spent on the jobs. Over 100% means faster than book time.
- key: discount
  label: Labor discounted or given away
  unit: "%"
  default: 6
  min: 0
  max: 100
  step: 0.5
  format: percent
  hint: Share of labor value lost to discounts, goodwill work and warranty work you do not get paid for.
- key: tech_cost
  label: Technician cost per paid hour
  unit: $
  default: 38
  min: 0
  max: 1000
  step: 0.5
  format: money2
  hint: Wage, payroll taxes and benefits for one paid hour.
```

```outputs
- key: paid_hours
  label: Paid hours per month
  formula: techs * hours
  format: int
- key: billed_hours
  label: Hours billed per month
  formula: paid_hours * productive / 100 * efficiency / 100
  format: number1
- key: labor_rev
  label: Labor revenue per month
  formula: billed_hours * rate * (1 - discount / 100)
  format: money
- key: elr
  label: Effective labor rate per paid hour
  formula: labor_rev / paid_hours
  format: money2
  highlight: true
  note: Compare with the posted rate.
- key: labor_gp
  label: Labor gross profit per month
  formula: labor_rev - paid_hours * tech_cost
  format: money
- key: labor_gp_pct
  label: Labor gross margin
  formula: labor_gp / labor_rev * 100
  format: percent
- key: rate_needed
  label: Posted rate needed to earn today's posted rate per paid hour
  formula: rate / (elr / rate)
  format: money2
  note: The posted rate at which each paid hour would earn the current posted rate.
```

```table
title: What productivity does to the effective rate
input: productive
values: 70, 75, 80, 85, 90
outputs: billed_hours, elr, labor_gp
```

```examples
- name: The starting numbers
  inputs: rate=120, techs=5, hours=168, productive=85, efficiency=105, discount=6, tech_cost=38
  expect: paid_hours=840, billed_hours=749.7, labor_rev=84566.16, elr=100.674, labor_gp=52646.16, labor_gp_pct=62.254405, rate_needed=143.035938
- name: A shop that bills slower than book time
  inputs: rate=135, techs=3, hours=170, productive=75, efficiency=92, discount=8, tech_cost=40
  expect: paid_hours=510, billed_hours=351.9, labor_rev=43705.98, elr=85.698, labor_gp=23305.98, labor_gp_pct=53.324465, rate_needed=212.665406
- name: A very efficient shop
  inputs: rate=110, techs=8, hours=165, productive=90, efficiency=125, discount=4, tech_cost=36
  expect: paid_hours=1320, billed_hours=1485, labor_rev=156816, elr=118.8, labor_gp=109296, labor_gp_pct=69.69697, rate_needed=101.851852
- name: A zero posted rate
  inputs: rate=0, techs=5, hours=168, productive=85, efficiency=105, discount=6, tech_cost=38
  expect: paid_hours=840, billed_hours=749.7, labor_rev=0, elr=0, labor_gp=-31920, labor_gp_pct=—, rate_needed=—
```

## How the effective labor rate is calculated

The posted rate applies to billed hours, and billed hours are fewer or more than the hours you pay for. The calculator follows an hour of paid time to the revenue it earns:

1. **Paid hours** = technicians × paid hours per technician.
2. **Billed hours** = paid hours × share of paid hours on repair orders × hours billed per hour worked.
3. **Labor revenue** = billed hours × posted rate × (1 − share of labor discounted or given away).
4. **Effective labor rate** = labor revenue ÷ paid hours.

With the starting numbers (example values, not benchmarks) five technicians paid for 168 hours each give 840 paid hours. With 85% of those hours spent on repair orders, and 105 hours billed for every 100 worked, the shop bills 749.7 hours. At a posted rate of $120 and 6% of labor discounted, labor revenue is $84,566 a month. The effective rate is $100.67 per paid hour, well under the $120 on the wall. Against a cost of $38 per paid hour, the labor gross profit is $52,646, a margin of 62.3%.

## How to read the result

The gap between the posted rate and the effective rate is the money that leaks out between the sign and the invoice. Three leaks matter: time paid but not on a repair order (waiting for parts, cleaning, training), the speed of the technicians against book time, and the labor you discount or give away. The table shows how steeply the effective rate depends on the first: every step of the share of time on repair orders moves the billed hours, the rate and the profit together.

The last line turns the gap into a price. To earn $120 for every paid hour in the starting case, the posted rate would have to be $143.04. That is not a recommendation to raise the rate by that much; it shows the size of the leak. Compare the cost of fixing each leak with the effect of a higher rate, and remember that the rate you can charge depends on your market.

The other examples show the contrast. A shop with a posted rate of $135 that works slower than book time, at 92 hours billed per 100 worked, with 75% of time on repair orders and 8% of labor discounted, earns an effective $85.70 per paid hour, and would need a posted rate of $212.67 to earn $135. A very efficient shop with a rate of $110 and 125 hours billed per 100 worked earns $118.80 per paid hour, more than its posted rate.

## Typical mistakes

- **Counting clocked hours as paid hours.** Use the hours you pay for, including time off the repair orders.
- **Mixing flat-rate and actual hours.** Billed hours are book hours; worked hours are the time on the clock.
- **Ignoring warranty and goodwill work.** It is labor you do and do not collect for.
- **Using one technician's speed for the shop.** Average across the technicians, weighted by hours.
- **Forgetting the cost of benefits.** The technician cost per paid hour should include payroll taxes and benefits.

## What this calculator cannot do

It looks at labor in one steady month. It does not show how parts sales add to the order, what the shop's fixed costs are, how many cars you can take in, or when you get paid. A financial model for a repair shop combines labor, parts, technicians and bays in a monthly forecast with cash and Low / Base / High scenarios for volume and rate, and produces lender-ready statements with a Checks sheet. For the parts side and the profit per order, use the [parts margin calculator](/calculators/auto-repair-parts-margin-per-order).

## FAQ {#faq}

### What is book time?

It is the standard time a published guide assigns to a repair. Shops bill the book hours, whether the technician takes more or less time.

### What is the effective labor rate?

It is labor revenue divided by the hours you pay for. It is lower than the posted rate when paid time is not billed or labor is discounted.

### How do I raise it?

Raise the share of time on repair orders, improve speed against book time, discount less, or raise the posted rate. The table shows the first.

### Why does the margin show a dash?

If the posted rate is zero, there is no labor revenue to divide by.
