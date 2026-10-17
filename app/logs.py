"""One logging setup for the web app and the worker (one line per event, UTC timestamps).

Uvicorn configures only its own loggers, so without this the app's INFO events (orders, emails,
admin alerts) never reach the host's log view.
"""

from __future__ import annotations

import logging
import os
import time

FORMAT = "%(asctime)sZ %(levelname)s %(name)s %(message)s"


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
    root._startupmodel_configured = True  # type: ignore[attr-defined]
