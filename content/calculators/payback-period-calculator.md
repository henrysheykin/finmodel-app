---
slug: /calculators/payback-period-calculator
title: Payback Period Calculator: Months to Recover an Investment | StartupModel
description: Enter an investment and the net cash it returns each month. Get the payback period, the yearly return, the gain over your horizon and the net present value at a discount rate you choose.
keyword: payback period calculator
guide: /guides/startup-costs-and-break-even-analysis
related: [break-even-calculator, startup-cost-calculator, loan-payment-calculator]
---

# Payback period calculator

The payback period is the time it takes for an investment to return the cash you put into it. It is the first test many owners apply to a new machine, a second location or a marketing programme. Enter the amount and the net cash it brings in each month; the payback appears, along with a view that allows for the time value of money.

```inputs
- key: invest
  label: Investment
  unit: $
  default: 60000
  min: 0
  max: 1000000000
  step: 500
  format: money
  hint: The cash you spend up front.
- key: cf
  label: Net cash returned per month
  unit: $
  default: 2500
  min: 0
  max: 100000000
  step: 50
  format: money
  hint: Extra cash the investment brings in each month, after the costs of running it.
- key: horizon
  label: Years you will count
  unit: years
  default: 5
  min: 1
  max: 40
  step: 1
  format: int
  hint: How long the investment is expected to keep earning.
- key: disc
  label: Discount rate
  unit: "%"
  default: 10
  min: 0
  max: 50
  step: 0.5
  format: percent
  hint: The yearly return you could earn elsewhere. Your assumption.
```

```outputs
- key: payback_months
  label: Payback period in months
  formula: invest / max(cf, 0)
  format: number1
  highlight: true
- key: payback_years
  label: Payback period in years
  formula: payback_months / 12
  format: number1
- key: annual
  label: Net cash returned per year
  formula: cf * 12
  format: money
- key: roi
  label: Simple yearly return on the investment
  formula: annual / invest * 100
  format: percent
- key: gain
  label: Net gain over the years counted
  formula: annual * horizon - invest
  format: money
  note: Cash returned over the horizon less the investment, not discounted.
- key: npv
  label: Net present value over the years counted
  formula: if(disc == 0, cf * horizon * 12, cf * (1 - 1 / (1 + disc / 100) ^ horizon) / ((1 + disc / 100) ^ (1 / 12) - 1)) - invest
  format: money
  note: Each month's cash is discounted at the rate you entered; negative means it does not earn that rate.
```

```table
title: How the net cash per month changes the payback
input: cf
relative: -20, -10, 0, 10, 20
outputs: payback_months, gain, npv
```

```examples
- name: The starting numbers
  inputs: invest=60000, cf=2500, horizon=5, disc=10
  expect: payback_months=24, payback_years=2, annual=30000, roi=50, gain=90000, npv=58846.250678
- name: A machine with a short life
  inputs: invest=18000, cf=400, horizon=3, disc=8
  expect: payback_months=45, payback_years=3.75, annual=4800, roi=26.666667, gain=-3600, npv=-5182.667445
- name: Investment with no discounting
  inputs: invest=40000, cf=1500, horizon=4, disc=0
  expect: payback_months=26.666667, payback_years=2.222222, annual=18000, roi=45, gain=32000, npv=32000
- name: No cash comes back
  inputs: invest=60000, cf=0, horizon=5, disc=10
  expect: payback_months=—, payback_years=—, annual=0, roi=0, gain=-60000, npv=-60000
- name: Nothing invested
  inputs: invest=0, cf=2500, horizon=5, disc=10
  expect: payback_months=0, payback_years=0, annual=30000, roi=—, gain=150000, npv=118846.250678
```

## How the payback period is calculated

**payback period = investment ÷ net cash returned per month**

The calculator also gives the yearly cash, the simple yearly return on the investment, the gain over the years you count, and a net present value that allows for the time value of money.

With the starting numbers (example values, not benchmarks) an investment of $60,000 that returns $2,500 a month is paid back in 24.0 months, or 2.0 years. It returns $30,000 a year, a simple return of 50.0% a year. Over 5 years the net gain is $90,000 before any discounting. At a discount rate of 10% a year, which is your assumption of what you could earn elsewhere, the net present value is $58,846.

## How to read the result

Payback is a measure of risk and liquidity: how long your money is at stake. A short payback means you are exposed for less time, and that the decision is less sensitive to what happens later. It is a good first filter, but it has two weaknesses, which is why the page shows more than one number.

First, it ignores what happens after the payback date. A project that pays back in two years and stops earning, and one that pays back in two years and earns for ten, have the same payback. The net gain over the years you count shows the difference. Second, it treats a dollar in five years as equal to a dollar today. The net present value discounts each month's cash at the rate you enter. If it is negative, the investment does not earn that rate over the period.

The second example shows both effects. A machine of $18,000 returning $400 a month pays back in 45.0 months, but it is only expected to last 3 years, so it never pays back: the gain is negative, and so is the net present value at a discount rate of 8%. The third shows an investment of $40,000 returning $1,500 a month, which pays back in 26.7 months, and with no discounting the gain and the net present value are both $32,000.

If cash returned is zero, the calculator shows a dash for the payback, because the investment is never recovered.

## Typical mistakes

- **Counting revenue instead of net cash.** Use the cash left after the costs of running the investment, including extra staff, maintenance and tax.
- **Assuming the cash starts at once.** New equipment, a new location or a campaign usually take months to reach full effect. Use the average over the period you count.
- **Ignoring the life of the investment.** Equipment wears out and campaigns fade. Set the years to the time it will really earn.
- **Forgetting reinvestment.** A machine may need replacing, and a shop may need a refit.
- **Using payback as the only test.** Compare it with the net present value and the gain.

## What this calculator cannot do

It assumes a steady monthly cash return from the first month. Real investments ramp up, have seasons and need extra working capital. A financial model builds the return month by month from sales and costs, includes the cash tied up in stock and receivables, and runs Low / Base / High scenarios so you see how the payback moves when sales are slower. It also gives lender-ready statements and a Checks sheet. The [startup cost calculator](/calculators/startup-cost-calculator) adds up the investment, the [break-even calculator](/calculators/break-even-calculator) finds the volume that covers the costs, and the [startup costs guide](/guides/startup-costs-and-break-even-analysis) explains the cash view.

## FAQ {#faq}

### What is a good payback period?

It depends on the risk and the life of the investment. Compare it with how long the investment lasts and how long you can afford to wait.

### What is net present value?

It is the sum of the future cash returns, each discounted back to today at the rate you enter, less the investment. A positive value means the investment earns more than that rate.

### What discount rate should I use?

Use the return you could earn on a similar use of the money, including a margin for risk. It is your own assumption.

### Why does the payback show a dash?

If no cash is returned, the investment is never recovered, so there is no payback period.
