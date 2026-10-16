---
id: how-to-use
trigger: 1 day after model-ready
type: service
subject: "Three things to do with your model this week"
preheader: "Replace the defaults, test the low case, and send the file, not a screenshot."
---

Hi {{ first_name or "there" }},

A model is only as good as its inputs. Here's how to get the most out of yours.

**1. Replace the defaults with real numbers**
Open the Inputs sheet. Anything you left blank in the questionnaire was filled with a sensible default. Swap in real figures: the rent from your lease, supplier quotes, actual salaries. Next to each one, note where it came from. Whoever reads the model will ask.

**2. Look at the low case first**
Switch the scenario to 1 (Low). Is the business still viable? {% if tier == "Full" %}Check the cash flow for the lowest cash point and when it happens. {% endif %}If the low case doesn't work, that's what to fix before anyone else sees the file.

**3. Send the Excel file, not a screenshot**
A lender, investor or adviser who can click a cell and see the formula trusts the number more. The Checks sheet travels with the file, so they can see the statements tie.

{% if tier == "Light" %}**Need cash flow and a balance sheet?** Lenders usually ask for them. You can upgrade to Full by paying the difference: just reply to this email.

{% endif %}Questions about the file? Reply here and you'll get an answer from a person.

StartupModel
{{ support_email }}

[Don't send me tips like this]({{ unsubscribe_url }})
