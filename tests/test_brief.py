import copy
import json

import pytest
from pydantic import ValidationError

from engine.brief import Brief, BriefError
from engine.templates import get_template

from .conftest import CAFE_BRIEF


def raw() -> dict:
    return json.loads(CAFE_BRIEF.read_text(encoding="utf-8"))


def set_driver(d: dict, key: str, **vals) -> dict:
    d = copy.deepcopy(d)
    for drv in d["drivers"]:
        if drv["key"] == key:
            drv.update(vals)
    return d


def check(d: dict) -> None:
    b = Brief.model_validate(d)
    get_template(b.template).validate(b)


def test_cafe_brief_is_valid():
    check(raw())


@pytest.mark.parametrize(
    "field,value",
    [
        ("horizon_years", 2),
        ("granularity", "weekly"),
        ("tier", "pro"),
        ("default_scenario", 4),
        ("currency", "EUR"),
        ("stage", "unicorn"),
    ],
)
def test_enum_fields_rejected(field, value):
    with pytest.raises(ValidationError):
        Brief.model_validate({**raw(), field: value})


def test_extra_fields_forbidden():
    with pytest.raises(ValidationError):
        Brief.model_validate({**raw(), "formula_override": "=1/0"})
    d = raw()
    d["drivers"][0]["fmt"] = "pct"  # formats belong to the template, not the brief
    with pytest.raises(ValidationError):
        Brief.model_validate(d)


def test_duplicate_and_bad_keys():
    d = raw()
    d["drivers"].append(dict(d["drivers"][0]))
    with pytest.raises(ValidationError, match="duplicate"):
        Brief.model_validate(d)
    d = raw()
    d["drivers"][0]["key"] = "Bad Key"
    with pytest.raises(ValidationError):
        Brief.model_validate(d)


def test_missing_and_unknown_drivers():
    d = raw()
    d["drivers"] = [x for x in d["drivers"] if x["key"] != "ticket"]
    with pytest.raises(BriefError, match="missing drivers: \\['ticket'\\]"):
        check(d)
    d = raw()
    d["drivers"].append({"key": "mystery", "low": 1, "base": 1, "high": 1})
    with pytest.raises(BriefError, match="unknown drivers"):
        check(d)


def test_bounds_and_integers():
    with pytest.raises(BriefError, match="cogs_pct.high=1.5 outside"):
        check(set_driver(raw(), "cogs_pct", high=1.5, base=1.6, low=1.7))
    with pytest.raises(BriefError, match="whole number"):
        check(set_driver(raw(), "loan_term_years", base=5.5))
    with pytest.raises(BriefError, match="outside"):
        check(set_driver(raw(), "tax_rate", low=-0.1))


def test_scenario_ordering():
    with pytest.raises(BriefError, match="ticket: needs Low <= Base <= High"):
        check(set_driver(raw(), "ticket", low=8))
    with pytest.raises(BriefError, match="cogs_pct: needs Low >= Base >= High"):
        check(set_driver(raw(), "cogs_pct", low=0.2))


def test_roles_need_their_drivers_and_template_needs_a_role():
    d = raw()
    d["roles"].append({"key": "manager", "title": "Manager"})
    with pytest.raises(BriefError, match="manager_fte"):
        check(d)
    d = raw()
    d["roles"] = []
    d["drivers"] = [
        x for x in d["drivers"] if not x["key"].startswith("staff_") and x["key"] not in ("payroll_tax", "wage_g")
    ]
    with pytest.raises(BriefError, match="headcount role"):
        check(d)


def test_values_and_with_options(cafe_brief):
    assert cafe_brief.values(1)["ticket"] == 5.5
    assert cafe_brief.values(3)["ticket"] == 7.5
    b = cafe_brief.with_options(tier="light", granularity="annual", horizon_years=5)
    assert (b.tier, b.granularity, b.horizon_years) == ("light", "annual", 5)
    with pytest.raises(ValidationError):
        cafe_brief.with_options(horizon_years=4)


def test_unknown_template():
    with pytest.raises(KeyError, match="unknown template"):
        get_template("spaceport")
