# TODO: Project Issues and Enhancements

This document tracks issues, missing functionality, and enhancements needed for the Barody Project to comply with best practices and improve overall quality. It also includes Azure deployment next steps and infrastructure guidance.

**Version**: 0.1.0  
**Last Updated**: October 26, 2025

## Table of Contents

- [Azure Deployment Next Steps](#azure-deployment-next-steps)
- [Configuration & Setup Issues](#configuration--setup-issues)
- [CI/CD & Automation](#cicd--automation)
- [Documentation Gaps](#documentation-gaps)
- [Code Quality & Testing](#code-quality--testing)
- [Security & Best Practices](#security--best-practices)
- [Infrastructure & Deployment](#infrastructure--deployment)
- [Project Organization](#project-organization)
- [Feature Enhancements](#feature-enhancements)

---

## Azure Deployment Next Steps

This section contains immediate next steps for Azure deployment using Azure Developer CLI (azd).

### 🚀 Immediate Azure Deployment Actions

- [ ] **Provision infrastructure and deploy application**
  - **Action**: Run `azd up` to provision infrastructure and deploy to Azure
  - **Alternative**: Run `azd provision` then `azd deploy` separately
  - **Verify**: Visit service endpoints to confirm deployment
  - **Troubleshooting**: See [Azure troubleshooting](#azure-troubleshooting) section below

- [ ] **Configure environment variables for running services**
  - **Action**: Update `settings` in [main.parameters.json](./infra/main.parameters.json)
  - **Database**: Configure `POSTGRES_*` environment variables in [src.bicep](./infra/app/src.bicep)
  - **Customize**: Modify variables to match application needs

- [ ] **Setup CI/CD pipeline for Azure**
  - **Step 1**: Create workflow pipeline file locally using starters:
    - [GitHub Actions starter](https://github.com/Azure-Samples/azd-starter-bicep/blob/main/.github/workflows/azure-dev.yml)
    - [Azure Pipelines starter](https://github.com/Azure-Samples/azd-starter-bicep/blob/main/.azdo/pipelines/azure-dev.yml)
  - **Step 2**: Run `azd pipeline config` to configure secure Azure connection
  - **Priority**: High - needed for automated deployments

### 🏗️ Azure Infrastructure Overview

The following infrastructure was added by `azd init`:

**Core Files:**
- `azure.yaml` - azd project configuration
- `infra/` - Infrastructure as Code (Bicep) files
  - `main.bicep` - main deployment module
  - `app/` - Application resource modules
  - `shared/` - Shared resource modules
  - `modules/` - Library modules

**Azure Resources:**
- [app/src.bicep](./infra/app/src.bicep) - Azure Container Apps for 'src' service
- [app/db-postgre.bicep](./infra/app/db-postgre.bicep) - PostgreSQL Flexible Server for 'barodydb'
- [shared/keyvault.bicep](./infra/shared/keyvault.bicep) - Azure KeyVault for secrets
- [shared/monitoring.bicep](./infra/shared/monitoring.bicep) - Log Analytics and Application Insights
- [shared/registry.bicep](./infra/shared/registry.bicep) - Container Registry for Docker images

### 🐳 Container Build Configuration

**Build with Buildpacks using Oryx** (if no Dockerfile present):
- Uses [Buildpacks](https://buildpacks.io/) with [Oryx](https://github.com/microsoft/Oryx/blob/main/doc/README.md)
- Local testing:
  1. Run `azd package` to build image
  2. Copy the Image Tag shown
  3. Run `docker run -it <Image Tag>` to test locally

**Port Configuration:**
- Oryx sets `PORT` to default `80` (`8080` for Java)
- Auto-configures web servers (gunicorn, ASP.NET Core)
- If app uses different port: Update `targetPort` in `.bicep` files under `infra/app/`

### 💰 Cost Management

- [ ] **Setup cost monitoring**
  - **Action**: Visit *Cost Management + Billing* in Azure Portal
  - **Monitor**: Track current spend and set up alerts
  - **Reference**: [Azure billing overview](https://learn.microsoft.com/azure/developer/intro/azure-developer-billing)

### 🔧 Azure Troubleshooting

**Common Issue: Blank page, welcome page, or error page**

**Diagnostic Steps:**
1. Run `azd show` and click "View in Azure Portal"
2. Navigate to failing Container App service
3. Click failing revision under "Revisions with Issues"
4. Review "Status details" for failure information
5. Check Console log stream and System log stream for errors
6. Use *Console* navigation to connect to shell in running container

**Additional Resources:**
- [Container Apps troubleshooting](https://learn.microsoft.com/azure/container-apps/troubleshooting)
- [Azure Developer CLI docs](https://learn.microsoft.com/azure/developer/azure-developer-cli/make-azd-compatible?pivots=azd-convert)

---

## Configuration & Setup Issues

### 🔴 Critical

- [ ] **License Inconsistency** - `pyproject.toml` specifies GPL-3.0-or-later but `LICENSE` file contains MIT License. Need to choose one and update accordingly.
  - **Impact**: Legal ambiguity for contributors and users
  - **Recommendation**: Stick with MIT (more permissive) and update pyproject.toml
  - **Files**: `LICENSE`, `pyproject.toml`

- [ ] **Missing .env.example File** - No template file for environment variables
  - **Impact**: New developers don't know what environment variables are needed
  - **Action**: Create `.env.example` with all required variables (with dummy values)
  - **Should include**: All variables from setup instructions in README

### 🟡 Medium Priority

- [ ] **Duplicate Dependency Management** - Dependencies defined in both `requirements.txt` and `pyproject.toml`
  - **Impact**: Potential version conflicts, maintenance overhead
  - **Recommendation**: Migrate fully to pyproject.toml with optional groups
  - **Files**: `src/requirements.txt`, `requirements-dev.txt`, `pyproject.toml`

- [ ] **Virtual Environment Not in .gitignore** - `.venv*` is ignored but specific venv patterns may leak
  - **Impact**: Could accidentally commit large virtual environment directories
  - **Action**: Review and ensure all common venv patterns are covered
  - **File**: `.gitignore`

- [ ] **Production vs Development Settings** - Single settings.py file without clear environment separation
  - **Impact**: Risk of running with DEBUG=True in production
  - **Recommendation**: Split into `settings/base.py`, `settings/development.py`, `settings/production.py`
  - **File**: `src/barodybroject/settings.py`

### 🟢 Low Priority

- [ ] **Database Migration Files Ignored** - `.gitignore` excludes migration files (`src/parodynews/migrations/0*`)
  - **Impact**: Migration history lost, potential schema inconsistencies
  - **Recommendation**: Track migration files in version control
  - **File**: `.gitignore` line 188

---

## CI/CD & Automation

### 🔴 Critical

- [ ] **Setup Azure CI/CD Pipeline** - No automated deployment to Azure configured
  - **Impact**: Manual deployments to Azure, higher error risk
  - **Action**: Configure Azure deployment pipeline:
    - Use GitHub Actions starter: [azure-dev.yml](https://github.com/Azure-Samples/azd-starter-bicep/blob/main/.github/workflows/azure-dev.yml)
    - Run `azd pipeline config` for secure Azure connection
    - Test deployment workflow
  - **Priority**: Critical for production deployments

- [ ] **Missing GitHub Actions Workflows** - No `.github/workflows/` directory found
  - **Impact**: No automated testing, linting, or deployment
  - **Action**: Create workflows for:
    - Pull request validation (linting, testing)
    - Azure deployment workflow (using azd)
    - Dependency vulnerability scanning
    - Docker image building and publishing

- [ ] **No Pre-commit Hooks** - No `.pre-commit-config.yaml` found
  - **Impact**: Code quality issues and style violations committed
  - **Action**: Add pre-commit hooks for:
    - Ruff (linting)
    - Black (formatting)
    - isort (import sorting)
    - Check for secrets
    - Trailing whitespace removal

### 🟡 Medium Priority

- [ ] **No Automated Testing Pipeline** - Tests exist but no CI to run them
  - **Impact**: Breaking changes can be merged
  - **Action**: Add GitHub Actions workflow to run pytest on every PR
  - **Should include**: Coverage reports, test result annotations
  - **Integration**: Should run before Azure deployment

- [ ] **Azure Environment Configuration** - No environment-specific deployments
  - **Impact**: Cannot deploy to staging/production separately
  - **Action**: Setup multiple Azure environments:
    - Staging environment for testing
    - Production environment
    - Environment-specific parameters
    - Approval workflows for production

- [ ] **No Dependabot Configuration** - No automated dependency updates
  - **Impact**: Outdated dependencies, security vulnerabilities
  - **Action**: Add `.github/dependabot.yml` for:
    - pip dependencies
    - Docker dependencies
    - GitHub Actions
    - Bicep modules (if applicable)

- [ ] **Missing Azure Infrastructure Validation** - Bicep files not validated in CI
  - **Impact**: Infrastructure deployment failures
  - **Action**: Add Bicep validation to CI:
    - Bicep linting with `az bicep build`
    - Infrastructure testing with `azd provision --dry-run`
    - Template security scanning

### 🟢 Low Priority

- [ ] **No Release Automation** - Manual version bumping and changelog updates
  - **Impact**: Inconsistent release process
  - **Action**: Add semantic-release or similar tool
  - **Related**: `VERSION` file exists but no automation around it
  - **Integration**: Coordinate with Azure deployments

- [ ] **No Container Image Scanning** - Docker images not scanned for vulnerabilities
  - **Impact**: Security vulnerabilities in production
  - **Action**: Add container scanning:
    - Trivy or Snyk scanning in CI
    - Azure Container Registry vulnerability scanning
    - Block deployment of vulnerable images

---

## Documentation Gaps

### 🔴 Critical

- [ ] **Missing SECURITY.md** - No security vulnerability reporting guidelines
  - **Impact**: Security issues reported publicly or not at all
  - **Action**: Create `SECURITY.md` with:
    - Supported versions
    - Vulnerability reporting process
    - Security update policy
  - **Template**: Use GitHub's security policy template

### 🟡 Medium Priority

- [ ] **Missing CODE_OF_CONDUCT.md** - Referenced in CONTRIBUTING.md but doesn't exist
  - **Impact**: Broken link, unclear community standards
  - **Action**: Add `CODE_OF_CONDUCT.md` (use Contributor Covenant)
  - **File**: `CONTRIBUTING.md` line 141

- [ ] **Missing CHANGELOG.md** - No change history tracking
  - **Impact**: Users don't know what changed between versions
  - **Action**: Create `CHANGELOG.md` following Keep a Changelog format
  - **Should track**: Breaking changes, new features, bug fixes

- [ ] **No API Documentation** - REST API exists but no documentation
  - **Impact**: API consumers don't know available endpoints
  - **Action**: Add Swagger/OpenAPI documentation using drf-spectacular
  - **Alternative**: Use Django REST Framework's built-in documentation

- [ ] **Missing Database Schema Documentation** - No ER diagrams or model documentation
  - **Impact**: Hard to understand data relationships
  - **Action**: Generate with django-extensions graph_models or document manually
  - **Tools**: graphviz, django-extensions

- [ ] **No Architecture Diagrams** - Text description only in README
  - **Impact**: Harder to understand system architecture
  - **Action**: Create diagrams for:
    - System architecture
    - Deployment architecture
    - Data flow
  - **Tools**: draw.io, mermaid, PlantUML

### 🟢 Low Priority

- [ ] **Too Many Scattered README Files** - 133 README.md files throughout the project
  - **Impact**: Outdated or duplicate information, maintenance burden
  - **Action**: Consolidate or remove unnecessary READMEs
  - **Keep**: Main README, infra/README, src/parodynews/README
  - **Consider**: Single docs/ directory with organized documentation

- [ ] **Missing Development Guide** - No detailed guide for setting up development environment
  - **Impact**: Harder for new contributors to get started
  - **Action**: Create `docs/DEVELOPMENT.md` with:
    - IDE setup recommendations
    - Debugging tips
    - Common issues and solutions
    - Development workflow

- [ ] **No Deployment Runbook** - Deployment steps scattered
  - **Impact**: Deployment inconsistencies, knowledge loss
  - **Action**: Create `docs/DEPLOYMENT.md` with detailed procedures

---

## Code Quality & Testing

### 🔴 Critical

- [ ] **Test Code in Production** - `src/parodynews/foobar/` directory appears to be test code
  - **Impact**: Unnecessary code in production, potential security risk
  - **Action**: Review and remove foobar directory or move to tests
  - **Location**: `src/parodynews/foobar/`

### 🟡 Medium Priority

- [ ] **Missing Test Coverage Reporting** - pytest-cov installed but no coverage requirements
  - **Impact**: Unknown code coverage, potential untested code paths
  - **Action**: 
    - Set minimum coverage threshold (e.g., 80%)
    - Add coverage badge to README
    - Enforce in CI pipeline

- [ ] **Ruff Configured But Not Enforced** - Linter configured in pyproject.toml but no automation
  - **Impact**: Code style inconsistencies
  - **Action**: 
    - Add ruff to pre-commit hooks
    - Add ruff check to CI pipeline
    - Run `ruff check --fix` on codebase

- [ ] **No Code Formatting Tool Enforced** - Black configured but not enforced
  - **Impact**: Inconsistent code style across files
  - **Action**: 
    - Add Black to pre-commit hooks
    - Run Black on entire codebase
    - Enforce in CI

- [ ] **Missing Integration Tests Documentation** - Tests exist but no guide on running/writing them
  - **Impact**: Contributors don't know testing expectations
  - **Action**: Add testing guide to CONTRIBUTING.md or separate doc

### 🟢 Low Priority

- [ ] **No Performance Testing** - No load testing or performance benchmarks
  - **Impact**: Unknown performance characteristics
  - **Action**: Add locust or similar for load testing
  - **Document**: Performance baselines and requirements

- [ ] **No Accessibility Testing** - axe-playwright-python installed but unclear usage
  - **Impact**: Potential accessibility issues
  - **Action**: Document accessibility testing procedures
  - **Add**: Accessibility test examples

---

## Security & Best Practices

### 🔴 Critical

- [ ] **No Security Scanning in CI/CD** - No automated security checks
  - **Impact**: Vulnerabilities may go undetected
  - **Action**: Add to CI pipeline:
    - Bandit (Python security linter)
    - Safety (dependency vulnerability scanner)
    - Trivy or Snyk (container scanning)

- [ ] **Secrets in Environment Variables** - SECRET_KEY and API keys in .env
  - **Impact**: Risk of secrets in version control if .env committed
  - **Action**: 
    - Add .env to .gitignore (already done, but verify)
    - Document using Azure Key Vault for production
    - Add pre-commit hook to check for secrets

- [ ] **Missing Rate Limiting** - No rate limiting on API endpoints
  - **Impact**: API abuse, DDoS vulnerability
  - **Action**: Implement django-ratelimit or throttling in DRF

### 🟡 Medium Priority

- [ ] **No Dependency Vulnerability Scanning** - Dependencies not regularly scanned
  - **Impact**: Known vulnerabilities in dependencies
  - **Action**: 
    - Add GitHub Dependabot security alerts
    - Add pip-audit to CI pipeline
    - Regular manual audits

- [ ] **Django DEBUG=True in Examples** - Setup instructions use DEBUG=True
  - **Impact**: Debug mode might accidentally run in production
  - **Action**: 
    - Emphasize DEBUG=False for production
    - Add check in settings.py to prevent DEBUG in production
    - Document proper production settings

- [ ] **Missing CORS Configuration Documentation** - No CORS settings documented
  - **Impact**: API may not work with frontend apps
  - **Action**: Document django-cors-headers configuration if needed

### 🟢 Low Priority

- [ ] **No Security Headers Documentation** - Missing CSP, HSTS, etc. documentation
  - **Impact**: Potential security vulnerabilities
  - **Action**: Document required security headers for production
  - **Tool**: django-csp or django-security

- [ ] **No Input Validation Documentation** - Form validation exists but not documented
  - **Impact**: Developers may not follow validation best practices
  - **Action**: Document validation patterns and examples

---

## Infrastructure & Deployment

### 🔴 Critical

- [ ] **Complete Azure Deployment Setup** - Infrastructure provisioned but not fully configured
  - **Impact**: Application not running in production environment
  - **Action**: Complete Azure deployment next steps:
    - Run `azd up` to provision and deploy
    - Configure environment variables in `main.parameters.json`
    - Setup CI/CD pipeline with `azd pipeline config`
  - **Reference**: See [Azure Deployment Next Steps](#azure-deployment-next-steps) section

- [ ] **No Production Configuration Documented** - README focuses on development
  - **Impact**: Unclear how to configure for production
  - **Action**: Document production settings:
    - Required environment variables
    - Scaling considerations
    - Performance tuning
    - Database connection pooling

- [ ] **Configure PostgreSQL Connection Variables** - Database variables need proper configuration
  - **Impact**: Application cannot connect to Azure PostgreSQL
  - **Action**: Update `POSTGRES_*` environment variables in [src.bicep](./infra/app/src.bicep)
  - **Variables needed**: POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  - **Reference**: Azure Flexible Server connection strings

### 🟡 Medium Priority

- [ ] **Docker Image Not Optimized** - No multi-stage build apparent
  - **Impact**: Larger image sizes, slower deployments
  - **Action**: Review Dockerfile and optimize:
    - Multi-stage build
    - Layer caching optimization
    - Remove unnecessary dependencies
  - **File**: `src/Dockerfile`
  - **Note**: Consider using Oryx buildpacks for optimized builds

- [ ] **No Health Check Endpoints** - No documented health/readiness endpoints
  - **Impact**: Container orchestration may not work properly
  - **Action**: Add health check endpoints:
    - `/health` - basic health check
    - `/ready` - readiness check (DB connectivity, etc.)
  - **Document**: In deployment section
  - **Azure**: Configure in Container Apps health probes

- [ ] **Missing Monitoring Setup Documentation** - Azure Application Insights mentioned but not configured
  - **Impact**: No production monitoring
  - **Action**: Document and configure:
    - Application Insights setup (already in infra/shared/monitoring.bicep)
    - Log aggregation configuration
    - Alert configuration
    - Dashboard setup
    - Custom metrics and traces

- [ ] **No Backup and Recovery Procedures** - Database backups not documented
  - **Impact**: Data loss risk
  - **Action**: Document:
    - Azure PostgreSQL Flexible Server backup procedures
    - Point-in-time restore procedures
    - Backup retention policy
    - Disaster recovery plan

- [ ] **Azure Port Configuration** - Application port may not match Azure expectations
  - **Impact**: Application may not be accessible
  - **Action**: Verify port configuration:
    - Check if app listens to `PORT` environment variable
    - Update `targetPort` in bicep files if needed
    - Test with `azd package` and local Docker run

### 🟢 Low Priority

- [ ] **No CDN Configuration** - Static files served from app
  - **Impact**: Slower static file delivery
  - **Action**: Document Azure CDN or Blob Storage setup for static files
  - **Azure**: Use Azure CDN with Container Apps

- [ ] **No Caching Strategy Documented** - No Redis or caching documented
  - **Impact**: Potential performance issues at scale
  - **Action**: Document caching strategy:
    - Azure Cache for Redis setup
    - Cache configuration
    - Cache invalidation
    - Integration with Django caching framework

- [ ] **No Load Balancing Configuration** - Single instance deployment
  - **Impact**: No high availability or load distribution
  - **Action**: Document Azure Container Apps scaling:
    - Horizontal Pod Autoscaler configuration
    - CPU and memory-based scaling
    - Custom metrics scaling
    - Traffic splitting for blue-green deployments

- [ ] **No SSL/TLS Certificate Management** - HTTPS configuration unclear
  - **Impact**: Security and SEO issues
  - **Action**: Document SSL setup:
    - Azure Container Apps custom domains
    - Let's Encrypt certificate automation
    - Certificate renewal procedures

---

## Project Organization

### 🔴 Critical

- [ ] **Clean Up Test Directories** - Multiple test directories and files in production code
  - **Impact**: Bloated deployment, potential confusion
  - **Action**: 
    - Remove or consolidate test data
    - Move test utilities to proper test directories
  - **Locations**: Various `tests/` subdirectories with READMEs

### 🟡 Medium Priority

- [ ] **Archive Directory Not Documented** - `/archive/` contains old Dockerfiles
  - **Impact**: Confusion about which files to use
  - **Action**: 
    - Document purpose in `archive/README.md`
    - Consider removing if no longer needed
  - **Location**: `/archive/`

- [ ] **Virtual Environment Committed** - `src/src_env/` appears to be a virtual environment
  - **Impact**: Unnecessary files in repository
  - **Action**: 
    - Remove from repository
    - Add to .gitignore
  - **Location**: `src/src_env/`

- [ ] **Unclear Events Directory** - `/events/` with single event.json file
  - **Impact**: Purpose unclear
  - **Action**: Document purpose or remove if unused
  - **Location**: `/events/`

### 🟢 Low Priority

- [ ] **Version Management Strategy** - VERSION file exists but no clear versioning strategy
  - **Impact**: Unclear versioning scheme
  - **Action**: Document versioning strategy:
    - Semantic versioning (major.minor.patch)
    - When to bump versions
    - How versions relate to deployments

- [ ] **Multiple Configuration Files** - Several config formats (YAML, TOML, JSON)
  - **Impact**: Maintenance complexity
  - **Action**: Document why each format is used and when to use each

- [ ] **Jekyll Integration Purpose Unclear** - Jekyll pages in Django app unclear purpose
  - **Impact**: Confusion about architecture
  - **Action**: Document:
    - Why Jekyll is used
    - How it integrates with Django
    - When to use Django vs Jekyll for content

---

## Feature Enhancements

### 🟡 Medium Priority

- [ ] **Add Swagger/OpenAPI Documentation** - REST API needs interactive documentation
  - **Impact**: Better API discoverability
  - **Action**: Install drf-spectacular and configure
  - **Benefit**: Auto-generated, interactive API docs

- [ ] **Add Django Debug Toolbar** - For development debugging
  - **Impact**: Easier debugging and optimization
  - **Action**: Install django-debug-toolbar for development
  - **Benefit**: SQL query inspection, timing information

- [ ] **Add Django Extensions** - Useful management commands
  - **Impact**: Better development experience
  - **Action**: Already listed in comments, install and configure
  - **Features**: shell_plus, graph_models, runserver_plus

- [ ] **Implement Proper Logging** - Structured logging not configured
  - **Impact**: Harder to debug production issues
  - **Action**: Configure Python logging:
    - Structured JSON logs
    - Log levels per module
    - Separate log files by severity

### 🟢 Low Priority

- [ ] **Add Admin Actions Documentation** - Custom admin actions not documented
  - **Impact**: Admins don't know available bulk actions
  - **Action**: Document admin interface features

- [ ] **Add Management Commands Documentation** - Custom commands exist but undocumented
  - **Impact**: Developers don't know available commands
  - **Action**: Document all custom management commands
  - **Location**: `src/parodynews/management/commands/`

- [ ] **Add Webhooks** - For GitHub and other integrations
  - **Impact**: Limited integration capabilities
  - **Action**: Add webhook handlers for:
    - GitHub events
    - OpenAI callbacks
    - Other third-party integrations

- [ ] **Add Email Templates** - Plain text emails only
  - **Impact**: Less professional appearance
  - **Action**: Create HTML email templates with inline CSS

- [ ] **Add Celery for Background Tasks** - Long-running tasks block requests
  - **Impact**: Poor user experience for slow operations
  - **Action**: Add Celery + Redis for:
    - AI content generation
    - Email sending
    - Report generation

---

## Priority Summary

### Immediate Actions (Do First)
1. **Complete Azure deployment**: Run `azd up` and configure environment variables
2. **Setup Azure CI/CD pipeline**: Use GitHub Actions starter and run `azd pipeline config`
3. Fix license inconsistency
4. Create .env.example file
5. Remove/clean up test code from production (foobar directory)
6. Configure PostgreSQL connection variables in Azure

### Short Term (Next Sprint)
1. Add SECURITY.md
2. Setup GitHub Actions for CI/CD (non-Azure workflows)
3. Add pre-commit hooks
4. Setup automated testing pipeline
5. Create CHANGELOG.md and CODE_OF_CONDUCT.md
6. Add security scanning to CI
7. Configure Azure monitoring and alerts

### Medium Term (Next Month)
1. Document production configuration and deployment procedures
2. Setup test coverage reporting
3. API documentation with Swagger
4. Consolidate scattered documentation
5. Add monitoring and logging documentation
6. Implement rate limiting
7. Optimize Docker images and Azure container configuration

### Long Term (Future Releases)
1. Add performance testing
2. Implement caching strategy with Azure Cache for Redis
3. Add Celery for background tasks
4. Create architecture diagrams
5. Enhance email templates
6. Add webhook support
7. Setup Azure CDN and advanced scaling

---

## Contributing to This TODO

This TODO is a living document. If you identify additional issues or complete items:

1. Update this file with your changes
2. Move completed items to CHANGELOG.md
3. Add new issues as they're discovered
4. Update priorities as project needs change

**Note**: This document consolidates information from the previous `next-steps.md` file (generated by `azd init`) to provide a comprehensive project roadmap.

**Last Review**: October 26, 2025  
**Next Review**: November 2025

