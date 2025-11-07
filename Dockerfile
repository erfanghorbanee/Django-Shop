FROM python:3.12-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=on

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        libmagic1 \
    && rm -rf /var/lib/apt/lists/*

FROM base as builder

COPY requirements /tmp/requirements
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --upgrade pip \
    && /opt/venv/bin/pip install -r /tmp/requirements/production.txt

FROM builder as dev-deps
RUN /opt/venv/bin/pip install -r /tmp/requirements/local.txt

FROM base as production

ENV PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv
COPY Django-Shop /app
COPY docker/entrypoint.sh /entrypoint.sh

RUN groupadd -g 1000 appgroup \
    && useradd --create-home --shell /bin/bash --uid 1000 --gid appgroup appuser \
    && chown -R appuser:appgroup /app \
    && chmod +x /entrypoint.sh

USER appuser

ENV DJANGO_SETTINGS_MODULE=config.settings

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

FROM production as development

COPY --from=dev-deps /opt/venv /opt/venv
COPY docker/entrypoint.sh /entrypoint.sh

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

