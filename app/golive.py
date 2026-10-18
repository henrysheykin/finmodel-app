"""Go-live readiness (E18): what still stands between this deployment and taking real money.

Pure function of the settings and the repo content, no network. Shown in three places so Henry never
has to run a shell: the deploy log (``python -m app.manage preflight`` in ``deploy/start.sh``), the top
of ``/admin``, and the go-live runbook (``docs/RUNBOOK_GO_LIVE.md``), which names each check by key.

Levels: ``ok``; ``warn`` = fine for a test-mode site, must be fixed before live payments;
``fail`` = live payments are switched on while this is still wrong.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from app import __version__
from app.config import Settings
from app.emails import CONTENT as EMAIL_CONTENT
from app.emails import PLACEHOLDER
from app.landing import LEGAL, LEGAL_PAGES, legal_text

OK, WARN, FAIL = "ok", "warn", "fail"
LIVE_PREFIXES = ("sk_live_", "rk_live_")
#: hosts that mean "the site is still on the hosting provider's test address"
TEMP_HOSTS = (".up.railway.app", ".railway.app", "localhost", "127.0.0.1")
#: shared sender domains of the email providers (usable only for tests)
SHARED_SENDERS = ("resend.dev", "postmarkapp.com")


@dataclass(frozen=True)
class Item:
    key: str
    level: str
    message: str


def live_payments(cfg: Settings) -> bool:
    return cfg.payment_provider == "stripe" and cfg.stripe_secret_key.startswith(LIVE_PREFIXES)


def _domain(addr: str) -> str:
    addr = addr.strip().rstrip(">")
    return addr.rsplit("@", 1)[-1].lower() if "@" in addr else ""


def readiness(cfg: Settings, legal_dir: Path = LEGAL, email_dir: Path = EMAIL_CONTENT) -> list[Item]:
    live = live_payments(cfg)
    bad = FAIL if live else WARN  # a gap is only fatal once real money flows
    items: list[Item] = []

    def add(key: str, ok: bool, good: str, problem: str, level: str | None = None) -> None:
        items.append(Item(key, OK if ok else (level or bad), good if ok else problem))

    host = (urlparse(cfg.public_base_url).hostname or "").lower()
    add(
        "domain",
        cfg.public_base_url.startswith("https://") and bool(host) and not host.endswith(TEMP_HOSTS),
        f"site address {cfg.public_base_url}",
        f"PUBLIC_BASE_URL is {cfg.public_base_url} — set it to https://startup-model.com after the domain is connected",
    )
    if cfg.payment_provider != "stripe":
        items.append(
            Item("stripe", WARN, f"PAYMENT_PROVIDER={cfg.payment_provider} (fake payments, not for customers)")
        )
    elif not live:
        items.append(Item("stripe", WARN, "Stripe is in test mode (sk_test_…): no real money is taken"))
    elif not cfg.allow_live_payments:
        items.append(
            Item(
                "stripe",
                FAIL,
                "a live Stripe key is set but ALLOW_LIVE_PAYMENTS is not 1 — the web app refuses to start",
            )
        )
    else:
        items.append(Item("stripe", OK, "Stripe live mode (ALLOW_LIVE_PAYMENTS=1)"))
    if cfg.payment_provider == "stripe":
        add(
            "webhook",
            cfg.stripe_webhook_secret.startswith("whsec_"),
            "Stripe webhook signing secret set",
            "STRIPE_WEBHOOK_SECRET is missing — paid orders would never be built",
            level=FAIL,
        )
    sender = _domain(cfg.email_from)
    if cfg.email_provider not in ("resend", "postmark"):
        items.append(Item("email", bad, f"EMAIL_PROVIDER={cfg.email_provider}: emails are only printed to the log"))
    else:
        add(
            "email",
            bool(sender)
            and not sender.endswith(SHARED_SENDERS)
            and (not host or host.endswith(sender) or sender.endswith(host.removeprefix("www."))),
            f"emails sent by {cfg.email_provider} from {sender}",
            f"EMAIL_FROM ({cfg.email_from or 'empty'}) is not on the site's domain — verify the domain in the email "
            "provider and send from it, or emails land in spam",
        )
    add("support", bool(cfg.support_email), f"support address {cfg.support_email}", "SUPPORT_EMAIL is empty")
    add(
        "admin",
        bool(cfg.admin_user and cfg.admin_password and cfg.admin_email),
        "admin panel on, failure alerts go to ADMIN_EMAIL",
        "set ADMIN_USER, ADMIN_PASSWORD and ADMIN_EMAIL (build-failure alerts)",
    )
    add(
        "client_ip",
        bool(cfg.client_ip_header),
        f"rate limits count {cfg.client_ip_header}",
        "CLIENT_IP_HEADER is empty — set X-Real-IP on Railway so rate limits count real visitors",
        level=WARN,
    )
    missing = [p for p in LEGAL_PAGES if not legal_text(p, legal_dir)]
    add(
        "legal",
        not missing,
        "privacy, terms and refund pages published",
        "legal texts missing or with unfilled [PLACEHOLDERS]: "
        + ", ".join(f"content/legal/{p}.md" for p in missing)
        + " (Stripe checks them)",
    )
    unfinished = sorted(
        f.stem for f in email_dir.glob("*.md") if f.name != "README.md" and PLACEHOLDER.search(f.read_text("utf-8"))
    )
    add(
        "email_copy",
        not unfinished,
        "email copy complete",
        "unfinished email copy (placeholders): " + ", ".join(unfinished),
        level=WARN,
    )
    return items


def ready_for_live(items: list[Item]) -> bool:
    return all(i.level == OK for i in items if i.key not in ("email_copy",))


def report(cfg: Settings, items: list[Item] | None = None) -> str:
    items = readiness(cfg) if items is None else items
    mark = {OK: "ok  ", WARN: "WARN", FAIL: "FAIL"}
    lines = [
        f"go-live preflight v{__version__}: " + ("READY for live payments" if ready_for_live(items) else "not ready")
    ]
    lines += [f"  {mark[i.level]} {i.key}: {i.message}" for i in items]
    return "\n".join(lines)
