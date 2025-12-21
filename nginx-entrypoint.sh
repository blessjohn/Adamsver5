#!/bin/sh

# Check if SSL certificates exist
if [ -f /etc/letsencrypt/live/adams.org.in/fullchain.pem ] && [ -f /etc/letsencrypt/live/adams.org.in/privkey.pem ]; then
    echo "SSL certificates found - using HTTPS configuration"
    # SSL certificates exist, use full config with HTTPS (already copied as default.conf)
else
    echo "SSL certificates not found - using HTTP only configuration"
    # Use HTTP-only config for local development
    cp /etc/nginx/conf.d/nginx-http-only.conf /etc/nginx/conf.d/default.conf
fi

# Test nginx configuration
nginx -t || {
    echo "Nginx configuration test failed!"
    exit 1
}

echo "Nginx configuration is valid"

