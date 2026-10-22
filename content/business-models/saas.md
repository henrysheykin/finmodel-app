---
slug: /business-models/saas
title: How a SaaS Company Makes Money: MRR, Churn, CAC and Runway | StartupModel
description: How a subscription software company makes money, with tables from a working financial model: MRR, churn, CAC, payback, hiring costs, funding need and runway.
keyword: how do saas companies make money
secondary: [saas business model, saas unit economics, saas startup costs, saas runway, saas churn and cac]
template: saas
published: 2026-10-21
modified: 2026-10-21
sample: saas, full, monthly, 5 years
---

# How a SaaS company makes money

A software-as-a-service company sells access instead of a one-off product. Customers pay a subscription every month or every year, so revenue arrives in small, repeating amounts. That is attractive, but it also means the cost of winning a customer is paid today while the money comes back over the following months. This page walks through that arithmetic for one illustrative startup, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example of how the pieces fit together rather than a forecast for your own product.

## What the sample assumes

The sample starts with {{num:drivers.start_customers.base}} paying customers, each paying about {{num:drivers.arpa.base}} a month on average. Every month some customers cancel (churn) and new ones arrive from two sources: organic and referral sign-ups, and paid marketing. The table lists the main drivers with a Low, Base and High value for each.

{{table:drivers}}

Hiring plans, hosting costs, price increases and expansion revenue from existing customers sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: customers, price and churn

SaaS revenue is the number of paying customers multiplied by the average monthly price, so it is built up customer by customer rather than guessed as a single line. Each month the model takes last month's customers, removes the share that churned, and adds the new ones. Monthly recurring revenue (MRR) is the result, and annual recurring revenue (ARR) is year-end MRR times twelve.

Churn is the quiet driver. A small change in the monthly cancellation rate compounds, because it is applied to the whole customer base every month. At the Base churn of {{num:drivers.churn_m.base}} a month, the sample ends year 1 with {{num:unit.cust.y1}} customers and ARR of {{num:unit.arr.y1}}. By year 5 it reaches {{num:unit.cust.y5}} customers and ARR of {{num:unit.arr.y5}}. Recognised revenue in the P&L lags ARR because customers join through the year: it is {{num:pnl.rev.y1}} in year 1 and {{num:pnl.rev.y5}} in year 5.

{{chart:revenue_costs}}

## Costs: cheap to serve, expensive to build

A subscription product is cheap to deliver once it exists. In the sample, hosting, payment fees and customer support take {{num:costs.cogs.y1}} of revenue in year 1, which leaves a gross margin of {{num:pnl.gm.y1}}. This is why subscription software is often described as a high-margin business: each extra customer brings in most of its price as gross profit.

The expense sits above the gross profit line. People build the product, sell it and look after customers, and payroll is by far the biggest cost. The sample's team grows from {{num:unit.team.y1}} full-time equivalents at the end of year 1 to {{num:unit.team.y5}} at the end of year 5, so payroll is {{num:costs.payroll.y1}} of revenue in year 1 and still {{num:costs.payroll.y5}} in year 5. Paid marketing is the second lever, taking {{num:costs.mkt.y1}} of revenue in year 1.

{{table:costs}}

{{chart:cost_structure}}

In this sample the hiring plan runs ahead of revenue. EBITDA is a loss of {{num:pnl.ebitda.y1|abs}} in year 1 and a loss of {{num:pnl.ebitda.y5|abs}} in year 5, so the company never reaches profit inside the five-year window. That is not a prediction about SaaS in general. The cause is visible in the P&L: payroll is {{num:costs.payroll.y1}} of year 1 revenue, and every year it adds more dollars than gross profit does. Gross profit rises from {{num:pnl.gp.y1}} in year 1 to {{num:pnl.gp.y5}} in year 5, while payroll rises from {{num:pnl.payroll.y1|abs}} to {{num:pnl.payroll.y5|abs}}. A model should make that visible before you commit to a hiring plan.

{{table:pnl}}

## Investment and funding: the runway question

A software startup has little to buy up front. The sample spends only {{num:startup.capex_to_low}} on equipment before cash hits its lowest point. The real investment is the operating loss you fund while the customer base builds, and the model measures it directly: it adds up the cash burned until the cash balance is at its lowest, then adds a buffer of about three months of costs. In the sample the burn is {{num:startup.burn_to_low}} and the funding required is {{num:startup.required}}.

{{table:startup}}

Equity of {{num:startup.equity}} covers only part of that, so the last row shows a shortfall of {{num:startup.gap|abs}}. The year-end cash line in the unit table shows the same story: {{num:unit.cash.y1}} at the end of year 1, {{num:unit.cash.y3}} in year 3 and below zero in year 4, at minus {{num:unit.cash.y4|abs}}. In practice a founder reads this as a runway test: either raise more, cut the plan, or reach profit sooner. The U.S. Small Business Administration has a [guide to funding options](https://www.sba.gov/business-guide/plan-your-business/fund-your-business) that covers loans, investors (including venture capital), grants and crowdfunding.

## Unit economics: what one customer is worth

SaaS unit economics compare what you pay to win a customer with what that customer returns. Customer acquisition cost (CAC) is marketing spend divided by new customers. Payback is how many months of gross profit it takes to earn that cost back. Lifetime value is roughly the monthly gross profit per customer divided by the monthly churn rate.

The sample's paid CAC is {{num:drivers.cac.base}} per customer in the Base case, but because organic sign-ups carry no paid-marketing cost the blended CAC in year 1 is {{num:unit.cac.y1}}, and payback is {{num:unit.payback.y1}} months. Average revenue per customer drifts up from {{num:unit.arpa.y1}} to {{num:unit.arpa.y5}} a month through price increases and expansion.

{{table:unit}}

Short payback is healthy, but it does not by itself make a company profitable. The table shows strong unit economics next to a large operating loss, because the cost of the team is paid before the customers arrive.

## Break-even: when the company pays for itself

The model shows several break-even points, because "break-even" means different things. For the first month with positive EBITDA the sample answers "{{num:breakeven.first_ebitda}}", and the same for the first month with positive net income ("{{num:breakeven.first_ni}}"). Cash is lowest in {{num:breakeven.low_p}} at minus {{num:breakeven.min_cash|abs}}, the last month of the plan, which means it is still falling when the model ends. Payback of the cash invested: "{{num:breakeven.payback}}".

{{table:breakeven}}

Break-even revenue is operating expenses divided by gross margin. For year 1 that is {{num:breakeven.be_rev_y1}} against revenue of {{num:pnl.rev.y1}}. By year 5 it is {{num:breakeven.be_rev_y5}}, because the cost base has grown. The break-even revenue figure moves with price, hosting and support cost, how fast you hire and how much you spend on paid acquisition. Churn and sign-up speed do not change that threshold. They change how long it takes revenue to reach it, and how much cash you burn on the way.

## Key risks

- **Churn higher than planned.** It shrinks the base every month, so the revenue curve flattens.
- **CAC creeping up.** Paid channels get more expensive as you scale, which lengthens payback.
- **Hiring ahead of revenue.** Payroll is fixed once people are on the team.
- **Running out of cash before profit.** The funding table is the early warning.

## How to use Low, Base and High

Each driver has three values, and a switch in cell B4 on the Dashboard of the workbook (1 for Low, 2 for Base, 3 for High) picks the case for the whole model. Base is your best estimate. Low is a cautious case with fewer sign-ups and more churn. High is a good case.

In the sample, the price per customer ranges from {{num:drivers.arpa.low}} to {{num:drivers.arpa.high}} a month, and monthly churn from {{num:drivers.churn_m.high}} to {{num:drivers.churn_m.low}}. Switch to Low and look at the lowest cash balance, then switch to High and see how far the runway extends. The gap between the two tells you which assumption to test first with real customers.

## Frequently asked questions

### How does a SaaS company make money?

It charges customers a recurring subscription. Revenue grows when the number of paying customers rises, the price per customer rises, or customers stay longer.

### Why is churn so important?

Churn is applied to every customer every month. Reducing it keeps customers longer, which raises their lifetime value and lowers the number of new customers you need to win.

### How much money does a SaaS startup need?

It depends mostly on payroll and how long it takes to reach profit. The model finds the lowest cash point in the plan and adds a buffer, so the answer comes from your own hiring plan and growth assumptions.

## Next steps

Download the sample and trace any figure on this page back to its cell. When you are ready to use your own numbers, the [SaaS financial model with scenarios](/models/saas-financial-model-with-scenarios) page describes what the full model includes, and the button below starts a short brief about your company.
