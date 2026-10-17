# content/

Copy that the app renders. Code never hard-codes these texts.

- `landing.md` — landing meta, JSON-LD notes and placeholders (M03; layout from design v2).
- `email/` — transactional email copy (M07, rendered by `app/emails.py`).
- `legal/` — `privacy.md`, `terms.md`, `refunds.md` (Henry's texts; `/privacy`, `/terms`, `/refunds`).
- `seo/` — industry and guide pages (E16, rendered by `app/seo.py`).

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
