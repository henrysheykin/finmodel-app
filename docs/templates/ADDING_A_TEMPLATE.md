# Adding an industry template

A new industry is **one new file** in `engine/templates/` plus its tests, sample and memo. Nothing else
in the app lists industries by hand: the registry discovers the template, and the wizard, the brief
schema, the landing page ("Available now", samples), `llms.txt` and the order pipeline all read it from
there (ADR-009).

## 1. The template file — `engine/templates/<key>.py`

```python
class FitnessTemplate(Template):
    key = "fitness"  # template id, also the sample file name
    title = "Fitness studio / gym"  # shown in the wizard and on the landing page
    business_types = ("fitness",)  # wizard business-type ids this template serves
    order = 60  # position in the wizard list (10, 20, … by convention)
    key_numbers = ("members_start", "price_m", "churn_m", "rent", "capex", "equity")  # wizard step 5
    sample_title = "Fitness studio"  # landing "Open a sample" row (omit to hide)
    sample_desc = "Full workbook with members, churn, class revenue and rent"

    def driver_specs(self): ...  # template drivers (standard + headcount are added)
    def revenue_lines(self, t): ...  # must define `rev` and `cogs`
    def opex_lines(self, t): ...
    def capex_lines(self, t): ...
    def reference_top(self, d, p, y, t, hc): ...  # plain-Python twin used by the challenger
    def default_brief(self, stage): ...  # stage defaults: planning / early / growing / established
```

Optional economics (ADR-011): `loan_style = "annuity"` for a level-payment mortgage (default `"straight"`);
a `capex_land` line inside `capex` (with `Top.land` in the twin) keeps land out of depreciation;
`returns = True` adds the property Returns sheet (needs the drivers in `engine/returns.py`
`REQUIRED_DRIVERS` and a `capex_buy` line) — see `engine/templates/real_estate.py`.

Rules that do not change (CLAUDE.md): Excel-2007 functions only, every assumption in its own labelled
cell, guarded denominators, zero formula errors, challenger within $1 in every scenario-year.

If the business type was announced as "coming soon", remove it from `PLANNED` in
`engine/templates/__init__.py` in the same PR (the registry also hides a planned entry automatically as
soon as a template serves it).

Tier modules (Break-even, Valuation) need nothing from the template: they read the standard grid lines, and
`tests/test_goals.py` runs the investor pitch for every registered template.

The Dashboard (ADR-013, `engine/dashboard.py`) needs two optional hooks so the industry block and the fourth chart
fit the business: `dashboard_metrics(t)` returns 2–4 `DashMetric(key, label, src, fmt)` lines (`src` = `"kpi:<row key>"`
of your `kpi_rows`, or a period-grid line key rolled up by `agg`; the builder adds the team line itself) and
`dashboard_chart(t)` returns a `DashChart(title, bars=<metric keys>, lines=<metric keys on the right axis>)`. The block
band uses `kpi_title`. Without them the Dashboard shows no industry lines and charts gross profit and margin
(`tests/test_dashboard.py` expects every registered template to define both).

## 2. Tests — `tests/test_<key>.py`

Copy the structure of `tests/test_services.py`: the tier × granularity × horizon matrix through
LibreOffice + challenger, the four stage defaults, monthly = annual, and template-specific checks.
`tests/test_catalog.py` already covers registration, wizard key numbers and the landing for every
template automatically.

## 3. Sample and memo

```bash
python scripts/build_samples.py <key>         # writes samples/<key>-full.xlsx (Full, 3 years, monthly)
                                              # and samples/<key>-full-5y.xlsx (Full, 5 years, monthly)
```

Commit both files. `<key>-full-5y.xlsx` is the sample the template's business-model page (section 4) computes its
tables from and offers for download; `tests/test_bizmodel.py` compares every table cell of every registered template
with the rebuilt workbook and with this committed file.

Write `docs/templates/<key>.md` (assumption memo with questions for the CFO at the end) and add the
"CFO review" line to `docs/HUMAN_TODO.md` R1.

## 4. Optional

- An SEO page in `content/seo/` (M track) once the CFO has signed off the template. Front matter and
  samples: `content/README.md`; `python scripts/build_samples.py --seo` builds any sample a page offers.
- A business-model page `content/business-models/<key>.md` (`/business-models/<key>`, E35, ADR-014) and calculator
  pages (`content/calculators/`, E34) **may go live before the CFO sign-off** (ADR-014 supersedes the line above for
  these two page types): they explain the business and carry the line "Illustrative Base case of the sample model;
  your model uses your numbers". Only the `/models/...` SEO pages, which sell the model, wait for the sign-off.
  The page is Markdown with `{{table:<name>}}`, `{{chart:<name>}}` and `{{num:<table>.<row>[.<column>]}}`
  placeholders, so every figure comes from the sample (`app/bizmodel.py`); an unknown placeholder fails the build.
  Front matter: `slug: /business-models/<key>`, `title`, `description`, `keyword`, `template: <key>`,
  `sample: <key>, full, monthly, 5 years`. Copy rules are enforced by `tests/test_bizmodel.py`: 900 to 1,500 words,
  no `[UPPER]` placeholders except prices, and any `$` or `%` figure written by hand needs a source link in its sentence.
- Announce a future industry early: add it to `PLANNED` and it appears in the wizard as
  "(coming soon)" without a template.
