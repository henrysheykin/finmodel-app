"""Playwright (E34): the calculator pages in Chromium: fill the inputs, read the results, no errors, no shifts."""

import pytest

from app import calculators as C
from app.calc_expr import format_value
from tests.test_browser_wizard import live_server, no_horizontal_scroll, page  # noqa: F401  (fixtures)

pytestmark = pytest.mark.browser

CALCS = list(C.calculators().values())
IDS = [c.name for c in CALCS]


def _open(page, live_server, calc, width=1280):  # noqa: F811
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.set_viewport_size({"width": width, "height": 900})
    page.goto(f"{live_server}{calc.slug}")
    page.wait_for_selector(".calc.is-live")
    page.evaluate("document.fonts.ready")
    return errors


def _fill(page, inputs):  # noqa: F811
    for key, value in inputs.items():
        page.fill(f"#in-{key}", str(value))


def _box(page, selector):  # noqa: F811
    """Top and height on the page (not the viewport, which moves when a field scrolls into view)."""
    return page.locator(selector).first.evaluate(
        "el => { const r = el.getBoundingClientRect(); return {y: r.top + window.scrollY, height: r.height}; }"
    )


def _shown(page, calc):  # noqa: F811
    return {o.key: page.inner_text(f'[data-out="{o.key}"]') for o in calc.outputs}


@pytest.mark.parametrize("calc", CALCS, ids=IDS)
def test_examples_in_the_browser_match_python(page, live_server, calc):  # noqa: F811
    errors = _open(page, live_server, calc)
    for ex in calc.examples:
        _fill(page, ex.inputs)
        want = calc.compute(ex.inputs)
        assert _shown(page, calc) == {o.key: format_value(want[o.key], o.format) for o in calc.outputs}, ex.name
        # and the numbers the example promises, formatted the way the page shows them
        for key, value in ex.expect.items():
            assert page.inner_text(f'[data-out="{key}"]') == format_value(value, calc.output(key).format), key
        if calc.table:
            rows = calc.sweep(ex.inputs)
            for i, (sv, outs) in enumerate(rows):
                tr = page.locator(f'tr[data-row="{i}"]')
                assert tr.locator("[data-sweep]").inner_text() == format_value(sv, calc.input(calc.table.input).format)
                for key in calc.table.outputs:
                    assert tr.locator(f'[data-cell="{key}"]').inner_text() == format_value(
                        outs[key], calc.output(key).format
                    )
    assert not errors, errors


@pytest.mark.parametrize("calc", CALCS, ids=IDS)
def test_defaults_show_on_load_and_nothing_overflows_on_a_phone(page, live_server, calc):  # noqa: F811
    errors = _open(page, live_server, calc, width=360)
    res = calc.compute()
    assert _shown(page, calc) == {o.key: format_value(res[o.key], o.format) for o in calc.outputs}
    assert no_horizontal_scroll(page)
    # stacked on a phone: the inputs come first, the results below them
    box_in, box_out = page.locator(".calc__in").bounding_box(), page.locator(".calc__out").bounding_box()
    assert box_out["y"] >= box_in["y"] + box_in["height"] - 1 and abs(box_in["x"] - box_out["x"]) < 2
    assert not errors, errors


@pytest.mark.parametrize("calc", CALCS, ids=IDS)
def test_side_by_side_on_desktop(page, live_server, calc):  # noqa: F811
    _open(page, live_server, calc, width=1280)
    box_in, box_out = page.locator(".calc__in").bounding_box(), page.locator(".calc__out").bounding_box()
    assert box_out["x"] > box_in["x"] + box_in["width"] - 1 and abs(box_out["y"] - box_in["y"]) < 40


@pytest.mark.parametrize("calc", CALCS, ids=IDS)
def test_results_panel_causes_no_layout_shift(page, live_server, calc):  # noqa: F811
    _open(page, live_server, calc, width=360)
    page.wait_for_load_state("networkidle")
    page.evaluate(
        """() => { window.__cls = 0; new PerformanceObserver((l) => {
        for (const e of l.getEntries()) window.__cls += e.value; })
        .observe({type: 'layout-shift', buffered: false}); }"""
    )
    marks = ".calc__out", ".calc__table", ".calc-prose:last-of-type", ".promo"
    before = [_box(page, m) for m in marks if page.locator(m).count()]
    for ex in calc.examples:
        _fill(page, ex.inputs)
        page.wait_for_timeout(30)
    _fill(page, {calc.inputs[0].key: ""})  # an invalid entry shows a message in the space reserved for the hint
    page.wait_for_timeout(50)
    _fill(page, {i.key: i.default for i in calc.inputs})
    page.wait_for_timeout(600)
    after = [_box(page, m) for m in marks if page.locator(m).count()]
    assert page.evaluate("window.__cls") < 0.001
    assert [b["y"] for b in before] == [b["y"] for b in after] and [b["height"] for b in before] == [
        b["height"] for b in after
    ]


def test_invalid_and_out_of_range_inputs(page, live_server):  # noqa: F811
    calc = C.calculators()["/calculators/cafe-menu-price"]
    errors = _open(page, live_server, calc)
    page.fill("#in-cost", "")
    assert page.inner_text('[data-out="price"]') == "—" and page.get_attribute("#in-cost", "aria-invalid") == "true"
    assert "Enter a number" in page.inner_text('[data-msg="cost"]')
    page.fill("#in-cost", "1.4")
    assert (
        page.inner_text('[data-out="price"]') == "$4.75" and page.get_attribute("#in-cost", "aria-invalid") == "false"
    )
    assert page.inner_text('[data-msg="cost"]') == calc.input("cost").hint
    page.fill("#in-target_pct", "500")  # above the maximum of 95: calculated with 95
    assert "Calculated with 95.0%" in page.inner_text('[data-msg="target_pct"]')
    assert page.inner_text('[data-out="price_exact"]') == format_value(
        calc.compute({"target_pct": 95})["price_exact"], "money2"
    )
    page.fill("#in-cost", "0")
    assert page.inner_text('[data-out="actual_pct"]') == "—"  # division by zero shows a dash
    assert not errors, errors


def test_hero_result_is_announced_politely(page, live_server):  # noqa: F811
    calc = C.calculators()["/calculators/cafe-break-even-covers"]
    _open(page, live_server, calc)
    page.fill("#in-fixed", "30000")
    page.wait_for_timeout(800)  # the spoken summary is debounced
    assert page.inner_text("[data-live]").startswith("Customers needed per day: ")
    assert page.get_attribute("[data-live]", "aria-live") == "polite"
