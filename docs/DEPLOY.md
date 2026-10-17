# Deploy: Railway + Cloudflare + Stripe + Resend

Shape (ADR-008): **one Railway service** built from the repo's `Dockerfile`, plus **Railway
Postgres** and a **volume at `/data`** for the built `.xlsx` files. The container entry point
`deploy/start.sh` applies migrations, then runs the build worker and the web server side by side;
if either stops, the container stops and Railway restarts it. Cloudflare stays the registrar and DNS
for `startup-model.com`. Vercel is not used (no long-running worker, no LibreOffice).

Verified locally on 2026-10-17: the production image starts against Postgres 16 with a mounted
volume, applies migrations, owns `/data/storage` as the `app` user and serves the full customer path
(wizard → payment → build in ~9 s → email → sign-in → download).

## 1. Railway project (≈10 minutes)

1. Railway → **New Project → Deploy from GitHub repo** → `henrysheykin/finmodel-app` (allow the
   Railway GitHub app; private repos work). Railway detects the `Dockerfile`.
2. In the project: **+ New → Database → PostgreSQL**.
3. App service → **Settings**:
   - **Volumes → + Volume**, mount path `/data`.
   - **Deploy → Healthcheck path** `/healthz`, timeout 120 s.
   - **Deploy → Restart policy**: On failure.
4. App service → **Variables** (values typed in Railway only, never in chat or the repo):

| Variable | Value |
|---|---|
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (Railway reference) |
| `SECRET_KEY` | 48+ random characters from a password manager. Never change it later: it signs download links and sessions. |
| `PUBLIC_BASE_URL` | `https://startup-model.com` (the Railway URL while testing before DNS) |
| `PAYMENT_PROVIDER` | `stripe` |
| `STRIPE_SECRET_KEY` | test: `sk_test_…`; go-live: `sk_live_…` (or a restricted `rk_live_…`) |
| `STRIPE_WEBHOOK_SECRET` | `whsec_…` of the webhook endpoint in step 3 (test and live endpoints have different secrets) |
| `ALLOW_LIVE_PAYMENTS` | empty while testing; `1` only at go-live |
| `EMAIL_PROVIDER` | `resend` |
| `EMAIL_API_KEY` | Resend API key (`re_…`) |
| `EMAIL_FROM` | `StartupModel <models@startup-model.com>` |
| `SUPPORT_EMAIL` | `support@startup-model.com` |
| `ADMIN_USER` / `ADMIN_PASSWORD` | your admin login; password 12+ characters |
| `ADMIN_EMAIL` | where build-failure alerts go (your own inbox) |
| `CLIENT_IP_HEADER` | `X-Real-IP` (Railway's edge sets it to the visitor's address; used by the rate limits) |
| `RATE_LIMIT_PER_10MIN` | optional; default `30` new orders and `30` checkout sessions per visitor address per 10 minutes, `0` = off |

`APP_ENV=prod` and `STORAGE_DIR=/data/storage` are set in the image. The app refuses to start in
production without `SECRET_KEY`, Stripe and a real email provider; `python -m app.manage check`
(first line of the deploy log) prints the active settings without secrets.

## 2. Domain on Cloudflare

1. App service → **Settings → Networking → + Custom Domain** → `startup-model.com`. Railway shows a
   **CNAME** target (`….up.railway.app`) and a **TXT** verification record.
2. Cloudflare → DNS: add **CNAME `@` → the Railway target, proxied (orange)**, and the **TXT** record
   exactly as shown. Both are required.
3. Cloudflare → **SSL/TLS → Full** (not Full strict); Universal SSL on.
4. Optional: CNAME `www` → `@` (proxied) and a 301 redirect `www` → root.
5. Do **not** turn on Bot Fight Mode (it can block Stripe's webhook calls); if a WAF rule is added
   later, skip it for `/webhooks/stripe`.
6. Support inbox for free: Cloudflare **Email Routing** → forward `support@startup-model.com` to
   your own mailbox.

## 3. Stripe

1. Dashboard → **Developers → Webhooks → Add endpoint** `https://startup-model.com/webhooks/stripe`,
   events `checkout.session.completed`, `checkout.session.async_payment_succeeded`,
   `checkout.session.expired`. Copy the signing secret into `STRIPE_WEBHOOK_SECRET`.
2. Test first: test-mode key + test-mode webhook, pay with `4242 4242 4242 4242`, any future date,
   any CVC. The model must arrive by email and in "My models".
3. Go-live: activate the account (business details, bank account, identity). Stripe reviews the site:
   product description, prices, refund policy, terms, privacy policy and a contact address must be
   visible. Then create the **live** webhook endpoint (same URL and events), switch
   `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` to the live values and set
   `ALLOW_LIVE_PAYMENTS=1`. Make one real purchase with your own card, then refund it from `/admin`.
4. Tax: Stripe charges the price as is; VAT/sales tax handling (Stripe Tax, EU OSS) is a decision
   for your tax adviser (HUMAN_TODO D2).

## 4. Resend (email)

1. resend.com → **Domains → Add** `startup-model.com` (Resend uses a `send.` subdomain for bounces).
2. Add the DNS records it lists (SPF, DKIM, MX for `send`) in Cloudflare as **DNS only** (grey).
3. Wait for "Verified", create an API key with sending access, put it in `EMAIL_API_KEY`.

## 5. After every deploy

- `https://startup-model.com/healthz` → `{"status":"ok"}`.
- `/admin` → sign in; the order counters load.
- A test order (test mode) or, after go-live, watch the first real orders in `/admin`.

## Backups and recovery

- Postgres: Railway's database backups (enable in the Postgres service). Orders, briefs, payments
  and accounts live there.
- Files on `/data` can always be rebuilt from the stored brief (`/admin` → order → Re-build), so the
  volume is not the only copy of anything that matters.

## Rate limits

Per visitor address, in memory of the one web process (a restart resets the counts):

| Endpoint | Limit | When exceeded |
|---|---|---|
| `POST /start` (wizard) and `POST /api/orders` — one shared budget | 30 / 10 min | 429 + `Retry-After`; the wizard re-shows the form with the answers kept |
| `POST /checkout/{id}/pay` (opens a Stripe session) | 30 / 10 min | 429 page with a link back to the order |
| `POST /login` (magic link) | 5 per email, 20 per address / 15 min | same "check your inbox" answer, no email |
| `POST /admin/login` | failed attempts per address | 429 |

The visitor address is the `CLIENT_IP_HEADER` header when set, otherwise the peer address uvicorn
takes from `X-Forwarded-For`. Use a header the edge proxy *overwrites* (Railway: `X-Real-IP`), so a
caller cannot pick its own address. Check after deploy: two orders from your phone and laptop on
different networks do not share a budget.

## Local run of the production image

The whole stack (production image with web + worker, Postgres 16, a volume) with Docker Compose —
fake payments (a `/dev/pay` page), emails printed to the log, throwaway local credentials:

```bash
docker compose up --build --wait                        # http://localhost:8000, admin: admin / local-admin-only
COMPOSE_BASE_URL=http://localhost:8000 pytest -m compose tests/test_compose_e2e.py
docker compose logs app                                 # worker + web log, including the emails
docker compose down -v                                  # stop and delete the local data
```

The E2E test walks the customer path (landing → wizard → checkout → test payment → worker build with
LibreOffice → challenger → ready) and downloads the model through `/admin`; its Checks sheet must
say PASS. CI runs it on every pull request (`compose` job).

Single container without Postgres:

```bash
docker build -t finmodel-app .
docker run --rm -p 8000:8000 -e APP_ENV=dev finmodel-app      # fake payments, console email, SQLite
```
