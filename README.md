# ADAMS Django Application

Association of Doctors and Medical Students (ADAMS) web application built with Django.

## 🚀 Production Stack

- **Django 5.1.3** - Web framework
- **Gunicorn** - WSGI HTTP server
- **Nginx** - Reverse proxy and web server
- **PostgreSQL** - Database
- **MinIO** - Object storage for media files

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 16+
- Nginx
- MinIO server
- Ubuntu 22.04 LTS (recommended for AWS Lightsail)

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd adams-django-main
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

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

**Important**: Load environment variables before running Django. You can use `python-dotenv` or export them in your systemd service file.

### 4. Database setup

```bash
# Create database and user
sudo -u postgres psql
CREATE DATABASE adamsdb;
CREATE USER admin_adams WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE adamsdb TO admin_adams;
\q
```

### 5. Run migrations

```bash
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

## 🚀 Production Deployment

For complete deployment instructions on AWS Lightsail, see **[DEPLOYMENT.md](DEPLOYMENT.md)**.

### Quick Start (Development)

```bash
source venv/bin/activate
python manage.py runserver
```

### Production (Gunicorn)

```bash
source venv/bin/activate
gunicorn -c gunicorn_config.py adams.wsgi:application
```

## 📁 Project Structure

```
adams-django-main/
├── adams/                 # Django project settings
│   ├── settings.py       # Main configuration
│   ├── urls.py           # URL routing
│   └── wsgi.py           # WSGI application
├── app/                   # Main application
│   ├── models.py         # Database models
│   ├── views.py          # Vew functions
│   ├── urls.py           # App URLs
│   └── utils.py          # Utility functions (MinIO)
├── nginx.conf            # Nginx configuration
├── gunicorn_config.py    # Gunicorn configuration
├── requirements.txt      # Python dependencies
└── manage.py            # Django management script
```

## 🔧 Configuration Files

- **`adams/settings.py`** - Django settings (database, MinIO, security)
- **`nginx.conf`** - Nginx reverse proxy configuration
- **`gunicorn_config.py`** - Gunicorn WSGI server configuration

## 🔐 Security Settings

The application is configured with:
- ✅ HTTPS/SSL support via Nginx
- ✅ CSRF protection with trusted origins
- ✅ Secure cookies (HTTPS only)
- ✅ XSS protection
- ✅ Content type sniffing protection
- ✅ X-Frame-Options: DENY

## 📝 Environment Variables

All sensitive configuration is managed through environment variables. See the `.env` example above.

**Required variables:**
- `DJANGO_SECRET_KEY` - Django secret key
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST` - Database credentials
- `MINIO_URL`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET_NAME` - MinIO configuration
- `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` - Email configuration

## 🗄️ Database

- **Engine**: PostgreSQL
- **Default database**: `adamsdb`
- **Timezone**: Asia/Kolkata

## 📦 Media Storage

Media files are stored in **MinIO** object storage, not in the local filesystem. All file uploads go directly to MinIO.

## 🧪 Testing

```bash
source venv/bin/activate
python manage.py test
```

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete AWS Lightsail deployment guide
- **[MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md)** - Docker removal migration summary
- **[DOCKER_REMOVAL_NOTES.md](DOCKER_REMOVAL_NOTES.md)** - Docker removal documentation

## 🐛 Troubleshooting

### 502 Bad Gateway
- Check Gunicorn is running: `sudo systemctl status adams-gunicorn`
- Verify Gunicorn is listening: `sudo netstat -tlnp | grep 8000`
- Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`

### CSRF Errors
- Verify `CSRF_TRUSTED_ORIGINS` includes your domain
- Check `SECURE_PROXY_SSL_HEADER` is set correctly
- Ensure Nginx sends `X-Forwarded-Proto` header

### Static Files Not Loading
- Run `python manage.py collectstatic --noinput`
- Verify `STATIC_ROOT` path matches Nginx configuration
- Check file permissions

### MinIO Connection Errors
- Verify MinIO is running: `sudo systemctl status minio`
- Check `MINIO_URL` is set to `localhost:9000`
- Test connection: `curl http://localhost:9000/minio/health/live`

## 📄 License

[Add your license information here]

## 👥 Contributors

[Add contributor information here]

## 📞 Support

For issues and questions, please contact the development team.
