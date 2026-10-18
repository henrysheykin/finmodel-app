---
slug: /guides/dcf-valuation-small-business
title: DCF Valuation for a Small Business: A Plain Guide | StartupModel
description: How a discounted cash flow valuation works for a small business: free cash flow, WACC, terminal value two ways, and a sensitivity table. With an Excel model built on your numbers.
keyword: dcf valuation small business
secondary: [discounted cash flow valuation small business excel, how to value a small business dcf, dcf model template for small business, wacc terminal value sensitivity table]
template: any (sample: cafe, full, monthly, 3 years)
tier: full
page_type: guide + sample
wave: 3
---

# DCF valuation for a small business, explained

A discounted cash flow (DCF) valuation says a business is worth the cash it will produce, brought back to today's money. It is the standard method for putting a value on a business when you have a forecast, and it is only as good as that forecast and the discount rate. StartupModel adds a Valuation sheet to any of its models when you choose "Business valuation (DCF)" as the main goal. It builds from the same period grid as the rest of the model, so it moves with the Low / Base / High switch. Full costs $349; Light costs $149.

## The four steps

**1. Free cash flow.** For each period: operating cash flow + interest × (1 − tax rate) − capital spending. Adding back after-tax interest gives *unlevered* cash flow, the cash the business makes before financing choices. The sheet sums it by year.

**2. Discount rate (WACC).** Future cash is worth less than cash today. The weighted average cost of capital is the rate used to discount it. Small and young businesses carry a high rate because the cash flows are uncertain. The model applies year-end discounting and checks that the sum of present values equals Excel's `NPV()` of the same flows.

**3. Terminal value.** The business is assumed to keep going after the forecast ends. The Valuation sheet shows two methods side by side:

- **Perpetual growth:** final-year free cash flow × (1 + g) ÷ (WACC − g)
- **Exit multiple:** final-year EBITDA × a multiple

It reports enterprise value for each, the share of value that sits in the terminal value, and cross-checks: the multiple implied by the growth method and the growth implied by the multiple method. If the two methods are far apart, one of your assumptions is doing the work.

**4. Sensitivity.** A 5 × 5 table shows the perpetual-growth value for WACC two steps either side of your rate and growth two steps either side of yours. The centre cell must equal the headline value; the Checks sheet tests it.

## A worked example

Illustrative inputs only, not benchmarks. Suppose final-year free cash flow is $100,000, WACC is 20% and terminal growth is 2%.

- Perpetual growth: $100,000 × 1.02 ÷ (0.20 − 0.02) = **$566,667** at the end of the final year.
- Exit multiple: final-year EBITDA $150,000 × 4.5 = **$675,000**.

Both are brought back to today and added to the discounted free cash flows of the forecast years. The gap between $566,667 and $675,000 is the sort of difference you should explain before showing anyone the number.

## Defaults and guard rails

The model fills WACC, exit multiple and terminal growth by business stage as illustrative starting points. They are not market data; replace them with your own. For example, the defaults put WACC higher for a planning-stage business than for an established one. Guard rails:

- A brief is refused if WACC − terminal growth is below 1 percentage point in any scenario, because the formula explodes.
- WACC is ordered Low ≥ Base ≥ High, so the pessimistic case has the higher discount rate.
- A negative final-year free cash flow gives a warning in Checks.

## Limits to know about

- Terminal value uses final-year free cash flow. A growing business still carries growth capital spending and working capital in that year, which lowers the perpetual-growth value.
- Year-end discounting, not mid-year.
- The interest tax shield is taken at the headline tax rate, even while losses are carried forward.
- A DCF is an estimate for planning and negotiation, not a formal valuation opinion or appraisal.

## How each model is verified

Every value on the Valuation sheet, from free cash flow to enterprise value, is recomputed independently in plain Python for all three scenarios and must match the workbook (within $1 for money). The Checks sheet must show no FAIL. A model that fails is not delivered.

## Sample

The sample linked here is a Full model without the Valuation sheet, so you can inspect the formulas, statements and checks that the valuation is built on. The Valuation sheet is added when you choose the valuation goal in the questionnaire.

[Download a sample Full model (.xlsx)](/samples/cafe-full.xlsx)

## Questions

**Can I use this to sell my business?**
It gives you a structured estimate and a sensitivity range. It is not an appraisal and not advice; a buyer will form their own view.

**Which goal do I choose?**
"Business valuation (DCF)" adds the Valuation sheet. "Investor-ready pitch model" adds a Summary sheet, Break-even and Valuation.

**What if the model doesn't fit my needs?**
Write to us within 7 days and we refund the full amount.

See also: [Financial model for investors](/models/financial-model-for-investors) · [Rental property pro forma for lenders](/models/rental-property-pro-forma-for-lenders) · [All custom financial models](/models/custom-financial-model)

[Build my valuation model — from $149](/start)
