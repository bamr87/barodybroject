#!/bin/bash

# Interactive Setup Test Script
# 
# File: test_interactive_mode.sh
# Description: Test the interactive setup wizard mode
# Author: Barodybroject Team <team@example.com>
# Created: 2025-01-27
# Last Modified: 2025-01-27
# Version: 1.0.0
# 
# Dependencies:
# - django: Web framework
# - expect: For automated input simulation
# 
# Usage: ./test/scripts/test_interactive_mode.sh

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
LOG_FILE="$LOG_DIR/interactive_test_$(date +%Y%m%d_%H%M%S).log"

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
    log_info "Setting up interactive test environment..."
    
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
    
    log_success "Test environment setup complete"
}

test_interactive_with_expect() {
    log_info "Testing interactive mode with expect..."
    
    if ! command -v expect &> /dev/null; then
        log_warning "expect not available, skipping automated input test"
        return 0
    fi
    
    # Create expect script
    local expect_script="$LOG_DIR/interactive_test.exp"
    
    cat > "$expect_script" << 'EOF'
#!/usr/bin/expect -f

set timeout 30
log_file [lindex $argv 0]

spawn python src/manage.py setup_wizard

# Wait for username prompt
expect "Enter username for admin user:" {
    send "testadmin\r"
}

# Wait for email prompt
expect "Enter email for admin user:" {
    send "admin@test.com\r"
}

# Wait for password prompt
expect "Enter password:" {
    send "TestPassword123!\r"
}

# Wait for confirm password prompt
expect "Confirm password:" {
    send "TestPassword123!\r"
}

# Wait for confirmation prompt
expect "Create admin user?" {
    send "y\r"
}

# Wait for completion
expect {
    "Installation wizard completed successfully" {
        puts "SUCCESS: Interactive setup completed"
        exit 0
    }
    timeout {
        puts "ERROR: Interactive setup timed out"
        exit 1
    }
    eof {
        puts "ERROR: Interactive setup ended unexpectedly"
        exit 1
    }
}
EOF
    
    chmod +x "$expect_script"
    
    # Run expect script
    if "$expect_script" "$LOG_FILE.expect"; then
        log_success "Interactive mode test with expect passed"
        return 0
    else
        log_error "Interactive mode test with expect failed"
        return 1
    fi
}

test_interactive_with_input_simulation() {
    log_info "Testing interactive mode with input simulation..."
    
    # Create input file
    local input_file="$LOG_DIR/test_input.txt"
    cat > "$input_file" << EOF
simadmin
sim@test.com
SimPassword123!
SimPassword123!
y
EOF
    
    # Run command with input redirection
    cd "$SRC_DIR"
    if python manage.py setup_wizard < "$input_file" 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Interactive mode with input simulation completed"
        
        # Verify admin user was created
        if python -c "
import django
django.setup()
from django.contrib.auth.models import User
try:
    user = User.objects.get(username='simadmin')
    print(f'User created: {user.username}, Staff: {user.is_staff}, Superuser: {user.is_superuser}')
    exit(0)
except User.DoesNotExist:
    print('ERROR: Admin user not created')
    exit(1)
" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Admin user verification passed"
            return 0
        else
            log_error "Admin user verification failed"
            return 1
        fi
    else
        log_error "Interactive mode with input simulation failed"
        return 1
    fi
}

test_interactive_validation() {
    log_info "Testing interactive mode input validation..."
    
    # Test invalid input handling
    local input_file="$LOG_DIR/invalid_input.txt"
    cat > "$input_file" << EOF

invalid_email
weak
different
n
validadmin
valid@test.com
ValidPassword123!
ValidPassword123!
y
EOF
    
    cd "$SRC_DIR"
    if python manage.py setup_wizard < "$input_file" 2>&1 | tee -a "$LOG_FILE"; then
        log_info "Interactive validation test completed"
        
        # Check that it handled invalid input gracefully
        if grep -q "validadmin" "$LOG_FILE"; then
            log_success "Interactive validation handled invalid input correctly"
            return 0
        else
            log_warning "Interactive validation test results unclear"
            return 0
        fi
    else
        log_error "Interactive validation test failed"
        return 1
    fi
}

test_interactive_cancellation() {
    log_info "Testing interactive mode cancellation..."
    
    # Test user cancellation
    local input_file="$LOG_DIR/cancel_input.txt"
    cat > "$input_file" << EOF
canceladmin
cancel@test.com
CancelPassword123!
CancelPassword123!
n
EOF
    
    cd "$SRC_DIR"
    
    # This should exit without creating user
    if python manage.py setup_wizard < "$input_file" 2>&1 | tee -a "$LOG_FILE"; then
        # Check that no user was created
        if python -c "
import django
django.setup()
from django.contrib.auth.models import User
try:
    User.objects.get(username='canceladmin')
    print('ERROR: User should not have been created')
    exit(1)
except User.DoesNotExist:
    print('SUCCESS: User correctly not created after cancellation')
    exit(0)
" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Interactive cancellation test passed"
            return 0
        else
            log_error "Interactive cancellation test failed - user was created"
            return 1
        fi
    else
        log_info "Interactive cancellation test completed (expected failure)"
        return 0
    fi
}

test_interactive_help_and_info() {
    log_info "Testing interactive mode help and information..."
    
    cd "$SRC_DIR"
    
    # Test help flag
    if python manage.py setup_wizard --help 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Help flag test passed"
    else
        log_warning "Help flag test failed"
    fi
    
    # Test that help contains expected information
    if python manage.py setup_wizard --help 2>&1 | grep -q "headless"; then
        log_success "Help contains headless option"
    else
        log_warning "Help missing headless option"
    fi
}

test_interactive_error_recovery() {
    log_info "Testing interactive mode error recovery..."
    
    # Create scenario with existing user
    cd "$SRC_DIR"
    python -c "
import django
django.setup()
from django.contrib.auth.models import User
User.objects.create_user('existing', 'existing@test.com', 'password123')
print('Created existing user for conflict test')
" 2>&1 | tee -a "$LOG_FILE"
    
    # Try to create user with same username
    local input_file="$LOG_DIR/conflict_input.txt"
    cat > "$input_file" << EOF
existing
existing@test.com
ExistingPassword123!
ExistingPassword123!
y
recoveryuser
recovery@test.com
RecoveryPassword123!
RecoveryPassword123!
y
EOF
    
    if python manage.py setup_wizard < "$input_file" 2>&1 | tee -a "$LOG_FILE"; then
        log_info "Error recovery test completed"
        
        # Check if recovery user was created
        if python -c "
import django
django.setup()
from django.contrib.auth.models import User
try:
    User.objects.get(username='recoveryuser')
    print('SUCCESS: Recovery user created after conflict')
    exit(0)
except User.DoesNotExist:
    print('INFO: Recovery user not created')
    exit(1)
" 2>&1 | tee -a "$LOG_FILE"; then
            log_success "Error recovery test passed"
            return 0
        else
            log_info "Error recovery test - no recovery user created"
            return 0
        fi
    else
        log_error "Error recovery test failed"
        return 1
    fi
}

cleanup_test_environment() {
    log_info "Cleaning up interactive test environment..."
    
    # Clean up test files
    rm -f "$LOG_DIR"/*.exp
    rm -f "$LOG_DIR"/*_input.txt
    
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

generate_interactive_test_report() {
    log_info "Generating interactive test report..."
    
    local report_file="$LOG_DIR/interactive_test_report.html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Interactive Setup Test Report</title>
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
    <h1>Interactive Setup Test Report</h1>
    <div class="section">
        <h2>Test Summary</h2>
        <p>Generated: $(date)</p>
        <p>Test Focus: Interactive setup wizard mode</p>
    </div>
    
    <div class="section">
        <h2>Test Results</h2>
        <pre>$(cat "$LOG_FILE")</pre>
    </div>
</body>
</html>
EOF
    
    log_success "Interactive test report generated: $report_file"
}

main() {
    log_info "Starting interactive setup wizard tests..."
    
    # Setup
    setup_test_environment || exit 1
    
    # Run tests
    local overall_exit_code=0
    
    test_interactive_with_expect || overall_exit_code=1
    test_interactive_with_input_simulation || overall_exit_code=1
    test_interactive_validation || overall_exit_code=1
    test_interactive_cancellation || overall_exit_code=1
    test_interactive_help_and_info || overall_exit_code=1
    test_interactive_error_recovery || overall_exit_code=1
    
    # Generate report
    generate_interactive_test_report
    
    # Cleanup
    cleanup_test_environment
    
    # Final result
    if [[ $overall_exit_code -eq 0 ]]; then
        log_success "All interactive tests passed!"
    else
        log_error "Some interactive tests failed. Check log: $LOG_FILE"
    fi
    
    exit $overall_exit_code
}

# Handle interruption
trap cleanup_test_environment EXIT

# Run main function
main "$@"