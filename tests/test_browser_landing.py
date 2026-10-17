"""Playwright: the landing page's spreadsheet window and the "How it works" demo brief."""

import re

import pytest

from app import xlview
from tests.test_browser_wizard import live_server, no_horizontal_scroll, page  # noqa: F401  (fixtures)

pytestmark = pytest.mark.browser


def _open(page, live_server):  # noqa: F811
    page.set_viewport_size({"width": 1440, "height": 900})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"{live_server}/")
    page.wait_for_selector("#xl.is-live")
    return errors


def test_browser_renders_the_same_cells_as_the_server(page, live_server):  # noqa: F811
    """landing.js and app/xlview.py format every Dashboard cell identically."""
    _open(page, live_server)
    sh = xlview.sheet("Dashboard")
    shown = page.evaluate("Array.from(document.querySelectorAll('#xl-grid .c')).map(n => [n.id, n.textContent])")
    shown = dict(shown)
    for a in sh["cells"]:
        assert shown[f"xc-{a}"] == xlview.cell_view(sh, a)["text"], a


def test_select_edit_and_trace_precedents(page, live_server):  # noqa: F811
    errors = _open(page, live_server)
    assert page.input_value("#xl-name") == "B4"
    assert page.locator("#xl-tip").is_visible()  # the cell's input message, as in the file
    page.click("#xc-C12")
    assert page.input_value("#xl-name") == "C12" and page.inner_text("#xl-f") == "='P&L'!C21"
    assert page.inner_text("#xl-nf") == "Custom"
    page.keyboard.press("ArrowUp")
    assert page.input_value("#xl-name") == "C11"
    page.keyboard.press("F2")
    assert page.inner_text("#xl-mode") == "Edit" and page.locator("#xc-C11 .xed").is_visible()
    page.keyboard.press("Escape")
    page.click("#xl-f")  # clicking the formula bar edits too; a cross-sheet reference is a link
    page.locator("#xl-f a[data-go]").first.click()
    assert page.get_by_role("tab", name="P&L").get_attribute("aria-selected") == "true"
    assert page.input_value("#xl-name") == "C15"
    page.get_by_role("tab", name="Checks").click()
    page.click("#xc-B16")
    page.keyboard.press("F2")  # COUNTIF(B4:B14,...) on the same sheet: the range is outlined
    assert "inset" in (page.locator("#xc-B10").get_attribute("style") or "")
    assert not errors


def test_range_sum_case_switch_and_sheets(page, live_server):  # noqa: F811
    errors = _open(page, live_server)
    page.click("#xc-B8")
    page.click("#xc-D8", modifiers=["Shift"])
    stats = page.inner_text("#xl-stats")
    assert "Count: 3" in stats and "Sum: $1,174,865" in stats, stats
    base = page.inner_text("#xc-B10")
    page.click("#xc-B4")
    page.click("#xl-dv")
    page.click("#xl-list li[data-v='1']")
    assert page.inner_text("#xc-C4") == "Low" and page.inner_text("#xc-B10") != base
    page.get_by_role("tab", name="Checks").click()
    assert page.inner_text("#xc-B14") == "WARN"
    page.get_by_role("tab", name="Monthly").click()
    page.click("#xc-C12")
    page.keyboard.press("Control+ArrowRight")  # jumps to the last month, like Excel
    assert page.input_value("#xl-name") == "AL12"
    a12, al12 = page.locator("#xc-A12").bounding_box(), page.locator("#xc-AL12").bounding_box()
    scroller = page.locator("#xl-scroll").bounding_box()
    assert scroller["x"] <= a12["x"] < scroller["x"] + 60  # column A is frozen: still on screen at the left
    assert al12["x"] + al12["width"] <= scroller["x"] + scroller["width"] + 1  # and the last month scrolled into view
    page.fill("#xl-name", "Inputs!E7")
    page.press("#xl-name", "Enter")
    assert page.get_by_role("tab", name="Inputs").get_attribute("aria-selected") == "true"
    assert page.inner_text("#xl-f").startswith("=CHOOSE(Dashboard!$B$4,")
    assert re.fullmatch(r"\d+", page.inner_text("#xc-E7"))
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
