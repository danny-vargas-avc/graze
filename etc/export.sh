#!/bin/bash
# Exports local database to fixtures for production deployment.
set -e

DJANGO_DIR="$(cd "$(dirname "$0")/../src/django" && pwd)"
FIXTURE="$DJANGO_DIR/fixtures/data.json"

echo "==> Exporting local database..."
cd "$DJANGO_DIR"
python3.9 manage.py dumpdata api --indent 2 -o "$FIXTURE"

echo "==> Exported to src/django/fixtures/data.json"
echo ""
python3.9 -c "
import json
data = json.load(open('$FIXTURE'))
counts = {}
for obj in data:
    model = obj['model'].split('.')[-1]
    counts[model] = counts.get(model, 0) + 1
for model, count in sorted(counts.items()):
    print(f'   {model}: {count}')
print(f'   total: {len(data)} records')
"
echo ""
echo "==> Syncing media files to VPS..."
MEDIA_DIR="$DJANGO_DIR/media/restaurants"
VPS_HOST="graze"
DEPLOY_PATH="/opt/graze"
COMPOSE="docker compose -f etc/docker/docker-compose.yml --env-file etc/docker/.env.production"

rsync -avz "$MEDIA_DIR/" "$VPS_HOST:/tmp/media-upload/"
ssh "$VPS_HOST" "cd $DEPLOY_PATH && $COMPOSE cp /tmp/media-upload web:/app/media/restaurants/ && $COMPOSE exec web bash -c 'cp -r /app/media/restaurants/media-upload/* /app/media/restaurants/ && rm -rf /app/media/restaurants/media-upload'"
echo "==> Media synced."

echo ""
echo "==> Commit and push, then run etc/build.sh + etc/deploy.sh"
