---
slug: /business-models/services
title: How a Consulting or Professional Services Firm Makes Money | StartupModel
description: How a consulting or agency firm makes money, with tables from a working financial model: billable hours, rates, utilisation, payroll, cash timing and break-even.
keyword: how does a consulting firm make money
secondary: [professional services business model, consulting firm profit margin, agency business model, billable utilisation, services firm start-up costs]
template: services
published: 2026-10-21
modified: 2026-10-21
sample: services, full, monthly, 5 years
---

# How a professional services firm makes money

A consulting, accounting, design or marketing firm sells the time and skill of its people. Clients pay for hours, projects or monthly retainers, and the firm earns a profit when it bills those hours for more than the people cost. There is little stock and not much equipment, so the economics come down to three questions: how many hours your team can sell, what you charge for them, and what you pay the people who deliver the work. This page walks through that arithmetic for one illustrative firm, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for your own firm.

## What the sample assumes

The sample charges {{num:drivers.senior_rate.base}} an hour for partners and senior consultants and {{num:drivers.staff_rate.base}} for consultants, who bill {{num:drivers.staff_util.base}} of their available time. Contractors cover another {{num:drivers.contractor_hours.base}} billable hours a month in year 1. Customers pay on terms of {{num:drivers.ar_days.base}} days. The table lists the main drivers with a Low, Base and High value for each.

{{table:drivers}}

Salaries, retainer share, discounts against the rate card, headcount growth and overhead sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: hours, rate and utilisation

Fee revenue is billable hours multiplied by the rate per hour. Hours are limited by how many people you have and how much of their time can be sold. That share is called utilisation, because a consultant also spends time on proposals, training, admin and holidays. Rates matter just as much. The rate card is a list price, and firms rarely collect all of it, so the model also applies a realisation factor, which is the share of list price actually billed.

In the sample the team bills {{num:unit.hours.y1}} hours in year 1 at an effective rate of {{num:unit.rate.y1}} an hour, and fee revenue is {{num:pnl.rev.y1}}. Realisation against the rate card is {{num:unit.realised.y1}}. By year 5 revenue reaches {{num:pnl.rev.y5}}. Retainer fees, which repeat month after month, are {{num:unit.retainer_share.y1}} of revenue, and they make the plan more predictable than a book that relies only on projects.

{{chart:revenue_costs}}

## Costs: people first

The largest cost by far is the people who deliver the work. The model separates the cost of delivery from the staff who do not bill. In the sample, cost of delivery is {{num:costs.cogs.y1}} of revenue in year 1, so the gross margin is {{num:pnl.gm.y1}}. Non-billable payroll, such as operations and finance staff, takes {{num:costs.payroll_nb.y1}}. Marketing, software, office and general overhead are small by comparison.

{{table:costs}}

{{chart:cost_structure}}

Because overheads are modest and hours are sold at a healthy margin, EBITDA is {{num:pnl.ebitda.y1}} in year 1, an EBITDA margin of {{num:pnl.ebitda_m.y1}}. By year 5 the margin is {{num:pnl.ebitda_m.y5}}, as fixed overhead spreads across more revenue. Net income is lower because depreciation, interest and income tax come after EBITDA.

{{table:pnl}}

## Investment: working capital, not machinery

A services firm needs little equipment, so the start-up cash goes mainly into paying people before clients pay you. The model adds up capital spending ({{num:startup.capex_to_low}} in the sample), the operating cash burned until cash is lowest ({{num:startup.burn_to_low}}), and a buffer, which gives the funding required: {{num:startup.required}}.

{{table:startup}}

Equity and a loan bring in {{num:startup.sources}}, so the last row shows a shortfall of {{num:startup.gap|abs}}. Notice how large the operating burn is, given that the firm earns a profit from month one. Most of it is the payment-terms effect: costs are paid every month, while fees arrive about {{num:drivers.ar_days.base}} days after the invoice. At the end of year 1 clients owe the firm {{num:unit.ar.y1}}. The U.S. Small Business Administration publishes a [guide to calculating start-up costs](https://www.sba.gov/business-guide/plan-your-business/calculate-your-startup-costs) that is a useful checklist for your own list.

## Unit economics: the billable employee

For a services firm the unit is the billable person. The table shows how many billable employees the firm has, how much revenue each brings ({{num:unit.rev_fte.y1}} in year 1), the utilisation of their time ({{num:unit.util.y1}}, across all billable employees, so it differs from the consultant driver above) and the share of hours supplied by contractors ({{num:unit.contr_share.y1}}).

{{table:unit}}

Utilisation and rate are the two levers that matter most. Raising either lifts revenue per person without adding a salary, which is why the model shows both. Contractors give flexibility, because their cost scales with the work sold rather than sitting on the payroll.

## Break-even: when the firm pays for itself

The first month with positive EBITDA is {{num:breakeven.first_ebitda}} and the first month with positive net income is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}, and the cash invested is paid back in {{num:breakeven.payback}}.

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin. In year 1 that is {{num:breakeven.be_rev_y1}} against revenue of {{num:pnl.rev.y1}}. The break-even revenue figure moves with the gross margin and the non-billable overhead. Utilisation, the rate you actually collect and hires who are not yet fully booked all change the gross margin. Payment terms do not change the threshold, but they change how much cash you need while you work towards it.

## Key risks

- **Low utilisation.** Salaries are fixed, so unsold hours go straight to the bottom line.
- **Discounting.** Realisation falls when you cut prices to win work.
- **Client concentration.** Losing one large client leaves capacity idle.
- **Slow payers.** Longer payment terms tie up cash.
- **Hiring ahead of work.** New hires cost money before they bill.

## How to use Low, Base and High

Each driver has three values, and a switch in cell B4 on the Dashboard of the workbook (1 for Low, 2 for Base, 3 for High) picks the case for the whole model. Base is your best estimate. Low is a cautious case with lower rates and less utilisation. High is a good case.

In the sample, the consultant rate ranges from {{num:drivers.staff_rate.low}} to {{num:drivers.staff_rate.high}} an hour, and utilisation from {{num:drivers.staff_util.low}} to {{num:drivers.staff_util.high}}. Set the switch to Low and see what happens to EBITDA and the lowest cash balance. If Low still covers the team, the plan is robust.

## Frequently asked questions

### How does a consulting firm make money?

It bills clients for hours, projects or retainers at a price above what it pays the people who deliver the work.

### What is utilisation?

It is the share of a person's available time that is billed to clients. The rest goes to admin, sales and training.

### Why can a profitable services firm run short of cash?

Staff are paid every month, but clients often pay weeks after the invoice. The gap has to be funded.

### Is a retainer better than a project?

Retainers repeat and are easier to forecast, while projects can be larger but end. A firm can combine both, and the model lets you set the retainer share.

## Next steps

Download the sample and trace any figure on this page back to its cell. When you are ready to use your own numbers, the [professional services financial projections](/models/professional-services-financial-projections) page describes what the full model includes, and the button below starts a short brief about your firm.
