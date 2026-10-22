---
slug: /calculators/car-wash-membership-break-even
title: Car Wash Membership Calculator: MRR and Break-Even Members | StartupModel
description: Enter fixed costs, the monthly plan price and how often members wash. Get the members needed to break even, monthly membership revenue today and the profit at your current member count.
keyword: car wash membership calculator
template: car_wash
related: [car-wash-cost-per-wash]
---

# Car wash membership calculator

An unlimited wash plan turns a car wash into a subscription business: monthly recurring revenue from members, plus single washes sold at the pay station. Members who wash often cost more to serve, so the price and the visit rate decide the margin. Enter your plan and your fixed costs; the break-even member count and today's result update as you type.

```inputs
- key: fixed
  label: Fixed costs per month
  unit: $
  default: 38000
  min: 0
  max: 100000000
  step: 500
  format: money
  hint: Lease or loan, staff on shift, insurance, marketing, maintenance contracts, software.
- key: plan_price
  label: Membership price per month
  unit: $
  default: 25
  min: 0
  max: 10000
  step: 1
  format: money
  hint: The average monthly price across your plans.
- key: visits
  label: Washes per member per month
  default: 3.5
  min: 0
  max: 60
  step: 0.1
  format: number1
  hint: The average number of washes a member uses each month. Your assumption.
- key: var_wash
  label: Variable cost per wash
  unit: $
  default: 0.9
  min: 0
  max: 100
  step: 0.05
  format: money2
  hint: Chemicals, water, electricity and consumables for one wash.
- key: fee_pct
  label: Payment fees on memberships
  unit: "%"
  default: 3
  min: 0
  max: 20
  step: 0.1
  format: percent
  hint: Card processing and billing software, as a share of the plan price.
- key: retail_washes
  label: Single washes sold per month
  default: 2200
  min: 0
  max: 10000000
  step: 50
  format: int
  hint: Washes sold at the pay station to people who are not members.
- key: retail_price
  label: Average price of a single wash
  unit: $
  default: 11
  min: 0
  max: 1000
  step: 0.5
  format: money2
- key: members_now
  label: Members today
  default: 1800
  min: 0
  max: 10000000
  step: 25
  format: int
```

```outputs
- key: contrib
  label: Contribution per member per month
  formula: plan_price * (1 - fee_pct / 100) - visits * var_wash
  format: money2
  note: Plan price less payment fees and the cost of the washes the member uses.
- key: retail_contrib
  label: Contribution from single washes per month
  formula: retail_washes * (retail_price - var_wash)
  format: money
- key: be_members
  label: Members needed to break even
  formula: max(fixed - retail_contrib, 0) / max(contrib, 0)
  format: int
  highlight: true
  note: Round up in practice.
- key: mrr
  label: Membership revenue per month today
  formula: members_now * plan_price
  format: money
- key: profit_now
  label: Profit per month today
  formula: members_now * contrib + retail_contrib - fixed
  format: money
  note: Before tax and before the owner's pay if it is not in the fixed costs.
- key: mrr_share
  label: Memberships as a share of sales
  formula: mrr / (mrr + retail_washes * retail_price) * 100
  format: percent
```

```table
title: Break-even members at different plan prices
input: plan_price
values: 20, 25, 30, 35, 40
outputs: contrib, be_members, profit_now
```

```examples
- name: The starting numbers
  inputs: fixed=38000, plan_price=25, visits=3.5, var_wash=0.9, fee_pct=3, retail_washes=2200, retail_price=11, members_now=1800
  expect: contrib=21.1, retail_contrib=22220, be_members=747.867299, mrr=45000, profit_now=22200, mrr_share=65.028902
- name: A smaller site with a cheaper plan
  inputs: fixed=22000, plan_price=19, visits=3, var_wash=0.8, fee_pct=3, retail_washes=1500, retail_price=9, members_now=1100
  expect: contrib=16.03, retail_contrib=12300, be_members=605.115409, mrr=20900, profit_now=7933, mrr_share=60.755814
- name: Single washes cover the fixed costs
  inputs: fixed=20000, plan_price=25, visits=3.5, var_wash=0.9, fee_pct=3, retail_washes=2500, retail_price=10, members_now=300
  expect: contrib=21.1, retail_contrib=22750, be_members=0, mrr=7500, profit_now=9080, mrr_share=23.076923
- name: Members who cost more than they pay
  inputs: fixed=38000, plan_price=10, visits=15, var_wash=0.9, fee_pct=3, retail_washes=2200, retail_price=11, members_now=1800
  expect: contrib=-3.8, retail_contrib=22220, be_members=—, mrr=18000, profit_now=-22620, mrr_share=42.654028
- name: No members and no sales
  inputs: fixed=38000, plan_price=25, visits=3.5, var_wash=0.9, fee_pct=3, retail_washes=0, retail_price=11, members_now=0
  expect: contrib=21.1, retail_contrib=0, be_members=1800.947867, mrr=0, profit_now=-38000, mrr_share=—
```

## How the membership break-even is calculated

Members pay the same price each month however often they wash, so the heavier users cost more to serve than they pay for. The calculator works out what a member contributes after fees and the washes they use, adds what single washes contribute, and finds the member count that covers the fixed costs:

1. **Contribution per member** = plan price × (1 − payment fees) − washes per member × variable cost per wash.
2. **Contribution from single washes** = single washes × (price of a single wash − variable cost per wash).
3. **Members to break even** = (fixed costs − contribution from single washes) ÷ contribution per member.

With the starting numbers (example values, not benchmarks) a $25 plan loses 3% to payment fees and 3.5 washes at $0.90 each, so each member contributes $21.10. Single washes, 2,200 at $11, add $22,220. Against fixed costs of $38,000 the site needs 748 members to break even. With 1,800 members today it takes in $45,000 a month in membership revenue, which is 65.0% of its sales, and makes $22,200 a month before tax.

## How to read the result

Membership revenue is the number investors and lenders like because it recurs, but it is only worth having if each member contributes. Two things move the contribution: the plan price and the washes each member uses. The table shows the first: as the price rises, the contribution rises by almost the full increase and the members needed fall quickly.

The visit rate is the hidden driver. A plan that attracts members who wash far more often than you assumed has a much lower contribution, and may have none. In the example where the plan costs $10 and members use 15 washes, each member costs more than they pay, so the break-even shows a dash: more members make the loss bigger. Track the average washes per member each month and enter the real figure.

The single-wash contribution reduces the members you need. In the third example, single washes contribute $22,750 against fixed costs of $20,000, so no members are needed to break even and the 300 members add profit. That is the case for keeping the pay station busy, not only selling plans.

## Typical mistakes

- **Using the sign-up count.** Count members who are paying this month; frozen and failed payments contribute nothing.
- **Ignoring cannibalization.** A member who used to buy single washes now pays the plan price, which may be less than they spent before.
- **Forgetting that the visit rate changes with weather and season.** Use a typical average.
- **Leaving out payment fees and failed charges.** They are a real cost of selling plans.
- **Assuming all plans cost the same.** Enter the average price across your plans.

## What this calculator cannot do

It shows a steady month. It does not show how long it takes to build the member base, how many members leave each month and need replacing, what the pre-sale and the ramp-up do to cash, or what the equipment loan does to your cash flow. A financial model for a car wash builds members month by month from joiners and churn, adds the single washes, the labor and the loan, shows the funding you need to the lowest cash point, and runs Low / Base / High scenarios. It ends in lender-ready statements with a Checks sheet. For the unit cost, use the [cost per wash calculator](/calculators/car-wash-cost-per-wash), and for the general method the [break-even calculator](/calculators/break-even-calculator).

## FAQ {#faq}

### What is MRR for a car wash?

Monthly recurring revenue is what members pay each month: the members times the average plan price. It is shown here as membership revenue per month.

### Why do members who wash more often matter?

The price is fixed but the cost rises with each wash. The more a member uses the plan, the less they contribute.

### Do single washes count towards break-even?

Yes. Their contribution is taken off the fixed costs before the members needed are calculated.

### Why does the result show a dash?

If a member costs as much as the plan brings in, or more, each new member adds nothing, so no number of members breaks even.
