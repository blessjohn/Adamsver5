# AWS Lightsail Deployment Guide

This guide covers deploying the ADAMS Django application directly on AWS Lightsail without Docker.

## Prerequisites

- AWS Lightsail instance (Ubuntu 22.04 LTS recommended)
- Domain name configured (adams.org.in)
- SSH access to the instance

## Stack Components

- **Django**: Web application framework
- **Gunicorn**: WSGI HTTP server
- **Nginx**: Reverse proxy and web server
- **PostgreSQL**: Database server
- **MinIO**: Object storage for media files

## Step 1: Server Setup

### Update system packages
```bash
sudo apt update && sudo apt upgrade -y
```

### Install required packages
```bash
sudo apt install -y python3-pip python3-venv postgresql postgresql-contrib nginx certbot python3-certbot-nginx
```

### Install MinIO
```bash
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/
```

## Step 2: Database Setup

### Create PostgreSQL database and user
```bash
sudo -u postgres psql
```

In PostgreSQL shell:
```sql
CREATE DATABASE adamsdb;
CREATE USER admin_adams WITH PASSWORD 'your_secure_password';
ALTER ROLE admin_adams SET client_encoding TO 'utf8';
ALTER ROLE admin_adams SET default_transaction_isolation TO 'read committed';
ALTER ROLE admin_adams SET timezone TO 'Asia/Kolkata';
GRANT ALL PRIVILEGES ON DATABASE adamsdb TO admin_adams;
\q
```

### Configure PostgreSQL for remote/local access
Edit `/etc/postgresql/*/main/postgresql.conf`:
```
listen_addresses = 'localhost'
```

Edit `/etc/postgresql/*/main/pg_hba.conf`:
```
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Step 3: MinIO Setup

### Create MinIO data directory
```bash
sudo mkdir -p /opt/minio/data
sudo chown -R $USER:$USER /opt/minio
```

### Create MinIO systemd service
Create `/etc/systemd/system/minio.service`:
```ini
[Unit]
Description=MinIO Object Storage
After=network.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
ExecStart=/usr/local/bin/minio server /opt/minio/data --console-address ":9001"
Restart=always
Environment="MINIO_ROOT_USER=fire_user"
Environment="MINIO_ROOT_PASSWORD=fire_pasword"

[Install]
WantedBy=multi-user.target
```

### Start MinIO
```bash
sudo systemctl daemon-reload
sudo systemctl enable minio
sudo systemctl start minio
```

Verify MinIO is running:
```bash
curl http://localhost:9000/minio/health/live
```

## Step 4: Application Deployment

### Clone/Upload application
```bash
cd /var/www
sudo mkdir -p adams
sudo chown -R $USER:$USER adams
cd adams
# Upload your application files here
```

### Create Python virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Configure environment variables
Create `.env` file in project root:
```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG_MODE=false

# Hosts & CSRF
ALLOWED_HOSTS=adams.org.in,www.adams.org.in,13.126.176.168
CSRF_TRUSTED_ORIGINS=https://adams.org.in,https://www.adams.org.in,https://13.126.176.168

# PostgreSQL Database
DB_NAME=adamsdb
DB_USER=admin_adams
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# MinIO
MINIO_URL=localhost:9000
MINIO_ACCESS_KEY=fire_user
MINIO_SECRET_KEY=fire_pasword
MINIO_BUCKET_NAME=adams

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.hostinger.com
EMAIL_HOST_USER=officedesk@adams.org.in
EMAIL_HOST_PASSWORD=your_email_password
```

**Important**: Load environment variables. You can:
1. Use a `.env` file with `python-dotenv`
2. Export them in systemd service file
3. Use `/etc/environment` (less secure)

### Run migrations and collect static files
```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

## Step 5: Gunicorn Setup

### Create Gunicorn systemd service
Create `/etc/systemd/system/adams-gunicorn.service`:
```ini
[Unit]
Description=ADAMS Gunicorn daemon
After=network.target postgresql.service

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/var/www/adams/adams-django-main
Environment="PATH=/var/www/adams/adams-django-main/venv/bin"
ExecStart=/var/www/adams/adams-django-main/venv/bin/gunicorn \
    --config /var/www/adams/adams-django-main/gunicorn_config.py \
    adams.wsgi:application

Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Note**: Update paths to match your actual deployment directory.

### Start Gunicorn
```bash
sudo systemctl daemon-reload
sudo systemctl enable adams-gunicorn
sudo systemctl start adams-gunicorn
sudo systemctl status adams-gunicorn
```

## Step 6: Nginx Configuration

### Update nginx.conf paths
Edit `nginx.conf` and update the static files path:
```nginx
location /static/ {
    alias /var/www/adams/adams-django-main/staticfiles/;
    ...
}
```

### Copy nginx configuration
```bash
sudo cp nginx.conf /etc/nginx/sites-available/adams
sudo ln -s /etc/nginx/sites-available/adams /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default if needed
```

### Test and reload Nginx
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Step 7: SSL Certificate Setup

### Obtain Let's Encrypt certificate
```bash
sudo certbot --nginx -d adams.org.in -d www.adams.org.in
```

### Auto-renewal (already configured by certbot)
```bash
sudo certbot renew --dry-run
```

## Step 8: Firewall Configuration

### Configure AWS Lightsail firewall
In Lightsail console, open ports:
- 80 (HTTP)
- 443 (HTTPS)
- 22 (SSH)
- 9000 (MinIO API - optional, can be restricted)
- 9001 (MinIO Console - optional, can be restricted)

### Configure UFW (if using)
```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Step 9: Verification

### Check all services
```bash
sudo systemctl status adams-gunicorn
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status minio
```

### Test application
```bash
curl http://localhost:8000/health/
curl http://localhost/
```

### Check logs
```bash
# Gunicorn logs
sudo journalctl -u adams-gunicorn -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Django logs (if configured)
tail -f /var/www/adams/adams-django-main/logs/*.log
```

## Troubleshooting

### 502 Bad Gateway
- Check Gunicorn is running: `sudo systemctl status adams-gunicorn`
- Check Gunicorn logs: `sudo journalctl -u adams-gunicorn -n 50`
- Verify Gunicorn is listening: `sudo netstat -tlnp | grep 8000`
- Check Nginx error log: `sudo tail -f /var/log/nginx/error.log`

### CSRF Errors
- Verify `CSRF_TRUSTED_ORIGINS` includes your domain
- Check `SECURE_PROXY_SSL_HEADER` is set correctly
- Verify Nginx is sending `X-Forwarded-Proto` header

### Static files not loading
- Verify `STATIC_ROOT` path matches Nginx `alias` path
- Run `python manage.py collectstatic --noinput`
- Check file permissions: `sudo chown -R www-data:www-data /var/www/adams/adams-django-main/staticfiles`

### MinIO connection errors
- Verify MinIO is running: `sudo systemctl status minio`
- Check `MINIO_URL` is set to `localhost:9000` (not `minio:9000`)
- Test connection: `curl http://localhost:9000/minio/health/live`

### Database connection errors
- Verify PostgreSQL is running: `sudo systemctl status postgresql`
- Check database credentials in `.env`
- Test connection: `psql -U admin_adams -d adamsdb -h localhost`

## Maintenance

### Update application
```bash
cd /var/www/adams/adams-django-main
source venv/bin/activate
git pull  # or upload new files
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart adams-gunicorn
```

### Backup database
```bash
pg_dump -U admin_adams adamsdb > backup_$(date +%Y%m%d).sql
```

### Monitor resources
```bash
htop
df -h
free -h
```

## Security Notes

1. **Never commit `.env` file** - Keep secrets out of version control
2. **Use strong passwords** - For database, MinIO, and Django secret key
3. **Keep system updated** - Regular `apt update && apt upgrade`
4. **Restrict MinIO ports** - Only expose 9000/9001 if needed externally
5. **Regular backups** - Database and MinIO data
6. **Monitor logs** - Set up log rotation and monitoring
