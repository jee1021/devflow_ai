FROM python:3.13-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /devflow_ai

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir poetry
RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-root


FROM python:3.13-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /devflow_ai

RUN addgroup --system app && adduser --system --ingroup app app

RUN mkdir -p /devflow_ai/apps/static \
    /devflow_ai/apps/media \
    /devflow_ai/staticfiles \
    && chown -R app:app /devflow_ai

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder --chmod=755 /usr/local/bin/ /usr/local/bin/

COPY --chown=app:app . ./

USER app