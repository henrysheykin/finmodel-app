# Email copy (for E12)

One file per email. Front matter: `id`, `trigger`, `type` (transactional / service / marketing),
`subject`, `preheader`. Body is Markdown with Jinja2 variables; render to HTML and plain text.

Variables used (all must be supplied by E12; fall back as shown):

| Variable | Meaning | Fallback |
|---|---|---|
| `first_name` | Customer's first name, optional in the wizard | "there" (`{{ first_name or "there" }}`) |
| `order_id` | Human-readable order reference | — |
| `tier` | "Light" or "Full" | — |
| `template_title` | e.g. "Restaurant / cafe" | — |
| `horizon_years`, `granularity` | 1/3/5, "monthly"/"annual" | — |
| `amount` | Amount paid or refunded, formatted, e.g. "$349" | — |
| `download_url` | Signed link to the file | — |
| `link_expires` | Expiry date of the signed link (7 days) | — |
| `resend_url` | Page that issues a fresh link | — |
| `resume_url` | Returns to the saved wizard / checkout | — |
| `feedback_url` | Feedback form | — |
| `unsubscribe_url` | One-click unsubscribe (service and marketing emails) | — |
| `support_email` | Reply-to / support address | `[SUPPORT_EMAIL]` until set |

Rules: plain and short; no countdown timers, fake scarcity or guilt; one reminder only for
abandoned checkout; marketing emails only to people who consented (legal check in M08);
never mention FinModelsLab; sign-off "StartupModel".

| File | Trigger | Type |
|---|---|---|
| order-received.md | payment confirmed (`paid`) | transactional |
| model-ready.md | job `ready` | transactional |
| build-failed.md | job `failed` | transactional |
| refund-issued.md | refund created | transactional |
| how-to-use.md | day 1 after `ready` | service (opt-out link) |
| feedback-request.md | day 7 after `ready` | marketing-lite (opt-out link) |
| abandoned-checkout.md | 24 h after checkout started and not paid, once | marketing (consent + opt-out) |
