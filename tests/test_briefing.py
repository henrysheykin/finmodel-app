"""Wizard answers → brief (prefill path, no LLM)."""

import pytest
from pydantic import ValidationError

from app.briefing import TEMPLATE_FOR, Answers, PrefillBriefSource
from engine.brief import BriefError

SRC = PrefillBriefSource()


@pytest.mark.parametrize("btype", sorted(TEMPLATE_FOR))
def test_every_supported_type_builds_a_valid_brief(btype):
    b = SRC.build_brief(Answers(business_type=btype, stage="early", tier="light", horizon_years=5))
    assert b.template == TEMPLATE_FOR[btype]
    assert (b.tier, b.horizon_years, b.business_type) == ("light", 5, btype)


def test_key_numbers_set_base_and_keep_spread():
    default = SRC.build_brief(Answers(business_type="saas", stage="early"))
    d0 = default.driver("arpa")
    b = SRC.build_brief(Answers(business_type="saas", stage="early", key_numbers={"arpa": 200, "equity": 1e6}))
    d = b.driver("arpa")
    assert d.base == 200
    assert d.low == pytest.approx(d0.low / d0.base * 200) and d.high == pytest.approx(d0.high / d0.base * 200)
    assert b.driver("equity").base == 1e6 and "Your number" in d.note


def test_zero_default_takes_value_in_all_scenarios():
    b = SRC.build_brief(Answers(business_type="saas", stage="planning", key_numbers={"start_customers": 12}))
    d = b.driver("start_customers")
    assert (d.low, d.base, d.high) == (12, 12, 12)


def test_business_name_goes_into_model_name():
    b = SRC.build_brief(Answers(business_type="retail_ecommerce", business_name="Blue Shop"))
    assert b.model_name == "Blue Shop — financial model"


def test_rejections():
    with pytest.raises(BriefError, match="not available"):
        SRC.build_brief(Answers(business_type="real_estate"))
    with pytest.raises(BriefError, match="unknown key numbers"):
        SRC.build_brief(Answers(business_type="saas", key_numbers={"bogus": 1}))
    with pytest.raises(BriefError):  # out of the template's bounds
        SRC.build_brief(Answers(business_type="saas", key_numbers={"churn_m": 5}))
    with pytest.raises(ValidationError):
        Answers(business_type="saas", horizon_years=4)
