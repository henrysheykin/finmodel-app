---
slug: /models/home-services-financial-projections
title: Home Services & Trades Financial Projections in Excel | StartupModel
description: Financial projections for plumbing, HVAC, electrical, cleaning and landscaping businesses: technician capacity, leads, jobs, vans, cash. Low/base/high scenarios. Built on your numbers.
keyword: plumbing business financial projections
secondary: [hvac business financial projections, home services business plan financial projections, trades business financial model excel, cleaning business financial projections, landscaping business financial projections]
template: home_services
tier: full
page_type: product landing + sample
sample: home_services, full, monthly, 3 years
wave: 3
---

# Home services and trades financial projections

A trades business grows by hiring technicians, and each hire means a van, tools and a few months before the phone rings enough to keep them busy. StartupModel builds home services projections in Excel around technician capacity and job demand, so you can see when you need to hire and what it costs. You get a P&L, cash flow and balance sheet, a low / base / high scenario switch and a Checks sheet. Full costs $349; Light costs $149.

It suits plumbing, HVAC, electrical, cleaning, pest control and landscaping businesses that sell jobs done by their own technicians.

[Download the sample model](#sample) and inspect every formula before you buy.

## Capacity, demand and jobs completed

**Capacity** = technician FTE on payroll × jobs per technician per working day × working days per month. A technician hired in month 7 adds capacity from month 7.

**Demand** = jobs booked from marketing leads + repeat and referral jobs. Leads are marketing spend ÷ cost per lead; booked jobs are leads × booking rate. In monthly models a June–August busy season lifts those three months and lowers the other nine, so the year's demand is unchanged.

**Jobs completed = the lower of demand and capacity.** When demand exceeds capacity the extra jobs are turned away and shown on the Dashboard. That is your hiring signal. With a busy season and tight capacity, the summer cap costs revenue even though the year's demand is the same.

## Revenue and costs

| Line | How it's modelled |
|---|---|
| Job revenue | Jobs completed × average revenue per job; rises once a year |
| Maintenance plans | Average plan members × monthly plan fee |
| Technician payroll | Salary, payroll taxes and benefits, wage growth |
| Materials and parts | % of job revenue |
| Vehicles | Per technician per month |
| Plan visits | % of plan fees |
| Dispatch and office | Roles you add, with salaries and start dates |
| Marketing, software, insurance, rent, card fees | Inputs and % of revenue |
| Van and tools | Capital spending for each technician added beyond those already equipped |

Gross profit is the field margin. Small receivable days reflect that most jobs are paid on completion; raise them if you do commercial work.

## An illustration of the capacity logic

Made-up inputs, not benchmarks. A business with 4 technicians, each completing 2.5 jobs a working day over 21 working days a month, has capacity for 4 × 2.5 × 21 = **210 jobs a month**. If marketing and repeat work generate 240 job requests in a busy month, 30 are turned away. At an average of $440 a job that is $13,200 of revenue the books never show, and the number that tells you a fifth technician is worth hiring. If demand is only 150 jobs in a quiet month, utilisation is 150 ÷ 210 = 71%, and the same four salaries are spread over fewer jobs. The scenario switch lets you see both months in one file.

## Hiring and cash

Each technician added beyond those already equipped brings a van and tools as capital spending in the month of the hire, plus payroll, vehicle and software costs from that month. Revenue arrives only as fast as leads turn into booked jobs. The model puts those timings in the cash flow so you can see how much funding the growth needs, and where the lowest cash point falls.

## Metrics reported

Technicians, job capacity, jobs demanded, jobs completed, utilisation, jobs turned away, marketing cost per booked job, average revenue per job, revenue per technician, plan members and plan revenue, gross profit per job and EBITDA margin.

## What you get

**Full — $349:** Dashboard with the scenario selector and trade metrics; Inputs; monthly detail; annual P&L, cash flow statement and balance sheet; headcount plan; Checks sheet.

**Light — $149:** Inputs, P&L with period detail and the metrics, Checks sheet. Upgrade to Full later by paying the difference.

Before release, every scenario and year is recomputed independently in plain Python and must match the workbook within $1, including technicians, job capacity, jobs and plan revenue. The Checks sheet must show no FAIL.

## Sample {#sample}

The sample is a growing business with seven technicians and two office staff: Full tier, three years of monthly detail, all three scenarios. Cut jobs per technician per day and watch utilisation, turned-away jobs and cash move.

[Download the sample model (.xlsx)](/samples/home_services-full.xlsx)

## What the model doesn't do

- One average ticket for all jobs: no split between service calls, repairs and installations.
- The busy season is fixed to June–August. For heating-led trades set the uplift to 0.
- Maintenance plan members grow at a flat yearly rate, not linked to jobs or churn.
- Vans are bought outright. For leased vans, enter the lease as the vehicle cost per technician.
- No warranty callbacks, customer financing fees or technician commission plans.

## Common mistakes in trades projections

1. **Hiring without demand.** An idle technician costs salary, van and insurance.
2. **Demand without capacity.** Turned-away jobs are revenue you never see in the books.
3. **No van capex.** Each new technician needs equipment before earning anything.
4. **Flat revenue through the year.** Summer peaks stretch capacity.
5. **One scenario.** Show the lender the slow year.

## Questions

**Does it work for a one-person business?**
Yes: start with one technician and add hires over time.

**Can I model a seasonal peak in winter?**
Set the uplift to 0 to remove the summer peak. A winter peak is not available.

**What if the model doesn't fit my business?**
Write to us within 7 days and we refund the full amount.

See also: [Financial projections for a bank loan](/guides/financial-projections-for-bank-loan) · [Professional services projections](/models/professional-services-financial-projections) · [All custom financial models](/models/custom-financial-model)

[Build my trades model — from $149](/start)
