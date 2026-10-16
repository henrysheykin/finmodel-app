---
id: refund-issued
trigger: refund created
type: transactional
subject: "Your refund of {{ amount }} is on its way"
preheader: "Order {{ order_id }}. Card refunds usually take a few business days to appear."
---

Hi {{ first_name or "there" }},

We've refunded **{{ amount }}** for order {{ order_id }} to the card you paid with.

Refunds usually take a few business days to appear on your statement. The exact timing depends on your bank.

You can keep any file you downloaded.

If something didn't work for you, we'd like to know what. Just reply. It's optional, and it doesn't affect your refund.

StartupModel
{{ support_email }}
