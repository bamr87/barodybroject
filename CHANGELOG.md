# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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