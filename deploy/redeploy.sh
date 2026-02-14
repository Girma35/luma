#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════
# ReOrder AI — Quick Redeploy (run on Droplet after rsync)
# Usage: sudo bash /root/reorder-ai/deploy/redeploy.sh
# ══════════════════════════════════════════════════════════════
set -euo pipefail

APP_DIR="/home/deploy/reorder-ai"
UPLOAD_DIR="/root/reorder-ai"

echo "── Copying updated files..."
rsync -a --exclude='.venv' --exclude='node_modules' --exclude='.env' --exclude='*.db' \
    "${UPLOAD_DIR}/" "${APP_DIR}/"
chown -R deploy:deploy "${APP_DIR}"

echo "── Updating Python deps..."
sudo -u deploy bash -c "cd ${APP_DIR} && .venv/bin/pip install -r requirements.txt -q"

echo "── Rebuilding dashboard..."
sudo -u deploy bash -c "cd ${APP_DIR}/dashboard && npm ci --production=false && npm run build"

echo "── Running migrations..."
sudo -u deploy bash -c "cd ${APP_DIR} && .venv/bin/alembic upgrade head"

echo "── Restarting services..."
systemctl restart reorder-api
systemctl restart reorder-dashboard

echo "── Checking health..."
sleep 3
curl -sf http://127.0.0.1:8000/api/v1/health | python3 -m json.tool || echo "⚠ API not responding yet — check: journalctl -u reorder-api -f"

echo "── Done!"
