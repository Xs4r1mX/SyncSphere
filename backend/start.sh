#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py collectstatic --noinput

if [ "${CELERY_TASK_ALWAYS_EAGER:-False}" = "True" ]; then
  GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-300}"
else
  GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"
fi

# Matches the Render env paste: CELERY_TASK_ALWAYS_EAGER=True and no Redis.
# A worker starts only if eager is off and a broker URL is set (e.g. Upstash).
if [ "${CELERY_TASK_ALWAYS_EAGER:-False}" != "True" ] && [ -n "${CELERY_BROKER_URL:-}" ]; then
  celery -A core worker --loglevel=info --concurrency="${CELERY_CONCURRENCY:-1}" &
  celery_pid=$!

  shutdown() {
    kill -TERM "$celery_pid" 2>/dev/null || true
    if [ -n "${gunicorn_pid:-}" ]; then
      kill -TERM "$gunicorn_pid" 2>/dev/null || true
    fi
  }
  trap shutdown INT TERM

  gunicorn core.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-1}" \
    --threads "${WEB_THREADS:-2}" \
    --timeout "${GUNICORN_TIMEOUT}" \
    --access-logfile - \
    --error-logfile - &
  gunicorn_pid=$!
  wait "$gunicorn_pid"
  shutdown
  wait "$celery_pid" 2>/dev/null || true
else
  exec gunicorn core.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers "${WEB_CONCURRENCY:-1}" \
    --threads "${WEB_THREADS:-2}" \
    --timeout "${GUNICORN_TIMEOUT}" \
    --access-logfile - \
    --error-logfile -
fi
