---
slug: /calculators/cafe-table-turnover-revenue
title: Table Turnover Calculator: Revenue Per Seat and Per Day | StartupModel
description: Enter seats, how many times each seat is filled a day and the average spend per guest. See guests, daily and monthly sales, sales per seat and the turns a sales target needs.
keyword: table turnover calculator
template: cafe
related: [cafe-break-even-covers, cafe-prime-cost, cafe-menu-price]
guide: /guides/restaurant-break-even-analysis
---

# Table turnover calculator: revenue from your seats

Table turnover is the number of times a seat is filled during a day. Multiply it by the number of seats and the average spend and you have the sales a room can produce. Enter your numbers; the guests, the sales and the turns a sales target would need update as you type.

```inputs
- key: seats
  label: Seats
  default: 40
  min: 1
  max: 1000
  step: 1
  format: int
  hint: Seats guests can actually use, not the fire-code maximum.
- key: turns
  label: Seat turns per day
  unit: per day
  default: 2.5
  min: 0
  max: 20
  step: 0.1
  format: number1
  hint: How many guests, on average, sit in each seat during a day. An example value.
- key: spend
  label: Average spend per guest
  unit: $
  default: 22
  min: 0
  max: 1000
  step: 0.5
  format: money2
  hint: Sales divided by paying guests, before sales tax or VAT.
- key: hours
  label: Hours open per day
  unit: hours
  default: 10
  min: 1
  max: 24
  step: 0.5
  format: number1
- key: days
  label: Days open per month
  unit: days
  default: 28
  min: 1
  max: 31
  step: 1
  format: int
- key: target
  label: Sales target per month
  unit: $
  default: 90000
  min: 0
  max: 100000000
  step: 1000
  format: money
  hint: The monthly sales you want the room to reach.
```

```outputs
- key: guests_day
  label: Guests per day
  formula: seats * turns
  format: int
- key: sales_day
  label: Sales per day
  formula: guests_day * spend
  format: money
- key: sales_month
  label: Sales per month
  formula: sales_day * days
  format: money
  highlight: true
- key: per_seat
  label: Sales per seat per month
  formula: sales_month / seats
  format: money
- key: minutes
  label: Minutes of opening time per seat turn
  formula: hours * 60 / turns
  format: int
  note: The average time a seat has to produce one guest's spend.
- key: turns_needed
  label: Seat turns per day for the sales target
  formula: target / (seats * spend * days)
  format: number2
  note: Compare with your seat turns today.
```

```table
title: What each seat turn is worth
input: turns
values: 1.5, 2, 2.5, 3, 3.5
outputs: guests_day, sales_month, minutes
```

```examples
- name: The starting numbers
  inputs: seats=40, turns=2.5, spend=22, hours=10, days=28, target=90000
  expect: guests_day=100, sales_day=2200, sales_month=61600, per_seat=1540, minutes=240, turns_needed=3.652597
- name: A small cafe with quick turns
  inputs: seats=18, turns=4, spend=9.5, hours=9, days=30, target=40000
  expect: guests_day=72, sales_day=684, sales_month=20520, per_seat=1140, minutes=135, turns_needed=7.797271
- name: A restaurant open for dinner only
  inputs: seats=60, turns=1.5, spend=48, hours=5, days=26, target=150000
  expect: guests_day=90, sales_day=4320, sales_month=112320, per_seat=1872, minutes=200, turns_needed=2.003205
- name: No turns and no spend give no answer
  inputs: seats=40, turns=0, spend=0, hours=10, days=28, target=90000
  expect: guests_day=0, sales_day=0, sales_month=0, per_seat=0, minutes=—, turns_needed=—
```

## How table turnover revenue is calculated

A room has a fixed number of seats and a fixed number of hours, so its sales have a ceiling. The calculator builds that ceiling in four steps:

1. **Guests per day** = seats × seat turns per day.
2. **Sales per day** = guests per day × average spend per guest.
3. **Sales per month** = sales per day × days open.
4. **Sales per seat** = sales per month ÷ seats, which lets you compare a 40-seat room with a 60-seat one.

With the starting numbers (example values, not benchmarks) 40 seats turned 2.5 times a day serve 100 guests. At an average spend of $22 that is $2,200 a day and $61,600 a month, or $1,540 for every seat. The line "minutes of opening time per seat turn" divides the hours you are open by the turns: ten hours and 2.5 turns leave 240 minutes of opening time for each guest's visit.

The last result turns the question round. If you want $90,000 a month, the room needs about 3.65 seat turns a day at the same spend, against the 2.5 you started with. That gap is the real question for a seating plan, a menu or a booking system: do you raise the turns, raise the spend, or add seats?

## Seat turns, table turns and covers

People use "table turnover" in two ways. **Table turns** count how often a table is reseated. **Seat turns** count how often a seat is. This calculator uses seats, because a table for four that is often occupied by two wastes two seats, and counting seats shows it. If you only know table turns, multiply by the average party size and divide by seats per table to get a rough seat figure, and say which one you used when you compare with another venue.

## How to read the result

The table above shows what one more seat turn is worth in guests and in monthly sales. It also shows that every extra turn takes opening time away from each guest, which is why turnover and spend pull against each other. A $48 dinner can sit for a long evening and a $9.50 coffee cannot, so the two sets of examples on this page turn very differently: a small cafe at 4 turns serves 72 guests a day from 18 seats, and a dinner room at 1.5 turns serves 90 from 60.

Use the result as a ceiling check. If the sales you need to cover your costs are above what your seats can produce at a believable turn and spend, no amount of cost cutting fixes the plan; the room is too small, the price is too low, or both.

## Typical mistakes

- **Using the busiest night as the average.** Turns on a Saturday are not turns on a Tuesday. Use an average over a typical week.
- **Counting seats you never put out.** Bar stools, a patio closed in winter and a back room used for events belong in a separate calculation.
- **Forgetting that spend changes with speed.** Pushing guests through faster can lower what each one orders.

## What this calculator cannot do

It gives one steady month. It does not know that a new place builds up over several months, that summer and winter differ, or that sales have costs attached. A financial model keeps these apart: monthly figures for the ramp-up, cash for the weeks before steady trade, and Low / Base / High scenarios for turns and spend, so you can see which assumption the plan depends on. It also checks its own arithmetic and produces statements a lender or investor can read. To test the cost side, use the [prime cost calculator](/calculators/cafe-prime-cost) or the [menu price calculator](/calculators/cafe-menu-price). The [break-even guide](/guides/restaurant-break-even-analysis) explains how the pieces fit together.

## FAQ {#faq}

### What is a good table turnover rate?

It depends on the concept, the hours and the spend per guest, so there is no single figure to copy. Use the rate you actually see across a typical week and test what the plan needs against it with the sales target field.

### How do I count seat turns?

Divide the number of guests served in a day by the number of seats. If you served 100 guests with 40 seats, the seat turns for that day are 2.5. Average several days.

### Why does a result show a dash?

The sales target needs a spend above zero, and the minutes line needs turns above zero. With either at zero the calculation has no answer, so it shows a dash.
