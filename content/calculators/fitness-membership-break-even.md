---
slug: /calculators/fitness-membership-break-even
title: Gym Membership Break-Even Calculator: Members Needed | StartupModel
description: Enter fixed costs, monthly dues, other income and cost per member. Get the members a gym or studio needs to break even, the share of capacity that is, and the profit at your current membership.
keyword: gym break even calculator
template: fitness
related: [fitness-churn-steady-state-members]
guide: /guides/startup-costs-and-break-even-analysis
---

# Gym membership break-even calculator

A gym covers its rent and staff whether ten members or a thousand turn up. Each member then adds their dues, less what they cost to serve. Enter your fixed costs and what a member brings in; the calculator shows how many members you need, how much of your capacity that uses, and where you stand today.

```inputs
- key: fixed
  label: Fixed costs per month
  unit: $
  default: 22000
  min: 0
  max: 100000000
  step: 100
  format: money
  hint: Rent, coaches and front desk, utilities, insurance, software, loan payments.
- key: dues
  label: Dues per member per month
  unit: $
  default: 59
  min: 0
  max: 10000
  step: 1
  format: money
  hint: The average amount a member pays for membership each month.
- key: extras
  label: Other income per member per month
  unit: $
  default: 6
  min: 0
  max: 10000
  step: 1
  format: money
  hint: Drinks, retail, personal training and classes, averaged over all members.
- key: var_cost
  label: Cost per member per month
  unit: $
  default: 7
  min: 0
  max: 10000
  step: 1
  format: money
  hint: Payment fees, cleaning supplies, towels and anything that rises with each member.
- key: members_now
  label: Members today
  default: 420
  min: 0
  max: 100000
  step: 5
  format: int
- key: capacity
  label: Members the space can hold
  default: 600
  min: 1
  max: 100000
  step: 10
  format: int
  hint: The most members the space and the schedule can serve well.
```

```outputs
- key: contrib
  label: Contribution per member per month
  formula: dues + extras - var_cost
  format: money
  note: What each member adds towards the fixed costs.
- key: be_members
  label: Members needed to break even
  formula: fixed / max(contrib, 0)
  format: number1
  highlight: true
- key: be_util
  label: Share of capacity needed to break even
  formula: be_members / capacity * 100
  format: percent
- key: gap
  label: Members above (+) or below (-) break-even
  formula: members_now - be_members
  format: number1
- key: safety
  label: Margin of safety today
  formula: (members_now - be_members) / members_now * 100
  format: percent
- key: profit_now
  label: Profit per month at today's members
  formula: contrib * members_now - fixed
  format: money
  note: Before tax and before the owner's pay if it is not in the fixed costs.
```

```table
title: Members needed at different dues
input: dues
relative: -10, -5, 0, 5, 10
outputs: be_members, be_util, profit_now
```

```examples
- name: The starting numbers
  inputs: fixed=22000, dues=59, extras=6, var_cost=7, members_now=420, capacity=600
  expect: contrib=58, be_members=379.310345, be_util=63.218391, gap=40.689655, safety=9.688013, profit_now=2360
- name: A boutique studio with higher dues
  inputs: fixed=15000, dues=149, extras=12, var_cost=10, members_now=90, capacity=140
  expect: contrib=151, be_members=99.337748, be_util=70.955535, gap=-9.337748, safety=-10.375276, profit_now=-1410
- name: A large low-cost gym
  inputs: fixed=70000, dues=24, extras=3, var_cost=4, members_now=2800, capacity=4500
  expect: contrib=23, be_members=3043.478261, be_util=67.63285, gap=-243.478261, safety=-8.695652, profit_now=-5600
- name: Costs per member above income
  inputs: fixed=22000, dues=10, extras=0, var_cost=14, members_now=420, capacity=600
  expect: contrib=-4, be_members=—, be_util=—, gap=—, safety=—, profit_now=-23680
- name: No members today
  inputs: fixed=22000, dues=59, extras=6, var_cost=7, members_now=0, capacity=600
  expect: contrib=58, be_members=379.310345, be_util=63.218391, gap=-379.310345, safety=—, profit_now=-22000
```

## How membership break-even is calculated

A gym has a high share of fixed costs, so the question is how many members it takes to cover them. The calculator works in three steps:

1. **Contribution per member per month** = dues + other income per member − cost per member.
2. **Members to break even** = fixed costs ÷ contribution per member.
3. **Share of capacity** = members to break even ÷ the members the space can hold.

With the starting numbers (example values, not benchmarks) the fixed costs are $22,000 a month. A member pays $59 in dues, brings in another $6 through drinks, classes and training, and costs $7 to serve, so each member contributes $58. The gym needs 379.3 members to break even, which uses 63.2% of the 600 the space can hold. With 420 members today it is 40.7 members above break-even, a margin of safety of 9.7%, and it makes $2,360 a month before tax.

## How to read the result

The share of capacity is the number to look at first. If break-even needs most of the capacity of the space, the business has no room for a bad month and no room to grow into. If it needs a small share, the fixed costs are low for the size of the place. A studio with a tight capacity needs higher dues, because it cannot fill its way out of trouble.

The table shows what a change in dues does to the members you need and the profit. Dues are the lever with the largest effect and the one owners are most nervous about. It also shows the risk in the other direction: a discount that fills the place can need many more members to produce the same contribution.

The other examples show how different the businesses are. A boutique studio with dues of $149 and 140 places breaks even at 99.3 members, 71.0% of capacity. At 90 members it is 9.3 members short, and the month ends in a loss. A large low-cost gym with dues of $24 contributes only $23 per member, so with fixed costs of $70,000 it needs 3043.5 members, 67.6% of its 4,500. Low dues work only with a large space and tight costs.

## Typical mistakes

- **Treating the signed members as the paying members.** Include only members who pay each month; freezes and unpaid accounts do not contribute.
- **Mixing prices.** If you sell monthly, annual and drop-in passes, enter the average dues per member per month.
- **Forgetting the cost per member.** Payment fees, cleaning and supplies add up as members do.
- **Leaving out the owner's pay.** If you work in the gym, include a wage in the fixed costs.
- **Ignoring seasonality.** If your membership is seasonal, use a typical month, or run the numbers for the weakest months too.

## What this calculator cannot do

It shows one steady level. It does not show how long it takes to build membership from the day you open, what the pre-sale and the first months cost in cash, or how far membership falls each month as people leave. A financial model builds membership month by month from joiners and churn, adds staff and equipment, shows the funding you need to reach the lowest cash point, and runs Low / Base / High scenarios for membership and dues. It ends in lender-ready statements and a Checks sheet. The [churn calculator](/calculators/fitness-churn-steady-state-members) shows the level your joiners can sustain, and the [startup costs and break-even guide](/guides/startup-costs-and-break-even-analysis) explains the cash view.

## FAQ {#faq}

### What counts as a fixed cost for a gym?

Rent, the staff you need to open, utilities, insurance, software, equipment leases and loan payments. Costs that rise with each member go in the cost per member.

### Why is capacity part of the calculation?

Break-even members only make sense against what the space can hold. A figure above your capacity means the plan cannot work at the current dues and costs.

### Does the calculator include enrollment fees?

No. Enter them as other income per member only if you spread them over the average time a member stays.

### Why does the result show a dash?

If the contribution per member is zero or negative, each new member adds nothing towards the fixed costs, and no number of members breaks even.
