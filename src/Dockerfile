# Dockerfile
FROM python:3-slim

# Install dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        libxml2-dev \
        libxmlsec1-dev \
        pkg-config \
        libffi-dev \
        postgresql-client \
        xdg-utils \
        libcairo2-dev \
        libgirepository1.0-dev \
        libpango1.0-dev \
        libglib2.0-dev \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements file
COPY requirements.txt ./

# Update pip and install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy entrypoint script and make it executable
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

# Copy the rest of the application code
COPY . ./

# Set the entrypoint
CMD ["bash", "-c", "./entrypoint.sh"]