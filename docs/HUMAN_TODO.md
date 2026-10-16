# Henry's queue

Things only Henry can do. Agents add items here; Henry ticks them and writes
the answer next to the item (agents read this file every run).

## Decisions
- [x] D1 Name + domain — **startup-model.com, brand StartupModel** (Henry gave 6 domains,
      agent picked; ADR-002). Still for Henry: TMview / USPTO check for "StartupModel" (classes
      9, 35, 36, 42); optionally buy startupmodel.com as a redirect.
      "Startup Models" (startupmodels.co) — Henry 2026-10-16: site not active, not a concern.
- [ ] D2 Payment provider: Stripe (you handle VAT/sales tax yourself) or a merchant of
      record such as Lemon Squeezy or Paddle (they handle tax, higher fee). Code
      supports Stripe first, adapter for the other.
- [x] D3 Price — Henry 2026-10-16: **Light $149, Full $349, pack 5 × Full $1,250**, Light->Full
      upgrade = pay the difference. **Refund window: 7 days.**
- [x] D5 FinModelsLab vs StartupModel — Henry 2026-10-16: **separate brands**. No links,
      copy or upgrade credit between them (ADR-002).
- [ ] D4 Hosting for the Docker image (options in `docs/DEPLOY.md` after E15).

## Accounts & keys (put keys only into the hosting provider's env vars, never in chat or the repo)
- [ ] A1 Anthropic API key with a monthly spend limit (for the brief builder).
- [ ] A2 Payment provider account (after D2), test keys first.
- [ ] A3 Email provider (Resend or Postmark) + DNS records for the domain.
- [ ] A4 Hosting account (after D4).
- [ ] A5 Domain (after D1).

## Reviews
- [ ] R0 (non-blocking) CFO glance at the shared engine economics in `docs/DECISIONS.md` ADR-003
      "Economics defaults": tax loss carry-forward, straight-line depreciation, loan drawn in period 1
      with straight-line repayment, AR/inventory/AP days. Sample: run
      `python -m engine.build engine/briefs/cafe.json cafe.xlsx` (or ask an agent for the file).
- [ ] R1 CFO sign-off for each template (agents add one line per template with the
      sample file and assumption memo). Launch is blocked until the launch
      templates are signed off.
- [ ] R2 Lawyer review of legal drafts (after M08).

## Go-live
- [ ] G1 Deploy and run the first real order end to end (runbook from E18).
