---
slug: /calculators/guest-house-adr-occupancy-revpar
title: ADR, Occupancy and RevPAR Calculator for Guest Houses | StartupModel
description: Enter rooms, occupancy and average daily rate. Get room nights sold, room revenue, RevPAR and total revenue per available room, plus the rate or occupancy a monthly room revenue target needs.
keyword: ADR occupancy RevPAR calculator
template: guest_house
related: [guest-house-break-even-occupancy]
---

# ADR, occupancy and RevPAR calculator

Three numbers describe how a guest house is doing: how many room nights it sells (occupancy), what it earns for each one (average daily rate, or ADR), and the revenue per room it could have sold (RevPAR). RevPAR is occupancy times ADR, which makes it the one figure that moves when either one moves. Enter your rooms and rates; the calculator shows all three and what a revenue target would need.

```inputs
- key: rooms
  label: Rooms for guests
  default: 6
  min: 1
  max: 1000
  step: 1
  format: int
- key: occupancy
  label: Occupancy
  unit: "%"
  default: 68
  min: 0
  max: 100
  step: 1
  format: percent
  hint: Room nights sold as a share of room nights available. Your assumption.
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
  hint: Breakfast, drinks, late checkout and other extras, averaged over the nights sold.
- key: days
  label: Days open per month
  unit: days
  default: 30
  min: 1
  max: 31
  step: 1
  format: int
- key: target
  label: Room revenue you want per month
  unit: $
  default: 17000
  min: 0
  max: 100000000
  step: 500
  format: money
```

```outputs
- key: available
  label: Room nights available per month
  formula: rooms * days
  format: int
- key: sold
  label: Room nights sold per month
  formula: available * occupancy / 100
  format: number1
- key: room_rev
  label: Room revenue per month
  formula: sold * adr
  format: money
- key: revpar
  label: RevPAR
  formula: room_rev / available
  format: money2
  highlight: true
  note: Room revenue per room night available; occupancy times ADR.
- key: total_rev
  label: Total revenue per month, with extras
  formula: room_rev + sold * extras
  format: money
- key: trevpar
  label: Total revenue per available room night
  formula: total_rev / available
  format: money2
- key: adr_needed
  label: ADR for the room revenue target at this occupancy
  formula: target / sold
  format: money2
- key: occ_needed
  label: Occupancy for the target at this ADR
  formula: target / (available * adr) * 100
  format: percent
  note: Above 100% means the target cannot be reached at this rate.
```

```table
title: What occupancy does to room revenue
input: occupancy
values: 50, 60, 68, 75, 85
outputs: sold, room_rev, revpar
```

```examples
- name: The starting numbers
  inputs: rooms=6, occupancy=68, adr=135, extras=12, days=30, target=17000
  expect: available=180, sold=122.4, room_rev=16524, revpar=91.8, total_rev=17992.8, trevpar=99.96, adr_needed=138.888889, occ_needed=69.958848
- name: A larger house with a lower rate
  inputs: rooms=14, occupancy=60, adr=95, extras=8, days=30, target=30000
  expect: available=420, sold=252, room_rev=23940, revpar=57, total_rev=25956, trevpar=61.8, adr_needed=119.047619, occ_needed=75.18797
- name: A boutique house with a high rate
  inputs: rooms=4, occupancy=55, adr=220, extras=25, days=30, target=18000
  expect: available=120, sold=66, room_rev=14520, revpar=121, total_rev=16170, trevpar=134.75, adr_needed=272.727273, occ_needed=68.181818
- name: No rooms sold gives no rate
  inputs: rooms=6, occupancy=0, adr=135, extras=12, days=30, target=17000
  expect: available=180, sold=0, room_rev=0, revpar=0, total_rev=0, trevpar=0, adr_needed=—, occ_needed=69.958848
```
## How the numbers are calculated

A guest house sells room nights. The calculator starts from what it could sell and works down to revenue:

1. **Room nights available** = rooms × days open.
2. **Room nights sold** = room nights available × occupancy.
3. **Room revenue** = room nights sold × average daily rate (ADR).
4. **RevPAR** = room revenue ÷ room nights available. It also equals occupancy × ADR.
5. **Total revenue** = room revenue + room nights sold × other revenue per night.

With the starting numbers (example values, not benchmarks) 6 rooms open for 30 days have 180 room nights available. At 68% occupancy 122.4 are sold at $135, so room revenue is $16,524 and RevPAR is $91.80. With $12 of extras per night sold, total revenue is $17,993, or $99.96 for each room night available.

The target lines reverse the calculation. To earn $17,000 a month from rooms at 68% occupancy, the average rate must be $138.89. At a rate of $135, the occupancy must be 70.0%.

## How to read the result

ADR tells you what a night sold earns, occupancy tells you how many nights sell, and RevPAR combines the two. A house can raise ADR and lose nights, or fill every night at a low rate. RevPAR shows whether the trade was worth it: if it rises, you earned more per room you could have sold.

The second example is a house of 14 rooms at a rate of $95 and 60% occupancy. It sells 252 room nights and earns $23,940 from rooms, but its RevPAR is $57.00. The third is a boutique house of 4 rooms at $220 and 55% occupancy, whose RevPAR is $121.00 even though it is emptier. Comparing the two with revenue alone would mislead; comparing per room does not. For a target of $30,000 the larger house would need 75.2% occupancy at its rate, and the boutique house would need an ADR of $272.73 at its occupancy to reach $18,000.

## Typical mistakes

- **Dividing revenue by the wrong nights.** ADR divides by nights sold; RevPAR divides by nights available.
- **Counting free or owner nights as sold.** They are available but earn nothing, so they lower occupancy.
- **Including taxes in the rate.** Sales tax and lodging tax are collected for the authorities; leave them out.
- **Mixing extras into ADR.** Keep breakfast and other extras on their own line, as here, so rates can be compared.
- **Using one busy month for the year.** Occupancy changes with the season; run the calculator for a busy and a quiet month.

## What this calculator cannot do

It shows revenue only. It does not subtract the commission paid to booking platforms, the cleaning and laundry, or the fixed costs, and it does not show the seasons, the first months after opening, or cash. A financial model for a guest house builds occupancy and rate by month, adds the costs, the financing and the cash flow, runs Low / Base / High scenarios, and ends in lender-ready statements with a Checks sheet. To see how full the rooms must be to cover your costs, use the [break-even occupancy calculator](/calculators/guest-house-break-even-occupancy).

## FAQ {#faq}

### What is the difference between ADR and RevPAR?

ADR is the room revenue divided by the room nights sold. RevPAR is the room revenue divided by the room nights available. RevPAR is lower unless every room is full, because it counts the empty nights.

### Should breakfast be part of the rate?

If breakfast is included in the price the guest pays, you can keep it in the rate. If you sell it separately, enter it as other revenue per night, as the calculator does.

### Does occupancy count booked nights or stayed nights?

Stayed nights. A booking that is cancelled or a guest who leaves early leaves a night that is available and not sold.

### Why does the required rate show a dash?

If no room nights are sold, there is nothing to spread the target over, so the rate needed is undefined and the calculator shows a dash.
