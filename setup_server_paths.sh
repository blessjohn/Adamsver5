#!/bin/bash
# Server Path Configuration Script
# This script helps configure paths for your server deployment

echo "=========================================="
echo "ADAMS Django Server Path Configuration"
echo "=========================================="
echo ""

# Detect current directory
CURRENT_DIR=$(pwd)
echo "Current directory: $CURRENT_DIR"
echo ""

# Ask user to confirm or set deployment path
read -p "Enter your deployment path (or press Enter to use current: $CURRENT_DIR): " DEPLOY_PATH
DEPLOY_PATH=${DEPLOY_PATH:-$CURRENT_DIR}

# Normalize path (remove trailing slash)
DEPLOY_PATH=$(echo "$DEPLOY_PATH" | sed 's:/*$::')

echo ""
echo "Using deployment path: $DEPLOY_PATH"
echo ""

# Set paths
MEDIA_PATH="$DEPLOY_PATH/media"
STATIC_PATH="$DEPLOY_PATH/staticfiles"

# Create directories if they don't exist
echo "Creating directories..."
mkdir -p "$MEDIA_PATH"
mkdir -p "$STATIC_PATH"
echo "[OK] Directories created"
echo ""

# Set permissions
echo "Setting permissions..."
chmod 755 "$MEDIA_PATH"
chmod 755 "$STATIC_PATH"
echo "[OK] Permissions set"
echo ""

# Create nginx configuration with correct paths
echo "Creating nginx configuration..."
cat > nginx.conf.server <<EOF
# Nginx configuration for ADAMS Django Application
# Deployment Path: $DEPLOY_PATH
# Generated on: $(date)

upstream django {
    server 127.0.0.1:8000;
    keepalive 32;
}

# HTTP server - redirects to HTTPS in production
server {
    listen 80;
    listen [::]:80;
    server_name adams.org.in www.adams.org.in;

    # Redirect to HTTPS in production
    return 301 https://\$host\$request_uri;
}

# HTTPS server for production
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name adams.org.in www.adams.org.in;

    ssl_certificate /etc/letsencrypt/live/adams.org.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/adams.org.in/privkey.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 100M;

    # Static files
    location /static/ {
        alias $STATIC_PATH/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (user uploads)
    location /media/ {
        alias $MEDIA_PATH/;
        expires 7d;
        add_header Cache-Control "public";
        autoindex off;
    }

    # Proxy to Django
    location / {
        proxy_pass http://django;
        proxy_http_version 1.1;
        
        # Headers - critical for HTTPS/SSL proxy
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_added_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        proxy_set_header Connection "";
        
        # Buffering and timeouts to prevent 502 errors
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
        proxy_send_timeout 300s;
        proxy_request_buffering off;
    }
}
EOF

echo "[OK] Nginx configuration created: nginx.conf.server"
echo ""

# Create systemd service file
echo "Creating Gunicorn systemd service..."
cat > adams-gunicorn.service <<EOF
[Unit]
Description=ADAMS Gunicorn daemon
After=network.target postgresql.service

[Service]
User=admin
Group=admin
WorkingDirectory=$DEPLOY_PATH
Environment="PATH=$DEPLOY_PATH/venv/bin"
ExecStart=$DEPLOY_PATH/venv/bin/gunicorn \\
    --config $DEPLOY_PATH/gunicorn_config.py \\
    adams.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo "[OK] Gunicorn service file created: adams-gunicorn.service"
echo ""

# Display summary
echo "=========================================="
echo "Configuration Summary"
echo "=========================================="
echo "Deployment Path: $DEPLOY_PATH"
echo "Media Path: $MEDIA_PATH"
echo "Static Path: $STATIC_PATH"
echo ""
echo "Next Steps:"
echo "1. Review nginx.conf.server and update if needed"
echo "2. Copy to nginx: sudo cp nginx.conf.server /etc/nginx/sites-available/adams"
echo "3. Enable site: sudo ln -s /etc/nginx/sites-available/adams /etc/nginx/sites-enabled/"
echo "4. Test nginx: sudo nginx -t"
echo "5. Reload nginx: sudo systemctl reload nginx"
echo ""
echo "6. Copy Gunicorn service: sudo cp adams-gunicorn.service /etc/systemd/system/"
echo "7. Enable service: sudo systemctl daemon-reload"
echo "8. Start service: sudo systemctl enable adams-gunicorn && sudo systemctl start adams-gunicorn"
echo ""
echo "=========================================="
