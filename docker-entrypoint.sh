#!/bin/bash
set -e

# Check if using PostgreSQL (not SQLite)
if [ "${USE_SQLITE:-true}" != "true" ]; then
    echo "Waiting for PostgreSQL database to be ready..."
    python << END
import sys
import time
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adams.settings')
import django
django.setup()
from django.conf import settings

# Only wait if using PostgreSQL
if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    import psycopg2
    max_attempts = 30
    attempt = 0
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            )
            conn.close()
            print("Database is ready!")
            break
        except psycopg2.OperationalError:
            attempt += 1
            print(f"Waiting for database... ({attempt}/{max_attempts})")
            time.sleep(2)
    else:
        print("Database connection failed after 60 seconds")
        sys.exit(1)
else:
    print("Using SQLite database - no connection wait needed")
END
else
    echo "Using SQLite database - skipping database connection wait"
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating techbless superuser (if not exists)..."
python manage.py create_techbless_superuser || echo "Note: Superuser creation skipped or already exists"

echo "Starting application..."
exec "$@"
