# Workbook standard v1 (ADR-013)

The look, sheet set and report layout of **every** delivered workbook, all templates, both tiers. Agreed with
Henry on 2026-10-20 after two prototype rounds. Reference file: `design/workbook-standard-v1-prototype.xlsx`
(SaaS, Full, 5 years, monthly; built by `scripts/prototypes/standard_v1/` on top of a real engine workbook —
a visual reference only, not production code). Numbers never depend on presentation: tiers and this standard
change sheets and formatting, not a single calculated figure.

## 1. Sheet set (order = reader first)

| # | Sheet | Content | Light | Full |
|---|---|---|---|---|
| 1 | Cover | Model name, scope line, purpose (from the wizard goal), active scenario, checks verdict, date, contents with links, colour legend | ✓ | ✓ |
| 2 | Dashboard | Scenario switch (B4) + checks verdict; 6 KPI tiles; left: Core financials → industry metrics → Funding & valuation; right: 4 charts 2×2 | ✓ | ✓ |
| 3 | Summary | Income statement, cash flow, balance sheet: 5 years on the left + one year by month on the right ("Select detailed year"); one chart right of each monthly block | | ✓ |
| 4 | Scenarios | Key drivers Low/Base/High/Active; outputs Low/Base/High/Active (**live**); per-year tables; 4 charts 2×2 (revenue, EBITDA, net income, year-end cash) | | ✓ |
| 5 | Break-even | Funding need, break-even timing, annual break-even revenue; one large chart (revenue bars + break-even revenue line) | ✓ | ✓ |
| 6 | Valuation | Assumptions as links to Inputs (scenario-driven), free cash flow, DCF (perpetual growth + exit multiple), WACC × g sensitivity; no chart | | ✓ |
| 7 | Sources & Uses | Funding structure (+ doughnut), sources and uses of cash for the first N months (input), uses bar chart, balance check | | ✓ |
| 8 | KPIs | Financial ratios, DuPont, industry metrics; "Target" input column (left blank — never invented benchmarks); 4 charts 2×2 | | ✓ |
| — | Industry sheets | Only where the industry needs one (real estate: Returns — both tiers, ADR-011), after KPIs (Light: after Break-even) | ✓ | ✓ |
| 9 | Inputs | The single source of assumptions: sections, Low/Base/High, Active, Unit, Source/comment | ✓ | ✓ |
| 10–12 | P&L, Cash Flow, Balance Sheet | Annual statements (Light: P&L with the annual summary and the period detail, as today) | P&L | ✓ |
| 13–14 | Monthly (or Annual), Headcount | Calculation engine (template-specific) | | ✓ |
| 15 | Checks | Live integrity checks; overall verdict shown on Cover and Dashboard | ✓ | ✓ |

Sheet order, copied verbatim by the engine and every task:
- **Light:** Cover, Dashboard, Break-even, [industry sheets], Inputs, P&L, Checks.
- **Full:** Cover, Dashboard, Summary, Scenarios, Break-even, Valuation, Sources & Uses, KPIs, [industry sheets],
  Inputs, P&L, Cash Flow, Balance Sheet, Monthly (or Annual), Headcount, Checks.

"5 years" in this document means every year of the model's horizon (1, 3 or 5).

The wizard goal no longer adds or removes sheets (ADR-010 superseded in that part): every model has the sheets of
its tier. The goal sets the Cover's purpose line (e.g. "Investor-ready plan"). The Cover date is the build date,
written as a static value (not TODAY()).

## 2. Dashboard

- Target screen: 1920 px wide at 100% zoom (laptops scroll right — acceptable). One 68 px grid: column width 9;
  column A = 28.4 (three grid cells); G = 2 (gap); H:O and P:W = chart columns.
- Row 4: "Active scenario" + selector **B4** (the only input on the Dashboard; list 1/2/3 with an input message)
  + scenario name; "Model checks" verdict on the right with PASS/WARN/FAIL colours.
- Tiles (rows 6–8): six equal tiles of 272 px — Revenue Y_last (CAGR), EBITDA margin Y_last (EBITDA),
  Net income Y_last (net margin), Lowest cash balance (month), Funding required (covered / shortfall),
  Enterprise value (DCF average; Light: EBITDA break-even month instead).
- Left column, always in this order, from row 10:
  1. **Core financials ($'000)** — the same 13 lines for every business: revenue, gross profit, gross margin,
     operating expenses, EBITDA, EBITDA margin, net income, net margin, operating / investing / financing cash flow,
     net change in cash, year-end cash.
  2. **Industry metrics** — 3–5 lines chosen by the template (SaaS: customers, ARR, LTV ÷ CAC, team).
  3. **Funding & valuation** — equity raised, loan drawn, funding required, surplus / (shortfall), lowest cash
     (month), first month with positive EBITDA, payback, EV perpetual / exit multiple / average (Light: no EV rows).
- Right: four charts 2×2 — Revenue & EBITDA (+ EBITDA margin on the right axis), Cash flow by activity,
  Year-end cash (data labels), one industry chart chosen by the template (SaaS: ARR & customers).

## 3. Charts (all sheets)

- Native Excel charts referencing cells, so they stay live. Standard size **14.2 × 8.3 cm** (8 grid cells × 16 rows),
  laid out in two columns (left, right, then the next row) — never pinned to table rows.
  Exception: Break-even, one large chart 20 × 10.5 cm. Summary: one chart to the right of each monthly block.
- Arial; title 10 pt bold ink; axes and legend 8 pt grey; legend at the bottom; no chart border; light gridlines;
  category labels at the bottom even when values go negative; data labels with all flags but the value off
  (LibreOffice shows series/category names otherwise).
- Series colours in this order: pine `0F6E56`, sage `7FB5A3`, amber `D9A21B`, ink `1B2A2F`, grey `A3ABA8`;
  red `B8322A` only for losses / lost items.
- Every chart must survive the LibreOffice recalculation step (a test opens the delivered file and finds them).

## 4. Formatting

- Font Arial 9 everywhere; sheet title 14 pt bold ink `1B2A2F`; subtitle 9 pt grey; "◂ Contents" link in row 1 of
  every sheet. No brand, logo or footer credit in delivered files (D8).
- Section bands: pine fill, white bold. Column headers: bold ink with a medium ink bottom border.
- Totals: bold with a thin top border; key totals (net income, closing cash, total liabilities & equity, EV average)
  with a double underline. Percentages and margins: italic grey. Gridlines hidden.
- Tab colours: presentation sheets pine, Inputs amber `E0B43C`, statements ink, calculations grey, Checks red.
- Colour code:
  - **Input** = yellow fill `FFF2CC` + blue font `0000FF` (Inputs sheet, the Target column, the S&U months).
  - **View switch** (scenario B4, Summary's detailed year) = stronger yellow `FFE08A` with a frame.
  - **Formula** = black. **Active value** (Inputs column E) = grey fill.
  - **Link to another sheet** = green `008000` on Inputs, calculation sheets, Break-even, Valuation and
    industry sheets (they show scenario-driven assumptions); the report sheets (Cover, Dashboard, Summary,
    Scenarios, Sources & Uses, KPIs) use ink so they read as a report.
- Tab colour pine for every sheet before Inputs (incl. Break-even, Valuation, industry sheets).
- Units: the report sheets in $'000 (`$#,##0,;($#,##0,);"-"`, band titles say "($'000)"); Break-even, Valuation,
  industry sheets, statements and calculations in full dollars (`$#,##0;($#,##0);-`); percentages `0.0%;(0.0%);-`; multiples `0.0"x"`;
  tiles in millions (`$#,##0.0,,"M"`).
- Print: landscape (Cover portrait), fit to one page wide; footer = sheet name + "Page n of N".
- Functions: Excel-2007 set only (CLAUDE.md). Hyperlinks via `HYPERLINK("#'Sheet'!A1", …)`.

## 5. What stays as it is

Inputs remains the only place assumptions live (Valuation and Break-even show them as links, because they follow the
scenario). The only input cells elsewhere are view settings that change no figure outside their own sheet: the scenario
selector (Dashboard!B4), Summary's detailed year, the Sources & Uses period length and the KPIs Target column. Calculation sheets keep their layout (period columns from C, year row, same formula across periods).
Every presentation cell is a link or a simple formula over statements / grid lines — no new financial logic
outside the challenger's reach; new logic (Scenarios' parallel chains, Sources & Uses, ratios) is recomputed by
the challenger.
