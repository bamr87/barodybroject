#!/bin/bash

# Build Sphinx documentation for Barodybroject
# This script sets up the environment and builds the documentation

set -e

echo "Building Barodybroject documentation..."

# Set required environment variables for Django
export DEBUG=True
export SECRET_KEY=docs-secret-key-for-sphinx
export DATABASE_URL=sqlite:///docs-temp.db
export CONTAINER_APP_NAME=docs
export CONTAINER_APP_ENV_DNS_SUFFIX=localhost

# Change to docs directory
cd "$(dirname "$0")/docs"

# Clean previous build
echo "Cleaning previous build..."
make clean

# Build HTML documentation
echo "Building HTML documentation..."
make html

echo "Documentation build complete!"
echo "Open docs/build/html/index.html to view the documentation"