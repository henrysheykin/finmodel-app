"""Template registry."""

from engine.templates.base import Template
from engine.templates.cafe import CafeTemplate
from engine.templates.retail import RetailTemplate
from engine.templates.saas import SaasTemplate

TEMPLATES: dict[str, Template] = {t.key: t for t in (CafeTemplate(), SaasTemplate(), RetailTemplate())}


def get_template(key: str) -> Template:
    try:
        return TEMPLATES[key]
    except KeyError:
        raise KeyError(f"unknown template {key!r}; known: {sorted(TEMPLATES)}") from None
