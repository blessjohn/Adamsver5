# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for psycopg2 and other libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY . .

# Collect static files for production
RUN python manage.py collectstatic --noinput || true

ENV PYTHONUNBUFFERED=1