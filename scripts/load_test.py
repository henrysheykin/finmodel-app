"""Load test (E17): N customers order and pay at once; ONE worker builds every model for real.

Starts the web server and one worker as separate processes (as in the production container),
places N orders through the wizard form at the same time, pays each with a signed (fake-Stripe)
webhook delivered twice, then watches the queue drain while timing the landing page and the
wizard. Each model goes through the real pipeline: openpyxl → LibreOffice → challenger.

    python scripts/load_test.py --orders 50 --out docs/reviews/load-test.json
    DATABASE_URL=postgresql+psycopg://... python scripts/load_test.py   # against Postgres

Nothing leaves the machine: fake payments, console email, a temporary database and storage.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import socket
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from adapters.payments import stripe_signature  # noqa: E402
from app import wizard  # noqa: E402

WEBHOOK_SECRET = "whsec_fake"  # the fake provider's default secret (no STRIPE_WEBHOOK_SECRET set)


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _pct(xs: list[float], p: float) -> float:
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))] if xs else 0.0


def order_mix(n: int) -> list[dict]:
    """A realistic spread: every available industry, both tiers, 1/3/5 years, monthly and annual."""
    types = [bt for bt, _ in wizard.BUSINESS_TYPES if wizard.available(bt)]
    shapes = [("light", "1", "monthly"), ("full", "3", "monthly"), ("full", "5", "annual"), ("full", "5", "monthly")]
    combos = itertools.cycle(itertools.product(shapes, types))
    out = []
    for i in range(n):
        (tier, years, gran), bt = next(combos)
        out.append(
            {
                "business_type": bt,
                "business_name": f"Load {i:02d}",
                "goal": "revenue_profit",
                "stage": "early",
                "horizon_years": years,
                "granularity": gran,
                "tier": tier,
                "email": f"load{i:02d}@example.com",
                "sample_data": "1",
            }
        )
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--orders", type=int, default=50)
    ap.add_argument("--timeout", type=float, default=3600, help="seconds to wait for the queue to drain")
    ap.add_argument("--out", type=Path, help="write the JSON result here")
    a = ap.parse_args(argv)

    tmp = Path(tempfile.mkdtemp(prefix="sm-load-"))
    port = _free_port()
    base = f"http://127.0.0.1:{port}"
    env = {
        **os.environ,
        "APP_ENV": "dev",
        "DATABASE_URL": os.environ.get("DATABASE_URL") or f"sqlite:///{tmp / 'load.db'}",
        "STORAGE_DIR": str(tmp / "storage"),
        "SECRET_KEY": "load-test-secret-key-0123456789abcdef",
        "PUBLIC_BASE_URL": base,
        "PAYMENT_PROVIDER": "fake",
        "EMAIL_PROVIDER": "console",
        "RATE_LIMIT_PER_10MIN": "0",
        "PYTHONPATH": str(ROOT),
    }
    py = sys.executable
    subprocess.run([py, "-m", "app.manage", "migrate"], env=env, cwd=ROOT, check=True, capture_output=True)
    logs = open(tmp / "processes.log", "w")  # noqa: SIM115 - closed at the end
    web = subprocess.Popen(
        [py, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        env=env,
        cwd=ROOT,
        stdout=logs,
        stderr=subprocess.STDOUT,
    )
    worker = subprocess.Popen([py, "-m", "worker.main"], env=env, cwd=ROOT, stdout=logs, stderr=subprocess.STDOUT)
    http = httpx.Client(base_url=base, timeout=60)
    try:
        for _ in range(200):
            try:
                if http.get("/healthz").status_code == 200:
                    break
            except httpx.TransportError:
                time.sleep(0.1)
        forms = order_mix(a.orders)

        # ---------------------------------------------------------------- orders, all at once
        def place(form: dict) -> tuple[str, float]:
            t0 = time.perf_counter()
            r = http.post("/start", data=form, follow_redirects=False)
            assert r.status_code == 303, (r.status_code, r.text[:300])
            return r.headers["location"].rsplit("/", 1)[1], time.perf_counter() - t0

        t_start = time.perf_counter()
        with ThreadPoolExecutor(a.orders) as pool:
            placed = list(pool.map(place, forms))
        order_ids = [oid for oid, _ in placed]

        # ---------------------------------------------------------------- payments, each delivered twice
        def pay(oid: str) -> tuple[str, float]:
            o = http.get(f"/api/orders/{oid}").json()
            evt = {
                "id": f"evt_{oid[:12]}",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": f"cs_load_{oid}",
                        "client_reference_id": oid,
                        "payment_status": "paid",
                        "payment_intent": f"pi_load_{oid}",
                        "amount_total": o["price_cents"],
                        "currency": o["currency"].lower(),
                    }
                },
            }
            payload = json.dumps(evt).encode()
            sig = stripe_signature(WEBHOOK_SECRET, payload, int(time.time()))
            t0 = time.perf_counter()
            r = http.post("/webhooks/stripe", content=payload, headers={"Stripe-Signature": sig})
            return r.json().get("action", f"HTTP {r.status_code}"), time.perf_counter() - t0

        with ThreadPoolExecutor(a.orders) as pool:
            paid = list(pool.map(pay, order_ids + order_ids))
        t_paid = time.perf_counter()

        # ---------------------------------------------------------------- drain, while browsing
        page_ms: dict[str, list[float]] = {"/": [], "/start": [], "/healthz": []}
        statuses: dict[str, str] = {}
        deadline = time.monotonic() + a.timeout
        while time.monotonic() < deadline:
            for path in page_ms:
                t0 = time.perf_counter()
                assert http.get(path).status_code == 200
                page_ms[path].append((time.perf_counter() - t0) * 1000)
            statuses = {oid: http.get(f"/api/orders/{oid}").json()["status"] for oid in order_ids}
            if all(s in ("ready", "failed") for s in statuses.values()):
                break
            time.sleep(1)
        t_done = time.perf_counter()
    finally:
        http.close()
        for p in (web, worker):
            p.terminate()
        for p in (web, worker):
            p.wait(10)
        logs.close()

    # ---------------------------------------------------------------- results from the database
    from sqlalchemy import select

    from app.db import make_engine, make_sessionmaker, session_scope
    from app.models import Order

    with session_scope(make_sessionmaker(make_engine(env["DATABASE_URL"]))) as s:
        rows = s.scalars(select(Order).where(Order.id.in_(order_ids))).all()
        builds = sorted((o.ready_at - o.paid_at).total_seconds() for o in rows if o.ready_at and o.paid_at)
        jobs = sum(len(o.jobs) for o in rows)
        per_build = []
        for o in rows:
            for j in o.jobs:
                if j.finished_at and j.locked_at:
                    per_build.append((j.finished_at - j.locked_at).total_seconds())
        failed = {o.id[:8]: (o.failure_reason or "")[:200] for o in rows if o.status != "ready"}
        sizes = [o.artifact("model_xlsx").size for o in rows if o.artifact("model_xlsx")]

    actions: dict[str, int] = {}
    for act, _ in paid:
        actions[act] = actions.get(act, 0) + 1
    result = {
        "orders": a.orders,
        "database": env["DATABASE_URL"].split("://")[0],
        "workers": 1,
        "ready": sum(1 for s in statuses.values() if s == "ready"),
        "not_ready": failed,
        "build_jobs": jobs,
        "webhook_actions": actions,
        "order_placement_s": {"p50": _pct([t for _, t in placed], 50), "max": max(t for _, t in placed)},
        "webhook_s": {"p50": _pct([t for _, t in paid], 50), "max": max(t for _, t in paid)},
        "drain_wall_s": round(t_done - t_paid, 1),
        "total_wall_s": round(t_done - t_start, 1),
        "build_s_per_model": {
            "mean": round(statistics.mean(per_build), 2) if per_build else None,
            "p50": round(_pct(per_build, 50), 2),
            "p95": round(_pct(per_build, 95), 2),
            "max": round(max(per_build), 2) if per_build else None,
        },
        "paid_to_ready_s": {"p50": round(_pct(builds, 50), 1), "max": round(max(builds), 1) if builds else None},
        "models_per_hour": round(len(builds) / max(t_done - t_paid, 1e-9) * 3600),
        "file_kb": {"min": min(sizes) // 1024 if sizes else None, "max": max(sizes) // 1024 if sizes else None},
        "pages_while_building_ms": {
            p: {"p50": round(_pct(v, 50)), "p95": round(_pct(v, 95)), "max": round(max(v)) if v else None}
            for p, v in page_ms.items()
        },
        "cpu_count": os.cpu_count(),
    }
    text = json.dumps(result, indent=2)
    print(text)
    if a.out:
        a.out.write_text(text + "\n")
    ok = result["ready"] == a.orders and jobs == a.orders and actions.get("paid") == a.orders
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
