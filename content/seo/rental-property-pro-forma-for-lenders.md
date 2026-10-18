---
slug: /models/rental-property-pro-forma-for-lenders
title: Rental Property Pro Forma for Lenders: NOI, DSCR, IRR | StartupModel
description: A rental property pro forma in Excel built on your numbers: rent roll, vacancy, NOI, mortgage schedule, DSCR, cash-on-cash, levered and unlevered IRR, with scenarios.
keyword: rental property pro forma for bank loan
secondary: [dscr loan rental projections, 10 year rental property cash flow projection excel, rental property investment model with scenarios, real estate pro forma excel]
template: real_estate
tier: full (light as entry)
page_type: product landing + sample
sample: real_estate, full, monthly, 3 years
wave: 2
---

# Rental property pro forma for lenders, built on your numbers

A lender financing a rental property looks at one number first: whether the property's net operating income covers the mortgage payment, and by how much. An investor or partner looks next at the return on the equity. StartupModel builds a rental property pro forma in Excel that answers both, from your numbers. It covers the rent roll, vacancy, operating costs and NOI, a mortgage amortisation schedule, DSCR and cash-on-cash by year, and levered and unlevered IRR and NPV on a sale at the end of the hold. It has a low / base / high scenario switch and a Checks sheet. Full costs $349; Light costs $149.

It suits buy-and-hold investors in single-family rentals, small multifamily and apartment buildings.

[Download the sample property model](#sample) before you buy.

## How the model works

**Rent roll.** Units × average rent per unit per month (rising once a year by rent growth) gives gross potential rent. Less vacancy and credit loss (% of potential rent), plus other income per unit (parking, laundry, fees), gives effective gross income: the model's revenue.

**Operating costs.** Repairs and maintenance (% of collected rent) and owner-paid utilities sit as direct property costs. Below them: property tax (% of purchase price per year), insurance per unit, property management (% of revenue), and legal, accounting and other costs. Fixed costs rise with your cost inflation rate. The result, EBITDA, is the property's **net operating income (NOI)**.

**Purchase and depreciation.** The purchase price plus closing costs is spent in month 1. The land share of the price is not depreciated; the building and closing costs are depreciated straight-line over the period you set. A capital reserve per unit per year (roofs, appliances, unit turns) is spent every period and depreciated the same way.

**Mortgage.** The loan is drawn at purchase and repaid as a level payment (Excel's `PMT`), with interest on the balance at the start of each period. The full amortisation schedule is in the monthly sheet: opening balance, interest, principal, payment, closing balance. Your equity covers the rest of the purchase plus a cash cushion.

## The Returns sheet

On both tiers, a Returns sheet builds the investment cash flows:

- **Year 0:** the all-in purchase cost (levered: less the loan).
- **Years 1 to the end of the hold:** NOI minus capital reserves; levered flows also pay interest and principal.
- **Sale at the end of the hold:** next year's NOI ÷ your exit cap rate, less selling costs; the levered flow repays the remaining loan.

It reports unlevered and levered IRR, NPV at your discount rate, total profit, multiple on money, the going-in cap rate, and DSCR and cash-on-cash for every year. These flows are before income tax.

Before release, every scenario and year is recomputed independently in plain Python and must match the workbook within $1, and the IRRs within 0.01 percentage points. The Checks sheet ties NOI to EBITDA and the purchase to capital spending, confirms the loan is fully repaid at sale and each IRR gives an NPV of zero, and warns when DSCR falls below 1.0x.

## A worked example

Illustrative inputs only; these are not market figures.

| Input | Value |
|---|---|
| Purchase price | $1,500,000 |
| Units | 10 |
| Average rent | $1,500 per unit per month |
| Vacancy & credit loss | 5% |
| Operating costs | 40% of effective gross income (for this example) |
| Loan | $975,000 (65% of price) at 6.5% over 30 years |

- Gross potential rent: 10 × $1,500 × 12 = **$180,000**
- Effective gross income after 5% vacancy: **$171,000**
- NOI after 40% operating costs: **$102,600**, a going-in cap rate of **6.8%** on the price
- Mortgage payment: about **$6,163 a month**, **$73,952 a year**
- DSCR: $102,600 ÷ $73,952 = **1.39x**

Now flip to the low case: lower rent, higher vacancy, higher repairs. Watch DSCR fall toward the 1.0x warning. Your lender's minimum coverage ratio is the line that matters; ask them what it is.

## Metrics the model reports

Average rent per unit, gross potential rent, vacancy, economic occupancy, revenue, NOI and NOI margin, operating expense ratio, NOI per unit, NOI ÷ purchase price, debt service, DSCR, year-end loan and loan ÷ price. These sit on the Dashboard in Full and the P&L sheet in Light, alongside the Returns sheet.

## What you get

**Full — $349:** Dashboard with the scenario selector and property metrics; Inputs; monthly detail with rent roll, costs, reserves, depreciation and the amortisation schedule; annual P&L, cash flow statement and balance sheet; Returns sheet; Checks sheet.

**Light — $149:** Inputs, P&L with period detail and the property metrics, Returns sheet, Checks sheet. Upgrade to Full by paying the difference.

## Sample {#sample}

The sample is a 10-unit building: Full tier, three years of monthly detail, all three scenarios. Try a longer hold and a different exit cap rate, and see how much of the return comes from the sale.

[Download the sample property model (.xlsx)](/samples/real_estate-full.xlsx)

## What the model doesn't do

- One purchase at the start and one sale at the end: no refinancing, no renovation phase, no lease-up of a vacant building.
- One average rent for all units and one vacancy rate; no unit-by-unit rent roll.
- Returns are before tax; depreciation recapture and capital-gains tax on sale are not modelled.
- The loan amount is an input; there is no interest-only period and no loan fees.

If your deal needs any of these, the model is a starting point rather than the whole answer.

## Common mistakes in rental pro formas

1. **No vacancy.** Every property has turnover and bad debt.
2. **Capital reserves left out.** Roofs and appliances wear out; lenders know it.
3. **Exit at today's cap rate on a short hold.** Transaction costs eat a short hold's return; test a higher exit cap.
4. **Interest-only maths on an amortising loan.** Principal leaves the bank account too.
5. **One scenario.** Show the lender the low case before they build their own.

## Questions

**Can I model a 5- or 10-year hold?**
The questionnaire offers 1, 3 or 5 years. Longer holds are not available yet.

**Does it work for a single house?**
Yes: set units to 1.

**What if the model doesn't fit my deal?**
Write to us within 7 days and we refund the full amount.

See also: [Financial projections for a bank loan](/guides/financial-projections-for-bank-loan) · [DCF valuation for small-business owners](/guides/dcf-valuation-small-business) · [All custom financial models](/models/custom-financial-model)

[Build my property model — from $149](/start)
