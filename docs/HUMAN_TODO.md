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
- [ ] D13 (from L1) EU consumers have a 14-day right to withdraw from digital purchases unless, at checkout, they expressly
      agree to immediate delivery and acknowledge losing that right. The checkout has no such checkbox yet, so for consumers
      the 7-day refund is effectively 14 days. Add the checkbox (small E task) or accept 14 days for consumers?
- [ ] L1 Privacy policy, Terms of service, Refund policy — **drafted by an agent 2026-10-18** at Henry's request
      (`content/legal/privacy.md`, `terms.md`, `refunds.md`; not reviewed by a lawyer). They go live automatically once the
      three placeholders are filled; until then the pages keep saying "being prepared". Henry: send the agent
      (a) the seller's legal name (your full name as autónomo, or the company name), (b) NIF/NIE/CIF, (c) postal address
      in Spain. Read the texts once; two choices in them are yours to confirm:
      - refunds.md answers **D9**: a model that fails the checks → the customer chooses a corrected model or a full refund;
      - terms.md: prices **include** any tax we must charge (see D2 / tax adviser).

## Accounts & keys (put keys only into the hosting provider's env vars, never in chat or the repo)
Step-by-step for all of these: `docs/DEPLOY.md` (Railway service + Postgres + volume, Cloudflare DNS, Stripe
webhook, Resend domain).
- [ ] A1 Anthropic API key with a monthly spend limit (for the brief builder).
- [x] A2 (test mode done 2026-10-17: keys + webhook on the Railway URL, test purchase delivered) Stripe account, test-mode keys first (put them only into Railway env vars). Exact steps (keys, webhook
      endpoint `/webhooks/stripe` and its 3 events, local test with the Stripe CLI): `docs/PAYMENTS.md`.
- [x] A3 (Resend key done 2026-10-17; domain DNS still to verify — sender is onboarding@resend.dev until then) Email provider (Resend or Postmark) + DNS records for the domain.
- [x] A4 (done: https://finmodel-app-production.up.railway.app, Postgres, all variables; end-to-end test order 539a9c52 ready, Checks PASS) Railway account (project with app, worker and Postgres services).
- [ ] A5 Domain (after D1).
- [ ] A6 (from E15, 1 minute) Railway → app service → Variables: add `CLIENT_IP_HEADER` = `X-Real-IP`, so the new rate
      limits (30 orders / 30 checkouts per visitor per 10 min) count real visitor addresses (docs/DEPLOY.md "Rate limits").

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
      - [ ] Real estate / rental property (incl. annuity mortgage, land, Returns sheet with IRR/NPV): sample
            `samples/real_estate-full.xlsx`, memo `docs/templates/real_estate.md` (questions at the end).
      - [ ] Goal modules (break-even, DCF valuation, investor summary — all templates): sample
            `samples/cafe-investor_pitch.xlsx`, memo `docs/templates/goal-modules.md` (questions at the end).
- [x] R2 Lawyer review of legal drafts — n/a: Henry cancelled M08 (2026-10-17); legal texts are his to provide.

## Go-live (v0.1.0, E18 — step by step with checks: `docs/RUNBOOK_GO_LIVE.md`)
Where you stand at any moment: the "Before live payments" box at the top of `/admin` (also printed in every
Railway deploy log). It disappears when everything is done.
- [ ] G0 (1 minute) Tag the release: GitHub → finmodel-app → Releases → Draft a new release → "Choose a tag" → type
      `v0.1.0` → target: commit `0deedd7` (E18 merge on main) → title "v0.1.0", notes from `CHANGELOG.md` → Publish.
      Agents cannot push tags from their sandbox.
- [ ] G1 Go live — the exact steps, in order (runbook section in brackets):
  - [ ] G1.1 Decide what to launch with: R1 sign-offs for the templates you will promote; D9; VAT with your adviser (§0).
  - [ ] G1.2 Railway Variables: `CLIENT_IP_HEADER=X-Real-IP` (= A6), `ADMIN_EMAIL` = your inbox (§1).
  - [ ] G1.3 `PUBLIC_BASE_URL=https://startup-model.com` — the domain already answers (checked 2026-10-18), but the
        sitemap and links still use the Railway address (§2).
  - [ ] G1.4 Resend: verify startup-model.com, then `EMAIL_FROM=StartupModel <models@startup-model.com>`,
        `SUPPORT_EMAIL=support@startup-model.com`, Cloudflare Email Routing for support@ (§3).
  - [ ] G1.5 Legal texts into `content/legal/` (= L1) (§4).
  - [ ] G1.6 Test-mode order on https://startup-model.com with card 4242…: emails, file, Checks PASS, refund (§5).
  - [ ] G1.7 Stripe: public name StartupModel (now "FRANCHISE"), activate the account (§6).
  - [ ] G1.8 Live webhook + `sk_live_…` + its `whsec_…` + `ALLOW_LIVE_PAYMENTS=1` in ONE save; deploy log says
        "READY for live payments" (§7).
  - [ ] G1.9 One real $149 purchase with your own card, check, refund from /admin; tick G1 with the date (§8).
