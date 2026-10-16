---
id: abandoned-checkout
trigger: 24 hours after checkout started and not paid; send once, only with marketing consent
type: marketing
subject: "Your model answers are saved"
preheader: "Pick up where you left off, or ignore this. We won't send another reminder."
---

Hi {{ first_name or "there" }},

You started setting up a {{ template_title }} model but didn't finish checkout. Your answers are saved.

**[Pick up where you left off]({{ resume_url }})**

If something stopped you, such as a question about the model, the price or whether it fits your business, reply and ask. A person will answer.

This is the only reminder we'll send. If you've changed your mind, there's nothing you need to do.

StartupModel
{{ support_email }}

[Unsubscribe]({{ unsubscribe_url }})
