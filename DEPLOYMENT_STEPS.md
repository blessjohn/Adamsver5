# 🚀 ADAMS Django Application - Deployment Steps

Complete step-by-step guide for deploying the ADAMS Django application using Docker.

## 📋 Pre-Deployment Checklist

- [ ] Server with Docker and Docker Compose installed
- [ ] Domain name configured (adams.org.in, www.adams.org.in)
- [ ] SSL certificate (Let's Encrypt recommended)
- [ ] Firewall configured (ports 80, 443, 8000, 9000, 9001)
- [ ] Email SMTP credentials ready
- [ ] Backup strategy planned

---

## 🖥️ Server Requirements

- **OS**: Ubuntu 22.04 LTS (recommended) or any Linux with Docker support
- **RAM**: Minimum 2GB (4GB+ recommended)
- **Storage**: Minimum 20GB (50GB+ recommended)
- **CPU**: 2+ cores recommended
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

---

## 📦 Step 1: Server Setup

### 1.1 Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 1.2 Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (optional, for non-sudo usage)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

### 1.3 Install Nginx (for reverse proxy)

```bash
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx
```

### 1.4 Install Certbot (for SSL)

```bash
sudo apt install certbot python3-certbot-nginx -y
```

---

## 📥 Step 2: Deploy Application Code

### 2.1 Clone or Upload Code

```bash
# Option 1: Clone from Git
git clone <your-repository-url>
cd adams-django-main

# Option 2: Upload via SCP/SFTP
# Upload the entire project directory to /opt/adams-django-main
```

### 2.2 Navigate to Project Directory

```bash
cd /opt/adams-django-main  # or your project path
```

---

## ⚙️ Step 3: Configure Environment Variables

### 3.1 Create `.env` File

```bash
cp docker-compose.env.example .env
nano .env  # or use your preferred editor
```

### 3.2 Configure Production Settings

Edit `.env` with production values:

```bash
# Django Configuration
DJANGO_SECRET_KEY=<generate-strong-secret-key>
DEBUG_MODE=false

# Hosts & CSRF
ALLOWED_HOSTS=adams.org.in,www.adams.org.in,<your-server-ip>
CSRF_TRUSTED_ORIGINS=https://adams.org.in,https://www.adams.org.in

# Database Configuration
USE_SQLITE=false
DB_NAME=adamsdb
DB_USER=admin_adams
DB_PASSWORD=<strong-database-password>
DB_HOST=db
DB_PORT=5432

# MinIO Configuration
MINIO_URL=minio:9000
MINIO_ACCESS_KEY=<secure-access-key>
MINIO_SECRET_KEY=<secure-secret-key>
MINIO_BUCKET_NAME=adams
MINIO_ROOT_USER=<secure-root-user>
MINIO_ROOT_PASSWORD=<secure-root-password>
MINIO_SECURE=false

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.hostinger.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=officedesk@adams.org.in
EMAIL_HOST_PASSWORD=<your-email-password>
```

### 3.3 Generate Secret Key

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Important**: Use strong, unique passwords for:
- `DJANGO_SECRET_KEY`
- `DB_PASSWORD`
- `MINIO_ROOT_PASSWORD`
- `MINIO_SECRET_KEY`

---

## 🔒 Step 4: Configure Nginx Reverse Proxy

### 4.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/adams
```

### 4.2 Add Configuration

```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name adams.org.in www.adams.org.in;

    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    # Redirect all other traffic to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS - Main Application
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name adams.org.in www.adams.org.in;

    # SSL Configuration (will be updated by Certbot)
    ssl_certificate /etc/letsencrypt/live/adams.org.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/adams.org.in/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Max upload size
    client_max_body_size 100M;

    # Proxy to Django
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header Connection "";
        proxy_buffering off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Static files (served by WhiteNoise in Docker, but can be optimized)
    location /static/ {
        proxy_pass http://127.0.0.1:8000;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files (served from MinIO via Django)
    location /media/ {
        proxy_pass http://127.0.0.1:8000;
        expires 7d;
        add_header Cache-Control "public";
    }
}
```

### 4.3 Enable Site

```bash
sudo ln -s /etc/nginx/sites-available/adams /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

---

## 🔐 Step 5: Setup SSL Certificate

### 5.1 Obtain SSL Certificate

```bash
sudo certbot --nginx -d adams.org.in -d www.adams.org.in
```

Follow the prompts:
- Enter email address
- Agree to terms
- Choose whether to redirect HTTP to HTTPS (recommended: Yes)

### 5.2 Auto-Renewal Setup

Certbot automatically sets up renewal. Test it:

```bash
sudo certbot renew --dry-run
```

---

## 🐳 Step 6: Deploy with Docker

### 6.1 Build and Start Services

```bash
# Build and start all services
docker-compose up -d --build

# View logs
docker-compose logs -f
```

### 6.2 Verify Services

```bash
# Check service status
docker-compose ps

# Check logs
docker-compose logs web
docker-compose logs db
docker-compose logs minio
```

All services should show as "Up" and "healthy".

---

## ✅ Step 7: Post-Deployment Verification

### 7.1 Check Application

```bash
# Test from server
curl http://localhost:8000/health/

# Test from browser
# Visit: https://adams.org.in
```

### 7.2 Verify Admin Access

1. Go to: `https://adams.org.in/admin/`
2. Login with:
   - Username: `techbless`
   - Password: `admin123` (change immediately!)

### 7.3 Check MinIO Console

1. Go to: `http://<your-server-ip>:9001`
2. Login with MinIO credentials from `.env`
3. Verify bucket `adams` exists and contains files

### 7.4 Test File Upload

1. Register a test user
2. Upload a file
3. Verify it appears in MinIO console

---

## 🔧 Step 8: Production Optimizations

### 8.1 Change Admin Password

```bash
docker-compose exec web python manage.py changepassword techbless
```

### 8.2 Set Up Backups

Create backup script `/opt/backup-adams.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/adams"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
docker-compose exec -T db pg_dump -U admin_adams adamsdb > $BACKUP_DIR/db_$DATE.sql

# Backup MinIO data
docker run --rm -v adams-django-main_minio_data:/data -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/minio_$DATE.tar.gz -C /data .

# Keep only last 7 days
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable and schedule:

```bash
chmod +x /opt/backup-adams.sh
crontab -e
# Add: 0 2 * * * /opt/backup-adams.sh
```

### 8.3 Set Up Log Rotation

```bash
sudo nano /etc/logrotate.d/adams-docker
```

Add:

```
/var/lib/docker/containers/*/*.log {
    rotate 7
    daily
    compress
    size=1M
    missingok
    delaycompress
    copytruncate
}
```

### 8.4 Monitor Resources

```bash
# Install monitoring tools
sudo apt install htop -y

# Check container stats
docker stats
```

---

## 🔄 Step 9: Maintenance Commands

### 9.1 Update Application

```bash
cd /opt/adams-django-main
git pull  # If using Git
docker-compose up -d --build
```

### 9.2 View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### 9.3 Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
```

### 9.4 Run Django Commands

```bash
# Migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Shell access
docker-compose exec web python manage.py shell
```

### 9.5 Backup Database

```bash
docker-compose exec -T db pg_dump -U admin_adams adamsdb > backup.sql
```

### 9.6 Restore Database

```bash
docker-compose exec -T db psql -U admin_adams adamsdb < backup.sql
```

---

## 🚨 Step 10: Troubleshooting

### Application Not Accessible

```bash
# Check if containers are running
docker-compose ps

# Check logs
docker-compose logs web

# Check Nginx
sudo nginx -t
sudo systemctl status nginx

# Check firewall
sudo ufw status
```

### Database Connection Issues

```bash
# Check database logs
docker-compose logs db

# Test connection
docker-compose exec web python -c "import psycopg2; psycopg2.connect(dbname='adamsdb', user='admin_adams', password='your_password', host='db')"
```

### MinIO Connection Issues

```bash
# Check MinIO logs
docker-compose logs minio

# Access MinIO console
# http://<server-ip>:9001
```

### SSL Certificate Issues

```bash
# Renew certificate
sudo certbot renew

# Check certificate status
sudo certbot certificates
```

---

## 📊 Step 11: Monitoring & Alerts

### 11.1 Set Up Health Checks

Create health check script:

```bash
#!/bin/bash
# /opt/health-check.sh

if ! curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "Application is down!" | mail -s "ADAMS Alert" admin@adams.org.in
    docker-compose restart web
fi
```

### 11.2 Monitor Disk Space

```bash
df -h
docker system df
```

### 11.3 Monitor Container Resources

```bash
docker stats --no-stream
```

---

## 🔐 Security Checklist

- [ ] Changed default admin password
- [ ] Strong database passwords set
- [ ] Strong MinIO credentials set
- [ ] SSL certificate installed and auto-renewing
- [ ] Firewall configured (only necessary ports open)
- [ ] Regular backups scheduled
- [ ] Log rotation configured
- [ ] DEBUG_MODE=false in production
- [ ] ALLOWED_HOSTS configured correctly
- [ ] CSRF_TRUSTED_ORIGINS configured

---

## 📞 Support & Maintenance

### Regular Tasks

- **Daily**: Check application logs
- **Weekly**: Review backups
- **Monthly**: Update dependencies
- **Quarterly**: Security audit

### Important Files

- `.env` - Environment variables (keep secure!)
- `docker-compose.yml` - Service configuration
- `/etc/nginx/sites-available/adams` - Nginx config
- `/opt/backups/adams/` - Backup directory

---

## 🎉 Deployment Complete!

Your application should now be accessible at:
- **Main Site**: https://adams.org.in
- **Admin Panel**: https://adams.org.in/admin/
- **MinIO Console**: http://<server-ip>:9001

**Next Steps:**
1. Change admin password immediately
2. Test all functionality
3. Set up monitoring
4. Schedule regular backups
5. Document any custom configurations

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
