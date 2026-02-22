# Docker Setup Guide

This guide explains how to run the ADAMS Django application using Docker and Docker Compose.

## 📋 Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
cd adams-django-main
```

### 2. Configure Environment Variables

Copy the example environment file and update it:

```bash
cp docker-compose.env.example .env
```

Edit `.env` and set:
- `DJANGO_SECRET_KEY` - Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DB_PASSWORD` - Strong password for PostgreSQL
- `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` - MinIO admin credentials
- Email settings (if needed)

**Important:** For Docker, set `USE_SQLITE=false` to use PostgreSQL.

### 3. Build and Start Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Access the Application

- **Django Application:** http://localhost:8000
- **MinIO Console:** http://localhost:9001
  - Login with `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` from `.env`
- **PostgreSQL:** localhost:5432 (if needed for direct access)

## 🛠️ Common Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f minio
```

### Execute Commands in Container
```bash
# Django management commands
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic

# Shell access
docker-compose exec web bash
```

### Rebuild After Code Changes
```bash
# Rebuild and restart
docker-compose up -d --build

# Rebuild specific service
docker-compose build web
docker-compose up -d web
```

### Stop and Remove Everything (including volumes)
```bash
docker-compose down -v
```

## 📁 Docker Services

### 1. **web** - Django Application
- **Image:** Built from `Dockerfile`
- **Port:** 8000
- **Volumes:**
  - Code: Mounted from project directory
  - Static files: `static_volume`
  - Media files: `media_volume`
  - Logs: `logs_volume`

### 2. **db** - PostgreSQL Database
- **Image:** `postgres:16-alpine`
- **Port:** 5432
- **Volume:** `postgres_data` (persistent storage)
- **Health Check:** Automatically waits for database to be ready

### 3. **minio** - Object Storage
- **Image:** `minio/minio:latest`
- **Ports:** 
  - 9000: MinIO API
  - 9001: MinIO Console
- **Volume:** `minio_data` (persistent storage)
- **Health Check:** Ensures MinIO is ready before starting Django

## 🔧 Configuration

### Environment Variables

The `.env` file is loaded by `docker-compose.yml`. Key variables:

- **Database:** `DB_HOST=db` (service name, not localhost)
- **MinIO:** `MINIO_URL=minio:9000` (service name, not localhost)
- **Django:** Standard Django settings

### Network

All services are on the `adams_network` bridge network, allowing them to communicate using service names:
- `db` for PostgreSQL
- `minio` for MinIO
- `web` for Django

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection from web container
docker-compose exec web python -c "import psycopg2; psycopg2.connect(dbname='adamsdb', user='postgres', password='postgres', host='db')"
```

### MinIO Connection Issues

```bash
# Check if MinIO is running
docker-compose ps minio

# Check MinIO logs
docker-compose logs minio

# Access MinIO console
# Open http://localhost:9001 and login
```

### Application Not Starting

```bash
# Check application logs
docker-compose logs web

# Check if migrations ran
docker-compose exec web python manage.py showmigrations

# Run migrations manually
docker-compose exec web python manage.py migrate
```

### Static Files Not Loading

```bash
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check static volume
docker volume inspect adams-django-main_static_volume
```

### Port Already in Use

If ports 8000, 9000, 9001, or 5432 are already in use:

1. Change ports in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Change host port
```

2. Or stop the conflicting service

## 🔄 Development Workflow

### Making Code Changes

Code changes are automatically reflected (volume mount). For Python package changes:

```bash
# Rebuild the image
docker-compose build web
docker-compose up -d web
```

### Database Migrations

```bash
# Create migration
docker-compose exec web python manage.py makemigrations

# Apply migration
docker-compose exec web python manage.py migrate
```

### Creating Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

## 🚀 Production Deployment

### 1. Update `.env` for Production

```bash
DEBUG_MODE=false
DJANGO_SECRET_KEY=<strong-secret-key>
ALLOWED_HOSTS=adams.org.in,www.adams.org.in
CSRF_TRUSTED_ORIGINS=https://adams.org.in,https://www.adams.org.in
```

### 2. Use Production Gunicorn Config

The `gunicorn_config.py` is already configured. For production, you may want to:
- Adjust worker count
- Configure SSL
- Set up reverse proxy (Nginx)

### 3. Set Up Nginx Reverse Proxy

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name adams.org.in www.adams.org.in;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
}
```

### 4. Persistent Data

All data is stored in Docker volumes:
- `postgres_data` - Database
- `minio_data` - Object storage
- `static_volume` - Static files
- `media_volume` - Media files
- `logs_volume` - Application logs

**Backup these volumes regularly!**

## 📝 Notes

- The entrypoint script (`docker-entrypoint.sh`) automatically:
  - Waits for PostgreSQL to be ready
  - Runs migrations
  - Collects static files
- MinIO bucket is created automatically on first access
- All services have health checks for proper startup order
- Use `docker-compose down -v` to completely remove all data

## 🔗 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
