---
slug: /business-models/pet_care
title: How a Pet Grooming and Boarding Business Makes Money | StartupModel
description: How a pet grooming and boarding business makes money, with tables from a working financial model: grooming capacity, kennel occupancy, costs, funding and break-even.
keyword: how does a pet grooming business make money
secondary: [pet care business model, dog boarding business profit, pet grooming start-up costs, kennel occupancy revenue, pet care break-even point]
template: pet_care
published: 2026-10-22
modified: 2026-10-22
sample: pet_care, full, monthly, 5 years
---

# How a pet grooming and boarding business makes money

A pet care business usually sells two services under one roof. Grooming sells appointments: a groomer works on one animal at a time, so the capacity of the shop is the number of grooms it can finish in a day. Boarding sells nights: a kennel run is either occupied or empty, so the capacity is the number of runs times the calendar nights. Retail products sell on top of both. This page walks through that arithmetic for one illustrative business, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for your own business.

## What the sample assumes

At maturity the sample completes {{num:drivers.grooms_day.base}} grooming appointments per operating day at an average price of {{num:drivers.groom_price.base}}. It has {{num:drivers.runs.base}} kennel runs, which are occupied on average {{num:drivers.occ.base}} of the nights at maturity and charge {{num:drivers.night_rate.base}} per night. Rent is {{num:drivers.rent.base}} a month. The table shows each driver with a Low, Base and High value.

{{table:drivers}}

Groomer pay, boarding costs, retail sales, the build-out and the loan sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: grooms, nights and retail

Grooming revenue is the number of grooms completed times the average price. Grooms are limited by capacity, which is the lower of what the grooming stations and what the groomers can handle in a day. The shop also does not open at full volume: appointments ramp up over the first months and then grow each year. Boarding revenue is runs times nights times occupancy times the nightly rate. In monthly models the sample makes boarding busier in the summer and in December and gives that back in the other months, so a full year is unchanged.

In the sample the shop completes {{num:unit.grooms.y1}} grooms in year 1, using {{num:unit.groom_use.y1}} of grooming capacity, and boarding occupancy averages {{num:unit.occ_rate.y1}} over the year. Grooming brings in {{num:unit.rev_groom.y1}} and boarding {{num:unit.rev_board.y1}}, so boarding is {{num:unit.board_share.y1}} of revenue. Retail adds {{num:unit.rev_retail.y1}}. Total revenue is {{num:pnl.rev.y1}} in year 1 and {{num:pnl.rev.y5}} in year 5.

{{chart:revenue_costs}}

## Costs: people, premises and a thin cost of sales

Cost of sales covers groomer pay, boarding food, cleaning and laundry, and the products sold. It takes {{num:costs.cogs.y1}} of revenue in year 1, leaving a gross margin of {{num:pnl.gm.y1}}. Groomers receive a small guaranteed base plus a commission on grooming revenue, so part of that cost moves with sales.

Below gross profit, the costs are mostly fixed. Attendants, manager and other payroll are {{num:costs.payroll_nb.y1}} of revenue in year 1 and rent is {{num:costs.rent.y1}}. By year 5 they fall to {{num:costs.payroll_nb.y5}} and {{num:costs.rent.y5}}, because the premises and the team stay the same while revenue grows. Marketing starts at {{num:costs.mkt.y1}} of revenue and falls to {{num:costs.mkt.y5}} as the sample reduces it each year.

{{table:costs}}

{{chart:cost_structure}}

EBITDA is a loss of {{num:pnl.ebitda.y1|abs}} in year 1 while the business ramps up, then turns positive at {{num:pnl.ebitda.y2}} in year 2 and reaches {{num:pnl.ebitda.y5}} in year 5. Net income is lower because depreciation, interest and income tax come after EBITDA.

{{table:pnl}}

## Investment: grooming stations, kennels and fit-out

The start-up spend covers grooming tables, tubs and dryers, the kennel build-out and a fit-out of the premises. Capital spending until the cash low point is {{num:startup.capex_to_low}} in the sample. The model adds the operating cash burned until then ({{num:startup.burn_to_low}}) and the loan repayments paid, plus a buffer, to give the funding required: {{num:startup.required}}.

{{table:startup}}

Equity and a loan bring in {{num:startup.sources}}, which is a surplus of {{num:startup.gap}} over the requirement. That surplus is the margin for a slower opening than planned. The U.S. Small Business Administration publishes a [guide to calculating start-up costs](https://www.sba.gov/business-guide/plan-your-business/calculate-your-startup-costs) that is a useful checklist for your own list.

## Unit economics: the groom and the run-night

Grooming is measured per appointment. Revenue per groom, including retail, is {{num:unit.groom_ticket.y1}} in year 1, and revenue per groomer is {{num:unit.rev_groomer.y1}}. Boarding is measured per available run-night, which combines occupancy and price: the sample earns {{num:unit.revpan.y1}} for each run-night available in year 1, rising to {{num:unit.revpan.y5}} in year 5. An empty run earns nothing, so occupancy matters as much as the nightly rate.

{{table:unit}}

The table also shows capacity. Grooming capacity, the lower of what the stations and the groomers can handle, is {{num:unit.groom_cap.y1}} grooms a year, and the kennels offer {{num:unit.avail_n.y1}} run-nights. In year 5 grooming uses {{num:unit.groom_use.y5}} of its capacity and boarding {{num:unit.occ_rate.y5}} of its nights, so both still have room.

## Break-even: when the business pays for itself

The first month with positive EBITDA is {{num:breakeven.first_ebitda}} and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}, and the cash invested is paid back in {{num:breakeven.payback}}.

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin: {{num:breakeven.be_rev_y1}} in year 1 against revenue of {{num:pnl.rev.y1}}. The threshold moves with the margin on sales, rent and payroll. Appointment volume, occupancy and prices decide how soon revenue gets there.

## Key risks

- **Slow ramp.** Rent and payroll start at once, while appointments and bookings build over months.
- **Empty runs.** Boarding earns only on occupied nights.
- **Seasonality.** Busy periods have to carry the quieter ones.
- **Groomer capacity.** The shop cannot book more grooms than its groomers and stations allow.
- **Fixed premises.** Rent and insurance do not shrink in a quiet month.

## How to use Low, Base and High

Each driver has three values, and a switch in cell B4 on the Dashboard of the workbook (1 for Low, 2 for Base, 3 for High) picks the case for the whole model. Base is your best estimate. Low is a cautious case with fewer appointments, lower prices and lower occupancy. High is a good case.

In the sample, grooms per day range from {{num:drivers.grooms_day.low}} to {{num:drivers.grooms_day.high}} and boarding occupancy from {{num:drivers.occ.low}} to {{num:drivers.occ.high}}. Set the switch to Low and look at the lowest cash balance and the month EBITDA turns positive.

## Frequently asked questions

### How does a pet grooming and boarding business make money?

It sells grooming appointments, nightly boarding and retail products. Groomers, food and cleaning, rent and overhead are paid from that revenue.

### What is boarding occupancy?

It is the share of available run-nights that are booked. A run that is empty for a night earns nothing for that night.

### Why do grooming and boarding work well together?

They use different resources. Grooming needs groomers and stations, while boarding needs runs and attendants. The model treats them as separate revenue streams, so you can see what each contributes.

### How much does it cost to open?

It depends on the premises, the number of runs and the equipment. The model adds up the build-out, equipment and early losses from your own numbers.

## Next steps

Download the sample and trace any figure on this page back to its cell. For a general checklist, read the [startup costs and break-even guide](/guides/startup-costs-and-break-even-analysis). When you are ready to use your own numbers, the button below starts a short brief about your business.
