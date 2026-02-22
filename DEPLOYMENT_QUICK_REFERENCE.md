# 🚀 Quick Deployment Reference

Quick commands for deploying and managing the ADAMS Django application.

## 📋 Pre-Deployment

```bash
# Generate Django secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Copy environment template
cp docker-compose.env.example .env
nano .env  # Edit with production values
```

## 🐳 Docker Commands

### Start Services
```bash
# Build and start
docker-compose up -d --build

# Start existing containers
docker-compose up -d

# View logs
docker-compose logs -f
```

### Stop Services
```bash
# Stop containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything (including volumes - WARNING: deletes data!)
docker-compose down -v
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart web
```

### View Status
```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# Service logs
docker-compose logs web
docker-compose logs db
docker-compose logs minio
```

## 🔧 Django Management Commands

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Django shell
docker-compose exec web python manage.py shell

# Create techbless superuser (auto-created on startup)
docker-compose exec web python manage.py create_techbless_superuser
```

## 💾 Backup & Restore

### Backup Database
```bash
docker-compose exec -T db pg_dump -U admin_adams adamsdb > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
docker-compose exec -T db psql -U admin_adams adamsdb < backup_20240222.sql
```

### Backup MinIO Data
```bash
docker run --rm -v adams-django-main_minio_data:/data -v $(pwd):/backup \
    alpine tar czf /backup/minio_backup_$(date +%Y%m%d).tar.gz -C /data .
```

## 🔍 Troubleshooting

### Check Application Health
```bash
curl http://localhost:8000/health/
```

### Test Database Connection
```bash
docker-compose exec web python -c "import psycopg2; psycopg2.connect(dbname='adamsdb', user='admin_adams', password='your_password', host='db')"
```

### Check MinIO Connection
```bash
# Access MinIO console
# http://<server-ip>:9001
```

### View Container Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f minio
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build web
```

## 🌐 Nginx Commands

```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

## 🔐 SSL Certificate

```bash
# Obtain certificate
sudo certbot --nginx -d adams.org.in -d www.adams.org.in

# Renew certificate
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run

# Check certificates
sudo certbot certificates
```

## 📊 Monitoring

```bash
# Container stats
docker stats

# Disk usage
df -h
docker system df

# Check volumes
docker volume ls
docker volume inspect adams-django-main_postgres_data
```

## 🔄 Update Application

```bash
# Pull latest code (if using Git)
git pull

# Rebuild and restart
docker-compose up -d --build

# Run migrations if needed
docker-compose exec web python manage.py migrate
```

## 🗑️ Cleanup

```bash
# Remove unused containers, networks, images
docker system prune

# Remove unused volumes (WARNING: may delete data!)
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

## 📝 Important Files

- `.env` - Environment variables
- `docker-compose.yml` - Service configuration
- `/etc/nginx/sites-available/adams` - Nginx config
- `DEPLOYMENT_STEPS.md` - Complete deployment guide

## 🔗 Access URLs

- **Application**: https://adams.org.in
- **Admin Panel**: https://adams.org.in/admin/
- **MinIO Console**: http://<server-ip>:9001
- **Health Check**: http://localhost:8000/health/

## ⚠️ Important Notes

1. **Always backup before major changes**
2. **Keep `.env` file secure** (never commit to Git)
3. **Change default passwords** in production
4. **Monitor logs regularly**
5. **Set up automated backups**
6. **Keep Docker and dependencies updated**
