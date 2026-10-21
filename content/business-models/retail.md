---
slug: /business-models/retail
title: How a Retail Business Makes Money: Margin, Inventory and Break-Even | StartupModel
description: How a retail business makes money online and in stores, with tables from a working financial model: margin, ad spend, inventory, funding need and break-even.
keyword: how does a retail business make money
secondary: [retail business model, ecommerce business model, retail startup costs, retail break-even point, retail inventory turnover]
template: retail
published: 2026-10-21
modified: 2026-10-21
sample: retail, full, monthly, 5 years
---

# How a retail business makes money

A retailer buys products, marks them up and sells them for more than they cost. The difference pays for shipping, staff, advertising and rent, and what is left is profit. It sounds simple, but a retailer also has to pay for stock before it is sold, which ties up cash. This page walks through the arithmetic for one illustrative business that sells through a website and a few physical stores, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for your own business.

## What the sample assumes

The online side of the sample draws {{num:drivers.visits.base}} website visits a month from non-paid sources in year 1. About {{num:drivers.conv.base}} of visits turn into an order, and the average order is {{num:drivers.aov.base}}. On top of that the business spends {{num:drivers.ad_budget.base}} a month on paid ads and runs {{num:drivers.stores.base}} stores from the start. Product cost is {{num:drivers.cogs_pct.base}} of net sales in the Base case.

{{table:drivers}}

Return rates, repeat buying, shipping costs, store openings, payroll and the loan sit in the same Inputs sheet and follow the same Low, Base and High pattern.

## Revenue: traffic, conversion and order value

Online revenue is a chain of three numbers: visitors, the share that buy, and how much each order is worth. Paid ads add visitors on top of the free ones. Stores add a separate stream, and repeat customers add orders without any extra acquisition cost. Small changes in the conversion rate or the order value feed straight through the chain, so they matter more than most owners expect.

In the Base case net sales are {{num:pnl.rev.y1}} in year 1 and {{num:pnl.rev.y5}} in year 5. In year 1 the website brings in {{num:unit.online.y1}} of gross sales from {{num:unit.orders.y1}} orders, and the stores bring in {{num:unit.store.y1}}. The number of stores grows from {{num:unit.stores.y1}} at the end of year 1 to {{num:unit.stores.y5}} at the end of year 5.

{{chart:revenue_costs}}

## Costs: the product, the parcel and the shop

Costs split into three groups. The first is the product itself. It moves with sales, and in the sample it leaves a gross margin of {{num:pnl.gm.y1}}. The second group is what it costs to get an order to the customer and to find the customer: fulfilment and shipping take {{num:costs.fulfil.y1}} of revenue in year 1, payment processing {{num:costs.payment.y1}} and paid ads {{num:costs.ads.y1}}. The third group is fixed: payroll at {{num:costs.payroll.y1}}, plus store rent, store running costs, software and general overhead.

{{table:costs}}

{{chart:cost_structure}}

The gap between gross margin and the other costs is what a retailer fights for. EBITDA is {{num:pnl.ebitda.y1}} in year 1 and {{num:pnl.ebitda.y5}} in year 5. Net income is lower still, because depreciation of the store fit-out, interest on the loan and income tax come after EBITDA.

{{table:pnl}}

## Investment: stores, stock and a cash buffer

The biggest start-up items for a retailer are store fit-out and the first stock order. The model finds the month when cash is lowest, adds up the capital spending ({{num:startup.capex_to_low}} in the sample), the operating cash burned ({{num:startup.burn_to_low}}) and the loan repayments paid until then, and adds a cash buffer. The total is the funding required: {{num:startup.required}}.

{{table:startup}}

Equity and the loan bring in {{num:startup.sources}}, so the sample has a surplus of {{num:startup.gap}} over the requirement. Inventory is part of the story. At the end of year 1 the business holds {{num:unit.inv.y1}} of stock. The U.S. Small Business Administration publishes a [guide to calculating start-up costs](https://www.sba.gov/business-guide/plan-your-business/calculate-your-startup-costs) that is a useful checklist when you build your own list.

## Unit economics: the order and the stock

For retail, unit economics start with one order. The average order value is {{num:unit.aov.y1}} in year 1, and the gross margin is {{num:unit.gm.y1}} of it. The cost of ads is spread across online sales: it is {{num:unit.ads_pct.y1}} of online gross sales in year 1. Repeat orders make up {{num:unit.repeat_share.y1}} of online orders in the sample, coming on top of the orders from newly acquired customers, with no extra ad spend in the model.

{{table:unit}}

The last rows of the table deal with stock. Inventory turns, which is product cost divided by year-end inventory, are {{num:unit.turns.y1}} in year 1. A higher figure means stock sells faster and less cash sits on the shelf.

## Break-even: when the business pays for itself

In the sample the first month with positive EBITDA is {{num:breakeven.first_ebitda}}, and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}, and the cash invested is paid back in {{num:breakeven.payback}}. The sample starts with traffic already in place, so it is profitable from the first month and cash never runs out. A business that has to build its audience from zero would start slower, and you can show that by lowering the visits driver.

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin. In year 1 that is {{num:breakeven.be_rev_y1}} against net sales of {{num:pnl.rev.y1}}, so sales can fall by roughly the gap between the two before the business stops covering its costs. What moves break-even: product cost, order value, the cost of ads per order, and the fixed costs of staff and stores.

## Key risks

- **Margin squeeze.** Suppliers raise prices or you discount to clear stock.
- **Acquisition cost rising.** Paid ads get more expensive as you scale.
- **Too much stock.** Cash is stuck on shelves and old stock sells at a loss.
- **Returns and shipping.** They eat into the margin of each online order.
- **Fixed store costs.** Rent and payroll continue when sales dip.

## How to use Low, Base and High

Every driver has three values, and a switch on the Dashboard of the workbook picks the case for the whole model. Base is your best estimate. Low is a cautious case with fewer visits, lower conversion and higher product cost. High is a good case.

In the sample, conversion ranges from {{num:drivers.conv.low}} to {{num:drivers.conv.high}} and the order value from {{num:drivers.aov.low}} to {{num:drivers.aov.high}}. Set the switch to Low and see how the funding requirement and the lowest cash balance move. If Low still works you have a plan you can defend; if not, you know which number to work on first.

## Frequently asked questions

### How does a retail business make money?

It sells products for more than they cost, and the gross margin pays for shipping, advertising, staff and rent. Profit is what remains.

### What is the difference between markup and margin?

Markup is profit as a share of cost; margin is profit as a share of the selling price. The same product has a lower margin than markup, so check which one a supplier or competitor is quoting.

### Why does inventory matter so much?

Stock is bought before it is sold, so it uses cash. Slow-moving stock needs more funding and risks being sold at a discount.

### How much does it cost to start a retail business?

It depends on the format. Online sellers mostly need stock and marketing, while stores also need fit-out and a deposit. The model calculates the funding required from your own plan.

## Next steps

Download the sample and trace any figure on this page back to its cell. When you are ready to use your own numbers, the [retail store financial projections](/models/retail-store-financial-projections) page describes what the full model includes, and the button below starts a short brief about your business.
