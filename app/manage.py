"""Operations commands for deploys.

python -m app.manage migrate   # apply database migrations (run on every container start)
python -m app.manage check     # load and validate settings, print a short summary (no secrets)
python -m app.manage preflight # go-live readiness (app/golive.py); --strict exits 1 unless ready for live
"""

from __future__ import annotations

import argparse
import sys

from app import __version__
from app.config import load_settings
from app.db import migrate


def _summary() -> str:
    cfg = load_settings()
    db = cfg.database_url.split("://", 1)[0]
    stripe_mode = "live" if cfg.stripe_secret_key.startswith(("sk_live_", "rk_live_")) else "test"
    if not cfg.stripe_secret_key:
        stripe_mode = "-"
    return (
        f"v{__version__} env={cfg.app_env} db={db} storage={cfg.storage_backend} payments={cfg.payment_provider}"
        f" stripe={stripe_mode} email={cfg.email_provider} base_url={cfg.public_base_url}"
        f" admin={'on' if cfg.admin_user and cfg.admin_password else 'off'}"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m app.manage")
    ap.add_argument("command", choices=["migrate", "check", "preflight"])
    ap.add_argument("--strict", action="store_true", help="preflight: exit 1 unless ready for live payments")
    a = ap.parse_args(argv)
    if a.command == "preflight":
        from app import golive

        cfg = load_settings()
        items = golive.readiness(cfg)
        print(golive.report(cfg, items))
        return 1 if a.strict and not golive.ready_for_live(items) else 0
    if a.command == "check":
        print(_summary())
        return 0
    cfg = load_settings()
    migrate(cfg.database_url)
    print("migrations applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
