---
slug: /guides/startup-costs-and-break-even-analysis
title: Startup Costs, Funding Need and Break-Even Analysis | StartupModel
description: How much money does a startup need before it breaks even? How to calculate the funding need to the lowest cash point, break-even revenue and payback, with an Excel model built on your numbers.
keyword: startup costs and break-even analysis
secondary: [how much funding does my startup need, break even analysis excel, startup funding need calculator, break even revenue formula, cash runway startup model]
template: any (sample: cafe, full, monthly, 3 years)
tier: full
page_type: guide + sample
wave: 3
---

# Startup costs, funding need and break-even analysis

The question behind most start-up plans is simple: how much money do I need before the business pays for itself? The honest answer is not the cost of the equipment. It is the *lowest point your cash reaches* on the way to profit, plus a cushion. StartupModel adds a Break-even sheet to any of its models when you choose "Startup costs and break-even" as the main goal. Full costs $349; Light costs $149.

## Funding need: up to the lowest cash point

Find the period where closing cash is lowest. Everything spent up to that point has to be funded:

- **Capital spending**: fit-out, equipment, vehicles, deposits.
- **Operating cash burn**: losses and working capital (stock bought, customers who haven't paid yet).
- **Loan repayments** that fall due before then.

Add a **minimum cash buffer** and you have the funding required. The model's buffer is an input, defaulting to about three months of year-1 operating expenses rounded to $1,000; set your own. Compare it with your sources (equity plus loan) and you get a surplus or a shortfall. A check in the file confirms that the lowest cash equals sources minus uses.

## Timing: when does it turn?

The sheet reports three dates:

- the first period with positive EBITDA,
- the first period with positive net income,
- the period when the cash invested is paid back (cumulative operating and investing cash flow back above zero).

Where something doesn't happen inside your horizon it says "Not within horizon" rather than guessing.

## Break-even revenue

Annual break-even revenue = operating expenses ÷ gross margin. Cost of sales is treated as variable and operating expenses as fixed.

Illustrative example, not a benchmark: operating expenses of $240,000 a year and a 60% gross margin give break-even revenue of $240,000 ÷ 0.60 = **$400,000**. If the plan shows $500,000 of revenue, the **margin of safety** is ($500,000 − $400,000) ÷ $500,000 = **20%**: revenue can fall by a fifth before the business loses money.

The simplification matters. Marketing that scales with revenue is really variable, so treat the result as a first estimate.

## Three mistakes that cause a shortfall

1. **Funding the equipment and forgetting the losses.** Most new businesses lose money before they make it.
2. **Leaving out working capital.** Stock and slow-paying customers absorb cash before the first profit.
3. **No cushion.** The plan works exactly, until it doesn't. Show the low case.

## A worked funding example

Made-up numbers, not benchmarks. A new shop plans $120,000 of fit-out and equipment. Operating losses and working capital in the first months come to $90,000 before cash turns around. The lowest cash point is in month 9, so uses of funds up to then are $120,000 + $90,000 = $210,000. Add a $30,000 buffer and the funding required is **$240,000**. If the owner puts in $150,000 and borrows $60,000, sources are $210,000 and the model shows a **shortfall of $30,000**: the plan runs out of cash at the lowest point unless more is raised or costs are cut. That is far better to learn from a spreadsheet than from a bank balance.

## Who this helps

- **First-time founders** who need a figure to take to a bank, investor or family member.
- **Existing owners** opening a second site who want to know how much the expansion needs before it carries itself.
- **Advisers** who must justify the number in a loan pack. The Checks sheet travels with the file, so the lender can see the statements tie.

## Scenarios

Flip the Low / Base / High switch and the funding need, lowest cash point and payback date all move. The Low case stacks every pessimistic value, so it is a stress case. It's the number to compare with what you're raising.

## How each model is verified

Every value on the Break-even sheet is recomputed independently in plain Python for all three scenarios and must match the workbook (within $1 for money, exact for periods). The Checks sheet must show no FAIL. A model that fails is not delivered.

## Sample

The sample linked here is a Full café model without the Break-even sheet, so you can inspect the statements and cash flow the sheet is built from. The Break-even sheet is added when you choose the break-even goal in the questionnaire.

[Download a sample Full model (.xlsx)](/samples/cafe-full.xlsx)

## Questions

**Does it work for my industry?**
Yes. The Break-even sheet is added to every template: restaurants, SaaS, retail, professional services, rental property, fitness and home services.

**Can I also get a valuation?**
Choose the investor-ready pitch goal for a Summary, Break-even and Valuation. See [DCF valuation for a small business](/guides/dcf-valuation-small-business).

**What if the model doesn't fit my business?**
Write to us within 7 days and we refund the full amount.

See also: [Restaurant break-even analysis](/guides/restaurant-break-even-analysis) · [Financial projections for a bank loan](/guides/financial-projections-for-bank-loan) · [All custom financial models](/models/custom-financial-model)

[Build my break-even model — from $149](/start)
