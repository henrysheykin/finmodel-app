---
slug: /business-models/real_estate
title: How Rental Property Makes Money: NOI, Debt Service and Cash Returns | StartupModel
description: How a rental property makes money, with tables from a working financial model: rent, vacancy, operating costs, NOI, loan and equity, break-even and exit assumptions.
keyword: how does rental property make money
secondary: [rental property business model, rental property noi, rental property cash flow, real estate investment funding, rental property break-even]
template: real_estate
published: 2026-10-21
modified: 2026-10-21
sample: real_estate, full, monthly, 5 years
---

# How a rental property makes money

A rental property earns money in two ways. The first is the rent, which pays the running costs and the loan and leaves some cash for the owner. The second is the change in the property's value, which the owner collects only when the property is sold or refinanced. The business is slower and calmer than a restaurant or a software company, but it is also more sensitive to financing: the same building can be a comfortable investment or a strain depending on the loan. This page walks through the arithmetic for one illustrative small apartment building, using tables and charts from a working five-year financial model.

Every figure here comes from the sample workbook you can download at the end of the page. They are the sample's assumptions, not market benchmarks, so read them as a worked example rather than a forecast for a real property.

## What the sample assumes

The sample buys a building for {{num:drivers.price.base}} with {{num:drivers.units.base}} rentable units. In the Base case each unit rents for {{num:drivers.rent.base}} a month, and {{num:drivers.vacancy.base}} of potential rent is lost to vacancy and unpaid bills. The purchase is funded with a {{num:drivers.loan_amount.base}} loan at {{num:drivers.loan_rate.base}} interest and {{num:drivers.equity.base}} of equity. At the end of the plan the sample values a sale at an exit cap rate of {{num:drivers.exit_cap.base}}. The table shows each driver with a Low, Base and High value.

{{table:drivers}}

Closing costs, the land share of the price, rent growth, cost inflation and selling costs sit in the same Inputs sheet and follow the same three-case pattern.

## Revenue: units, rent and vacancy

Rental revenue is simple. Multiply the number of units by the average monthly rent and by twelve to get gross potential rent, which is what the building would collect if every unit were rented all year. Then take off vacancy and credit loss, the rent you do not collect, and you have effective gross income.

In the sample gross potential rent is {{num:unit.gpr.y1}} in year 1 and vacancy takes {{num:unit.vac.y1|abs}} of it, leaving revenue of {{num:pnl.rev.y1}}. Rents rise each year, so revenue reaches {{num:pnl.rev.y5}} by year 5. Economic occupancy, meaning the share of potential rent actually collected, is {{num:unit.occ.y1}}.

{{chart:revenue_costs}}

## Costs: what the owner pays before the bank

A building has operating costs that do not depend on how much the owner borrows. In the sample they are direct property costs (repairs, maintenance and utilities paid by the owner) at {{num:costs.cogs.y1}} of revenue, property tax at {{num:costs.prop_tax.y1}}, property management at {{num:costs.mgmt.y1}}, insurance at {{num:costs.insurance.y1}} and legal, accounting and other general costs at {{num:costs.ga_other.y1}}. Together they use {{num:costs.total.y1}} of revenue and leave an operating margin of {{num:costs.ebitda_m.y1}}.

{{table:costs}}

{{chart:cost_structure}}

That profit before financing is called net operating income, or NOI, and in this table it appears as EBITDA. It is {{num:pnl.ebitda.y1}} in year 1 and {{num:pnl.ebitda.y5}} in year 5. Below NOI come depreciation, interest and tax, which is why net income is far smaller: in year 1 it is a loss of {{num:pnl.ni.y1|abs}}. Depreciation is an accounting cost, not a cash payment. The IRS explains how rental income, expenses and depreciation are treated in [Publication 527, Residential Rental Property](https://www.irs.gov/publications/p527).

{{table:pnl}}

## Investment and funding: price, loan and equity

Here the investment is the purchase itself, plus closing costs and a small reserve. In the sample the property purchase including closing costs is {{num:startup.capex_buy}}. The model also finds the month when cash is lowest, adds the operating cash flow and loan repayments up to then, and adds a buffer. The funding required is {{num:startup.required}}.

{{table:startup}}

A loan of {{num:startup.loan}} and equity of {{num:startup.equity}} bring in {{num:startup.sources}}, a surplus of {{num:startup.gap}} over the requirement. The mix between debt and equity is the main lever in this business. More debt reduces the cash the owner has to put in, but it also raises the payment the building must cover every year.

## Unit economics: NOI per unit and debt service

For a landlord the unit is the apartment. NOI per unit is {{num:unit.noi_unit.y1}} in year 1 and {{num:unit.noi_unit.y5}} in year 5. The ratio of NOI to purchase price, sometimes called the going-in cap rate, is {{num:unit.yield.y1}} in year 1 and {{num:unit.yield.y5}} in year 5.

{{table:unit}}

The table also shows debt service, which is interest plus principal. It is {{num:unit.ds.y1}} a year, against NOI of {{num:unit.noi.y1}} in year 1. The excess of NOI over debt service is the cash left for the owner, before reserves and tax. Lenders look at the same relationship as a ratio, NOI divided by debt service, called the debt service coverage ratio. The loan balance falls from {{num:unit.loan_end.y1}} at the end of year 1 to {{num:unit.loan_end.y5}} at the end of year 5.

## Break-even: when the property pays for itself

The first month with positive operating profit is {{num:breakeven.first_ebitda}}, because rent starts immediately. The first month with positive net income, after depreciation and interest, is {{num:breakeven.first_ni}}. Cash is lowest in {{num:breakeven.low_p}} at {{num:breakeven.min_cash}}. For the payback of the cash invested the answer is "{{num:breakeven.payback}}". In a property deal the return also depends on the exit, so the model values a sale at the end of the plan using the exit cap rate and selling costs, and compares it with your target return.

{{table:breakeven}}

Break-even revenue in this table is operating expenses divided by gross margin, which is {{num:breakeven.be_rev_y1}} in year 1. It covers running costs only. A lender will also ask whether the rent covers the loan payments, so test that by comparing NOI with debt service, as above. Rent, vacancy, operating costs and the interest rate are the numbers that move the answer.

## Key risks

- **Higher vacancy.** A few empty units can erase the margin for debt service.
- **Rising interest rates.** A floating or refinanced loan can cost much more.
- **Unplanned repairs.** A reserve helps, but a big failure can exceed it.
- **Property tax and insurance increases.** They are costs you cannot negotiate.
- **Exit assumptions.** A higher cap rate at sale means a lower sale price.

## How to use Low, Base and High

Each driver has three values, and a switch on the Dashboard of the workbook picks the case for the whole model. Base is your best estimate. Low is a cautious case with lower rent, higher vacancy and a higher exit cap rate. High is a good case.

In the sample, rent ranges from {{num:drivers.rent.low}} to {{num:drivers.rent.high}} a month, and vacancy from {{num:drivers.vacancy.high}} to {{num:drivers.vacancy.low}}. Set the switch to Low and check whether NOI still covers debt service and how the lowest cash balance moves.

## Frequently asked questions

### How does a rental property make money?

It collects rent, pays operating costs and the loan, and keeps the remainder. The owner may also gain when the property rises in value and is sold.

### What is NOI?

Net operating income is rent collected minus operating costs, before the loan, depreciation and income tax.

### Why is net income low when NOI is high?

Depreciation and interest are deducted after NOI. Depreciation is not a cash cost, so cash flow can be better than net income suggests.

### Do I need a lender-ready model?

Lenders usually want to see NOI, debt service and coverage under cautious assumptions. The [rental property pro forma for lenders](/models/rental-property-pro-forma-for-lenders) page describes what the full model provides.

## Next steps

Download the sample and trace any figure on this page back to its cell. When you are ready to use your own numbers, the button below starts a short brief about your property.
