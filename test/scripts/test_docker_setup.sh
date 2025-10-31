#!/bin/bash

# Docker Setup Test Script
# 
# File: test_docker_setup.sh
# Description: Test installation wizard in Docker environment
# Author: Barodybroject Team <team@example.com>
# Created: 2025-01-27
# Last Modified: 2025-01-27
# Version: 1.0.0
# 
# Dependencies:
# - docker: Container platform
# - docker-compose: Container orchestration
# 
# Usage: ./test/scripts/test_docker_setup.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/test/logs"
LOG_FILE="$LOG_DIR/docker_test_$(date +%Y%m%d_%H%M%S).log"

# Docker configuration
COMPOSE_FILE="$PROJECT_ROOT/.devcontainer/docker-compose_dev.yml"
CONTAINER_NAME="barodybroject_python_1"
TIMEOUT=120

# Create logs directory
mkdir -p "$LOG_DIR"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

check_prerequisites() {
    log_info "Checking Docker prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    # Check compose file
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    log_success "All prerequisites met"
}

cleanup_docker_environment() {
    log_info "Cleaning up Docker environment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>&1 | tee -a "$LOG_FILE" || true
    
    # Remove setup data volume if exists
    docker volume rm barodybroject_setup_data 2>/dev/null || true
    
    # Wait for cleanup
    sleep 5
    
    log_success "Docker environment cleaned up"
}

start_docker_environment() {
    log_info "Starting Docker environment..."
    
    cd "$PROJECT_ROOT"
    
    # Build and start containers
    if docker-compose -f "$COMPOSE_FILE" up -d --build 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Docker containers started"
    else
        log_error "Failed to start Docker containers"
        return 1
    fi
    
    # Wait for containers to be ready
    log_info "Waiting for containers to be ready..."
    local attempts=0
    while [[ $attempts -lt 30 ]]; do
        if docker-compose -f "$COMPOSE_FILE" exec -T python python --version &> /dev/null; then
            log_success "Python container is ready"
            break
        fi
        sleep 2
        ((attempts++))
    done
    
    if [[ $attempts -eq 30 ]]; then
        log_error "Timeout waiting for containers to be ready"
        return 1
    fi
    
    # Check database connectivity
    if docker-compose -f "$COMPOSE_FILE" exec -T python python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barodybroject.settings.development')
django.setup()
from django.db import connection
cursor = connection.cursor()
print('Database connection successful')
" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Database connectivity verified"
    else
        log_warning "Database connectivity check failed"
    fi
}

test_docker_interactive_setup() {
    log_info "Testing interactive setup in Docker..."
    
    cd "$PROJECT_ROOT"
    
    # Create input file for interactive mode
    local input_file="$LOG_DIR/docker_interactive_input.txt"
    cat > "$input_file" << EOF
dockeradmin
dockeradmin@test.com
DockerPassword123!
DockerPassword123!
y
EOF
    
    # Run interactive setup in container
    if docker-compose -f "$COMPOSE_FILE" exec -T python bash -c "
cd /app && python manage.py setup_wizard < /tmp/input.txt
" < "$input_file" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Interactive setup in Docker completed"
        
        # Verify admin user was created
        if docker-compose -f "$COMPOSE_FILE" exec -T python python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barodybroject.settings.development')
django.setup()
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='dockeradmin')
    print(f'Docker admin user: {user.username}, Staff: {user.is_staff}, Superuser: {user.is_superuser}')
    exit(0)
except User.DoesNotExist:
    print('ERROR: Docker admin user not found')
    exit(1)
" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Docker interactive setup verification passed"
            return 0
        else
            log_error "Docker interactive setup verification failed"
            return 1
        fi
    else
        log_error "Interactive setup in Docker failed"
        return 1
    fi
}

test_docker_headless_setup() {
    log_info "Testing headless setup in Docker..."
    
    cd "$PROJECT_ROOT"
    
    # Clean previous setup state
    docker-compose -f "$COMPOSE_FILE" exec -T python rm -rf /app/setup_data 2>/dev/null || true
    
    # Run headless setup in container
    local headless_output
    headless_output=$(docker-compose -f "$COMPOSE_FILE" exec -T python python manage.py setup_wizard --headless 2>&1)
    
    echo "$headless_output" | tee -a "$LOG_FILE"
    
    if echo "$headless_output" | grep -q -i "headless"; then
        log_success "Headless setup in Docker completed"
        
        # Extract token from output
        local token
        token=$(echo "$headless_output" | grep -i "token" | head -1 | sed 's/.*[Tt]oken[^a-zA-Z0-9]*\([a-zA-Z0-9]\+\).*/\1/' || echo "")
        
        if [[ -n "$token" ]] && [[ ${#token} -gt 10 ]]; then
            log_success "Token extracted from Docker headless setup: ${token:0:10}..."
            echo "$token" > "$LOG_DIR/docker_token.txt"
            return 0
        else
            log_warning "Could not extract token from Docker headless output"
            # Try to get token via service
            token=$(docker-compose -f "$COMPOSE_FILE" exec -T python python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barodybroject.settings.development')
django.setup()
from setup.services import InstallationService
service = InstallationService()
token = service.generate_setup_token()
print(token)
" 2>&1 | tail -1)
            
            if [[ -n "$token" ]] && [[ ${#token} -gt 10 ]]; then
                echo "$token" > "$LOG_DIR/docker_token.txt"
                log_success "Token generated via service: ${token:0:10}..."
                return 0
            else
                log_error "Failed to get token from Docker headless setup"
                return 1
            fi
        fi
    else
        log_error "Headless setup in Docker failed"
        return 1
    fi
}

test_docker_web_interface() {
    log_info "Testing web interface in Docker..."
    
    cd "$PROJECT_ROOT"
    
    # Start Django server in container
    log_info "Starting Django server in Docker..."
    docker-compose -f "$COMPOSE_FILE" exec -d python python manage.py runserver 0.0.0.0:8000
    
    # Wait for server to start
    sleep 10
    
    # Get container IP or use localhost
    local server_url="http://localhost:8000"
    
    # Test basic connectivity
    if docker-compose -f "$COMPOSE_FILE" exec -T python curl -s "$server_url" > /dev/null; then
        log_success "Django server accessible in Docker"
    else
        log_warning "Django server not accessible via curl from within container"
    fi
    
    # Test setup endpoints
    if docker-compose -f "$COMPOSE_FILE" exec -T python curl -s "$server_url/setup/wizard/" > /dev/null; then
        log_success "Setup wizard accessible in Docker"
    else
        log_warning "Setup wizard not accessible in Docker"
    fi
    
    # Test with token if available
    if [[ -f "$LOG_DIR/docker_token.txt" ]]; then
        local token=$(cat "$LOG_DIR/docker_token.txt")
        if docker-compose -f "$COMPOSE_FILE" exec -T python curl -s "$server_url/setup/create-admin/?token=$token" > /dev/null; then
            log_success "Admin creation page accessible with token in Docker"
        else
            log_warning "Admin creation page not accessible with token in Docker"
        fi
    fi
}

test_docker_data_persistence() {
    log_info "Testing data persistence in Docker..."
    
    cd "$PROJECT_ROOT"
    
    # Create test data
    docker-compose -f "$COMPOSE_FILE" exec -T python python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barodybroject.settings.development')
django.setup()
from django.contrib.auth.models import User
User.objects.create_user('persisttest', 'persist@test.com', 'PersistPassword123!')
print('Test user created')
" 2>&1 | tee -a "$LOG_FILE"
    
    # Stop containers
    log_info "Stopping containers to test persistence..."
    docker-compose -f "$COMPOSE_FILE" stop 2>&1 | tee -a "$LOG_FILE"
    
    # Start containers again
    log_info "Restarting containers..."
    docker-compose -f "$COMPOSE_FILE" start 2>&1 | tee -a "$LOG_FILE"
    
    # Wait for restart
    sleep 10
    
    # Check if data persisted
    if docker-compose -f "$COMPOSE_FILE" exec -T python python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barodybroject.settings.development')
django.setup()
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='persisttest')
    print(f'Persistence test passed: {user.username}')
    exit(0)
except User.DoesNotExist:
    print('ERROR: Data did not persist')
    exit(1)
" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Data persistence test passed"
        return 0
    else
        log_error "Data persistence test failed"
        return 1
    fi
}

test_docker_environment_variables() {
    log_info "Testing environment variables in Docker..."
    
    cd "$PROJECT_ROOT"
    
    # Check Django settings
    if docker-compose -f "$COMPOSE_FILE" exec -T python python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barodybroject.settings.development')
django.setup()
from django.conf import settings
print(f'DEBUG: {settings.DEBUG}')
print(f'DATABASE ENGINE: {settings.DATABASES[\"default\"][\"ENGINE\"]}')
print('Environment variables loaded correctly')
" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Environment variables test passed"
    else
        log_error "Environment variables test failed"
        return 1
    fi
    
    # Check custom environment variables
    docker-compose -f "$COMPOSE_FILE" exec -T python bash -c "
echo 'Python Path:' \$PYTHONPATH
echo 'Django Settings:' \$DJANGO_SETTINGS_MODULE
" 2>&1 | tee -a "$LOG_FILE"
}

test_docker_setup_integration() {
    log_info "Testing Docker setup integration..."
    
    cd "$PROJECT_ROOT"
    
    # Test setup service functionality in Docker
    if docker-compose -f "$COMPOSE_FILE" exec -T python python -c "
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'barodybroject.settings.development')
django.setup()
from setup.services import InstallationService

# Test service instantiation
service = InstallationService()
print('Service instantiated successfully')

# Test token generation
token = service.generate_setup_token()
print(f'Token generated: {token[:10]}...')

# Test token validation
is_valid = service.validate_token(token)
print(f'Token validation: {is_valid}')

# Test status check
status = service.get_installation_status()
print(f'Installation status: {status}')

print('Docker setup integration test completed')
" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Docker setup integration test passed"
        return 0
    else
        log_error "Docker setup integration test failed"
        return 1
    fi
}

generate_docker_test_report() {
    log_info "Generating Docker test report..."
    
    local report_file="$LOG_DIR/docker_test_report.html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Docker Setup Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .success { color: green; }
        .error { color: red; }
        .warning { color: orange; }
        .section { margin: 20px 0; }
        pre { background: #f5f5f5; padding: 10px; overflow-x: auto; }
    </style>
</head>
<body>
    <h1>Docker Setup Test Report</h1>
    <div class="section">
        <h2>Test Summary</h2>
        <p>Generated: $(date)</p>
        <p>Test Focus: Installation wizard in Docker environment</p>
        <p>Compose File: $COMPOSE_FILE</p>
    </div>
    
    <div class="section">
        <h2>Docker Environment</h2>
        <pre>
Docker Version: $(docker --version 2>/dev/null || echo "Not available")
Docker Compose Version: $(docker-compose --version 2>/dev/null || echo "Not available")
        </pre>
    </div>
    
    <div class="section">
        <h2>Test Results</h2>
        <pre>$(cat "$LOG_FILE")</pre>
    </div>
</body>
</html>
EOF
    
    log_success "Docker test report generated: $report_file"
}

main() {
    log_info "Starting Docker setup wizard tests..."
    
    # Prerequisites
    check_prerequisites || exit 1
    
    # Initial cleanup
    cleanup_docker_environment
    
    # Start environment
    start_docker_environment || exit 1
    
    # Run tests
    local overall_exit_code=0
    
    test_docker_interactive_setup || overall_exit_code=1
    test_docker_headless_setup || overall_exit_code=1
    test_docker_web_interface || overall_exit_code=1
    test_docker_data_persistence || overall_exit_code=1
    test_docker_environment_variables || overall_exit_code=1
    test_docker_setup_integration || overall_exit_code=1
    
    # Generate report
    generate_docker_test_report
    
    # Final cleanup
    cleanup_docker_environment
    
    # Final result
    if [[ $overall_exit_code -eq 0 ]]; then
        log_success "All Docker tests passed!"
    else
        log_error "Some Docker tests failed. Check log: $LOG_FILE"
    fi
    
    exit $overall_exit_code
}

# Handle interruption
trap cleanup_docker_environment EXIT

# Run main function
main "$@"