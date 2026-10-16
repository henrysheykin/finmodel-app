# Henry's queue

Things only Henry can do. Agents add items here; Henry ticks them and writes
the answer next to the item (agents read this file every run).

## Decisions
- [x] D1 Name + domain — **startup-model.com, brand StartupModel** (Henry gave 6 domains,
      agent picked; ADR-002). Still for Henry: TMview / USPTO check for "StartupModel" (classes
      9, 35, 36, 42); optionally buy startupmodel.com as a redirect.
      "Startup Models" (startupmodels.co) — Henry 2026-10-16: site not active, not a concern.
- [x] D2 Payment provider — Henry 2026-10-16: **Stripe** (ADR-003). Consequence: VAT / sales
      tax is yours (e.g. Stripe Tax and/or EU VAT OSS registration in Spain) — confirm with
      your tax adviser before go-live.
- [x] D3 Price — Henry 2026-10-16: **Light $149, Full $349, pack 5 × Full $1,250**, Light->Full
      upgrade = pay the difference. **Refund window: 7 days.**
- [x] D5 FinModelsLab vs StartupModel — Henry 2026-10-16: **separate brands**. No links,
      copy or upgrade credit between them (ADR-002).
- [x] D4 Hosting — Henry 2026-10-16: "Vercel/Railway" → **Railway** for app + worker + Postgres
      (ADR-003). Vercel is not used: it runs serverless functions, not our Docker image with
      LibreOffice and a long-running worker.

## Accounts & keys (put keys only into the hosting provider's env vars, never in chat or the repo)
- [ ] A1 Anthropic API key with a monthly spend limit (for the brief builder).
- [ ] A2 Stripe account, test-mode keys first (put them only into Railway env vars).
- [ ] A3 Email provider (Resend or Postmark) + DNS records for the domain.
- [ ] A4 Railway account (project with app, worker and Postgres services).
- [ ] A5 Domain (after D1).

## Reviews
- [ ] R1 CFO sign-off for each template (agents add one line per template with the
      sample file and assumption memo). Launch is blocked until the launch
      templates are signed off.
- [ ] R2 Lawyer review of legal drafts (after M08).

## Go-live
- [ ] G1 Deploy and run the first real order end to end (runbook from E18).
