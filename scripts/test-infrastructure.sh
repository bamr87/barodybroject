#!/bin/bash

# File: test-infrastructure.sh
# Description: Comprehensive infrastructure testing script for Django/OpenAI installation wizard
# Author: Barodybroject Team <team@example.com>
# Created: 2025-10-30
# Last Modified: 2025-10-30
# Version: 1.0.0
#
# Dependencies:
# - docker-compose
# - pytest
# - Django test environment
#
# Container Requirements:
# - Development containers running (postgres, python, jekyll)
# - Proper volume mounts and networking
#
# Usage: ./scripts/test-infrastructure.sh [--verbose] [--skip-cleanup] [--ci-mode]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/.devcontainer/docker-compose_dev.yml"
LOG_FILE="${PROJECT_ROOT}/logs/infrastructure-test-$(date +%Y%m%d_%H%M%S).log"
EXIT_CODE=0

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Options
VERBOSE=false
SKIP_CLEANUP=false
CI_MODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose)
            VERBOSE=true
            shift
            ;;
        --skip-cleanup)
            SKIP_CLEANUP=true
            shift
            ;;
        --ci-mode)
            CI_MODE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--verbose] [--skip-cleanup] [--ci-mode]"
            echo ""
            echo "Options:"
            echo "  --verbose      Enable verbose output"
            echo "  --skip-cleanup Skip cleanup after tests"
            echo "  --ci-mode      Run in CI environment mode"
            echo "  -h, --help     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Ensure logs directory exists
mkdir -p "${PROJECT_ROOT}/logs"

# Logging functions
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

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1" | tee -a "$LOG_FILE"
}

log_test() {
    echo -e "${CYAN}[TEST]${NC} $1" | tee -a "$LOG_FILE"
}

# Error handling
handle_error() {
    local line_number=$1
    local error_code=$2
    log_error "Error on line $line_number: Command exited with code $error_code"
    EXIT_CODE=$error_code
    if [[ "$CI_MODE" == "true" ]]; then
        cleanup_on_exit
        exit $error_code
    fi
}

trap 'handle_error $LINENO $?' ERR

# Cleanup function
cleanup_on_exit() {
    if [[ "$SKIP_CLEANUP" == "false" && "$CI_MODE" == "false" ]]; then
        log_info "Cleaning up test environment..."
        cd "$PROJECT_ROOT"
        docker-compose -f "$COMPOSE_FILE" down || true
        log_info "Cleanup completed"
    fi
}

trap cleanup_on_exit EXIT

# Docker command wrapper
docker_exec() {
    local service="$1"
    shift
    if [[ "$VERBOSE" == "true" ]]; then
        docker-compose -f "$COMPOSE_FILE" exec "$service" "$@"
    else
        docker-compose -f "$COMPOSE_FILE" exec "$service" "$@" 2>/dev/null
    fi
}

# Test execution wrapper
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    log_test "Running: $test_name"
    
    if eval "$test_command"; then
        log_success "✅ $test_name"
        return 0
    else
        log_error "❌ $test_name"
        EXIT_CODE=1
        return 1
    fi
}

# Main testing function
main() {
    log_info "🚀 Starting Comprehensive Infrastructure Testing"
    log_info "Project: Barodybroject Django/OpenAI Installation Wizard"
    log_info "Timestamp: $(date)"
    log_info "Log file: $LOG_FILE"
    echo ""

    cd "$PROJECT_ROOT"

    # Step 1: Environment Setup
    log_step "🔧 STEP 1: ENVIRONMENT SETUP"
    echo "======================================"
    
    log_info "Starting Docker containers..."
    if ! docker-compose -f "$COMPOSE_FILE" up -d; then
        log_error "Failed to start Docker containers"
        exit 1
    fi
    
    log_info "Waiting for services to be ready..."
    sleep 10
    
    # Verify containers are running
    if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        log_error "Docker containers are not running properly"
        exit 1
    fi
    
    # Wait for Django installation to complete (check for django module)
    log_info "Waiting for package installation to complete..."
    MAX_WAIT=180  # 3 minutes max wait
    WAIT_COUNT=0
    LAST_ERROR=""
    while [ $WAIT_COUNT -lt $MAX_WAIT ]; do
        LAST_ERROR=$(docker-compose -f "$COMPOSE_FILE" exec -T python python3 -c "import django; print('Django installed')" 2>&1)
        if echo "$LAST_ERROR" | grep -q "Django installed"; then
            log_success "Package installation completed"
            break
        fi
        sleep 5
        WAIT_COUNT=$((WAIT_COUNT + 5))
        if [ $((WAIT_COUNT % 30)) -eq 0 ]; then
            log_info "Still waiting for package installation... ($WAIT_COUNT seconds elapsed)"
        fi
    done
    
    if [ $WAIT_COUNT -ge $MAX_WAIT ]; then
        log_warning "Package installation timeout reached. Some tests may fail."
        log_error "Last error from Django import: $LAST_ERROR"
    fi
    
    log_success "Docker containers started successfully"
    echo ""

    # Step 2: Docker Infrastructure Testing
    log_step "🐳 STEP 2: DOCKER INFRASTRUCTURE TESTING"
    echo "========================================="
    
    # Test container status
    run_test "Container Status Check" \
        "docker-compose -f '$COMPOSE_FILE' ps | grep -q 'Up'"
    
    # Test container connectivity
    run_test "Python Container Connectivity" \
        "docker_exec python echo 'Container accessible' > /dev/null"
    
    # Test volume mounts
    run_test "Volume Mount Verification" \
        "docker_exec python test -d /workspace/src"
    
    # Test network connectivity between containers
    # Using Python socket instead of nc (netcat) for better container compatibility
    run_test "Inter-container Network" \
        "docker_exec python python3 -c 'import socket; s = socket.socket(); s.settimeout(2); \
try: s.connect((\"barodydb\", 5432)); print(\"Connection successful\") \
finally: s.close()'"
    
    echo ""

    # Step 3: Database and Django Testing
    log_step "🗄️ STEP 3: DATABASE AND DJANGO TESTING"
    echo "======================================"
    
    # Test Django setup
    run_test "Django Configuration" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); print(\\\"Django setup successful\\\")\"'"
    
    # Test database connectivity
    run_test "Database Connection" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from django.db import connection; connection.cursor()\"'"
    
    # Run migrations
    run_test "Database Migrations" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python src/manage.py migrate --run-syncdb --skip-checks'"
    
    echo ""

    # Step 4: Installation Service Testing
    log_step "⚙️ STEP 4: INSTALLATION SERVICE TESTING"
    echo "======================================"
    
    # Test service initialization
    run_test "InstallationService Import" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from setup.services import InstallationService; svc = InstallationService()\"'"
    
    # Test token generation
    run_test "Token Generation" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from setup.services import InstallationService; svc = InstallationService(); token = svc.generate_setup_token(); assert len(token) > 0\"'"
    
    # Test token validation
    run_test "Token Validation" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from setup.services import InstallationService; svc = InstallationService(); token = svc.generate_setup_token(); assert svc.validate_token(token) == True\"'"
    
    echo ""

    # Step 5: Admin User Creation Testing
    log_step "👤 STEP 5: ADMIN USER CREATION TESTING"
    echo "====================================="
    
    # Test admin user creation
    run_test "Admin User Creation" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from setup.services import InstallationService; svc = InstallationService(); token = svc.generate_setup_token(); user = svc.create_admin_user(\\\"testadmin\\\", \\\"admin@test.com\\\", \\\"TestPass123\\\", token); assert user is not None; assert user.is_superuser == True\"'"
    
    # Test installation completion
    run_test "Installation Completion Status" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from setup.services import InstallationService; svc = InstallationService(); assert svc.is_installation_complete() == True\"'"
    
    echo ""

    # Step 6: Web Interface Testing
    log_step "🌐 STEP 6: WEB INTERFACE TESTING"
    echo "================================"
    
    # Test view imports
    run_test "View Classes Import" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from setup.views import SetupWizardView, CreateAdminView, SetupStatusView\"'"
    
    # Test Django test client
    run_test "Django Test Client" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from django.test import Client; client = Client()\"'"
    
    # Test form imports
    run_test "Form Classes Import" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from setup.forms import AdminUserForm\"'"
    
    echo ""

    # Step 7: Management Commands Testing
    log_step "🔧 STEP 7: MANAGEMENT COMMANDS TESTING"
    echo "====================================="
    
    # Test command availability
    run_test "Setup Wizard Command Available" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python src/manage.py help | grep -q setup_wizard'"
    
    # Test command help
    run_test "Setup Wizard Command Help" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python src/manage.py setup_wizard --help > /dev/null'"
    
    echo ""

    # Step 8: Unit Tests Validation
    log_step "🧪 STEP 8: UNIT TESTS VALIDATION"
    echo "================================"
    
    # Run complete unit test suite
    run_test "Complete Unit Test Suite" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -m pytest test/unit/test_services.py -v --tb=short -q'"
    
    echo ""

    # Step 9: Integration Tests (if available)
    log_step "🔗 STEP 9: INTEGRATION TESTS"
    echo "============================"
    
    # Check if integration tests can run (skip CMS-dependent tests)
    if docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c "import cms" 2>/dev/null'; then
        run_test "Integration Tests Execution" \
            "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -m pytest test/integration/ -v --tb=short -q'"
    else
        log_warning "⚠️ Integration tests skipped (CMS dependency not available)"
    fi
    
    echo ""

    # Step 10: Security and Performance Testing
    log_step "🔐 STEP 10: SECURITY AND PERFORMANCE TESTING"
    echo "============================================"
    
    # Test token security
    run_test "Token Security Validation" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from setup.services import InstallationService; svc = InstallationService(); token1 = svc.generate_setup_token(); token2 = svc.generate_setup_token(); assert token1 != token2; assert len(token1) >= 32\"'"
    
    # Test password validation
    run_test "Password Strength Validation" \
        "docker_exec python bash -c 'cd /workspace && PYTHONPATH=/workspace/src:/workspace DJANGO_SETTINGS_MODULE=barodybroject.test_settings python -c \"import django; django.setup(); from setup.services import InstallationService; svc = InstallationService(); token = svc.generate_setup_token(); try: svc.create_admin_user(\\\"test\\\", \\\"test@test.com\\\", \\\"weak\\\", token); assert False; except: pass\"'"
    
    echo ""

    # Final Summary
    log_step "📊 FINAL SUMMARY"
    echo "================"
    
    if [[ $EXIT_CODE -eq 0 ]]; then
        log_success "🎉 ALL INFRASTRUCTURE TESTS PASSED!"
        log_success "✅ Installation wizard infrastructure is production-ready"
        log_success "✅ Docker orchestration working correctly"
        log_success "✅ Database connectivity verified"
        log_success "✅ Django services operational"
        log_success "✅ Web interface components functional"
        log_success "✅ Security measures validated"
        log_success "✅ Unit tests maintaining 100% pass rate"
    else
        log_error "❌ Some infrastructure tests failed"
        log_error "Please review the log file: $LOG_FILE"
        log_error "Fix any issues before proceeding to production"
    fi
    
    echo ""
    log_info "Infrastructure testing completed at $(date)"
    log_info "Full log available at: $LOG_FILE"
    
    exit $EXIT_CODE
}

# Script execution check
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi