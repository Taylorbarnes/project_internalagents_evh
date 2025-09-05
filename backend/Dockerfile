# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=5000

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates tini \
      fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 \
      libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libx11-6 \
      libx11-xcb1 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
      libxrandr2 libxrender1 libxss1 libxtst6 xdg-utils \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 10001 appuser
WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install chromium for Playwright
RUN python -m playwright install --with-deps chromium

COPY app.py booking-api-schema.yaml ./

USER appuser
EXPOSE ${PORT}

CMD ["tini", "--", "python", "app.py"]



