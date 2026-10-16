---
slug: /guides/restaurant-break-even-analysis
title: Restaurant Break-Even Analysis: Formula and Worked Example | StartupModel
description: How to calculate break-even for a restaurant or coffee shop: fixed costs, contribution margin, customers per day needed, and the cash break-even lenders care about.
keyword: break even analysis for restaurant
secondary: [coffee shop break even analysis, break even analysis template excel, startup costs and break even for loan application, how many customers to break even restaurant]
template: cafe
tier: light (full for cash break-even)
page_type: guide + sample
sample: cafe, full, monthly, 3 years
wave: 2
---

# Restaurant break-even analysis: formula and worked example

A restaurant breaks even when its contribution, meaning revenue minus the costs that rise with sales, covers its fixed costs. The formula is **break-even revenue = fixed costs ÷ contribution margin %**. Divide that by your average ticket and operating days and you get the number that matters on the floor: **customers per day needed to break even**. This guide works through the calculation, then shows the second break-even that lenders look at: the point where the business stops consuming cash.

## Step 1: Split costs into fixed and variable

**Variable costs** move with sales:

- food and beverage cost (as a % of revenue);
- marketing, if you budget it as a % of revenue;
- card processing fees and delivery-platform commissions, if any.

**Fixed costs** stay roughly the same whether you serve 80 or 180 customers a day:

- rent;
- salaried and rota staff, including payroll taxes and benefits;
- utilities, insurance, software, accounting;
- loan interest.

Some costs are in between: extra staff on busy days, for example. For a first pass, treat the core rota as fixed and add hours as a separate step.

## Step 2: Contribution margin

Contribution margin % = 100% − variable costs as a % of revenue.

If food and beverage cost is 32% and marketing is 3%, the contribution margin is 65%. Every $1 of sales leaves 65 cents to pay rent, staff and everything else.

## Step 3: Break-even revenue and customers per day

Illustrative inputs only; these are not benchmarks.

| Monthly fixed costs | |
|---|---|
| Rent | $4,800 |
| Payroll incl. taxes and benefits | $16,000 |
| Utilities & other | $2,200 |
| **Total fixed** | **$23,000** |

Break-even revenue = $23,000 ÷ 65% = **$35,385 a month**.

With an average ticket of $6.40 and 30 operating days, that is $35,385 ÷ ($6.40 × 30) = **about 184 customers a day**.

Now compare that with your estimate of traffic at maturity. If you expect 150 customers a day, this concept loses money every month, even when it is fully ramped up. That is exactly what a break-even analysis is for: finding it on paper, before the lease is signed.

## Step 4: Pull the levers

The same formula shows which change helps most. From the example:

| Change | New break-even (customers/day) |
|---|---|
| None | ~184 |
| Average ticket $7.50 instead of $6.40 | ~157 |
| Food & beverage cost 28% instead of 32% | ~174 |
| Payroll $13,000 instead of $16,000 | ~160 |

Ticket and labour usually move break-even more than shaving food cost. But each change has to be believable: a higher ticket needs a menu and a customer base that support it.

## Step 5: The ramp-up and the months below break-even

New sites rarely open at mature traffic. If you open at 60% of full traffic and take six months to get there, the first months will be below break-even even if the mature month is comfortably above it. Add up the losses in those months: that is part of the cash you need on day one, on top of fit-out and equipment.

## Step 6: Cash break-even, the one lenders care about

Profit break-even ignores three things that use cash:

1. **Loan principal.** Interest is a cost in the P&L; repaying principal is not, but it still leaves the bank account.
2. **Capital spending.** The fit-out is depreciated in the P&L over years, but it is paid for up front.
3. **Working capital.** Stock on the shelves and supplier payment terms shift when cash moves.

A business can be past profit break-even and still running down its cash. A lender asks a simpler question: from which month does the business generate enough cash to cover its repayments, and how deep is the cash dip before then? Answering that needs a monthly cash flow statement and a balance sheet, not just a P&L.

## Doing this in a model instead of on a napkin

The napkin version is fine for a first look. Before you commit money, put it in a model where:

- every input sits in its own labelled cell;
- revenue is built from customers per day × average ticket × operating days, with a traffic ramp;
- payroll is built from roles and salaries, with taxes and benefits as a separate input;
- the monthly P&L shows the month EBITDA turns positive;
- the monthly cash flow shows the lowest cash point and when it occurs;
- a low / base / high switch shows how fragile break-even is.

StartupModel's café and restaurant model is built exactly this way. **Light ($149)** gives you the inputs, a monthly P&L and the scenario switch. That's enough to see when each scenario turns profitable. **Full ($349)** adds the cash flow statement, balance sheet, loan schedule and working capital: what you need for the cash break-even and for a lender.

Every model comes with a Checks sheet. Before release, every scenario and year is recomputed independently outside Excel and must match the workbook within $1.

## Sample

[Download the sample café model (.xlsx)](/samples/cafe-full.xlsx). Open the Monthly sheet, find the month EBITDA turns positive, then switch the scenario on the Dashboard and watch it move.

## Common mistakes

- **Leaving payroll taxes and benefits out of fixed costs.** Break-even looks lower than it is.
- **Using the menu price as the average ticket.** Use the basket you actually expect.
- **One break-even number for every scenario.** In the low case it is higher, and that's the number to plan around.
- **Stopping at profit break-even.** A lender will ask about cash.

[Build my restaurant model — from $149](/models/restaurant-coffee-shop-financial-projections) · [Restaurant pro forma guide](/guides/restaurant-pro-forma) · [Financial projections for a bank loan](/guides/financial-projections-for-bank-loan)
