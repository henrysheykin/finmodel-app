"""ADR-009: the template catalog is the single list of industries.

Every registered template is checked here automatically, so a new industry needs no edits to the
wizard, the brief schema or the landing page — only its own file, tests, sample and memo.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from app import landing, wizard
from app.briefing import TEMPLATE_FOR, Answers, PrefillBriefSource
from engine import templates
from engine.brief import Brief
from engine.templates import PLANNED, TEMPLATES, known_business_types, planned, template_for_business_type

ROOT = Path(__file__).resolve().parents[1]
STAGES = ["planning", "early", "growing", "established"]


def test_every_template_module_is_discovered():
    modules = {p.stem for p in (ROOT / "engine" / "templates").glob("*.py") if p.stem not in ("__init__", "base")}
    assert {type(t).__module__.rsplit(".", 1)[1] for t in TEMPLATES.values()} == modules


def test_catalog_fields_are_complete():
    for key, t in TEMPLATES.items():
        assert t.key == key and t.title and t.business_types, key
        assert t.key_numbers, f"{key}: no wizard key numbers"
        assert t.sample_stage in STAGES, key


@pytest.mark.parametrize("key", sorted(TEMPLATES))
def test_key_numbers_exist_in_the_template(key):
    t = TEMPLATES[key]
    brief = t.default_brief("growing")
    specs = {s.key for s in t.all_specs(brief.roles)}
    missing = [k for k in t.key_numbers if k not in specs]
    assert not missing, f"{key}: key numbers not in driver specs: {missing}"


@pytest.mark.parametrize("key", sorted(TEMPLATES))
@pytest.mark.parametrize("stage", STAGES)
def test_every_stage_has_defaults_that_validate(key, stage):
    t = TEMPLATES[key]
    brief = t.default_brief(stage)
    assert brief.template == key and brief.business_type in t.business_types
    t.validate(brief)


def test_wizard_lists_live_templates_then_planned():
    types = [bt for bt, _ in wizard.BUSINESS_TYPES]
    live = list(template_for_business_type())
    assert types[: len(live)] == live
    assert types[len(live) :] == list(planned())
    labels = dict(wizard.BUSINESS_TYPES)
    for bt in planned():
        assert labels[bt].endswith("(coming soon)") and not wizard.available(bt)
    for bt in live:
        assert wizard.available(bt) and "coming soon" not in labels[bt]
    assert set(wizard.KEY_NUMBERS) == set(TEMPLATES)


def test_briefing_map_and_prefill_cover_every_business_type():
    assert TEMPLATE_FOR == template_for_business_type()
    src = PrefillBriefSource()
    for bt, key in TEMPLATE_FOR.items():
        b = src.build_brief(Answers(business_type=bt, stage="early"))
        assert b.template == key and b.stage == "early"


def test_brief_business_type_comes_from_the_catalog():
    assert {"other"} | set(PLANNED) | set(TEMPLATE_FOR) == known_business_types()
    base = TEMPLATES["saas"].default_brief("early").model_dump()
    with pytest.raises(ValidationError):
        Brief.model_validate({**base, "business_type": "spaceships"})
    Brief.model_validate({**base, "business_type": "other"})  # free-text "something else" stays valid


def test_planned_entry_disappears_once_a_template_serves_it(monkeypatch):
    monkeypatch.setitem(templates.PLANNED, "saas", "SaaS")  # served by the SaaS template
    assert "saas" not in planned()


def test_landing_samples_follow_the_catalog():
    assert set(landing.SAMPLE_FILES) == {k for k, t in TEMPLATES.items() if t.sample_title}
    for key, (fname, title, desc) in landing.SAMPLE_FILES.items():
        assert fname == f"{key}-full.xlsx" and title and desc
        assert (ROOT / "samples" / fname).is_file(), f"run: python scripts/build_samples.py {key}"


def test_duplicate_business_type_is_refused():
    class Clone(type(TEMPLATES["saas"])):
        key = "saas_clone"

    templates.check_catalog(TEMPLATES)  # the real catalog is clean
    with pytest.raises(RuntimeError, match="served by both"):
        templates.check_catalog({**TEMPLATES, "saas_clone": Clone()})
