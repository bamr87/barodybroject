#!/bin/bash
# File: migrate-docker-setup.sh
# Description: Migration script to consolidate Docker configuration
# Author: Barodybroject Team
# Version: 1.0.0
# Usage: ./migrate-docker-setup.sh

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Script directory
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Print header
print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║   Barodybroject Docker Configuration Migration Script     ║"
    echo "║   Consolidating multiple docker-compose files             ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
}

# Check if Docker is running
check_docker() {
    log_info "Checking Docker status..."
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    log_success "Docker is running"
}

# Backup existing configuration
backup_config() {
    log_info "Creating backup of existing configuration..."
    
    local backup_dir="docker-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup docker-compose files
    if [ -f "docker-compose.yml" ]; then
        cp docker-compose.yml "$backup_dir/"
        log_success "Backed up: docker-compose.yml"
    fi
    
    if [ -f "docker-compose.prod.yml" ]; then
        cp docker-compose.prod.yml "$backup_dir/"
        log_success "Backed up: docker-compose.prod.yml"
    fi
    
    if [ -f "src/docker-compose.yml" ]; then
        cp src/docker-compose.yml "$backup_dir/"
        log_success "Backed up: src/docker-compose.yml"
    fi
    
    # Backup .env if exists
    if [ -f ".env" ]; then
        cp .env "$backup_dir/"
        log_success "Backed up: .env"
    fi
    
    log_success "Backup created in: $backup_dir"
}

# Stop running containers
stop_containers() {
    log_info "Stopping running containers..."
    
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        docker-compose down
        log_success "Stopped containers from root docker-compose.yml"
    fi
    
    if [ -f "src/docker-compose.yml" ]; then
        cd src
        if docker-compose ps -q 2>/dev/null | grep -q .; then
            docker-compose down
            log_success "Stopped containers from src/docker-compose.yml"
        fi
        cd ..
    fi
}

# Install new configuration
install_new_config() {
    log_info "Installing new unified Docker configuration..."
    
    # Replace docker-compose.yml
    if [ -f "docker-compose.yml.new" ]; then
        mv docker-compose.yml.new docker-compose.yml
        log_success "Installed new docker-compose.yml"
    else
        log_error "docker-compose.yml.new not found!"
        exit 1
    fi
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_success "Created .env from .env.example"
            log_warning "Please update .env with your actual configuration"
        else
            log_error ".env.example not found!"
            exit 1
        fi
    else
        log_info ".env already exists (keeping current configuration)"
    fi
}

# Move old files to archive
archive_old_files() {
    log_info "Archiving old Docker configuration files..."
    
    mkdir -p archive/docker-old
    
    if [ -f "docker-compose.prod.yml" ]; then
        mv docker-compose.prod.yml archive/docker-old/
        log_success "Archived: docker-compose.prod.yml"
    fi
    
    if [ -f "src/docker-compose.yml" ]; then
        mv src/docker-compose.yml archive/docker-old/
        log_success "Archived: src/docker-compose.yml"
    fi
    
    if [ -f "supervisord.conf" ]; then
        mv supervisord.conf archive/docker-old/
        log_success "Archived: supervisord.conf"
    fi
}

# Test new configuration
test_config() {
    log_info "Testing new Docker configuration..."
    
    # Validate docker-compose.yml
    if docker-compose config > /dev/null 2>&1; then
        log_success "docker-compose.yml is valid"
    else
        log_error "docker-compose.yml validation failed!"
        docker-compose config
        exit 1
    fi
    
    # Test build
    log_info "Testing container build..."
    if docker-compose build web-dev > /dev/null 2>&1; then
        log_success "Development image builds successfully"
    else
        log_warning "Development image build failed (may need manual intervention)"
    fi
}

# Start services
start_services() {
    log_info "Starting services with new configuration..."
    
    echo ""
    read -p "Start development services now? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose up -d
        log_success "Services started successfully!"
        echo ""
        log_info "Access your application at:"
        echo "  - Django:     http://localhost:8000"
        echo "  - Admin:      http://localhost:8000/admin"
        echo "  - PostgreSQL: localhost:5432"
        echo ""
        log_info "View logs with: docker-compose logs -f"
    else
        log_info "Skipped starting services"
        log_info "Start manually with: docker-compose up -d"
    fi
}

# Print summary
print_summary() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                    Migration Complete!                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "Summary of changes:"
    echo "  ✅ Consolidated 3 docker-compose files into 1"
    echo "  ✅ Created unified configuration with profiles"
    echo "  ✅ Set up .env file for configuration"
    echo "  ✅ Archived old configuration files"
    echo ""
    log_info "Quick reference:"
    echo "  Development:  docker-compose up"
    echo "  Production:   docker-compose --profile production up"
    echo "  With Jekyll:  docker-compose --profile jekyll up"
    echo "  Stop all:     docker-compose down"
    echo ""
    log_info "Documentation:"
    echo "  📖 See README.md Docker Setup section for complete usage guide"
    echo "  📖 See .env.example for configuration options"
    echo ""
    log_warning "Next steps:"
    echo "  1. Review and update .env with your configuration"
    echo "  2. Update VS Code tasks to use new docker-compose.yml"
    echo "  3. Update any CI/CD pipelines"
    echo "  4. Review README.md Docker Setup section for new commands"
    echo ""
}

# Main execution
main() {
    print_header
    
    # Change to project root
    cd "$SCRIPT_DIR"
    
    # Run migration steps
    check_docker
    backup_config
    stop_containers
    install_new_config
    archive_old_files
    test_config
    start_services
    print_summary
    
    log_success "Migration completed successfully! 🎉"
}

# Run main function
main "$@"
