# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy project
COPY . .

# Create directories for media and logs
RUN mkdir -p /app/media /app/logs /app/staticfiles

# Collect static files (will be done at runtime, but prepare directory)
RUN python manage.py collectstatic --noinput || true

# Create entrypoint script
RUN chmod +x /app/docker-entrypoint.sh || true

# Expose port
EXPOSE 8000

# Use entrypoint script
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Default command
CMD ["gunicorn", "-c", "gunicorn_config.py", "adams.wsgi:application"]
