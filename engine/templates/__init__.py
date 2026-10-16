"""Template registry."""

from engine.templates.base import Template
from engine.templates.cafe import CafeTemplate

TEMPLATES: dict[str, Template] = {t.key: t for t in (CafeTemplate(),)}


def get_template(key: str) -> Template:
    try:
        return TEMPLATES[key]
    except KeyError:
        raise KeyError(f"unknown template {key!r}; known: {sorted(TEMPLATES)}") from None
