"""E18 release candidate: version, go-live preflight (app/golive.py), admin readiness box, runbook."""

import tomllib
from dataclasses import replace
from pathlib import Path

from app import __version__, golive
from app.config import Settings
from app.manage import main as manage_main
from tests.test_admin import admin_on, login  # noqa: F401 (fixture)

ROOT = Path(__file__).resolve().parents[1]

LIVE = Settings(
    app_env="prod",
    secret_key="x" * 48,
    public_base_url="https://startup-model.com",
    payment_provider="stripe",
    stripe_secret_key="sk_live_abc",
    stripe_webhook_secret="whsec_abc",
    allow_live_payments=True,
    email_provider="resend",
    email_api_key="re_abc",
    email_from="StartupModel <models@startup-model.com>",
    support_email="support@startup-model.com",
    admin_user="henry",
    admin_password="correct horse battery",
    admin_email="owner@example.com",
    client_ip_header="X-Real-IP",
)


def legal_dir(tmp_path, pages=("privacy", "terms", "refunds")):
    d = tmp_path / "legal"
    d.mkdir(parents=True)
    for p in pages:
        (d / f"{p}.md").write_text("# Text\n\nBody.\n", encoding="utf-8")
    return d


def email_dir(tmp_path, body="Hello {{ name }}."):
    d = tmp_path / "email"
    d.mkdir(parents=True)
    (d / "model-ready.md").write_text(f"---\nid: x\nsubject: s\n---\n{body}\n", encoding="utf-8")
    (d / "README.md").write_text("[SOMETHING_IN_README] is ignored\n", encoding="utf-8")
    return d


def levels(cfg, tmp_path, **kw):
    items = golive.readiness(cfg, kw.get("legal") or legal_dir(tmp_path), kw.get("email") or email_dir(tmp_path))
    return {i.key: i.level for i in items}, items


def test_version_matches_pyproject_and_changelog():
    project = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))["project"]
    assert project["version"] == __version__ == "0.1.0"
    assert f"## v{__version__}" in (ROOT / "CHANGELOG.md").read_text("utf-8")


def test_fully_configured_live_site_is_ready(tmp_path):
    lv, items = levels(LIVE, tmp_path)
    assert set(lv.values()) == {golive.OK}, items
    assert golive.ready_for_live(items)
    assert "READY for live payments" in golive.report(LIVE, items)


def test_gaps_are_warnings_in_test_mode(tmp_path):
    cfg = replace(
        LIVE,
        stripe_secret_key="sk_test_abc",
        allow_live_payments=False,
        public_base_url="https://finmodel-app-production.up.railway.app",
        email_from="onboarding@resend.dev",
        client_ip_header="",
    )
    lv, items = levels(cfg, tmp_path, legal=legal_dir(tmp_path, pages=()))
    assert lv["stripe"] == lv["domain"] == lv["email"] == lv["client_ip"] == lv["legal"] == golive.WARN
    assert golive.FAIL not in lv.values()
    assert not golive.ready_for_live(items)


def test_gaps_fail_once_live_money_flows(tmp_path):
    cfg = replace(LIVE, public_base_url="https://x.up.railway.app", support_email="")
    lv, _ = levels(cfg, tmp_path, legal=legal_dir(tmp_path, pages=("privacy",)))
    assert lv["domain"] == lv["support"] == lv["legal"] == golive.FAIL
    lv, items = levels(replace(LIVE, allow_live_payments=False), tmp_path / "b")
    assert lv["stripe"] == golive.FAIL and not golive.ready_for_live(items)


def test_missing_webhook_secret_always_fails(tmp_path):
    lv, _ = levels(replace(LIVE, stripe_secret_key="sk_test_1", stripe_webhook_secret=""), tmp_path)
    assert lv["webhook"] == golive.FAIL


def test_email_sender_must_be_on_the_site_domain(tmp_path):
    for i, sender in enumerate(("models@other.com", "onboarding@resend.dev", "")):
        lv, _ = levels(replace(LIVE, email_from=sender), tmp_path / str(i))
        assert lv["email"] == golive.FAIL, sender
    lv, _ = levels(replace(LIVE, email_from="models@send.startup-model.com"), tmp_path / "ok")
    assert lv["email"] == golive.OK
    lv, _ = levels(replace(LIVE, email_provider="console"), tmp_path / "console")
    assert lv["email"] == golive.FAIL


def test_unfinished_email_copy_is_flagged_but_does_not_block(tmp_path):
    lv, items = levels(LIVE, tmp_path, email=email_dir(tmp_path, "[FAILED_BUILD_POLICY: decide] {{ amount }}"))
    assert lv["email_copy"] == golive.WARN
    assert golive.ready_for_live(items)
    # the real repo: no email copy is left unfinished
    real = {i.key: i for i in golive.readiness(LIVE)}
    assert real["email_copy"].level == golive.OK, real["email_copy"].message


def test_preflight_command(monkeypatch, capsys):
    for k in ("APP_ENV", "PAYMENT_PROVIDER", "PUBLIC_BASE_URL"):
        monkeypatch.delenv(k, raising=False)
    assert manage_main(["preflight"]) == 0
    out = capsys.readouterr().out
    assert out.startswith(f"go-live preflight v{__version__}: not ready")
    assert "WARN stripe" in out and "sk_" not in out
    assert manage_main(["preflight", "--strict"]) == 1


def test_preflight_never_prints_secrets(tmp_path):
    out = golive.report(LIVE, golive.readiness(LIVE, legal_dir(tmp_path), email_dir(tmp_path)))
    for secret in (LIVE.stripe_secret_key, LIVE.stripe_webhook_secret, LIVE.email_api_key, LIVE.admin_password):
        assert secret not in out


def test_start_script_runs_preflight_without_stopping():
    script = (ROOT / "deploy" / "start.sh").read_text("utf-8")
    assert "python -m app.manage preflight || true" in script
    assert script.index("manage preflight") < script.index("python -m worker.main")


def test_admin_shows_readiness_box(client, admin_on):  # noqa: F811
    login(client)
    page = client.get("/admin").text
    assert "Before live payments" in page and "client_ip" in page and __version__ in page


def test_admin_hides_box_when_ready(client, admin_on, monkeypatch):  # noqa: F811
    monkeypatch.setattr(golive, "readiness", lambda cfg: [golive.Item("stripe", golive.OK, "live")])
    login(client)
    assert "Before live payments" not in client.get("/admin").text


def test_runbook_covers_every_check_and_variable():
    runbook = (ROOT / "docs" / "RUNBOOK_GO_LIVE.md").read_text("utf-8")
    for key in ("domain", "stripe", "webhook", "email", "support", "admin", "client_ip", "legal", "email_copy"):
        assert f"`{key}`" in runbook, key
    env_names = [
        line.split("=", 1)[0]
        for line in (ROOT / ".env.example").read_text("utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    prod_vars = (
        "DATABASE_URL SECRET_KEY PUBLIC_BASE_URL PAYMENT_PROVIDER STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET "
        "ALLOW_LIVE_PAYMENTS EMAIL_PROVIDER EMAIL_API_KEY EMAIL_FROM SUPPORT_EMAIL ADMIN_USER ADMIN_PASSWORD "
        "ADMIN_EMAIL CLIENT_IP_HEADER"
    ).split()
    for name in prod_vars:
        assert name in env_names and f"`{name}`" in runbook, name
    assert "v0.1.0" in runbook and "Rollback" in runbook
