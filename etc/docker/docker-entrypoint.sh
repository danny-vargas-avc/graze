#!/bin/bash
set -e

echo "==> Copying frontend build to shared volume..."
cp -r /app/frontend-dist/* /app/frontend-serve/

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Starting gunicorn..."
exec gunicorn graze_api.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile -
