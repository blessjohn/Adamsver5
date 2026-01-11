# Deployment Checklist

## Pre-Deployment

- [ ] Set `DEBUG_MODE=false` in production environment
- [ ] Set `DJANGO_SECRET_KEY` in production environment (strong, random key)
- [ ] Configure `ALLOWED_HOSTS` environment variable with production domain
- [ ] Set up PostgreSQL database and configure connection
- [ ] Configure MinIO server and credentials
- [ ] Set up email SMTP credentials
- [ ] Run `python manage.py collectstatic` to collect static files
- [ ] Run `python manage.py migrate` to apply database migrations
- [ ] Test Gunicorn configuration: `gunicorn -c gunicorn_config.py adams.wsgi:application`
- [ ] Configure Nginx using `nginx.conf` template
- [ ] Set up SSL certificate (Let's Encrypt recommended)
- [ ] Configure firewall rules (ports 80, 443, 22)
- [ ] Set up log rotation for application logs

## Environment Variables Required

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG_MODE=false
ALLOWED_HOSTS=adams.org.in,www.adams.org.in

# Database
DB_HOST=localhost
DB_NAME=adamsdb
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_PORT=5432

# MinIO
MINIO_URL=localhost:9000
MINIO_ACCESS_KEY=your_access_key
MINIO_SECRET_KEY=your_secret_key
MINIO_BUCKET_NAME=adams

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## Post-Deployment

- [ ] Verify HTTPS is working
- [ ] Test user registration and login
- [ ] Test email sending functionality
- [ ] Verify file uploads to MinIO
- [ ] Check application logs for errors
- [ ] Monitor server resources (CPU, memory, disk)
- [ ] Set up automated backups for database
- [ ] Configure monitoring and alerts

## Security Checklist

- [ ] DEBUG is set to False
- [ ] SECRET_KEY is strong and secure
- [ ] CSRF_TRUSTED_ORIGINS includes production domain
- [ ] Database credentials are secure
- [ ] MinIO credentials are secure
- [ ] Email credentials are secure
- [ ] SSL/TLS is properly configured
- [ ] Firewall rules are in place
- [ ] Regular security updates are scheduled
