# Henry's queue

Things only Henry can do. Agents add items here; Henry ticks them and writes
the answer next to the item (agents read this file every run).

## Decisions
- [ ] D1 Pick name + domain — 8 screened candidates in `docs/marketing/positioning.md`
      (Ledgerline = CAUTION; suggested legal-search order: Modelproof, Sheetproof, Balanceproof).
      Web screening only: check TMview / USPTO / WIPO in classes 9, 35, 36, 42, domains and handles yourself.
- [ ] D2 Payment provider: Stripe (you handle VAT/sales tax yourself) or a merchant of
      record such as Lemon Squeezy or Paddle (they handle tax, higher fee). Code
      supports Stripe first, adapter for the other.
- [ ] D3 Pick price — M02 recommends Light $149 (floor $129, never $99), Full $349 (fallback $299,
      max $399), Light->Full upgrade = pay the difference, accountant pack 5 Full for $1,250.
      Reasoning in `docs/marketing/positioning.md`.
- [ ] D5 FinModelsLab vs Ledgerline (from M01, `docs/marketing/competitors.md`): FinModelsLab
      sells 2,000 templates at $99 with the same headline features. Decide (a) keep the brands
      separate or linked, (b) whether to offer a FinModelsLab -> Ledgerline "built on your
      numbers" upgrade credit, (c) confirm the price for D3 should sit clearly above $99.
- [ ] D4 Hosting for the Docker image (options in `docs/DEPLOY.md` after E15).

## Accounts & keys (put keys only into the hosting provider's env vars, never in chat or the repo)
- [ ] A1 Anthropic API key with a monthly spend limit (for the brief builder).
- [ ] A2 Payment provider account (after D2), test keys first.
- [ ] A3 Email provider (Resend or Postmark) + DNS records for the domain.
- [ ] A4 Hosting account (after D4).
- [ ] A5 Domain (after D1).

## Reviews
- [ ] R1 CFO sign-off for each template (agents add one line per template with the
      sample file and assumption memo). Launch is blocked until the launch
      templates are signed off.
- [ ] R2 Lawyer review of legal drafts (after M08).

## Go-live
- [ ] G1 Deploy and run the first real order end to end (runbook from E18).
