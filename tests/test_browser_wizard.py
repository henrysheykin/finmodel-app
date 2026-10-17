"""Playwright: complete the wizard in Chromium and land on checkout with an order awaiting payment."""

import os
import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn

from app.db import session_scope
from app.main import create_app
from app.models import Order
from app.orders import brief_of

pytestmark = pytest.mark.browser
sync_api = pytest.importorskip("playwright.sync_api")


def _chromium_path() -> str | None:
    p = os.environ.get("PLAYWRIGHT_CHROMIUM_PATH") or "/opt/pw-browsers/chromium"
    return p if Path(p).exists() else None


@pytest.fixture
def live_server(services):
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(create_app(services), host="127.0.0.1", port=port, log_level="warning"))
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    t.join(5)


@pytest.fixture
def page():
    with sync_api.sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(executable_path=_chromium_path())
        except Exception as exc:  # browser missing locally
            if os.environ.get("REQUIRE_BROWSER") == "1":
                raise
            pytest.skip(f"chromium not available: {exc}")
        ctx = browser.new_context(viewport={"width": 360, "height": 740})
        yield ctx.new_page()
        browser.close()


def no_horizontal_scroll(page) -> bool:
    return page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")


def test_complete_wizard_on_a_phone(page, live_server, services):
    page.goto(f"{live_server}/start?plan=full")
    assert no_horizontal_scroll(page)
    nxt = page.get_by_role("button", name="Next")

    nxt.click()  # nothing chosen yet
    assert page.get_by_role("alert").inner_text().startswith("Choose one option")
    page.get_by_label("SaaS / software").check()
    page.get_by_label("Business name").fill("Rocket Notes")
    nxt.click()
    assert page.get_by_role("heading", name="2. What the model is for").is_visible()
    page.get_by_label("Investor-ready pitch model").check()
    nxt.click()
    page.get_by_label("Early — first year").check()
    nxt.click()
    page.get_by_label("5 years").check()
    page.get_by_label("Annual").check()
    nxt.click()

    arpa = page.get_by_label("Average MRR per new customer (ARPA)")
    arpa.wait_for()
    assert arpa.input_value() == "99"
    arpa.fill("150")
    churn = page.get_by_label("Customer churn per month")
    assert churn.input_value() == "3"
    assert no_horizontal_scroll(page)
    nxt.click()

    page.get_by_role("radio", name="Light $149", exact=True).check()
    assert page.locator('[data-sum="price"]').inner_text() == "$149"
    assert page.locator('[data-sum="business_type"]').inner_text() == "Rocket Notes"
    nxt.click()

    page.get_by_label("Email").fill("founder@example.com")
    assert no_horizontal_scroll(page)
    page.get_by_role("button", name="Continue to payment").click()

    page.wait_for_url("**/checkout/*")
    assert page.get_by_role("heading", name="Review and pay").is_visible()
    assert page.get_by_role("button", name="Pay $149").is_visible()
    assert no_horizontal_scroll(page)
    oid = page.url.rsplit("/", 1)[1]
    with session_scope(services.sessions) as s:
        o = s.get(Order, oid)
        assert (o.status, o.tier, o.email) == ("awaiting_payment", "light", "founder@example.com")
        b = brief_of(o)
        assert b.driver("arpa").base == 150 and (b.horizon_years, b.granularity) == (5, "annual")


def test_back_button_and_keyboard(page, live_server):
    page.goto(f"{live_server}/start")
    page.get_by_label("Restaurant / cafe").check()
    page.keyboard.press("Tab")
    page.get_by_role("button", name="Next").click()
    focused = page.evaluate("document.activeElement.textContent")
    assert focused == "2. What the model is for"  # focus moves to the new step's heading
    page.get_by_role("button", name="Back").click()
    assert page.get_by_label("Restaurant / cafe").is_checked()


def test_unavailable_type_is_blocked(page, live_server):
    page.goto(f"{live_server}/start")
    page.get_by_label("Real estate (coming soon)").check()
    page.get_by_role("button", name="Next").click()
    assert "not available yet" in page.get_by_role("alert").inner_text()
