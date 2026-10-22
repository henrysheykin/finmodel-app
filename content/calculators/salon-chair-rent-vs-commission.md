---
slug: /calculators/salon-chair-rent-vs-commission
title: Chair Rental vs Commission Calculator for Salon Owners | StartupModel
description: Compare what a salon owner keeps when a stylist pays chair rent and when the stylist earns a commission. See both results, the break-even rent and the sales at which the two models are equal.
keyword: chair rent vs commission calculator
template: salon
related: [salon-service-price]
---

# Chair rental vs commission calculator

A stylist can work for a salon in two ways. On commission, the salon takes the clients' payments, pays the stylist a share and buys the supplies. On chair rental, the stylist pays a fixed amount for the chair and keeps what they earn. The owner's result and the stylist's result differ a lot between the two. Enter your numbers to compare them.

```inputs
- key: revenue
  label: Service sales per month for the chair
  unit: $
  default: 7000
  min: 0
  max: 10000000
  step: 100
  format: money
  hint: What the stylist is expected to bring in each month.
- key: commission
  label: Commission paid to the stylist
  unit: "%"
  default: 45
  min: 0
  max: 100
  step: 1
  format: percent
  hint: The share of service sales the stylist receives on commission.
- key: payroll_pct
  label: Employer payroll costs on commission pay
  unit: "%"
  default: 10
  min: 0
  max: 60
  step: 0.5
  format: percent
  hint: Employer taxes and insurance that go with the commission. Your assumption.
- key: supplies_pct
  label: Supplies as a share of service sales
  unit: "%"
  default: 6
  min: 0
  max: 60
  step: 0.5
  format: percent
  hint: Colour, products and consumables. The salon pays them on commission; the stylist pays them when renting.
- key: chair_cost
  label: Cost of providing the chair per month
  unit: $
  default: 700
  min: 0
  max: 10000000
  step: 50
  format: money
  hint: The chair's share of rent, utilities, laundry and software.
- key: rent
  label: Chair rent charged per month
  unit: $
  default: 1400
  min: 0
  max: 10000000
  step: 50
  format: money
```

```outputs
- key: owner_comm
  label: Owner keeps on commission
  formula: revenue - revenue * commission / 100 * (1 + payroll_pct / 100) - revenue * supplies_pct / 100 - chair_cost
  format: money
- key: owner_rent
  label: Owner keeps on chair rental
  formula: rent - chair_cost
  format: money
- key: diff
  label: Commission better (+) or rental better (-) for the owner
  formula: owner_comm - owner_rent
  format: money
  highlight: true
- key: stylist_comm
  label: Stylist receives on commission
  formula: revenue * commission / 100
  format: money
- key: stylist_rent
  label: Stylist keeps on chair rental
  formula: revenue - rent - revenue * supplies_pct / 100
  format: money
  note: Before the stylist's own taxes and costs.
- key: rent_equal
  label: Chair rent that matches the commission result
  formula: owner_comm + chair_cost
  format: money
- key: sales_equal
  label: Monthly sales at which the two models are equal
  formula: rent / max(1 - commission / 100 * (1 + payroll_pct / 100) - supplies_pct / 100, 0)
  format: money
  note: Above this, commission pays the owner more; below it, rental does.
```

```table
title: How the stylist's sales change the choice
input: revenue
relative: -30, -15, 0, 15, 30
outputs: owner_comm, owner_rent, diff
```

```examples
- name: The starting numbers
  inputs: revenue=7000, commission=45, payroll_pct=10, supplies_pct=6, chair_cost=700, rent=1400
  expect: owner_comm=2415, owner_rent=700, diff=1715, stylist_comm=3150, stylist_rent=5180, rent_equal=3115, sales_equal=3146.067416
- name: A busy stylist
  inputs: revenue=12000, commission=50, payroll_pct=10, supplies_pct=7, chair_cost=800, rent=1500
  expect: owner_comm=3760, owner_rent=700, diff=3060, stylist_comm=6000, stylist_rent=9660, rent_equal=4560, sales_equal=3947.368421
- name: A new stylist with few clients
  inputs: revenue=3000, commission=40, payroll_pct=10, supplies_pct=6, chair_cost=700, rent=1000
  expect: owner_comm=800, owner_rent=300, diff=500, stylist_comm=1200, stylist_rent=1820, rent_equal=1500, sales_equal=2000
- name: Costs of commission take all the sales
  inputs: revenue=7000, commission=90, payroll_pct=10, supplies_pct=6, chair_cost=700, rent=1400
  expect: owner_comm=-1050, owner_rent=700, diff=-1750, stylist_comm=6300, stylist_rent=5180, rent_equal=-350, sales_equal=—
```

## How the two models are compared

On **commission**, the clients pay the salon. The salon pays the stylist a share of the service sales, adds the employer payroll costs on that pay, buys the supplies and carries the cost of the chair. On **chair rental**, the stylist pays a fixed rent, buys their own supplies and keeps the rest of what clients pay. The calculator puts the two next to each other for one chair:

- **Owner on commission** = sales − commission − payroll costs on the commission − supplies − cost of the chair.
- **Owner on chair rental** = chair rent − cost of the chair.
- **Stylist on commission** = commission. **Stylist on rental** = sales − rent − supplies.

With the starting numbers (example values, not benchmarks) a chair that brings in $7,000 a month pays the stylist $3,150 at 45%. Payroll costs of 10% add to that, and supplies are 6% of sales. After the chair's own cost of $700 the owner keeps $2,415. On rental at $1,400 the owner keeps $700, the rent less the chair's cost, so commission is better for the owner by $1,715 a month. The stylist, who keeps $3,150 on commission, keeps $5,180 on rental before their own taxes and costs.

The last two lines show where the models cross. A rent of $3,115 would give the owner what commission does at these sales, and at a rent of $1,400 the two models are equal when the chair brings in $3,146 a month.

## How to read the result

The owner's gain from commission depends on how much the stylist sells. A busy stylist is worth more to the owner on commission: at $12,000 of sales the owner keeps $3,760, against $700 on rental, a difference of $3,060. A stylist who is only starting out and brings in $3,000 gives the owner $800 on commission, and the difference narrows to $500 on a rent of $1,000.

Look at the sales at which the models are equal. Below it, the rent is worth more than a share of the sales; above it, the commission is. A salon with a full book wants commission, or a higher rent. A salon with empty chairs may prefer the certainty of rent, because the rent is paid even when the chair is quiet. The table shows how fast the choice changes as the stylist's sales move.

The stylist's side matters too. A stylist who earns much more on rental than on commission will want to rent, and a rent that is too high will not find a stylist. Look at both results, not only the owner's.

## Typical mistakes

- **Leaving out payroll costs on commission.** The employer pays taxes and insurance on top of the commission.
- **Ignoring who pays for supplies.** In one model the salon pays; in the other the stylist does.
- **Comparing the rent with the stylist's sales, not the owner's gain.** The owner still carries the cost of the chair.
- **Forgetting the empty chair.** On commission, a quiet month brings the owner little; on rental, the rent still arrives.
- **Treating the legal status as a detail.** Employees and renters are treated differently by tax and labor rules. Check how your local rules apply, with an adviser, before choosing.
- **Using the sales you hope for.** Use the sales a stylist has actually delivered.

## What this calculator cannot do

It compares one chair in one month. It does not show how a new stylist's sales build up over months, what the salon earns from retail products and the front desk, how many chairs you can fill, or how the choice changes your cash. A financial model for a salon builds chairs, stylists, services and products month by month, with cash and Low / Base / High scenarios for bookings, and produces lender-ready statements with a Checks sheet. To price the services themselves, use the [service price calculator](/calculators/salon-service-price).

## FAQ {#faq}

### Which is better for the owner?

It depends on the stylist's sales. Above the break-even sales, commission pays the owner more; below them, rental does. The calculator shows both.

### What counts as the cost of the chair?

Its share of the rent, utilities, laundry, software and insurance. Divide the monthly costs of the room by the number of chairs.

### What if the stylist's commission rises with sales?

Run the calculator at each level of commission and sales, and compare the results.

### Why is the break-even sales figure a dash?

If commission, payroll costs and supplies together take all the sales, no sales level makes commission match the rent.
