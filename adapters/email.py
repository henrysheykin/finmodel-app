"""Email senders: console (dev/tests), Resend and Postmark (HTTP APIs over httpx)."""

from __future__ import annotations

import logging
import secrets
from dataclasses import dataclass, field
from typing import Protocol

import httpx

log = logging.getLogger("email")


class EmailError(RuntimeError):
    pass


@dataclass(frozen=True)
class EmailMessage:
    to: str
    subject: str
    text: str
    html: str
    reply_to: str = ""
    tag: str = ""


class EmailSender(Protocol):
    name: str

    def send(self, msg: EmailMessage) -> str: ...


@dataclass
class ConsoleSender:
    """Logs instead of sending; keeps an outbox for tests and local runs."""

    name: str = "console"
    outbox: list[EmailMessage] = field(default_factory=list)

    def send(self, msg: EmailMessage) -> str:
        self.outbox.append(msg)
        log.info("EMAIL to=%s subject=%r\n%s", msg.to, msg.subject, msg.text)
        return "console_" + secrets.token_hex(6)


class ResendSender:
    name = "resend"

    def __init__(self, api_key: str, sender: str, client: httpx.Client | None = None):
        if not api_key or not sender:
            raise EmailError("EMAIL_API_KEY and EMAIL_FROM are required for Resend")
        self.sender = sender
        self.client = client or httpx.Client(base_url="https://api.resend.com", timeout=15)
        self.client.headers["Authorization"] = f"Bearer {api_key}"

    def send(self, msg: EmailMessage) -> str:
        body = {"from": self.sender, "to": [msg.to], "subject": msg.subject, "html": msg.html, "text": msg.text}
        if msg.reply_to:
            body["reply_to"] = msg.reply_to
        if msg.tag:
            body["tags"] = [{"name": "type", "value": msg.tag}]
        return _post(self.client, "/emails", body, "id")


class PostmarkSender:
    name = "postmark"

    def __init__(self, server_token: str, sender: str, client: httpx.Client | None = None):
        if not server_token or not sender:
            raise EmailError("EMAIL_API_KEY and EMAIL_FROM are required for Postmark")
        self.sender = sender
        self.client = client or httpx.Client(base_url="https://api.postmarkapp.com", timeout=15)
        self.client.headers["X-Postmark-Server-Token"] = server_token
        self.client.headers["Accept"] = "application/json"

    def send(self, msg: EmailMessage) -> str:
        body = {
            "From": self.sender,
            "To": msg.to,
            "Subject": msg.subject,
            "HtmlBody": msg.html,
            "TextBody": msg.text,
            "MessageStream": "outbound",
        }
        if msg.reply_to:
            body["ReplyTo"] = msg.reply_to
        if msg.tag:
            body["Tag"] = msg.tag
        return _post(self.client, "/email", body, "MessageID")


def _post(client: httpx.Client, path: str, body: dict, id_key: str) -> str:
    try:
        r = client.post(path, json=body)
    except httpx.HTTPError as exc:
        raise EmailError(f"email provider unreachable: {type(exc).__name__}") from exc
    if r.status_code >= 400:
        raise EmailError(f"email provider refused: HTTP {r.status_code} {r.text[:200]}")
    return str(r.json().get(id_key, ""))


def make_sender(provider: str, api_key: str, sender: str) -> EmailSender:
    if provider in ("", "console"):
        return ConsoleSender()
    if provider == "resend":
        return ResendSender(api_key, sender)
    if provider == "postmark":
        return PostmarkSender(api_key, sender)
    raise RuntimeError(f"unknown EMAIL_PROVIDER {provider!r}")
