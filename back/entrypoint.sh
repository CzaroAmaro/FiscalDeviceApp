#!/bin/sh
set -e

python -m celery -A config worker -l info &

exec gunicorn config.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT:-8000}