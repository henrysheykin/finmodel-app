---
slug: /calculators/home-services-job-price
title: Job Price Calculator for Plumbers, HVAC and Trades | StartupModel
description: Enter hours on site, travel, crew size, labor cost, materials and overhead for a job. Get the job cost, the quote that earns your target margin, the profit and the price per hour on site.
keyword: job pricing calculator
template: home_services
related: [home-services-technician-capacity]
---

# Job price calculator: quote a job from its cost

A quote that covers only the hours on site and the materials loses money, because the crew also drives, the van burns fuel and the office has to be paid for. Enter what a typical job takes and costs; the calculator builds the full cost and the price that leaves the margin you want.

```inputs
- key: hours
  label: Hours on site per person
  unit: hours
  default: 3
  min: 0
  max: 1000
  step: 0.25
  format: number2
  hint: The time each worker spends at the customer's property.
- key: travel
  label: Travel and loading hours per person
  unit: hours
  default: 0.75
  min: 0
  max: 100
  step: 0.25
  format: number2
  hint: Driving, picking up parts and loading the van for this job.
- key: crew
  label: People on the job
  default: 2
  min: 1
  max: 50
  step: 1
  format: int
- key: rate
  label: Labor cost per hour
  unit: $
  default: 38
  min: 0
  max: 1000
  step: 1
  format: money
  hint: Wages plus payroll taxes, benefits and insurance for one hour of one worker.
- key: materials
  label: Materials and parts
  unit: $
  default: 140
  min: 0
  max: 10000000
  step: 5
  format: money
  hint: At what you pay, not what you charge.
- key: vehicle
  label: Vehicle and fuel for the job
  unit: $
  default: 18
  min: 0
  max: 100000
  step: 1
  format: money
- key: overhead
  label: Share of overhead for the job
  unit: $
  default: 35
  min: 0
  max: 1000000
  step: 1
  format: money
  hint: Office, insurance, software and tools, spread over your jobs. Your assumption.
- key: margin
  label: Profit margin you want
  unit: "%"
  default: 30
  min: 0
  max: 90
  step: 1
  format: percent
  hint: Profit as a share of the price. Your own target.
```

```outputs
- key: paid_hours
  label: Paid hours on the job
  formula: (hours + travel) * crew
  format: number2
- key: labour
  label: Labor cost
  formula: paid_hours * rate
  format: money
- key: cost
  label: Total cost of the job
  formula: labour + materials + vehicle + overhead
  format: money
- key: price
  label: Quote for your target margin
  formula: cost / (1 - margin / 100)
  format: money
  highlight: true
- key: profit
  label: Profit on the job
  formula: price - cost
  format: money
- key: per_hour
  label: Price per hour of job time
  formula: price / hours
  format: money
  note: The quote divided by the hours on site, whatever the crew size.
```

```table
title: How the length of the job changes the quote
input: hours
values: 2, 3, 4, 5, 6
outputs: cost, price, profit
```

```examples
- name: The starting numbers
  inputs: hours=3, travel=0.75, crew=2, rate=38, materials=140, vehicle=18, overhead=35, margin=30
  expect: paid_hours=7.5, labour=285, cost=478, price=682.857143, profit=204.857143, per_hour=227.619048
- name: A one-person service call
  inputs: hours=1.5, travel=0.5, crew=1, rate=42, materials=25, vehicle=12, overhead=20, margin=40
  expect: paid_hours=2, labour=84, cost=141, price=235, profit=94, per_hour=156.666667
- name: A day-long job for a crew of three
  inputs: hours=8, travel=1, crew=3, rate=36, materials=1200, vehicle=45, overhead=120, margin=25
  expect: paid_hours=27, labour=972, cost=2337, price=3116, profit=779, per_hour=389.5
- name: No hours on site gives no hourly price
  inputs: hours=0, travel=0.75, crew=2, rate=38, materials=140, vehicle=18, overhead=35, margin=30
  expect: paid_hours=1.5, labour=57, cost=250, price=357.142857, profit=107.142857, per_hour=—
```

## How a job is priced

The calculator builds the quote from the full cost of the visit and then adds the margin you want:

1. **Paid hours** = (hours on site + travel and loading hours) × people on the job.
2. **Labor cost** = paid hours × labor cost per hour.
3. **Total cost** = labor + materials + vehicle and fuel + the job's share of overhead.
4. **Quote** = total cost ÷ (1 − target margin).

The division in the last step is deliberate. A margin is a share of the price, so adding 30% to the cost earns less than 30% of the quote. Dividing by (1 − margin) makes the profit exactly the share of the price you set.

With the starting numbers (example values, not benchmarks) two workers spend 3 hours on site and 0.75 hours travelling and loading, which is 7.50 paid hours at $38 an hour. The materials cost $140, the vehicle $18 and the share of overhead $35, so the job costs $478. To keep a margin of 30% the quote is $683 and the profit on the job is $205. Divided by the 3 hours on site, the price is $228 per hour of job time, whatever the crew size. That is much higher than the labor cost of $38, and it is not greed: it is what pays for travel, materials, the van, the office and the profit.

## How to read the result

The price per hour of job time is the number to compare with what customers expect to pay. It looks high because the hour on site carries the hours before and after it, and the overhead. If customers will not pay it, look for the cause: the travel hours, the crew size or the overhead share, rather than cutting the margin first.

The sensitivity table shows the cost, the quote and the profit for jobs of different lengths. Short jobs carry a larger share of fixed per-visit costs such as travel and the overhead share, so their price per hour is higher. A minimum call-out fee exists for that reason. The one-person service call in the second example takes 1.5 hours on site and costs $141, so it needs a quote of $235 at a margin of 40%, which gives a profit of $94 and $157 per hour of job time. A day-long job for a crew of three costs $2,337, with a quote of $3,116 and a profit of $779.

## Typical mistakes

- **Pricing the hours on site only.** Travel, loading and callbacks are paid time.
- **Using the wage as the cost of an hour.** Add payroll taxes, insurance and benefits.
- **Charging materials at cost.** Handling, ordering and warranty returns are costs too; the overhead share or the margin has to cover them.
- **Forgetting the unbillable visits.** Quotes you do not win and calls that turn into nothing are paid for by the jobs you do win.
- **Quoting without a margin.** A job with no margin cannot pay for a bad month.
- **Using one overhead share for every job.** Check it against the actual overhead divided by the actual number of jobs.

## What this calculator cannot do

It prices one visit at a time. It does not know how many jobs you can book, how many technicians you can keep busy, or when you get paid. A financial model for a trades business turns price, jobs and capacity into a monthly forecast with payroll, vehicles and cash, runs Low / Base / High scenarios for volume and pricing, and checks its own arithmetic in a Checks sheet. For the capacity side, use the [technician capacity calculator](/calculators/home-services-technician-capacity).

## FAQ {#faq}

### Should I charge by the hour or per job?

Per job is easier for customers, and an hourly price is useful for open-ended work. Use this calculator to see the price per hour that a per-job quote implies.

### What goes into overhead?

The office, insurance, software, tools, advertising and the pay of people who do not work on jobs. Divide the monthly total by the number of jobs you do, and enter the result.

### Is the quote before tax?

Yes. It is before any sales tax.

### Why does the price per hour show a dash?

If the hours on site are zero, a price per hour of job time cannot be worked out.
