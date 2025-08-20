#!/bin/bash

# Azure Deployment Setup Wrapper Script
# This script provides a simple way to run the Azure deployment setup

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🚀 BarodyBroject Azure Deployment Setup"
echo "========================================"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/azure.yaml" ]; then
    echo "❌ This doesn't appear to be the BarodyBroject root directory."
    echo "   Please run this script from the project root or scripts directory."
    exit 1
fi

# Change to project root
cd "$PROJECT_ROOT"

# Run the Python setup script
echo "Starting interactive setup..."
echo ""
python3 "$SCRIPT_DIR/azure-deployment-setup.py"

echo ""
echo "✅ Setup script completed!"
