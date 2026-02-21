#!/bin/bash
# Deploys (or redeploys) the app on the VPS.
# Run from anywhere: ./etc/deploy.sh
set -e

VPS_HOST="graze"
DEPLOY_PATH="/opt/graze"
COMPOSE="docker compose -f etc/docker/docker-compose.yml --env-file etc/docker/.env.production"

echo "==> Starting containers on $VPS_HOST..."
ssh "$VPS_HOST" "cd $DEPLOY_PATH && $COMPOSE up -d"

echo "==> Waiting for services to be healthy..."
ssh "$VPS_HOST" "cd $DEPLOY_PATH && $COMPOSE ps"

echo ""
echo "==> Deployed. Checking web container logs..."
ssh "$VPS_HOST" "cd $DEPLOY_PATH && $COMPOSE logs web --tail 20"
