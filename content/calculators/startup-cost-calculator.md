---
slug: /calculators/startup-cost-calculator
title: Startup Cost Calculator: Total Funding for Opening a Business | StartupModel
description: List your one-off opening costs, add a contingency and a cash buffer of operating months. See the total startup cost, the funding gap after your own cash and how much is working capital.
keyword: startup cost calculator
guide: /guides/startup-costs-and-break-even-analysis
related: [break-even-calculator, payback-period-calculator, loan-payment-calculator]
---

# Startup cost calculator

The money a new business needs is more than the cost of opening the door. It is the one-off costs of getting ready, a cushion for what goes wrong, and enough cash to pay the running costs until sales catch up. Enter your own figures in each line; the total and the gap you must fund update as you type.

```inputs
- key: equipment
  label: Equipment and fit-out
  unit: $
  default: 45000
  min: 0
  max: 1000000000
  step: 500
  format: money
  hint: Tools, machinery, furniture, renovation and signage.
- key: deposits
  label: Deposits and prepayments
  unit: $
  default: 8000
  min: 0
  max: 1000000000
  step: 500
  format: money
  hint: Lease deposit, utility deposits, first insurance premium.
- key: legal
  label: Licences, legal and professional fees
  unit: $
  default: 3500
  min: 0
  max: 1000000000
  step: 100
  format: money
- key: stock
  label: Opening inventory
  unit: $
  default: 12000
  min: 0
  max: 1000000000
  step: 500
  format: money
- key: marketing
  label: Pre-opening marketing
  unit: $
  default: 5000
  min: 0
  max: 1000000000
  step: 100
  format: money
  hint: Website, launch campaign, opening event.
- key: prelaunch_payroll
  label: Pre-opening payroll and training
  unit: $
  default: 9000
  min: 0
  max: 1000000000
  step: 100
  format: money
  hint: Wages paid before the first sale.
- key: contingency
  label: Contingency on the one-off costs
  unit: "%"
  default: 10
  min: 0
  max: 100
  step: 1
  format: percent
  hint: A cushion for overruns. Your assumption.
- key: monthly_costs
  label: Running costs per month
  unit: $
  default: 22000
  min: 0
  max: 1000000000
  step: 500
  format: money
  hint: Rent, wages, utilities and everything else you pay each month.
- key: buffer_months
  label: Months of running costs to hold in cash
  unit: months
  default: 3
  min: 0
  max: 36
  step: 1
  format: int
  hint: How long you expect to fund the losses before sales cover costs. Your assumption.
- key: own_cash
  label: Your own cash for the business
  unit: $
  default: 40000
  min: 0
  max: 1000000000
  step: 1000
  format: money
```

```outputs
- key: one_off
  label: One-off costs
  formula: equipment + deposits + legal + stock + marketing + prelaunch_payroll
  format: money
- key: cont_amt
  label: Contingency
  formula: one_off * contingency / 100
  format: money
- key: working
  label: Cash buffer for running costs
  formula: monthly_costs * buffer_months
  format: money
- key: total
  label: Total funding to raise or have
  formula: one_off + cont_amt + working
  format: money
  highlight: true
- key: gap
  label: Funding still needed after your own cash
  formula: max(total - own_cash, 0)
  format: money
- key: working_share
  label: Share of the total that is cash buffer
  formula: working / total * 100
  format: percent
- key: own_share
  label: Share covered by your own cash
  formula: own_cash / total * 100
  format: percent
```

```table
title: What the cash buffer does to the total
input: buffer_months
values: 1, 2, 3, 4, 6
outputs: working, total, gap
```

```examples
- name: The starting numbers
  inputs: equipment=45000, deposits=8000, legal=3500, stock=12000, marketing=5000, prelaunch_payroll=9000, contingency=10, monthly_costs=22000, buffer_months=3, own_cash=40000
  expect: one_off=82500, cont_amt=8250, working=66000, total=156750, gap=116750, working_share=42.105263, own_share=25.518341
- name: A home-based business
  inputs: equipment=6000, deposits=0, legal=1200, stock=2500, marketing=1500, prelaunch_payroll=0, contingency=15, monthly_costs=3000, buffer_months=4, own_cash=20000
  expect: one_off=11200, cont_amt=1680, working=12000, total=24880, gap=4880, working_share=48.231511, own_share=80.385852
- name: Own cash covers everything
  inputs: equipment=15000, deposits=2000, legal=1000, stock=3000, marketing=1000, prelaunch_payroll=0, contingency=10, monthly_costs=5000, buffer_months=2, own_cash=60000
  expect: one_off=22000, cont_amt=2200, working=10000, total=34200, gap=0, working_share=29.239766, own_share=175.438596
- name: Nothing entered
  inputs: equipment=0, deposits=0, legal=0, stock=0, marketing=0, prelaunch_payroll=0, contingency=10, monthly_costs=0, buffer_months=0, own_cash=0
  expect: one_off=0, cont_amt=0, working=0, total=0, gap=0, working_share=—, own_share=—
```

## What the startup cost is made of

The total has three parts:

1. **One-off costs**: equipment and fit-out, deposits, licences and professional fees, opening inventory, pre-opening marketing and pre-opening payroll.
2. **Contingency**: a percentage of the one-off costs, held for the overruns that almost every opening has.
3. **A cash buffer**: the running costs of a number of months, so that you can pay the bills while sales build up.

**total funding = one-off costs × (1 + contingency) + running costs per month × buffer months**

With the starting numbers (example values, not benchmarks) the one-off costs add up to $82,500. A contingency of 10% adds $8,250. A buffer of 3 months of running costs of $22,000 is $66,000. The total is $156,750, of which 42.1% is the cash buffer. With $40,000 of your own cash, which covers 25.5% of the total, you still need $116,750.

The buffer is the part that most plans leave out. It is not spent on the opening; it is held so that the business can lose money for a while without running out of cash. A business that opens with only the one-off costs covered has no room for a slow start.

## How to read the result

The total is the amount to raise or have, not the cost of the premises. Look at the split: a business with a large buffer share is one where the opening is cheap and the running costs are heavy, such as a service business. A business with a small buffer share is one where the opening is the cost, such as a shop with a fit-out.

The table shows what a longer buffer does to the total and to the gap. Every extra month of buffer costs one month of running costs, which is why it is worth being honest about how long it will take to reach break-even. The [break-even calculator](/calculators/break-even-calculator) tells you the sales, and the months it takes to get there depend on how fast you can build up.

The other examples show a range. A home-based business with $11,200 of one-off costs, a contingency of 15% and a four-month buffer of $12,000 needs $24,880 in total, and $4,880 more than its own cash. In the third, a business with $22,000 of one-off costs and $10,000 of buffer needs $34,200, and its own cash covers 175.4% of it, so no further funding is needed.

## Typical mistakes

- **Leaving out the buffer.** The first months almost never earn enough to pay for themselves.
- **Underestimating deposits.** Leases, utilities and suppliers may all ask for money before you start.
- **Forgetting pre-opening payroll.** Staff are usually hired and trained before the first sale.
- **No contingency.** Fit-outs and permits tend to cost more and take longer than planned.
- **Counting money you do not have yet.** Only your own cash and committed funding belong in the cash field.

## What this calculator cannot do

It adds up a list. It does not show when each amount is spent, how the cash balance moves month by month once you open, or the lowest point it reaches, which is the number that sets the funding you really need. A financial model builds that timeline, ties it to sales and costs, shows the sources and uses of cash, and runs Low / Base / High scenarios so you can see how much more you would need if sales are slower. It also gives you lender-ready statements and a Checks sheet. The [startup costs guide](/guides/startup-costs-and-break-even-analysis) walks through the method, and the [loan payment calculator](/calculators/loan-payment-calculator) shows what borrowing the gap would cost each month.

## FAQ {#faq}

### How much cash buffer should I hold?

It depends on how long it takes you to reach break-even. Estimate that time, add a margin, and enter the months. The break-even calculator and a monthly model help.

### What is a contingency?

It is an allowance for costs you cannot foresee. It is a percentage of the one-off costs, and you choose it.

### Should the owner's pay be in the running costs?

Yes, if you need to draw a wage from the first months. Otherwise the buffer is too small.

### Why do the shares show a dash?

If everything is zero, the total is zero and a share of it cannot be calculated.
