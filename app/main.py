"""FastAPI application (skeleton; pages and API arrive in later tasks)."""

from fastapi import FastAPI

app = FastAPI(title="Ledgerline", docs_url=None, redoc_url=None)


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}
