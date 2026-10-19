# Status

Written by the P track every Monday (see `docs/BACKLOG.md`, Track P). Last review: **2026-10-19**.

## Done this week (2026-10-16 → 2026-10-19)
- Track E: 24 of 25 tasks done (PRs #1–#42 merged, all via review + green CI). Engine, 6 industry
  templates (SaaS, retail, services, home services, fitness, real estate) + cafe, goal modules
  (break-even, DCF, investor summary), orders/worker/challenger pipeline, wizard, Stripe checkout,
  email delivery, magic-link accounts, admin, SEO engine, hardening (E2E, security, load test of 50 builds),
  release candidate v0.1.0, LLM brief builder on OpenAI (E08, E25, E24, off until `BRIEF_MODEL` is set).
- Track M: 12 of 12 closed (9 done, 3 cancelled by Henry): research, positioning, landing copy, SEO plan,
  4 batches of SEO pages, emails.
- Production: https://startup-model.com answers (`/healthz` → 0.1.0, checked 2026-10-19); legal pages
  live; Stripe activated, Resend domain verified; test order on the Railway URL delivered with Checks PASS.

## In progress
- Nothing is IN_PROGRESS. No open PRs.

## Blocked
- **E23** brief-model eval — `NEEDS_HENRY`: the live run needs `OPENAI_API_KEY` (HUMAN_TODO A1).
  Harness and fixtures are merged (#40, #41); only the live run + memo are left.

## Plan for next week
- Henry: R1 sign-offs → G1.6 test order on the domain → G1.8 live keys → G1.9 first real order.
- E: E23 live run as soon as A1 is in place (needs the E schedule switched back on, see Risks).
- No other E or M task is queued. Candidates if Henry wants them: checkout for the 5-model pack and
  Light→Full upgrade (D11), Light/Full gating of the investor goal (D12).

## Risks
1. **Launch is gated on R1 (CFO sign-off of 7 templates/modules).** Everything else for live payments is
   built; this is now the critical path, and only Henry can do it.
2. Both the "Инженерия" and "Маркетинг" scheduled tasks were switched off on 2026-10-18 21:03 UTC
   (last runs succeeded). When A1 is done, E23 will not run by itself — switch the E task back on or
   run it once by hand.
3. VAT / sales tax on Stripe sales (D2) is not confirmed with the tax adviser — must be settled before
   live money (G1.1).
4. The LLM brief builder ships untested on live traffic: keep `BRIEF_MODEL` empty until the E23 memo.

## Henry's queue (most urgent first)
1. **R1** — sign off the templates you will launch with: open `samples/<industry>-full.xlsx` and answer the
   questions at the end of `docs/templates/<industry>.md`; tick each line in HUMAN_TODO R1
   (start with SaaS and cafe/goal modules).
2. **G1.1 VAT** — one email to your tax adviser: Stripe Tax / EU VAT OSS for a Wyoming LLC selling to EU
   consumers; write the answer next to D2.
3. **G1.6** — test-mode order on https://startup-model.com with card 4242 4242 4242 4242: email, file,
   Checks PASS, refund from /admin (`docs/RUNBOOK_GO_LIVE.md` §5).
4. **G1.8 → G1.9** — live webhook + `sk_live_…` + `whsec_…` + `ALLOW_LIVE_PAYMENTS=1` in one save, then one
   real $149 purchase and refund (§7–§8).
5. **A1** — OpenAI key with a monthly spend limit into the Claude cloud environment (for E23) and Railway;
   then switch the "Инженерия" scheduled task back on. `BRIEF_MODEL` only after the memo.
6. **D11 / D12** — two yes/no answers in HUMAN_TODO (pack + upgrade in checkout? investor goal Full-only?).
7. Optional: G0 tag v0.1.0; R0 glance at ADR-003 economics; A5 can be ticked (domain live);
   TMview/USPTO check for "StartupModel" (D1).
