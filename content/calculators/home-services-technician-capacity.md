---
slug: /calculators/home-services-technician-capacity
title: Technician Capacity Calculator: Jobs and Revenue Per Month | StartupModel
description: Enter technicians, hours, the share of time spent on jobs and the length of a job. See jobs and revenue a crew can handle, how loaded it is and how many technicians your bookings need.
keyword: technician capacity calculator
template: home_services
related: [home-services-job-price]
---

# Technician capacity calculator

A technician is paid for the whole shift but sells only the time spent working on jobs. Driving, parts runs, paperwork and callbacks take the rest. Enter your team and the share of the day that earns money; the calculator shows how many jobs and how much revenue that capacity allows, and whether your bookings fit.

```inputs
- key: techs
  label: Technicians
  default: 6
  min: 1
  max: 1000
  step: 1
  format: int
- key: day_hours
  label: Paid hours per technician per day
  unit: hours
  default: 8
  min: 1
  max: 16
  step: 0.5
  format: number1
- key: days
  label: Working days per month
  unit: days
  default: 21
  min: 1
  max: 31
  step: 1
  format: int
  hint: Net of holidays and days off.
- key: productive
  label: Share of paid hours spent on jobs
  unit: "%"
  default: 70
  min: 1
  max: 100
  step: 1
  format: percent
  hint: Time at the customer's property as a share of paid hours. Your assumption.
- key: job_hours
  label: Hours per job
  unit: hours
  default: 2.5
  min: 0
  max: 100
  step: 0.25
  format: number2
  hint: Average time spent on site per job.
- key: rate
  label: Revenue per hour on jobs
  unit: $
  default: 95
  min: 0
  max: 10000
  step: 1
  format: money
  hint: Average revenue earned for each hour spent on jobs.
- key: booked
  label: Jobs booked per month
  default: 240
  min: 0
  max: 1000000
  step: 5
  format: int
  hint: The jobs you expect or have on the calendar.
```

```outputs
- key: paid
  label: Paid hours per month
  formula: techs * day_hours * days
  format: int
- key: billable
  label: Hours on jobs per month
  formula: paid * productive / 100
  format: number1
- key: jobs_cap
  label: Jobs the team can do per month
  formula: billable / job_hours
  format: number1
  highlight: true
- key: rev_cap
  label: Revenue at full capacity
  formula: billable * rate
  format: money
- key: load
  label: Load from the booked jobs
  formula: booked * job_hours / billable * 100
  format: percent
  note: Above 100% means more work is booked than the team can do.
- key: techs_needed
  label: Technicians needed for the booked jobs
  formula: booked * job_hours / (day_hours * days * productive / 100)
  format: number1
  note: Round up in practice.
- key: spare
  label: Jobs of spare capacity
  formula: jobs_cap - booked
  format: number1
  note: Negative means jobs you cannot fit.
```

```table
title: What the share of paid hours on jobs is worth
input: productive
values: 55, 60, 65, 70, 75
outputs: jobs_cap, load, techs_needed
```

```examples
- name: The starting numbers
  inputs: techs=6, day_hours=8, days=21, productive=70, job_hours=2.5, rate=95, booked=240
  expect: paid=1008, billable=705.6, jobs_cap=282.24, rev_cap=67032, load=85.034014, techs_needed=5.102041, spare=42.24
- name: A small team that is overbooked
  inputs: techs=3, day_hours=8, days=22, productive=60, job_hours=3, rate=110, booked=200
  expect: paid=528, billable=316.8, jobs_cap=105.6, rev_cap=34848, load=189.393939, techs_needed=5.681818, spare=-94.4
- name: Short jobs and a larger team
  inputs: techs=12, day_hours=9, days=20, productive=65, job_hours=1.5, rate=85, booked=800
  expect: paid=2160, billable=1404, jobs_cap=936, rev_cap=119340, load=85.470085, techs_needed=10.25641, spare=136
- name: No job length gives no job count
  inputs: techs=6, day_hours=8, days=21, productive=70, job_hours=0, rate=95, booked=240
  expect: paid=1008, billable=705.6, jobs_cap=—, rev_cap=67032, load=0, techs_needed=0, spare=—
```

## How capacity is calculated

A technician's day is not all work on jobs. Drive time, parts runs, paperwork, waiting for customers and callbacks use hours that are paid for but not sold. The calculator takes that into account:

1. **Paid hours per month** = technicians × paid hours per day × working days.
2. **Hours on jobs** = paid hours × the share of paid hours spent on jobs.
3. **Jobs the team can do** = hours on jobs ÷ hours per job.
4. **Revenue at full capacity** = hours on jobs × revenue per hour on jobs.

Then it compares capacity with demand. **Load** is the hours your booked jobs need divided by the hours the team has. **Technicians needed** is the hours the booked jobs need divided by the hours on jobs of one technician.

With the starting numbers (example values, not benchmarks) six technicians working 8 hours a day for 21 days are paid for 1,008 hours. At 70% on jobs that is 705.6 hours, enough for 282.2 jobs of 2.5 hours and $67,032 of revenue at $95 an hour. With 240 jobs booked the team is 85.0% loaded, needs 5.1 technicians and has room for 42.2 more jobs.

## How to read the result

Load is the number to watch. Well below 100% means spare capacity: you can take more work or have paid for people you do not need. Near or above 100% means work is queuing, response times lengthen and customers go elsewhere. The load that is healthy for you depends on how much you value fast response against full diaries, so decide it on purpose.

The share of paid hours on jobs is the lever most firms underrate. The sensitivity table shows what each step in it is worth in jobs, load and technicians. Better routing, a stocked van and fewer callbacks add jobs without adding a salary, which is why they are often worth more than hiring.

The second example shows the other side. Three technicians with 60% on jobs and 3-hour jobs can do 105.6 jobs a month, but 200 are booked: the load is 189.4% and they would need 5.7 technicians. The shortfall is 94.4 jobs, shown as a negative amount of spare capacity.

## Typical mistakes

- **Counting a whole day as billable.** Plan from the hours actually spent on jobs.
- **Using the length of the quote as the length of the job.** Use how long jobs really take, travel excluded.
- **Mixing job types.** A small repair and an installation have different lengths and rates. Run them separately or use a weighted average.
- **Ignoring leave and training.** Use working days net of holidays, sickness and courses.
- **Forgetting the seasons.** Demand for heating and cooling work swings. A yearly average hides the months where the crew is overloaded.

## What this calculator cannot do

It shows one month at a steady level. It does not show how long a new technician takes to become productive, how demand moves through the year, or what the extra payroll, van and tools do to your cash. A financial model plans headcount and revenue month by month, includes vehicles, payroll and the cash cost of growth, runs Low / Base / High scenarios for demand and productivity, and produces statements a lender can read, with a Checks sheet that confirms the totals. To price the jobs, use the [job price calculator](/calculators/home-services-job-price).

## FAQ {#faq}

### What share of paid hours should be on jobs?

It depends on how far you drive, how well you plan routes and how often the van is missing a part. Measure your own for a few weeks and use that.

### Does the calculator count overtime?

Only if you include it in the paid hours per day. Overtime adds hours but usually costs more per hour.

### How do I read a load above 100%?

You have booked more work than the team can do in the month. The excess waits, is moved to later, or needs more people or hours.

### Why does the result show a dash?

If the hours per job are zero, a number of jobs cannot be calculated.
