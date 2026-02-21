# Graze

Find high-protein meals at fast-casual restaurants near you. Vue 3 frontend + Django REST backend with 7 restaurants, 200+ menu items, and 4,000+ locations.

## Project Structure

```
src/
  django/          Django REST API (Python 3.9)
  graze/           Vue 3 + Vite frontend
etc/
  docker/          Docker deployment files
  data/            Nutrition PDFs, CSVs, location data
  scripts/         Data scrapers and utilities
  build.sh         Build on VPS (pulls + docker build)
  deploy.sh        Deploy on VPS (docker up)
  start.sh         Local dev server (backend)
```

## Local Development

**Backend:**

```bash
./etc/start.sh              # starts Django on :8000 (creates venv, migrates)
./etc/start.sh --import     # also imports menu data
```

**Frontend:**

```bash
cd src/graze
yarn install
yarn dev                    # starts Vite on :5173, proxies /api to :8000
```

**Management commands** (from `src/django/`):

```bash
python3.9 manage.py import_data        # import menu items
python3.9 manage.py import_locations    # import restaurant locations
python3.9 manage.py import_byo         # import BYO calculator ingredients
```

## Production Deployment

### Architecture

```
Internet -> Cloudflare (SSL + CDN) -> VPS:80 -> nginx
                                                 |-- /             -> Vue SPA
                                                 |-- /api/, /admin -> gunicorn (Django)
                                                 |-- /static/      -> gunicorn (WhiteNoise)
                                                 |-- /media/       -> nginx (direct)
```

Three Docker services: `db` (Postgres 16), `web` (Django + gunicorn), `nginx`.

### First-Time VPS Setup

1. Clone repo to `/opt/graze`
2. Copy and fill in env:
   ```bash
   cp etc/docker/.env.production.example etc/docker/.env.production
   ```
3. Build and deploy:
   ```bash
   ./etc/build.sh
   ./etc/deploy.sh
   ```
4. Create superuser:
   ```bash
   ssh graze "cd /opt/graze && docker compose -f etc/docker/docker-compose.yml --env-file etc/docker/.env.production exec web python manage.py createsuperuser"
   ```
5. Import data (dump from local SQLite first):
   ```bash
   # Local: dump data
   cd src/django && python3.9 manage.py dumpdata --natural-foreign -o data.json

   # Remote: load data
   scp src/django/data.json graze:/opt/graze/src/django/
   ssh graze "cd /opt/graze && docker compose -f etc/docker/docker-compose.yml --env-file etc/docker/.env.production exec web python manage.py loaddata data.json"
   ```
6. Copy media files:
   ```bash
   scp -r src/django/media/* graze:/opt/graze/media/
   ```
7. Cloudflare: A record -> VPS IP, SSL mode -> "Full"

### Updating

From your local machine:

```bash
git push                  # push changes
./etc/build.sh            # pulls on VPS + rebuilds images
./etc/deploy.sh           # restarts containers (runs migrations automatically)
```

### Useful Commands

```bash
# View logs
ssh graze "cd /opt/graze && docker compose -f etc/docker/docker-compose.yml --env-file etc/docker/.env.production logs web --tail 50"

# Django shell
ssh graze "cd /opt/graze && docker compose -f etc/docker/docker-compose.yml --env-file etc/docker/.env.production exec web python manage.py shell"

# Container status
ssh graze "cd /opt/graze && docker compose -f etc/docker/docker-compose.yml --env-file etc/docker/.env.production ps"
```
