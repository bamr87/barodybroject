#!/bin/bash
# docker-entrypoint.sh
# Production entrypoint script for Barodybroject Django application
# 
# This script runs before starting the Django application to ensure:
# 1. Database migrations are applied
# 2. Admin user is created/updated with environment credentials
# 3. Static files are collected (if needed)

set -e  # Exit on error

echo "=========================================="
echo "Barodybroject Production Startup"
echo "=========================================="

# Wait for database to be ready
echo "⏳ Waiting for database..."
python << END
import sys
import time
import psycopg2
import os

max_retries = 30
retry_count = 0

db_config = {
    'dbname': os.environ.get('DB_NAME', 'barodydb'),
    'user': os.environ.get('DB_USERNAME', 'postgres'),
    'password': os.environ.get('DB_PASSWORD', 'postgres'),
    'host': os.environ.get('DB_HOST', 'barodydb'),
    'port': os.environ.get('DB_PORT', '5432')
}

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(**db_config)
        conn.close()
        print("✅ Database connection successful!")
        sys.exit(0)
    except psycopg2.OperationalError as e:
        retry_count += 1
        print(f"Database not ready (attempt {retry_count}/{max_retries}). Waiting...")
        time.sleep(2)

print("❌ Could not connect to database after {max_retries} attempts")
sys.exit(1)
END

# Run database migrations
echo ""
echo "📦 Running database migrations..."
python manage.py migrate --noinput

# Create or update admin user
echo ""
echo "👤 Ensuring admin user exists..."
python manage.py ensure_admin

# Collect static files (in case they weren't collected during build)
echo ""
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput || echo "⚠️  Static files collection skipped or failed (non-critical)"

echo ""
echo "=========================================="
echo "✅ Startup complete! Starting application..."
echo "=========================================="
echo ""

# Execute the main command (gunicorn)
exec "$@"



