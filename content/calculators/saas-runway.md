---
slug: /calculators/saas-runway
title: Startup Runway Calculator: Months of Cash Left | StartupModel
description: Enter your cash, monthly revenue, monthly costs and revenue growth. See net burn, months of runway, when to start raising and how much cash you would have in 12 months.
keyword: runway calculator
template: saas
related: [saas-mrr-growth-churn, saas-ltv-cac]
---

# Runway calculator: how many months of cash you have

Runway is the number of months until the cash runs out if nothing changes. It is the first thing an investor asks about and the number that decides when you must start raising money or cutting costs. Enter the cash you have and your monthly figures; the runway and the cash left after 12 months update as you type.

```inputs
- key: cash
  label: Cash in the bank
  unit: $
  default: 400000
  min: 0
  max: 1000000000
  step: 1000
  format: money
  hint: What you can spend today, not including money you expect to receive.
- key: revenue
  label: Cash revenue per month
  unit: $
  default: 30000
  min: 0
  max: 100000000
  step: 500
  format: money
  hint: Cash you collect from customers each month.
- key: costs
  label: Cash costs per month
  unit: $
  default: 60000
  min: 0
  max: 100000000
  step: 500
  format: money
  hint: Salaries, hosting, tools, marketing, rent, everything you pay out.
- key: growth
  label: Revenue growth per month
  unit: "%"
  default: 4
  min: 0
  max: 30
  step: 0.5
  format: percent
  hint: Your assumption for how fast revenue grows from month to month.
- key: lead
  label: Months a fundraise takes
  unit: months
  default: 6
  min: 0
  max: 24
  step: 1
  format: int
  hint: From the first conversation to money in the bank.
```

```outputs
- key: net_burn
  label: Net burn per month
  formula: costs - revenue
  format: money
  note: Cash costs less cash revenue; negative means you make cash.
- key: runway
  label: Runway at today's burn
  formula: cash / max(net_burn, 0)
  format: number1
  highlight: true
  note: In months, assuming revenue and costs stay as they are.
- key: raise_by
  label: Months from now to start raising
  formula: runway - lead
  format: number1
  note: Negative means the runway is already shorter than a fundraise takes.
- key: cash_12
  label: Cash after 12 months with revenue growth
  formula: cash - 12 * costs + revenue * if(growth == 0, 12, ((1 + growth / 100) ^ 12 - 1) / (growth / 100))
  format: money
  note: Costs stay flat. Negative means the cash runs out before then.
- key: revenue_12
  label: Revenue in month 12
  formula: revenue * (1 + growth / 100) ^ 11
  format: money
```

```table
title: How costs move the runway
input: costs
relative: -10, -5, 0, 5, 10
outputs: net_burn, runway, cash_12
```

```examples
- name: The starting numbers
  inputs: cash=400000, revenue=30000, costs=60000, growth=4, lead=6
  expect: net_burn=30000, runway=13.333333, raise_by=7.333333, cash_12=130774.163926, revenue_12=46183.621689
- name: A lean team with no growth
  inputs: cash=150000, revenue=8000, costs=21000, growth=0, lead=4
  expect: net_burn=13000, runway=11.538462, raise_by=7.538462, cash_12=-6000, revenue_12=8000
- name: Burning fast
  inputs: cash=1200000, revenue=40000, costs=190000, growth=6, lead=9
  expect: net_burn=150000, runway=8, raise_by=-1, cash_12=-405202.35211, revenue_12=75931.942333
- name: Revenue covers the costs
  inputs: cash=250000, revenue=70000, costs=55000, growth=2, lead=6
  expect: net_burn=-15000, runway=—, raise_by=—, cash_12=528846.280969, revenue_12=87036.201588
```

## How runway is calculated

**net burn = cash costs per month − cash revenue per month**

**runway in months = cash in the bank ÷ net burn**

With the starting numbers (example values, not benchmarks) the company has $400,000, collects $30,000 a month and pays out $60,000, so the net burn is $30,000 and the runway is 13.3 months. If a fundraise takes 6 months, the company should start about 7.3 months from now, because the money has to arrive before the cash runs out, not on the day it does.

The simple runway assumes that nothing changes. Revenue usually grows, so the calculator adds a second view: cash after 12 months, with revenue growing at the monthly rate you enter and costs held flat. At 4% growth the company ends the year with $130,774 and revenue of $46,184 in month 12, up from $30,000. That does not mean the runway is longer than 13.3 months in every case; it means that if the growth assumption holds and costs stay flat, the company does not run out within the year. The growth is your assumption, so test it against what you have actually achieved.

## How to read the result

Use runway as a planning number, not a forecast. Three readings matter:

- **Runway shorter than the fundraise lead time.** The "months from now to start raising" line goes negative. That is the signal to cut costs or look for a bridge now.
- **Cash after 12 months negative.** The cash runs out within the year even with the growth you assumed.
- **A dash for runway.** Revenue covers the costs, so there is no burn and no runway to count. The cash after 12 months is still shown.

Two other cases show the range. A lean team with $150,000, $8,000 revenue and $21,000 costs has 11.5 months and, with no growth, runs out of cash before the year ends. A company with $1,200,000 and a net burn of $150,000 has 8 months, shorter than a 9 month fundraise, so the raise-by line shows -1.0.

## Typical mistakes

- **Using accounting profit instead of cash.** Annual contracts paid up front, unpaid invoices and loan repayments change cash, not profit. Enter cash figures.
- **Counting committed money as cash.** A term sheet is not cash in the bank.
- **Assuming growth with no extra cost.** Revenue growth usually needs more people, hosting and marketing. Costs here are flat, so raise them if your plan calls for hiring.
- **Forgetting the fundraise lead time.** The date on which the money runs out is not the date you should start looking for more.
- **Reading one month's burn as typical.** Annual bills and tax payments make some months heavier than others. Use a typical month.

## What this calculator cannot do

It looks at three numbers and one growth rate. A financial model shows cash month by month: payment timing, payroll, tax, loan repayments, the funding you need to reach the lowest cash point and the month in which it happens. It runs Low / Base / High scenarios, so you see the runway when growth is slower than planned, and ends in statements and a Checks sheet that lenders and investors can read. The [MRR growth calculator](/calculators/saas-mrr-growth-churn) rolls revenue forward, and the [LTV to CAC calculator](/calculators/saas-ltv-cac) tests whether growth pays for itself.

## FAQ {#faq}

### What is the difference between gross burn and net burn?

Gross burn is everything you pay out in a month. Net burn is what you pay out less what you collect. Runway uses net burn.

### How much runway should a startup have?

There is no single figure. It depends on how long it takes you to raise money or reach break-even. Compare the runway with the lead time you enter and leave yourself margin.

### Does the calculator include debt repayments?

Only if you include them in the cash costs. Add loan repayments to the monthly costs, or the runway will be too long.

### Why does the table move only costs?

Costs are the lever you control fastest. The table shows how a cut or a rise in costs changes burn, runway and cash after 12 months. Change revenue and growth in the fields to test the other side.
