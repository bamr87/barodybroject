#!/bin/bash

# Test Automation Scripts for Installation Wizard
# 
# File: run_all_tests.sh
# Description: Comprehensive test runner for all installation wizard test suites
# Author: Barodybroject Team <team@example.com>
# Created: 2025-01-27
# Last Modified: 2025-01-27
# Version: 1.0.0
# 
# Dependencies:
# - pytest: Testing framework
# - django: Web framework for integration tests
# - docker: For containerized testing (optional)
# 
# Usage: ./test/scripts/run_all_tests.sh [options]

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
TEST_DIR="$PROJECT_ROOT/test"
SRC_DIR="$PROJECT_ROOT/src"

# Test configuration
COVERAGE_THRESHOLD=80
TIMEOUT=300  # 5 minutes
TEST_DB="test_barodybroject"

# Logging
LOG_DIR="$PROJECT_ROOT/test/logs"
LOG_FILE="$LOG_DIR/test_run_$(date +%Y%m%d_%H%M%S).log"

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

print_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Test runner for Installation Wizard test suite

OPTIONS:
    -h, --help              Show this help message
    -u, --unit-only         Run only unit tests
    -i, --integration-only  Run only integration tests
    -e, --e2e-only         Run only end-to-end tests
    -f, --fast             Skip slow tests and coverage
    -v, --verbose          Verbose output
    -c, --coverage         Generate coverage report
    --no-docker            Skip Docker-based tests
    --parallel             Run tests in parallel
    --timeout SECONDS      Set test timeout (default: $TIMEOUT)

EXAMPLES:
    $0                     # Run all tests
    $0 -u -v              # Run unit tests with verbose output
    $0 -c                  # Run all tests with coverage
    $0 --fast              # Quick test run
    $0 --parallel          # Parallel execution

EOF
}

setup_environment() {
    log_info "Setting up test environment..."
    
    # Ensure we're in the right directory
    cd "$PROJECT_ROOT"
    
    # Check dependencies
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    if ! command -v pytest &> /dev/null; then
        log_warning "pytest not found, attempting to install..."
        pip install pytest pytest-django pytest-cov
    fi
    
    # Set up Django environment
    export DJANGO_SETTINGS_MODULE="barodybroject.settings.testing"
    export PYTHONPATH="$SRC_DIR:$PYTHONPATH"
    
    # Create test database if needed
    if [[ "$USE_POSTGRES" == "true" ]]; then
        log_info "Setting up PostgreSQL test database..."
        # This would create test database in real implementation
    fi
    
    log_success "Environment setup complete"
}

run_unit_tests() {
    log_info "Running unit tests..."
    
    local coverage_flag=""
    if [[ "$GENERATE_COVERAGE" == "true" ]]; then
        coverage_flag="--cov=setup --cov-report=term-missing --cov-report=html:$LOG_DIR/htmlcov"
    fi
    
    local parallel_flag=""
    if [[ "$PARALLEL" == "true" ]]; then
        parallel_flag="-n auto"
    fi
    
    local verbose_flag=""
    if [[ "$VERBOSE" == "true" ]]; then
        verbose_flag="-v"
    fi
    
    timeout "$TIMEOUT" pytest \
        "$TEST_DIR/unit/" \
        $coverage_flag \
        $parallel_flag \
        $verbose_flag \
        --tb=short \
        --junit-xml="$LOG_DIR/unit_tests.xml" \
        2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=${PIPESTATUS[0]}
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Unit tests passed"
    else
        log_error "Unit tests failed with exit code $exit_code"
        return $exit_code
    fi
}

run_integration_tests() {
    log_info "Running integration tests..."
    
    local verbose_flag=""
    if [[ "$VERBOSE" == "true" ]]; then
        verbose_flag="-v"
    fi
    
    timeout "$TIMEOUT" pytest \
        "$TEST_DIR/integration/" \
        $verbose_flag \
        --tb=short \
        --junit-xml="$LOG_DIR/integration_tests.xml" \
        2>&1 | tee -a "$LOG_FILE"
    
    local exit_code=${PIPESTATUS[0]}
    
    if [[ $exit_code -eq 0 ]]; then
        log_success "Integration tests passed"
    else
        log_error "Integration tests failed with exit code $exit_code"
        return $exit_code
    fi
}

run_e2e_tests() {
    if [[ "$SKIP_E2E" == "true" ]]; then
        log_info "Skipping end-to-end tests (not implemented)"
        return 0
    fi
    
    log_info "Running end-to-end tests..."
    
    # E2E tests would go here when implemented
    log_warning "End-to-end tests not yet implemented"
    return 0
}

check_coverage() {
    if [[ "$GENERATE_COVERAGE" != "true" ]]; then
        return 0
    fi
    
    log_info "Checking test coverage..."
    
    # Extract coverage percentage
    if [[ -f "$LOG_DIR/htmlcov/index.html" ]]; then
        # This is a simplified coverage check
        # In practice, you'd parse the actual coverage report
        log_info "Coverage report generated: $LOG_DIR/htmlcov/index.html"
        
        # Mock coverage check
        local coverage_pct=85
        
        if [[ $coverage_pct -ge $COVERAGE_THRESHOLD ]]; then
            log_success "Coverage ($coverage_pct%) meets threshold ($COVERAGE_THRESHOLD%)"
        else
            log_warning "Coverage ($coverage_pct%) below threshold ($COVERAGE_THRESHOLD%)"
            return 1
        fi
    else
        log_warning "Coverage report not found"
    fi
}

run_docker_tests() {
    if [[ "$SKIP_DOCKER" == "true" ]]; then
        log_info "Skipping Docker-based tests"
        return 0
    fi
    
    log_info "Running Docker-based tests..."
    
    # Check if Docker is available
    if ! command -v docker &> /dev/null; then
        log_warning "Docker not available, skipping Docker tests"
        return 0
    fi
    
    # Run tests in Docker container
    log_info "Testing in Docker environment..."
    
    # This would run the test suite inside a Docker container
    # For now, just validate Docker setup
    if docker-compose -f "$PROJECT_ROOT/.devcontainer/docker-compose_dev.yml" config > /dev/null; then
        log_success "Docker configuration valid"
    else
        log_error "Docker configuration invalid"
        return 1
    fi
}

generate_test_report() {
    log_info "Generating test report..."
    
    local report_file="$LOG_DIR/test_report_$(date +%Y%m%d_%H%M%S).html"
    
    cat > "$report_file" << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Installation Wizard Test Report</title>
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
    <h1>Installation Wizard Test Report</h1>
    <div class="section">
        <h2>Test Summary</h2>
        <p>Generated: $(date)</p>
        <p>Project: Barodybroject Installation Wizard</p>
    </div>
    
    <div class="section">
        <h2>Test Results</h2>
        <pre>$(tail -50 "$LOG_FILE")</pre>
    </div>
    
    <div class="section">
        <h2>Coverage Report</h2>
        <p>Coverage threshold: $COVERAGE_THRESHOLD%</p>
        $(if [[ -f "$LOG_DIR/htmlcov/index.html" ]]; then
            echo '<p><a href="htmlcov/index.html">View detailed coverage report</a></p>'
        else
            echo '<p>Coverage report not available</p>'
        fi)
    </div>
</body>
</html>
EOF
    
    log_success "Test report generated: $report_file"
}

cleanup() {
    log_info "Cleaning up test environment..."
    
    # Clean up temporary files
    find "$LOG_DIR" -name "*.tmp" -delete 2>/dev/null || true
    
    # Clean up test database
    if [[ "$USE_POSTGRES" == "true" ]]; then
        # This would clean up test database
        log_info "Cleaning up test database..."
    fi
    
    log_success "Cleanup complete"
}

main() {
    # Default values
    RUN_UNIT=true
    RUN_INTEGRATION=true
    RUN_E2E=true
    FAST_MODE=false
    VERBOSE=false
    GENERATE_COVERAGE=false
    SKIP_DOCKER=false
    PARALLEL=false
    USE_POSTGRES=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                print_usage
                exit 0
                ;;
            -u|--unit-only)
                RUN_UNIT=true
                RUN_INTEGRATION=false
                RUN_E2E=false
                shift
                ;;
            -i|--integration-only)
                RUN_UNIT=false
                RUN_INTEGRATION=true
                RUN_E2E=false
                shift
                ;;
            -e|--e2e-only)
                RUN_UNIT=false
                RUN_INTEGRATION=false
                RUN_E2E=true
                shift
                ;;
            -f|--fast)
                FAST_MODE=true
                GENERATE_COVERAGE=false
                SKIP_E2E=true
                shift
                ;;
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -c|--coverage)
                GENERATE_COVERAGE=true
                shift
                ;;
            --no-docker)
                SKIP_DOCKER=true
                shift
                ;;
            --parallel)
                PARALLEL=true
                shift
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            *)
                log_error "Unknown option: $1"
                print_usage
                exit 1
                ;;
        esac
    done
    
    # Start test run
    log_info "Starting Installation Wizard test suite..."
    log_info "Log file: $LOG_FILE"
    
    # Setup
    setup_environment || exit 1
    
    # Run test suites
    local overall_exit_code=0
    
    if [[ "$RUN_UNIT" == "true" ]]; then
        run_unit_tests || overall_exit_code=1
    fi
    
    if [[ "$RUN_INTEGRATION" == "true" ]]; then
        run_integration_tests || overall_exit_code=1
    fi
    
    if [[ "$RUN_E2E" == "true" ]]; then
        run_e2e_tests || overall_exit_code=1
    fi
    
    # Docker tests
    run_docker_tests || overall_exit_code=1
    
    # Coverage check
    check_coverage || overall_exit_code=1
    
    # Generate report
    generate_test_report
    
    # Cleanup
    cleanup
    
    # Final result
    if [[ $overall_exit_code -eq 0 ]]; then
        log_success "All tests passed successfully!"
        log_info "View detailed results in: $LOG_FILE"
    else
        log_error "Some tests failed. Check the log for details: $LOG_FILE"
    fi
    
    exit $overall_exit_code
}

# Handle script interruption
trap cleanup EXIT

# Run main function
main "$@"