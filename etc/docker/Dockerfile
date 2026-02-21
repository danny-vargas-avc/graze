# Stage 1: Build Vue frontend
FROM node:20-alpine AS frontend

WORKDIR /build
COPY src/graze/package.json src/graze/yarn.lock ./
RUN yarn install --frozen-lockfile

COPY src/graze/ ./
ARG VITE_MAPBOX_TOKEN
ENV VITE_MAPBOX_TOKEN=$VITE_MAPBOX_TOKEN
ENV VITE_API_URL=
RUN yarn build

# Stage 2: Python backend + built frontend
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY src/django/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/django/ .
COPY --from=frontend /build/dist /app/frontend-dist

COPY etc/docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/docker-entrypoint.sh"]
