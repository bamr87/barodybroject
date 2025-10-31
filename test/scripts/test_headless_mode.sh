#!/bin/bash

# Headless Setup Test Script
# 
# File: test_headless_mode.sh
# Description: Test the headless setup wizard mode with web completion
# Author: Barodybroject Team <team@example.com>
# Created: 2025-01-27
# Last Modified: 2025-01-27
# Version: 1.0.0
# 
# Dependencies:
# - django: Web framework
# - curl: For web interface testing
# 
# Usage: ./test/scripts/test_headless_mode.sh

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
SRC_DIR="$PROJECT_ROOT/src"
LOG_DIR="$PROJECT_ROOT/test/logs"
LOG_FILE="$LOG_DIR/headless_test_$(date +%Y%m%d_%H%M%S).log"

# Test configuration
TEST_SERVER_PORT=8001
TEST_SERVER_URL="http://localhost:$TEST_SERVER_PORT"
TIMEOUT=30

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

setup_test_environment() {
    log_info "Setting up headless test environment..."
    
    # Change to project directory
    cd "$PROJECT_ROOT"
    
    # Set up Django environment
    export DJANGO_SETTINGS_MODULE="barodybroject.settings.testing"
    export PYTHONPATH="$SRC_DIR:$PYTHONPATH"
    
    # Clean up any existing setup state
    if [[ -d "/app/setup_data" ]]; then
        rm -rf "/app/setup_data"
    fi
    
    # Ensure clean database state
    if [[ -f "$SRC_DIR/db.sqlite3" ]]; then
        rm -f "$SRC_DIR/db.sqlite3"
    fi
    
    # Run initial migrations
    cd "$SRC_DIR"
    python manage.py migrate --run-syncdb 2>&1 | tee -a "$LOG_FILE"
    
    log_success "Test environment setup complete"
}

start_test_server() {
    log_info "Starting Django test server on port $TEST_SERVER_PORT..."
    
    cd "$SRC_DIR"
    
    # Start server in background
    python manage.py runserver "$TEST_SERVER_PORT" > "$LOG_DIR/server.log" 2>&1 &
    local server_pid=$!
    
    # Store PID for cleanup
    echo "$server_pid" > "$LOG_DIR/server.pid"
    
    # Wait for server to start
    local attempts=0
    while [[ $attempts -lt 10 ]]; do
        if curl -s "$TEST_SERVER_URL" > /dev/null 2>&1; then
            log_success "Test server started successfully (PID: $server_pid)"
            return 0
        fi
        sleep 2
        ((attempts++))
    done
    
    log_error "Failed to start test server"
    return 1
}

stop_test_server() {
    if [[ -f "$LOG_DIR/server.pid" ]]; then
        local server_pid=$(cat "$LOG_DIR/server.pid")
        if ps -p "$server_pid" > /dev/null; then
            log_info "Stopping test server (PID: $server_pid)..."
            kill "$server_pid" 2>/dev/null || true
            sleep 2
            
            # Force kill if still running
            if ps -p "$server_pid" > /dev/null; then
                kill -9 "$server_pid" 2>/dev/null || true
            fi
        fi
        rm -f "$LOG_DIR/server.pid"
    fi
}

test_headless_command() {
    log_info "Testing headless setup command..."
    
    cd "$SRC_DIR"
    
    # Run headless command and capture output
    local output_file="$LOG_DIR/headless_output.txt"
    if python manage.py setup_wizard --headless > "$output_file" 2>&1; then
        log_success "Headless command executed successfully"
        
        # Verify output contains expected elements
        local output=$(cat "$output_file")
        
        if echo "$output" | grep -q -i "headless"; then
            log_success "Output contains headless mode indication"
        else
            log_warning "Output missing headless mode indication"
        fi
        
        if echo "$output" | grep -q -i "token"; then
            log_success "Output contains token information"
        else
            log_warning "Output missing token information"
        fi
        
        if echo "$output" | grep -q "http"; then
            log_success "Output contains URL information"
        else
            log_warning "Output missing URL information"
        fi
        
        # Save output for later use
        cat "$output_file" >> "$LOG_FILE"
        return 0
    else
        log_error "Headless command failed"
        cat "$output_file" >> "$LOG_FILE"
        return 1
    fi
}

extract_setup_token() {
    log_info "Extracting setup token..."
    
    # Try to extract token from service
    cd "$SRC_DIR"
    local token
    token=$(python -c "
import django
django.setup()
from setup.services import InstallationService
try:
    service = InstallationService()
    if hasattr(service, '_config') and service._config:
        token = service._config.get('setup_token')
        if token:
            print(token)
        else:
            # Generate a new token for testing
            token = service.generate_setup_token()
            print(token)
    else:
        # Generate a new token for testing
        service = InstallationService()
        token = service.generate_setup_token()
        print(token)
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1)
    
    if [[ "$token" =~ ^[a-zA-Z0-9]+$ ]] && [[ ${#token} -gt 10 ]]; then
        echo "$token" > "$LOG_DIR/setup_token.txt"
        log_success "Setup token extracted: ${token:0:10}..."
        return 0
    else
        log_error "Failed to extract valid setup token: $token"
        return 1
    fi
}

test_web_interface_access() {
    log_info "Testing web interface access with token..."
    
    local token
    if [[ -f "$LOG_DIR/setup_token.txt" ]]; then
        token=$(cat "$LOG_DIR/setup_token.txt")
    else
        log_error "Setup token not available"
        return 1
    fi
    
    # Test wizard page access
    log_info "Testing wizard page access..."
    if curl -s "$TEST_SERVER_URL/setup/wizard/" > "$LOG_DIR/wizard_response.html"; then
        if grep -q "Installation Wizard" "$LOG_DIR/wizard_response.html"; then
            log_success "Wizard page accessible and contains expected content"
        else
            log_warning "Wizard page accessible but missing expected content"
        fi
    else
        log_error "Failed to access wizard page"
        return 1
    fi
    
    # Test admin creation page with token
    log_info "Testing admin creation page with token..."
    if curl -s "$TEST_SERVER_URL/setup/create-admin/?token=$token" > "$LOG_DIR/admin_response.html"; then
        if grep -q "Create Administrator" "$LOG_DIR/admin_response.html"; then
            log_success "Admin creation page accessible with token"
        else
            log_warning "Admin creation page accessible but missing expected content"
        fi
    else
        log_error "Failed to access admin creation page with token"
        return 1
    fi
    
    # Test admin creation page without token (should redirect)
    log_info "Testing admin creation page without token..."
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" "$TEST_SERVER_URL/setup/create-admin/")
    
    if [[ "$response_code" == "302" ]]; then
        log_success "Admin creation page correctly redirects without token"
    else
        log_warning "Admin creation page response code without token: $response_code"
    fi
}

test_web_form_submission() {
    log_info "Testing web form submission..."
    
    local token
    if [[ -f "$LOG_DIR/setup_token.txt" ]]; then
        token=$(cat "$LOG_DIR/setup_token.txt")
    else
        log_error "Setup token not available"
        return 1
    fi
    
    # Get CSRF token first
    log_info "Getting CSRF token..."
    local csrf_token
    csrf_token=$(curl -s -c "$LOG_DIR/cookies.txt" "$TEST_SERVER_URL/setup/create-admin/?token=$token" | \
                grep -o 'csrfmiddlewaretoken.*value="[^"]*"' | \
                sed 's/.*value="//;s/".*//' | head -1)
    
    if [[ -z "$csrf_token" ]]; then
        log_warning "Could not extract CSRF token, using dummy token"
        csrf_token="dummy_csrf_token"
    else
        log_success "CSRF token extracted: ${csrf_token:0:10}..."
    fi
    
    # Submit admin creation form
    log_info "Submitting admin creation form..."
    local response_code
    response_code=$(curl -s -o "$LOG_DIR/form_response.html" -w "%{http_code}" \
        -b "$LOG_DIR/cookies.txt" \
        -X POST \
        -d "username=webadmin" \
        -d "email=webadmin@test.com" \
        -d "password1=WebPassword123!" \
        -d "password2=WebPassword123!" \
        -d "token=$token" \
        -d "csrfmiddlewaretoken=$csrf_token" \
        "$TEST_SERVER_URL/setup/create-admin/")
    
    log_info "Form submission response code: $response_code"
    
    if [[ "$response_code" == "302" ]]; then
        log_success "Form submission successful (redirect response)"
        
        # Verify admin user was created
        cd "$SRC_DIR"
        if python -c "
import django
django.setup()
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='webadmin')
    print(f'SUCCESS: User created - {user.username}, Staff: {user.is_staff}, Superuser: {user.is_superuser}')
    exit(0)
except User.DoesNotExist:
    print('ERROR: Admin user not found')
    exit(1)
" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Admin user verification passed"
            return 0
        else
            log_error "Admin user verification failed"
            return 1
        fi
    else
        log_error "Form submission failed with response code: $response_code"
        cat "$LOG_DIR/form_response.html" >> "$LOG_FILE"
        return 1
    fi
}

test_headless_security() {
    log_info "Testing headless mode security features..."
    
    # Test invalid token
    log_info "Testing invalid token rejection..."
    local response_code
    response_code=$(curl -s -o /dev/null -w "%{http_code}" \
        "$TEST_SERVER_URL/setup/create-admin/?token=invalid_token_123")
    
    if [[ "$response_code" == "302" ]] || [[ "$response_code" == "403" ]]; then
        log_success "Invalid token correctly rejected"
    else
        log_warning "Invalid token response code: $response_code"
    fi
    
    # Test token format
    local token
    if [[ -f "$LOG_DIR/setup_token.txt" ]]; then
        token=$(cat "$LOG_DIR/setup_token.txt")
        
        if [[ ${#token} -ge 20 ]]; then
            log_success "Token has sufficient length (${#token} chars)"
        else
            log_warning "Token may be too short (${#token} chars)"
        fi
        
        if [[ "$token" =~ ^[a-zA-Z0-9]+$ ]]; then
            log_success "Token format is alphanumeric"
        else
            log_warning "Token contains non-alphanumeric characters"
        fi
    fi
}

test_headless_status_endpoints() {
    log_info "Testing status endpoints..."
    
    # Test status endpoint
    if curl -s "$TEST_SERVER_URL/setup/status/" > "$LOG_DIR/status_response.json"; then
        if grep -q "installation" "$LOG_DIR/status_response.json"; then
            log_success "Status endpoint accessible and contains installation info"
        else
            log_warning "Status endpoint accessible but missing expected content"
        fi
    else
        log_error "Failed to access status endpoint"
    fi
    
    # Test health endpoint
    if curl -s "$TEST_SERVER_URL/setup/health/" > "$LOG_DIR/health_response.html"; then
        if grep -q -i "health" "$LOG_DIR/health_response.html"; then
            log_success "Health endpoint accessible"
        else
            log_warning "Health endpoint accessible but missing expected content"
        fi
    else
        log_error "Failed to access health endpoint"
    fi
}

cleanup_test_environment() {
    log_info "Cleaning up headless test environment..."
    
    # Stop test server
    stop_test_server
    
    # Clean up test files
    rm -f "$LOG_DIR"/*.txt
    rm -f "$LOG_DIR"/*.html
    rm -f "$LOG_DIR"/*.json
    rm -f "$LOG_DIR/cookies.txt"
    
    # Clean up setup state
    if [[ -d "/app/setup_data" ]]; then
        rm -rf "/app/setup_data"
    fi
    
    # Clean up database
    if [[ -f "$SRC_DIR/db.sqlite3" ]]; then
        rm -f "$SRC_DIR/db.sqlite3"
    fi
    
    log_success "Cleanup complete"
}

generate_headless_test_report() {
    log_info "Generating headless test report..."
    
    local report_file="$LOG_DIR/headless_test_report.html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Headless Setup Test Report</title>
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
    <h1>Headless Setup Test Report</h1>
    <div class="section">
        <h2>Test Summary</h2>
        <p>Generated: $(date)</p>
        <p>Test Focus: Headless setup wizard mode with web completion</p>
        <p>Server URL: $TEST_SERVER_URL</p>
    </div>
    
    <div class="section">
        <h2>Test Results</h2>
        <pre>$(cat "$LOG_FILE")</pre>
    </div>
</body>
</html>
EOF
    
    log_success "Headless test report generated: $report_file"
}

main() {
    log_info "Starting headless setup wizard tests..."
    
    # Setup
    setup_test_environment || exit 1
    
    # Start test server
    start_test_server || exit 1
    
    # Run tests
    local overall_exit_code=0
    
    test_headless_command || overall_exit_code=1
    extract_setup_token || overall_exit_code=1
    test_web_interface_access || overall_exit_code=1
    test_web_form_submission || overall_exit_code=1
    test_headless_security || overall_exit_code=1
    test_headless_status_endpoints || overall_exit_code=1
    
    # Generate report
    generate_headless_test_report
    
    # Cleanup
    cleanup_test_environment
    
    # Final result
    if [[ $overall_exit_code -eq 0 ]]; then
        log_success "All headless tests passed!"
    else
        log_error "Some headless tests failed. Check log: $LOG_FILE"
    fi
    
    exit $overall_exit_code
}

# Handle interruption
trap cleanup_test_environment EXIT

# Run main function
main "$@"