---
slug: /calculators/services-utilization-hourly-rate
title: Billable Utilization and Hourly Rate Calculator | StartupModel
description: Enter team size, hours, billable utilization, hourly rate and monthly cost. Get billable hours, revenue, profit, the break-even rate and utilization, and the rate that earns your target margin.
keyword: billable utilization calculator
template: services
related: [services-project-price]
---

# Billable utilization and hourly rate calculator

A services firm sells hours, and not every hour it pays for can be sold. Utilization is the share of paid hours that are billed to clients; the hourly rate is what each billed hour earns. Together they decide revenue. Enter your team's hours, its cost and your rate; the results show profit, the rate and utilization at which you break even, and the rate that earns the margin you want.

```inputs
- key: people
  label: People who bill time
  default: 4
  min: 1
  max: 1000
  step: 1
  format: int
  hint: Full-time equivalents who work on client projects.
- key: hours
  label: Paid hours per person per month
  unit: hours
  default: 160
  min: 1
  max: 300
  step: 1
  format: int
  hint: The hours you pay for, including time that cannot be billed.
- key: util
  label: Billable utilization
  unit: "%"
  default: 70
  min: 0
  max: 100
  step: 1
  format: percent
  hint: The share of paid hours billed to clients. Your assumption.
- key: rate
  label: Hourly rate
  unit: $
  default: 95
  min: 0
  max: 10000
  step: 1
  format: money
  hint: The average amount billed per billable hour.
- key: cost
  label: Total cost per month
  unit: $
  default: 36000
  min: 0
  max: 100000000
  step: 500
  format: money
  hint: Salaries and payroll costs of the team plus its share of rent, software and overhead.
- key: target_margin
  label: Profit margin you want
  unit: "%"
  default: 20
  min: 0
  max: 90
  step: 1
  format: percent
  hint: Profit as a share of revenue. Your own target.
```

```outputs
- key: capacity
  label: Paid hours per month
  formula: people * hours
  format: int
- key: billable
  label: Billable hours per month
  formula: capacity * util / 100
  format: number1
- key: revenue
  label: Revenue per month
  formula: billable * rate
  format: money
- key: profit
  label: Profit per month
  formula: revenue - cost
  format: money
- key: profit_pct
  label: Profit margin
  formula: profit / revenue * 100
  format: percent
- key: be_rate
  label: Break-even hourly rate
  formula: cost / billable
  format: money2
  note: The rate at this utilization that covers the cost and nothing more.
- key: be_util
  label: Break-even utilization
  formula: cost / (capacity * rate) * 100
  format: percent
  note: The utilization at this rate that covers the cost and nothing more.
- key: rate_target
  label: Hourly rate for your profit margin
  formula: cost / (1 - target_margin / 100) / billable
  format: money2
  highlight: true
```

```table
title: What utilization does to the month
input: util
values: 50, 60, 70, 80, 90
outputs: revenue, profit, rate_target
```

```examples
- name: The starting numbers
  inputs: people=4, hours=160, util=70, rate=95, cost=36000, target_margin=20
  expect: capacity=640, billable=448, revenue=42560, profit=6560, profit_pct=15.413534, be_rate=80.357143, be_util=59.210526, rate_target=100.446429
- name: A two-person consultancy
  inputs: people=2, hours=150, util=60, rate=140, cost=21000, target_margin=25
  expect: capacity=300, billable=180, revenue=25200, profit=4200, profit_pct=16.666667, be_rate=116.666667, be_util=50, rate_target=155.555556
- name: A busy agency below its cost
  inputs: people=10, hours=160, util=85, rate=60, cost=95000, target_margin=15
  expect: capacity=1600, billable=1360, revenue=81600, profit=-13400, profit_pct=-16.421569, be_rate=69.852941, be_util=98.958333, rate_target=82.179931
- name: Nothing billed gives no rate
  inputs: people=4, hours=160, util=0, rate=95, cost=36000, target_margin=20
  expect: capacity=640, billable=0, revenue=0, profit=-36000, profit_pct=—, be_rate=—, be_util=59.210526, rate_target=—
```

## How utilization and rate set the result

A services business has a fixed capacity: the hours it pays its people for. Only a share of those hours can be sold. The calculator follows the hours to the money:

1. **Paid hours** = people × paid hours per person.
2. **Billable hours** = paid hours × utilization.
3. **Revenue** = billable hours × hourly rate.
4. **Profit** = revenue − total cost.

Then it turns the question round twice. The **break-even rate** is the total cost divided by the billable hours, and the **break-even utilization** is the total cost divided by the revenue you would earn if every paid hour were billed at your rate. The **rate for your margin** is the total cost divided by (1 − target margin), divided by the billable hours.

With the starting numbers (example values, not benchmarks) four people paid for 160 hours each give 640 paid hours. At 70% utilization that is 448 billable hours, and at $95 an hour the revenue is $42,560. Against a cost of $36,000 the profit is $6,560, a margin of 15.4%. The business breaks even at a rate of $80.36 or a utilization of 59.2%. To earn a 20% margin at 70% utilization it needs an hourly rate of $100.45.

## How to read the result

Utilization and rate pull on the same lever from two sides, and the table shows how steeply. Each step of utilization moves revenue and profit by the same amount, because the cost does not change. Rate is more powerful still: a dollar on the rate applies to every billable hour, and nothing extra has to be sold.

Look at the break-even utilization first. It tells you how much room there is. A firm with break-even utilization close to its actual utilization is one slow month from a loss. In the third example ten people at 85% utilization and a $60 rate earn $81,600 against a cost of $95,000; the break-even utilization is 99.0%, which is not achievable in practice, so the only fix is a higher rate or a lower cost.

Utilization is a measure of the business, not a target to push to 100%. Time for sales, training, admin and holidays is real. A firm that drives staff to the limit loses people, quality and the time to win the next job. Set a level you can sustain and price from it.

## Typical mistakes

- **Counting all hours as paid hours of work.** Use the hours you pay for, including holiday and sickness, or the utilization will be overstated.
- **Leaving overhead out of the cost.** The rate has to carry rent, software, insurance and the time of the partners who do not bill.
- **Mixing rates.** If juniors bill at one rate and seniors at another, enter the average, weighted by hours.
- **Using the quoted rate instead of the realized rate.** Discounts and write-offs lower the average. Use what you actually collected per billable hour.
- **Treating the owner's time as free.** Put a fair salary for the owner into the cost.

## What this calculator cannot do

It describes one steady month. It does not know that utilization falls when the team grows ahead of the work, that new hires take months to become productive, or that clients pay 30 or 60 days after you bill them. A financial model shows hiring and revenue month by month, cash and the working capital that late payments tie up, and Low / Base / High scenarios for utilization and rate. It ends in lender-ready statements and a Checks sheet. To price a single fixed-fee job from the same logic, use the [project price calculator](/calculators/services-project-price).

## FAQ {#faq}

### What is billable utilization?

It is the share of the hours you pay for that are billed to clients. If a team is paid for 640 hours and bills 448 of them, its utilization is 70%.

### Should I include the owner in the people who bill?

Include the owner only for the hours they actually bill, as a fraction of a person, and include their pay in the cost either way.

### What is the difference between break-even rate and target rate?

The break-even rate covers the costs and nothing more. The target rate also earns the profit margin you enter.

### Why does the result show a dash?

With zero utilization there are no billable hours, so a rate per hour cannot be worked out.
