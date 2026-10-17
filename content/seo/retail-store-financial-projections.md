---
slug: /models/retail-store-financial-projections
title: Retail Store Financial Projections for a Bank Loan | StartupModel
description: Retail store financial projections in Excel: sales per sq ft, rent, fit-out, like-for-like growth, seasonality, inventory and cash, with low/base/high scenarios. Built on your numbers.
keyword: retail business plan financial projections for bank loan
secondary: [retail store financial projections, retail store financial model excel, retail startup costs and break even, boutique financial projections]
template: retail
tier: full
page_type: product landing + sample
sample: retail, full, monthly, 3 years
wave: 3
---

# Retail store financial projections for a bank loan

A lender looking at a shop asks: will the space sell enough to cover the rent and the people, and does the business have the cash to carry stock through the slow months? StartupModel builds retail store projections in Excel around the numbers that answer that question: selling area, sales per square foot, rent per square foot, fit-out, like-for-like growth, seasonality and inventory. You get a P&L, cash flow and balance sheet, a low / base / high scenario switch and a Checks sheet. Full costs $349; Light costs $149.

[Download the sample model](#sample) and inspect every formula before you buy.

## How the store revenue build works

**Store sales** = stores open × selling area per store × sales per square foot per year, divided across the months. From year 2, sales per square foot grow by your **like-for-like** rate.

**New stores** open on the first day of a later year. Each new store brings its own selling area, rent and running costs, plus its fit-out as capital spending in the month it opens.

**Seasonality.** One driver, the November–December uplift, raises the holiday months and lowers the other ten so the annual total is unchanged. That puts the stock build-up and the cash low point in the right months.

**Returns** come off gross sales; **product cost** is a % of net sales.

If you also sell online, the same model adds an online channel (visits, conversion, average order value, paid ads, fulfilment). Set those drivers to zero for a store-only business. For an online-led brand, see [e-commerce financial model for investors](/models/ecommerce-financial-model-for-investors).

## The costs a lender will look at

| Cost | How it's modelled |
|---|---|
| Rent | Selling area × rent per sq ft per year, per store |
| Store running costs | Per store per month (utilities, maintenance, local costs) |
| People | Roles, headcount, salaries, start dates, payroll taxes and benefits, wage growth |
| Payment processing | % of net sales |
| Software and G&A | Monthly amounts |
| Fit-out and equipment | Capital spending at opening, depreciated over time |

**Rent per square foot against sales per square foot** is the ratio to watch: rent is fixed, sales are not. The scenario switch shows what the lease looks like in a slow year.

## Inventory: where retail cash goes

Inventory is held as **days of product cost**. Before a shop sells anything, it buys stock, and before the holidays it buys more. The model carries that through the cash flow statement and balance sheet, together with receivable and payable days, and reports year-end inventory and inventory turns. Many retail loan applications are really about financing this working capital, so it needs to be in the numbers.

An illustration with made-up inputs (not benchmarks): one store with 1,500 sq ft selling $300 per sq ft a year makes $450,000 of sales, or $37,500 in an average month. At rent of $30 per sq ft a year, rent is $45,000 a year, 10% of sales. If sales per sq ft come in 20% lower, rent rises to 12.5% of sales, while the lease stays the same.

## What a lender expects

The SBA's guide to business plans asks for a five-year outlook with forecasted income statements, balance sheets, cash flow statements and capital expenditure budgets, and monthly or quarterly detail in the first year ([SBA — Write your business plan](https://legacy.sba.gov/business-guide/plan-your-business/write-your-business-plan)). Your lender may ask for less or more; ask before you build. The model supports 1, 3 or 5 years in monthly or annual detail, with loan amount, rate and term as inputs and repayments in the cash flow.

## What you get

**Full — $349:** Dashboard with the scenario selector and retail metrics; Inputs; monthly detail for store and online sales, costs, inventory, working capital, fit-out, loan and equity; annual P&L, cash flow statement and balance sheet; headcount plan; Checks sheet.

**Light — $149:** Inputs, P&L with period detail and the metrics, Checks sheet. A lender will usually want Full; upgrade later by paying the difference.

Before release, every scenario and year is recomputed independently in plain Python and must match the workbook within $1. That covers the statements plus stores open and online sales. The Checks sheet must show no FAIL, and it stays in the file for your lender to see.

## Sample {#sample}

The sample is a growing retailer with two stores and an online channel: Full tier, three years of monthly detail, all three scenarios. Set the online drivers to zero to see a store-only business, then change sales per square foot and follow it to cash.

[Download the sample model (.xlsx)](/samples/retail-full.xlsx)

## Common mistakes in store projections

1. **Sales per square foot from a flagship, applied to a new shop.** Use comparable stores in comparable locations.
2. **No seasonality.** The cash low point moves when the holiday stock is bought.
3. **Fit-out in the first month's P&L.** It is capital spending, depreciated.
4. **No inventory in the cash flow.** The most common reason a profitable shop runs short of cash.
5. **One scenario.** The lender will think about the slow year anyway; show it first.

## Questions

**Can I model several stores opening over time?**
Yes: stores open at the start, plus new stores opening at the start of later years.

**Does it fit a café or restaurant?**
Use the [restaurant and coffee shop model](/models/restaurant-coffee-shop-financial-projections) instead; it is built around customers per day and average ticket.

**What if the model doesn't fit my business?**
Write to us within 7 days and we refund the full amount.

See also: [Financial projections for a bank loan](/guides/financial-projections-for-bank-loan) · [SBA loan financial projections](/models/sba-loan-financial-projections) · [All custom financial models](/models/custom-financial-model)

[Build my retail model — from $149](/start)
