# Payments (E11)

Stripe Checkout, **test mode only** until go-live (ADR-004). Live keys (`sk_live_…`) are refused
unless `ALLOW_LIVE_PAYMENTS=1`; production refuses anything but `PAYMENT_PROVIDER=stripe`.

## Flow
1. Wizard → order `awaiting_payment` → `/checkout/{id}`.
2. "Pay" → `POST /checkout/{id}/pay` creates a Checkout Session (amount and currency from the order,
   `client_reference_id` = order id) and redirects to Stripe.
3. Stripe → `POST /webhooks/stripe`. Signature checked (HMAC-SHA256, 5-minute tolerance). Only
   `checkout.session.completed` / `async_payment_succeeded` with `payment_status=paid` count; the
   amount and currency must match the order. Duplicate deliveries are no-ops. A second, different
   payment for the same order is refunded automatically.
4. The customer lands on `/checkout/{id}/success`, which only shows status (the browser is never
   trusted about payment) and updates itself until the model is ready.
5. Refunds: `app.orders.refund_order` (full amount, idempotent per order); admin button in E14.

## Without keys (dev)
`PAYMENT_PROVIDER=fake` (default outside production): "Pay" opens `/dev/pay/{session}`, a local
test page that sends a signed Stripe-shaped event through the same code path. Hidden in production.

## What Henry sets up (HUMAN_TODO A2)
- Stripe account → **test mode** → API keys: put `STRIPE_SECRET_KEY` (sk_test_…) into Railway env vars.
- Developers → Webhooks → add endpoint `https://<domain>/webhooks/stripe` with events
  `checkout.session.completed`, `checkout.session.async_payment_succeeded`,
  `checkout.session.expired`; copy its signing secret into `STRIPE_WEBHOOK_SECRET`.
- Local test with the Stripe CLI: `stripe listen --forward-to localhost:8000/webhooks/stripe`
  (it prints a temporary signing secret), then pay with card `4242 4242 4242 4242`.
