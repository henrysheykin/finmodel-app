---
slug: /business-models/auto_repair
title: How an Auto Repair Shop Makes Money: Labor, Parts and Bay Capacity | StartupModel
description: How an auto repair shop makes money, with tables from a working financial model: repair orders, labor rate, parts margin, technician and bay capacity, funding and break-even.
keyword: how does an auto repair shop make money
secondary: [auto repair shop business model, auto repair profit margin, auto repair shop start-up costs, effective labor rate, auto repair break-even point]
template: auto_repair
published: 2026-10-22
modified: 2026-10-22
sample: auto_repair, full, monthly, 5 years
---

# How an auto repair shop makes money

An auto repair shop sells two things: the skilled hours of its technicians and the parts that go into the car. Customers bring in vehicles, the shop writes a repair order, technicians bill hours against it, and parts are added at a markup. The shop makes money when the labor and parts it sells cover the technicians, parts cost, rent and everything else. This page walks through that arithmetic for one illustrative shop, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for your own shop.

## What the sample assumes

At maturity the shop completes {{num:drivers.ro_day.base}} repair orders per operating day with an effective labor rate of {{num:drivers.labor_rate.base}} per billed hour. It has {{num:drivers.bays.base}} service bays, earns a gross margin of {{num:drivers.parts_margin.base}} on parts and pays {{num:drivers.rent.base}} a month in rent. Lifts and bay equipment cost {{num:drivers.capex_bay.base}} per bay. The table shows each driver with a Low, Base and High value.

{{table:drivers}}

Technician wages, shop supplies, warranty rework, diagnostic tools, the fit-out and the loan sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: repair orders, hours and parts

Each repair order needs a number of billed labor hours. Labor revenue is billed hours times the effective labor rate, and parts revenue is billed hours times the parts sold per hour. A small shop supplies fee is added on top of labor. The shop does not open at full volume: orders ramp up over the first months and then grow each year.

Billed hours are limited by capacity, and capacity is the lower of two limits: what the bays can carry and what the technicians can bill. In the sample the technicians are the tighter limit, so adding a bay alone would not add billed hours. The shop bills {{num:unit.billed_h.y1}} hours in year 1, using {{num:unit.cap_use.y1}} of its capacity, and {{num:unit.billed_h.y5}} hours in year 5 at {{num:unit.cap_use.y5}}. Revenue is {{num:pnl.rev.y1}} in year 1 and {{num:pnl.rev.y5}} in year 5, of which parts account for {{num:unit.parts_share.y1}}.

{{chart:revenue_costs}}

## Costs: technicians sit in cost of sales

In a repair shop the technicians are a cost of sales, together with parts, shop supplies and rework on repairs that come back. In the sample cost of sales takes {{num:costs.cogs.y1}} of revenue in year 1 and {{num:costs.cogs.y5}} in year 5. The gross margin rises from {{num:pnl.gm.y1}} to {{num:pnl.gm.y5}} because the technician team stays the same size while billed hours grow, so each hour carries less technician cost.

Below gross profit are advisor and manager payroll ({{num:costs.payroll_nb.y1}} of revenue in year 1), rent ({{num:costs.rent.y1}}), insurance, software and other overhead, and marketing. Marketing is highest at the start and the sample lets it fall each year.

{{table:costs}}

{{chart:cost_structure}}

EBITDA is a loss of {{num:pnl.ebitda.y1|abs}} in year 1 because the ramp is still under way, turns positive at {{num:pnl.ebitda.y2}} in year 2 and reaches {{num:pnl.ebitda.y5}} in year 5. Net income is lower because depreciation, interest and income tax come after EBITDA.

{{table:pnl}}

## Investment: bays, tools and fit-out

A shop needs lifts and equipment for each bay, diagnostic tools and a fit-out of the premises. In the sample capital spending until the cash low point is {{num:startup.capex_to_low}}. The model adds the operating cash burned ({{num:startup.burn_to_low}}) and the loan repayments paid until then, plus a buffer. The funding required is {{num:startup.required}}.

{{table:startup}}

Equity and a loan bring in {{num:startup.sources}}, so the last row shows a shortfall of {{num:startup.gap|abs}}. A gap like that is a prompt to ask whether the ramp is realistic or whether the plan needs more money. The U.S. Small Business Administration publishes a [guide to calculating start-up costs](https://www.sba.gov/business-guide/plan-your-business/calculate-your-startup-costs) that is a useful checklist for your own list.

## Unit economics: the repair order and the billed hour

The unit is the repair order. The table shows revenue per order ({{num:unit.rev_ro.y1}} in year 1), revenue per billed hour ({{num:unit.rev_hour.y1}}, which combines labor and parts) and revenue per technician ({{num:unit.rev_tech.y1}}). Parts revenue is {{num:unit.rev_parts.y1}} in year 1, with a gross margin of {{num:unit.parts_gm.y1}}.

{{table:unit}}

Labor rate and billed hours are the two levers. A shop can sell the same hours at a higher effective rate, or fill technician time that would otherwise go unbilled. Both lift gross profit without adding a salary.

## Break-even: when the shop pays for itself

The first month with positive EBITDA is {{num:breakeven.first_ebitda}} and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}, and the cash invested is paid back in {{num:breakeven.payback}}.

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin. In year 1 it is {{num:breakeven.be_rev_y1}}, higher than revenue of {{num:pnl.rev.y1}}, because the year 1 gross margin is low while the shop is still filling. By year 5 the threshold falls to {{num:breakeven.be_rev_y5}} as the gross margin improves. Technician pay is fixed in cost of sales, so more billed hours and a higher labor rate raise the gross margin and lower the break-even revenue. A lower parts margin, higher technician pay, rent or overhead push it up. Order volume also decides how soon revenue reaches it.

## Key risks

- **Slow ramp.** Technicians and rent are paid from the first month, before the bays fill.
- **Unbilled technician time.** A technician on the payroll earns nothing for hours that are not sold.
- **Comebacks.** Rework on repairs that return costs labor and parts with no revenue.
- **Parts margin.** A lower margin on parts reduces gross profit on every order.
- **Thin funding.** A shortfall at the start leaves little room for a slower ramp.

## How to use Low, Base and High

Each driver has three values, and a switch in cell B4 on the Dashboard of the workbook (1 for Low, 2 for Base, 3 for High) picks the case for the whole model. Base is your best estimate. Low is a cautious case with fewer repair orders, a lower labor rate and a lower parts margin. High is a good case.

In the sample, repair orders per day range from {{num:drivers.ro_day.low}} to {{num:drivers.ro_day.high}} and the labor rate from {{num:drivers.labor_rate.low}} to {{num:drivers.labor_rate.high}}. Set the switch to Low and look at the lowest cash balance and the month EBITDA turns positive.

## Frequently asked questions

### How does an auto repair shop make money?

It bills technician hours at a labor rate and sells parts at a margin. Technicians, rent and overhead are paid from that, and the rest is profit.

### What is an effective labor rate?

It is the revenue earned per billed hour, after discounts. It can differ from the posted rate.

### What limits how much a shop can earn?

Capacity. The shop can bill only as many hours as its bays and technicians can carry.

### How much does it cost to open a repair shop?

It depends on the premises, the number of bays and the tools. The model adds up equipment, fit-out and early losses from your own numbers.

## Next steps

Download the sample and trace any figure on this page back to its cell. For a general checklist, read the [startup costs and break-even guide](/guides/startup-costs-and-break-even-analysis). When you are ready to use your own numbers, the button below starts a short brief about your shop.
