---
slug: /business-models/salon
title: How a Hair Salon Makes Money: Chairs, Commission and Break-Even | StartupModel
description: How a hair salon or barbershop makes money, with tables from a working financial model: chair utilisation, commission, chair rent, costs, funding and break-even.
keyword: how does a hair salon make money
secondary: [salon business model, hair salon profit margin, salon start-up costs, salon break-even point, chair rental vs commission]
template: salon
published: 2026-10-22
modified: 2026-10-22
sample: salon, full, monthly, 5 years
---

# How a hair salon makes money

A salon sells the time of its stylists. Every styling chair is a small unit of capacity: it can be booked for a certain number of hours a month, and each booked hour brings in service revenue. The owner keeps what is left after paying the stylist, buying products and covering rent. Some owners also rent chairs to independent stylists for a fixed weekly fee instead of employing them. This page walks through that arithmetic for one illustrative salon, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for your own salon.

## What the sample assumes

The sample salon has {{num:drivers.chairs.base}} styling chairs. In the first year the employed chairs are booked for {{num:drivers.util.base}} of their available hours, and the average service costs {{num:drivers.price.base}}. Employed stylists earn a commission of {{num:drivers.comm_pct.base}} of the service revenue they produce, and {{num:drivers.rented_share.base}} of the chairs are rented to independent stylists. Rent for the premises is {{num:drivers.rent.base}} a month. The table shows each driver with a Low, Base and High value.

{{table:drivers}}

Opening days, hours per day, retail sales, product cost, wages and the loan sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: hours, utilisation and price

Salon revenue has three streams. The main one is service revenue from the employed chairs. The model works it out from bookable hours (days open times hours per chair per day times the number of employed chairs), multiplied by utilisation, the share of those hours that are actually booked, then by services per booked hour and the average price. The second stream is retail products sold on top of services. The third is chair rent from independent stylists, which does not depend on how busy those stylists are.

Utilisation is the lever to watch. In the sample it starts at {{num:unit.util.y1}} in year 1 and gains several points a year, reaching {{num:unit.util.y5}} in year 5, so services performed grow from {{num:unit.services.y1}} to {{num:unit.services.y5}} on the same number of chairs. Revenue is {{num:pnl.rev.y1}} in year 1 and {{num:pnl.rev.y5}} in year 5.

{{chart:revenue_costs}}

## Costs: commission first, then rent

The largest cost of sales is the stylists. Their commission, plus payroll taxes, product costs, backbar supplies and card fees, makes up {{num:costs.cogs.y1}} of revenue in year 1 and leaves a gross margin of {{num:pnl.gm.y1}}. Because commission is a share of what each stylist sells, it rises and falls with revenue.

The costs below gross profit mostly do not. Rent of {{num:costs.rent.y1}} of revenue in year 1 falls to {{num:costs.rent.y5}} by year 5, because the rent itself is flat while revenue grows. Staff payroll for the manager, receptionist and assistants goes from {{num:costs.payroll.y1}} to {{num:costs.payroll.y5}} of revenue, because the team stays the same size while revenue grows.

{{table:costs}}

{{chart:cost_structure}}

EBITDA is a loss of {{num:pnl.ebitda.y1|abs}} in year 1, turns positive at {{num:pnl.ebitda.y2}} in year 2 and reaches {{num:pnl.ebitda.y5}} in year 5. Net income lags behind because depreciation of the fit-out, interest on the loan and income tax come after EBITDA.

{{table:pnl}}

## Investment: fit-out, stations and wash basins

Before the first appointment a salon needs a fit-out, a styling station for each chair and backwash units. The model adds up the capital spending until the cash low point ({{num:startup.capex_to_low}}), the operating cash burned until then ({{num:startup.burn_to_low}}) and the loan repayments, and adds a cash buffer. The funding required is {{num:startup.required}}.

{{table:startup}}

Equity and a loan bring in {{num:startup.sources}}, so the last row shows a shortfall of {{num:startup.gap|abs}}. A small gap like that is a signal to look at the opening ramp or trim the fit-out before approaching a lender. The U.S. Small Business Administration publishes a [guide to calculating start-up costs](https://www.sba.gov/business-guide/plan-your-business/calculate-your-startup-costs) that is a useful checklist for your own list.

## Unit economics: the chair

The unit of a salon is the chair. The table shows booked chair hours against bookable hours, the average revenue per service ({{num:unit.ticket.y1}} in year 1) and the service revenue per employed chair, which rises from {{num:unit.rev_emp_chair.y1}} in year 1 to {{num:unit.rev_emp_chair.y5}} in year 5 as utilisation grows.

{{table:unit}}

A rented chair works differently. In the sample each rented chair pays {{num:unit.rent_chair.y1}} a month in year 1. That is a fixed payment with no commission attached, so the salon takes less revenue per chair than from a busy employed stylist, but also carries less risk if the chair is quiet. Retail products add {{num:unit.rev_retail.y1}} in year 1, or {{num:unit.retail_share.y1}} of service revenue.

## Break-even: when the salon pays for itself

The first month with positive EBITDA is {{num:breakeven.first_ebitda}} and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}, and the cash invested is paid back in {{num:breakeven.payback}}.

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin: {{num:breakeven.be_rev_y1}} in year 1 against revenue of {{num:pnl.rev.y1}}. That threshold moves with the commission rate, product and supply costs, rent and staff payroll. Utilisation and price change it only slightly, because backbar supplies are a fixed amount per service and chair rent carries no cost of sales. They mainly decide how soon revenue reaches the threshold, which is why the opening ramp matters so much.

## Key risks

- **Slow ramp.** Rent and payroll start on day one, while utilisation builds over years.
- **Commission rate.** A higher commission lowers the gross margin on every service.
- **Empty rented chairs.** Chair rent depends on finding and keeping independent stylists.
- **Fixed rent.** It does not shrink when appointments are quiet.
- **Thin funding.** A small shortfall at the start leaves little room for delay.

## How to use Low, Base and High

Each driver has three values, and a switch in cell B4 on the Dashboard of the workbook (1 for Low, 2 for Base, 3 for High) picks the case for the whole model. Base is your best estimate. Low is a cautious case with lower utilisation, a lower price and a higher commission. High is a good case.

In the sample, year 1 utilisation ranges from {{num:drivers.util.low}} to {{num:drivers.util.high}} and the service price from {{num:drivers.price.low}} to {{num:drivers.price.high}}. Set the switch to Low and look at the lowest cash balance. If it falls below zero, the plan needs more funding, a smaller space or a faster ramp.

## Frequently asked questions

### How does a hair salon make money?

It earns service revenue from booked chair hours, sells retail products, and may rent chairs to independent stylists. Commission, products, rent and staff come out of that.

### Is it better to rent chairs or employ stylists?

It is a trade-off. Employed stylists bring in service revenue and the owner keeps it after commission, but the owner carries the risk of quiet days. Rented chairs give a fixed payment and less upside. The model lets you set the share of rented chairs and compare.

### What is chair utilisation?

It is the share of bookable hours on a chair that are booked by clients. A chair that is empty half the time earns half the service revenue.

### How much does it cost to open a salon?

It depends on the space and the number of chairs. The model adds up fit-out, equipment and early losses from your own numbers.

## Next steps

Download the sample and trace any figure on this page back to its cell. For a general checklist, read the [startup costs and break-even guide](/guides/startup-costs-and-break-even-analysis). When you are ready to use your own numbers, the button below starts a short brief about your salon.
