---
slug: /calculators/auto-repair-parts-margin-per-order
title: Parts Margin and Gross Profit Per Repair Order Calculator | StartupModel
description: Enter labor hours, labor rate, parts cost and parts markup for a typical repair order. Get the parts margin, blended gross profit per order, the monthly profit and the orders needed to break even.
keyword: gross profit per repair order calculator
template: auto_repair
related: [auto-repair-effective-labor-rate]
---

# Parts margin and gross profit per repair order

A repair order earns money twice: on the labor and on the parts. Each has its own cost and its own margin, and the blend decides what the order contributes to the rent and the payroll of the shop. Enter a typical repair order; the calculator shows the margin on the parts, the gross profit of the whole order and how many orders a month the shop needs.

```inputs
- key: hours
  label: Labor hours billed per order
  unit: hours
  default: 2.2
  min: 0
  max: 100
  step: 0.1
  format: number1
- key: rate
  label: Labor rate charged per hour
  unit: $
  default: 120
  min: 0
  max: 1000
  step: 1
  format: money
- key: tech_cost
  label: Technician cost per billed hour
  unit: $
  default: 38
  min: 0
  max: 1000
  step: 0.5
  format: money2
  hint: What an hour of technician time costs you, with payroll costs, per hour billed.
- key: parts_cost
  label: Parts cost per order
  unit: $
  default: 165
  min: 0
  max: 100000
  step: 5
  format: money
  hint: At what you pay your supplier.
- key: markup
  label: Markup on parts
  unit: "%"
  default: 45
  min: 0
  max: 500
  step: 1
  format: percent
  hint: The amount added to the parts cost, as a share of the cost. Your assumption.
- key: orders
  label: Repair orders per month
  default: 320
  min: 0
  max: 100000
  step: 5
  format: int
- key: fixed
  label: Other costs per month
  unit: $
  default: 20000
  min: 0
  max: 100000000
  step: 500
  format: money
  hint: Rent, service writers, utilities, insurance, equipment, marketing.
```

```outputs
- key: labor_sale
  label: Labor sale per order
  formula: hours * rate
  format: money2
- key: labor_gp
  label: Labor gross profit per order
  formula: labor_sale - hours * tech_cost
  format: money2
- key: parts_sale
  label: Parts sale per order
  formula: parts_cost * (1 + markup / 100)
  format: money2
- key: parts_gp
  label: Parts gross profit per order
  formula: parts_sale - parts_cost
  format: money2
- key: parts_margin
  label: Parts margin
  formula: parts_gp / parts_sale * 100
  format: percent
  note: Profit as a share of the parts price; lower than the markup.
- key: ro_sale
  label: Sale per repair order
  formula: labor_sale + parts_sale
  format: money2
- key: ro_gp
  label: Gross profit per repair order
  formula: labor_gp + parts_gp
  format: money2
  highlight: true
- key: ro_gp_pct
  label: Blended gross margin
  formula: ro_gp / ro_sale * 100
  format: percent
- key: profit
  label: Profit per month
  formula: ro_gp * orders - fixed
  format: money
- key: be_orders
  label: Orders per month to break even
  formula: fixed / max(ro_gp, 0)
  format: int
  note: Round up in practice.
```

```table
title: What the parts markup does to the order
input: markup
values: 25, 35, 45, 55, 65
outputs: parts_margin, ro_gp, profit
```

```examples
- name: The starting numbers
  inputs: hours=2.2, rate=120, tech_cost=38, parts_cost=165, markup=45, orders=320, fixed=20000
  expect: labor_sale=264, labor_gp=180.4, parts_sale=239.25, parts_gp=74.25, parts_margin=31.034483, ro_sale=503.25, ro_gp=254.65, ro_gp_pct=50.601093, profit=61488, be_orders=78.539171
- name: A labor-heavy job
  inputs: hours=5, rate=130, tech_cost=40, parts_cost=60, markup=40, orders=150, fixed=18000
  expect: labor_sale=650, labor_gp=450, parts_sale=84, parts_gp=24, parts_margin=28.571429, ro_sale=734, ro_gp=474, ro_gp_pct=64.577657, profit=53100, be_orders=37.974684
- name: A parts-heavy job at a thin markup
  inputs: hours=1, rate=115, tech_cost=36, parts_cost=480, markup=20, orders=200, fixed=20000
  expect: labor_sale=115, labor_gp=79, parts_sale=576, parts_gp=96, parts_margin=16.666667, ro_sale=691, ro_gp=175, ro_gp_pct=25.325615, profit=15000, be_orders=114.285714
- name: An order with no sale
  inputs: hours=0, rate=120, tech_cost=38, parts_cost=0, markup=45, orders=320, fixed=20000
  expect: labor_sale=0, labor_gp=0, parts_sale=0, parts_gp=0, parts_margin=—, ro_sale=0, ro_gp=0, ro_gp_pct=—, profit=-20000, be_orders=—
```

## How the gross profit of a repair order is calculated

A repair order sells labor and parts. Each earns a profit, and the shop earns the sum:

1. **Labor gross profit** = hours billed × (labor rate − technician cost per billed hour).
2. **Parts sale** = parts cost × (1 + markup).
3. **Parts gross profit** = parts sale − parts cost.
4. **Gross profit per order** = labor gross profit + parts gross profit.
5. **Orders to break even** = other costs per month ÷ gross profit per order.

With the starting numbers (example values, not benchmarks) a repair order bills 2.2 hours at $120, which is $264.00, and after the cost of the technician's time the labor gross profit is $180.40. Parts that cost $165 at a markup of 45% sell for $239.25, a gross profit of $74.25. The order sells for $503.25 and earns $254.65, a blended gross margin of 50.6%. At 320 orders a month and $20,000 of other costs, the profit is $61,488 a month, and the shop breaks even at 79 orders.

## Markup and margin

The parts margin is 31.0%, not 45%. The markup is the profit as a share of the cost; the margin is the profit as a share of the price. A markup of 45% on a $165 part adds $74.25, which is 31.0% of the $239.25 selling price. When someone talks about margin on parts, ask which of the two they mean. Quoting one as the other is a common way for a shop to earn less than it thinks.

## How to read the result

The blended gross profit per order says what each car that comes in contributes to the rent, the service writers and everything else. The mix between labor and parts changes it. In the second example a labor-heavy order of 5 hours with $60 of parts earns $474 of gross profit and a margin of 64.6%, because most of the sale is labor. In the third, a parts-heavy order with 1 hour and $480 of parts at a markup of 20% earns $175 on a sale of $691, a margin of 25.3%: the parts margin is 16.7%, and the order carries a lot of money but little profit.

The table shows what the markup on parts does to the parts margin, the profit per order and the profit per month. Parts pricing is where shops differ most, and it is also where customers compare most. A markup that suits a cheap part may not suit an expensive one, so some shops use a sliding scale. Test yours on the typical orders you handle.

## Typical mistakes

- **Mixing up markup and margin.** Check which one a supplier, a manager or a target refers to.
- **Using the list price of parts as the cost.** Use what you pay after discounts and freight.
- **Counting the technician hour at the wage.** Include payroll costs and benefits, and allow for time that is paid but not billed.
- **Averaging very different jobs.** A brake job and an engine rebuild have different mixes. Run typical jobs separately.
- **Ignoring returns and core charges.** Parts returned or lost reduce the margin you actually keep.

## What this calculator cannot do

It describes a typical order in a steady month. It does not show how many orders the bays and technicians can handle, what the shop's labor really earns per paid hour, how the work is spread across the days, or the cash tied up in parts and equipment. A financial model for a repair shop does: bays, technicians, labor and parts in a monthly forecast, cash, Low / Base / High scenarios for orders and prices, and lender-ready statements with a Checks sheet. The [effective labor rate calculator](/calculators/auto-repair-effective-labor-rate) looks at the labor side.

## FAQ {#faq}

### What is a repair order?

It is the record of one job for one customer: the labor and parts sold, with the customer's authorisation. The calculator treats it as the unit of sale.

### What is a good parts markup?

It depends on the part, the supplier and your market. Treat it as your own assumption and test what your orders earn at different levels.

### Is labor or parts more profitable?

Labor usually earns a higher margin, parts a lower margin on a larger sale. The calculator shows both on your numbers.

### Why does the result show a dash?

An order with no sale has no margin to calculate, and a shop with no gross profit per order never breaks even.
