---
slug: /business-models/bakery
title: How a Bakery Makes Money: Retail Counter, Wholesale and Waste | StartupModel
description: How a bakery makes money from its retail counter and wholesale accounts, with tables from a working financial model: waste, payroll, funding and break-even.
keyword: how does a bakery make money
secondary: [bakery business model, bakery profit margin, bakery start-up costs, bakery wholesale accounts, bakery break-even point]
template: bakery
published: 2026-10-22
modified: 2026-10-22
sample: bakery, full, monthly, 5 years
---

# How a bakery makes money

A bakery turns flour, butter and early mornings into products people buy every day. It usually has two kinds of customer. Walk-in customers pay at the counter, one small ticket at a time. Wholesale accounts, such as cafes and restaurants, place a regular weekly order. The counter brings a higher price per item and daily traffic, while wholesale brings volume that is planned in advance. This page walks through that arithmetic for one illustrative bakery, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for your own bakery.

## What the sample assumes

At full traffic the sample serves {{num:drivers.cust_full.base}} walk-in customers a day with an average ticket of {{num:drivers.ticket.base}}. It supplies {{num:drivers.ws_accounts.base}} wholesale accounts, each ordering about {{num:drivers.ws_order.base}} a week. Of the retail products it bakes, {{num:drivers.waste_pct.base}} are not sold. Rent is {{num:drivers.rent.base}} a month and the fit-out and equipment cost {{num:drivers.capex.base}}. The table shows each driver with a Low, Base and High value.

{{table:drivers}}

Ingredient costs, packaging, wages, delivery, equipment replacement and the loan sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: the counter and the accounts

Retail revenue is customers per day times the average ticket times the days the shop is open. Traffic builds up from opening to full traffic, grows each year, and in monthly models has a holiday peak in November and December. Wholesale revenue is the number of accounts times the weekly order value, which ramps up on the same opening curve.

In the sample, retail counter revenue is {{num:unit.rev_retail.y1}} in year 1 and wholesale revenue is {{num:unit.rev_ws.y1}}, so wholesale is {{num:unit.ws_share.y1}} of the total revenue of {{num:pnl.rev.y1}}. By year 5 revenue reaches {{num:pnl.rev.y5}} and wholesale grows to {{num:unit.ws_share.y5}} of it as the number of accounts rises from {{num:unit.accounts.y1}} to {{num:unit.accounts.y5}}.

{{chart:revenue_costs}}

## Costs: ingredients, waste and people

Cost of sales covers ingredients, packaging and the cost of products that were baked but not sold. It takes {{num:costs.cogs.y1}} of revenue in year 1 and leaves a gross margin of {{num:pnl.gm.y1}}. Waste is a bakery-specific cost: products baked for the counter that do not sell. The table of unit economics puts a number on it, {{num:unit.waste_k.y1}} in year 1, or {{num:unit.waste_share.y1}} of retail revenue.

Payroll is the largest cost below gross profit, {{num:costs.payroll.y1}} of revenue in year 1. Bakers start early, counter staff cover opening hours and a manager runs the shop. Rent, utilities for the ovens, wholesale delivery, marketing, card fees and overhead are smaller. Rent and utilities are flat, so they shrink as a share of revenue, from {{num:costs.rent.y1}} for rent in year 1 to {{num:costs.rent.y5}} in year 5, while payroll grows with the team.

{{table:costs}}

{{chart:cost_structure}}

EBITDA is {{num:pnl.ebitda.y1}} in year 1 and {{num:pnl.ebitda.y5}} in year 5, an EBITDA margin of {{num:pnl.ebitda_m.y1}} rising to {{num:pnl.ebitda_m.y5}}. Net income is lower because depreciation of the ovens and fit-out, interest on the loan and income tax come after EBITDA.

{{table:pnl}}

## Investment: ovens, fit-out and a cash buffer

The start-up spend is the fit-out and the equipment: ovens, mixers and display cases. In the sample capital spending until the cash low point is {{num:startup.capex_to_low}}. Operating cash burned until then is {{num:startup.burn_to_low}}. The model then adds a cash buffer of {{num:startup.buffer}} to reach a funding requirement of {{num:startup.required}}.

{{table:startup}}

Equity and a loan bring in {{num:startup.sources}}, so the last row shows a shortfall of {{num:startup.gap|abs}}. Equity and the loan more than cover the total uses of funds of {{num:startup.uses}}, so the shortfall is entirely against the buffer. The lowest cash balance in the plan is {{num:breakeven.min_cash}}, which stays positive but is far below the buffer. A lender or investor would want to see that the owner can survive a slow quarter, which is what the buffer represents. The U.S. Small Business Administration publishes a [guide to calculating start-up costs](https://www.sba.gov/business-guide/plan-your-business/calculate-your-startup-costs) that is a useful checklist for your own list.

## Unit economics: the ticket, the account and prime cost

The retail unit is the transaction: {{num:unit.tx.y1}} of them in year 1 at an average ticket of {{num:unit.ticket.y1}}, rising to {{num:unit.ticket.y5}} in year 5 with price increases. The wholesale unit is the account. Delivery is a cost per drop, so the sample spends {{num:unit.deliv_k.y1}} on delivery in year 1.

{{table:unit}}

Bakeries often look at prime cost, the sum of cost of sales and payroll as a share of revenue. In the sample it is {{num:unit.prime.y1}} in year 1 and {{num:unit.prime.y5}} in year 5. What is left must pay for rent, utilities and everything else, so prime cost is a quick test of whether the recipe, the staffing and the prices work together.

## Break-even: when the bakery pays for itself

The sample is profitable from the start: the first month with positive EBITDA is {{num:breakeven.first_ebitda}} and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}, and the cash invested is paid back in {{num:breakeven.payback}}.

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin: {{num:breakeven.be_rev_y1}} in year 1 against revenue of {{num:pnl.rev.y1}}. The threshold moves with ingredient cost, waste, payroll and rent. A lower waste rate or a higher margin on wholesale lowers it. Customer counts and the ticket decide how far above the threshold the bakery sits.

## Key risks

- **Waste.** Baked products that do not sell are a cost with no revenue.
- **Payroll.** Early shifts and a full counter team are fixed before the customers arrive.
- **Ingredient prices.** A rise cuts the margin on every item unless prices follow.
- **Wholesale concentration.** One large account leaving removes a block of planned volume.
- **Oven and equipment failure.** Replacement spending is part of the plan.

## How to use Low, Base and High

Each driver has three values, and a switch in cell B4 on the Dashboard of the workbook (1 for Low, 2 for Base, 3 for High) picks the case for the whole model. Base is your best estimate. Low is a cautious case with fewer customers, a smaller ticket, fewer wholesale accounts and more waste. High is a good case.

In the sample, customers at full traffic range from {{num:drivers.cust_full.low}} to {{num:drivers.cust_full.high}} a day and the waste rate from {{num:drivers.waste_pct.high}} to {{num:drivers.waste_pct.low}}. Set the switch to Low and check EBITDA and the lowest cash balance.

## Frequently asked questions

### How does a bakery make money?

It sells baked goods at the counter and to wholesale accounts. Ingredients, waste, staff and rent are paid from that revenue, and the rest is profit.

### Why is waste so important?

Everything baked but not sold has already cost ingredients and labor. The model counts it as a cost, so you can see how a change in the waste rate affects the margin.

### Is wholesale worth it?

Wholesale adds planned weekly volume, but it also adds delivery cost. The model shows both streams separately so you can compare them.

### How much does it cost to open a bakery?

It depends on the space and the equipment. The model adds up the fit-out, ovens and early cash needs from your own numbers.

## Next steps

Download the sample and trace any figure on this page back to its cell. For a general checklist, read the [startup costs and break-even guide](/guides/startup-costs-and-break-even-analysis). When you are ready to use your own numbers, the button below starts a short brief about your bakery.
