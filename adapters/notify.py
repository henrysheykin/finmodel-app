"""Notifications raised by the pipeline. Console implementation for dev; E12 adds email.

The pipeline only calls this interface, so a failed build alerts the admin and the customer
never receives a file that did not pass the checks.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Protocol

log = logging.getLogger("notify")


class Notifier(Protocol):
    def model_ready(self, email: str, order_id: str, download_url: str) -> None: ...
    def admin_alert(self, subject: str, body: str) -> None: ...
    def login_link(self, email: str, url: str) -> None: ...


class ConsoleNotifier:
    def model_ready(self, email: str, order_id: str, download_url: str) -> None:
        log.info("model ready: order=%s to=%s link=%s", order_id, email, download_url)

    def admin_alert(self, subject: str, body: str) -> None:
        log.error("ADMIN ALERT: %s\n%s", subject, body)

    def login_link(self, email: str, url: str) -> None:
        log.info("sign-in link for %s: %s", email, url)


@dataclass
class RecordingNotifier:
    """Test double: remembers every call."""

    ready: list[tuple[str, str, str]] = field(default_factory=list)
    alerts: list[tuple[str, str]] = field(default_factory=list)
    logins: list[tuple[str, str]] = field(default_factory=list)

    def model_ready(self, email: str, order_id: str, download_url: str) -> None:
        self.ready.append((email, order_id, download_url))

    def admin_alert(self, subject: str, body: str) -> None:
        self.alerts.append((subject, body))

    def login_link(self, email: str, url: str) -> None:
        self.logins.append((email, url))
