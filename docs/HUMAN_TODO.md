# Henry's queue

Things only Henry can do. Agents add items here; Henry ticks them and writes
the answer next to the item (agents read this file every run).

## Decisions
- [ ] D1 Brand name and domain — options will come from M02 (`docs/marketing/positioning.md`).
- [ ] D2 Payment provider: Stripe (you handle VAT/sales tax yourself) or a merchant of
      record such as Lemon Squeezy or Paddle (they handle tax, higher fee). Code
      supports Stripe first, adapter for the other.
- [ ] D3 Prices for Light and Full tiers (M02 will recommend).
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
