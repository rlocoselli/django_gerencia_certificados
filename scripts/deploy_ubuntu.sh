#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/djangoapp"
REPO_DIR="$(pwd)"
VENV_DIR="$APP_DIR/venv"
APP_CODE_DIR="$APP_DIR/app"
ENV_FILE="/etc/djangoapp.env"
SERVICE_NAME="djangoapp"
GUNICORN_BIND="127.0.0.1:8080"

echo "==> Creating app directories..."
sudo mkdir -p "$APP_DIR"
sudo rsync -a --delete --exclude ".git" --exclude ".github" "$REPO_DIR/" "$APP_CODE_DIR/"
sudo chown -R "$USER":"$USER" "$APP_DIR"

echo "==> Creating/Updating virtualenv..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip wheel
"$VENV_DIR/bin/pip" install -r "$APP_CODE_DIR/requirements.txt"

echo "==> Loading env vars from $ENV_FILE (if present)..."
set +u
if [[ -f "$ENV_FILE" ]]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' "$ENV_FILE" | xargs -d '\n')
fi
set -u

echo "==> Django migrate + collectstatic..."
cd "$APP_CODE_DIR"
"$VENV_DIR/bin/python" manage.py migrate --noinput
"$VENV_DIR/bin/python" manage.py collectstatic --noinput

echo "==> Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
sudo tee "$SERVICE_FILE" >/dev/null <<EOF
[Unit]
Description=Django (gunicorn) service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_CODE_DIR
EnvironmentFile=$ENV_FILE
ExecStart=$VENV_DIR/bin/gunicorn project.wsgi:application --bind $GUNICORN_BIND --workers 3 --access-logfile -
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"
sudo systemctl status "$SERVICE_NAME" --no-pager || true


echo "==> Configuring nginx..."
DOMAIN="${DOMAIN:-_}"
CERTBOT_EMAIL="${CERTBOT_EMAIL:-}"

# Ensure self-signed cert exists (used if certbot not run)
SSL_DIR="/etc/ssl/djangoapp"
sudo mkdir -p "$SSL_DIR"
if [[ ! -f "$SSL_DIR/selfsigned.crt" || ! -f "$SSL_DIR/selfsigned.key" ]]; then
  sudo openssl req -x509 -nodes -newkey rsa:2048 -days 3650 \
    -keyout "$SSL_DIR/selfsigned.key" -out "$SSL_DIR/selfsigned.crt" \
    -subj "/CN=$DOMAIN" >/dev/null 2>&1 || true
fi

NGINX_SITE="/etc/nginx/sites-available/${SERVICE_NAME}"
sudo tee "$NGINX_SITE" >/dev/null <<EOF
server {
    listen 80;
    server_name ${DOMAIN};

    # Redirect all HTTP to HTTPS
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate     $SSL_DIR/selfsigned.crt;
    ssl_certificate_key $SSL_DIR/selfsigned.key;

    location /static/ {
        alias $APP_CODE_DIR/staticfiles/;
    }

    location / {
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_pass http://$GUNICORN_BIND;
    }
}
EOF

sudo ln -sf "$NGINX_SITE" "/etc/nginx/sites-enabled/${SERVICE_NAME}"
sudo nginx -t
sudo systemctl reload nginx

if [[ "$DOMAIN" != "_" && -n "$CERTBOT_EMAIL" ]]; then
  echo "==> Requesting/renewing Let's Encrypt certificate with certbot..."
  sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "$CERTBOT_EMAIL" --redirect || true
else
  echo "==> Using self-signed certificate (no DOMAIN/CERTBOT_EMAIL for Let's Encrypt)."
fi

echo "==> Done. App should be reachable via https://$DOMAIN (or server IP if DOMAIN is '_')."

