#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput || true

exec gunicorn config.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT:-8000} \
  --workers 2
