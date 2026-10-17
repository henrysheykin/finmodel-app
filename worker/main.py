"""Worker process: polls the jobs table and runs the delivery pipeline.

Usage: python -m worker.main [--once]
"""

from __future__ import annotations

import argparse
import logging
import os
import socket
import time

from adapters.notify import ConsoleNotifier
from adapters.storage import make_storage
from app.config import load_settings
from app.db import make_engine, make_sessionmaker, migrate
from worker.pipeline import Pipeline


def make_pipeline() -> Pipeline:
    cfg = load_settings()
    if not cfg.is_prod:
        migrate(cfg.database_url)
    sessions = make_sessionmaker(make_engine(cfg.database_url))
    storage = make_storage(cfg.storage_backend, cfg.storage_dir, cfg.s3_bucket, cfg.s3_endpoint_url)
    return Pipeline(sessions, cfg, storage, ConsoleNotifier(), worker_id=f"{socket.gethostname()}:{os.getpid()}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true", help="process at most one job and exit")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    pipe = make_pipeline()
    if a.once:
        pipe.run_once()
        return 0
    while True:
        if not pipe.run_once():
            time.sleep(pipe.cfg.worker_poll_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
