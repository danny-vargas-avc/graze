#!/bin/bash
# Pulls latest code and builds Docker images on the VPS.
# Run from anywhere: ./etc/build.sh
set -e

VPS_HOST="graze"
DEPLOY_PATH="/opt/graze"
COMPOSE="docker compose -f etc/docker/docker-compose.yml --env-file etc/docker/.env.production"

echo "==> Pulling latest code on $VPS_HOST..."
ssh "$VPS_HOST" "cd $DEPLOY_PATH && git pull"

echo "==> Building Docker images..."
ssh "$VPS_HOST" "cd $DEPLOY_PATH && $COMPOSE build"

echo "==> Done. Run etc/deploy.sh to bring it up."
