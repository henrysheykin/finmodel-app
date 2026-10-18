"""Wizard and checkout pages, server side (no browser)."""

import re

import pytest

from app import wizard
from app.db import session_scope
from app.models import Order

FORM = {
    "business_type": "saas",
    "business_name": "Rocket Notes",
    "goal": "investor_pitch",
    "stage": "early",
    "horizon_years": "5",
    "granularity": "annual",
    "tier": "full",
    "email": "Founder@Example.com",
}


def test_start_page_renders_every_step(client):
    r = client.get("/start?plan=light")
    assert r.status_code == 200
    html = r.text
    for n in range(1, 8):
        assert f'data-step="{n}"' in html
    assert 'name="tier" value="light" checked' in html
    assert "$149" in html and "$349" in html
    assert re.search(r'<label for="email">Email</label>', html)
    for bad in ("1F3864", "2563EB", "DM Sans"):
        assert bad not in html


def test_key_numbers_api(client):
    r = client.get("/api/key-numbers", params={"business_type": "saas", "stage": "early"})
    fields = {f["key"]: f for f in r.json()["fields"]}
    assert set(fields) == set(wizard.KEY_NUMBERS["saas"])
    assert fields["churn_m"]["percent"] is True and fields["churn_m"]["default"] == 3.0
    assert client.get("/api/key-numbers", params={"business_type": "other"}).json() == {
        "available": False,
        "fields": [],
    }
    assert client.get("/api/key-numbers", params={"business_type": "saas", "stage": "x"}).status_code == 422


def test_submit_creates_order_and_redirects_to_checkout(client, services):
    r = client.post("/start", data={**FORM, "kn_arpa": "150", "kn_churn_m": "2.5"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].startswith("/checkout/")
    oid = r.headers["location"].rsplit("/", 1)[1]
    with session_scope(services.sessions) as s:
        o = s.get(Order, oid)
        assert (o.status, o.tier, o.price_cents, o.email) == ("awaiting_payment", "full", 34900, "founder@example.com")
        from app.orders import brief_of

        b = brief_of(o)
        assert b.driver("arpa").base == 150 and b.driver("churn_m").base == pytest.approx(0.025)
        assert (b.horizon_years, b.granularity, b.goal) == (5, "annual", "investor_pitch")
        assert b.model_name.startswith("Rocket Notes")
    page = client.get(r.headers["location"])
    assert page.status_code == 200
    assert "Rocket Notes" in page.text and "$349" in page.text and "5 years, annual" in page.text
    assert "f***@example.com" in page.text and "founder@example.com" not in page.text.lower()
    assert f'action="/checkout/{oid}/pay"' in page.text


def test_sample_data_ignores_key_numbers(client, services):
    r = client.post("/start", data={**FORM, "sample_data": "1", "kn_arpa": "nonsense"}, follow_redirects=False)
    assert r.status_code == 303


@pytest.mark.parametrize(
    "change,message",
    [
        ({"business_type": ""}, "Choose your business type"),
        ({"business_type": "other"}, "not available yet"),
        ({"email": "nope"}, "email address"),
        ({"kn_arpa": "abc"}, "enter a number"),
        ({"kn_churn_m": "80"}, "must be between"),
        ({"business_type": "retail_ecommerce", "kn_stores": "2.5"}, "whole number"),
        ({"horizon_years": "4"}, "could not be used"),
    ],
)
def test_submit_errors_rerender_the_form(client, services, change, message):
    r = client.post("/start", data={**FORM, **change}, follow_redirects=False)
    assert r.status_code == 422 and message in r.text
    assert 'role="alert"' in r.text
    with session_scope(services.sessions) as s:
        assert s.query(Order).count() == 0


def test_typed_values_survive_an_error(client):
    r = client.post("/start", data={**FORM, "email": "bad", "kn_arpa": "123"})
    assert 'value="123"' in r.text and 'value="Rocket Notes"' in r.text


def test_checkout_unknown_order(client):
    assert client.get("/checkout/nope").status_code == 404
    assert client.post("/checkout/nope/pay").status_code == 404


def test_static_assets(client):
    assert client.get("/static/app.css").status_code == 200
    js = client.get("/static/wizard.js")
    assert js.status_code == 200 and "loadKeyNumbers" in js.text
