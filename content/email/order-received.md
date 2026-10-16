---
id: order-received
trigger: order status becomes paid
type: transactional
subject: "We've got your order: your {{ tier }} model is being built"
preheader: "Order {{ order_id }}. We'll email the download link as soon as the checks pass."
---

Hi {{ first_name or "there" }},

Thanks for your order. Here's what you bought:

- **Model:** {{ template_title }}, {{ tier }}
- **Horizon:** {{ horizon_years }} years, {{ granularity }} detail
- **Paid:** {{ amount }}
- **Order:** {{ order_id }}

**What happens now**

1. We build your workbook from your answers.
2. Every scenario and year is recomputed independently, outside Excel. The workbook has to match within $1, and the Checks sheet must show no FAIL.
3. When it passes, we email you a download link.

If anything fails, the file is not sent. We'll email you instead and tell you what happens next.

You don't need to do anything. If you spot a mistake in your answers, reply to this email and tell us before the model is ready.

StartupModel
{{ support_email }}
