---
slug: /calculators/salon-service-price
title: Salon Service Price Calculator: Price From Time and Margin | StartupModel
description: Enter stylist time, chair time, product cost and overhead for a service. Get the price that earns your target margin, the profit per service and the revenue the chair earns per hour.
keyword: salon service price calculator
template: salon
related: [salon-chair-rent-vs-commission]
---

# Salon service price calculator

A haircut or a colour is priced against the time it takes, not only the product it uses. The stylist is paid for the minutes they work, and the chair is occupied for the whole appointment, including the minutes spent waiting for a colour to process. Enter the time and costs of a service; the calculator gives the price that earns the margin you want.

```inputs
- key: active_min
  label: Stylist minutes of active work
  unit: min
  default: 60
  min: 0
  max: 600
  step: 5
  format: int
  hint: The minutes the stylist is hands-on, including consultation and finishing.
- key: chair_min
  label: Minutes the chair is occupied
  unit: min
  default: 90
  min: 0
  max: 600
  step: 5
  format: int
  hint: Active work plus processing time and the reset of the station.
- key: stylist_cost
  label: Stylist cost per hour
  unit: $
  default: 24
  min: 0
  max: 1000
  step: 0.5
  format: money2
  hint: Wage, payroll taxes and benefits for one hour of work.
- key: overhead_hour
  label: Overhead per chair hour
  unit: $
  default: 11
  min: 0
  max: 1000
  step: 0.5
  format: money2
  hint: Rent, utilities, software and insurance divided by the chair hours you open. Your assumption.
- key: product
  label: Product cost for the service
  unit: $
  default: 14
  min: 0
  max: 10000
  step: 0.5
  format: money2
  hint: Colour, treatment and styling product used, at what you pay.
- key: margin
  label: Profit margin you want
  unit: "%"
  default: 35
  min: 0
  max: 80
  step: 1
  format: percent
  hint: Profit as a share of the price. Your own target.
- key: fee
  label: Payment and booking fees
  unit: "%"
  default: 2.5
  min: 0
  max: 10
  step: 0.1
  format: percent
  hint: The share of the price taken by card processing and booking software.
```

```outputs
- key: labour
  label: Stylist cost for the service
  formula: active_min / 60 * stylist_cost
  format: money2
- key: space
  label: Chair overhead for the service
  formula: chair_min / 60 * overhead_hour
  format: money2
- key: cost
  label: Cost of the service
  formula: labour + space + product
  format: money2
- key: price
  label: Price for your target margin
  formula: cost / (1 - (margin + fee) / 100)
  format: money2
  highlight: true
- key: profit
  label: Profit per service
  formula: price * (1 - fee / 100) - cost
  format: money2
- key: per_chair_hour
  label: Revenue per chair hour
  formula: price / (chair_min / 60)
  format: money2
  note: What the chair earns while the service takes place.
```

```table
title: Price at different target margins
input: margin
values: 20, 25, 30, 35, 40
outputs: price, profit, per_chair_hour
```

```examples
- name: The starting numbers
  inputs: active_min=60, chair_min=90, stylist_cost=24, overhead_hour=11, product=14, margin=35, fee=2.5
  expect: labour=24, space=16.5, cost=54.5, price=87.2, profit=30.52, per_chair_hour=58.133333
- name: A men's haircut
  inputs: active_min=30, chair_min=35, stylist_cost=22, overhead_hour=11, product=2, margin=40, fee=2.5
  expect: labour=11, space=6.416667, cost=19.416667, price=33.768116, profit=13.507246, per_chair_hour=57.888199
- name: A full colour with a long processing time
  inputs: active_min=100, chair_min=170, stylist_cost=26, overhead_hour=12, product=38, margin=30, fee=3
  expect: labour=43.333333, space=34, cost=115.333333, price=172.139303, profit=51.641791, per_chair_hour=60.755048
- name: No chair time gives no hourly figure
  inputs: active_min=60, chair_min=0, stylist_cost=24, overhead_hour=11, product=14, margin=35, fee=2.5
  expect: labour=24, space=0, cost=38, price=60.8, profit=21.28, per_chair_hour=—
```

## How a service price is built

A salon service uses three things: the stylist's working time, the chair's time and the product. The calculator costs each one and then works out the price that leaves the margin you want after payment fees:

1. **Stylist cost** = active minutes ÷ 60 × stylist cost per hour.
2. **Chair overhead** = minutes the chair is occupied ÷ 60 × overhead per chair hour.
3. **Cost of the service** = stylist cost + chair overhead + product.
4. **Price** = cost ÷ (1 − (target margin + fees)).

The two time inputs are different on purpose. A colour may need an hour of the stylist's hands and ninety minutes of the chair, because the client sits while the colour develops. The stylist may serve someone else in the gap, but the chair is not available, and the rent is paid for the whole time.

With the starting numbers (example values, not benchmarks) a service with 60 active minutes and 90 chair minutes costs $24.00 in stylist time, $16.50 in chair overhead and $14.00 in product, so $54.50 in all. To keep a margin of 35% after fees of 2.5%, the price is $87.20 and the profit on the service is $30.52. The chair earns $58.13 for each hour it is occupied.

## How to read the result

The revenue per chair hour is the number to compare across services. A short haircut and a long colour can look very different on the price list yet earn about the same per chair hour, or very different amounts. In the examples a men's haircut priced at $33.77 earns $57.89 per chair hour, and a full colour at $172.14 earns $60.76. If one of your services earns far less per chair hour than the others, it is either underpriced or is the service the chair should do less of.

The sensitivity table shows the price at several target margins. A few points of margin change the price by a few dollars, and a few dollars on every service is a large sum over a month. Compare the result with what clients in your area pay and decide whether to adjust the price, the time the service takes, or the product used.

## Typical mistakes

- **Pricing only the product and the stylist's minutes.** The chair and the room cost money for the whole appointment.
- **Using the wage as the cost of an hour.** Add payroll taxes and benefits.
- **Forgetting the minutes between clients.** Reset the station and the consultation are part of the chair time.
- **Spreading overhead over the hours you wish to be busy.** Divide the monthly overhead by the chair hours you actually fill.
- **Copying a competitor's price.** Their costs and time are not yours.
- **Leaving out the cost of product waste.** Colour that is mixed and not used is still paid for.

## What this calculator cannot do

It prices one service in isolation. It cannot say how many appointments you will fill, how the mix of services changes the average ticket, how a new stylist builds a client list, or when cash comes in and goes out. A financial model for a salon combines services, chairs, stylists and product sales in a monthly forecast with cash and the opening costs, runs Low / Base / High scenarios for bookings and prices, and produces lender-ready statements with a Checks sheet. To decide how to employ a stylist, see the [chair rental vs commission calculator](/calculators/salon-chair-rent-vs-commission).

## FAQ {#faq}

### What is the difference between active minutes and chair minutes?

Active minutes are the time the stylist works on the client. Chair minutes are the time the chair is occupied, including waiting for colour to process and resetting the station.

### Should tips be included?

No. Tips belong to the stylist and are not part of the price.

### Does the price include sales tax?

No. It is the price before any sales tax.

### Why does revenue per chair hour show a dash?

If the chair minutes are zero, an hourly figure cannot be worked out.
