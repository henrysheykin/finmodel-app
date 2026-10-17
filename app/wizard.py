"""Wizard content: choices, plans and the "key numbers" step.

Key numbers are a short list of drivers per template that a customer can type in; every
field starts at the stage default. Percent drivers are shown and typed as percentages
(3.5 means 3.5%) and stored as fractions.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.briefing import TEMPLATE_FOR, Answers, PrefillBriefSource
from engine.templates import TEMPLATES, get_template, planned

#: wizard choices from the template catalog (ADR-009): live templates in their order, then announced ones
BUSINESS_TYPES = [(bt, t.title) for t in TEMPLATES.values() for bt in t.business_types] + [
    (bt, f"{label} (coming soon)") for bt, label in planned().items()
]
GOALS = [
    ("revenue_profit", "Revenue and profit projections"),
    ("startup_breakeven", "Startup costs and break-even"),
    ("dcf_valuation", "Business valuation (DCF)"),
    ("investor_pitch", "Investor-ready pitch model"),
    ("other", "Something else"),
]
STAGES = [
    ("planning", "Planning — not trading yet"),
    ("early", "Early — first year"),
    ("growing", "Growing — 1 to 3 years"),
    ("established", "Established — 3+ years"),
]
HORIZONS = [(1, "1 year"), (3, "3 years"), (5, "5 years")]
GRANULARITIES = [("monthly", "Monthly"), ("annual", "Annual")]
PLANS = {
    "light": {"name": "Light", "lines": ["Inputs, P&L and Checks", "Low, base and high cases"]},
    "full": {
        "name": "Full",
        "lines": ["Everything in Light", "Cash flow, balance sheet and headcount", "Dashboard with the case switch"],
    },
}

KEY_NUMBERS: dict[str, list[str]] = {key: list(t.key_numbers) for key, t in TEMPLATES.items()}


@dataclass(frozen=True)
class KeyNumber:
    key: str
    label: str
    unit: str
    percent: bool
    integer: bool
    default: float  # as shown to the customer (percent already × 100)
    min: float
    max: float

    def to_dict(self) -> dict:
        return self.__dict__.copy()


def available(business_type: str) -> bool:
    return business_type in TEMPLATE_FOR


def key_numbers(business_type: str, stage: str) -> list[KeyNumber]:
    tkey = TEMPLATE_FOR.get(business_type)
    if tkey is None:
        return []
    tpl = get_template(tkey)
    brief = PrefillBriefSource().build_brief(Answers(business_type=business_type, stage=stage))
    specs = {s.key: s for s in tpl.all_specs(brief.roles)}
    out = []
    for k in KEY_NUMBERS[tkey]:
        s, base = specs[k], brief.driver(k).base
        pct = s.fmt == "pct"
        f = 100 if pct else 1
        out.append(
            KeyNumber(k, s.label, "%" if pct else s.unit, pct, s.integer, round(base * f, 4), s.min * f, s.max * f)
        )
    return out


def parse_key_numbers(business_type: str, stage: str, form: dict[str, str]) -> dict[str, float]:
    """Read ``kn_<key>`` form fields; blank means 'keep the default'. Raises ValueError on bad input."""
    out: dict[str, float] = {}
    for kn in key_numbers(business_type, stage):
        raw = (form.get(f"kn_{kn.key}") or "").strip().replace(",", "").replace("$", "").replace("%", "")
        if not raw:
            continue
        try:
            v = float(raw)
        except ValueError:
            raise ValueError(f"{kn.label}: enter a number") from None
        if not (kn.min <= v <= kn.max):
            raise ValueError(f"{kn.label}: must be between {kn.min:g} and {kn.max:g}")
        if kn.integer and v != int(v):
            raise ValueError(f"{kn.label}: enter a whole number")
        if v == kn.default:
            continue
        out[kn.key] = v / 100 if kn.percent else v
    return out
