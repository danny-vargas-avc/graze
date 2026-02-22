#!/bin/bash
set -e

echo "==> Copying frontend build to shared volume..."
rm -rf /app/frontend-serve/*
cp -r /app/frontend-dist/* /app/frontend-serve/

echo "==> Collecting static files..."
python manage.py collectstatic --noinput

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Loading data fixtures..."
python manage.py loaddata fixtures/data.json

echo "==> Starting gunicorn..."
exec gunicorn graze_api.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --access-logfile - \
    --error-logfile -
