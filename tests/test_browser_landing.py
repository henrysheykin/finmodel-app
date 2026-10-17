"""Playwright: the landing page's live spreadsheet and the "How it works" demo brief."""

import pytest

from tests.test_browser_wizard import live_server, no_horizontal_scroll, page  # noqa: F401  (fixtures)

pytestmark = pytest.mark.browser


def test_sheet_cells_case_switch_and_tabs(page, live_server):  # noqa: F811
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(f"{live_server}/")
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    assert page.inner_text("#xl-name") == "B10"

    page.click('#xl-grid [data-a="C12"]')
    assert page.inner_text("#xl-name") == "C12"
    assert page.inner_text("#xl-f") == "='P&L'!C21"

    page.keyboard.press("ArrowUp")
    assert page.inner_text("#xl-name") == "C11"

    base_ebitda = page.inner_text('#xl-grid [data-a="B10"]')
    page.select_option("#xl-case", "1")
    assert page.inner_text('#xl-grid [data-a="C4"]') == "Low"
    assert page.inner_text('#xl-grid [data-a="B10"]') != base_ebitda

    page.click('#xl [data-tab="chk"]')
    funding = page.locator('#xl-grid [data-a="B14"]')
    assert funding.inner_text() == "WARN" and "res--warn" in funding.get_attribute("class")
    page.click('#xl [data-tab="inp"]')
    assert page.inner_text("#xl-name") == "E7"
    assert page.inner_text("#xl-f").startswith("=CHOOSE(Dashboard!$B$4,")
    assert not errors


def test_demo_brief_hands_answers_to_the_real_brief(page, live_server):  # noqa: F811
    page.goto(f"{live_server}/")
    assert no_horizontal_scroll(page)
    page.locator("#how").scroll_into_view_if_needed()
    nxt = page.locator("#demo-next")
    assert nxt.is_disabled()
    page.get_by_role("button", name="Restaurant / cafe").click()
    nxt.click()
    page.get_by_role("button", name="Business valuation (DCF)").click()
    nxt.click()
    page.get_by_role("button", name="5 years, annual").click()
    nxt.click()
    page.locator("#demo-go").click()
    page.wait_for_url("**/start?*")
    assert page.get_by_label("Restaurant / cafe").is_checked()
    assert page.get_by_label("Business valuation (DCF)").is_checked()
    assert page.get_by_label("5 years").is_checked()
    assert page.get_by_label("Annual").is_checked()
