# Go-live runbook — StartupModel v0.1.0

For Henry. Takes the site from today's state (Railway, Stripe **test mode**, Railway address, Resend
test sender) to taking real money on `https://startup-model.com`. Every step is done in a web console;
no terminal is needed. Settings screens are described in detail in `docs/DEPLOY.md`; this file is the
order to do them in and how to check each one.

**How to know where you are.** Two places show the same go-live preflight (`app/golive.py`):

- the top of **`/admin`** — a box "Before live payments" lists every open item; it disappears when
  nothing is left;
- the **Railway deploy log** — right after the line `v0.1.0 env=prod …` comes
  `go-live preflight v0.1.0: not ready` (or `READY for live payments`) with one line per check.

Each step below names the check it turns to `ok`. `WARN` = fine while testing; `FAIL` = live payments
are on and this is still wrong — fix it at once.

| Check | What it means | Step |
|---|---|---|
| `domain` | `PUBLIC_BASE_URL` is `https://` and not a Railway / localhost address | 2 |
| `email` | real email provider, `EMAIL_FROM` on the site's domain (not `resend.dev`) | 3 |
| `support` | `SUPPORT_EMAIL` set | 3 |
| `admin` | `ADMIN_USER`, `ADMIN_PASSWORD`, `ADMIN_EMAIL` set (failure alerts) | 1 |
| `client_ip` | `CLIENT_IP_HEADER` set (rate limits count real visitors) | 1 |
| `legal` | `content/legal/privacy.md`, `terms.md`, `refunds.md` exist | 4 |
| `stripe` | live key **and** `ALLOW_LIVE_PAYMENTS=1` | 7 |
| `webhook` | `STRIPE_WEBHOOK_SECRET` (`whsec_…`) set — `FAIL` whenever it is missing | 7 |
| `email_copy` | no unfinished placeholder in the emails (today: build-failed, decision D9) | 0 |

## 0. Decisions before go-live (not technical)

- **R1 CFO sign-off** of the templates you will sell (HUMAN_TODO R1). A template you have not signed
  off can stay listed; just do not promote it.
- **D9 failed-build policy** — decided 2026-10-18: the customer is told the model is being fixed and
  gets a passing one within 2 business days (`/admin` → Re-build), or a full refund.
- **Tax**: VAT / sales tax with your tax adviser (HUMAN_TODO D2) — Stripe charges the price as is.
- **D11** pack and upgrade stay manual ("write to us") unless you decide otherwise.

## Production variables at go-live

All in Railway → app service → **Variables**; values never in chat or the repo. Meaning of each:
`docs/DEPLOY.md` §1. Already set today unless a step is named.

| Variable | Final value | Set in |
|---|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | done |
| `SECRET_KEY` | 48+ random characters — never change it | done |
| `PUBLIC_BASE_URL` | `https://startup-model.com` | step 2 |
| `PAYMENT_PROVIDER` | `stripe` | done |
| `STRIPE_SECRET_KEY` | `sk_live_…` (or `rk_live_…`) | step 7 |
| `STRIPE_WEBHOOK_SECRET` | live endpoint's `whsec_…` | step 7 |
| `ALLOW_LIVE_PAYMENTS` | `1` | step 7 |
| `EMAIL_PROVIDER` | `resend` | done |
| `EMAIL_API_KEY` | Resend key `re_…` | done |
| `EMAIL_FROM` | `StartupModel <models@startup-model.com>` | step 3 |
| `SUPPORT_EMAIL` | `support@startup-model.com` | step 3 |
| `ADMIN_USER` / `ADMIN_PASSWORD` | your admin login, password 12+ characters | step 1 |
| `ADMIN_EMAIL` | your inbox (build-failure alerts) | step 1 |
| `CLIENT_IP_HEADER` | `X-Real-IP` | step 1 |

`APP_ENV=prod` and `STORAGE_DIR=/data/storage` come from the image; `RATE_LIMIT_PER_10MIN`,
`LOG_LEVEL` keep their defaults.

## 1. Deploy v0.1.0 and the small variables (5 min)

1. Railway redeploys `main` automatically after the release merge. Open the app service →
   **Deployments** → the newest one → **View logs**. Expect `v0.1.0 env=prod …`,
   `migrations applied`, the preflight block, then the web server start.
2. `https://<railway address>/healthz` → `{"status":"ok","version":"0.1.0"}`.
3. App service → **Variables**: `CLIENT_IP_HEADER` = `X-Real-IP` (HUMAN_TODO A6 → check `client_ip`);
   make sure `ADMIN_USER`, `ADMIN_PASSWORD` (12+ characters) and `ADMIN_EMAIL` (your inbox) are set
   (check `admin`). Saving variables redeploys the service (≈2 min).

## 2. Domain (HUMAN_TODO A5, 15 min + DNS wait)

State on 2026-10-18: `https://startup-model.com` already reaches the app through Cloudflare, but
`PUBLIC_BASE_URL` is still the Railway address (the sitemap and canonical links point there) — only
item 2 below is left.

1. Railway → app service → **Settings → Networking → Custom Domain** → `startup-model.com`; add the
   CNAME (proxied) and TXT records in Cloudflare exactly as `docs/DEPLOY.md` §2 says; SSL/TLS **Full**.
2. When Railway shows the domain as active: Variables → `PUBLIC_BASE_URL` = `https://startup-model.com`
   (check `domain`). This address goes into download links, sign-in links and Stripe return pages.
3. Check: `https://startup-model.com/healthz` answers; the landing loads with a padlock;
   `https://startup-model.com/sitemap.xml` lists `https://startup-model.com/…` addresses.

## 3. Email from your own domain (HUMAN_TODO A3, 10 min + DNS wait)

1. Resend → **Domains → Add** `startup-model.com`, put its SPF / DKIM / MX records into Cloudflare as
   **DNS only** (grey cloud), wait for "Verified" (`docs/DEPLOY.md` §4).
2. Variables: `EMAIL_FROM` = `StartupModel <models@startup-model.com>`, `SUPPORT_EMAIL` =
   `support@startup-model.com` (checks `email`, `support`). Set up Cloudflare Email Routing so
   `support@` reaches your inbox (`docs/DEPLOY.md` §2.6).
3. Check: sign in at `https://startup-model.com/login` with your own address — the sign-in email
   arrives from `models@startup-model.com`, not in spam.

## 4. Legal pages (HUMAN_TODO L1)

Done 2026-10-18: `content/legal/privacy.md`, `terms.md`, `refunds.md` (StartupModels LLC, Wyoming).
After the deploy, `/privacy`, `/terms`, `/refunds` show the texts and become indexable (check `legal`).
A text with an unfilled `[PLACEHOLDER]` is never published. Stripe reviews these pages before it enables live payments.

## 5. Full test order on the real domain (test mode, 10 min)

On a phone or a private window, as a customer would:

1. `https://startup-model.com` → **Build my model** → answer the wizard with your own email → plan
   Light → pay with test card `4242 4242 4242 4242`, any future date, any CVC.
2. Within a minute: the order-received email, then the model-ready email with a download link.
3. Open the file in Excel: no `#REF!`/`#VALUE!`, the **Checks** sheet says PASS, switching the
   scenario cell changes the numbers.
4. `/admin` → the order is `ready`; **Refund** it — the refund email arrives.
5. Stripe Dashboard (test mode) → **Developers → Webhooks** → the endpoint shows successful (2xx)
   deliveries only.

If any of this fails, stop here (see "Rollback" below) — do not switch to live.

## 6. Stripe account ready for live (Stripe, ~30 min, review may take days)

1. Stripe → **Settings → Business**: public business name **StartupModel** (today it shows
   "FRANCHISE" on the checkout page), statement descriptor `STARTUPMODEL`, support email
   `support@startup-model.com`, website `https://startup-model.com`.
2. **Activate payments**: business details, bank account, identity. Product description: "Custom Excel
   financial models, delivered by email" — prices $149 / $349 are on the site.
3. Wait for Stripe's approval email.

## 7. Switch on live payments (5 min)

Do the three variable changes in **one** save — a live key without `ALLOW_LIVE_PAYMENTS=1` stops the
web app from starting:

1. Stripe (live mode) → **Developers → Webhooks → Add endpoint**
   `https://startup-model.com/webhooks/stripe`, events `checkout.session.completed`,
   `checkout.session.async_payment_succeeded`, `checkout.session.expired`. Copy its signing secret.
2. Stripe (live mode) → **Developers → API keys** → secret key (or a restricted key with Checkout
   Sessions write + Refunds write).
3. Railway Variables, one save: `STRIPE_SECRET_KEY` = `sk_live_…`, `STRIPE_WEBHOOK_SECRET` = the live
   `whsec_…`, `ALLOW_LIVE_PAYMENTS` = `1` (checks `stripe`, `webhook`).
4. Deploy log: `stripe=live` and `go-live preflight v0.1.0: READY for live payments` (an open
   `email_copy` WARN is allowed). `/admin` shows no box, or only `email_copy`.

## 8. First real order (15 min)

1. Repeat step 5 with **your own real card** on the Light plan ($149).
2. Check the email, the file, `/admin` (status `ready`, amount $149), and Stripe live → Payments.
3. `/admin` → order → **Refund**; Stripe shows the refund; the refund email arrives.
4. Tell the agents you are live: tick HUMAN_TODO G1 with the date.

## 9. First week

- Each morning: `/admin` counters — **Failed** must stay 0 (each failure also emails `ADMIN_EMAIL`);
  orders stuck in `paid`/`building` for more than 15 minutes mean the worker is down (deploy log).
- Stripe → Webhooks: no failing deliveries.
- Railway → Postgres → **Backups** enabled (daily).

## Rollback

**Rollback triggers** — act at once if any of these happens:

- a paid order is not `ready` within 15 minutes, or any order ends `failed`;
- `/healthz` does not answer, or the deploy log shows the container restarting in a loop;
- Stripe shows failing webhook deliveries;
- a customer reports a file with errors or a Checks FAIL.

**Bad release** (it worked before the last deploy): Railway → app service → **Deployments** → the last
good deployment → **⋯ → Redeploy**. The database is kept. v0.1.0 is the first release; for later ones,
read the release notes first — a release that added a database migration says whether the previous
version still runs on the new schema.

**Stop taking orders** (anything you cannot fix in minutes): Railway → app service → **Deployments** →
active deployment → **⋯ → Remove** (the site goes offline). Paid orders are not lost: they are in
Postgres and Stripe keeps retrying webhooks for up to 3 days; redeploy when fixed and the worker
builds them. Do **not** swap the live keys back to test keys while the site is up — anyone could then
"buy" a model with a test card.

**Wrong live variables** (preflight `FAIL`, or the web app does not start after step 7): compare the
three values with step 7 and save them again; if the cause is not obvious, "Stop taking orders" until
it is fixed.

**One bad model**: `/admin` → order → **Refund**; **Re-build** rebuilds it from the stored brief.
