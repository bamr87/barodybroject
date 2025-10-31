#!/bin/bash
# File: test-init-setup.sh
# Description: Automated test suite for init_setup.sh
# Author: Barodybroject Team
# Created: 2025-10-30
# Version: 1.0.0

set -euo pipefail

readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0
TEST_LOG="/tmp/init_setup_test_$(date +%Y%m%d_%H%M%S).log"

log_test() {
    echo -e "${BLUE}[TEST]${NC} $1" | tee -a "$TEST_LOG"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1" | tee -a "$TEST_LOG"
    ((TESTS_PASSED++))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1" | tee -a "$TEST_LOG"
    ((TESTS_FAILED++))
}

test_script_exists() {
    log_test "Checking if init_setup.sh exists..."
    if [ -f "./init_setup.sh" ]; then
        log_pass "init_setup.sh found"
        return 0
    else
        log_fail "init_setup.sh not found"
        return 1
    fi
}

test_script_executable() {
    log_test "Checking if init_setup.sh is executable..."
    if [ -x "./init_setup.sh" ]; then
        log_pass "init_setup.sh is executable"
        return 0
    else
        log_fail "init_setup.sh is not executable"
        return 1
    fi
}

test_syntax() {
    log_test "Checking bash syntax..."
    if bash -n ./init_setup.sh; then
        log_pass "Bash syntax is valid"
        return 0
    else
        log_fail "Bash syntax errors found"
        return 1
    fi
}

test_shebang() {
    log_test "Checking shebang..."
    local shebang=$(head -1 ./init_setup.sh)
    if [[ "$shebang" == "#!/bin/bash" ]]; then
        log_pass "Correct shebang found"
        return 0
    else
        log_fail "Incorrect shebang: $shebang"
        return 1
    fi
}

test_error_handling() {
    log_test "Checking error handling (set -euo pipefail)..."
    if grep -q "set -euo pipefail" ./init_setup.sh; then
        log_pass "Error handling enabled"
        return 0
    else
        log_fail "Error handling not found"
        return 1
    fi
}

test_logging_functions() {
    log_test "Checking logging functions..."
    local required_functions=("log_info" "log_success" "log_warning" "log_error")
    local all_found=true
    
    for func in "${required_functions[@]}"; do
        if ! grep -q "^${func}()" ./init_setup.sh; then
            log_fail "Function $func not found"
            all_found=false
        fi
    done
    
    if $all_found; then
        log_pass "All logging functions found"
        return 0
    else
        return 1
    fi
}

test_dependency_checks() {
    log_test "Checking dependency check functions..."
    if grep -q "check_dependencies()" ./init_setup.sh; then
        log_pass "Dependency checking function found"
        return 0
    else
        log_fail "Dependency checking function not found"
        return 1
    fi
}

test_setup_modes() {
    log_test "Checking setup mode functions..."
    local modes=("setup_docker" "setup_local" "setup_azure" "setup_testing")
    local all_found=true
    
    for mode in "${modes[@]}"; do
        if ! grep -q "^${mode}()" ./init_setup.sh; then
            log_fail "Function $mode not found"
            all_found=false
        fi
    done
    
    if $all_found; then
        log_pass "All setup mode functions found"
        return 0
    else
        return 1
    fi
}

test_pip_detection() {
    log_test "Checking pip detection logic..."
    # Check that we use the correct logic (AND not OR)
    if grep -q 'command_exists pip3 && ! command_exists pip' ./init_setup.sh; then
        log_pass "Correct pip detection logic found"
        return 0
    else
        log_fail "Pip detection logic may be incorrect"
        return 1
    fi
}

test_os_detection() {
    log_test "Checking OS detection..."
    if grep -q "detect_os()" ./init_setup.sh; then
        log_pass "OS detection function found"
        return 0
    else
        log_fail "OS detection function not found"
        return 1
    fi
}

test_color_codes() {
    log_test "Checking color code definitions..."
    local colors=("RED" "GREEN" "YELLOW" "BLUE" "NC")
    local all_found=true
    
    for color in "${colors[@]}"; do
        if ! grep -q "readonly ${color}=" ./init_setup.sh; then
            log_fail "Color $color not defined"
            all_found=false
        fi
    done
    
    if $all_found; then
        log_pass "All color codes defined"
        return 0
    else
        return 1
    fi
}

test_log_directory() {
    log_test "Checking log directory creation..."
    if grep -q 'mkdir -p.*LOG_DIR' ./init_setup.sh; then
        log_pass "Log directory creation found"
        return 0
    else
        log_fail "Log directory creation not found"
        return 1
    fi
}

test_cleanup_handler() {
    log_test "Checking cleanup and exit handler..."
    if grep -q "cleanup_and_exit()" ./init_setup.sh; then
        log_pass "Cleanup handler found"
        return 0
    else
        log_fail "Cleanup handler not found"
        return 1
    fi
}

test_error_trap() {
    log_test "Checking error trap..."
    if grep -q "trap.*ERR" ./init_setup.sh; then
        log_pass "Error trap configured"
        return 0
    else
        log_fail "Error trap not found"
        return 1
    fi
}

print_summary() {
    echo ""
    echo "========================================="
    echo "Test Summary"
    echo "========================================="
    echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
    echo ""
    echo "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"
    echo "Success Rate: $(( TESTS_PASSED * 100 / (TESTS_PASSED + TESTS_FAILED) ))%"
    echo ""
    echo "Full log: $TEST_LOG"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed! ✅${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed! ❌${NC}"
        return 1
    fi
}

main() {
    echo "========================================="
    echo "Init Setup Script Test Suite"
    echo "========================================="
    echo "Testing: ./init_setup.sh"
    echo "Date: $(date)"
    echo "Log: $TEST_LOG"
    echo ""
    
    # Run all tests
    test_script_exists || true
    test_script_executable || true
    test_syntax || true
    test_shebang || true
    test_error_handling || true
    test_logging_functions || true
    test_dependency_checks || true
    test_setup_modes || true
    test_pip_detection || true
    test_os_detection || true
    test_color_codes || true
    test_log_directory || true
    test_cleanup_handler || true
    test_error_trap || true
    
    # Print summary
    print_summary
}

main "$@"
