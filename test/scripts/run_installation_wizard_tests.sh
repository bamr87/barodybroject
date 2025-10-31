#!/bin/bash

#
# File: run_installation_wizard_tests.sh
# Description: Comprehensive test runner for installation wizard and infrastructure
# Author: Barodybroject Team <team@example.com>
# Created: 2025-10-30
# Last Modified: 2025-10-30
# Version: 1.0.0
#
# Dependencies:
# - pytest: Python testing framework
# - docker: Container runtime for environment testing
# - django: Web framework
#
# Usage: ./test/scripts/run_installation_wizard_tests.sh [options]

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TEST_DIR="$PROJECT_ROOT/test"
SRC_DIR="$PROJECT_ROOT/src"
LOG_DIR="$TEST_DIR/logs"

# Test configuration
DJANGO_SETTINGS_MODULE="barodybroject.settings"
PYTHONPATH="$SRC_DIR:${PYTHONPATH:-}"
COVERAGE_THRESHOLD=80
TEST_DATABASE_URL="sqlite:///test_installation_wizard.db"

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
Installation Wizard Test Runner

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --unit-only         Run only unit tests
    --integration-only  Run only integration tests
    --fast             Skip slow tests and detailed coverage
    --coverage         Generate detailed coverage report
    --parallel         Run tests in parallel (faster)
    --verbose          Verbose output
    --quiet            Minimal output
    --docker           Run tests in Docker containers
    --clean            Clean up test artifacts before running
    --dry-run          Show what would be tested without running
    --help             Show this help message

EXAMPLES:
    $0                           # Run all tests with default settings
    $0 --unit-only --coverage    # Run unit tests with coverage
    $0 --integration-only        # Run integration tests only
    $0 --fast --parallel         # Quick test run
    $0 --docker --clean          # Full Docker-based testing

ENVIRONMENT VARIABLES:
    COVERAGE_THRESHOLD    Coverage percentage threshold (default: 80)
    TEST_DATABASE_URL     Test database URL (default: SQLite)
    DJANGO_SETTINGS_MODULE Test Django settings module

EOF
}

# Parse command line arguments
UNIT_ONLY=false
INTEGRATION_ONLY=false
FAST_MODE=false
COVERAGE_MODE=false
PARALLEL_MODE=false
VERBOSE_MODE=false
QUIET_MODE=false
DOCKER_MODE=false
CLEAN_MODE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --unit-only)
            UNIT_ONLY=true
            shift
            ;;
        --integration-only)
            INTEGRATION_ONLY=true
            shift
            ;;
        --fast)
            FAST_MODE=true
            shift
            ;;
        --coverage)
            COVERAGE_MODE=true
            shift
            ;;
        --parallel)
            PARALLEL_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE_MODE=true
            shift
            ;;
        --quiet)
            QUIET_MODE=true
            shift
            ;;
        --docker)
            DOCKER_MODE=true
            shift
            ;;
        --clean)
            CLEAN_MODE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
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

# Setup environment
setup_environment() {
    log_info "Setting up test environment..."
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    # Set environment variables
    export DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE"
    export PYTHONPATH="$PYTHONPATH"
    export TEST_DATABASE_URL="$TEST_DATABASE_URL"
    
    # Clean up if requested
    if [ "$CLEAN_MODE" = true ]; then
        log_info "Cleaning up test artifacts..."
        rm -rf "$LOG_DIR"/*.log
        rm -rf "$LOG_DIR"/htmlcov
        rm -rf "$PROJECT_ROOT"/.pytest_cache
        rm -rf "$SRC_DIR"/__pycache__
        find "$TEST_DIR" -name "*.pyc" -delete
        find "$TEST_DIR" -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    fi
    
    # Check dependencies
    check_dependencies
}

# Check required dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python &> /dev/null; then
        log_error "Python is required but not installed"
        exit 1
    fi
    
    # Check pytest
    if ! python -c "import pytest" 2>/dev/null; then
        log_error "pytest is required but not installed. Install with: pip install pytest"
        exit 1
    fi
    
    # Check Django
    if ! python -c "import django" 2>/dev/null; then
        log_error "Django is required but not installed. Install with: pip install django"
        exit 1
    fi
    
    # Check Docker if needed
    if [ "$DOCKER_MODE" = true ]; then
        if ! command -v docker &> /dev/null; then
            log_error "Docker is required for --docker mode but not installed"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            log_error "docker-compose is required for --docker mode but not installed"
            exit 1
        fi
    fi
    
    log_success "All dependencies satisfied"
}

# Build pytest command
build_pytest_command() {
    local pytest_cmd="pytest"
    local pytest_args=""
    
    # Test selection
    if [ "$UNIT_ONLY" = true ]; then
        pytest_args="$pytest_args $TEST_DIR/unit/"
    elif [ "$INTEGRATION_ONLY" = true ]; then
        pytest_args="$pytest_args $TEST_DIR/integration/"
    else
        pytest_args="$pytest_args $TEST_DIR/unit/ $TEST_DIR/integration/"
    fi
    
    # Coverage options
    if [ "$COVERAGE_MODE" = true ] && [ "$FAST_MODE" = false ]; then
        pytest_args="$pytest_args --cov=setup --cov-report=html:$LOG_DIR/htmlcov --cov-report=xml:$LOG_DIR/coverage.xml --cov-report=term"
        pytest_args="$pytest_args --cov-fail-under=$COVERAGE_THRESHOLD"
    fi
    
    # Parallel execution
    if [ "$PARALLEL_MODE" = true ]; then
        pytest_args="$pytest_args -n auto"
    fi
    
    # Verbosity
    if [ "$VERBOSE_MODE" = true ]; then
        pytest_args="$pytest_args -v -s"
    elif [ "$QUIET_MODE" = true ]; then
        pytest_args="$pytest_args -q"
    else
        pytest_args="$pytest_args -v"
    fi
    
    # Fast mode exclusions
    if [ "$FAST_MODE" = true ]; then
        pytest_args="$pytest_args -m 'not slow'"
    fi
    
    # Output formatting
    pytest_args="$pytest_args --tb=short --durations=10"
    
    echo "$pytest_cmd $pytest_args"
}

# Run tests in Docker environment
run_docker_tests() {
    log_info "Running tests in Docker environment..."
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Start development containers
    log_info "Starting Docker containers..."
    docker-compose -f .devcontainer/docker-compose_dev.yml up -d --build
    
    # Wait for containers to be ready
    sleep 10
    
    # Run database migrations
    log_info "Running database migrations..."
    docker-compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py migrate --noinput
    
    # Run tests inside container
    local pytest_cmd=$(build_pytest_command)
    log_info "Executing tests in container: $pytest_cmd"
    
    if [ "$DRY_RUN" = false ]; then
        docker-compose -f .devcontainer/docker-compose_dev.yml exec python $pytest_cmd
        local test_exit_code=$?
    else
        log_info "DRY RUN: Would execute: $pytest_cmd"
        local test_exit_code=0
    fi
    
    # Clean up containers
    log_info "Stopping Docker containers..."
    docker-compose -f .devcontainer/docker-compose_dev.yml down
    
    return $test_exit_code
}

# Run tests in local environment
run_local_tests() {
    log_info "Running tests in local environment..."
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Run Django migrations
    log_info "Running database migrations..."
    if [ "$DRY_RUN" = false ]; then
        python "$SRC_DIR/manage.py" migrate --noinput
    else
        log_info "DRY RUN: Would run: python manage.py migrate --noinput"
    fi
    
    # Build and execute pytest command
    local pytest_cmd=$(build_pytest_command)
    log_info "Executing tests: $pytest_cmd"
    
    if [ "$DRY_RUN" = false ]; then
        $pytest_cmd
        return $?
    else
        log_info "DRY RUN: Would execute: $pytest_cmd"
        return 0
    fi
}

# Generate test report
generate_test_report() {
    local exit_code=$1
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local report_file="$LOG_DIR/test_report_$timestamp.txt"
    
    log_info "Generating test report..."
    
    cat > "$report_file" << EOF
Installation Wizard Test Report
Generated: $(date)
===============================

Test Configuration:
- Unit Only: $UNIT_ONLY
- Integration Only: $INTEGRATION_ONLY
- Fast Mode: $FAST_MODE
- Coverage Mode: $COVERAGE_MODE
- Parallel Mode: $PARALLEL_MODE
- Docker Mode: $DOCKER_MODE
- Exit Code: $exit_code

Environment:
- Django Settings: $DJANGO_SETTINGS_MODULE
- Python Path: $PYTHONPATH
- Test Database: $TEST_DATABASE_URL
- Coverage Threshold: $COVERAGE_THRESHOLD

Test Results:
EOF
    
    if [ $exit_code -eq 0 ]; then
        echo "- Status: PASSED" >> "$report_file"
        log_success "All tests passed!"
    else
        echo "- Status: FAILED" >> "$report_file"
        log_error "Some tests failed!"
    fi
    
    # Add coverage information if available
    if [ "$COVERAGE_MODE" = true ] && [ -f "$LOG_DIR/coverage.xml" ]; then
        echo "" >> "$report_file"
        echo "Coverage Report:" >> "$report_file"
        echo "- HTML Report: $LOG_DIR/htmlcov/index.html" >> "$report_file"
        echo "- XML Report: $LOG_DIR/coverage.xml" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "Log Files:" >> "$report_file"
    echo "- Test Report: $report_file" >> "$report_file"
    
    if [ "$QUIET_MODE" = false ]; then
        log_info "Test report saved to: $report_file"
        
        if [ "$COVERAGE_MODE" = true ] && [ -f "$LOG_DIR/htmlcov/index.html" ]; then
            log_info "Coverage report available at: $LOG_DIR/htmlcov/index.html"
        fi
    fi
}

# Main execution function
main() {
    log_info "Starting Installation Wizard Test Suite"
    log_info "Project Root: $PROJECT_ROOT"
    log_info "Test Directory: $TEST_DIR"
    
    # Show configuration in verbose mode
    if [ "$VERBOSE_MODE" = true ]; then
        log_info "Configuration:"
        log_info "  Unit Only: $UNIT_ONLY"
        log_info "  Integration Only: $INTEGRATION_ONLY"
        log_info "  Fast Mode: $FAST_MODE"
        log_info "  Coverage Mode: $COVERAGE_MODE"
        log_info "  Parallel Mode: $PARALLEL_MODE"
        log_info "  Docker Mode: $DOCKER_MODE"
        log_info "  Clean Mode: $CLEAN_MODE"
        log_info "  Dry Run: $DRY_RUN"
    fi
    
    # Setup environment
    setup_environment
    
    # Run tests
    local exit_code=0
    if [ "$DOCKER_MODE" = true ]; then
        run_docker_tests
        exit_code=$?
    else
        run_local_tests
        exit_code=$?
    fi
    
    # Generate report
    generate_test_report $exit_code
    
    # Exit with appropriate code
    if [ $exit_code -eq 0 ]; then
        log_success "Test suite completed successfully"
    else
        log_error "Test suite completed with failures"
    fi
    
    exit $exit_code
}

# Ensure we're in the right directory and run
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi