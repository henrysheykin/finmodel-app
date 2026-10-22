---
slug: /calculators/guest-house-break-even-occupancy
title: Guest House Break-Even Occupancy Calculator | StartupModel
description: Enter fixed costs, rate, extras, booking commissions and cost per room night. Get the occupancy a guest house needs to break even, the rate it needs at current occupancy and the monthly profit.
keyword: bed and breakfast break even occupancy
template: guest_house
related: [guest-house-adr-occupancy-revpar]
---

# Guest house break-even occupancy calculator

A guest house has a large share of fixed costs, so the question is how full the rooms must be before it stops losing money. Each room night sold brings in the rate and any extras, less the commission on the booking and the cost of turning the room round. Enter your figures; the occupancy you need and where you stand today appear as you type.

```inputs
- key: fixed
  label: Fixed costs per month
  unit: $
  default: 12500
  min: 0
  max: 100000000
  step: 250
  format: money
  hint: Mortgage or rent, utilities, insurance, software, the staff you need whatever the bookings.
- key: rooms
  label: Rooms for guests
  default: 6
  min: 1
  max: 1000
  step: 1
  format: int
- key: days
  label: Days open per month
  unit: days
  default: 30
  min: 1
  max: 31
  step: 1
  format: int
- key: adr
  label: Average daily rate
  unit: $
  default: 135
  min: 0
  max: 100000
  step: 1
  format: money
  hint: Room revenue divided by room nights sold, before sales tax and lodging tax.
- key: extras
  label: Other revenue per occupied room night
  unit: $
  default: 12
  min: 0
  max: 10000
  step: 0.5
  format: money2
  hint: Breakfast and other extras, averaged over the nights sold.
- key: commission
  label: Commission on room revenue
  unit: "%"
  default: 12
  min: 0
  max: 50
  step: 0.5
  format: percent
  hint: The average share of room revenue paid to booking platforms and payment providers. Your assumption.
- key: var_night
  label: Cost per occupied room night
  unit: $
  default: 24
  min: 0
  max: 10000
  step: 0.5
  format: money2
  hint: Cleaning, laundry, breakfast ingredients, toiletries and utilities that rise with each night.
- key: occ_now
  label: Occupancy today
  unit: "%"
  default: 68
  min: 0
  max: 100
  step: 1
  format: percent
```

```outputs
- key: net_night
  label: Contribution per occupied room night
  formula: adr * (1 - commission / 100) + extras - var_night
  format: money2
- key: available
  label: Room nights available per month
  formula: rooms * days
  format: int
- key: be_nights
  label: Room nights to sell per month to break even
  formula: fixed / max(net_night, 0)
  format: number1
- key: be_occ
  label: Break-even occupancy
  formula: be_nights / available * 100
  format: percent
  highlight: true
  note: Above 100% means the rooms cannot cover the fixed costs at this rate.
- key: be_adr
  label: Average daily rate to break even at today's occupancy
  formula: ((fixed / (available * occ_now / 100) - extras + var_night) / (1 - commission / 100))
  format: money2
- key: profit_now
  label: Profit per month at today's occupancy
  formula: available * occ_now / 100 * net_night - fixed
  format: money
  note: Before tax and before the owner's pay if it is not in the fixed costs.
- key: safety
  label: Occupancy cushion today
  formula: occ_now - be_occ
  format: number1
  note: Percentage points above (+) or below (-) break-even.
```

```table
title: Break-even occupancy at different rates
input: adr
values: 105, 120, 135, 150, 165
outputs: net_night, be_occ, profit_now
```

```examples
- name: The starting numbers
  inputs: fixed=12500, rooms=6, days=30, adr=135, extras=12, commission=12, var_night=24, occ_now=68
  expect: net_night=106.8, available=180, be_nights=117.041199, be_occ=65.022888, be_adr=129.686572, profit_now=572.32, safety=2.977112
- name: A larger house with a lower rate
  inputs: fixed=24000, rooms=14, days=30, adr=95, extras=8, commission=15, var_night=20, occ_now=60
  expect: net_night=68.75, available=420, be_nights=349.090909, be_occ=83.116883, be_adr=126.162465, profit_now=-6675, safety=-23.116883
- name: A rate too low to cover the fixed costs
  inputs: fixed=12500, rooms=6, days=30, adr=60, extras=5, commission=12, var_night=24, occ_now=68
  expect: net_night=33.8, available=180, be_nights=369.822485, be_occ=205.456936, be_adr=137.641117, profit_now=-8362.88, safety=-137.456936
- name: A night that costs more than it earns
  inputs: fixed=12500, rooms=6, days=30, adr=20, extras=0, commission=12, var_night=24, occ_now=68
  expect: net_night=-6.4, available=180, be_nights=—, be_occ=—, be_adr=143.322935, profit_now=-13283.36, safety=—
- name: No rooms sold today
  inputs: fixed=12500, rooms=6, days=30, adr=135, extras=12, commission=12, var_night=24, occ_now=0
  expect: net_night=106.8, available=180, be_nights=117.041199, be_occ=65.022888, be_adr=—, profit_now=-12500, safety=-65.022888
```
## How the break-even is calculated

The calculator finds what one occupied room night adds after its own costs, and then how many nights cover the fixed costs:

1. **Contribution per occupied night** = ADR × (1 − commission) + other revenue per night − cost per occupied night.
2. **Room nights available** = rooms × days open.
3. **Nights to sell** = fixed costs ÷ contribution per occupied night.
4. **Break-even occupancy** = nights to sell ÷ room nights available.
5. **Rate to break even** = (fixed costs ÷ nights sold today − other revenue + cost per night) ÷ (1 − commission).

With the starting numbers (example values, not benchmarks) a night at $135 less a 12% commission, plus $12 of extras, less $24 of cost, contributes $106.80. Fixed costs of $12,500 need 117.0 nights of the 180 available, so the break-even occupancy is 65.0%. At 68% the house earns $572 a month. That is a cushion of 3.0 percentage points, and the average rate could fall to $129.69 before the house loses money at today's occupancy.

## How to read the result

The cushion is the number to watch. A house that is 3 points above break-even loses money if a few bookings fall through. The table shows how the break-even occupancy and the profit move with the rate; compare what a change in the rate does with what the same change in occupancy would do on your numbers.

The second example is a house of 14 rooms at $95 with fixed costs of $24,000 and a 15% commission. Each occupied night contributes $68.75, so it needs 83.1% occupancy and sells 60%, and its rate would have to be $126.16 to break even at that occupancy. The third example has a rate of $60: each night contributes $33.80, and the occupancy needed is 205.5%. A figure above 100% means the rooms cannot cover the fixed costs at that rate, however full they are; the rate or the costs must change.

## Typical mistakes

- **Using the listed rate and forgetting the commission.** Platform and card fees reduce what each night brings in.
- **Treating cleaning as fixed.** Cleaning, laundry and breakfast ingredients rise with each night; keep them in the cost per night.
- **Leaving out the owner's time.** If you run the house and do not pay yourself, the profit is overstated.
- **Planning for full occupancy.** Rooms are never full all the time; the break-even should leave room below 100%.
- **Mixing high-season and low-season rates.** Use the average for the period you are testing.

## What this calculator cannot do

It treats the month as steady. It does not show how occupancy changes through the year, the build-up after opening, repairs, the property loan or the cash needed for the property. The financial model for a guest house builds occupancy by month with a June to August season and the opening ramp, adds yearly rate growth, repairs and the loan with the cash flow, runs Low / Base / High scenarios, and ends in lender-ready statements with a Checks sheet. For the revenue per room that goes with these figures, use the [ADR, occupancy and RevPAR calculator](/calculators/guest-house-adr-occupancy-revpar).

## FAQ {#faq}

### What goes into the fixed costs?

Costs that you pay even if no guest arrives: the mortgage or rent, insurance, utilities at a base level, software, and the staff you need to open. Costs that rise with each night go in the cost per occupied night.

### Is break-even occupancy the same as a target occupancy?

No. It is the floor. At that occupancy the house covers its costs and earns nothing, so set the target above it.

### Why does the result show a dash?

If a night brings in less than it costs, each night sold loses money, and no occupancy can cover the fixed costs, so the calculator shows a dash. The rate to break even also shows a dash when no nights are sold today.

### Should I include sales tax and lodging tax in the rate?

No. Those are collected for the authorities, so enter the rate before tax.
