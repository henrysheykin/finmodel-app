---
slug: /calculators/real-estate-dscr
title: DSCR Calculator: Debt Service Coverage Ratio for Property | StartupModel
description: Enter net operating income and the loan amount, rate and term. Get the debt service coverage ratio, the NOI a lender needs at their minimum and the largest loan your income supports.
keyword: DSCR calculator
template: real_estate
related: [real-estate-cap-rate, real-estate-cash-on-cash-return, real-estate-mortgage-payment]
guide: /guides/financial-projections-for-bank-loan
---

# DSCR calculator: can the property pay its loan?

The debt service coverage ratio compares the income a property earns with the loan payments it has to cover. Lenders use it to decide how much to lend. Enter the net operating income and the loan; the calculator shows the ratio, the income a lender would want, and the largest loan the income supports at the minimum ratio you enter.

```inputs
- key: noi
  label: Net operating income per year
  unit: $
  default: 30000
  min: 0
  max: 1000000000
  step: 500
  format: money
  hint: Income less operating costs, before mortgage payments.
- key: loan
  label: Loan amount
  unit: $
  default: 337500
  min: 0
  max: 1000000000
  step: 1000
  format: money
- key: rate
  label: Interest rate
  unit: "%"
  default: 6.5
  min: 0
  max: 25
  step: 0.125
  format: percent
  hint: The annual rate on the loan.
- key: years
  label: Loan term
  unit: years
  default: 30
  min: 1
  max: 40
  step: 1
  format: int
- key: required
  label: Minimum DSCR the lender asks for
  default: 1.25
  min: 0.5
  max: 5
  step: 0.05
  format: number2
  hint: Ask your lender; the minimum differs between lenders and loan types.
```

```outputs
- key: pmt
  label: Loan payment per month
  formula: if(rate == 0, loan / (years * 12), loan * (rate / 1200) / (1 - 1 / (1 + rate / 1200) ^ (years * 12)))
  format: money2
  note: Principal and interest only.
- key: ds
  label: Debt service per year
  formula: pmt * 12
  format: money
- key: dscr
  label: Debt service coverage ratio
  formula: noi / ds
  format: multiple
  highlight: true
  note: NOI divided by the yearly loan payments.
- key: noi_needed
  label: NOI the lender needs for this loan
  formula: ds * required
  format: money
- key: cushion
  label: NOI cushion (negative: income is short)
  formula: (noi - noi_needed) / noi * 100
  format: percent
  note: How far NOI can fall before the minimum is missed.
- key: max_loan
  label: Largest loan at the minimum DSCR
  formula: if(rate == 0, noi / required * years, noi / required / 12 * (1 - 1 / (1 + rate / 1200) ^ (years * 12)) / (rate / 1200))
  format: money
```

```table
title: How the interest rate changes the coverage
input: rate
values: 5, 6, 6.5, 7, 8
outputs: pmt, dscr, max_loan
```

```examples
- name: The starting numbers
  inputs: noi=30000, loan=337500, rate=6.5, years=30, required=1.25
  expect: pmt=2133.229579, ds=25598.754951, dscr=1.171932, noi_needed=31998.443689, cushion=-6.661479, max_loan=316421.639074
- name: A comfortable loan
  inputs: noi=48000, loan=300000, rate=6, years=25, required=1.25
  expect: pmt=1932.904204, ds=23194.850453, dscr=2.069425, noi_needed=28993.563067, cushion=39.596744, max_loan=496661.964823
- name: A zero-interest loan
  inputs: noi=24000, loan=240000, rate=0, years=20, required=1.2
  expect: pmt=1000, ds=12000, dscr=2, noi_needed=14400, cushion=40, max_loan=400000
- name: No loan has no ratio
  inputs: noi=30000, loan=0, rate=6.5, years=30, required=1.25
  expect: pmt=0, ds=0, dscr=—, noi_needed=0, cushion=100, max_loan=316421.639074
- name: Income of zero
  inputs: noi=0, loan=337500, rate=6.5, years=30, required=1.25
  expect: pmt=2133.229579, ds=25598.754951, dscr=0, noi_needed=31998.443689, cushion=—, max_loan=0
```

## How the debt service coverage ratio is calculated

**DSCR = net operating income per year ÷ debt service per year**

Debt service is the twelve monthly payments of principal and interest on the loan. The calculator finds the payment from the loan amount, the rate and the term, then compares it with the NOI.

It also works backwards in two ways. **NOI the lender needs** is the debt service times the minimum ratio, which tells you the income the property must show. **Largest loan at the minimum** is the loan whose payments, at your rate and term, take exactly the NOI divided by the minimum ratio.

With the starting numbers (example values, not benchmarks) a loan of $337,500 at 6.5% over 30 years has a payment of $2,133.23 a month, or $25,599 a year. The NOI of $30,000 covers it 1.17 times. A lender asking for a minimum of 1.25 would need an NOI of $31,998, so the property falls short of that minimum. The largest loan the income supports at that minimum is $316,422.

Lenders set their own minimums. One lender's guidance puts the usual minimum for commercial loans at about 1.25, with a range of 1.15 to 1.35 depending on the property and the loan ([CDC New England](https://cdcnewengland.com/post/debt-service-coverage-ratio)). Enter the figure your lender quotes.

## How to read the result

A ratio of 1.00 means the income exactly pays the loan with nothing to spare. Anything above that is the cushion, and the lender's minimum is the cushion they require. The cushion line says how far the NOI can fall before you miss the minimum; a negative number means the NOI is already short.

If the ratio is too low, there are three ways out: a smaller loan, a longer term or a lower rate, which cut the payment, or a higher NOI. The table shows what the rate alone does to the payment, the ratio and the largest loan. The largest-loan line is the one to bring to a lender conversation: it is the loan that fits your numbers.

The other examples show the contrast. A loan of $300,000 at 6% over 25 years against an NOI of $48,000 has a ratio of 2.07x and a cushion of 39.6%, and the income supports up to $496,662. An interest-free loan of $240,000 over 20 years against $24,000 of NOI has a payment of $1,000 a month and a ratio of 2.00x.

## Typical mistakes

- **Using the net income of the owner instead of the property.** Lenders want the property's NOI, after a vacancy allowance.
- **Including a management fee only if you pay one.** Lenders usually assume that someone manages the property.
- **Forgetting that the rate may be different from the headline rate.** Use the rate in the offer.
- **Ignoring fees and balloon payments.** Only the principal-and-interest payment is in this calculator.
- **Treating the minimum as fixed.** It varies by lender, property type and loan program. Ask.

## What this calculator cannot do

It tests one year of income against one loan. It cannot tell you how the ratio changes as rents grow, how it behaves in the first months before the property is let, or what the lender will accept for your property and your credit. A financial model for a rental property shows the DSCR year by year with the loan schedule, runs Low / Base / High scenarios for rent and vacancy so you see the ratio in a bad year, and prepares the statements and Checks sheet a lender expects. The [bank loan guide](/guides/financial-projections-for-bank-loan) explains what lenders ask for. See also the [cap rate calculator](/calculators/real-estate-cap-rate) for the income and the [cash-on-cash calculator](/calculators/real-estate-cash-on-cash-return) for your own return.

## FAQ {#faq}

### What is a good DSCR?

It depends on the lender. Ask what they require for your property type, then keep a margin above it for a bad year.

### Is DSCR calculated on NOI or cash flow?

On NOI. Cash flow after the debt is what remains once the debt service is paid.

### Does DSCR include taxes and insurance paid through the lender?

Property taxes and insurance are operating costs in the NOI. The DSCR here compares the NOI with the loan payment only.

### Why does the ratio show a dash?

If there is no loan, there is no debt service to divide by. If the NOI is zero, the cushion cannot be calculated, so it shows a dash.
