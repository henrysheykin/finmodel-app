---
slug: /business-models/fitness
title: How a Gym or Fitness Studio Makes Money: Members, Churn and Capacity | StartupModel
description: How a gym or fitness studio makes money, with tables from a working financial model: memberships, churn, capacity, rent, start-up funding and break-even.
keyword: how does a gym make money
secondary: [fitness studio business model, gym profit margin, gym start-up costs, gym break-even point, membership churn gym]
template: fitness
published: 2026-10-21
modified: 2026-10-21
sample: fitness, full, monthly, 5 years
---

# How a gym or fitness studio makes money

A gym or boutique studio sells membership. Members pay a fee every month, and the studio earns a profit when those fees, plus extras such as personal training and retail, cover rent, instructors, equipment upkeep and marketing. Two things make the business unusual. The building is a large fixed cost that you pay whether the floor is busy or empty, and the studio has a ceiling: only so many members fit. This page walks through that arithmetic for one illustrative studio, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for your own studio.

## What the sample assumes

The sample opens with {{num:drivers.members_start.base}} members, each paying {{num:drivers.fee.base}} a month. Every month {{num:drivers.churn_m.base}} of members cancel, and the studio spends {{num:drivers.mkt.base}} a month on marketing to replace them and to grow. The space holds at most {{num:drivers.max_members.base}} members, and rent is {{num:drivers.rent.base}} a month. The table shows each driver with a Low, Base and High value.

{{table:drivers}}

Instructor pay, trainer payouts, equipment maintenance, utilities, personal training sales and price increases sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: members, fee and the capacity ceiling

Membership revenue is the number of members multiplied by the monthly fee. The count moves in two directions. New members join, partly because of paid marketing and partly through referrals and walk-ins, and existing members leave. Cancellations are not a side detail in a gym; they are a constant drain, and a studio with a high cancellation rate spends much of its marketing budget just standing still.

Then comes the ceiling. In the sample the studio ends year 1 with {{num:unit.members.y1}} members, which is {{num:unit.cap.y1}} of capacity, and reaches full capacity of {{num:unit.members.y2}} in year 2. After that, joins are lost because there is no room. Revenue is {{num:pnl.rev.y1}} in year 1, {{num:pnl.rev.y2}} in year 2 and {{num:pnl.rev.y5}} in year 5, so it grows only slowly once the studio is full. Membership fees account for {{num:unit.rev_mem.y1}} of the year 1 total, and personal training, retail and joining fees add {{num:unit.rev_extra.y1}}.

{{chart:revenue_costs}}

## Costs: the fixed building

Rent is the dominant cost. It stays at {{num:drivers.rent.base}} a month however many members you have, so in year 1 it takes {{num:costs.rent.y1}} of revenue and by year 5 only {{num:costs.rent.y5}}. Staff payroll follows the same pattern, at {{num:costs.payroll.y1}} falling to {{num:costs.payroll.y5}}. Marketing, utilities, maintenance, booking software and insurance are smaller. Cost of sales, which in the sample covers instructors, trainer payouts and the cost of retail goods, is {{num:costs.cogs.y1}} of revenue in year 1.

{{table:costs}}

{{chart:cost_structure}}

These fixed costs explain the shape of the profit line. EBITDA is a loss of {{num:pnl.ebitda.y1|abs}} in year 1 because the studio is still filling up, turns positive at {{num:pnl.ebitda.y2}} in year 2 and reaches {{num:pnl.ebitda.y5}} by year 5. Net income lags behind because depreciation of the equipment, interest on the loan and tax come after EBITDA.

{{table:pnl}}

## Investment: fit-out, equipment and the first losses

Before the doors open a studio needs fit-out and equipment, and then it must fund the early months while membership builds. The model adds up capital spending ({{num:startup.capex_to_low}}), the operating cash burned until the cash low point ({{num:startup.burn_to_low}}) and loan repayments, and adds a buffer. The funding required is {{num:startup.required}}.

{{table:startup}}

Equity and a loan bring in {{num:startup.sources}}, so the last row shows a shortfall of {{num:startup.gap|abs}}. The lowest cash balance is only {{num:breakeven.min_cash}}, so this plan runs very close to the edge. The U.S. Small Business Administration publishes a [guide to calculating start-up costs](https://www.sba.gov/business-guide/plan-your-business/calculate-your-startup-costs) that is a useful checklist for your own list.

## Unit economics: what a member is worth

Each member pays a fee, brings a gross margin and stays until they cancel. Lifetime value in the model is the monthly fee times gross margin, divided by the monthly cancellation rate. In year 1 it is {{num:unit.ltv.y1}} per member. The cost of replacing that member is the marketing cost per new member, {{num:unit.cac.y1}} in the sample. Lifetime value is well above that cost, which is what makes marketing worthwhile, but notice how sensitive it is to cancellations: halve them and the value roughly doubles.

{{table:unit}}

The last row, revenue per square foot, is the metric a landlord or lender may ask about. It rises from {{num:unit.rev_sqft.y1}} in year 1 to {{num:unit.rev_sqft.y5}} in year 5 as the studio fills.

## Break-even: when the studio pays for itself

The first month with positive EBITDA is {{num:breakeven.first_ebitda}} and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}. For the payback of the cash invested the answer is "{{num:breakeven.payback}}".

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin, and for year 1 it is {{num:breakeven.be_rev_y1}} against revenue of {{num:pnl.rev.y1}}, so year 1 sits below break-even. Break-even moves when you change the fee, the cancellation rate, the speed of the opening ramp, and above all the rent.

## Key risks

- **High cancellations.** They force you to spend more on marketing just to keep the same member count.
- **Slow opening.** Rent and payroll start on day one, but membership builds over months.
- **The capacity ceiling.** Once full, revenue grows only through price or a second location.
- **A long lease.** Rent is committed whether or not the plan works.
- **Thin cash.** A small delay can use up the buffer.

## How to use Low, Base and High

Each driver has three values, and a switch on the Dashboard of the workbook picks the case for the whole model. Base is your best estimate. Low is a cautious case with fewer starting members, a lower fee and higher cancellations. High is a good case.

In the sample, the fee ranges from {{num:drivers.fee.low}} to {{num:drivers.fee.high}} a month, and monthly cancellations from {{num:drivers.churn_m.high}} to {{num:drivers.churn_m.low}}. Set the switch to Low and look at the lowest cash balance. If it goes negative, the plan needs more funding, a cheaper space or a faster ramp.

## Frequently asked questions

### How does a gym make money?

It collects monthly membership fees, usually with extras such as personal training, classes and retail, and keeps what is left after rent, staff and equipment costs.

### Why do gyms care so much about cancellations?

Members who leave have to be replaced, and finding new members costs marketing money. Lower cancellations mean the same budget grows the studio faster.

### How many members does a studio need to break even?

It depends on your rent, staff and fee. The model finds the break-even revenue from your own cost structure, and you can divide it by the fee to translate it into members.

### What limits a studio's growth?

Space. Once the studio reaches capacity, extra growth comes from higher prices, add-on services or another location.

## Next steps

Download the sample and trace any figure on this page back to its cell. When you are ready to use your own numbers, the [gym and fitness studio financial projections](/models/fitness-studio-financial-projections) page describes what the full model includes, and the button below starts a short brief about your studio.
