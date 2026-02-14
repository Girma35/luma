#!/usr/bin/env bash
# ══════════════════════════════════════════════════════════════
# ReOrder AI — DigitalOcean Droplet Setup Script (Fedora)
# Target: Fedora 39+, 2 GB RAM / 1 vCPU
#
# Run as root on the Droplet:
#   bash /root/reorder-ai/deploy/setup.sh
# ══════════════════════════════════════════════════════════════
set -euo pipefail

DEPLOY_USER="deploy"
APP_DIR="/home/${DEPLOY_USER}/reorder-ai"
DOMAIN="${DOMAIN:-_}"
DB_PASSWORD="${DB_PASSWORD:-$(openssl rand -base64 24)}"

echo "══════════════════════════════════════════════════════════"
echo "  ReOrder AI — Fedora Droplet Setup"
echo "══════════════════════════════════════════════════════════"

# ── 1. System updates ────────────────────────────────────────
echo "[1/9] Updating system packages..."
dnf update -y -q

# ── 2. Install dependencies ──────────────────────────────────
echo "[2/9] Installing Nginx, PostgreSQL, Python, Node.js..."
dnf install -y -q \
    nginx \
    postgresql-server postgresql-contrib \
    python3 python3-pip python3-devel \
    certbot python3-certbot-nginx \
    git curl firewalld fail2ban \
    gcc libffi-devel

# Install Node.js 20 LTS via dnf module
if ! command -v node &>/dev/null; then
    dnf module install -y -q nodejs:20/common || dnf install -y -q nodejs
fi

echo "  Python: $(python3 --version)"
echo "  Node:   $(node --version)"
echo "  Nginx:  $(nginx -v 2>&1)"

# ── 3. Create deploy user ───────────────────────────────────
echo "[3/9] Creating deploy user..."
if ! id "${DEPLOY_USER}" &>/dev/null; then
    useradd -m -s /bin/bash "${DEPLOY_USER}"
fi

# ── 4. Firewall ─────────────────────────────────────────────
echo "[4/9] Configuring firewall..."
systemctl enable --now firewalld
firewall-cmd --permanent --add-service=ssh
firewall-cmd --permanent --add-service=http
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
echo "  Firewall: SSH + HTTP/HTTPS allowed"

# ── 5. PostgreSQL ────────────────────────────────────────────
echo "[5/9] Setting up PostgreSQL..."
# Initialize DB if not already done
if [ ! -f /var/lib/pgsql/data/PG_VERSION ]; then
    postgresql-setup --initdb
fi

# Start PostgreSQL
systemctl enable --now postgresql

# Configure pg_hba.conf for local password auth
PG_HBA=$(sudo -u postgres psql -t -c "SHOW hba_file;" | xargs)
if ! grep -q "reorder" "${PG_HBA}" 2>/dev/null; then
    # Add password auth for reorder user before the default ident line
    sed -i '/^local.*all.*all.*peer/i local   reorder_ai   reorder                          md5' "${PG_HBA}"
    sed -i '/^host.*all.*all.*127/i host    reorder_ai   reorder   127.0.0.1/32          md5' "${PG_HBA}"
    systemctl reload postgresql
fi

# Create user and database
sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='reorder'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER reorder WITH PASSWORD '${DB_PASSWORD}';"
sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='reorder_ai'" | grep -q 1 || \
    sudo -u postgres createdb -O reorder reorder_ai
echo "  Database: reorder_ai (user: reorder)"
echo "  DB Password: ${DB_PASSWORD}"
echo "  ↑ SAVE THIS — you'll need it for .env"

# ── 6. Copy project to deploy user ──────────────────────────
echo "[6/9] Setting up project files..."
if [ -d "/root/reorder-ai" ]; then
    # Copy from root upload to deploy user's home
    if [ -d "${APP_DIR}" ]; then
        rm -rf "${APP_DIR}"
    fi
    cp -r /root/reorder-ai "${APP_DIR}"
    chown -R "${DEPLOY_USER}:${DEPLOY_USER}" "${APP_DIR}"
    echo "  Copied /root/reorder-ai → ${APP_DIR}"
else
    echo "  ERROR: /root/reorder-ai not found!"
    echo "  Upload your project first: rsync -avz ./ root@droplet:/root/reorder-ai/"
    exit 1
fi

# Python backend
echo "[6/9] Setting up Python backend..."
sudo -u "${DEPLOY_USER}" bash -c "
    cd '${APP_DIR}'
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip -q
    .venv/bin/pip install -r requirements.txt -q
"

# Astro dashboard
echo "[6/9] Building Astro dashboard..."
sudo -u "${DEPLOY_USER}" bash -c "
    cd '${APP_DIR}/dashboard'
    npm ci --production=false
    npm run build
"

# ── 7. Environment file ─────────────────────────────────────
echo "[7/9] Creating .env..."
if [ ! -f "${APP_DIR}/.env" ]; then
    API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))")
    cat > "${APP_DIR}/.env" <<ENVEOF
ENVIRONMENT=production
DATABASE_URL=postgresql://reorder:${DB_PASSWORD}@localhost:5432/reorder_ai
PORT=8000
LOG_LEVEL=WARNING
CORS_ORIGINS=https://${DOMAIN}
API_SECRET_KEY=${API_KEY}
RATE_LIMIT_DEFAULT=60/minute
RATE_LIMIT_SYNC=10/minute
FORECAST_PROVIDER=simple
FORECAST_REFRESH_HOURS=24
# AWS — uncomment and fill when ready:
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
ENVEOF
    chown "${DEPLOY_USER}:${DEPLOY_USER}" "${APP_DIR}/.env"
    chmod 600 "${APP_DIR}/.env"
    echo "  .env created (edit AWS keys later)"
else
    echo "  .env already exists, skipping"
fi

# ── 8. Run database migrations ───────────────────────────────
echo "[8/9] Running database migrations..."
sudo -u "${DEPLOY_USER}" bash -c "
    cd '${APP_DIR}'
    .venv/bin/alembic upgrade head
"

# ── 9. Systemd services + Nginx ─────────────────────────────
echo "[9/9] Installing services..."

# API service
cp "${APP_DIR}/deploy/reorder-api.service" /etc/systemd/system/
# Dashboard service
cp "${APP_DIR}/deploy/reorder-dashboard.service" /etc/systemd/system/

systemctl daemon-reload
systemctl enable --now reorder-api
systemctl enable --now reorder-dashboard

# Nginx
cp "${APP_DIR}/deploy/nginx.conf" /etc/nginx/conf.d/reorder-ai.conf
# Remove default welcome page if exists
rm -f /etc/nginx/conf.d/default.conf 2>/dev/null || true
# SELinux: allow Nginx to connect to backend
setsebool -P httpd_can_network_connect 1 2>/dev/null || true
nginx -t && systemctl enable --now nginx && systemctl reload nginx

# ── Done ─────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════════════════════"
echo "  ✓  ReOrder AI deployed!"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "  Dashboard:  http://${DOMAIN}"
echo "  API:        http://${DOMAIN}/api/v1/health"
echo "  API Docs:   http://${DOMAIN}/api/v1/docs"
echo ""
echo "  DB Password:  ${DB_PASSWORD}"
echo "  API Key:      (check ${APP_DIR}/.env)"
echo ""
echo "  Next steps:"
echo "    1. Edit ${APP_DIR}/.env with your AWS keys"
echo "    2. Update server_name in /etc/nginx/conf.d/reorder-ai.conf"
echo "    3. Run: certbot --nginx -d yourdomain.com"
echo "    4. Restart: systemctl restart reorder-api reorder-dashboard"
echo ""
echo "  Useful commands:"
echo "    journalctl -u reorder-api -f        # API logs"
echo "    journalctl -u reorder-dashboard -f  # Dashboard logs"
echo "    systemctl restart reorder-api        # Restart API"
echo "    systemctl restart reorder-dashboard  # Restart Dashboard"
echo "══════════════════════════════════════════════════════════"
