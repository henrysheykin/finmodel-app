---
slug: /calculators/real-estate-mortgage-payment
title: Mortgage Payment Calculator With Tax, Insurance and Interest | StartupModel
description: Enter price, down payment, rate and term. Get the monthly mortgage payment, the payment with property tax and insurance, total interest over the loan and the split of the first payment.
keyword: mortgage payment calculator
template: real_estate
related: [real-estate-cash-on-cash-return, real-estate-dscr, real-estate-cap-rate]
guide: /guides/financial-projections-for-bank-loan
---

# Mortgage payment calculator

A mortgage payment is the same amount every month, but its parts change: at first most of it is interest, and over the years more of it repays the loan. Enter the price, the down payment, the rate and the term. The calculator shows the payment, the payment with property tax and insurance added, and what the loan costs in interest.

```inputs
- key: price
  label: Property price
  unit: $
  default: 400000
  min: 0
  max: 1000000000
  step: 1000
  format: money
- key: down
  label: Down payment
  unit: "%"
  default: 20
  min: 0
  max: 100
  step: 1
  format: percent
  hint: The share of the price you pay in cash.
- key: rate
  label: Interest rate
  unit: "%"
  default: 6.5
  min: 0
  max: 25
  step: 0.125
  format: percent
  hint: The annual rate on the loan. Your assumption.
- key: years
  label: Loan term
  unit: years
  default: 30
  min: 1
  max: 40
  step: 1
  format: int
- key: tax
  label: Property tax per year
  unit: $
  default: 4800
  min: 0
  max: 100000000
  step: 100
  format: money
- key: insurance
  label: Insurance per year
  unit: $
  default: 1400
  min: 0
  max: 100000000
  step: 100
  format: money
```

```outputs
- key: loan
  label: Loan amount
  formula: price * (1 - down / 100)
  format: money
- key: pmt
  label: Mortgage payment per month
  formula: if(rate == 0, loan / (years * 12), loan * (rate / 1200) / (1 - 1 / (1 + rate / 1200) ^ (years * 12)))
  format: money2
  highlight: true
  note: Principal and interest only.
- key: all_in
  label: Payment with property tax and insurance
  formula: pmt + (tax + insurance) / 12
  format: money2
- key: total_paid
  label: Total paid to the lender over the term
  formula: pmt * years * 12
  format: money
- key: interest_total
  label: Total interest over the term
  formula: total_paid - loan
  format: money
- key: interest_1
  label: Interest in the first payment
  formula: loan * rate / 1200
  format: money2
- key: principal_1
  label: Loan repaid in the first payment
  formula: pmt - interest_1
  format: money2
```

```table
title: How the rate changes the payment
input: rate
values: 5.5, 6, 6.5, 7, 7.5
outputs: pmt, all_in, interest_total
```

```examples
- name: The starting numbers
  inputs: price=400000, down=20, rate=6.5, years=30, tax=4800, insurance=1400
  expect: loan=320000, pmt=2022.617675, all_in=2539.284342, total_paid=728142.363064, interest_total=408142.363064, interest_1=1733.333333, principal_1=289.284342
- name: A shorter loan
  inputs: price=400000, down=20, rate=6.5, years=15, tax=4800, insurance=1400
  expect: loan=320000, pmt=2787.543569, all_in=3304.210236, total_paid=501757.842411, interest_total=181757.842411, interest_1=1733.333333, principal_1=1054.210236
- name: A smaller loan at a lower rate
  inputs: price=250000, down=35, rate=5, years=25, tax=3000, insurance=900
  expect: loan=162500, pmt=949.958817, all_in=1274.958817, total_paid=284987.645235, interest_total=122487.645235, interest_1=677.083333, principal_1=272.875484
- name: An interest-free loan
  inputs: price=240000, down=25, rate=0, years=20, tax=2400, insurance=600
  expect: loan=180000, pmt=750, all_in=1000, total_paid=180000, interest_total=0, interest_1=0, principal_1=750
- name: A price of zero
  inputs: price=0, down=20, rate=6.5, years=30, tax=0, insurance=0
  expect: loan=0, pmt=0, all_in=0, total_paid=0, interest_total=0, interest_1=0, principal_1=0
```

## How the mortgage payment is calculated

A fixed-rate mortgage is repaid in equal monthly payments. The payment is set so that, after the last one, the balance is exactly zero:

**payment = loan × r ÷ (1 − (1 + r)^−n)**

where r is the monthly rate (the yearly rate divided by 12) and n is the number of monthly payments (years × 12). If the rate is zero, the payment is the loan divided by n.

With the starting numbers (example values, not benchmarks) a property priced at $400,000 with 20% down needs a loan of $320,000. At 6.5% over 30 years the payment of principal and interest is $2,022.62 a month. Adding property tax of $4,800 and insurance of $1,400 a year brings the monthly outlay to $2,539.28. Over the full term the borrower pays $728,142 to the lender, of which $408,142 is interest.

The first payment shows how a mortgage works. Of the $2,022.62, $1,733.33 is interest on the whole balance and only $289.28 repays the loan. As the balance falls, the interest part shrinks and the repayment part grows.

## How to read the result

The monthly payment is the number lenders and buyers look at, but the total interest is the cost of the loan. The table shows both for several rates: a change of half a point looks small each month and large over thirty years.

The second example shows the effect of the term. The same loan over 15 years instead of 30 has a payment of $2,787.54 a month, a higher outlay, and $181,758 of interest, less than half as much. A shorter term costs more each month and far less in total. The third example, a $250,000 property with 35% down at 5% over 25 years, needs a loan of $162,500 and pays $949.96 a month.

For an investment property, compare the payment with the rent. A payment that is not covered by the net operating income means you fund the gap from other money. The [DSCR calculator](/calculators/real-estate-dscr) shows the lender's view of this, and the [cash-on-cash calculator](/calculators/real-estate-cash-on-cash-return) shows your return after the payment.

## Typical mistakes

- **Comparing payments without comparing the terms.** A lower payment on a longer loan costs more in total.
- **Forgetting taxes and insurance.** They are part of what you pay each month, even when the lender collects only the principal and interest.
- **Leaving out other costs.** Mortgage insurance, homeowners association fees and maintenance are not in this calculator.
- **Using a teaser rate.** If the rate changes after a few years, test the higher rate.
- **Forgetting the down payment and closing costs.** The cash you need on day one is more than the down payment alone.

## What this calculator cannot do

It computes a fixed-rate payment on a single loan. It does not handle adjustable rates, interest-only periods, extra payments, mortgage insurance or the tax effect of the interest. A financial model for a property builds the loan schedule month by month beside rent, costs and cash, runs Low / Base / High scenarios for rate and rent, and produces lender-ready statements with a Checks sheet. For the underwriting side, see the [bank loan guide](/guides/financial-projections-for-bank-loan) and the [cap rate calculator](/calculators/real-estate-cap-rate).

## FAQ {#faq}

### Does the payment include taxes and insurance?

The main payment line is principal and interest only. The second line adds the property tax and insurance you enter, spread over twelve months.

### Why is so little of the first payment principal?

Interest is charged on the whole balance, which is largest at the start. The repayment part is what is left of the payment after the interest.

### What if the rate is 0%?

The payment is the loan divided by the number of months, and no interest is charged. This is rare for a mortgage, but it models an interest-free family loan.

### Can I use it for a rental property?

Yes. Enter the price, the down payment and the loan terms. The result is the principal and interest you need to cover from the rent.
