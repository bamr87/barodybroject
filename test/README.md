# Test Suite for Installation Wizard

This directory contains comprehensive tests for the Barodybroject installation wizard feature. The test suite covers all aspects of the installation wizard functionality, including unit tests, integration tests, and end-to-end testing scenarios.

## Test Structure

```
test/
├── README.md                           # This file
├── unit/                              # Unit tests for individual components
│   ├── test_services.py              # InstallationService tests
│   ├── test_views.py                 # Django views tests
│   ├── test_forms.py                 # Form validation tests
│   ├── test_middleware.py            # Middleware tests
│   └── test_management_commands.py   # Management command tests
├── integration/                       # Integration tests
│   ├── test_wizard_flow.py           # Complete wizard flow tests
│   ├── test_headless_mode.py         # Headless installation tests
│   ├── test_token_authentication.py  # Token system tests
│   └── test_docker_integration.py    # Docker container tests
├── e2e/                              # End-to-end tests
│   ├── test_interactive_setup.py     # Full interactive setup
│   ├── test_production_deployment.py # Production deployment tests
│   └── test_ui_components.py         # Web interface tests
├── fixtures/                         # Test data and configurations
│   ├── test_config.json             # Test configuration files
│   ├── docker-compose.test.yml      # Test Docker configuration
│   └── sample_data.py               # Test data generators
├── scripts/                          # Test automation scripts
│   ├── run_all_tests.sh             # Run complete test suite
│   ├── test_interactive_mode.sh     # Test interactive wizard
│   ├── test_headless_mode.sh        # Test headless installation
│   ├── test_docker_setup.sh         # Test Docker integration
│   └── cleanup_test_env.sh          # Clean up test environment
└── performance/                      # Performance and load tests
    ├── test_wizard_performance.py    # Performance benchmarks
    └── load_test_setup.py           # Load testing scenarios
```

## Quick Start

### Run All Tests
```bash
# Run complete test suite
./test/scripts/run_all_tests.sh

# Run specific test categories
pytest test/unit/                    # Unit tests only
pytest test/integration/             # Integration tests only
pytest test/e2e/                     # End-to-end tests only
```

### Test Individual Components
```bash
# Test installation service
pytest test/unit/test_services.py -v

# Test web interface
pytest test/e2e/test_ui_components.py -v

# Test Docker integration
pytest test/integration/test_docker_integration.py -v
```

### Manual Testing Scripts
```bash
# Test interactive mode
./test/scripts/test_interactive_mode.sh

# Test headless mode  
./test/scripts/test_headless_mode.sh

# Test Docker setup
./test/scripts/test_docker_setup.sh
```

## Test Categories

### 🔧 Unit Tests
- **InstallationService**: Token generation, validation, state management
- **Django Views**: Request handling, authentication, responses
- **Forms**: Input validation, error handling, security
- **Middleware**: Redirection logic, URL exemptions
- **Management Commands**: CLI functionality, argument parsing

### 🔗 Integration Tests
- **Complete Wizard Flow**: Interactive setup from start to finish
- **Headless Mode**: Token generation and web-based completion
- **Token Authentication**: Security validation and expiration
- **Docker Integration**: Container startup and configuration

### 🌐 End-to-End Tests
- **Interactive Setup**: Full CLI wizard experience
- **Production Deployment**: Real-world deployment scenarios
- **Web Interface**: UI functionality and user experience

### ⚡ Performance Tests
- **Wizard Performance**: Response times and resource usage
- **Load Testing**: Multiple concurrent setup sessions
- **Database Performance**: Query optimization and scaling

## Test Environment Setup

### Prerequisites
```bash
# Install test dependencies
pip install pytest pytest-django pytest-cov selenium requests

# Install Docker for container tests
# Docker Desktop or Docker Engine required
```

### Environment Configuration
```bash
# Copy test environment template
cp test/fixtures/test_config.json.example test/fixtures/test_config.json

# Set test environment variables
export DJANGO_SETTINGS_MODULE=barodybroject.settings
export TESTING=true
export DATABASE_URL=sqlite:///test_db.sqlite3
```

### Database Setup
```bash
# Create test database
python manage.py migrate --settings=barodybroject.test_settings

# Load test fixtures
python manage.py loaddata test/fixtures/test_data.json
```

## Test Scenarios

### 🎯 Core Functionality Tests
1. **Installation State Management**
   - Test installation completion detection
   - Verify state persistence across restarts
   - Validate configuration file handling

2. **Token Security System**
   - Generate and validate secure tokens
   - Test token expiration handling
   - Verify single-use token behavior

3. **Admin User Creation**
   - Test interactive admin creation
   - Validate password requirements
   - Verify user permissions setup

### 🌐 Web Interface Tests
1. **Setup Wizard Pages**
   - Test all wizard page rendering
   - Verify navigation and progress tracking
   - Validate responsive design behavior

2. **Form Validation**
   - Test input validation and error messages
   - Verify CSRF protection
   - Test JavaScript form enhancements

3. **Token Authentication**
   - Test token-based access control
   - Verify unauthorized access prevention
   - Test token expiration handling

### 🐳 Docker Integration Tests
1. **Container Startup**
   - Test development container setup
   - Verify production container configuration
   - Test volume persistence

2. **Environment Variables**
   - Test configuration via environment
   - Verify default value handling
   - Test production vs development modes

3. **Service Integration**
   - Test database connectivity
   - Verify Django application startup
   - Test inter-service communication

### 🔄 Workflow Tests
1. **Interactive Mode**
   - Complete setup wizard from CLI
   - Test all user input scenarios
   - Verify error handling and recovery

2. **Headless Mode**
   - Generate setup tokens
   - Complete web-based admin creation
   - Test automated deployment scenarios

3. **Mixed Mode Scenarios**
   - Start in headless, complete interactively
   - Test multiple setup attempts
   - Verify state consistency

## Continuous Integration

### GitHub Actions Integration
```yaml
# .github/workflows/test-installation-wizard.yml
name: Installation Wizard Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Installation Wizard Tests
        run: ./test/scripts/run_all_tests.sh
```

### Test Coverage Requirements
- **Unit Tests**: Minimum 90% code coverage
- **Integration Tests**: All critical paths tested
- **E2E Tests**: Complete user workflows validated
- **Performance Tests**: Response time benchmarks met

## Test Data Management

### Test Fixtures
- **User Data**: Sample admin and regular users
- **Configuration Data**: Various setup scenarios
- **Token Data**: Valid and expired tokens for testing

### Data Generation
```python
# Generate test data
python test/fixtures/sample_data.py --users 10 --tokens 5

# Reset test environment
python test/scripts/reset_test_data.py
```

### Database Isolation
- Each test uses isolated database transactions
- Test data is automatically cleaned up
- No test pollution between runs

## Debugging and Troubleshooting

### Test Debugging
```bash
# Run tests with verbose output
pytest test/ -v -s

# Run specific test with debugging
pytest test/unit/test_services.py::TestInstallationService::test_token_generation -v -s

# Run tests with coverage report
pytest test/ --cov=setup --cov-report=html
```

### Log Analysis
```bash
# View test logs
tail -f test/logs/test_run.log

# Analyze test failures
python test/scripts/analyze_failures.py
```

### Common Issues
1. **Database Connection**: Ensure test database is accessible
2. **Docker Services**: Verify Docker containers are running
3. **Environment Variables**: Check test configuration settings
4. **Port Conflicts**: Ensure test ports are available

## Performance Benchmarks

### Expected Performance Metrics
- **Token Generation**: < 100ms
- **Admin User Creation**: < 500ms
- **Page Load Times**: < 2 seconds
- **Database Queries**: < 10 queries per request

### Load Testing
```bash
# Run performance tests
python test/performance/test_wizard_performance.py

# Load test with multiple users
python test/performance/load_test_setup.py --users 50
```

## Contributing to Tests

### Adding New Tests
1. Follow pytest conventions
2. Use descriptive test names
3. Include docstrings explaining test purpose
4. Add to appropriate test category

### Test Guidelines
- **Arrange-Act-Assert**: Structure tests clearly
- **Isolation**: Each test should be independent
- **Repeatability**: Tests should produce consistent results
- **Documentation**: Explain complex test scenarios

### Code Coverage
- Maintain high test coverage (>90%)
- Test both success and failure paths
- Include edge cases and error conditions
- Document any uncovered code paths

---

**Quick Commands:**
```bash
# Run all tests
./test/scripts/run_all_tests.sh

# Test specific feature
pytest test/unit/test_services.py -k "test_token"

# Generate coverage report
pytest test/ --cov=setup --cov-report=term-missing
```