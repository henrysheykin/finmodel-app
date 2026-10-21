---
slug: /calculators/real-estate-cap-rate
title: Cap Rate Calculator: Net Operating Income and Property Value | StartupModel
description: Enter the purchase price, rent, vacancy and operating costs. Get net operating income, the cap rate, the operating expense ratio and the value the income supports at a cap rate you choose.
keyword: cap rate calculator
template: real_estate
related: [real-estate-cash-on-cash-return, real-estate-dscr, real-estate-mortgage-payment]
---

# Cap rate calculator

The capitalization rate compares what a rental property earns before financing with what it costs to buy. It is net operating income divided by the price. Enter the rent, the vacancy and the operating costs; the calculator builds the net operating income step by step and shows the cap rate, and the value that income supports at a cap rate you choose.

```inputs
- key: price
  label: Purchase price
  unit: $
  default: 450000
  min: 0
  max: 1000000000
  step: 1000
  format: money
- key: rent
  label: Rent per month
  unit: $
  default: 3200
  min: 0
  max: 100000000
  step: 50
  format: money
  hint: Rent for the property at full occupancy.
- key: other_income
  label: Other income per month
  unit: $
  default: 150
  min: 0
  max: 100000000
  step: 10
  format: money
  hint: Parking, laundry, storage and similar income.
- key: vacancy
  label: Vacancy and unpaid rent
  unit: "%"
  default: 5
  min: 0
  max: 100
  step: 0.5
  format: percent
  hint: Your assumption for income lost to empty periods and bad debts.
- key: tax
  label: Property tax per year
  unit: $
  default: 4800
  min: 0
  max: 100000000
  step: 100
  format: money
- key: insurance
  label: Insurance per year
  unit: $
  default: 1400
  min: 0
  max: 100000000
  step: 100
  format: money
- key: maintenance
  label: Repairs and maintenance per year
  unit: $
  default: 2400
  min: 0
  max: 100000000
  step: 100
  format: money
- key: other_costs
  label: Other operating costs per year
  unit: $
  default: 600
  min: 0
  max: 100000000
  step: 100
  format: money
  hint: Utilities you pay, service charges, licences, accounting.
- key: mgmt
  label: Property management fee
  unit: "%"
  default: 8
  min: 0
  max: 100
  step: 0.5
  format: percent
  hint: A share of the rent you collect. Enter 0 if you manage it yourself, but value your time.
- key: market_cap
  label: Cap rate to value the property at
  unit: "%"
  default: 6.5
  min: 0.5
  max: 30
  step: 0.1
  format: percent
  hint: Your assumption for what a buyer would accept.
```

```outputs
- key: pgi
  label: Potential income per year
  formula: (rent + other_income) * 12
  format: money
- key: vac_loss
  label: Vacancy and unpaid rent
  formula: pgi * vacancy / 100
  format: money
- key: egi
  label: Income actually collected
  formula: pgi - vac_loss
  format: money
- key: opex
  label: Operating costs per year
  formula: tax + insurance + maintenance + other_costs + egi * mgmt / 100
  format: money
  note: Includes the management fee. Excludes mortgage payments and depreciation.
- key: noi
  label: Net operating income (NOI)
  formula: egi - opex
  format: money
- key: cap_rate
  label: Cap rate
  formula: noi / price * 100
  format: percent
  highlight: true
- key: opex_ratio
  label: Operating costs as a share of income
  formula: opex / egi * 100
  format: percent
- key: value
  label: Value at your chosen cap rate
  formula: max(noi, 0) / (market_cap / 100)
  format: money
```

```table
title: How vacancy changes the NOI and the value
input: vacancy
values: 0, 5, 8, 10, 15
outputs: noi, cap_rate, value
```

```examples
- name: The starting numbers
  inputs: price=450000, rent=3200, other_income=150, vacancy=5, tax=4800, insurance=1400, maintenance=2400, other_costs=600, mgmt=8, market_cap=6.5
  expect: pgi=40200, vac_loss=2010, egi=38190, opex=12255.2, noi=25934.8, cap_rate=5.763289, opex_ratio=32.090076, value=398996.923077
- name: A small flat managed by the owner
  inputs: price=210000, rent=1500, other_income=0, vacancy=4, tax=2100, insurance=800, maintenance=1500, other_costs=300, mgmt=0, market_cap=7
  expect: pgi=18000, vac_loss=720, egi=17280, opex=4700, noi=12580, cap_rate=5.990476, opex_ratio=27.199074, value=179714.285714
- name: A four-unit building
  inputs: price=980000, rent=7600, other_income=400, vacancy=7, tax=11200, insurance=3600, maintenance=7200, other_costs=2400, mgmt=9, market_cap=6
  expect: pgi=96000, vac_loss=6720, egi=89280, opex=32435.2, noi=56844.8, cap_rate=5.80049, opex_ratio=36.329749, value=947413.333333
- name: A price of zero has no cap rate
  inputs: price=0, rent=3200, other_income=150, vacancy=5, tax=4800, insurance=1400, maintenance=2400, other_costs=600, mgmt=8, market_cap=6.5
  expect: pgi=40200, vac_loss=2010, egi=38190, opex=12255.2, noi=25934.8, cap_rate=—, opex_ratio=32.090076, value=398996.923077
- name: Nothing collected has no cost ratio
  inputs: price=450000, rent=0, other_income=0, vacancy=5, tax=4800, insurance=1400, maintenance=2400, other_costs=600, mgmt=8, market_cap=6.5
  expect: pgi=0, vac_loss=0, egi=0, opex=9200, noi=-9200, cap_rate=-2.044444, opex_ratio=—, value=0
```

## How the cap rate is calculated

The cap rate is a property's net operating income divided by its price. The income is built in steps:

1. **Potential income** = (rent + other income) × 12.
2. **Income collected** = potential income − vacancy and unpaid rent.
3. **Operating costs** = property tax + insurance + repairs and maintenance + other operating costs + the management fee.
4. **Net operating income (NOI)** = income collected − operating costs.
5. **Cap rate** = NOI ÷ purchase price × 100.

Mortgage payments are not in the NOI. That is the point: the cap rate describes the property, not the way it is financed, so two buyers with different loans see the same figure.

With the starting numbers (example values, not benchmarks) the rent and other income come to $40,200 a year. After vacancy of 5% the income collected is $38,190, and the operating costs of $12,255, including the 8% management fee, leave an NOI of $25,935. On a price of $450,000 the cap rate is 5.8%. The operating costs are 32.1% of the income collected. At a cap rate of 6.5%, which is your own assumption of what a buyer would accept, the NOI supports a value of $398,997, which is below the purchase price.

## How to read the result

The cap rate answers the question: if I paid cash, what yearly return would the property's operations give me? A higher cap rate is a higher return on the price, and usually more risk or a weaker location. A lower one suggests buyers expect growth, security or both. Neither is good or bad on its own; compare the property with similar ones in its market, and compare the cap rate with your cost of borrowing.

The value line turns the relation round. A buyer who wants a given cap rate will pay at most the NOI divided by that rate. The sensitivity table shows how fragile this is: a few points of vacancy change the NOI, and the value, by a lot, because the NOI is divided by a small number.

The other examples show the range. A small flat managed by its owner, with no management fee, has an NOI of $12,580 on $210,000, a cap rate of 6.0%. A four-unit building has an NOI of $56,845 on $980,000, a cap rate of 5.8%.

## Typical mistakes

- **Using the asking rent, not collected rent.** Use the vacancy line to allow for empty periods and unpaid rent.
- **Leaving out costs you do not see.** Repairs, replacement of worn parts, management and the owner's time all cost money, even in a year when nothing breaks.
- **Including the mortgage.** Debt service and depreciation are not operating costs.
- **Using next year's hoped-for rent.** The cap rate is usually based on the income as it is.
- **Comparing cap rates across different markets without context.** The figure only means something relative to similar properties.

## What this calculator cannot do

It gives one year of one property, before financing and tax. It does not show the cash you put in, the effect of the loan, how rents and costs grow, what happens in a bad year, or the return from selling the property. A financial model for a rental property builds the pro forma month by month with the loan, the cash invested, taxes and a sale, runs Low / Base / High scenarios for rent and vacancy, and delivers lender-ready statements with a Checks sheet. The [cash-on-cash calculator](/calculators/real-estate-cash-on-cash-return) adds the loan, the [DSCR calculator](/calculators/real-estate-dscr) tests the lender's view, and the [mortgage payment calculator](/calculators/real-estate-mortgage-payment) shows the payment.

## FAQ {#faq}

### What is a good cap rate?

It depends on the market, the type of property and the interest rates of the day. Compare with similar properties near you and with what you pay to borrow, rather than with a single figure.

### Is NOI the same as profit?

No. NOI is before the mortgage, depreciation and income tax. Cash flow after the mortgage is shown in the cash-on-cash calculator.

### Should I include capital expenses?

Not in the NOI as shown here. Big replacements such as a roof are usually treated separately, but you should plan for them, for instance through the repairs line.

### Why does the cap rate show a dash?

If the purchase price is zero, the NOI cannot be divided by it.
