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
echo "==> Commit and push, then run etc/build.sh + etc/deploy.sh"
