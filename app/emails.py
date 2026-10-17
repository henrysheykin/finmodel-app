"""Transactional emails rendered from content/email/*.md (front matter + Markdown with Jinja2).

Every email is rendered twice: plain text, and HTML where every variable is HTML-escaped
before a small Markdown subset (paragraphs, **bold**, [links](url), - and 1. lists) is
converted. ``EmailNotifier`` implements the pipeline's Notifier interface.
"""

from __future__ import annotations

import html
import json
import logging
import re
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from jinja2 import StrictUndefined
from jinja2.sandbox import SandboxedEnvironment
from sqlalchemy.orm import Session, sessionmaker

from adapters.email import EmailError, EmailMessage, EmailSender
from app import wizard
from app.config import Settings
from app.db import session_scope, utcnow
from app.models import Order

log = logging.getLogger("emails")
CONTENT = Path(__file__).resolve().parents[1] / "content" / "email"
FRONT = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
# unfinished copy, e.g. [FAILED_BUILD_POLICY: ...]; [SUPPORT_EMAIL] is enforced by config in production
PLACEHOLDER = re.compile(r"\[(?!SUPPORT_EMAIL\])[A-Z][A-Z_]{3,}[^\]]*\]")

_env = SandboxedEnvironment(undefined=StrictUndefined, autoescape=False, keep_trailing_newline=True)


@dataclass(frozen=True)
class Template:
    id: str
    type: str
    subject: str
    preheader: str
    body: str


def load(name: str) -> Template:
    raw = (CONTENT / f"{name}.md").read_text(encoding="utf-8")
    m = FRONT.match(raw)
    if not m:
        raise ValueError(f"{name}.md has no front matter")
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] == '"':
            v = v[1:-1]
        meta[k.strip()] = v
    return Template(
        meta["id"], meta.get("type", "transactional"), meta["subject"], meta.get("preheader", ""), m.group(2)
    )


# --------------------------------------------------------------------------- tiny Markdown → HTML
_INLINE = [
    (re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)"), r'<a href="\2" style="color:#0F6E56">\1</a>'),
]


def _inline(text: str) -> str:
    for rx, rep in _INLINE:
        text = rx.sub(rep, text)
    return text


def md_to_html(md: str) -> str:
    """Input is already escaped: only our own Markdown syntax becomes tags."""
    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        lines = block.splitlines()
        if all(re.match(r"^- ", ln) for ln in lines):
            out.append("<ul>" + "".join(f"<li>{_inline(ln[2:])}</li>" for ln in lines) + "</ul>")
        elif all(re.match(r"^\d+\. ", ln) for ln in lines):
            out.append("<ol>" + "".join(f"<li>{_inline(ln.split('. ', 1)[1])}</li>" for ln in lines) + "</ol>")
        else:
            out.append("<p>" + "<br>".join(_inline(ln) for ln in lines) + "</p>")
    return "\n".join(out)


def _md_to_text(md: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r"\1: \2", md)
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text).strip() + "\n"


LAYOUT = (
    '<!doctype html><html><body style="margin:0;background:#F7F8F3">'
    '<span style="display:none;max-height:0;overflow:hidden">{preheader}</span>'
    '<div style="max-width:560px;margin:0 auto;padding:32px 24px;background:#FFFFFF;'
    'font-family:Arial,Helvetica,sans-serif;font-size:15px;line-height:1.6;color:#1B2A2F">{body}</div>'
    "</body></html>"
)


def render(name: str, ctx: dict) -> tuple[str, str, str, Template]:
    """Return (subject, text, html, template)."""
    tpl = load(name)
    subject = _env.from_string(tpl.subject).render(ctx).strip()
    text = _md_to_text(_env.from_string(tpl.body).render(ctx))
    esc = {k: html.escape(v) if isinstance(v, str) else v for k, v in ctx.items()}
    body_html = md_to_html(_env.from_string(tpl.body).render(esc))
    pre = html.escape(_env.from_string(tpl.preheader).render(ctx))
    return subject, text, LAYOUT.format(preheader=pre, body=body_html), tpl


def has_placeholder(text: str) -> bool:
    return bool(PLACEHOLDER.search(text))


# --------------------------------------------------------------------------- notifier
@dataclass
class EmailNotifier:
    sender: EmailSender
    cfg: Settings
    sessions: sessionmaker[Session]

    def _ctx(self, order: Order, **extra) -> dict:
        a = json.loads(order.answers_json or "{}")
        years = a.get("horizon_years", "")
        return {
            "first_name": None,
            "order_id": order.id[:8].upper(),
            "tier": wizard.PLANS.get(order.tier, {}).get("name", order.tier),
            "template_title": a.get("business_name")
            or dict(wizard.BUSINESS_TYPES).get(a.get("business_type", ""), order.template),
            "horizon_years": years,
            "granularity": a.get("granularity", ""),
            "amount": f"${order.price_cents / 100:,.0f}",
            "support_email": self.cfg.support_email or "[SUPPORT_EMAIL]",
            "resend_url": f"{self.cfg.public_base_url}/account",
            **extra,
        }

    def _send(self, to: str, name: str, ctx: dict, block_placeholders: bool = True) -> bool:
        subject, text, body, tpl = render(name, ctx)
        if block_placeholders and has_placeholder(subject + text):
            # unfinished copy (e.g. failed-build policy, D9) never goes to a customer
            self.admin_alert(f"Email '{name}' not sent to {to}", f"Copy still has a placeholder:\n\n{text}")
            return False
        reply_to = self.cfg.support_email or ""
        try:
            self.sender.send(EmailMessage(to, subject, text, body, reply_to, tpl.type))
        except EmailError:
            log.exception("email %s to %s failed", name, to)
            raise
        return True

    def _order(self, order_id: str) -> Order:
        with session_scope(self.sessions) as s:
            order = s.get(Order, order_id)
            s.expunge(order)
            return order

    # Notifier interface ----------------------------------------------------------
    def model_ready(self, email: str, order_id: str, download_url: str) -> None:
        d = utcnow() + timedelta(seconds=self.cfg.link_ttl_seconds)
        expires = f"{d.day} {d:%B %Y}"
        ctx = self._ctx(self._order(order_id), download_url=download_url, link_expires=expires)
        self._send(email, "model-ready", ctx)

    def order_received(self, order_id: str) -> None:
        order = self._order(order_id)
        self._send(order.email, "order-received", self._ctx(order))

    def build_failed(self, order_id: str) -> None:
        order = self._order(order_id)
        self._send(order.email, "build-failed", self._ctx(order))

    def refund_issued(self, order_id: str) -> None:
        order = self._order(order_id)
        self._send(order.email, "refund-issued", self._ctx(order))

    def login_link(self, email: str, url: str) -> None:
        ctx = {"login_url": url, "support_email": self.cfg.support_email or "[SUPPORT_EMAIL]"}
        self._send(email, "sign-in", ctx, block_placeholders=False)

    def admin_alert(self, subject: str, body: str) -> None:
        log.error("ADMIN ALERT: %s\n%s", subject, body)
        if not self.cfg.admin_email:
            return
        try:
            msg = EmailMessage(
                self.cfg.admin_email, f"[StartupModel] {subject}", body, f"<pre>{html.escape(body)}</pre>", tag="admin"
            )
            self.sender.send(msg)
        except EmailError:
            log.exception("admin alert email failed")
