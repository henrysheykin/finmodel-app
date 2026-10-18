# E17 — Hardening review: end to end, security, performance

Date: 2026-10-18 · Track E (scheduled run) · Scope: `app/`, `adapters/`, `worker/`, `deploy/`, CI.
Method: read every request handler, the auth, payment, link and storage code; reproduce each
suspected problem with a failing test first, then fix; full customer journey in a browser;
dependency audit; load test of 50 simultaneous orders on one worker.

**Result: no open high-severity items.** Everything found at high or medium severity is fixed
and covered by a test. What remains is low severity or a decision by design, listed at the end.

## Findings

| # | Area | Finding | Severity | Status |
|---|---|---|---|---|
| 1 | Payments | Two deliveries of the same Stripe webhook processed at the same moment (provider retry + slow first response, or two web threads) could each "win": each queued its own build and sent its own receipt — reproduced with 4 threads: 4 builds, 4 receipts. The "already paid?" check read the row before the other request committed, and the job round number was recomputed after it. | High | Fixed: the payment is claimed with a conditional `UPDATE … WHERE payment_ref IS NULL AND status='awaiting_payment'`; losers get `AlreadyPaid` → `already_paid`, no receipt, no build. The reference-clash check ignores the order itself. `tests/test_concurrency.py` (6 threads × 10 rounds; 50 customers × 2 parallel deliveries). |
| 2 | Performance | The Stripe webhook, magic-link sign-in, wizard submit, test-payment page and admin actions were `async` handlers doing blocking work (database, Stripe API, email API) on the event loop. With one web process, one slow email send (Resend timeout 15 s) froze every page for every visitor — reproduced: `/healthz` took 1.8 s while one sign-in email took 2 s. | High | Fixed: the form/body is read by an async dependency (`FormData`, `RawBody`); the handlers are plain `def`, so FastAPI runs them in its thread pool. Test: a 2-second email no longer delays other requests. |
| 3 | Auth | Admin login: 5 failures per address, but nothing across addresses — an attacker rotating addresses could guess without limit. | Medium | Fixed: also 50 failures per 15 minutes from all addresses together (the owner waits out the window during an attack). |
| 4 | Auth | Magic-link and admin-login limits keyed on the proxy-derived peer address, while order/checkout limits used `CLIENT_IP_HEADER`: two different notions of "the visitor". | Medium | Fixed: every limit uses `ratelimit.client_ip`. Railway overwrites `X-Forwarded-For` and `X-Real-IP` at its edge (visitor first, internal hop last), so the default is safe there; still set `CLIENT_IP_HEADER=X-Real-IP` (HUMAN_TODO A6). The right-most `X-Forwarded-For` entry must **not** be used on Railway — it is an internal hop and would put every visitor in one bucket. |
| 5 | CSRF | Customer POSTs (`/login`, `/login/verify`, `/logout`, sign out everywhere, wizard, checkout) had no cross-site protection: another site could sign a visitor into the attacker's account (login CSRF), sign them out, or spend their order budget. | Medium | Fixed: any POST whose `Origin` is not our own is refused (403); webhooks are exempt (signed). Admin forms keep their CSRF tokens. |
| 6 | XSS defence | No Content-Security-Policy; the payment-success page had an inline script. | Medium | Fixed: CSP on every response (`script-src 'self'`, `frame-ancestors 'none'`, `object-src 'none'`, `base-uri 'self'`); inline script moved to `web/static/success.js`; a test fails on any executable inline script or `on…=` handler in templates; the browser journey fails on any CSP violation. Jinja autoescaping and the `<script type=application/json>` encoder were already correct. |
| 7 | Secrets in logs | Uvicorn's access log wrote magic-link tokens (`/login/verify?token=…`, valid 15 min) and download tokens (`/download/<token>`, valid 7 days) into the host's logs. | Medium | Fixed: a filter on `uvicorn.access` replaces both with `[redacted]`. |
| 8 | DoS | No request-size limit: a large POST (e.g. to the webhook) was read into memory. | Low | Fixed: bodies over 1 MB are refused with 413 before parsing (no endpoint takes uploads). |
| 9 | Supply chain | Dependencies had lower bounds only: every image build could pull new, untested versions. | Low | Fixed: `constraints.txt` pins the runtime set (the versions tested today); Dockerfile and CI install with `-c constraints.txt`; a test fails when a runtime dependency is not pinned; new CI job `audit` runs `pip-audit` on the pins. |
| 10 | UX under load | The success page stopped polling after 6 minutes; in the load test the 50th customer waited 6.5 minutes. | Low | Fixed: polls every 3 s for 2 minutes, then every 15 s up to 30 minutes. |

Checked and found sound (no change): download links (HMAC-SHA256, constant-time compare, expiry,
artifact must belong to a `ready` order — a refund kills the link); magic links (256-bit, hashed,
single use with an atomic update, 15 minutes, confirm button against mail scanners, same answer
for unknown addresses); customer sessions (hashed, HttpOnly, SameSite=Lax, Secure in prod,
revocable, "sign out everywhere"); another customer's order is a 404; Stripe signatures (timestamp
tolerance, constant-time, amount and currency must match the order, live keys refused unless
`ALLOW_LIVE_PAYMENTS=1`); storage keys (allow-list regex, no `..`, path must stay under the root);
download filenames are server-made slugs (no header injection); SQL only through SQLAlchemy
expressions; production refuses weak `SECRET_KEY`, console email and the fake payment provider;
the `/dev/pay` page is unreachable in production. File uploads: there are none.

## End to end

`tests/test_journey_e2e.py` (CI `test` job; Chromium + LibreOffice): landing → plan link →
wizard → checkout → Stripe-shaped hosted page → **signed webhook** → the same webhook again
(`already_paid`) → one worker with the **real engine** (openpyxl → LibreOffice → challenger) →
"model ready" email rendered from `content/email/` → download from the emailed link → magic-link
sign-in from the emailed link → My models → download (same bytes) → the link refuses a second
use. The downloaded workbook's Checks sheet says PASS; exactly two emails reach the customer;
no page triggers a CSP violation. The Docker stack (production image + Postgres 16) keeps its own
E2E in the CI `compose` job. Real Stripe test mode was verified on Railway on 2026-10-17 (A2); CI
does not call Stripe (no keys in CI, by rule).

## Dependency audit

`pip-audit` on the pinned runtime set (Python 3.12: FastAPI 0.143.3, Starlette 1.8.0, uvicorn
0.54.0, SQLAlchemy 2.1.5, psycopg 3.3.6, httpx 0.28.1, Jinja2 3.1.6, openpyxl 3.1.5, pydantic
2.14.1, python-multipart 0.0.32, markdown-it-py 4.2.0, alembic 1.20.0 …): **no known
vulnerabilities** (2026-10-18). CI re-checks on every push. The base image's Debian packages
(LibreOffice) are not covered by pip-audit; rebuilding the image picks up Debian security updates.

## Load test — 50 simultaneous orders, one worker

`python scripts/load_test.py --orders 50` (result: `docs/reviews/load-test-50.json`). Web and
worker as separate processes, like the container; 50 orders placed through the wizard at once,
each payment delivered twice in parallel; mix of every available industry × Light 1y monthly /
Full 3y monthly / Full 5y annual / Full 5y monthly. Machine: 2 vCPU sandbox, SQLite.

| Measure | Result |
|---|---|
| Orders ready / build jobs / failures | 50 / 50 / 0 |
| Webhooks | 50 `paid`, 50 `already_paid` (no duplicate builds or receipts) |
| Build time per model (generate + LibreOffice + challenger) | mean 7.8 s, p95 9.4 s, max 9.7 s |
| Queue drained in | 391 s → about **460 models per hour** per worker |
| Paid → ready | median 3.3 min, last customer 6.5 min |
| Landing page while building | p50 6 ms, p95 12 ms, max 93 ms |
| Wizard page while building | p50 3 ms, p95 8 ms |
| Order placement / webhook under the burst | p50 0.26 s / 0.24 s, max 0.5 s / 1.3 s |

Reading: one worker is ample for launch (a burst of 50 paid orders is far above what a new site
sees); the web stays fast while LibreOffice runs because the work is in another process. If the
queue ever regularly exceeds ~10 orders, run a second worker process (`python -m worker.main`;
the job claim is atomic, so workers can run side by side).

## Open items (low severity or by design — none blocks release)

- Admin session cookie is stateless (signed, 12 h): "log out" deletes the cookie but a copied
  cookie stays valid until it expires; rotating `SECRET_KEY` revokes all admin sessions (and all
  download links).
- Rate limits live in the memory of the one web process (ADR-008): a restart resets them; a
  second web process would need a shared store.
- `/checkout/{id}` and `/api/orders/{id}` show status to anyone holding the 128-bit order id
  (masked email, no file) — needed by the success page; ids are unguessable.
- Download links are bearer links for 7 days by design (the email can be forwarded); refund or a
  new `SECRET_KEY` revokes them.
- SQLite (dev/tests) may answer a racing webhook with "database is locked" (the provider retries);
  production runs Postgres, where the losing request waits for the row and returns `already_paid`.
