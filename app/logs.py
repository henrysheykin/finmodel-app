"""One logging setup for the web app and the worker (one line per event, UTC timestamps).

Uvicorn configures only its own loggers, so without this the app's INFO events (orders, emails,
admin alerts) never reach the host's log view.
"""

from __future__ import annotations

import logging
import os
import re
import time

FORMAT = "%(asctime)sZ %(levelname)s %(name)s %(message)s"
#: secrets that travel in URLs: magic-link tokens (?token=) and signed download links (/download/<token>)
_SECRET_IN_URL = re.compile(r"(/download/|[?&]token=)[^\s&\"]+")


def redact(text: str) -> str:
    return _SECRET_IN_URL.sub(r"\1[redacted]", text)


class RedactSecrets(logging.Filter):
    """Keeps sign-in and download tokens out of the access log (E17): anyone who can read the host's
    logs could otherwise sign in as a customer for 15 minutes or download a model for 7 days."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, tuple):
            record.args = tuple(redact(a) if isinstance(a, str) else a for a in record.args)
        elif isinstance(record.msg, str):
            record.msg = redact(record.msg)
        return True


def configure_logging() -> None:
    root = logging.getLogger()
    if getattr(root, "_startupmodel_configured", False):
        return
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    handler = logging.StreamHandler()
    fmt = logging.Formatter(FORMAT, datefmt="%Y-%m-%dT%H:%M:%S")
    fmt.converter = time.gmtime
    handler.setFormatter(fmt)
    root.addHandler(handler)
    root.setLevel(level)
    logging.getLogger("uvicorn.access").addFilter(RedactSecrets())
    root._startupmodel_configured = True  # type: ignore[attr-defined]
