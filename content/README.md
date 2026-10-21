# content/

Copy that the app renders. Code never hard-codes these texts.

- `landing.md` — landing meta, JSON-LD notes and placeholders (M03; layout from design v2).
- `email/` — transactional email copy (M07, rendered by `app/emails.py`).
- `legal/` — `privacy.md`, `terms.md`, `refunds.md` (Henry's texts; `/privacy`, `/terms`, `/refunds`).
- `seo/` — industry and guide pages (E16, rendered by `app/seo.py`).
- `calculators/` — one spec file per calculator (E34, ADR-014, rendered by `app/calculators.py`); format below.

- `business-models/` — one page per template, tables and charts computed from its sample (E35, `app/bizmodel.py`).

## SEO pages (`content/seo/*.md`)

Each file becomes a page at its `slug` with the shared layout: breadcrumbs, the Markdown body, a call to
action that opens the wizard on the page's template, the sample download, related pages, canonical/OG
tags and JSON-LD (Article for `/guides/…`, Product for `/models/…`). Pages are listed on `/models`,
`/guides`, in `sitemap.xml` and `llms.txt` automatically.

Front matter (one `key: value` per line; lists as `[a, b]`):

| key | required | meaning |
|---|---|---|
| `slug` | yes | `/models/<name>` or `/guides/<name>` |
| `title` | yes | `<title>`, ends with "\| StartupModel" |
| `description` | yes | meta description, 70–200 characters |
| `keyword` | yes | target keyword |
| `template` | no | template key (`cafe`, `saas`, …) or `any (sample: …)`; the CTA opens the wizard on it |
| `sample` | yes* | `key, tier, granularity, N years`, e.g. `cafe, light, monthly, 3 years` (*or inside `template: any (sample: …)`) |

Body: start with one `# H1`; `##`/`###` below it; `{#id}` at the end of a heading sets its anchor;
tables, lists, **bold**, *italic* and links work; raw HTML is not rendered. Link samples as
`/samples/<name>.xlsx` (name grammar in `engine/samples.py`, e.g. `cafe-full-5y`). After adding a page
that needs a new sample, run `python scripts/build_samples.py --seo` and commit the file.
`tests/test_seo.py` checks every page: one h1, heading order, title/description, canonical, JSON-LD,
every internal link and anchor resolves, the sample exists and is clean, prices match the config.

## Calculators (`content/calculators/<slug>.md`)

Each file becomes `/calculators/<slug>` (index `/calculators`, grouped by industry; listed in `sitemap.xml` and
`llms.txt`). The file name without `.md` is the slug. One page template and one evaluator serve every calculator:
no per-calculator code. Format: front matter, four fenced blocks anywhere in the body, then the Markdown explanation.
No YAML library is used; the blocks follow a strict YAML-like subset, and a spec that does not parse fails at
startup and in `tests/test_calculators.py`.

Front matter (`key: value` per line; lists as `[a, b]`):

| key | required | meaning |
|---|---|---|
| `slug` | yes | `/calculators/<file name>` |
| `title` | yes | `<title>`, ends with "\| StartupModel" |
| `description` | yes | meta description, 70-200 characters |
| `keyword` | yes | target keyword |
| `template` | no | template key (`cafe`, ...). Sets the promotion block's title, the wizard link (`/start?type=...`) and the default sample. Without it the block is generic and the wizard opens without a preset (cross-industry calculators) |
| `industry` | no | index group; default the template's title, else "General" |
| `related` | no | `[other-calculator-name, ...]` |
| `guide` | no | `/guides/...` SEO guide the calculator links to instead of repeating it |
| `sample` | no | `key, tier, granularity, N years`; default `<template>, full, monthly, 3 years`, shown when the file exists |

Blocks (an item starts with `- `; its other fields are indented lines `key: value`; `#` lines are comments):

- ```` ```inputs ```` (required): `key`, `label`, `default`, `min`, `max`, `step`, `format`; optional `unit` (`$` is a
  prefix, anything else a suffix; quote `"%"`) and `hint` (shown under the field, replaced by an error message).
  Values outside `min`..`max` are clamped; an empty field gives "—". Defaults are example values, never benchmarks.
- ```` ```outputs ```` (required, shown in this order, a `highlight: true` output leads, at most one): `key`, `label`,
  `formula`, `format`; optional `note`, `highlight`. Keys are `[a-z][a-z0-9_]*`, unique across inputs and outputs, not
  a function name. An output may use inputs and other outputs; cycles and unknown names are rejected.
- ```` ```table ```` (optional, one input swept over values): `title`, `input`, `outputs` (1-4 output keys) and either
  `values: 25, 28, 30` (absolute, inside the input's range) or `relative: -10, -5, 0, 5, 10` (percent change from the
  visitor's current value; the 0 row is highlighted).
- ```` ```examples ```` (required): `name`, `inputs: key=value, ...` (others default), `expect: key=value, ...` with `—`
  for "cannot be computed". Together the examples must expect every output, and at least one calculator shows a
  dash. Every example is checked in Python, in Node against `web/static/calc.js` and in Chromium on the page.

Formats: `int`, `number1`, `number2`, `money` ($1,235), `money2` ($1,234.50), `percent` (1 decimal; the value is in
percent points, 30 means 30.0%), `percent0`, `multiple` (3.46x). Negative numbers print with a minus sign; a value
that cannot be computed, or is 1e15 or larger, prints "—".

Formulas: numbers, input and output keys, `+ - * / ^` (also `× ÷ −`), parentheses, comparisons
`< <= > >= == !=` (1 or 0), `min(a, b, ...)`, `max(a, b, ...)`, `round(x)` / `round(x, digits)` (half away from
zero, 0-9 digits), `abs(x)` and `if(cond, a, b)` (only the chosen branch is evaluated). `-2^2` is -4 and `^` is right
associative. Division by zero, `0 ^ negative`, a negative base with a fractional exponent and overflow give "—",
which spreads through everything that uses the value; `x / max(y, 0)` is how a spec says "no answer unless y > 0".
The evaluators are hand-written parsers, `app/calc_expr.py` (Python) and `web/static/calc.js` (browser and Node),
and must agree to 1e-9 relative; change both together. Neither uses `eval`, `Function` or `ast`.

Body: starts with `# H1` and an intro; the calculator appears after the intro, before the first `##` heading, so the
body needs at least one `##` section. A `## FAQ` section whose `###` headings are questions becomes FAQPage JSON-LD.
Facts rule: no `[UPPER]` placeholders; every `$` or `%` figure in the body is one of the calculator's own numbers
(input default, example value, a result at the defaults or an example) or sits in a sentence with an external
`https://` link (`tests/test_calculators.py::test_copy_follows_the_facts_rule`). The promotion block
(`app/templates/_model_promo.html`, data from `app.calculators.promo_context`) takes prices from the config and lists
features per tier as `docs/WORKBOOK_STANDARD.md` section 1 sets them.

Tests: `tests/test_calculators.py` (specs, Python evaluator, Node parity, pages, sitemap/llms) and
`tests/test_browser_calculators.py` (Chromium: fill the inputs, read the results, no script errors, no layout shift).
The parity test needs `node`; locally it skips when node is missing, in CI (the `CI` variable) a missing node fails it.

## Business-model pages (`content/business-models/<template key>.md`)

`/business-models/<key>` explains how a kind of business makes money; the `/models/…` pages above sell the model.
Same front matter as SEO pages with `slug: /business-models/<key>`, `template: <key>`, `published` and
`modified` (YYYY-MM-DD, for the Article JSON-LD) and `sample: <key>, full, monthly, 5 years` (the committed `samples/<key>-full-5y.xlsx`). The body is Markdown plus
placeholders on the numbers, so copy cannot drift from the model; an unknown placeholder fails the build:

- `{{table:drivers}}`, `startup`, `pnl`, `costs`, `unit`, `breakeven` — a table on its own line;
- `{{chart:revenue_costs}}`, `cost_structure` — an inline SVG chart on its own line;
- `{{num:<table>.<row>[.<column>][|abs]}}` — one figure formatted as in the table, e.g. `{{num:pnl.rev.y1}}`,
  `{{num:startup.required}}`, `{{num:drivers.ticket.base}}`, `{{num:breakeven.first_ebitda}}` (`|abs` drops the
  brackets of a cost). Row and column keys: see `app/bizmodel.py`.

Rules (`tests/test_bizmodel.py`): 900–1,500 words; no `[UPPER]` placeholders except prices; a `$` or `%` figure typed
by hand needs an external source link in its sentence, otherwise use `{{num:…}}`; no invented statistics.

