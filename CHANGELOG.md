# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-11-26

### Changed
- **Template UI/UX Improvements**: Enhanced all major templates with Bootstrap 5 icons and improved styling
  - Added Bootstrap Icons to headings, buttons, and navigation elements
  - Improved table styling with `table-hover` class and proper `scope` attributes
  - Enhanced filter inputs with consistent styling and ARIA labels
  - Fixed nested form issues by moving action buttons outside main forms
  - Added empty state messages for tables when no data is available
  - Updated index page to use Django URL template tags instead of hardcoded paths

### Fixed
- **Template Accessibility**: Added comprehensive accessibility improvements
  - Added `aria-label` attributes to filter inputs and buttons
  - Added keyboard navigation support with `onkeydown` handlers
  - Added `tabindex` and `role="link"` for clickable table rows
  - Added proper `scope="col"` to table headers
  
- **Form Structure**: Fixed HTML validation issues
  - Removed nested forms by separating action buttons from main forms
  - Improved button styling with consistent `w-100` class
  - Standardized confirmation modal usage across templates

- **Python Docstrings**: Normalized docstring quotes in `models.py`
  - Fixed escaped quote characters in Assistant model docstring

### Added
- **Workflow Documentation**: Added `commit-publish.prompt.md`
  - Comprehensive release pipeline workflow guide
  - Semantic versioning and changelog update instructions
  - Test execution and documentation requirements

## [0.3.0] - 2025-11-24

### Changed
- **Django Major Version Upgrade**: Django 4.2.17 → 5.1.4
  - ⚠️ **BREAKING CHANGE**: Django 5.1 requires Python 3.10 or higher
  - Updated to latest Django stable release with new features and improvements
  - Removed support for Python 3.9 (now requires Python 3.10+)
  - Django 5.1 includes performance improvements and modern async support
  - See [Django 5.1 release notes](https://docs.djangoproject.com/en/5.1/releases/5.1/) for details

- **Python Version Requirement**: Increased minimum from Python 3.11 to Python 3.10
  - Supports Python 3.10, 3.11, and 3.12
  - Maintains compatibility with Django 5.1 requirements
  - Production container remains on Python 3.11

- **Dependency Management**: Upgraded all dependencies to latest stable versions with explicit version pinning
  - **Django**: 4.2.20 → 4.2.17 → 5.1.4 (Major version upgrade)
  - **djangorestframework**: Unpinned → 3.15.2
  - **django-environ**: Unpinned → 0.11.2
  - **django-allauth**: Unpinned → 65.3.0 (with MFA, SAML, socialaccount, steam extras)
  - **django-import-export**: Unpinned → 4.3.3
  - **django-json-widget**: Unpinned → 2.0.1
  - **django-markdownify**: Unpinned → 0.9.5
  - **django-filer**: Unpinned → 3.2.0
  - **django-ses**: Unpinned → 4.2.0
  - **psycopg2-binary**: Unpinned → 2.9.10
  - **openai**: Unpinned → 1.57.2
  - **boto3**: Unpinned → 1.35.75
  - **pygithub**: Unpinned → 2.5.0
  - **azure-monitor-opentelemetry**: Unpinned → 1.6.4
  - **Markdown**: 3.7 → 3.5.2 (compatibility with martor 1.6.44)
  - **PyYAML**: Unpinned → 6.0.2
  - **jsonschema**: Unpinned → 4.23.0
  - **martor**: Unpinned → 1.6.44
  
- **Development Dependencies**: Upgraded all development tools to latest versions
  - **pytest**: Unpinned → 8.3.4
  - **pytest-django**: Unpinned → 4.9.0
  - **pytest-playwright**: Unpinned → 0.6.2
  - **pytest-cov**: Unpinned → 6.0.0
  - **coverage**: Unpinned → 7.6.9
  - **selenium**: Unpinned → 4.27.1
  - **ruff**: Unpinned → 0.8.2
  - **black**: Added → 24.10.0 (code formatter)
  - **mypy**: Added → 1.13.0 (type checker)
  - **django-stubs**: Added → 5.1.1 (Django type stubs)
  - **sphinx**: Unpinned → 8.1.3
  - **sphinx-rtd-theme**: Unpinned → 3.0.2
  - **django-debug-toolbar**: Added → 4.4.6
  - **django-extensions**: Added → 3.2.3

- **Python Version**: Updated minimum requirement from >=3.9 to >=3.11
  - Ensures compatibility with all upgraded dependencies
  - Maintains production Python 3.11 baseline
  - Supports Python 3.11 and 3.12

- **Project Version**: Bumped from 0.2.0 to 0.3.0 to reflect dependency upgrades

### Added
- **requirements-base.txt**: New file with core production dependencies and explicit versions
- **Version Constraints**: Added semantic versioning constraints in pyproject.toml
  - Django pinned to 4.2.x LTS series (>=4.2.17,<5.0)
  - All packages now have explicit version ranges for reproducibility
  - Separate optional dependency groups: dev, security, monitoring, cms

### Fixed
- **Docker Configuration**: Updated docker-compose.yml to use proper Dockerfile build
  - Ensures gcc and build tools are available for packages requiring compilation
  - Fixes pycairo build issues for SVG support in easy-thumbnails
  - Proper multi-stage builds with caching

- **Dependency Conflicts**: Resolved Markdown version conflict
  - martor 1.6.44 requires Markdown<3.6
  - Fixed by downgrading Markdown from 3.7 to 3.5.2

### Security
- **Version Pinning**: All dependencies now have explicit versions
  - Enables security scanning and vulnerability tracking
  - Prevents unexpected breaking changes from automatic upgrades
  - Maintains reproducible builds across environments

## [0.2.0] - 2025-01-27

### Added
- **Azure Container Apps**: Successful deployment to Azure Container Apps (West US 2) with auto-scaling
  - Live application at assigned Azure URL with full database connectivity
  - Auto-scaling container orchestration with 0-3 replica configuration
  - Comprehensive monitoring via Application Insights integration
- **Cost-Optimized Infrastructure**: Added minimal cost Bicep templates in `infra/minimal/`
  - Burstable PostgreSQL tier (B1ms) for ~$12/month database costs
  - Basic App Service alternatives for quota-constrained subscriptions
  - Complete infrastructure-as-code templates with security best practices
- **Health Checks**: Added Django health check endpoints for container monitoring
  - Database connectivity validation
  - Application performance monitoring
  - Container Apps health probe integration
- **Bootstrap 5 UI**: Implemented pure Django templates with Bootstrap 5.3.3
  - Responsive navigation with Bootstrap components
  - Modern card-based layouts and Bootstrap icons
  - Mobile-optimized interface replacing CMS frontend
- **Comprehensive Documentation**: Added detailed guides and reports
  - Migration documentation with rollback procedures
  - Infrastructure evolution and cost analysis
  - Deployment validation and troubleshooting guides

### Changed
- **CMS Architecture**: Temporarily disabled Django CMS for deployment simplification
  - Commented out 36+ CMS-related Django apps for preservation
  - Replaced CMS placeholders with standard Django template inheritance
  - Maintained database schema while disabling CMS models and middleware
  - Preserved restoration path through systematic code commenting
- **Infrastructure Evolution**: Migrated from Azure App Service to Container Apps
  - Resolved Azure subscription quota limitations (zero VM quota)
  - Achieved successful deployment through alternative compute services
  - Maintained PostgreSQL Flexible Server with optimized configuration
  - Standardized resource naming and environment management
- **Port Standardization**: Unified application port to 8000 across all environments
  - Updated Bicep infrastructure templates for consistent port configuration
  - Modified Docker and Django settings for port alignment
  - Ensured end-to-end connectivity from ingress to application
- **Docker Optimization**: Enhanced containerization for production deployment
  - Multi-stage builds for reduced image size
  - Non-root user implementation for security
  - Health checks for container orchestration
  - Gunicorn production server configuration

### Fixed
- **GitHub Actions Workflows**: Comprehensive workflow modernization (2025-10-31)
  - Updated 15+ Docker Compose commands to modern syntax
  - Resolved Linux compatibility issues in Azure Dev workflow
  - Added timeout protection to 30+ workflow jobs
  - Enhanced security with pinned tool versions and secret scanning
  - Fixed CI path references and environment variable scoping
- **Azure Deployment**: Resolved quota and configuration issues
  - Identified and worked around Azure subscription quota limitations
  - Fixed port mismatches between infrastructure and application
  - Implemented successful Container Apps deployment strategy
  - Optimized resource allocation for cost and performance

### Removed
- **CMS Dependencies**: Temporarily removed to resolve deployment complexity
  - Frontend editing capabilities and CMS toolbar
  - Plugin system and placeholder-based content management
  - Multi-language support and CMS page hierarchy
  - Advanced menu generation and SEO management features

### Security
- **Container Security**: Enhanced security posture in containerized deployment
  - Non-root user execution in production containers
  - Azure Key Vault integration for secrets management
  - Managed identity authentication for service-to-service communication
  - PostgreSQL VNet integration and firewall configuration

### Performance
- **Infrastructure Optimization**: Improved performance and cost efficiency
  - Container Apps serverless scaling reduces idle resource costs
  - Optimized database configuration for burstable performance tiers
  - Enhanced caching and static file serving through CDN-ready setup
  - Monitoring and alerting for proactive performance management

## Migration Notes

### Database Migration
- **Zero Data Loss**: All existing content preserved during CMS removal
- **Schema Preservation**: CMS tables remain in database but unused
- **Rollback Ready**: Complete restoration path documented for future CMS re-enablement

### Infrastructure Migration
- **Cost Reduction**: Monthly infrastructure costs reduced from ~$50 to ~$25-35
- **Improved Scalability**: Container Apps auto-scaling vs. fixed App Service capacity
- **Enhanced Monitoring**: Application Insights with custom dashboards and alerting

### Development Workflow
- **Simplified Stack**: Reduced complexity enables faster development cycles
- **Container-First**: All development now occurs in Docker containers
- **Documentation-Driven**: Comprehensive guides for all operational procedures

## [0.1.0] - 2025-01-15

### Added
- Initial Django application with CMS integration
- PostgreSQL database configuration
- Basic parody news generation functionality
- Docker containerization setup
- Azure infrastructure templates

### Infrastructure
- Django CMS with full plugin ecosystem
- Azure App Service deployment configuration
- PostgreSQL Flexible Server setup
- Basic monitoring and logging

---

**Documentation References:**
- [Migration Guide](./docs/migration/v0.2.0-guide.md) - Complete migration procedures
- [Infrastructure Changes](./docs/infrastructure/v0.2.0-changes.md) - Detailed infrastructure evolution
- [Deployment Guide](./docs/deployment/minimal-guide.md) - Step-by-step deployment instructions
- [CMS Removal](./docs/migration/cms-removal.md) - CMS removal and restoration procedures
- [Troubleshooting](./docs/troubleshooting/azure-quota.md) - Common issues and solutions