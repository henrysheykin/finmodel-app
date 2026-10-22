---
slug: /business-models/home_services
title: How a Home Services Business Makes Money: Jobs, Technicians, Margins | StartupModel
description: How a plumbing, HVAC or other home services business makes money, with tables from a working financial model: job revenue, technician capacity, marketing cost and break-even.
keyword: how does a home services business make money
secondary: [home services business model, plumbing business profit margin, hvac business start-up costs, home services unit economics, trades business break-even]
template: home_services
published: 2026-10-21
modified: 2026-10-21
sample: home_services, full, monthly, 5 years
---

# How a home services business makes money

A plumbing, heating, electrical or cleaning company earns money one job at a time. A homeowner calls, a technician arrives, the work is done and the customer pays. What is left after the technician's wages, parts, vehicles, office and advertising is the profit. The business is simple to describe but easy to run badly, because the same technician is both the main cost and the only source of revenue. This page walks through the arithmetic for one illustrative company, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for your own company.

## What the sample assumes

The sample earns {{num:drivers.ticket.base}} per job on average, and each technician completes {{num:drivers.jobs_per_tech.base}} jobs per working day. The company spends {{num:drivers.mkt.base}} a month on marketing, pays {{num:drivers.cpl.base}} for each lead, and books {{num:drivers.booking.base}} of those leads as jobs. Materials and parts cost {{num:drivers.materials_pct.base}} of job revenue. The table shows each driver with a Low, Base and High value.

{{table:drivers}}

Wages, vehicles, insurance, rent, price increases and the loan sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: leads, jobs and ticket size

Revenue starts with leads. Marketing spend divided by the cost per lead gives the number of enquiries. A share of them book a job, and each job brings in the average ticket. That chain is why a home services owner watches three numbers closely: cost per lead, booking rate and ticket. Repeat and referral jobs add to the jobs that paid leads bring, without extra lead cost. Capacity is the second limit. Even with plenty of leads, a company can complete only as many jobs as its technicians have time for.

In the sample the company completes {{num:unit.jobs.y1}} jobs in year 1 against a capacity of {{num:unit.cap_jobs.y1}}, which is {{num:unit.util.y1}} technician utilisation. Revenue is {{num:pnl.rev.y1}} in year 1 and {{num:pnl.rev.y5}} in year 5. Part of it is recurring: maintenance plan members pay a fixed fee, and in year 1 the plans bring in {{num:unit.plan_rev.y1}}, or {{num:unit.plan_share.y1}} of revenue.

{{chart:revenue_costs}}

## Costs: the technician is the business

The largest cost is the cost of delivery: technician pay, vehicles and the materials used on each job. In the sample it takes {{num:costs.cogs.y1}} of revenue in year 1, leaving a gross margin of {{num:pnl.gm.y1}}. Marketing is next at {{num:costs.mkt.y1}}, followed by dispatch and office payroll at {{num:costs.payroll_nb.y1}}. Card fees, rent, insurance, licences and software are smaller items.

{{table:costs}}

{{chart:cost_structure}}

Most of these costs are semi-fixed. A technician is paid whether the schedule is full or empty, so margin improves when each day is booked more fully. In the sample, gross margin rises to {{num:pnl.gm.y5}} by year 5 and EBITDA from {{num:pnl.ebitda.y1}} to {{num:pnl.ebitda.y5}}. Net income is lower because depreciation, interest and income tax come after EBITDA.

{{table:pnl}}

## Investment: vans, tools and working cash

The up-front spending is modest. The sample pays for a small shop and equipment at the start, and then a van and tools for each technician it adds. The capital spending before the cash low point is {{num:startup.capex_to_low}}. The operating side is slightly positive in the early months, with {{num:startup.burn_to_low|abs}} coming in rather than going out, because customers pay within days of the job. After adding a cash buffer, the funding required is {{num:startup.required}}.

{{table:startup}}

Equity and a loan bring in {{num:startup.sources}}, so the sample has a surplus of {{num:startup.gap}} over the requirement. Trade businesses often need licences and insurance before the first job, and requirements differ by state and trade. The U.S. Small Business Administration has a [guide to business licenses and permits](https://www.sba.gov/business-guide/launch-your-business/apply-licenses-permits) as a starting point.

## Unit economics: one job at a time

The unit is the job. The table shows revenue per job ({{num:unit.rev_job.y1}} in year 1), gross profit per job ({{num:unit.gp_job.y1}}), and revenue per technician ({{num:unit.rev_tech.y1}}). Gross profit per job is all gross profit divided by jobs, so it already includes the cost of technicians, parts and vehicles. What is left must pay for marketing, the office and overhead.

{{table:unit}}

A useful test is to compare gross profit per job with what it costs to win that job: the cost per lead divided by the booking rate. If the first is much larger than the second, each extra job adds to profit. If they are close, growth just adds work.

## Break-even: when the business pays for itself

The first month with positive EBITDA is {{num:breakeven.first_ebitda}} and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}, and the cash invested is paid back in {{num:breakeven.payback}}.

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin. In year 1 that is {{num:breakeven.be_rev_y1}} against revenue of {{num:pnl.rev.y1}}. The break-even revenue figure moves with the ticket, materials cost, technician wages and overhead. The cost per lead and the booking rate decide how many jobs your marketing budget buys, so they change how soon revenue reaches that threshold rather than the threshold itself.

## Key risks

- **Idle technicians.** Wages continue when the schedule has gaps.
- **Rising cost per lead.** Online lead sources get more expensive as competitors bid.
- **Seasonality.** The sample has a busy summer season, and the quiet months have to be funded from it.
- **Technician turnover.** A skilled person leaving cuts capacity at once.
- **Callbacks and warranty work.** Return visits cost technician time and bring no revenue.

## How to use Low, Base and High

Each driver has three values, and a switch in cell B4 on the Dashboard of the workbook (1 for Low, 2 for Base, 3 for High) picks the case for the whole model. Base is your best estimate. Low is a cautious case with a smaller ticket, fewer jobs per day and costlier leads. High is a good case.

In the sample, the ticket ranges from {{num:drivers.ticket.low}} to {{num:drivers.ticket.high}} and the booking rate from {{num:drivers.booking.low}} to {{num:drivers.booking.high}}. Set the switch to Low and look at EBITDA and the lowest cash balance. If the company still pays its way, you have a plan you can defend.

## Frequently asked questions

### How does a home services business make money?

It charges customers for jobs, covers technician wages, parts and vehicles from that revenue, and keeps what is left after marketing and overhead.

### Why does technician utilisation matter?

Wages are paid for the whole day, so every empty slot lowers profit. Higher utilisation spreads fixed costs over more jobs.

### Are maintenance plans worth offering?

They bring recurring revenue and a reason for customers to call you first. The model shows the plan members and plan revenue separately so you can test the effect.

### How much does it cost to start?

It depends on the trade, the number of vehicles and local licensing. The model calculates the funding required from your own plan.

## Next steps

Download the sample and trace any figure on this page back to its cell. When you are ready to use your own numbers, the [home services financial projections](/models/home-services-financial-projections) page describes what the full model includes, and the button below starts a short brief about your company.
