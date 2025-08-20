#!/bin/bash
#
# Azure Deployment Setup Script for BarodyBroject
# 
# This script sets up a new Azure deployment by running the Python setup script.
# Make sure you have the Azure CLI and azd CLI installed and are logged in.
#
# Usage: ./setup-azure.sh
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI (az) is not installed. Please install it first:"
        echo "  https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    
    # Check Azure Developer CLI
    if ! command -v azd &> /dev/null; then
        print_error "Azure Developer CLI (azd) is not installed. Please install it first:"
        echo "  https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install it first."
        exit 1
    fi
    
    # Check curl
    if ! command -v curl &> /dev/null; then
        print_error "curl is not installed. Please install it first."
        exit 1
    fi
    
    print_success "All prerequisites are installed"
}

# Check if user is logged in to Azure
check_azure_login() {
    print_status "Checking Azure login status..."
    
    # Check Azure CLI login
    if ! az account show &> /dev/null; then
        print_warning "You are not logged in to Azure CLI"
        print_status "Attempting to log in..."
        az login
    fi
    
    # Check azd login
    if ! azd auth show &> /dev/null; then
        print_warning "You are not logged in to Azure Developer CLI"
        print_status "Attempting to log in..."
        azd auth login
    fi
    
    print_success "Azure authentication verified"
}

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_SCRIPT="$SCRIPT_DIR/azure-setup.py"

# Main execution
main() {
    echo "=============================================="
    echo "  BarodyBroject Azure Deployment Setup"
    echo "=============================================="
    echo
    
    # Check prerequisites
    check_prerequisites
    
    # Check Azure login
    check_azure_login
    
    # Run the Python setup script
    print_status "Starting interactive setup..."
    python3 "$PYTHON_SCRIPT"
    
    # Check exit code
    if [ $? -eq 0 ]; then
        print_success "Setup completed successfully!"
    else
        print_error "Setup failed. Please check the output above for details."
        exit 1
    fi
}

# Run main function
main "$@"
