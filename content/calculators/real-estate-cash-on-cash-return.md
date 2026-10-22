---
slug: /calculators/real-estate-cash-on-cash-return
title: Cash-on-Cash Return Calculator for a Rental Property | StartupModel
description: Enter price, down payment, loan terms and net operating income. Get the loan payment, annual cash flow after debt, the cash you invest and the cash-on-cash return, plus DSCR and cap rate.
keyword: cash on cash return calculator
template: real_estate
related: [real-estate-cap-rate, real-estate-dscr, real-estate-mortgage-payment]
---

# Cash-on-cash return calculator

Cash-on-cash return answers a narrow question: for each dollar of your own cash put into the property, how many dollars of cash does it return in a year after the mortgage is paid? Enter the price, how you finance it and the property's net operating income; the calculator shows the payment, the cash flow and the return.

```inputs
- key: price
  label: Purchase price
  unit: $
  default: 450000
  min: 0
  max: 1000000000
  step: 1000
  format: money
- key: down
  label: Down payment
  unit: "%"
  default: 25
  min: 0
  max: 100
  step: 1
  format: percent
  hint: The share of the price you pay in cash.
- key: closing
  label: Closing costs and upfront repairs
  unit: $
  default: 12000
  min: 0
  max: 1000000000
  step: 500
  format: money
  hint: Cash you spend on top of the down payment before the first tenant.
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
- key: noi
  label: Net operating income per year
  unit: $
  default: 30000
  min: 0
  max: 1000000000
  step: 500
  format: money
  hint: Income less operating costs, before mortgage payments. The cap rate calculator builds it.
```

```outputs
- key: loan
  label: Loan amount
  formula: price * (1 - down / 100)
  format: money
- key: cash
  label: Cash invested
  formula: price * down / 100 + closing
  format: money
- key: pmt
  label: Mortgage payment per month
  formula: if(rate == 0, loan / (years * 12), loan * (rate / 1200) / (1 - 1 / (1 + rate / 1200) ^ (years * 12)))
  format: money2
  note: Principal and interest only.
- key: ds
  label: Debt service per year
  formula: pmt * 12
  format: money
- key: cf
  label: Cash flow per year after the mortgage
  formula: noi - ds
  format: money
  note: Before tax.
- key: coc
  label: Cash-on-cash return
  formula: cf / cash * 100
  format: percent
  highlight: true
- key: cap
  label: Cap rate
  formula: noi / price * 100
  format: percent
- key: dscr
  label: Debt service coverage ratio
  formula: noi / ds
  format: multiple
```

```table
title: How the interest rate changes the return
input: rate
values: 5, 5.5, 6, 6.5, 7, 8
outputs: pmt, cf, coc
```

```examples
- name: The starting numbers
  inputs: price=450000, down=25, closing=12000, rate=6.5, years=30, noi=30000
  expect: loan=337500, cash=124500, pmt=2133.229579, ds=25598.754951, cf=4401.245049, coc=3.535137, cap=6.666667, dscr=1.171932
- name: A smaller property with a bigger down payment
  inputs: price=210000, down=30, closing=6000, rate=7, years=25, noi=16000
  expect: loan=147000, cash=69000, pmt=1038.96542, ds=12467.58504, cf=3532.41496, coc=5.119442, cap=7.619048, dscr=1.283328
- name: An interest-free family loan
  inputs: price=300000, down=20, closing=8000, rate=0, years=20, noi=21000
  expect: loan=240000, cash=68000, pmt=1000, ds=12000, cf=9000, coc=13.235294, cap=7, dscr=1.75
- name: No loan, all cash
  inputs: price=300000, down=100, closing=8000, rate=6.5, years=30, noi=21000
  expect: loan=0, cash=308000, pmt=0, ds=0, cf=21000, coc=6.818182, cap=7, dscr=—
- name: Nothing invested
  inputs: price=0, down=0, closing=0, rate=6.5, years=30, noi=21000
  expect: loan=0, cash=0, pmt=0, ds=0, cf=21000, coc=—, cap=—, dscr=—
```

## How cash-on-cash return is calculated

The calculator follows the cash from the purchase to the end of the year:

1. **Loan** = price × (1 − down payment).
2. **Cash invested** = price × down payment + closing costs and upfront repairs.
3. **Mortgage payment** = the level monthly payment that repays the loan over the term at the interest rate.
4. **Cash flow** = net operating income − 12 mortgage payments.
5. **Cash-on-cash return** = cash flow ÷ cash invested × 100.

With the starting numbers (example values, not benchmarks) a property costing $450,000 with 25% down is bought with a loan of $337,500 and $124,500 of cash, including $12,000 for closing and repairs. At 6.5% over 30 years the payment is $2,133.23 a month, or $25,599 a year. A net operating income of $30,000 leaves a cash flow of $4,401, and the cash-on-cash return is 3.5%. The property's cap rate is 6.7%, but the return on the cash you put in is lower, because the loan costs more than the property earns on the borrowed part.

That is the lesson of the calculator. Borrowing helps the return on your cash only when the property earns more than the loan costs. When the cost of the loan is higher than the cap rate, leverage lowers the return.

## How to read the result

Cash-on-cash is a measure of the current income on your cash, not the total return. It ignores the loan repaid out of each payment, the rise or fall in the property's value, and the tax. Use it to compare financing choices and properties on the same basis, not to judge the whole investment.

The table shows how much the interest rate matters. A change of a point in the rate shifts the payment, the cash flow and the return by a visible amount. The coverage ratio at the bottom shows how thin the cushion is: 1.17x means the NOI is only a little above the mortgage payments.

The other examples show the range. A $210,000 property bought with 30% down, at 7% over 25 years, returns 5.1%, with a cap rate of 7.6% and coverage of 1.28x. An interest-free family loan of $240,000 on a $300,000 property returns 13.2% on $68,000 of cash. With no loan at all, the return equals the NOI over the cash invested.

## Typical mistakes

- **Leaving out the cash you spend besides the down payment.** Closing costs, repairs and furnishing are part of the cash invested.
- **Using an NOI that already includes the mortgage.** Use the income before debt payments.
- **Ignoring years with no tenant.** Use a vacancy allowance in your NOI.
- **Assuming the rate stays fixed.** If your rate resets, test the higher rate in the table.
- **Comparing the figure with a total return.** The return from selling, from paying down the loan and from tax is not in it.

## What this calculator cannot do

It shows the first year as a snapshot. It does not show rent growth, rising costs, the loan balance falling, the tax effect, the sale at the end, or the cash needed in a weak year. A financial model for a rental property does all of this in a monthly pro forma, with cash, the loan schedule, Low / Base / High scenarios for rent, vacancy and interest, and lender-ready statements with a Checks sheet. Build the NOI in the [cap rate calculator](/calculators/real-estate-cap-rate), test the lender's coverage in the [DSCR calculator](/calculators/real-estate-dscr), and see the payment in the [mortgage payment calculator](/calculators/real-estate-mortgage-payment).

## FAQ {#faq}

### What is a good cash-on-cash return?

It depends on your alternatives and your risk. Compare it with what you could earn elsewhere with the same cash and with the cost of the loan.

### Does cash-on-cash include the principal I repay?

No. The principal part of the payment is treated as a cash cost here, even though it builds your equity. That is why the figure is a cash measure and not a total return.

### Can the return be negative?

Yes. If the net operating income is less than the mortgage payments, the cash flow is negative and so is the return.

### Why does the result show a dash?

If no cash is invested, a return on it cannot be calculated. The coverage ratio shows a dash when there is no loan.
