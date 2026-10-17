"""Settings read from environment variables (names listed in .env.example; values never in the repo)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _int(name: str, default: int) -> int:
    v = os.environ.get(name, "")
    return int(v) if v.strip() else default


@dataclass(frozen=True)
class Settings:
    app_env: str = "dev"
    database_url: str = "sqlite:///./dev.db"
    secret_key: str = ""
    public_base_url: str = "http://localhost:8000"
    storage_backend: str = "local"
    storage_dir: str = "./var/storage"
    s3_bucket: str = ""
    s3_endpoint_url: str = ""
    admin_email: str = ""
    admin_user: str = ""
    admin_password: str = ""
    payment_provider: str = "fake"
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    allow_live_payments: bool = False
    email_provider: str = "console"
    email_api_key: str = ""
    email_from: str = ""
    support_email: str = ""
    #: prices in cents (ADR-002 addendum 2: Light $149, Full $349)
    prices: dict[str, int] = field(default_factory=lambda: {"light": 14900, "full": 34900})
    #: download links in the "model ready" email live 7 days (content/email/model-ready.md)
    link_ttl_seconds: int = 7 * 24 * 3600
    job_max_attempts: int = 3
    job_backoff_seconds: int = 30
    job_timeout_seconds: int = 15 * 60
    worker_poll_seconds: int = 2

    @property
    def is_prod(self) -> bool:
        return self.app_env == "prod"

    def check(self) -> None:
        """Refuse to run in production with unsafe defaults."""
        if self.is_prod and (len(self.secret_key) < 32 or self.secret_key.startswith("dev-insecure")):
            raise RuntimeError("SECRET_KEY must be set (32+ characters) in production")
        if self.admin_password and len(self.admin_password) < 12:
            raise RuntimeError("ADMIN_PASSWORD must be at least 12 characters")
        if self.is_prod and self.payment_provider != "stripe":
            raise RuntimeError("production must use PAYMENT_PROVIDER=stripe")
        if self.is_prod and (self.email_provider == "console" or not self.email_from or not self.support_email):
            raise RuntimeError("production needs EMAIL_PROVIDER (resend|postmark), EMAIL_FROM and SUPPORT_EMAIL")


def load_settings() -> Settings:
    env = os.environ.get
    s = Settings(
        app_env=env("APP_ENV", "dev") or "dev",
        database_url=env("DATABASE_URL", "") or "sqlite:///./dev.db",
        # dev-only fallback so local runs work; prod refuses it in check()
        secret_key=env("SECRET_KEY", "") or "dev-insecure-secret-key-change-me",
        public_base_url=(env("PUBLIC_BASE_URL", "") or "http://localhost:8000").rstrip("/"),
        storage_backend=env("STORAGE_BACKEND", "") or "local",
        storage_dir=env("STORAGE_DIR", "") or "./var/storage",
        s3_bucket=env("S3_BUCKET", ""),
        s3_endpoint_url=env("S3_ENDPOINT_URL", ""),
        admin_email=env("ADMIN_EMAIL", ""),
        admin_user=env("ADMIN_USER", ""),
        admin_password=env("ADMIN_PASSWORD", ""),
        payment_provider=env("PAYMENT_PROVIDER", "") or "fake",
        stripe_secret_key=env("STRIPE_SECRET_KEY", ""),
        stripe_webhook_secret=env("STRIPE_WEBHOOK_SECRET", ""),
        allow_live_payments=env("ALLOW_LIVE_PAYMENTS", "") == "1",
        email_provider=env("EMAIL_PROVIDER", "") or "console",
        email_api_key=env("EMAIL_API_KEY", ""),
        email_from=env("EMAIL_FROM", ""),
        support_email=env("SUPPORT_EMAIL", ""),
        prices={"light": _int("PRICE_LIGHT_CENTS", 14900), "full": _int("PRICE_FULL_CENTS", 34900)},
        link_ttl_seconds=_int("LINK_TTL_SECONDS", 7 * 24 * 3600),
    )
    s.check()
    return s
