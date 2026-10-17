"""Static files are linked with a content hash so a deploy is never hidden behind a cached stylesheet."""

import re

import pytest

from app.web import STATIC_DIR, asset

PAGES = ["/", "/start"]


@pytest.mark.parametrize("path", PAGES)
def test_pages_link_css_and_js_with_a_content_hash(client, path):
    html = client.get(path).text
    links = re.findall(r'(?:href|src)="(/static/[^"?]+\.(?:css|js)(?:\?[^"]*)?)"', html)
    assert links, "page links no stylesheet or script"
    for url in links:
        assert re.search(r"\?v=[0-9a-f]{10}$", url), f"unversioned asset {url}"
        assert client.get(url).status_code == 200


def test_hash_changes_with_the_file_contents(tmp_path, monkeypatch):
    import app.web as web

    (tmp_path / "x.css").write_text("a{}")
    monkeypatch.setattr(web, "STATIC_DIR", tmp_path)
    web.asset.cache_clear()
    first = web.asset("x.css")
    (tmp_path / "x.css").write_text("b{}")
    web.asset.cache_clear()
    assert web.asset("x.css") != first
    web.asset.cache_clear()


def test_versioned_assets_are_immutable_and_plain_ones_revalidate(client):
    url = asset("site.css")
    assert (STATIC_DIR / "site.css").exists()
    assert "immutable" in client.get(url).headers["cache-control"]
    assert "must-revalidate" in client.get("/static/site.css").headers["cache-control"]
