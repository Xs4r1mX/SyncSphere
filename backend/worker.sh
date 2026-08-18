#!/bin/sh
set -eu

# Only the dedicated worker Render service should run this script.
# The API service must keep Docker Command empty so CMD stays ./start.sh.
if [ "${RUN_AS_WORKER:-False}" != "True" ]; then
  echo "Refusing to start: set RUN_AS_WORKER=True on the worker service only."
  echo "The API web service must use ./start.sh (leave Docker Command blank)."
  exit 1
fi

# Free Render "web" service running Celery:
# - tiny HTTP on $PORT for health checks / keep-alive pings
# - Celery worker for transfers and domain events
# No migrate / collectstatic here — the API web service owns those.

python worker_health.py &
health_pid=$!

shutdown() {
  kill -TERM "$celery_pid" 2>/dev/null || true
  kill -TERM "$health_pid" 2>/dev/null || true
}
trap shutdown INT TERM

celery -A core worker \
  --loglevel="${CELERY_LOGLEVEL:-info}" \
  --concurrency="${CELERY_CONCURRENCY:-1}" \
  --queues="${CELERY_QUEUES:-default}" &
celery_pid=$!

wait "$celery_pid"
shutdown
wait "$health_pid" 2>/dev/null || true
