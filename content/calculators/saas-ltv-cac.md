---
slug: /calculators/saas-ltv-cac
title: LTV to CAC Ratio Calculator for SaaS and Subscriptions | StartupModel
description: Enter revenue per customer, gross margin, churn and what you spend to win customers. Get CAC, customer lifetime value, the LTV to CAC ratio and the months to earn back the acquisition cost.
keyword: LTV CAC calculator
template: saas
related: [saas-mrr-growth-churn, saas-runway]
---

# LTV to CAC calculator

LTV to CAC compares what a customer is worth over their lifetime with what it cost to win them. Enter your sales and marketing spend, how many customers it brought in, what a customer pays each month, your gross margin and your monthly churn. The ratio and the payback time update as you type.

```inputs
- key: spend
  label: Sales and marketing spend per month
  unit: $
  default: 18000
  min: 0
  max: 100000000
  step: 100
  format: money
  hint: Ads, salaries of the people who sell, tools and commissions for the month.
- key: new
  label: New customers per month
  default: 20
  min: 0
  max: 1000000
  step: 1
  format: int
  hint: Customers won in the same month as the spend.
- key: arpa
  label: Revenue per customer per month
  unit: $
  default: 120
  min: 0
  max: 1000000
  step: 1
  format: money
  hint: Average monthly revenue per paying customer.
- key: gm
  label: Gross margin
  unit: "%"
  default: 80
  min: 0
  max: 100
  step: 0.5
  format: percent
  hint: Revenue less hosting, support and payment fees, as a share of revenue.
- key: churn
  label: Monthly customer churn
  unit: "%"
  default: 3
  min: 0
  max: 50
  step: 0.1
  format: percent
  hint: The share of customers who cancel each month.
```

```outputs
- key: cac
  label: Customer acquisition cost (CAC)
  formula: spend / new
  format: money
- key: profit_month
  label: Gross profit per customer per month
  formula: arpa * gm / 100
  format: money2
- key: lifetime
  label: Expected customer lifetime
  formula: 100 / churn
  format: number1
  note: In months, from churn.
- key: ltv
  label: Customer lifetime value (LTV)
  formula: profit_month * lifetime
  format: money
  note: Gross profit over the lifetime, before any discounting.
- key: ltv_cac
  label: LTV to CAC ratio
  formula: ltv / cac
  format: multiple
  highlight: true
- key: payback
  label: Months to earn back the CAC
  formula: cac / profit_month
  format: number1
```

```table
title: What churn does to the ratio
input: churn
values: 1.5, 2, 3, 4, 5
outputs: lifetime, ltv, ltv_cac
```

```examples
- name: The starting numbers
  inputs: spend=18000, new=20, arpa=120, gm=80, churn=3
  expect: cac=900, profit_month=96, lifetime=33.333333, ltv=3200, ltv_cac=3.555556, payback=9.375
- name: A low-priced product with higher churn
  inputs: spend=6000, new=60, arpa=29, gm=85, churn=6
  expect: cac=100, profit_month=24.65, lifetime=16.666667, ltv=410.833333, ltv_cac=4.108333, payback=4.056795
- name: An expensive sale to a business
  inputs: spend=60000, new=6, arpa=900, gm=75, churn=1.5
  expect: cac=10000, profit_month=675, lifetime=66.666667, ltv=45000, ltv_cac=4.5, payback=14.814815
- name: No churn gives no lifetime
  inputs: spend=18000, new=20, arpa=120, gm=80, churn=0
  expect: cac=900, profit_month=96, lifetime=—, ltv=—, ltv_cac=—, payback=9.375
- name: No new customers gives no CAC
  inputs: spend=18000, new=0, arpa=120, gm=80, churn=3
  expect: cac=—, profit_month=96, lifetime=33.333333, ltv=3200, ltv_cac=—, payback=—
```

## How LTV to CAC is calculated

The calculator works in five steps:

1. **CAC** = sales and marketing spend ÷ new customers won in the same month.
2. **Gross profit per customer per month** = revenue per customer × gross margin.
3. **Expected lifetime in months** = 100 ÷ monthly churn %. A churn of 3% a month means a customer stays 33.3 months on average.
4. **LTV** = gross profit per customer per month × lifetime.
5. **LTV to CAC** = LTV ÷ CAC. The payback line divides CAC by monthly gross profit per customer.

With the starting numbers (example values, not benchmarks) $18,000 of spend wins 20 customers, so a customer costs $900 to win. Each customer pays $120 a month, and at an 80% gross margin that is $96.00 of gross profit. At 3% churn the customer stays 33.3 months, so lifetime value is $3,200. LTV is 3.56 times CAC, and the $900 is earned back in about 9.4 months.

## How to read the result

The ratio says how many dollars of lifetime gross profit each dollar of acquisition buys. The payback time says how long your cash is tied up before it comes back, which matters more when money is short. A ratio can look healthy while the payback is too long for your cash position; read the two together.

A commonly quoted guideline is that LTV to CAC should be higher than 3, and that CAC should be recovered within 12 months; David Skok, who set it out, now accepts longer periods in some businesses ([SaaS Metrics 2.0](https://www.forentrepreneurs.com/pt-br/saas-metrics-2-definitions)). His guideline uses LTV without a gross margin adjustment, while this calculator uses gross profit, which is the stricter version. Treat any guideline as a prompt to look at your own numbers, not as a pass mark.

The table shows how sensitive the ratio is to churn. Churn sits under lifetime, so halving it doubles the lifetime, and a small change in churn moves LTV a lot. The second example, a $29 product with 6% churn and a CAC of $100, has an LTV of $411 and a ratio of 4.11. The third, a $900 product sold to businesses with a CAC of $10,000, has an LTV of $45,000 and a ratio of 4.50 but takes about 14.8 months to pay back.

## Typical mistakes

- **Leaving out costs in CAC.** Include salaries of the people who sell, tools and commissions, not only ad spend.
- **Counting revenue instead of gross profit.** LTV on revenue overstates what a customer is worth, because hosting, support and payment fees come out of it.
- **Matching spend to the wrong customers.** Spend in one month often wins customers in a later month. Use a quarter if your sales cycle is long.
- **Mixing customer churn and revenue churn.** This calculator uses customer churn. If larger customers leave less often, the average is not the whole story.
- **Using a blended number for different segments.** Annual and monthly plans, or small and large customers, behave differently. Run them separately.

## What this calculator cannot do

It gives one number from a steady state. It cannot show how churn and CAC change as you grow, how long it takes to reach the numbers you entered, or whether you have the cash to fund the months before the payback. A financial model shows revenue, churn and acquisition month by month, ties them to cash and a balance sheet, runs Low / Base / High scenarios for churn and CAC, and keeps a Checks sheet that confirms the totals add up, producing statements an investor or lender can read. The [MRR growth calculator](/calculators/saas-mrr-growth-churn) shows the revenue side and the [runway calculator](/calculators/saas-runway) the cash side.

## FAQ {#faq}

### What is CAC?

Customer acquisition cost is the sales and marketing spend needed to win one new customer. It is the spend for a period divided by the customers won in that period.

### What is LTV?

Lifetime value is the gross profit you expect from a customer over the whole time they stay. This calculator gets it from churn: the lifetime is 100 divided by the churn percentage.

### Why do I get a dash?

A dash means there is no answer. With 0% churn the lifetime is endless, and with no new customers there is no CAC to divide by.

### Should I include free trials and users who never pay?

Include the cost of winning them in the spend, but count only paying customers in the new-customer field. Otherwise CAC looks lower than it is.
