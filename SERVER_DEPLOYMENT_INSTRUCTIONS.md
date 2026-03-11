# Server Deployment Instructions

## 🖥️ For Your Server (admin@ip-172-26-10-8)

Based on your server setup, here are the exact steps to configure paths:

## 📍 Step 1: Find Your Deployment Path

On your server, run:
```bash
pwd
```

This will show your current directory. Common paths:
- `/home/admin/adams-django-main/` (if in home directory)
- `/var/www/adams/adams-django-main/` (standard web server path)
- `/opt/adams/` (alternative)

## 🔧 Step 2: Update Nginx Configuration

### Option A: Use the Setup Script (Recommended)

```bash
# Make script executable
chmod +x setup_server_paths.sh

# Run the script
bash setup_server_paths.sh
```

The script will:
- Detect your current path
- Create media and static directories
- Generate nginx.conf with correct paths
- Create Gunicorn service file

### Option B: Manual Update

1. Edit `nginx.conf` and replace paths:
   ```bash
   nano nginx.conf
   ```

2. Find and replace these lines:
   ```nginx
   # Change from:
   alias /var/www/adams/adams-django-main/media/;
   # To your actual path, e.g.:
   alias /home/admin/adams-django-main/media/;
   ```

3. Do the same for static files:
   ```nginx
   alias /home/admin/adams-django-main/staticfiles/;
   ```

## 📁 Step 3: Create Directories

```bash
# Replace /home/admin/adams-django-main with your actual path
DEPLOY_PATH="/home/admin/adams-django-main"  # UPDATE THIS!

mkdir -p $DEPLOY_PATH/media
mkdir -p $DEPLOY_PATH/staticfiles
chmod 755 $DEPLOY_PATH/media
chmod 755 $DEPLOY_PATH/staticfiles
```

## 🔐 Step 4: Set Permissions

```bash
# Set ownership (adjust user/group as needed)
# If running as 'admin' user:
sudo chown -R admin:admin $DEPLOY_PATH/media
sudo chown -R admin:admin $DEPLOY_PATH/staticfiles

# If using www-data (common for nginx):
sudo chown -R www-data:www-data $DEPLOY_PATH/media
sudo chown -R www-data:www-data $DEPLOY_PATH/staticfiles
```

## 🌐 Step 5: Configure Nginx

```bash
# Copy nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/adams

# Enable the site
sudo ln -s /etc/nginx/sites-available/adams /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## 🚀 Step 6: Configure Gunicorn Service

```bash
# Edit the service file with your path
sudo nano /etc/systemd/system/adams-gunicorn.service
```

Update these lines:
```ini
[Service]
User=admin  # Your username
Group=admin  # Your group
WorkingDirectory=/home/admin/adams-django-main  # Your path
Environment="PATH=/home/admin/adams-django-main/venv/bin"  # Your path
ExecStart=/home/admin/adams-django-main/venv/bin/gunicorn \  # Your path
    --config /home/admin/adams-django-main/gunicorn_config.py \  # Your path
    adams.wsgi:application
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable adams-gunicorn
sudo systemctl start adams-gunicorn
sudo systemctl status adams-gunicorn
```

## ✅ Step 7: Verify Everything Works

```bash
# Check Gunicorn is running
sudo systemctl status adams-gunicorn

# Check Nginx is running
sudo systemctl status nginx

# Test media directory is writable
touch /home/admin/adams-django-main/media/test.txt
rm /home/admin/adams-django-main/media/test.txt

# Check logs if issues
sudo journalctl -u adams-gunicorn -f
sudo tail -f /var/log/nginx/error.log
```

## 📝 Quick Reference

### Common Paths to Update:

1. **nginx.conf**:
   - `/home/admin/adams-django-main/media/`
   - `/home/admin/adams-django-main/staticfiles/`

2. **Gunicorn service** (`/etc/systemd/system/adams-gunicorn.service`):
   - `WorkingDirectory=/home/admin/adams-django-main`
   - `ExecStart=/home/admin/adams-django-main/venv/bin/gunicorn`

3. **Django settings** (already correct):
   - `MEDIA_ROOT = os.path.join(BASE_DIR, "media")` ✅
   - `STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")` ✅

## 🎯 Summary

Your Django app uses **relative paths** (`BASE_DIR/media`), so it will automatically work in any directory!

You just need to:
1. ✅ Update **nginx.conf** paths to match your server
2. ✅ Update **Gunicorn service** paths
3. ✅ Ensure directories exist with proper permissions

The media folder will work perfectly! 🎉
