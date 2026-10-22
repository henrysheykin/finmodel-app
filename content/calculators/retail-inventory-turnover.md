---
slug: /calculators/retail-inventory-turnover
title: Inventory Turnover Calculator: Turns and Days on Hand | StartupModel
description: Enter cost of goods sold and opening and closing inventory. Get inventory turnover, days of stock on hand, GMROI and the cash that would be freed by a faster turn.
keyword: inventory turnover calculator
template: retail
related: [retail-markup-vs-margin, retail-store-break-even]
---

# Inventory turnover calculator

Inventory turnover says how many times a year you sell through the stock you hold. Days on hand turns the same fact into time: how long a unit sits on the shelf before it sells. Enter the cost of goods sold for a period and the inventory at its start and end; the turns, the days and the cash tied up in stock appear as you type.

```inputs
- key: cogs
  label: Cost of goods sold in the period
  unit: $
  default: 480000
  min: 0
  max: 1000000000
  step: 1000
  format: money
  hint: The cost of the goods you sold, not the price you sold them for.
- key: sales
  label: Sales in the period
  unit: $
  default: 720000
  min: 0
  max: 1000000000
  step: 1000
  format: money
  hint: Net sales for the same period.
- key: inv_start
  label: Inventory at the start, at cost
  unit: $
  default: 80000
  min: 0
  max: 1000000000
  step: 1000
  format: money
- key: inv_end
  label: Inventory at the end, at cost
  unit: $
  default: 100000
  min: 0
  max: 1000000000
  step: 1000
  format: money
- key: days
  label: Days in the period
  unit: days
  default: 365
  min: 1
  max: 366
  step: 1
  format: int
  hint: 365 for a year, 90 for a quarter.
- key: target_turns
  label: Turns you would like to reach
  default: 6
  min: 0.5
  max: 100
  step: 0.5
  format: number1
  hint: Your own goal for the period.
```

```outputs
- key: avg_inv
  label: Average inventory
  formula: (inv_start + inv_end) / 2
  format: money
- key: turns
  label: Inventory turnover
  formula: cogs / avg_inv
  format: multiple
  highlight: true
  note: Cost of goods sold divided by average inventory.
- key: days_on_hand
  label: Days of inventory on hand
  formula: days * avg_inv / cogs
  format: number1
- key: gmroi
  label: Gross margin return on inventory
  formula: (sales - cogs) / avg_inv
  format: multiple
  note: Gross profit earned for each dollar of stock held.
- key: inv_target
  label: Inventory needed at your target turns
  formula: cogs / target_turns
  format: money
- key: cash_free
  label: Cash released at your target turns
  formula: avg_inv - inv_target
  format: money
  note: Negative means the target needs more stock than you hold.
```

```table
title: What faster turns release
input: target_turns
values: 4, 5, 6, 8, 10
outputs: inv_target, cash_free
```

```examples
- name: The starting numbers
  inputs: cogs=480000, sales=720000, inv_start=80000, inv_end=100000, days=365, target_turns=6
  expect: avg_inv=90000, turns=5.333333, days_on_hand=68.4375, gmroi=2.666667, inv_target=80000, cash_free=10000
- name: A fast-moving food shop for a quarter
  inputs: cogs=300000, sales=375000, inv_start=18000, inv_end=22000, days=90, target_turns=20
  expect: avg_inv=20000, turns=15, days_on_hand=6, gmroi=3.75, inv_target=15000, cash_free=5000
- name: Slow furniture stock
  inputs: cogs=210000, sales=380000, inv_start=150000, inv_end=190000, days=365, target_turns=3
  expect: avg_inv=170000, turns=1.235294, days_on_hand=295.47619, gmroi=1, inv_target=70000, cash_free=100000
- name: No stock at all gives no turnover
  inputs: cogs=480000, sales=720000, inv_start=0, inv_end=0, days=365, target_turns=6
  expect: avg_inv=0, turns=—, days_on_hand=0, gmroi=—, inv_target=80000, cash_free=-80000
```

## How inventory turnover is calculated

Turnover compares what you sold, at cost, with the stock it took to sell it:

1. **Average inventory** = (inventory at the start + inventory at the end) ÷ 2, both at cost.
2. **Inventory turnover** = cost of goods sold ÷ average inventory.
3. **Days of inventory on hand** = days in the period × average inventory ÷ cost of goods sold.
4. **GMROI** = gross profit ÷ average inventory.

With the starting numbers (example values, not benchmarks) a shop sold goods that cost $480,000 while holding stock of $80,000 at the start of the year and $100,000 at the end. Average inventory is $90,000, so the stock turned 5.33 times, and a typical unit sat on the shelf for 68.4 days. Sales were $720,000, so every dollar of stock held earned 2.67 dollars of gross profit.

The last two results ask what a faster turn would free. If you could run the same sales on 6 turns, you would need $80,000 of stock instead of $90,000, which releases $10,000 of cash. That cash is real: it no longer sits on the shelf.

## How to read the result

Turnover is a ratio of speed. Fast turns mean less money tied up in stock, fewer markdowns and fresher goods. But a very high turnover can also mean empty shelves and lost sales, so look at it alongside GMROI. GMROI is the better test of whether the stock earns its place, because it combines speed with margin: a slow line with a high margin can still beat a fast line with a thin one.

The table shows the stock you would need and the cash released at several target turns. If you see a negative number, the target needs more stock than you hold now; the cash was not tied up in stock, it was missing from it.

Other cases on the page show the range. A fast-moving food shop with $300,000 of cost of goods sold over a quarter and stock of $20,000 turns 15 times in 90 days, with 6 days on hand. Slow furniture stock of $170,000 against $210,000 of cost of goods sold turns about 1.24 times a year and sits for 295.5 days, with a GMROI of 1.00x. The right level depends on what you sell, so compare with your own history and with shops that sell the same range.

## Typical mistakes

- **Using sales instead of cost of goods sold.** Sales include the margin and make the ratio look better than it is. Stock is held at cost, so compare it with cost.
- **Using the closing inventory only.** A seasonal business can have very different stock at the start and the end. Average several months if you can.
- **Mixing periods.** A quarter of cost of goods sold must be paired with 90 days, not 365.
- **Averaging everything together.** A shop with fast and slow ranges needs the turn for each range, not one figure for all.
- **Cutting stock to raise the turn.** A higher turn is only good if sales hold up.

## What this calculator cannot do

It looks back at one period. It does not tell you what to order, when the cash goes out and comes back, or how a seasonal peak changes the stock you need. A financial model for a shop forecasts stock purchases and the cash they use month by month, links them to sales and payment terms, runs Low / Base / High scenarios for sales and for how fast goods sell, and produces statements and a Checks sheet a lender can read. For the margin side use the [markup vs margin calculator](/calculators/retail-markup-vs-margin), and for the sales you need to cover your costs, the [store break-even calculator](/calculators/retail-store-break-even).

## FAQ {#faq}

### What is a good inventory turnover?

It depends on what you sell. Groceries and fashion move at very different speeds. Compare with your own past periods and with similar shops, and read it together with GMROI.

### Should I use sales or cost of goods sold?

Cost of goods sold. Inventory is valued at cost, so the two sides of the ratio must both be at cost.

### What is GMROI?

Gross margin return on inventory is the gross profit earned for each dollar of stock held at cost. A value of 2.67x means each dollar of stock earned 2.67 dollars of gross profit.

### Why do I see a dash?

If there is no inventory at the start or the end, the average is zero and the ratio cannot be calculated.
