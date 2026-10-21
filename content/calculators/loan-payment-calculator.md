---
slug: /calculators/loan-payment-calculator
title: Business Loan Payment Calculator: Payment, Interest, Balance | StartupModel
description: Enter a loan amount, interest rate and term. Get the monthly payment, total interest, interest as a share of the loan, the interest in the first payment and the balance left after a number of years.
keyword: business loan payment calculator
guide: /guides/financial-projections-for-bank-loan
related: [break-even-calculator, startup-cost-calculator, payback-period-calculator]
---

# Business loan payment calculator

A term loan is repaid in equal monthly payments that cover the interest on the balance and part of the balance itself. Enter the amount, the rate and the term; the calculator shows the payment, what the loan costs in interest and how much you still owe after a number of years.

```inputs
- key: loan
  label: Loan amount
  unit: $
  default: 100000
  min: 0
  max: 1000000000
  step: 1000
  format: money
- key: rate
  label: Interest rate
  unit: "%"
  default: 8
  min: 0
  max: 40
  step: 0.125
  format: percent
  hint: The annual rate. Use the rate in your offer, not an average.
- key: years
  label: Loan term
  unit: years
  default: 5
  min: 1
  max: 40
  step: 1
  format: int
- key: years_paid
  label: Years already repaid
  unit: years
  default: 2
  min: 0
  max: 40
  step: 1
  format: int
  hint: Used to show the balance still owed.
```

```outputs
- key: pmt
  label: Monthly payment
  formula: if(rate == 0, loan / (years * 12), loan * (rate / 1200) / (1 - 1 / (1 + rate / 1200) ^ (years * 12)))
  format: money2
  highlight: true
- key: total_paid
  label: Total repaid over the term
  formula: pmt * years * 12
  format: money
- key: interest
  label: Total interest
  formula: total_paid - loan
  format: money
- key: interest_pct
  label: Interest as a share of the loan
  formula: interest / loan * 100
  format: percent
- key: first_interest
  label: Interest in the first payment
  formula: loan * rate / 1200
  format: money2
- key: balance
  label: Balance owed after the years repaid
  formula: round(if(rate == 0, loan - pmt * min(years_paid, years) * 12, loan * (1 + rate / 1200) ^ (min(years_paid, years) * 12) - pmt * ((1 + rate / 1200) ^ (min(years_paid, years) * 12) - 1) / (rate / 1200)), 2)
  format: money
```

```table
title: What the rate does to the cost of the loan
input: rate
values: 6, 7, 8, 9, 10
outputs: pmt, interest, interest_pct
```

```examples
- name: The starting numbers
  inputs: loan=100000, rate=8, years=5, years_paid=2
  expect: pmt=2027.639429, total_paid=121658.36573, interest=21658.36573, interest_pct=21.658366, first_interest=666.666667, balance=64705.64
- name: A longer, larger loan
  inputs: loan=350000, rate=7.5, years=15, years_paid=5
  expect: pmt=3244.54326, total_paid=584017.786802, interest=234017.786802, interest_pct=66.862225, first_interest=2187.5, balance=273335.71
- name: A loan with no interest
  inputs: loan=24000, rate=0, years=4, years_paid=1
  expect: pmt=500, total_paid=24000, interest=0, interest_pct=0, first_interest=0, balance=18000
- name: Fully repaid
  inputs: loan=100000, rate=8, years=5, years_paid=10
  expect: pmt=2027.639429, total_paid=121658.36573, interest=21658.36573, interest_pct=21.658366, first_interest=666.666667, balance=0
- name: No loan
  inputs: loan=0, rate=8, years=5, years_paid=2
  expect: pmt=0, total_paid=0, interest=0, interest_pct=—, first_interest=0, balance=0
```

## How the loan payment is calculated

A term loan is repaid in equal monthly payments. Each payment covers the interest on the balance and the rest repays part of the loan. The payment is set so that the balance is zero after the last one:

**payment = loan × r ÷ (1 − (1 + r)^−n)**

where r is the monthly rate (the yearly rate divided by 12) and n the number of payments (years × 12). With a rate of zero the payment is simply the loan divided by n.

From the payment the calculator works out the **total repaid** (payment × n), the **total interest** (total repaid − loan) and the interest as a share of the loan. The **balance owed** after a number of years comes from carrying the loan forward at the monthly rate and taking away the payments made.

With the starting numbers (example values, not benchmarks) a loan of $100,000 at 8% over 5 years has a monthly payment of $2,027.64. The borrower repays $121,658 in all, so the interest is $21,658, or 21.7% of the loan. The first payment contains $666.67 of interest. After 2 years the balance is $64,706.

## How to read the result

Look at the payment first, because that is what your cash flow has to carry every month. Then look at the total interest, because that is what the loan costs. A longer term lowers the payment and raises the interest. The second example, $350,000 at 7.5% over 15 years, has a payment of $3,244.54, with total interest of $234,018, which is 66.9% of the amount borrowed.

The table shows the effect of the rate. A point of difference is small in a month and large over the term, so compare offers on the total interest as well as on the payment.

The balance line is useful when you plan to sell, refinance or repay early: it is what you would still owe. It shows how slowly a loan is repaid at first, because the early payments are mostly interest. After 2 years of a 5-year loan, nearly two thirds of the loan is still owed.

A loan with no interest, as in the third example, is repaid in equal instalments of the principal: $24,000 over 4 years is $500 a month, and after one year the balance is $18,000.

## Typical mistakes

- **Comparing rates that are quoted differently.** Make sure the rate is the annual rate on the loan, not a monthly rate or a flat rate on the original amount.
- **Leaving out fees.** Arrangement fees, insurance and other charges raise the cost of the loan beyond what this calculator shows.
- **Forgetting balloon payments and interest-only periods.** The calculator assumes equal payments to a zero balance.
- **Judging a loan by the payment alone.** A low payment on a long term costs more in total.
- **Ignoring variable rates.** If the rate can move, test the higher rate in the table.

## What this calculator cannot do

It treats the loan alone. It does not show whether the business can afford the payment from its cash flow, how the interest affects profit and tax, or how the loan combines with other financing. A financial model puts the loan schedule beside the income statement, the cash flow and the balance sheet, tests the repayments in a weak month with Low / Base / High scenarios, and produces lender-ready statements with a Checks sheet. The [bank loan guide](/guides/financial-projections-for-bank-loan) explains what lenders ask to see, and the [startup cost calculator](/calculators/startup-cost-calculator) shows how much you may need to borrow.

## FAQ {#faq}

### Is the payment for principal and interest only?

Yes. Fees, insurance and taxes are not included.

### Why is so much of the early payment interest?

Interest is charged on the balance, which is highest at the start. As the balance falls, the interest share falls and the repayment share rises.

### How does paying off a loan early change the cost?

It cuts the interest, because you stop paying it on the balance you repaid. The balance line shows what you would owe at a given point.

### Why does the interest share show a dash?

If the loan amount is zero, the interest cannot be shown as a share of it.
