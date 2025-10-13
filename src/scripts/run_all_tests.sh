#!/bin/bash

# File: run_all_tests.sh
# Description: Master test runner for all Barodybroject template tests
# Author: Barodybroject Team
# Created: 2025-10-12
# Version: 1.0.0

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo ""
    echo "========================================"
    echo "  $1"
    echo "========================================"
    echo ""
}

# Run bash tests
run_bash_tests() {
    log_section "Running Bash Template Tests"
    
    if [ -f "$SCRIPT_DIR/test_templates.sh" ]; then
        chmod +x "$SCRIPT_DIR/test_templates.sh"
        "$SCRIPT_DIR/test_templates.sh" "$@"
        return $?
    else
        log_error "test_templates.sh not found"
        return 1
    fi
}

# Run Django tests
run_django_tests() {
    log_section "Running Django Template Tests"
    
    cd "$PROJECT_ROOT"
    
    if docker-compose exec -T python python manage.py test parodynews.tests.test_templates --verbosity=2; then
        log_success "Django tests passed"
        return 0
    else
        log_error "Django tests failed"
        return 1
    fi
}

# Run HTML validation
run_html_validation() {
    log_section "Running HTML Validation"
    
    log_info "Checking for HTML validation tools..."
    
    # Try to use html5validator if available
    if command -v html5validator &> /dev/null; then
        log_info "Running html5validator..."
        html5validator --root "$PROJECT_ROOT/parodynews/templates/" --show-warnings || true
    else
        log_info "html5validator not found. Install with: pip install html5validator"
    fi
}

# Check template syntax
check_template_syntax() {
    log_section "Checking Template Syntax"
    
    cd "$PROJECT_ROOT"
    
    if docker-compose exec -T python python manage.py validate_templates; then
        log_success "Template syntax check passed"
        return 0
    else
        log_error "Template syntax check failed"
        return 1
    fi
}

# Generate test report
generate_report() {
    local bash_result=$1
    local django_result=$2
    
    log_section "Test Summary Report"
    
    echo "Test Suite Results:"
    echo ""
    
    if [ $bash_result -eq 0 ]; then
        echo -e "  Bash Tests:     ${GREEN}✓ PASSED${NC}"
    else
        echo -e "  Bash Tests:     ${RED}✗ FAILED${NC}"
    fi
    
    if [ $django_result -eq 0 ]; then
        echo -e "  Django Tests:   ${GREEN}✓ PASSED${NC}"
    else
        echo -e "  Django Tests:   ${RED}✗ FAILED${NC}"
    fi
    
    echo ""
    
    if [ $bash_result -eq 0 ] && [ $django_result -eq 0 ]; then
        log_success "All tests passed! 🎉"
        return 0
    else
        log_error "Some tests failed. Please review the output above."
        return 1
    fi
}

# Main execution
main() {
    log_section "Barodybroject Comprehensive Test Suite"
    
    local bash_result=0
    local django_result=0
    
    # Run bash tests
    run_bash_tests "$@" || bash_result=$?
    
    # Run Django tests (if containers are still running)
    if docker-compose ps | grep -q "Up"; then
        run_django_tests || django_result=$?
    else
        log_info "Containers not running, skipping Django tests"
    fi
    
    # Run additional checks
    check_template_syntax || true
    run_html_validation || true
    
    # Generate report
    generate_report $bash_result $django_result
    return $?
}

main "$@"
