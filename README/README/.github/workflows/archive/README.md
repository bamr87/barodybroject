# Archived Workflows

This directory contains workflow files that have been superseded by the foundational CI/CD pipeline.

## Archived on: 2025-01-27

### tests.yml
**Reason**: Superseded by `ci.yml`
- **Original Purpose**: Cross-platform Python testing (Ubuntu, macOS, Windows) with multiple Python versions
- **Why Archived**: `ci.yml` now provides comprehensive testing with docker-compose approach, eliminating the need for complex matrix testing across different OS/Python combinations
- **Coverage**: The container-based approach in `ci.yml` ensures consistent environment testing

### format.yml  
**Reason**: Superseded by `quality.yml`
- **Original Purpose**: Python linting and formatting with ruff
- **Why Archived**: `quality.yml` now includes comprehensive code quality checks including formatting, linting, and security scanning
- **Coverage**: All formatting and linting functionality is now handled in the unified quality workflow

## Foundational Pipeline

The current foundational pipeline consists of:
1. **ci.yml** - Main CI pipeline with testing and validation
2. **quality.yml** - Code quality, formatting, linting, and security
3. **container.yml** - Docker-compose validation and container orchestration  
4. **deploy.yml** - Azure deployment and infrastructure management
5. **environment.yml** - Environment management and configuration

## Docker-Compose Only Approach

All archived workflows used custom Dockerfiles or complex environment setups. The foundational pipeline uses docker-compose exclusively for:
- Consistent development/CI environments
- Simplified container orchestration
- Reduced maintenance overhead
- Better integration with local development workflows

## Recovery Instructions

If any archived workflow needs to be restored:
1. Copy the file back to `.github/workflows/`
2. Update triggers to avoid conflicts with foundational pipeline
3. Verify compatibility with docker-compose approach
4. Update documentation accordingly