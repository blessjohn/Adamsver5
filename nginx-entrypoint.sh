#!/bin/sh
set -e

echo "=== Nginx Entrypoint Script ==="

# Check if SSL certificates exist
if [ -f /etc/letsencrypt/live/adams.org.in/fullchain.pem ] && [ -f /etc/letsencrypt/live/adams.org.in/privkey.pem ]; then
    echo "✓ SSL certificates found - switching to HTTPS configuration"
    cp /tmp/nginx-https.conf /etc/nginx/conf.d/default.conf
else
    echo "✗ SSL certificates not found - using HTTP-only configuration (default)"
    cp /tmp/nginx-http-only.conf /etc/nginx/conf.d/default.conf
fi

# Test nginx configuration
echo "Testing nginx configuration..."
nginx -t

echo "✓ Nginx is ready to start"

