#!/bin/bash

# Barodybroject Quick Start Script
# File: run.sh
# Description: Simple script to run the Barodybroject application
# Author: Barodybroject Team
# Version: 1.0.0
# 
# Usage: ./run.sh [options]
#   Options:
#     --prod       Run in production mode (default: development)
#     --jekyll     Include Jekyll static site generator
#     --build      Force rebuild containers
#     --stop       Stop all running containers
#     --logs       Show container logs
#     --help       Show this help message

set -euo pipefail

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly BOLD='\033[1m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$SCRIPT_DIR"

# Default options
MODE="development"
INCLUDE_JEKYLL=false
FORCE_BUILD=false
SHOW_LOGS=false
STOP_SERVICES=false

# ============================================================================
# LOGGING FUNCTIONS
# ============================================================================
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_header() {
    echo ""
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BOLD}${CYAN}  $1${NC}"
    echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# ============================================================================
# USAGE FUNCTION
# ============================================================================
show_usage() {
    cat << EOF
${BOLD}Barodybroject Quick Start${NC}

${BOLD}USAGE:${NC}
    ./run.sh [options]

${BOLD}OPTIONS:${NC}
    --prod       Run in production mode (default: development)
    --jekyll     Include Jekyll static site generator
    --build      Force rebuild containers before starting
    --stop       Stop all running containers
    --logs       Show container logs (follow mode)
    --help       Show this help message

${BOLD}EXAMPLES:${NC}
    ./run.sh                    # Start in development mode
    ./run.sh --prod             # Start in production mode
    ./run.sh --jekyll           # Start with Jekyll included
    ./run.sh --build --prod     # Rebuild and start in production
    ./run.sh --stop             # Stop all containers
    ./run.sh --logs             # Follow container logs

${BOLD}QUICK START:${NC}
    1. Run: ${GREEN}./run.sh${NC}
    2. Wait for services to start (usually 30-60 seconds)
    3. Access the application:
       - Django App: ${CYAN}http://localhost:8000${NC}
       - Admin Panel: ${CYAN}http://localhost:8000/admin${NC}
       - API: ${CYAN}http://localhost:8000/api${NC}

${BOLD}MORE INFO:${NC}
    See README.md for detailed documentation and troubleshooting.

EOF
}

# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================
check_docker() {
    log_info "Checking Docker installation..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        log_info "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker."
        exit 1
    fi
    
    log_success "Docker is available"
}

check_docker_compose() {
    log_info "Checking Docker Compose installation..."
    
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed or not available."
        log_info "Please install Docker Compose v2 or higher."
        exit 1
    fi
    
    log_success "Docker Compose is available"
}

check_env_file() {
    if [ ! -f "$PROJECT_ROOT/.env" ]; then
        log_warning "No .env file found."
        
        if [ -f "$PROJECT_ROOT/.env.example" ]; then
            log_info "Creating .env from .env.example..."
            cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
            log_success "Created .env file. Please review and update if needed."
        else
            log_info "No .env.example file found. Using default environment."
        fi
    else
        log_success ".env file exists"
    fi
}

# ============================================================================
# DOCKER OPERATIONS
# ============================================================================
stop_services() {
    log_header "Stopping Services"
    
    log_info "Stopping all containers..."
    docker compose down
    
    log_success "All services stopped"
}

start_services() {
    log_header "Starting Barodybroject"
    
    cd "$PROJECT_ROOT"
    
    # Build command components
    local compose_cmd="docker compose"
    local compose_args=""
    
    # Add profile based on mode
    if [ "$MODE" = "production" ]; then
        compose_args="--profile production"
        log_info "Starting in PRODUCTION mode"
    else
        log_info "Starting in DEVELOPMENT mode"
    fi
    
    # Add Jekyll profile if requested
    if [ "$INCLUDE_JEKYLL" = true ]; then
        compose_args="$compose_args --profile jekyll"
        log_info "Including Jekyll static site generator"
    fi
    
    # Build flag
    local build_flag=""
    if [ "$FORCE_BUILD" = true ]; then
        build_flag="--build"
        log_info "Forcing container rebuild..."
    fi
    
    # Start services
    log_info "Starting Docker containers..."
    $compose_cmd $compose_args up -d $build_flag
    
    # Wait for services to be ready
    log_info "Waiting for services to be ready..."
    sleep 5
    
    # Check service status
    log_info "Checking service status..."
    docker compose ps
    
    # Display access information
    display_access_info
}

display_access_info() {
    log_header "Application Ready"
    
    echo -e "${GREEN}${BOLD}✓ Services are running!${NC}"
    echo ""
    echo -e "${BOLD}Access Points:${NC}"
    
    if [ "$MODE" = "production" ]; then
        echo -e "  ${CYAN}►${NC} Django App:    ${CYAN}http://localhost:80${NC}"
        echo -e "  ${CYAN}►${NC} Admin Panel:   ${CYAN}http://localhost:80/admin${NC}"
        echo -e "  ${CYAN}►${NC} API Endpoints: ${CYAN}http://localhost:80/api${NC}"
    else
        echo -e "  ${CYAN}►${NC} Django App:    ${CYAN}http://localhost:8000${NC}"
        echo -e "  ${CYAN}►${NC} Admin Panel:   ${CYAN}http://localhost:8000/admin${NC}"
        echo -e "  ${CYAN}►${NC} API Endpoints: ${CYAN}http://localhost:8000/api${NC}"
    fi
    
    if [ "$INCLUDE_JEKYLL" = true ]; then
        echo -e "  ${CYAN}►${NC} Jekyll Site:   ${CYAN}http://localhost:4002${NC}"
    fi
    
    echo ""
    echo -e "${BOLD}Database:${NC}"
    echo -e "  ${CYAN}►${NC} PostgreSQL:    ${CYAN}localhost:5432${NC}"
    echo -e "  ${CYAN}►${NC} Database:      ${CYAN}barodydb${NC}"
    echo -e "  ${CYAN}►${NC} User:          ${CYAN}postgres${NC}"
    
    echo ""
    echo -e "${BOLD}Useful Commands:${NC}"
    echo -e "  ${CYAN}►${NC} View logs:     ${YELLOW}docker compose logs -f${NC}"
    echo -e "  ${CYAN}►${NC} Stop services: ${YELLOW}./run.sh --stop${NC}"
    echo -e "  ${CYAN}►${NC} Django shell:  ${YELLOW}docker compose exec web-dev python manage.py shell${NC}"
    echo -e "  ${CYAN}►${NC} Run tests:     ${YELLOW}docker compose exec web-dev python -m pytest${NC}"
    
    echo ""
    echo -e "${YELLOW}Note:${NC} First-time startup may take 30-60 seconds for migrations and setup."
    echo ""
}

show_logs() {
    log_header "Container Logs"
    
    log_info "Following logs (Ctrl+C to exit)..."
    docker compose logs -f
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --prod|--production)
                MODE="production"
                shift
                ;;
            --jekyll)
                INCLUDE_JEKYLL=true
                shift
                ;;
            --build)
                FORCE_BUILD=true
                shift
                ;;
            --stop)
                STOP_SERVICES=true
                shift
                ;;
            --logs)
                SHOW_LOGS=true
                shift
                ;;
            --help|-h)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Show header
    log_header "Barodybroject Quick Start"
    
    # Validation checks
    check_docker
    check_docker_compose
    
    # Handle stop command
    if [ "$STOP_SERVICES" = true ]; then
        stop_services
        exit 0
    fi
    
    # Handle logs command
    if [ "$SHOW_LOGS" = true ]; then
        show_logs
        exit 0
    fi
    
    # Check environment
    check_env_file
    
    # Start services
    start_services
    
    log_success "Barodybroject is running!"
}

# Run main function
main "$@"
