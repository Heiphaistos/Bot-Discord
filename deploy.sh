#!/bin/bash
# Deploy Bot-Discord sur le VPS
set -e

DEPLOY_DIR="/opt/bot-discord"
COMPOSE="docker compose -f docker/docker-compose.yml"

echo "[deploy] Mise à jour du code..."
git pull origin master

echo "[deploy] Build de l'image..."
$COMPOSE build --no-cache

echo "[deploy] Redémarrage du container..."
$COMPOSE down
$COMPOSE up -d

echo "[deploy] Statut:"
$COMPOSE ps

echo "[deploy] Done ✅"
