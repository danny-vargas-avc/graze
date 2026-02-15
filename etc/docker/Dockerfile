# Stage 1: Build Vue frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend

ARG VITE_API_URL=
ARG VITE_MAPBOX_TOKEN

COPY src/graze/package.json src/graze/yarn.lock ./
RUN yarn install --frozen-lockfile

COPY src/graze/ ./
RUN VITE_API_URL=$VITE_API_URL VITE_MAPBOX_TOKEN=$VITE_MAPBOX_TOKEN yarn build

# Stage 2: Django + gunicorn
FROM python:3.9-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY src/django/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/django/ .
COPY --from=frontend-build /app/frontend/dist /app/frontend-dist

COPY etc/docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
