# One image, one container: deploy/start.sh runs migrations, the worker and the web server.
# Single processes are still available for local use:
#   web:    uvicorn app.main:app --host 0.0.0.0 --port 8000
#   worker: python -m worker.main
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=prod \
    STORAGE_DIR=/data/storage

RUN apt-get update \
 && apt-get install -y --no-install-recommends libreoffice-calc-nogui fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 app
WORKDIR /srv/app

COPY pyproject.toml README.md constraints.txt ./
COPY engine ./engine
COPY app ./app
COPY worker ./worker
COPY adapters ./adapters
COPY alembic.ini ./
COPY web ./web
COPY content ./content
COPY samples ./samples
COPY deploy ./deploy
RUN pip install -c constraints.txt . && chmod +x deploy/start.sh

# Starts as root only to fix volume ownership; start.sh drops to the `app` user at once.
EXPOSE 8000
CMD ["/srv/app/deploy/start.sh"]
