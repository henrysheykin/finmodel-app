# Henry's queue

Things only Henry can do. Agents add items here; Henry ticks them and writes
the answer next to the item (agents read this file every run).

## Decisions
- [x] D1 Name + domain — **startup-model.com, brand StartupModel** (Henry gave 6 domains,
      agent picked; ADR-002). Still for Henry: TMview / USPTO check for "StartupModel" (classes
      9, 35, 36, 42); optionally buy startupmodel.com as a redirect.
      "Startup Models" (startupmodels.co) — Henry 2026-10-16: site not active, not a concern.
- [x] D2 Payment provider — Henry 2026-10-16: **Stripe** (ADR-004). Consequence: VAT / sales
      tax is yours (e.g. Stripe Tax and/or EU VAT OSS registration in Spain) — confirm with
      your tax adviser before go-live.
- [x] D3 Price — Henry 2026-10-16: **Light $149, Full $349, pack 5 × Full $1,250**, Light->Full
      upgrade = pay the difference. **Refund window: 7 days.**
- [x] D5 FinModelsLab vs StartupModel — Henry 2026-10-16: **separate brands**. No links,
      copy or upgrade credit between them (ADR-002).
- [x] D4 Hosting — Henry 2026-10-16: "Vercel/Railway" → **Railway** for app + worker + Postgres
      (ADR-004). Vercel is not used: it runs serverless functions, not our Docker image with
      LibreOffice and a long-running worker.
- [x] D6 SEO volumes — Henry 2026-10-16: no volume data will be provided; work qualitatively.
      (was: (from M04, `docs/marketing/seo-plan.md`): the Ahrefs connector returned
      "Insufficient plan", so no keyword volumes were measured. Either upgrade the Ahrefs API plan,
      or export volumes from Google Keyword Planner (your Google Ads account) for the keywords in
      seo-plan.md, then drop the CSV into `docs/marketing/`.)
- [x] D7 Brand risk — Henry 2026-10-16: no brand risk, keep StartupModel.
      (was: (from M04): **startupmodels.io** ranks for "SaaS financial model" with a name
      nearly identical to StartupModel (different from the inactive startupmodels.co). Check
      whether it is active and holds a mark; decide keep / adjust the brand.)

- [x] D8 Accountant pack details — Henry 2026-10-16: **credits valid 12 months; delivered files carry no StartupModel branding** (ADR-002 addendum 3).
      (was: (from M06, `content/seo/financial-projections-for-accountants.md`):
      (a) how long the 5-model pack credits stay valid (M02 suggested 12 months);
      (b) delivered files: StartupModel branding inside the workbook or none / white-label for firms?)

- [x] D10 Customer login + priority — Henry 2026-10-17: **magic link by email**; build the working app
      (login, payments, download) before more templates (ADR-006, BACKLOG priority note).

- [ ] D9 Failed-build policy (from M07, `content/email/build-failed.md`): when a model fails the
      checks, what does the customer get? Option A: automatic full refund at once. Option B: we fix
      and deliver within N business days (e.g. 2), or refund if they prefer. Also: support email
      address for all emails (`[SUPPORT_EMAIL]`).

- [ ] D11 Five-model pack and Light→Full upgrade (from E13): the site offers both, but there is no checkout for them
      yet — the landing says "write to us". Keep them manual (you invoice by Stripe payment link / refund the
      difference) or add them to checkout (an E task)?

- [ ] D12 Investor pitch on the Light plan (from E07): the "Investor-ready pitch model" goal adds Summary,
      Break-even and Valuation sheets to any plan. Keep it available on Light ($149), or make that goal
      require Full ($349) in the wizard (an E task)? Non-blocking; today it works on both.

## Legal (from E13, blocks Stripe live activation)
- [ ] L1 Privacy policy, Terms of service, Refund policy (Henry 2026-10-17: provides his own texts). Save them as
      `content/legal/privacy.md`, `terms.md`, `refunds.md` (Markdown: `#` headings, paragraphs, `-` lists,
      `**bold**`, `[link](url)`), or send them to an agent to add. Until then `/privacy`, `/terms`, `/refunds`
      show "being prepared" and are not indexed. Stripe checks these pages before enabling live payments.

## Accounts & keys (put keys only into the hosting provider's env vars, never in chat or the repo)
Step-by-step for all of these: `docs/DEPLOY.md` (Railway service + Postgres + volume, Cloudflare DNS, Stripe
webhook, Resend domain).
- [ ] A1 Anthropic API key with a monthly spend limit (for the brief builder).
- [ ] A2 Stripe account, test-mode keys first (put them only into Railway env vars). Exact steps (keys, webhook
      endpoint `/webhooks/stripe` and its 3 events, local test with the Stripe CLI): `docs/PAYMENTS.md`.
- [ ] A3 Email provider (Resend or Postmark) + DNS records for the domain.
- [ ] A4 Railway account (project with app, worker and Postgres services).
- [ ] A5 Domain (after D1).

## Reviews
- [ ] R0 (non-blocking) CFO glance at the shared engine economics in `docs/DECISIONS.md` ADR-003
      "Economics defaults": tax loss carry-forward, straight-line depreciation, loan drawn in period 1
      with straight-line repayment, AR/inventory/AP days. Sample: run
      `python -m engine.build engine/briefs/cafe.json cafe.xlsx` (or ask an agent for the file).
- [ ] R1 CFO sign-off for each template (agents add one line per template with the
      sample file and assumption memo). Launch is blocked until the launch
      templates are signed off.
      - [ ] SaaS: sample `samples/saas-full.xlsx`, memo `docs/templates/saas.md` (questions at the end).
      - [ ] Retail / e-commerce: sample `samples/retail-full.xlsx`, memo `docs/templates/retail.md` (questions at the end).
      - [ ] Professional services: sample `samples/services-full.xlsx`, memo `docs/templates/services.md` (questions at the end).
      - [ ] Home services / trades: sample `samples/home_services-full.xlsx`, memo `docs/templates/home_services.md` (questions at the end).
      - [ ] Fitness studio / gym: sample `samples/fitness-full.xlsx`, memo `docs/templates/fitness.md` (questions at the end).
      - [ ] Goal modules (break-even, DCF valuation, investor summary — all templates): sample
            `samples/cafe-investor_pitch.xlsx`, memo `docs/templates/goal-modules.md` (questions at the end).
- [x] R2 Lawyer review of legal drafts — n/a: Henry cancelled M08 (2026-10-17); legal texts are his to provide.

## Go-live
- [ ] G1 Deploy and run the first real order end to end (runbook from E18).
