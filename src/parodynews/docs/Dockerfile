# File: Dockerfile
# Description: Multi-stage Dockerfile for building and serving Sphinx documentation
# Author: Barodybroject Team
# Created: 2025-11-25
# Last Modified: 2025-11-25
# Version: 1.0.0
#
# Dependencies:
# - python:3.11-slim: Base image for building docs
# - nginx:alpine: Lightweight web server for serving static HTML
#
# Container Requirements:
# - Base Image: python:3.11-slim (builder), nginx:alpine (runtime)
# - Exposed Ports: 80/tcp
# - Volumes: None required (docs built into image)
# - Environment: DJANGO_SETTINGS_MODULE for autodoc imports
#
# Usage: docker build -t barody-docs -f parodynews/docs/Dockerfile .

# Build stage: Generate Sphinx documentation
FROM python:3.11-slim AS builder

WORKDIR /build

# Install system dependencies for Django and documentation build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy Django project and documentation files
COPY . /build/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Sphinx documentation dependencies
RUN pip install --no-cache-dir -r parodynews/docs/requirements.txt

# Set environment for Django imports in Sphinx autodoc
ENV DJANGO_SETTINGS_MODULE=barodybroject.settings
ENV PYTHONPATH=/build

# Build Sphinx documentation
WORKDIR /build/parodynews/docs
RUN make clean && make html

# Runtime stage: Serve documentation with nginx
FROM nginx:alpine

# Copy built documentation from builder stage
COPY --from=builder /build/parodynews/docs/build/html /usr/share/nginx/html

# Copy custom nginx configuration
COPY parodynews/docs/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# nginx starts automatically in the base image
