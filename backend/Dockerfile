# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=5000

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates tini \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 10001 appuser
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py booking-api-schema.yaml ./

USER appuser
EXPOSE ${PORT}

CMD ["tini", "--", "python", "app.py"]


