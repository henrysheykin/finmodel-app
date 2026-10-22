---
slug: /calculators/pet-boarding-occupancy-revenue
title: Pet Boarding Occupancy and Revenue Calculator: RevPAN | StartupModel
description: Enter kennels, occupancy, nightly rate and add-on income. Get boarding revenue per month, revenue per available night, stays per month and the occupancy needed to cover the fixed costs.
keyword: pet boarding revenue calculator
template: pet_care
related: [pet-grooming-price-per-dog]
---

# Pet boarding occupancy and revenue calculator

A boarding kennel sells nights, and a night that is not sold is gone for good. The numbers that matter are the share of nights sold, the rate for each night, and what each available night earns whether it is sold or not. Enter your kennels, occupancy and rates; the calculator shows the revenue and the occupancy you need to cover the fixed costs.

```inputs
- key: kennels
  label: Kennels or suites
  default: 30
  min: 1
  max: 10000
  step: 1
  format: int
- key: occupancy
  label: Occupancy
  unit: "%"
  default: 70
  min: 0
  max: 100
  step: 1
  format: percent
  hint: Nights sold as a share of nights available. Your assumption.
- key: rate
  label: Rate per night
  unit: $
  default: 48
  min: 0
  max: 10000
  step: 1
  format: money
  hint: The average price of a night before add-ons.
- key: addon
  label: Add-on income per night sold
  unit: $
  default: 6
  min: 0
  max: 10000
  step: 0.5
  format: money2
  hint: Playtime, medication, special food and webcams, averaged over the nights sold.
- key: days
  label: Days open per month
  unit: days
  default: 30
  min: 1
  max: 31
  step: 1
  format: int
- key: stay
  label: Average stay
  unit: nights
  default: 3.5
  min: 1
  max: 60
  step: 0.5
  format: number1
- key: var_night
  label: Variable cost per night sold
  unit: $
  default: 7
  min: 0
  max: 1000
  step: 0.5
  format: money2
  hint: Food, cleaning supplies, laundry and utilities that rise with each night.
- key: fixed
  label: Fixed costs of boarding per month
  unit: $
  default: 14000
  min: 0
  max: 100000000
  step: 250
  format: money
  hint: Staff you need to open, rent, insurance, software and loan payments for the boarding side.
```

```outputs
- key: available
  label: Nights available per month
  formula: kennels * days
  format: int
- key: sold
  label: Nights sold per month
  formula: available * occupancy / 100
  format: number1
- key: revenue
  label: Boarding revenue per month
  formula: sold * (rate + addon)
  format: money
- key: revpan
  label: Revenue per available night
  formula: revenue / available
  format: money2
  highlight: true
  note: Occupancy times the rate and add-ons; what each kennel earns per night open.
- key: stays
  label: Stays per month
  formula: sold / stay
  format: number1
- key: profit
  label: Profit per month from boarding
  formula: sold * (rate + addon - var_night) - fixed
  format: money
- key: be_occ
  label: Occupancy needed to break even
  formula: fixed / (available * max(rate + addon - var_night, 0)) * 100
  format: percent
  note: Above 100% means the kennels cannot cover the fixed costs at this rate.
```

```table
title: What occupancy does to boarding
input: occupancy
values: 50, 60, 70, 80, 90
outputs: revenue, revpan, profit
```

```examples
- name: The starting numbers
  inputs: kennels=30, occupancy=70, rate=48, addon=6, days=30, stay=3.5, var_night=7, fixed=14000
  expect: available=900, sold=630, revenue=34020, revpan=37.8, stays=180, profit=15610, be_occ=33.096927
- name: A small kennel with a premium rate
  inputs: kennels=12, occupancy=65, rate=75, addon=10, days=30, stay=4, var_night=9, fixed=9000
  expect: available=360, sold=234, revenue=19890, revpan=55.25, stays=58.5, profit=8784, be_occ=32.894737
- name: A large kennel with a low rate
  inputs: kennels=80, occupancy=55, rate=35, addon=3, days=30, stay=5, var_night=6, fixed=26000
  expect: available=2400, sold=1320, revenue=50160, revpan=20.9, stays=264, profit=16240, be_occ=33.854167
- name: Costs per night above the price
  inputs: kennels=30, occupancy=70, rate=5, addon=1, days=30, stay=3.5, var_night=7, fixed=14000
  expect: available=900, sold=630, revenue=3780, revpan=4.2, stays=180, profit=-14630, be_occ=—
```

## How boarding revenue is calculated

A kennel's capacity is its number of kennels times the days it is open. What it sells is a share of that capacity, and each night sold earns a rate and add-ons:

1. **Nights available** = kennels × days open.
2. **Nights sold** = nights available × occupancy.
3. **Boarding revenue** = nights sold × (rate per night + add-ons per night).
4. **Revenue per available night** = boarding revenue ÷ nights available.
5. **Stays** = nights sold ÷ average stay.

Revenue per available night, often called RevPAN, is the number the kennel can compare over time and with others. It combines the two things that matter, how often the kennels are full and what a full night earns, in one figure. It is the same idea as revenue per available room in a hotel.

With the starting numbers (example values, not benchmarks) 30 kennels open for 30 days have 900 nights available. At 70% occupancy 630.0 nights are sold, at $48 plus $6 of add-ons. Revenue is $34,020 a month, and RevPAN is $37.80. With an average stay of 3.5 nights, that is 180.0 stays a month. After $7 of variable cost a night and $14,000 of fixed costs, the profit is $15,610, and the kennel breaks even at an occupancy of 33.1%.

## How to read the result

Occupancy and rate trade off against each other. Cutting the rate may fill more nights, but if it does not fill them enough RevPAN falls. The table shows revenue, RevPAN and profit at several occupancy levels; compare what a rise in occupancy is worth with what a rise in the rate would earn.

The break-even occupancy shows the margin for error. The example kennel needs a third of its nights sold to cover the costs, and it sells 70%, so there is room. A kennel with a large share of fixed costs, or a low rate, has less. In the third example a large kennel with 80 kennels, a rate of $35 and $26,000 of fixed costs breaks even at 33.9% and sells 55%; its RevPAN is $20.90, against $55.25 for a small kennel with a premium rate of $75 and add-ons of $10.

Boarding is seasonal. Holidays fill the kennels and the weeks between them may be empty. The calculator uses one average, so run it for a busy and a quiet month and see both.

## Typical mistakes

- **Counting the booked nights, not the nights stayed.** Cancellations and early pickups leave empty nights.
- **Using the peak rate for every night.** Holiday rates apply to some nights only; use the average.
- **Ignoring the nights the kennels cannot be sold.** Cleaning days, maintenance and isolation of a sick animal reduce the nights available.
- **Treating staff as variable.** You need a minimum team to open, however few dogs stay.
- **Forgetting the cost of vaccinations and checks.** If you pay for them, they belong in the variable cost.

## What this calculator cannot do

It shows one steady month of boarding. It does not show the seasons, the build-up in the first months, the staffing steps as the kennel fills, or the cash needed to build or fit out the space. A financial model for a pet care business combines boarding, grooming and retail in a monthly forecast with cash and the opening costs, runs Low / Base / High scenarios for occupancy and rate, and ends in lender-ready statements with a Checks sheet. For the grooming side, use the [grooming price calculator](/calculators/pet-grooming-price-per-dog).

## FAQ {#faq}

### What is RevPAN?

Revenue per available night: the boarding revenue divided by all nights the kennels could have been sold. It is the occupancy times the revenue of a night sold.

### What is a good occupancy?

It depends on your costs and your market. The break-even occupancy shows the level you need; leave a margin above it for the quiet weeks.

### Are add-ons included in the rate?

They are separate. Enter an average add-on income per night sold, and the revenue includes it.

### Why does the break-even show a dash?

If the rate and add-ons are not above the variable cost of a night, each night sold adds nothing, and no occupancy covers the fixed costs.
