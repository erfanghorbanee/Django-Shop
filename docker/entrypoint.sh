#!/usr/bin/env bash
set -euo pipefail

export DJANGO_SETTINGS_MODULE="config.settings"
export PYTHONPATH="/app"

wait_for_db() {
  local tries="${DJANGO_DB_MAX_TRIES:-30}"
  local delay="${DJANGO_DB_RETRY_DELAY:-1}"

  python <<'PY'
import os
import sys
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402
from django.db import connections  # noqa: E402

django.setup()

tries = int(os.environ.get("DJANGO_DB_MAX_TRIES", "30"))
delay = float(os.environ.get("DJANGO_DB_RETRY_DELAY", "1"))

for attempt in range(1, tries + 1):
    try:
        connections["default"].ensure_connection()
        sys.exit(0)
    except Exception as exc:  # pragma: no cover
        print(f"[entrypoint] Database unavailable (attempt {attempt}/{tries}): {exc}")
        time.sleep(delay)

print("[entrypoint] Database connection failed after retries", file=sys.stderr)
sys.exit(1)
PY
}

if [[ "${DJANGO_WAIT_FOR_DB:-1}" != "0" ]]; then
  wait_for_db
fi

if [[ "${DJANGO_RUN_MIGRATIONS:-1}" != "0" ]]; then
  python manage.py migrate --noinput
fi

if [[ "${DJANGO_COLLECTSTATIC:-1}" != "0" ]]; then
  python manage.py collectstatic --noinput
fi

exec "$@"


