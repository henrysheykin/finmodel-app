---
slug: /business-models/guest_house
title: How a Guest House or B&B Makes Money: Occupancy, Daily Rate and RevPAR | StartupModel
description: How a guest house or B&B makes money, with tables from a working financial model: occupancy, average daily rate, RevPAR, booking commissions, property loan and break-even.
keyword: how does a bed and breakfast make money
secondary: [guest house business model, bed and breakfast profit, b&b start-up costs, revpar guest house, guest house break-even occupancy]
template: guest_house
published: 2026-10-22
modified: 2026-10-22
sample: guest_house, full, monthly, 5 years
---

# How a guest house makes money

A guest house or bed and breakfast sells room-nights. Each room can be sold once a night, and a night that goes unsold cannot be sold later. So the business is built on three numbers: how many rooms there are, how many of the nights are occupied, and what each occupied night earns. Breakfast and extras add a little on top. This page walks through that arithmetic for one illustrative guest house that owns its building, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for your own property.

## What the sample assumes

The sample has {{num:drivers.rooms.base}} lettable rooms. At maturity they are occupied {{num:drivers.occ.base}} of the nights, and the average daily rate (ADR) per occupied room is {{num:drivers.adr.base}}. The owner buys the building for {{num:drivers.capex_buy.base}}. A {{num:drivers.loan_amount.base}} loan at {{num:drivers.loan_rate.base}} interest and {{num:drivers.equity.base}} of equity pay for the purchase and also for the start-up costs: fit-out, the furnishing reserve and the early losses. The table shows each driver with a Low, Base and High value.

{{table:drivers}}

Length of stay, booking site commissions, breakfast and extras, cleaning, furnishings and wages sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: rooms, occupancy and rate

Room revenue is the number of rooms times the nights in the period, times the share of those nights that are occupied, times the ADR. Occupancy builds up over an opening ramp, grows a little each year and, in monthly models, is higher in June to August with the other months giving it back. Breakfast and extras are charged per occupied night.

Hoteliers combine occupancy and rate into one figure, RevPAR, which is room revenue per available room-night. In the sample it is {{num:unit.revpar.y1}} in year 1 and {{num:unit.revpar.y5}} in year 5. A guest house with a high rate but many empty nights can have the same RevPAR as one with a lower rate and a fuller house, which is why both need to be watched. Occupancy is {{num:unit.occ_rate.y1}} in year 1, and the effective rate is {{num:unit.adr_eff.y1}}. Total revenue is {{num:pnl.rev.y1}} in year 1 and {{num:pnl.rev.y5}} in year 5, of which breakfast and extras are {{num:unit.extras_share.y1}}.

{{chart:revenue_costs}}

## Costs: commissions, housekeeping and the building

Cost of sales for a guest house includes housekeeping, the commission paid to online booking sites on the share of rooms they sell, the cost of breakfast, cleaning for each stay and guest supplies. In the sample it is {{num:costs.cogs.y1}} of revenue in year 1, falling to {{num:costs.cogs.y5}} in year 5, and the gross margin rises from {{num:pnl.gm.y1}} to {{num:pnl.gm.y5}}.

Because the sample owns the building, there is no rent. Instead there is property tax, insurance, utilities, repairs, host and front-desk payroll, marketing and overhead. Payroll takes {{num:costs.payroll_nb.y1}} of revenue in year 1 and utilities {{num:costs.utilities.y1}}. Most of these costs hardly change with occupancy, which is why a fuller house is so much more profitable than a half-empty one.

{{table:costs}}

{{chart:cost_structure}}

EBITDA is {{num:pnl.ebitda.y1}} in year 1, {{num:pnl.ebitda.y2}} in year 2 and {{num:pnl.ebitda.y5}} in year 5. The large step in year 2 comes from occupancy filling up. Below EBITDA, depreciation of the building and furnishings and interest on the loan are heavy, so net income is a loss of {{num:pnl.ni.y1|abs}} in year 1 and turns positive in year 2.

{{table:pnl}}

## Investment: the property, the rooms and the loan

For an owner-operator the building is the main cost. The table lists each capital item: the property purchase, room furnishing and fit-out, building works, kitchen and signage, and a small FF&E replacement reserve. Together, capital spending until the cash low point is {{num:startup.capex_to_low}}. The model adds operating cash burned ({{num:startup.burn_to_low}}) and loan repayments, plus a buffer, for a funding requirement of {{num:startup.required}}. If the building is leased instead, the purchase falls away and rent appears as a running cost.

{{table:startup}}

Equity and a loan bring in {{num:startup.sources}}, so the last row shows a shortfall of {{num:startup.gap|abs}}. The property loan is repaid in level monthly instalments, so the payment is the same whatever the occupancy. The U.S. Small Business Administration describes loan options in its [guide to funding your business](https://www.sba.gov/business-guide/plan-your-business/fund-your-business).

## Unit economics: the room-night and the stay

The unit is the room-night. The sample has {{num:unit.avail_n.y1}} available room-nights a year and sells {{num:unit.nights.y1}} of them in year 1. Total revenue per available room-night, which adds breakfast and extras to RevPAR, is {{num:unit.trevpar.y1}} in year 1. A guest stays several nights, so the table also shows {{num:unit.stays.y1}} stays in year 1 and revenue per stay of {{num:unit.rev_stay.y1}}. Each stay brings a cleaning cost, so shorter stays cost more per night.

{{table:unit}}

## Break-even: when the guest house pays for itself

The first month with positive EBITDA is {{num:breakeven.first_ebitda}} and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}. For the payback of the cash invested the answer is "{{num:breakeven.payback}}", because most of the money goes into the building, which operating cash flow alone does not repay inside five years.

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin: {{num:breakeven.be_rev_y1}} in year 1 against revenue of {{num:pnl.rev.y1}}. Housekeeping, cleaning per stay and supplies per night sit in cost of sales, so they are largely fixed or per-stay costs. A fuller house and a higher rate therefore raise the gross margin, from {{num:pnl.gm.y1}} in year 1 to {{num:pnl.gm.y5}} in year 5, and keep the threshold flat even as costs grow. A higher booking commission, higher cleaning cost or higher fixed costs of the building push it up.

## Key risks

- **Low occupancy.** Unsold nights are lost, while the building costs and the loan continue.
- **Seasonality.** The sample is busier in summer, and the rest of the year must be funded from it.
- **Booking commissions.** The more rooms sold through booking sites, the lower the margin.
- **Loan payments.** They are fixed, whatever the occupancy.
- **Upkeep.** Repairs and the furnishing reserve keep the rooms competitive.

## How to use Low, Base and High

Each driver has three values, and a switch in cell B4 on the Dashboard of the workbook (1 for Low, 2 for Base, 3 for High) picks the case for the whole model. Base is your best estimate. Low is a cautious case with lower occupancy, a lower rate and higher commissions. High is a good case.

In the sample, occupancy at maturity ranges from {{num:drivers.occ.low}} to {{num:drivers.occ.high}} and the daily rate from {{num:drivers.adr.low}} to {{num:drivers.adr.high}}. Set the switch to Low and check whether EBITDA covers the loan payments and how the lowest cash balance moves.

## Frequently asked questions

### How does a guest house make money?

It sells room-nights and adds breakfast and extras. Housekeeping, commissions, utilities, taxes and the loan are paid from that revenue.

### What is RevPAR?

Revenue per available room-night. It is room revenue divided by all the room-nights you could have sold, so it combines occupancy and rate in one figure.

### Why does occupancy matter so much?

Costs such as the building, utilities and payroll change little with occupancy, so each additional occupied night adds revenue at a high margin.

### How much does it cost to open a guest house?

It depends on whether you buy or lease, and on the work the rooms need. The model adds up the property, furnishings, building works and early cash needs from your own numbers.

## Next steps

Download the sample and trace any figure on this page back to its cell. For a general checklist, read the [startup costs and break-even guide](/guides/startup-costs-and-break-even-analysis). When you are ready to use your own numbers, the button below starts a short brief about your guest house.
