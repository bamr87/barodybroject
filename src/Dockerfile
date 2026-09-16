# Dockerfile for Barodybroject
# Optimized for Azure Container Apps deployment.
#
# Two stages: Node builds the React frontend, Python serves it. The built
# bundle is copied into the Python image so `collectstatic` picks it up and
# WhiteNoise serves it — no separate web server or CDN is required.

# ---------------------------------------------------------------- frontend
FROM node:22-slim AS frontend

WORKDIR /build

# Install dependencies from the lockfile first so this layer is cached
# whenever only application code changed.
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

# ------------------------------------------------------------------ python
FROM python:3.11-slim

WORKDIR /app

# PostgreSQL client and the system libraries the Python dependencies build against.
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    gcc \
    libpq-dev \
    pkg-config \
    libcairo2-dev \
    libgirepository1.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies. This pulls in claude-agent-sdk, which bundles
# the Claude Code CLI binary the default provider drives.
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# The built frontend, and the manifest `parodynews.views.spa` reads to emit the
# hashed asset tags. Copied after the source so a frontend-only change does not
# invalidate the Python layers.
COPY --from=frontend /build/dist ./frontend/dist

# Create necessary directories
RUN mkdir -p /app/logs /app/setup_data /app/static /app/media

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=barodybroject.settings.production

# Collect static files, including the frontend bundle. A dummy SECRET_KEY keeps
# production settings importable at build time without baking in a real one.
RUN SECRET_KEY=build-time-only-not-used-at-runtime \
    RUNNING_IN_PRODUCTION=False \
    python manage.py collectstatic --noinput

# Copy and set up entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Expose port
EXPOSE 8000

# Set entrypoint and default command
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "barodybroject.wsgi:application"]
