"""Template registry (ADR-009).

Every module in this package that defines a concrete ``Template`` subclass with a ``key`` is registered
automatically: adding an industry is one new file here (see docs/templates/ADDING_A_TEMPLATE.md). The
wizard, the brief schema, the landing page and the order pipeline all read the catalog from here.
"""

from __future__ import annotations

import importlib
import pkgutil

from engine.templates.base import Template

#: industries shown in the wizard as "(coming soon)" before a template serves them: business type -> label
PLANNED: dict[str, str] = {
    "real_estate": "Real estate",
    "home_services": "Home services / trades",
    "fitness": "Fitness studio / gym",
}

#: business types accepted in a brief without a template (free-text "something else")
EXTRA_BUSINESS_TYPES = ("other",)


def _discover() -> dict[str, Template]:
    found: dict[str, Template] = {}
    for info in pkgutil.iter_modules(__path__):
        if info.name.startswith("_") or info.name == "base":
            continue
        module = importlib.import_module(f"{__name__}.{info.name}")
        for obj in vars(module).values():
            if (
                isinstance(obj, type)
                and issubclass(obj, Template)
                and obj.__module__ == module.__name__
                and obj.key
                and not getattr(obj, "__abstractmethods__", None)
            ):
                if obj.key in found:
                    raise RuntimeError(f"two templates use the key {obj.key!r}")
                found[obj.key] = obj()
    return dict(sorted(found.items(), key=lambda kv: (kv[1].order, kv[0])))


TEMPLATES: dict[str, Template] = _discover()


def get_template(key: str) -> Template:
    try:
        return TEMPLATES[key]
    except KeyError:
        raise KeyError(f"unknown template {key!r}; known: {sorted(TEMPLATES)}") from None


def template_for_business_type() -> dict[str, str]:
    """Wizard business type -> template key, for every registered template (in wizard order)."""
    out: dict[str, str] = {}
    for t in TEMPLATES.values():
        for bt in t.business_types:
            if bt in out:
                raise RuntimeError(f"business type {bt!r} is served by both {out[bt]!r} and {t.key!r}")
            out[bt] = t.key
    return out


def planned() -> dict[str, str]:
    """Announced industries that no registered template serves yet."""
    served = template_for_business_type()
    return {bt: label for bt, label in PLANNED.items() if bt not in served}


def known_business_types() -> set[str]:
    return set(template_for_business_type()) | set(PLANNED) | set(EXTRA_BUSINESS_TYPES)
