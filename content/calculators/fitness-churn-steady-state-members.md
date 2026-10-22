---
slug: /calculators/fitness-churn-steady-state-members
title: Gym Churn Calculator: Steady-State Membership | StartupModel
description: Enter members today, new joiners and monthly churn. See how many members you lose, where membership levels off, members after N months and the joiners needed each month to reach a target.
keyword: gym churn rate calculator
template: fitness
related: [fitness-membership-break-even]
---

# Gym churn calculator: where membership levels off

Members leave at a steady rate, so a gym that signs the same number of new members every month does not grow forever. Membership rises or falls until the members who leave each month equal the members who join. That level depends on only two numbers: how many join and how fast people leave. Enter yours and the calculator shows it.

```inputs
- key: m0
  label: Members today
  default: 420
  min: 0
  max: 100000
  step: 5
  format: int
- key: new
  label: New members per month
  default: 35
  min: 0
  max: 10000
  step: 1
  format: int
  hint: Members who join each month, as a steady number.
- key: churn
  label: Monthly churn
  unit: "%"
  default: 6
  min: 0
  max: 50
  step: 0.5
  format: percent
  hint: The share of members who cancel each month.
- key: months
  label: Months to look ahead
  unit: months
  default: 12
  min: 1
  max: 120
  step: 1
  format: int
- key: dues
  label: Dues per member per month
  unit: $
  default: 59
  min: 0
  max: 10000
  step: 1
  format: money
- key: target
  label: Members you want
  default: 600
  min: 0
  max: 100000
  step: 10
  format: int
```

```outputs
- key: lost
  label: Members lost per month
  formula: m0 * churn / 100
  format: number1
- key: net_change
  label: Net change in members this month
  formula: new - lost
  format: number1
- key: life
  label: Average membership length
  formula: 100 / churn
  format: number1
  note: In months, from churn.
- key: steady
  label: Membership where it levels off
  formula: new / (churn / 100)
  format: number1
  highlight: true
  note: New members per month divided by the churn rate.
- key: m_n
  label: Members after the chosen months
  formula: if(churn == 0, m0 + new * months, steady + (m0 - steady) * (1 - churn / 100) ^ months)
  format: number1
- key: dues_steady
  label: Dues per month at that level
  formula: steady * dues
  format: money
- key: need_new
  label: New members per month to hold your target
  formula: target * churn / 100
  format: number1
  note: The joiners that replace the members lost at your target size.
```

```table
title: What churn does to the level
input: churn
values: 3, 4, 5, 6, 8
outputs: life, steady, m_n
```

```examples
- name: The starting numbers
  inputs: m0=420, new=35, churn=6, months=12, dues=59, target=600
  expect: lost=25.2, net_change=9.8, life=16.666667, steady=583.333333, m_n=505.599682, dues_steady=34416.666667, need_new=36
- name: A studio losing members
  inputs: m0=150, new=8, churn=8, months=6, dues=140, target=150
  expect: lost=12, net_change=-4, life=12.5, steady=100, m_n=130.31775, dues_steady=14000, need_new=12
- name: Strong retention
  inputs: m0=300, new=20, churn=2.5, months=24, dues=45, target=800
  expect: lost=7.5, net_change=12.5, life=40, steady=800, m_n=527.679221, dues_steady=36000, need_new=20
- name: No churn means no level
  inputs: m0=420, new=35, churn=0, months=12, dues=59, target=600
  expect: lost=0, net_change=35, life=—, steady=—, m_n=840, dues_steady=—, need_new=0
```

## Why membership levels off

Every month, a share of the members leave, and a number of new members join. When there are few members, few leave and the total grows. As the total grows, more leave. Eventually the members who leave each month equal the members who join, and the total stops changing. That level is:

**membership where it levels off = new members per month ÷ monthly churn**

It does not depend on where you start. It depends only on how many join and how fast people leave.

The calculator also rolls the membership forward. Each month the membership is the previous month's times (1 − churn) plus the new members, so after the months you choose the total is the level it levels off at, plus the distance from that level that is left over.

With the starting numbers (example values, not benchmarks) a gym with 420 members, 35 joiners a month and 6% churn loses 25.2 members a month, so it grows by 9.8 in the first month. The average member stays 16.7 months. The membership would level off at 583.3 members, and after 12 months it stands at 505.6. At $59 a member, that level brings in $34,417 a month in dues. To hold a target of 600 members you would need 36.0 new members each month to replace the 6% who leave.

## How to read the result

The level is a ceiling for a given effort. If it is below the size you need, no amount of patience will get you there; you have to raise the joiners, lower the churn, or both. The table shows how strong the churn effect is. A small change in churn moves both the average stay and the ceiling a lot, so work on retention before you spend more on joining.

The other examples show the two directions. A studio with 150 members, 8 joiners and 8% churn has a ceiling of 100 members; it is losing 4 members net in the first month and in six months is down to 130.3. A gym with 20 joiners and churn of 2.5% has a ceiling of 800, so the 24 months shown are only the climb from 300 to 527.7. Retention is slow money: it takes a long time to show but it keeps working.

When churn is zero there is no ceiling and the calculator shows a dash for it, as membership grows by the new members every month.

## Typical mistakes

- **Treating joiners as constant.** Joiners vary with the season and with how much you spend on getting them. Run the numbers for a quiet and a busy month.
- **Counting freezes as members.** A frozen account pays nothing. Count paying members.
- **Mixing churn definitions.** Use the share of members at the start of the month who cancel in the month, the same way each time.
- **Forgetting that churn differs by cohort.** New members often leave faster than long-standing ones, so the average is a rough guide.
- **Reading far-out months as a forecast.** Twenty-four months of one assumption is an illustration.

## What this calculator cannot do

It uses one churn rate and one level of joiners. It does not link joiners to marketing spend, differ by cohort, or show the cost of keeping members. A financial model builds membership, dues, classes and staff month by month, ties them to cash and the balance sheet, and runs Low / Base / High scenarios for churn and joiners. It also checks its own arithmetic in a Checks sheet and produces statements a lender can read. To see how many members the gym needs, use the [membership break-even calculator](/calculators/fitness-membership-break-even).

## FAQ {#faq}

### What is monthly churn?

It is the share of the members at the start of a month who cancel during the month. A churn of 6% means that of every 100 members, six leave.

### How do I find my churn?

Divide the members who cancelled in a month by the members you had at its start, and average several months.

### Why does the membership level not depend on where I start?

Because the gym loses members in proportion to its size. Start higher and you lose more, until losses equal joiners; start lower and you lose fewer, until the same point.

### Why is the level a dash?

When churn is zero, members never leave and the total keeps growing, so there is no level to reach.
