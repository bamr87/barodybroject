# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    ruby-full \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install bundler and jekyll
RUN gem install bundler jekyll

# Set the working directory
WORKDIR /app

# Copy dependency files
COPY requirements.txt Gemfile ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Install Ruby dependencies
RUN bundle install

# **Install supervisor globally before switching users**
RUN pip install --no-cache-dir supervisor

# Copy the application code
COPY src/ /app/

# Create a non-root user and set permissions
RUN adduser --disabled-password --gecos '' appuser \
    && chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose ports
EXPOSE 8000 4002

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

RUN cat /etc/supervisor/conf.d/supervisord.conf

# Command to start supervisor
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]