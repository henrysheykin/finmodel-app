# Landing page copy — StartupModel (EN)

> **Update 2026-10-16 (ADR-005):** the landing moved to design v2 (`design/landing.dc.html`),
> which has different sections (no Problem quotes, no "VS" cards; adds a Checks section,
> a sheet table and a comparison table) and already carries this file's messaging, brand
> and prices. For page copy, the design wins. This file still owns Meta, the SEO/JSON-LD
> notes, llms.txt/robots notes and the placeholders below.

Source of structure: `design/landing.dc.html` (same sections, same order, similar lengths).
Decisions used: ADR-002 (brand StartupModel, domain startup-model.com, Light $149, Full $349,
5-Full pack $1,250, refund within 7 days,
FinModelsLab never mentioned). Positioning: `docs/marketing/positioning.md`.
Placeholders in `[CAPS]` must stay until Henry decides; see "Notes for E13" at the end.

---

## Meta

- **title:** Custom Excel Financial Model, Checked | StartupModel
- **description:** Answer a short questionnaire and get an Excel financial model built on your numbers: live formulas, low/base/high scenarios and a check report. From $149.
- **og:title:** Your business plan as a working Excel model
- **og:description:** Built on your numbers. Live formulas, three scenarios, every figure recomputed before delivery. One payment, from $149.
- **canonical:** https://startup-model.com/

---

## Nav

- Links: How it works · What's inside · Pricing · FAQ
- Button: Start my model

---

## Hero

**H1:** Your business plan as a working Excel model, built on your numbers

**Subhead:** Answer a short questionnaire and download an editable spreadsheet with live formulas, three scenarios and a check report. For startups, cafés and restaurants, shops, rental property and service firms.

**CTA:** Build my model

**Tag line under CTA:** Startup forecasts · Café and restaurant plans · Retail · Rental property · DCF valuation

**Mockup labels:** `bakery-cafe-plan.xlsx — Excel` · "Live preview — switch scenario & tabs" · Scenario: Low / Base / High · Tabs: Dashboard / Inputs / P&L / Checks ✓

---

## Problem

**H2:** Projections shouldn't eat your month

**Lead:** Every usual route to a financial model has a catch.

1. **"My spreadsheet still breaks after three weekends."**
   Starting from a blank sheet means days of setup, broken links and numbers you can't defend.
2. **"The consultant's quote cost more than my launch budget."**
   Hiring an analyst is the safe option, but rarely an affordable one for a new business.
3. **"I still have to rebuild someone else's file around my business."**
   A ready-made file is a starting point. Making it describe your numbers is still your job.

---

## How it works

**H2:** How it works

**Lead:** Three steps from questions to a spreadsheet you can present.

1. **Tell us about the business**
   A guided form asks about your business, your goal and a few key numbers in plain language. Sensible defaults fill the gaps, and a sample-data switch lets you explore before sharing real figures.
2. **We build it and check it**
   AI turns your answers into a structured brief. Tested templates write every formula. Then an independent check recomputes each scenario and year outside Excel, and the file is only released if it matches.
3. **Download, adjust, present**
   You get an .xlsx with live formulas, a low / base / high scenario switch and a check report. Change any input and the whole file follows.

**Pipeline labels (diagram):** Brief — *maps your answers* → Builder — *writes the formulas* → Checker — *recomputes every number*

**Form mockup:** "Set up your model" · "Step 1 of [N] — About your business" · Business type · Continue →

**File card:** `bakery-cafe-plan.xlsx` · "5 sheets · 3 scenarios · check report included" · Dashboard · Inputs · P&L · Checks

---

## What's inside

**H2:** What every model includes

**Lead:** Built around your inputs, not adapted from someone else's file.

1. **Three scenarios, one switch**
   Low, base and high cases live in the same file. Change one cell and every sheet recalculates.
2. **Formulas you can read**
   No pasted values. Inputs are blue, calculations are black, links between sheets are green, so anyone can trace a number to its source.
3. **Checked before delivery** — *badge: Our main difference*
   Every scenario-year is recomputed independently and must match the workbook to the dollar. The Checks sheet travels with the file, so your banker or investor can see it too.
4. **Ready in [DELIVERY_TIME]**
   The file is built after you finish the questions, not days after a kickoff call.

---

## Samples

**H2:** Open a real sample

**Lead:** Download a generated file and inspect every formula before you buy.

1. **Bakery-café plan** — tags: 5 sheets · 3 scenarios · Checked
   Three-year forecast with guest and ticket drivers, cost structure and the scenario switch.
2. **Rental property deal** — tags: Multi-sheet · 3 scenarios · Checked — *[SHOW ONLY AFTER E05 SHIPS THE SAMPLE]*
   Cash flow, cap rate, IRR and debt coverage for a buy-to-let purchase, with all three cases.

---

## Comparison

**H2:** Compared with the alternatives

**Lead:** What you'd otherwise reach for, and what you get here instead.

1. **VS Ready-made templates**
   A good shortcut if your business matches the file. If it doesn't, expect **long evenings rewiring formulas**.
   → StartupModel starts from your answers and your numbers, so the structure already fits.
2. **VS AI spreadsheet assistants**
   Fast at drafting, but **you still have to check every formula yourself**.
   → Here the arithmetic is recomputed independently before the file reaches you.
3. **VS Freelance analysts**
   Solid work when budget allows, but **usually priced in the hundreds or thousands and delivered in days or weeks**.
   → A custom, checked model from $149, delivered in [DELIVERY_TIME].

**Footer line:** Pay once and keep the file.

---

## Who it's for

**H2:** Made for people without a finance team

**Lead:** You bring the business knowledge. We handle the workbook.

1. **Founders raising money**
   Turn assumptions into a forecast you can drop into a deck and defend in a meeting.
2. **Cafés, shops and local services**
   Plan an opening, a loan or a second location with clear numbers for the bank or landlord.
3. **Accountants and advisers**
   Start each client forecast from a clean, checked structure, then refine it. Five-model packs available.

---

## Pricing

**H2:** Simple pricing

**Lead:** One payment per model. No subscription.

**Card 1 — Light — $149**
Single-sheet P&L with inputs and checks. Monthly or annual, 1, 3 or 5 years.

**Card 2 — Full — $349**
Full workbook: dashboard, inputs, monthly detail, P&L, cash flow, balance sheet, headcount and checks.

**Included in both:**
- ✓ Editable Excel workbook
- ✓ Low / base / high scenarios
- ✓ Live formulas throughout
- ✓ Check report included
- ✓ Download link by email
- ✓ Refund within 7 days

**Upgrade line:** Started with Light? Upgrade to Full by paying the difference.

**Pack line:** For accountants and advisers: 5 Full models for $1,250.

**CTA:** Build my model — from $149

**Under CTA:** Yours to keep after one payment.

*(The design's optional price-anchor line is left out: there is no sourced figure we want on the page yet.)*

---

## FAQ

**H2:** Questions, answered

**Lead:** The short version of what people ask before ordering.

1. **What does a model cost?**
   $149 for Light, a single-sheet P&L, and $349 for Full, a complete workbook with dashboard, cash flow and balance sheet. One payment, no subscription.
2. **Is the output a real Excel file?**
   Yes. A standard .xlsx with working formulas across sheets, not a chat answer or a screenshot.
3. **How do you know the numbers are right?**
   Before release, every scenario and year is recomputed outside Excel and must match the workbook to the dollar. The file also carries a Checks sheet. A model that fails is never sent.
4. **Do I need a finance background?**
   No. Questions are in plain language, and you can start from sample data and edit later.
5. **Can I open it in Google Sheets?**
   It is built for Microsoft Excel and uses only long-established functions. [VERIFY BEFORE LAUNCH: open a sample in Google Sheets and Numbers; keep only what passes.]
6. **What if it doesn't fit my business?**
   Write to us within 7 days and we refund the full amount.

**CTA:** Build my model — from $149

---

## Footer

- Links: Modeling guide · Café model · Privacy · Terms · Refund policy
- © 2026 StartupModel

---

## Notes for E13 (not page copy)

**Placeholders**

| Placeholder | Meaning | Owner |
|---|---|---|
| `[DELIVERY_TIME]` | Promised time from payment to email | E track: set after E09/E12 measure real end-to-end time |
| `[N]` in "Step 1 of [N]" | Number of wizard steps | E10 |

**Claims changed from the design file, and why**
- "Three AI agents assemble it" and "an independent reviewer agent" were removed. Under the core idea (CLAUDE.md), the LLM only fills the brief, deterministic templates build the workbook, and the challenger is plain Python, not an AI agent. The copy now says exactly that.
- "Ready today" and "same-day" became `[DELIVERY_TIME]`. No delivery time has been measured yet.
- "Works in Excel, Google Sheets and Numbers" became a `[VERIFY]` note. Compatibility has not been tested.
- "General chatbots hand back text" became "AI spreadsheet assistants": those tools now return workbooks (see `docs/marketing/competitors.md`).
- Templates are not run down. The copy says what we add, per the guardrail in positioning.md.
- The rental property sample shows only once E05 exists.
- The Checks rows in the hero mockup must match the real Checks sheet the engine writes. Do not show checks the engine doesn't run.

**SEO/structured data (for E13)**
- One H1 (the hero). The H2s follow the sections above.
- JSON-LD: `Organization` (name StartupModel, url https://startup-model.com/), a `Product` with two `Offer`s (Light 149 USD, Full 349 USD), and `FAQPage` from the six FAQ items, using the same wording as the page.
- Keep the copy in server-rendered HTML, not injected by JS, so crawlers read it.
- robots.txt should allow the AI crawlers (GPTBot, ClaudeBot, PerplexityBot). Add a short `llms.txt` with these facts only: what it is, the tiers and prices, what's in the file, and a contact `[SUPPORT_EMAIL]`.
- Never mention FinModelsLab (ADR-002).
