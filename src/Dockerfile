# Dockerfile for Barodybroject Django Application
# Optimized for Azure Container Apps deployment

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install PostgreSQL client and system dependencies including Cairo for svg support
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    libpq-dev \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/setup_data /app/static /app/media

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=barodybroject.settings

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "barodybroject.wsgi:application"]
