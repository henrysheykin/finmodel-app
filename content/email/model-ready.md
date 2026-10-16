---
id: model-ready
trigger: job status becomes ready
type: transactional
subject: "Your financial model is ready to download"
preheader: "{{ template_title }}, {{ tier }}: checked and ready. The link works until {{ link_expires }}."
---

Hi {{ first_name or "there" }},

Your model has passed its checks and is ready.

**[Download your model (.xlsx)]({{ download_url }})**

The link works until {{ link_expires }}. After that, [get a fresh link]({{ resend_url }}). Save the file somewhere you'll find it again; it's yours to keep.

**Before you start**

- **Blue cells are inputs.** Change them freely. Black cells are formulas, green cells link to other sheets.
- **The scenario switch** is on the {% if tier == "Full" %}Dashboard{% else %}Inputs sheet{% endif %}: 1 = Low, 2 = Base, 3 = High.
- **The Checks sheet** re-runs every time you change an input. If something shows FAIL after your edits, the last change broke a link; undo it and try again.

Tomorrow we'll send a short note on getting the most out of the file. That's it, no newsletter.

If the model doesn't fit your business, reply within 7 days of your order and we'll refund the full amount.

StartupModel
{{ support_email }}
