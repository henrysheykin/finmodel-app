---
slug: /business-models/cafe
title: How a Cafe Makes Money: Revenue, Costs, Start-up Funding and Break-Even | StartupModel
description: How a neighborhood cafe makes money, with tables from a working financial model: revenue drivers, costs, start-up funding, unit economics and break-even.
keyword: how does a cafe make money
secondary: [cafe business model, cafe start-up costs, cafe break-even point, coffee shop profit margin, cafe unit economics]
template: cafe
sample: cafe, full, monthly, 5 years
---

# How a cafe makes money

A cafe earns money in a simple way: customers walk in, each spends a few dollars, and what is left after food, staff, rent and everything else is profit. The hard part is that the first two numbers take months to build while rent and payroll start on day one. This page walks through that arithmetic for one illustrative neighborhood cafe, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so treat them as a worked example of how the pieces fit together rather than as a forecast for your own site.

## What the sample cafe assumes

The sample is a small cafe that reaches {{num:drivers.cust_full.base}} customers a day at full traffic, with an average ticket of {{num:drivers.ticket.base}}, open {{num:drivers.days.base}} days a month. The table shows the key numbers a cafe owner can most easily research or negotiate, each with a Low, Base and High value.

{{table:drivers}}

The rest of the model, such as the traffic ramp, wage growth, the loan terms and working capital, sits in the same Inputs sheet and follows the same Low, Base and High pattern.

## Revenue: customers, ticket and days

Cafe revenue is three numbers multiplied together: customers per day, average ticket, and operating days. A new cafe does not open at full traffic. The model starts at a share of full traffic and builds up over a set number of months, then grows a little each year, while prices rise by a fixed percentage a year.

In the Base case revenue is {{num:pnl.rev.y1}} in year 1 and {{num:pnl.rev.y5}} in year 5. The growth comes from the opening ramp, modest traffic growth and yearly price increases.

{{chart:revenue_costs}}

## Costs: what is variable and what is not

Costs fall into two groups. Food and beverage cost moves with sales: it is {{num:costs.cogs.y1}} of revenue in both years, so each extra ticket brings the same margin. Marketing in the sample is also a fixed share of revenue.

Rent, payroll and utilities do not move with sales. They are the reason a quiet first year can leave almost nothing: payroll alone takes {{num:costs.payroll.y1}} of year 1 revenue and falls to {{num:costs.payroll.y5}} by year 5 simply because revenue grows into a similar headcount. The same effect shrinks rent from {{num:costs.rent.y1}} of revenue to {{num:costs.rent.y5}}.

{{table:costs}}

{{chart:cost_structure}}

The full profit and loss shows how those shares turn into profit. EBITDA is {{num:pnl.ebitda.y1}} in year 1 and {{num:pnl.ebitda.y5}} in year 5. Net income is lower because depreciation of the fit-out, interest on the loan and income tax come after EBITDA.

{{table:pnl}}

## Investment: what it takes to open

Before the first coffee is sold the cafe needs fit-out and equipment. The model does not stop at that purchase. It finds the month when cash is lowest, adds up the capital spending, the operating cash burned and the loan repayments paid until then, and adds a cash buffer on top. That total is the funding the owner needs to raise.

{{table:startup}}

In the sample the capital spending is {{num:startup.capex_to_low}}, the operating burn before the cash low point is {{num:startup.burn_to_low}}, and the funding required is {{num:startup.required}}. Equity and the loan bring in {{num:startup.sources}}, so the last row shows the surplus or shortfall against that requirement. A negative number there is the model telling you to raise more or to cut the plan, before a lender or an investor tells you instead.

The U.S. Small Business Administration publishes a [guide to calculating start-up costs](https://www.sba.gov/business-guide/plan-your-business/calculate-your-startup-costs) that is a useful checklist for what to include in your own list.

## Unit economics: one customer at a time

Unit economics for a cafe come down to the ticket and the margin on it. With an average ticket of {{num:drivers.ticket.base}} and food and beverage cost of {{num:drivers.cogs_pct.base}} of sales, the gross margin is {{num:pnl.gm.y1}}, which leaves the rest of each ticket to pay for rent, staff and everything else.

{{table:unit}}

The table also shows customers per day and the average ticket at the end of each year. If the ticket rises with price growth and traffic grows too, revenue per day rises faster than either one alone.

## Break-even: when the cafe pays for itself

Break-even has several meanings, and the model shows each of them separately. The first month with positive EBITDA is {{num:breakeven.first_ebitda}}, and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}. The cash invested is paid back in {{num:breakeven.payback}}.

{{table:breakeven}}

Break-even revenue treats food and beverage cost as variable and operating expenses as fixed, so it is operating expenses divided by gross margin. In year 1 that is {{num:breakeven.be_rev_y1}} against revenue of {{num:pnl.rev.y1}}. It is a simple test, but it shows how far sales can fall before the cafe stops covering its fixed costs.

## How to use Low, Base and High

Every driver in the model has three values, and a single switch on the Dashboard chooses which set the whole workbook uses. Base is your best estimate. Low is a cautious case, with fewer customers, a smaller ticket and higher food cost. High is a good case.

In the sample, customers at full traffic range from {{num:drivers.cust_full.low}} to {{num:drivers.cust_full.high}} a day, and the average ticket from {{num:drivers.ticket.low}} to {{num:drivers.ticket.high}}. Open the downloaded workbook, set the switch to Low and see how the funding requirement and the break-even month move. If Low still works, you have a plan you can defend. If it does not, you know which number to work on first.

## Next steps

Download the sample and trace any figure on this page back to its cell. When you are ready to use your own numbers, the [restaurant and coffee shop financial projections](/models/restaurant-coffee-shop-financial-projections) page describes what the full model includes, and the button below starts a short brief about your cafe.
