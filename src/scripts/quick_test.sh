#!/bin/bash

# Quick template test script - assumes containers are already running
# Usage: ./quick_test.sh

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

BASE_URL="http://localhost:80"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[PASS]${NC} $1"; }
log_error() { echo -e "${RED}[FAIL]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Test HTTP status code
test_http_status() {
    local url=$1
    local expected=$2
    local description=$3
    
    TESTS_RUN=$((TESTS_RUN + 1))
    log_info "Testing: $description"
    
    local status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$status" -eq "$expected" ]; then
        log_success "HTTP $status (expected $expected)"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "HTTP $status (expected $expected)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test content contains string
test_content_contains() {
    local url=$1
    local search_string=$2
    local description=$3
    
    TESTS_RUN=$((TESTS_RUN + 1))
    log_info "Testing: $description"
    
    local content=$(curl -s "$url")
    
    if echo "$content" | grep -q "$search_string"; then
        log_success "Content contains: $search_string"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "Content does not contain: $search_string"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Test Bootstrap 5 is loaded
test_bootstrap() {
    local url=$1
    
    TESTS_RUN=$((TESTS_RUN + 1))
    log_info "Testing Bootstrap 5 integration"
    
    local content=$(curl -s "$url")
    
    if echo "$content" | grep -q "bootstrap@5"; then
        log_success "Bootstrap 5 CSS found"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        log_error "Bootstrap 5 CSS not found"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Main test execution
echo "========================================"
echo "   Quick Template Test Suite"
echo "========================================"
echo ""

# Test 1: Homepage
test_http_status "$BASE_URL/" 200 "Homepage loads"
test_content_contains "$BASE_URL/" "Welcome to Barody Broject" "Homepage has title"
test_bootstrap "$BASE_URL/"

# Test 2: Check for jQuery removal (should NOT contain jQuery)
TESTS_RUN=$((TESTS_RUN + 1))
log_info "Testing: jQuery removal"
content=$(curl -s "$BASE_URL/")
if echo "$content" | grep -q "jquery"; then
    log_warning "jQuery still found (should be removed)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
else
    log_success "jQuery successfully removed"
    TESTS_PASSED=$((TESTS_PASSED + 1))
fi

# Test 3: Check Bootstrap classes
test_content_contains "$BASE_URL/" "container" "Bootstrap container class"
test_content_contains "$BASE_URL/" "navbar" "Bootstrap navbar"

# Test 4: Check semantic HTML
test_content_contains "$BASE_URL/" "<main" "Semantic HTML main tag"
test_content_contains "$BASE_URL/" "<footer" "Semantic HTML footer tag"

# Test 5: Check accessibility
test_content_contains "$BASE_URL/" "aria-label" "ARIA labels present"

# Test 6: Check security attributes
test_content_contains "$BASE_URL/" 'rel="noopener noreferrer"' "Security attributes on links"

# Test 7: 404 page (if accessible via /404/)
log_info "Testing: 404 page"
status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/nonexistent-page/")
if [ "$status" -eq 404 ]; then
    log_success "404 page configured correctly"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    log_warning "404 page status: $status (expected 404)"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi
TESTS_RUN=$((TESTS_RUN + 1))

# Summary
echo ""
echo "========================================"
echo "           Test Summary"
echo "========================================"
echo -e "Total Tests:  $TESTS_RUN"
echo -e "${GREEN}Passed:       $TESTS_PASSED${NC}"
echo -e "${RED}Failed:       $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
