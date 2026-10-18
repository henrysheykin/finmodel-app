"""E12: every email template renders (text + HTML) and goes out through the console sender."""

import json
from dataclasses import replace

import httpx
import pytest

from adapters.email import ConsoleSender, EmailError, EmailMessage, PostmarkSender, ResendSender, make_sender
from app import emails
from app.config import Settings
from app.db import session_scope
from app.emails import EmailNotifier, md_to_html, render
from app.models import Order
from app.orders import mark_paid
from tests.conftest import ANSWERS
from tests.test_pipeline import make

TRANSACTIONAL = ["order-received", "model-ready", "build-failed", "refund-issued", "sign-in"]
CTX = {
    "first_name": None,
    "order_id": "AB12CD34",
    "tier": "Full",
    "template_title": "Rocket <Notes> & Co",
    "horizon_years": 3,
    "granularity": "monthly",
    "amount": "$349",
    "download_url": "https://startup-model.com/download/abc.123.sig",
    "link_expires": "24 October 2026",
    "resend_url": "https://startup-model.com/account",
    "login_url": "https://startup-model.com/login/verify?token=xyz",
    "feedback_url": "https://startup-model.com/feedback",
    "unsubscribe_url": "https://startup-model.com/unsubscribe",
    "resume_url": "https://startup-model.com/checkout/1",
    "support_email": "help@startup-model.com",
}


@pytest.mark.parametrize("name", sorted(p.stem for p in emails.CONTENT.glob("*.md") if p.stem != "README"))
def test_every_template_renders(name):
    subject, text, html, tpl = render(name, CTX)
    assert subject and "{{" not in subject + text + html and tpl.id == name
    assert "StartupModel" in text and "FinModelsLab" not in text
    assert "<script" not in html.lower()


def test_html_escapes_customer_text_and_converts_markdown():
    _, text, html, _ = render("order-received", CTX)
    assert "Rocket <Notes> & Co" in text
    assert "Rocket &lt;Notes&gt; &amp; Co" in html and "<Notes>" not in html
    assert "<li><strong>Model:</strong>" in html and "<ol>" in html
    _, text, html, _ = render("model-ready", CTX)
    assert f'href="{CTX["download_url"]}"' in html and f"Download your model (.xlsx): {CTX['download_url']}" in text
    assert "until 24 October 2026" in text and "Dashboard" in text


def test_md_subset():
    assert md_to_html("a **b**\nc\n\n- x\n- [y](https://u)") == (
        '<p>a <strong>b</strong><br>c</p>\n<ul><li>x</li><li><a href="https://u" style="color:#0F6E56">y</a></li></ul>'
    )


def test_placeholders_are_detected_but_support_email_is_not():
    assert emails.has_placeholder("[FAILED_BUILD_POLICY: decide]") and not emails.has_placeholder("[SUPPORT_EMAIL]")


# --------------------------------------------------------------------------- notifier, end to end through console
@pytest.fixture
def mail(services):
    sender = ConsoleSender()
    services.notifier = EmailNotifier(sender, services.cfg, services.sessions)
    return sender


def _paid_ready(client, services, notifier_):
    oid = client.post("/api/orders", json={"email": "a@b.co", "answers": ANSWERS}).json()["order_id"]
    with session_scope(services.sessions) as s:
        mark_paid(s, services.cfg, oid, f"cs_{oid}")
    make(services, notifier_).run_once()
    return oid


def test_model_ready_email_carries_the_signed_link(client, services, mail):
    oid = _paid_ready(client, services, services.notifier)
    (msg,) = mail.outbox
    assert msg.to == "a@b.co" and msg.subject == "Your financial model is ready to download"
    link = next(w for w in msg.text.split() if "/download/" in w)
    assert client.get(link.replace("http://testserver", "")).status_code == 200
    assert oid[:8].upper() not in msg.subject and msg.tag == "transactional"


def test_receipt_on_payment_once(client, services, mail):
    from tests.test_payments import _pay, _webhook

    oid, sid = _pay(client)
    _webhook(client, services, sid)
    _webhook(client, services, sid)
    assert [m.subject for m in mail.outbox] == ["We've got your order: your Light model is being built"]
    assert oid[:8].upper() in mail.outbox[0].text and "$149" in mail.outbox[0].text


def _fail_build(client, services):
    from worker.pipeline import BuildRejected

    def bad(brief, path):
        raise BuildRejected("challenger: mismatch")

    services.cfg = replace(services.cfg, admin_email="henry@example.com")
    services.notifier.cfg = services.cfg
    oid = client.post("/api/orders", json={"email": "a@b.co", "answers": ANSWERS}).json()["order_id"]
    with session_scope(services.sessions) as s:
        mark_paid(s, services.cfg, oid, "cs_f")
    make(services, services.notifier, check=bad).run_once()
    return oid


def test_failed_build_tells_the_customer_the_policy_and_alerts_admin(client, services, mail):
    _fail_build(client, services)
    customer = [m for m in mail.outbox if m.to == "a@b.co" and "didn't pass" in m.subject]
    assert len(customer) == 1
    assert "within 2 business days" in customer[0].text and "refund your $149 in full" in customer[0].text
    assert any(m.to == "henry@example.com" and "Build failed" in m.subject for m in mail.outbox)


def test_email_with_unfinished_copy_is_held(client, services, mail, tmp_path, monkeypatch):
    import shutil

    from app import emails

    shutil.copytree(emails.CONTENT, tmp_path / "email")
    f = tmp_path / "email" / "build-failed.md"
    f.write_text(f.read_text("utf-8").replace("**What happens next**", "[FAILED_BUILD_POLICY: decide]"), "utf-8")
    monkeypatch.setattr(emails, "CONTENT", tmp_path / "email")
    _fail_build(client, services)
    assert all(m.to == "henry@example.com" for m in mail.outbox)  # nothing with placeholder copy to the customer
    subjects = [m.subject for m in mail.outbox]
    assert any("Build failed" in x for x in subjects) and any("not sent to a@b.co" in x for x in subjects)


def test_refund_and_sign_in_emails(client, services, mail):
    oid = _paid_ready(client, services, services.notifier)
    services.notifier.refund_issued(oid)
    client.post("/login", data={"email": "a@b.co"})
    subjects = [m.subject for m in mail.outbox]
    assert "Your refund of $149 is on its way" in subjects and "Your StartupModel sign-in link" in subjects
    sign_in = next(m for m in mail.outbox if "sign-in" in m.subject)
    assert "/login/verify?token=" in sign_in.text


def test_failed_build_email_sends_once_policy_text_exists(services, mail, monkeypatch, tmp_path):
    src = (emails.CONTENT / "build-failed.md").read_text()
    body = src.split("**What happens next**")[0] + "**What happens next**\n\nWe will fix it or refund you.\n"
    (tmp_path / "build-failed.md").write_text(body)
    monkeypatch.setattr(emails, "CONTENT", tmp_path)
    with session_scope(services.sessions) as s:
        o = Order(email="c@d.co", template="saas", tier="full", price_cents=34900, brief_json="{}")
        s.add(o)
        s.flush()
        oid = o.id
    services.notifier.build_failed(oid)
    assert [m.to for m in mail.outbox] == ["c@d.co"]


# --------------------------------------------------------------------------- providers (mocked HTTP)
MSG = EmailMessage("a@b.co", "Hi", "text", "<p>html</p>", "help@x.co", "transactional")


def test_resend_payload():
    seen = {}

    def h(req):
        seen.update(req=req, body=json.loads(req.content))
        return httpx.Response(200, json={"id": "re_1"})

    s = ResendSender(
        "key",
        "StartupModel <m@x.co>",
        httpx.Client(base_url="https://api.resend.com", transport=httpx.MockTransport(h)),
    )
    assert s.send(MSG) == "re_1"
    assert seen["req"].headers["authorization"] == "Bearer key" and seen["req"].url.path == "/emails"
    assert (
        seen["body"]["to"] == ["a@b.co"] and seen["body"]["reply_to"] == "help@x.co" and seen["body"]["text"] == "text"
    )


def test_postmark_payload_and_errors():
    def ok(req):
        b = json.loads(req.content)
        assert (
            req.headers["x-postmark-server-token"] == "tok" and b["To"] == "a@b.co" and b["MessageStream"] == "outbound"
        )
        return httpx.Response(200, json={"MessageID": "pm_1"})

    c = httpx.Client(base_url="https://api.postmarkapp.com", transport=httpx.MockTransport(ok))
    assert PostmarkSender("tok", "m@x.co", c).send(MSG) == "pm_1"
    bad = httpx.Client(
        base_url="https://api.postmarkapp.com", transport=httpx.MockTransport(lambda r: httpx.Response(422, text="no"))
    )
    with pytest.raises(EmailError, match="422"):
        PostmarkSender("tok", "m@x.co", bad).send(MSG)
    with pytest.raises(EmailError):
        ResendSender("", "m@x.co")


def test_make_sender():
    assert isinstance(make_sender("console", "", ""), ConsoleSender)
    with pytest.raises(RuntimeError):
        make_sender("smtp", "", "")


def test_admin_alert_without_admin_email_only_logs(services):
    sender = ConsoleSender()
    EmailNotifier(sender, Settings(), services.sessions).admin_alert("x", "y")
    assert sender.outbox == []
