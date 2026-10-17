# One image for both processes:
#   web:    uvicorn app.main:app --host 0.0.0.0 --port 8000   (default CMD)
#   worker: python -m worker.main
FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends libreoffice-calc-nogui fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 10001 app
WORKDIR /srv/app

COPY pyproject.toml README.md ./
COPY engine ./engine
COPY app ./app
COPY worker ./worker
COPY adapters ./adapters
COPY alembic.ini ./
COPY web ./web
RUN pip install .

USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
