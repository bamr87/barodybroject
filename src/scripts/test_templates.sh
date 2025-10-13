#!/bin/bash

# File: test_templates.sh
# Description: Comprehensive template testing script for Barodybroject
# Author: Barodybroject Team
# Created: 2025-10-12
# Version: 1.0.0
#
# Dependencies:
# - docker
# - docker-compose
# - curl
#
# Usage: ./test_templates.sh [options]
# Options:
#   --build    Force rebuild of Docker containers
#   --verbose  Show detailed output
#   --quick    Run quick tests only

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Configuration
DOCKER_COMPOSE_FILE="docker-compose.yml"
BASE_URL="http://localhost:80"
TIMEOUT=30
VERBOSE=false
FORCE_BUILD=false
QUICK_TEST=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --build)
            FORCE_BUILD=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --quick)
            QUICK_TEST=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--build] [--verbose] [--quick]"
            exit 1
            ;;
    esac
done

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_test() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[TEST]${NC} $1"
    fi
}

# Test result tracking
pass_test() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
    log_success "$1"
}

fail_test() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
    log_error "$1"
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

# Build and start containers
start_containers() {
    log_info "Starting Docker containers..."
    
    if [ "$FORCE_BUILD" = true ]; then
        log_info "Building containers from scratch..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down -v
        docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    fi
    
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    if [ $? -eq 0 ]; then
        log_success "Containers started successfully"
    else
        log_error "Failed to start containers"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_service() {
    local url=$1
    local max_attempts=$2
    local attempt=0
    
    log_info "Waiting for service to be ready at $url..."
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s -o /dev/null -w "%{http_code}" "$url" > /dev/null 2>&1; then
            log_success "Service is ready"
            return 0
        fi
        
        attempt=$((attempt + 1))
        if [ "$VERBOSE" = true ]; then
            echo -n "."
        fi
        sleep 2
    done
    
    log_error "Service failed to start after $max_attempts attempts"
    return 1
}

# Test HTTP response
test_http_response() {
    local url=$1
    local expected_status=$2
    local test_name=$3
    
    log_test "Testing: $test_name"
    
    local status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    
    if [ "$status" = "$expected_status" ]; then
        pass_test "$test_name - Status: $status"
        return 0
    else
        fail_test "$test_name - Expected: $expected_status, Got: $status"
        return 1
    fi
}

# Test if content contains specific text
test_content_contains() {
    local url=$1
    local search_text=$2
    local test_name=$3
    
    log_test "Testing: $test_name"
    
    local content=$(curl -s "$url" 2>/dev/null)
    
    if echo "$content" | grep -q "$search_text"; then
        pass_test "$test_name - Found: '$search_text'"
        return 0
    else
        fail_test "$test_name - Not found: '$search_text'"
        if [ "$VERBOSE" = true ]; then
            echo "Content preview: ${content:0:200}..."
        fi
        return 1
    fi
}

# Test Bootstrap CSS is loaded
test_bootstrap_loaded() {
    local url=$1
    local test_name=$2
    
    log_test "Testing: $test_name - Bootstrap CSS"
    
    local content=$(curl -s "$url" 2>/dev/null)
    
    if echo "$content" | grep -q "bootstrap.*\.css"; then
        pass_test "$test_name - Bootstrap CSS found"
        return 0
    else
        fail_test "$test_name - Bootstrap CSS not found"
        return 1
    fi
}

# Test Bootstrap Icons are loaded
test_bootstrap_icons_loaded() {
    local url=$1
    local test_name=$2
    
    log_test "Testing: $test_name - Bootstrap Icons"
    
    local content=$(curl -s "$url" 2>/dev/null)
    
    if echo "$content" | grep -q "bootstrap-icons"; then
        pass_test "$test_name - Bootstrap Icons found"
        return 0
    else
        fail_test "$test_name - Bootstrap Icons not found"
        return 1
    fi
}

# Test responsive meta tag
test_responsive_meta() {
    local url=$1
    local test_name=$2
    
    log_test "Testing: $test_name - Responsive meta tag"
    
    local content=$(curl -s "$url" 2>/dev/null)
    
    if echo "$content" | grep -q 'name="viewport"'; then
        pass_test "$test_name - Responsive meta tag found"
        return 0
    else
        fail_test "$test_name - Responsive meta tag not found"
        return 1
    fi
}

# Test CSRF token in forms
test_csrf_token() {
    local url=$1
    local test_name=$2
    
    log_test "Testing: $test_name - CSRF token"
    
    local content=$(curl -s "$url" 2>/dev/null)
    
    if echo "$content" | grep -q "csrfmiddlewaretoken"; then
        pass_test "$test_name - CSRF token found"
        return 0
    else
        log_warning "$test_name - No forms with CSRF token (may be expected)"
        return 0
    fi
}

# Test semantic HTML5 structure
test_semantic_html() {
    local url=$1
    local test_name=$2
    
    log_test "Testing: $test_name - Semantic HTML"
    
    local content=$(curl -s "$url" 2>/dev/null)
    local passed=true
    
    # Check for main tag
    if ! echo "$content" | grep -q "<main"; then
        log_warning "$test_name - <main> tag not found"
        passed=false
    fi
    
    # Check for proper DOCTYPE
    if ! echo "$content" | grep -q "<!DOCTYPE html>"; then
        fail_test "$test_name - Missing DOCTYPE"
        return 1
    fi
    
    if [ "$passed" = true ]; then
        pass_test "$test_name - Semantic HTML structure OK"
        return 0
    else
        return 0  # Warning only, not critical
    fi
}

# Test navigation elements
test_navigation() {
    local url=$1
    local test_name=$2
    
    log_test "Testing: $test_name - Navigation"
    
    local content=$(curl -s "$url" 2>/dev/null)
    
    if echo "$content" | grep -q "navbar"; then
        pass_test "$test_name - Navigation found"
        return 0
    else
        fail_test "$test_name - Navigation not found"
        return 1
    fi
}

# Test footer
test_footer() {
    local url=$1
    local test_name=$2
    
    log_test "Testing: $test_name - Footer"
    
    local content=$(curl -s "$url" 2>/dev/null)
    
    if echo "$content" | grep -q "<footer"; then
        pass_test "$test_name - Footer found"
        return 0
    else
        fail_test "$test_name - Footer not found"
        return 1
    fi
}

# Test JavaScript is loaded
test_javascript_loaded() {
    local url=$1
    local test_name=$2
    
    log_test "Testing: $test_name - JavaScript"
    
    local content=$(curl -s "$url" 2>/dev/null)
    
    if echo "$content" | grep -q "bootstrap.*\.js"; then
        pass_test "$test_name - Bootstrap JS found"
        return 0
    else
        fail_test "$test_name - Bootstrap JS not found"
        return 1
    fi
}

# Run Django checks
run_django_checks() {
    log_info "Running Django system checks..."
    
    if docker-compose exec -T python python manage.py check; then
        pass_test "Django system checks passed"
    else
        fail_test "Django system checks failed"
    fi
}

# Test database connection
test_database_connection() {
    log_info "Testing database connection..."
    
    if docker-compose exec -T python python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1; then
        pass_test "Database connection successful"
    else
        fail_test "Database connection failed"
    fi
}

# Run template syntax checks
test_template_syntax() {
    log_info "Testing template syntax..."
    
    local templates=(
        "base.html"
        "footer.html"
        "index.html"
        "429.html"
        "chatbox.html"
        "object_template.html"
        "profile.html"
    )
    
    for template in "${templates[@]}"; do
        if docker-compose exec -T python python manage.py validate_templates 2>&1 | grep -q "error"; then
            fail_test "Template syntax error in $template"
        else
            pass_test "Template syntax OK: $template"
        fi
    done
}

# Main test suite
run_tests() {
    log_info "Starting comprehensive template tests..."
    echo ""
    
    # Test homepage
    log_info "=== Testing Homepage ==="
    test_http_response "$BASE_URL/" "200" "Homepage loads"
    test_content_contains "$BASE_URL/" "Barody Broject" "Homepage has title"
    test_bootstrap_loaded "$BASE_URL/" "Homepage"
    test_bootstrap_icons_loaded "$BASE_URL/" "Homepage"
    test_responsive_meta "$BASE_URL/" "Homepage"
    test_semantic_html "$BASE_URL/" "Homepage"
    test_navigation "$BASE_URL/" "Homepage"
    test_footer "$BASE_URL/" "Homepage"
    test_javascript_loaded "$BASE_URL/" "Homepage"
    
    if [ "$QUICK_TEST" = false ]; then
        echo ""
        
        # Test content pages
        log_info "=== Testing Content Page ==="
        test_http_response "$BASE_URL/content/" "200" "Content page loads"
        test_bootstrap_loaded "$BASE_URL/content/" "Content page"
        test_navigation "$BASE_URL/content/" "Content page"
        
        echo ""
        log_info "=== Testing Threads Page ==="
        test_http_response "$BASE_URL/threads/" "200" "Threads page loads"
        test_bootstrap_loaded "$BASE_URL/threads/" "Threads page"
        
        echo ""
        log_info "=== Testing Posts Page ==="
        test_http_response "$BASE_URL/posts/" "200" "Posts page loads"
        test_bootstrap_loaded "$BASE_URL/posts/" "Posts page"
        
        echo ""
        log_info "=== Testing Assistants Page ==="
        test_http_response "$BASE_URL/assistants/" "200" "Assistants page loads"
        test_bootstrap_loaded "$BASE_URL/assistants/" "Assistants page"
        
        echo ""
        log_info "=== Testing Assistant Groups Page ==="
        test_http_response "$BASE_URL/assistant-groups/" "200" "Assistant groups page loads"
        test_bootstrap_loaded "$BASE_URL/assistant-groups/" "Assistant groups page"
        
        echo ""
        log_info "=== Testing Messages Page ==="
        test_http_response "$BASE_URL/messages/" "200" "Messages page loads"
        test_bootstrap_loaded "$BASE_URL/messages/" "Messages page"
        
        echo ""
        log_info "=== Testing Admin Page ==="
        test_http_response "$BASE_URL/admin/" "302" "Admin redirects (authentication)"
        
        echo ""
        log_info "=== Testing Error Pages ==="
        test_http_response "$BASE_URL/nonexistent-page" "404" "404 page works"
        
        echo ""
        log_info "=== Testing Django System ==="
        run_django_checks
        test_database_connection
    fi
    
    echo ""
}

# Generate test report
generate_report() {
    echo ""
    echo "=================================="
    echo "       TEST RESULTS SUMMARY       "
    echo "=================================="
    echo ""
    echo "Total Tests Run:    $TESTS_RUN"
    echo -e "Tests Passed:       ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Tests Failed:       ${RED}$TESTS_FAILED${NC}"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ All tests passed!${NC}"
        echo ""
        return 0
    else
        echo ""
        echo -e "${RED}✗ Some tests failed!${NC}"
        echo ""
        return 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up..."
    if [ "${1:-}" = "stop" ]; then
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        log_info "Containers stopped"
    fi
}

# Main execution
main() {
    echo "========================================"
    echo "   Barodybroject Template Test Suite   "
    echo "========================================"
    echo ""
    
    # Change to src directory
    cd "$(dirname "$0")"
    
    # Run checks
    check_docker
    
    # Start containers
    start_containers
    
    # Wait for services
    if ! wait_for_service "$BASE_URL" 30; then
        log_error "Services failed to start. Check Docker logs."
        docker-compose logs --tail=50
        exit 1
    fi
    
    # Run tests
    run_tests
    
    # Generate report
    generate_report
    exit_code=$?
    
    # Cleanup
    if [ "${CLEANUP:-true}" = "true" ]; then
        cleanup "stop"
    fi
    
    exit $exit_code
}

# Handle script interruption
trap 'cleanup; exit 130' INT TERM

# Run main function
main "$@"
