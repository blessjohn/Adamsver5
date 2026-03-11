#!/bin/bash
# Quick script to update nginx.conf with your server path

echo "ADAMS Django - Server Path Updater"
echo "=================================="
echo ""

# Get current directory
CURRENT_DIR=$(pwd)
echo "Current directory: $CURRENT_DIR"
echo ""

# Ask for deployment path
read -p "Enter your deployment path (press Enter for current: $CURRENT_DIR): " DEPLOY_PATH
DEPLOY_PATH=${DEPLOY_PATH:-$CURRENT_DIR}
DEPLOY_PATH=$(echo "$DEPLOY_PATH" | sed 's:/*$::')

echo ""
echo "Updating nginx.conf with path: $DEPLOY_PATH"
echo ""

# Update nginx.conf
sed -i "s|alias /home/admin/adams-django-main/staticfiles/|alias $DEPLOY_PATH/staticfiles/|g" nginx.conf
sed -i "s|alias /home/admin/adams-django-main/media/|alias $DEPLOY_PATH/media/|g" nginx.conf
sed -i "s|alias /var/www/adams/staticfiles/|alias $DEPLOY_PATH/staticfiles/|g" nginx.conf
sed -i "s|alias /var/www/adams/adams-django-main/media/|alias $DEPLOY_PATH/media/|g" nginx.conf

echo "[OK] nginx.conf updated!"
echo ""
echo "Media path: $DEPLOY_PATH/media/"
echo "Static path: $DEPLOY_PATH/staticfiles/"
echo ""
echo "Next steps:"
echo "1. sudo cp nginx.conf /etc/nginx/sites-available/adams"
echo "2. sudo nginx -t"
echo "3. sudo systemctl reload nginx"
