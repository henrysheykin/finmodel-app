"""L1 legal texts: content/legal/*.md, held back while placeholders remain; retention purge promised in privacy.md."""

import re
from datetime import timedelta
from pathlib import Path

from sqlalchemy import func, select

from app import accounts, golive, landing
from app.briefing import Answers
from app.db import session_scope, utcnow
from app.models import Customer, CustomerSession, LoginToken, Order, OrderEvent
from app.orders import create_order, mark_paid
from app.retention import purge
from tests.conftest import ANSWERS
from tests.test_golive import LIVE, email_dir

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("privacy", "terms", "refunds")
LEGAL = ROOT / "content" / "legal"


def text(page):
    return (ROOT / "content" / "legal" / f"{page}.md").read_text("utf-8")


def test_texts_have_no_placeholders_and_name_the_operator():
    for p in PAGES:
        assert not landing.LEGAL_PLACEHOLDER.search(text(p)), p
        assert "StartupModels LLC" in text(p) and "Wyoming" in text(p), p
    assert "Spain" not in text("terms") + text("privacy")


def test_page_with_placeholders_is_not_published(client, tmp_path, monkeypatch):
    monkeypatch.setattr(landing, "LEGAL", tmp_path)
    (tmp_path / "terms.md").write_text("Seller: [OPERATOR_NAME].\n", encoding="utf-8")
    r = client.get("/terms")
    assert "being prepared" in r.text and "noindex" in r.text and "OPERATOR_NAME" not in r.text
    assert "/terms" not in client.get("/sitemap.xml").text


def test_texts_render_and_are_indexed(client):
    for p in PAGES:
        r = client.get(f"/{p}")
        assert r.status_code == 200 and "being prepared" not in r.text and "noindex" not in r.text
        assert "StartupModels LLC" in r.text and "mailto:support@startup-model.com" in r.text
        assert not re.search(r"\[[A-Z_]{4,}\]", r.text)
    sitemap = client.get("/sitemap.xml").text
    assert all(f"/{p}" in sitemap for p in PAGES)


def test_golive_legal_check_follows_placeholders(tmp_path):
    d = tmp_path / "legal"
    d.mkdir()
    for p in PAGES:
        (d / f"{p}.md").write_text(text(p), encoding="utf-8")
    items = {i.key: i for i in golive.readiness(LIVE, d, email_dir(tmp_path))}
    assert items["legal"].level == golive.OK
    (d / "terms.md").write_text("Seller: [OPERATOR_NAME]\n", encoding="utf-8")
    items = {i.key: i for i in golive.readiness(LIVE, d, email_dir(tmp_path / "e"))}
    assert items["legal"].level == golive.FAIL and "PLACEHOLDERS" in items["legal"].message


def test_texts_match_what_the_site_promises():
    refunds, terms, privacy = text("refunds"), text("terms"), text("privacy")
    assert "within 7 days of payment" in refunds and "full price" in refunds  # landing: "Full refund within 7 days"
    assert "sm_session" in privacy and "sm_admin" in privacy  # the only cookies the app sets
    for vendor in ("Stripe", "Railway", "Cloudflare", "Resend"):
        assert vendor in privacy
    assert "15 minutes" in privacy and "30 days" in privacy  # accounts.LOGIN_TTL / SESSION_TTL
    assert accounts.SESSION_TTL == timedelta(days=30)
    assert "$" not in terms  # prices come from config and the landing, never hard-coded here
    for t in (refunds, terms, privacy):
        assert "FinModelsLab" not in t and "Ledgerline" not in t


def _order(services, email, created, paid=False):
    with session_scope(services.sessions) as s:
        brief = services.briefs.build_brief(Answers(**ANSWERS))
        o = create_order(s, services.cfg, email, brief, ANSWERS)
        o.created_at = created
        if paid:
            mark_paid(s, services.cfg, o.id, f"cs_{o.id}")
        return o.id


def test_purge_removes_only_expired_unpaid_orders_and_old_sign_in_records(services):
    now = utcnow()
    old, recent = now - timedelta(days=400), now - timedelta(days=30)
    old_unpaid = _order(services, "a@b.co", old)
    old_paid = _order(services, "c@d.co", old, paid=True)
    new_unpaid = _order(services, "e@f.co", recent)
    with session_scope(services.sessions) as s:
        s.add(LoginToken(email="a@b.co", token_hash="1" * 64, created_at=old, expires_at=old))
        s.add(LoginToken(email="a@b.co", token_hash="2" * 64, created_at=recent, expires_at=recent))
        cust = Customer(email="a@b.co")
        s.add(cust)
        s.flush()
        s.add(CustomerSession(customer_id=cust.id, token_hash="3" * 64, expires_at=old))
        s.add(CustomerSession(customer_id=cust.id, token_hash="4" * 64, expires_at=now + timedelta(days=5)))
    with session_scope(services.sessions) as s:
        assert purge(s, now) == {"unpaid_orders": 1, "login_tokens": 1, "sessions": 1}
    with session_scope(services.sessions) as s:
        assert s.get(Order, old_unpaid) is None
        assert s.get(Order, old_paid) is not None and s.get(Order, new_unpaid) is not None
        assert s.scalar(select(func.count()).where(OrderEvent.order_id == old_unpaid)) == 0
        assert s.scalar(select(func.count()).select_from(LoginToken)) == 1
        assert s.scalar(select(func.count()).select_from(CustomerSession)) == 1
    with session_scope(services.sessions) as s:
        assert purge(s, now) == {"unpaid_orders": 0, "login_tokens": 0, "sessions": 0}


def test_start_script_runs_purge_after_migrations():
    script = (ROOT / "deploy" / "start.sh").read_text("utf-8")
    assert "python -m app.manage purge || true" in script
    assert script.index("manage migrate") < script.index("manage purge") < script.index("worker.main")


def test_manage_purge_command(tmp_path, monkeypatch, capsys):
    from app.manage import main as manage_main

    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path}/ops.db")
    assert manage_main(["migrate"]) == 0
    assert manage_main(["purge"]) == 0
    assert "retention purge: unpaid_orders=0, login_tokens=0, sessions=0" in capsys.readouterr().out
