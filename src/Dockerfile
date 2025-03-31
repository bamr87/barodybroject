# Dockerfile
FROM python:3.12

# Install dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends postgresql-client xmlsec1 \
    && apt-get install -y libxmlsec1 libxmlsec1-dev \
    && apt-get update && apt-get install -y xdg-utils \
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
CMD ["bash", "-c", ". entrypoint.sh"]