---
slug: /business-models/car_wash
title: How a Car Wash Makes Money: Retail Washes, Memberships and Break-Even | StartupModel
description: How an express car wash makes money, with tables from a working financial model: retail washes, unlimited plans, tunnel capacity, site costs, funding and break-even.
keyword: how does a car wash make money
secondary: [car wash business model, express car wash profit margin, car wash start-up costs, car wash membership revenue, car wash break-even point]
template: car_wash
published: 2026-10-22
modified: 2026-10-22
sample: car_wash, full, monthly, 5 years
---

# How a car wash makes money

An express car wash has two kinds of customer. Retail customers pay each time they drive through the tunnel. Members pay a fixed monthly fee for an unlimited plan and come as often as they like. The tunnel, the land and the building are expensive, but once they are in place each extra wash costs very little, so the business is mostly about filling the tunnel. This page walks through that arithmetic for one illustrative site, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for your own site.

## What the sample assumes

At maturity the sample washes {{num:drivers.cars_day.base}} retail cars per operating day at an average price of {{num:drivers.price.base}} per wash, with add-ons on top. It opens with {{num:drivers.members_start.base}} unlimited members paying {{num:drivers.mem_fee.base}} a month, and {{num:drivers.churn_m.base}} of members cancel each month. The site lease is {{num:drivers.lease.base}} a month and the tunnel equipment costs {{num:drivers.capex_equip.base}}. The table shows each driver with a Low, Base and High value.

{{table:drivers}}

Building and site works, pay stations, chemicals, water, electricity, marketing and the loan sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: retail washes and membership fees

Retail revenue is the number of cars per day times the price per wash plus add-ons. The model starts the site at a share of its mature traffic, builds up over a set number of months, and applies a winter dip in monthly models. Membership revenue is a different kind of income. Each member pays the monthly fee whatever they use, so the member count matters more than the number of visits. Members join from a share of retail customers and from direct sign-ups, and a share cancels each month.

In the sample the site performs {{num:unit.washes_day.y1}} washes per operating day in year 1 (retail and member washes together), using {{num:unit.cap_use.y1}} of the tunnel's capacity, and {{num:unit.washes_day.y5}} per day by year 5. Members grow from {{num:unit.members.y1}} at the end of year 1 to {{num:unit.members.y5}} at the end of year 5, so unlimited plan fees go from {{num:unit.mem_rev_share.y1}} of revenue to {{num:unit.mem_rev_share.y5}}. Revenue is {{num:pnl.rev.y1}} in year 1 and {{num:pnl.rev.y5}} in year 5.

{{chart:revenue_costs}}

## Costs: cheap per wash, heavy in fixed cost

Each wash uses chemicals, water and electricity. In the sample that comes to {{num:unit.var_per_wash.y1}} per wash in year 1, and with card fees the cost of sales is {{num:costs.cogs.y1}} of revenue, which leaves a gross margin of {{num:pnl.gm.y1}}. Members make visits that cost money without earning anything extra, so a heavy user is worth less than a light one.

The fixed costs are the real weight. Site payroll is {{num:costs.payroll.y1}} of revenue in year 1 and the lease {{num:costs.lease.y1}}. Maintenance, insurance and other overhead are smaller. Marketing is high at the start, {{num:costs.mkt.y1}} of revenue in year 1, and the sample lets it fall as the member base builds, to {{num:costs.mkt.y5}} by year 5. Fixed costs rise slowly while revenue grows, which is why the EBITDA margin climbs from {{num:costs.ebitda_m.y1}} in year 1 to {{num:costs.ebitda_m.y5}} in year 5.

{{table:costs}}

{{chart:cost_structure}}

EBITDA is a loss of {{num:pnl.ebitda.y1|abs}} in year 1, turns positive at {{num:pnl.ebitda.y2}} in year 2 and reaches {{num:pnl.ebitda.y5}} in year 5. Below EBITDA, depreciation of the equipment and building and interest on the loan are large, so net income turns positive later than EBITDA.

{{table:pnl}}

## Investment: the tunnel, the site and the loan

A car wash is a capital-heavy business. In the sample, capital spending until the cash low point is {{num:startup.capex_to_low}}, which includes the tunnel equipment, building and site works, and pay stations. The model adds the operating cash burned ({{num:startup.burn_to_low}}) and the loan repayments paid until then ({{num:startup.repay_to_low}}), plus a buffer, to get the funding required: {{num:startup.required}}.

{{table:startup}}

Equity and a loan bring in {{num:startup.sources}}, so the last row shows a shortfall of {{num:startup.gap|abs}}. At this scale the loan is the main funding source, so lenders will look closely at the cash flow. The U.S. Small Business Administration describes loan options in its [guide to funding your business](https://www.sba.gov/business-guide/plan-your-business/fund-your-business).

## Unit economics: the wash and the member

The unit is the wash. The table shows how many washes the site performs in a year, the share that come from members, and the revenue per wash ({{num:unit.rev_wash.y1}} in year 1). A member wash earns less than a retail wash: plan fee revenue per member wash is {{num:unit.rev_per_member_wash.y1}} in year 1, against a retail price of {{num:drivers.price.base}}. Members still help, because their fees are paid every month and add predictable revenue. The member share of washes grows from {{num:unit.mem_share.y1}} in year 1 to {{num:unit.mem_share.y5}} in year 5.

{{table:unit}}

Capacity is the other limit. The tunnel can process {{num:unit.cap_washes.y1}} washes a year in the sample, and in year 5 it still has room, with {{num:unit.cap_use.y5}} of capacity used.

## Break-even: when the site pays for itself

The first month with positive EBITDA is {{num:breakeven.first_ebitda}}, and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}, after the early operating losses and the loan repayments paid by then. For the payback of the cash invested the answer is "{{num:breakeven.payback}}".

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin: {{num:breakeven.be_rev_y1}} in year 1 against revenue of {{num:pnl.rev.y1}}. The threshold moves with the lease, payroll, marketing and the cost per wash. Traffic, price and the member count decide how soon revenue reaches it.

## Key risks

- **Slow traffic ramp.** The lease, payroll and loan payments start before the tunnel is busy.
- **Member churn.** Cancellations have to be replaced to hold the member base.
- **Heavy member use.** A member pays a flat fee, so frequent visits earn less per wash and cost more per member in chemicals, water and electricity.
- **Weather.** The sample includes a winter dip, and a harsher season would be worse.
- **Heavy debt.** Loan repayments are fixed and the funding gap is thin.

## How to use Low, Base and High

Each driver has three values, and a switch in cell B4 on the Dashboard of the workbook (1 for Low, 2 for Base, 3 for High) picks the case for the whole model. Base is your best estimate. Low is a cautious case with fewer cars, a lower price, fewer members and more cancellations. High is a good case.

In the sample, mature traffic ranges from {{num:drivers.cars_day.low}} to {{num:drivers.cars_day.high}} cars per day and the starting member base from {{num:drivers.members_start.low}} to {{num:drivers.members_start.high}}. Set the switch to Low and check the lowest cash balance and whether EBITDA still covers the loan.

## Frequently asked questions

### How does a car wash make money?

It charges per wash and for monthly unlimited plans. Chemicals, water and electricity cost little per wash, so revenue after those costs pays for the lease, staff and the loan.

### Why do car washes sell memberships?

A member pays every month whether or not they visit, which makes revenue more predictable. The trade-off is that a frequent visitor earns less per wash and costs more per member, because the fee stays the same while each visit uses chemicals, water and electricity.

### How much does it cost to build an express car wash?

It depends on the site and the equipment. The model adds up equipment, building and site works, pay stations and early losses from your own numbers.

### What is tunnel capacity?

It is the number of washes the tunnel can process in a year. When traffic reaches it, extra demand is lost.

## Next steps

Download the sample and trace any figure on this page back to its cell. For a general checklist, read the [startup costs and break-even guide](/guides/startup-costs-and-break-even-analysis). When you are ready to use your own numbers, the button below starts a short brief about your site.
