"""Operations commands for deploys.

python -m app.manage migrate   # apply database migrations (run on every container start)
python -m app.manage check     # load and validate settings, print a short summary (no secrets)
"""

from __future__ import annotations

import argparse
import sys

from app.config import load_settings
from app.db import migrate


def _summary() -> str:
    cfg = load_settings()
    db = cfg.database_url.split("://", 1)[0]
    stripe_mode = "live" if cfg.stripe_secret_key.startswith(("sk_live_", "rk_live_")) else "test"
    if not cfg.stripe_secret_key:
        stripe_mode = "-"
    return (
        f"env={cfg.app_env} db={db} storage={cfg.storage_backend} payments={cfg.payment_provider}"
        f" stripe={stripe_mode} email={cfg.email_provider} base_url={cfg.public_base_url}"
        f" admin={'on' if cfg.admin_user and cfg.admin_password else 'off'}"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.manage")
    ap.add_argument("command", choices=["migrate", "check"])
    a = ap.parse_args(argv)
    if a.command == "check":
        print(_summary())
        return 0
    cfg = load_settings()
    migrate(cfg.database_url)
    print("migrations applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
