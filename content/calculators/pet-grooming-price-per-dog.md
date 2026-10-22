---
slug: /calculators/pet-grooming-price-per-dog
title: Dog Grooming Price Calculator: Price by Dog Size | StartupModel
description: Enter groomer time, supplies and overhead for a small, medium and large dog. Get the price for each size that earns your target margin, the profit on a medium dog and the revenue per groomer per day.
keyword: dog grooming price calculator
template: pet_care
related: [pet-boarding-occupancy-revenue]
---

# Dog grooming price calculator

Grooming is priced by time, and a large dog takes much more of it than a small one. If every size is priced by guesswork, the big dogs quietly lose money. Enter the minutes a groom takes for each size, and your costs; the calculator gives a price for each size that earns the margin you want.

```inputs
- key: min_s
  label: Minutes for a small dog
  unit: min
  default: 45
  min: 0
  max: 600
  step: 5
  format: int
  hint: Bathing, drying, cutting and finishing.
- key: min_m
  label: Minutes for a medium dog
  unit: min
  default: 75
  min: 0
  max: 600
  step: 5
  format: int
- key: min_l
  label: Minutes for a large dog
  unit: min
  default: 110
  min: 0
  max: 600
  step: 5
  format: int
- key: buffer
  label: Minutes between dogs
  unit: min
  default: 15
  min: 0
  max: 120
  step: 5
  format: int
  hint: Cleaning the table and tub, a calm reset and paperwork.
- key: groomer_cost
  label: Groomer cost per hour
  unit: $
  default: 22
  min: 0
  max: 1000
  step: 0.5
  format: money2
  hint: Wage, payroll taxes and benefits for one hour.
- key: overhead_hour
  label: Overhead per working hour
  unit: $
  default: 9
  min: 0
  max: 1000
  step: 0.5
  format: money2
  hint: Rent, water, power, laundry and software per hour the station is in use. Your assumption.
- key: supplies_s
  label: Supplies for a small dog
  unit: $
  default: 3
  min: 0
  max: 1000
  step: 0.25
  format: money2
- key: supplies_m
  label: Supplies for a medium dog
  unit: $
  default: 4.5
  min: 0
  max: 1000
  step: 0.25
  format: money2
- key: supplies_l
  label: Supplies for a large dog
  unit: $
  default: 6.5
  min: 0
  max: 1000
  step: 0.25
  format: money2
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
- key: day_hours
  label: Working hours per groomer per day
  unit: hours
  default: 8
  min: 1
  max: 16
  step: 0.5
  format: number1
```

```outputs
- key: price_s
  label: Price for a small dog
  formula: ((min_s + buffer) / 60 * (groomer_cost + overhead_hour) + supplies_s) / (1 - (margin + fee) / 100)
  format: money2
- key: price_m
  label: Price for a medium dog
  formula: ((min_m + buffer) / 60 * (groomer_cost + overhead_hour) + supplies_m) / (1 - (margin + fee) / 100)
  format: money2
  highlight: true
- key: price_l
  label: Price for a large dog
  formula: ((min_l + buffer) / 60 * (groomer_cost + overhead_hour) + supplies_l) / (1 - (margin + fee) / 100)
  format: money2
- key: profit_m
  label: Profit on a medium dog
  formula: price_m * (1 - fee / 100) - ((min_m + buffer) / 60 * (groomer_cost + overhead_hour) + supplies_m)
  format: money2
- key: dogs_day
  label: Medium dogs per groomer per day
  formula: day_hours * 60 / (min_m + buffer)
  format: number1
- key: rev_day
  label: Revenue per groomer per day, medium dogs
  formula: price_m * dogs_day
  format: money
```

```table
title: Medium-dog price at different target margins
input: margin
values: 20, 25, 30, 35, 40
outputs: price_m, profit_m, rev_day
```

```examples
- name: The starting numbers
  inputs: min_s=45, min_m=75, min_l=110, buffer=15, groomer_cost=22, overhead_hour=9, supplies_s=3, supplies_m=4.5, supplies_l=6.5, margin=35, fee=2.5, day_hours=8
  expect: price_s=54.4, price_m=81.6, price_l=113.733333, profit_m=28.56, dogs_day=5.333333, rev_day=435.2
- name: A mobile groomer with higher costs
  inputs: min_s=60, min_m=90, min_l=130, buffer=30, groomer_cost=26, overhead_hour=14, supplies_s=3.5, supplies_m=5, supplies_l=7.5, margin=40, fee=3, day_hours=8
  expect: price_s=111.403509, price_m=149.122807, price_l=200.292398, profit_m=59.649123, dogs_day=4, rev_day=596.491228
- name: A fast salon with thin overhead
  inputs: min_s=35, min_m=55, min_l=80, buffer=10, groomer_cost=20, overhead_hour=7, supplies_s=2.5, supplies_m=4, supplies_l=5.5, margin=30, fee=2, day_hours=9
  expect: price_s=33.455882, price_m=48.897059, price_l=67.647059, profit_m=14.669118, dogs_day=8.307692, rev_day=406.221719
- name: No time for a medium dog and no break between dogs
  inputs: min_s=45, min_m=0, min_l=110, buffer=0, groomer_cost=22, overhead_hour=9, supplies_s=3, supplies_m=4.5, supplies_l=6.5, margin=35, fee=2.5, day_hours=8
  expect: price_s=42, price_m=7.2, price_l=101.333333, profit_m=2.52, dogs_day=—, rev_day=—
```

## How the grooming price is calculated

Grooming is a service sold by the hour of a groomer and a station. The calculator costs the time for each size and adds supplies:

1. **Time per dog** = minutes for the groom + minutes between dogs.
2. **Cost per dog** = time per dog in hours × (groomer cost per hour + overhead per hour) + supplies.
3. **Price** = cost ÷ (1 − (target margin + fees)).

The minutes between dogs are real. Cleaning the table and tub, calming the next dog and writing up the record take time that nobody pays for unless the price includes it.

With the starting numbers (example values, not benchmarks) a medium dog takes 75 minutes plus 15 between dogs, which is 1.5 hours at $22 for the groomer and $9 for overhead, plus $4.50 of supplies. To keep a margin of 35% after fees of 2.5%, the price is $81.60 and the profit is $28.56. A small dog is priced at $54.40 and a large dog at $113.73. At 90 minutes a dog, a groomer can do 5.3 medium dogs in an 8-hour day, which brings in $435 in a day.

## How to read the result

Look at the prices against each other. The large dog takes much longer than the small one, and its price is about twice as high. If your price list charges only a few dollars more for a large dog than a small one, the large dogs are paying less per hour than the small ones, and the table of prices will show it.

The revenue per groomer per day is the figure to compare with your costs and your booking pattern. It depends on the mix of sizes you actually see, so run it for each size and weight by your appointments. The dogs per day figure also warns when the day is too full: if it is more than the groomer can do without rushing, the quality and the safety of the dogs suffer.

The other examples show the range. A mobile groomer with longer groom times, 30 minutes between dogs and higher overhead needs $149.12 for a medium dog at a margin of 40%, and can do 4.0 dogs a day. A fast salon with 10 minutes between dogs and thin overhead prices a medium dog at $48.90 and does 8.3 a day. They are very different businesses, and each price is right for its own costs.

## Typical mistakes

- **Using one price for every size.** The time differs, so the price should too.
- **Pricing only the groom.** Add the minutes between dogs, and extras such as de-matting or nail work that take longer.
- **Using the wage as the cost of an hour.** Include payroll taxes and benefits.
- **Dividing overhead over the hours you hope to fill.** Use the hours you actually work.
- **Forgetting no-shows and late cancellations.** The empty slot still costs money. A deposit or a cancellation fee can cover it.

## What this calculator cannot do

It prices one groom at a time. It does not know how many dogs you will book, how the mix of sizes changes the day, how much your boarding or retail adds, or what the shop costs before the first booking. A financial model for a pet care business combines grooming, boarding and retail in a monthly forecast with cash and the opening costs, runs Low / Base / High scenarios for bookings and prices, and ends in lender-ready statements with a Checks sheet. For the boarding side, see the [boarding occupancy calculator](/calculators/pet-boarding-occupancy-revenue).

## FAQ {#faq}

### Should I charge by breed or by weight?

Either. Time is what drives cost, and coat type can matter as much as size. Use the calculator with the minutes you actually spend on each type of dog.

### How do I price add-ons?

Add the extra minutes and supplies to a groom and read the price, or price add-ons separately with the same method.

### Does the price include tax or tips?

No. It is before sales tax, and tips belong to the groomer.

### Why does a result show a dash?

If the minutes for a medium dog and the minutes between dogs are both zero, the dogs per day cannot be calculated.
