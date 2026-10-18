---
id: build-failed
trigger: job status becomes failed
type: transactional
status: not sent (D9, 2026-10-18: failures go to the admin alert only)
subject: "Your model didn't pass our checks, so we haven't sent it"
preheader: "Order {{ order_id }}. Nothing for you to do. Here's what happens next."
---

Hi {{ first_name or "there" }},

We're sorry: the model we built for order {{ order_id }} didn't pass our own checks, so we haven't sent it. We don't deliver a file whose numbers we can't stand behind.

**What happens next**

We're fixing it now and will send you a model that passes within 2 business days. If we can't, we'll refund your {{ amount }} in full.

You don't need to do anything. If you'd rather have your money back straight away, reply to this email and say so.

StartupModel
{{ support_email }}
