#!/bin/bash

#
# File: test_docker_infrastructure.sh
# Description: Test Docker infrastructure and installation wizard in containerized environment
# Author: Barodybroject Team <team@example.com>
# Created: 2025-10-30
# Last Modified: 2025-10-30
# Version: 1.0.0
#
# Dependencies:
# - docker: Container runtime
# - docker-compose: Multi-container orchestration
#
# Usage: ./test/scripts/test_docker_infrastructure.sh [options]

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/test/logs"

# Docker configuration
COMPOSE_FILE="$PROJECT_ROOT/.devcontainer/docker-compose_dev.yml"
CONTAINER_PREFIX="barodybroject"

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

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

# Help function
show_help() {
    cat << EOF
Docker Infrastructure Test Runner

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --build-only        Only test container builds
    --network-only      Only test container networking
    --data-only         Only test data persistence
    --full              Run complete infrastructure test suite
    --clean             Clean up all containers and volumes
    --logs              Show container logs during testing
    --timeout SECONDS   Set timeout for container operations (default: 300)
    --help              Show this help message

EXAMPLES:
    $0                      # Run standard Docker infrastructure tests
    $0 --full --logs       # Complete test suite with log output
    $0 --clean             # Clean up Docker environment
    $0 --build-only        # Test only container builds

EOF
}

# Parse command line arguments
BUILD_ONLY=false
NETWORK_ONLY=false
DATA_ONLY=false
FULL_TEST=false
CLEAN_MODE=false
SHOW_LOGS=false
TIMEOUT=300

while [[ $# -gt 0 ]]; do
    case $1 in
        --build-only)
            BUILD_ONLY=true
            shift
            ;;
        --network-only)
            NETWORK_ONLY=true
            shift
            ;;
        --data-only)
            DATA_ONLY=true
            shift
            ;;
        --full)
            FULL_TEST=true
            shift
            ;;
        --clean)
            CLEAN_MODE=true
            shift
            ;;
        --logs)
            SHOW_LOGS=true
            shift
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Check Docker availability
check_docker() {
    log_info "Checking Docker availability..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is required but not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "docker-compose is required but not installed"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "Docker environment is ready"
}

# Clean up Docker environment
cleanup_docker() {
    log_info "Cleaning up Docker environment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" down --volumes --remove-orphans 2>/dev/null || true
    
    # Remove unused images and volumes
    docker system prune -f &> /dev/null || true
    
    log_success "Docker environment cleaned"
}

# Test container builds
test_container_builds() {
    log_info "Testing container builds..."
    
    cd "$PROJECT_ROOT"
    
    # Build containers
    log_info "Building containers with docker-compose..."
    if docker-compose -f "$COMPOSE_FILE" build --no-cache; then
        log_success "Container builds completed successfully"
    else
        log_error "Container builds failed"
        return 1
    fi
    
    # Verify images exist
    log_info "Verifying built images..."
    local images=(
        "${CONTAINER_PREFIX}_python"
        "postgres:15-alpine"
    )
    
    for image in "${images[@]}"; do
        if docker images | grep -q "$image"; then
            log_success "Image $image exists"
        else
            log_warning "Image $image not found"
        fi
    done
    
    return 0
}

# Test container startup and health
test_container_startup() {
    log_info "Testing container startup and health..."
    
    cd "$PROJECT_ROOT"
    
    # Start containers
    log_info "Starting containers..."
    if docker-compose -f "$COMPOSE_FILE" up -d; then
        log_success "Containers started successfully"
    else
        log_error "Failed to start containers"
        return 1
    fi
    
    # Wait for containers to be ready
    log_info "Waiting for containers to be ready..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
            log_success "Containers are running"
            break
        fi
        
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "Containers failed to start within timeout"
        return 1
    fi
    
    # Check container health
    log_info "Checking container health..."
    docker-compose -f "$COMPOSE_FILE" ps
    
    return 0
}

# Test container networking
test_container_networking() {
    log_info "Testing container networking..."
    
    cd "$PROJECT_ROOT"
    
    # Test database connectivity from Python container
    log_info "Testing database connectivity..."
    if docker-compose -f "$COMPOSE_FILE" exec python python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(
        host='barodydb',
        database='parody_dev',
        user='parody_user',
        password='parody_password'
    )
    print('Database connection successful')
    conn.close()
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"; then
        log_success "Database connectivity test passed"
    else
        log_error "Database connectivity test failed"
        return 1
    fi
    
    # Test Django can connect to database
    log_info "Testing Django database connection..."
    if docker-compose -f "$COMPOSE_FILE" exec python python manage.py check --database default; then
        log_success "Django database connection test passed"
    else
        log_error "Django database connection test failed"
        return 1
    fi
    
    return 0
}

# Test data persistence
test_data_persistence() {
    log_info "Testing data persistence..."
    
    cd "$PROJECT_ROOT"
    
    # Run migrations to create database structure
    log_info "Running database migrations..."
    if docker-compose -f "$COMPOSE_FILE" exec python python manage.py migrate --noinput; then
        log_success "Database migrations completed"
    else
        log_error "Database migrations failed"
        return 1
    fi
    
    # Test installation wizard data persistence
    log_info "Testing installation wizard data persistence..."
    
    # Create admin user via management command
    if docker-compose -f "$COMPOSE_FILE" exec python python manage.py shell -c "
from django.contrib.auth.models import User
from setup.services import InstallationService

# Create admin user
try:
    user = User.objects.create_superuser('testpersist', 'test@persist.com', 'PersistPassword123!')
    print(f'Created user: {user.username}')
    
    # Mark installation complete
    service = InstallationService()
    service.mark_installation_complete()
    print('Installation marked complete')
    
except Exception as e:
    print(f'Error: {e}')
    exit(1)
"; then
        log_success "Test data creation successful"
    else
        log_error "Test data creation failed"
        return 1
    fi
    
    # Restart containers to test persistence
    log_info "Restarting containers to test data persistence..."
    docker-compose -f "$COMPOSE_FILE" restart
    
    # Wait for restart
    sleep 10
    
    # Verify data persisted
    if docker-compose -f "$COMPOSE_FILE" exec python python manage.py shell -c "
from django.contrib.auth.models import User
from setup.services import InstallationService

try:
    # Check user exists
    user = User.objects.get(username='testpersist')
    print(f'Found user: {user.username}')
    
    # Check installation status
    service = InstallationService()
    if service.is_installation_complete():
        print('Installation status persisted')
    else:
        print('Installation status lost')
        exit(1)
        
except User.DoesNotExist:
    print('User data lost after restart')
    exit(1)
except Exception as e:
    print(f'Error: {e}')
    exit(1)
"; then
        log_success "Data persistence test passed"
    else
        log_error "Data persistence test failed"
        return 1
    fi
    
    return 0
}

# Test installation wizard in Docker
test_installation_wizard_docker() {
    log_info "Testing installation wizard in Docker environment..."
    
    cd "$PROJECT_ROOT"
    
    # Test headless installation
    log_info "Testing headless installation..."
    if docker-compose -f "$COMPOSE_FILE" exec python python manage.py setup_wizard --headless --force; then
        log_success "Headless installation test passed"
    else
        log_error "Headless installation test failed"
        return 1
    fi
    
    # Test installation status
    log_info "Testing installation status..."
    if docker-compose -f "$COMPOSE_FILE" exec python python -c "
from setup.services import InstallationService
service = InstallationService()
status = service.get_installation_status()
print(f'Installation complete: {status[\"installation_complete\"]}')
print(f'Admin user exists: {status[\"admin_user_exists\"]}')
print(f'Database ready: {status[\"database_ready\"]}')
"; then
        log_success "Installation status test passed"
    else
        log_error "Installation status test failed"
        return 1
    fi
    
    return 0
}

# Show container logs
show_container_logs() {
    if [ "$SHOW_LOGS" = true ]; then
        log_info "Container logs:"
        echo "===================="
        docker-compose -f "$COMPOSE_FILE" logs --tail=50
        echo "===================="
    fi
}

# Main test execution
run_tests() {
    local test_results=()
    
    # Container build tests
    if [ "$BUILD_ONLY" = true ] || [ "$FULL_TEST" = true ] || { [ "$BUILD_ONLY" = false ] && [ "$NETWORK_ONLY" = false ] && [ "$DATA_ONLY" = false ]; }; then
        if test_container_builds; then
            test_results+=("BUILD:PASS")
        else
            test_results+=("BUILD:FAIL")
        fi
    fi
    
    # Container startup tests
    if [ "$NETWORK_ONLY" = true ] || [ "$DATA_ONLY" = true ] || [ "$FULL_TEST" = true ] || { [ "$BUILD_ONLY" = false ] && [ "$NETWORK_ONLY" = false ] && [ "$DATA_ONLY" = false ]; }; then
        if test_container_startup; then
            test_results+=("STARTUP:PASS")
        else
            test_results+=("STARTUP:FAIL")
            show_container_logs
            return 1
        fi
    fi
    
    # Network tests
    if [ "$NETWORK_ONLY" = true ] || [ "$FULL_TEST" = true ] || { [ "$BUILD_ONLY" = false ] && [ "$NETWORK_ONLY" = false ] && [ "$DATA_ONLY" = false ]; }; then
        if test_container_networking; then
            test_results+=("NETWORK:PASS")
        else
            test_results+=("NETWORK:FAIL")
            show_container_logs
        fi
    fi
    
    # Data persistence tests
    if [ "$DATA_ONLY" = true ] || [ "$FULL_TEST" = true ] || { [ "$BUILD_ONLY" = false ] && [ "$NETWORK_ONLY" = false ] && [ "$DATA_ONLY" = false ]; }; then
        if test_data_persistence; then
            test_results+=("PERSISTENCE:PASS")
        else
            test_results+=("PERSISTENCE:FAIL")
            show_container_logs
        fi
    fi
    
    # Installation wizard tests
    if [ "$FULL_TEST" = true ] || { [ "$BUILD_ONLY" = false ] && [ "$NETWORK_ONLY" = false ] && [ "$DATA_ONLY" = false ]; }; then
        if test_installation_wizard_docker; then
            test_results+=("WIZARD:PASS")
        else
            test_results+=("WIZARD:FAIL")
            show_container_logs
        fi
    fi
    
    # Report results
    log_info "Test Results Summary:"
    for result in "${test_results[@]}"; do
        local test_name="${result%:*}"
        local test_status="${result#*:}"
        
        if [ "$test_status" = "PASS" ]; then
            log_success "$test_name: PASSED"
        else
            log_error "$test_name: FAILED"
        fi
    done
    
    # Check for any failures
    for result in "${test_results[@]}"; do
        if [[ "$result" == *":FAIL" ]]; then
            return 1
        fi
    done
    
    return 0
}

# Main execution function
main() {
    log_info "Starting Docker Infrastructure Tests"
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Check Docker
    check_docker
    
    # Clean up if requested
    if [ "$CLEAN_MODE" = true ]; then
        cleanup_docker
        log_success "Docker environment cleaned successfully"
        exit 0
    fi
    
    # Ensure clean state
    cleanup_docker
    
    # Run tests
    local exit_code=0
    if run_tests; then
        log_success "All Docker infrastructure tests passed!"
    else
        log_error "Some Docker infrastructure tests failed!"
        exit_code=1
    fi
    
    # Show logs if requested
    show_container_logs
    
    # Clean up after tests
    cleanup_docker
    
    exit $exit_code
}

# Run main function if script is executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi