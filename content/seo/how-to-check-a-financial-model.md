---
slug: /guides/how-to-check-a-financial-model
title: How to Check a Financial Model: A 20-Point Review Checklist | StartupModel
description: A practical checklist to review any Excel financial model before it goes to a lender or investor: structure, formulas, the three statements, scenarios and assumptions.
keyword: how to check a financial model
secondary: [financial model review checklist, how to audit a financial model, financial model errors, check excel financial model before sending to bank]
template: any (sample: cafe, full, monthly, 3 years)
tier: light, full
page_type: guide + sample
wave: 2
---

# How to check a financial model: a 20-point review checklist

Checking a financial model means confirming four things: the structure lets you trace every number, the formulas are consistent, the three statements agree with each other, and the assumptions are ones you can defend. You don't need to re-build the model to do this. The 20 checks below take one to two hours on a typical small-business model, and they catch most of the errors that embarrass people in front of a lender or investor. Use them on any model: one you built, one you bought, or one an AI drafted.

## A. Structure: can you follow it?

**1. Inputs live in one place.** Every assumption (growth, prices, costs, salaries, loan terms) should sit in a clearly labelled input area, not inside formulas.

**2. Inputs look different from formulas.** The common convention is blue font for inputs and black for formulas, with links from other sheets often in green. If everything looks the same, you can't tell what you're allowed to change.

**3. Every input has a label and a unit.** "Growth" is not enough; "Traffic growth per year, %" is.

**4. Sheets flow in one direction.** Inputs → calculations → statements → summary. Formulas that jump backwards and forwards between sheets are where errors hide.

**5. No hidden rows, columns or sheets doing real work.** Unhide everything and look.

## B. Formulas: are they consistent?

**6. No typed numbers in the forecast area.** Click through the revenue and cost rows. Each cell should be a formula pointing at inputs or other rows. A typed number is a value someone pasted in, and it won't change when the assumptions do.

**7. The same formula runs across every period.** Select a row and step across the columns. If the formula changes in month 7, find out why. Usually it's a manual fix that was never cleaned up.

**8. Denominators are guarded.** Ratios such as margin % should handle a zero denominator without showing #DIV/0!.

**9. No error values anywhere.** Search the workbook for #REF!, #VALUE!, #DIV/0! and #N/A. One error in a calculation chain can quietly zero out a total.

**10. Functions work in the reader's Excel.** Newer functions don't exist in older versions of Excel or in some other spreadsheet apps. If your lender opens the file in an older Excel, the model may break on their screen and not on yours.

## C. The three statements: do they agree?

**11. The balance sheet balances in every period,** not just at year end. Total assets minus total liabilities and equity should be zero in each column. If it isn't, something in the P&L or the cash flow is wrong.

**12. Cash reconciles.** Closing cash on the balance sheet should equal opening cash plus every net cash flow to date.

**13. Annual totals equal the sum of the periods.** Annual revenue and net income should equal the sum of the monthly figures.

**14. Loan principal is in the cash flow.** Interest belongs in the P&L, but principal repayments only appear in the cash flow and on the balance sheet. A model that forgets them overstates cash.

**15. Capital spending is depreciated, not expensed.** Equipment and fit-out should hit cash when paid and the P&L gradually through depreciation.

## D. Scenarios: does the model react?

**16. Changing an input changes the outputs.** Halve revenue growth. Revenue, profit, cash and the balance sheet should all move. If one of them doesn't, it isn't wired.

**17. The downside is really a downside.** In the low case, revenue drivers go down and cost drivers go **up**. A "low" case with lower costs is a common and misleading mistake.

**18. One switch, not three files.** Low, base and high should live in one file behind one selector. Separate copies drift apart within days.

## E. Assumptions: can you defend them?

**19. Each big assumption has a source.** Rent from the lease, prices from your menu or price list, salaries from offers or market data, traffic from a comparable site. Write the source next to the input.

**20. The ramp is realistic.** Month-one revenue equal to a mature business's is the fastest way to lose a reader's trust.

## Building the checks into the model

Many of these checks can be written as formulas that run every time an input changes: a balance-sheet difference that must be zero, a cash reconciliation, annual-vs-period ties, scenario ordering. Put them on one Checks sheet with a PASS / FAIL result for each, and the model tells you the moment an edit breaks something.

Checks 12, 13 and 17, plus a validity check on the scenario selector, are on the Checks sheet of every StartupModel file, and check 11 is added in the Full model, which has a balance sheet. On top of that, before a model is delivered, every scenario and year is recomputed independently outside Excel and must match the workbook within $1. Checks 1–10 are handled by how the template is built: inputs in one labelled sheet, blue / black / green formatting, the same formula in every period, guarded denominators and only long-established Excel functions.

Checks 19 and 20, the assumptions, are still yours. No tool can tell you whether your rent is right.

## Try the checklist on our sample

[Download a sample café model (.xlsx)](/samples/cafe-full.xlsx) and run the 20 checks on it. Then run them on whatever model you're using now.

## If your model fails the checklist

- **A few fails in sections A–B:** fix them; they're usually quick.
- **Fails in section C:** the statements don't agree, and the numbers can't be relied on until they do. This often means a rebuild of the cash flow or balance sheet.
- **Fails in section D:** the model isn't really a model yet; it's a table of numbers.

If a rebuild is on the cards, it may be faster to start from a model that passes by construction. StartupModel builds one from your numbers: **Light $149** (P&L, inputs, checks) or **Full $349** (all three statements), with a refund within 7 days if it doesn't fit your business.

[Build my model — from $149](/start) · [AI model generators vs a verified model](/guides/ai-financial-model-generator-vs-verified-model) · [Financial projections for a bank loan](/guides/financial-projections-for-bank-loan)
