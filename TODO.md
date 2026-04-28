# TODO: Project Issues and Enhancements

This document tracks open issues, missing functionality, and enhancements for the
Barodybroject Django/OpenAI project. It was reviewed against the current repository
state on April 27, 2026.

**Version**: 0.4.0
**Last Updated**: April 27, 2026
**Last Review**: April 27, 2026
**Next Review**: May 2026

## Table of Contents

- [Review Snapshot](#review-snapshot)
- [Azure Deployment Next Steps](#azure-deployment-next-steps)
- [Configuration & Setup Issues](#configuration--setup-issues)
- [CI/CD & Automation](#cicd--automation)
- [Documentation Gaps](#documentation-gaps)
- [Code Quality & Testing](#code-quality--testing)
- [Security & Best Practices](#security--best-practices)
- [Infrastructure & Deployment](#infrastructure--deployment)
- [Project Organization](#project-organization)
- [Feature Enhancements](#feature-enhancements)
- [Resolved Since Previous Review](#resolved-since-previous-review)
- [Priority Summary](#priority-summary)
- [Contributing to This TODO](#contributing-to-this-todo)

---

## Review Snapshot

The previous TODO contained several stale findings. The repository now includes:

- Split Django settings in `src/barodybroject/settings/`.
- A root `.env.example` template.
- Tracked initial Django migration at `src/parodynews/migrations/0001_initial.py`.
- GitHub Actions workflows for CI, quality/security scanning, containers,
  infrastructure tests, and Azure deployment.
- DRF throttling defaults in `src/barodybroject/settings/base.py`.
- Optional Django Debug Toolbar and django-extensions configuration.
- Logging configuration in `src/barodybroject/settings/base.py`.
- A setup health endpoint at `/setup/health/`.

Known remaining gaps are concentrated around Azure production hardening,
repository governance files, dependency automation, OpenAPI documentation,
deployment runbook consolidation, and local developer automation.

---

## Azure Deployment Next Steps

This section tracks Azure Developer CLI (`azd`) and Azure Container Apps follow-up
work. The deployment workflow exists at `.github/workflows/azure-dev.yml`, so the
remaining work is verification and production hardening rather than creating the
pipeline from scratch.

### Critical

- [ ] **Harden Azure application environment values**
  - **Impact**: `infra/app/src.bicep` currently sets an insecure fallback
    `SECRET_KEY` and `RUNNING_IN_PRODUCTION=false` for the Container App.
  - **Action**: Move `SECRET_KEY` into Key Vault or secure app settings, and set
    production deployments to `RUNNING_IN_PRODUCTION=true`.
  - **Files**: `infra/app/src.bicep`, `infra/main.parameters.json`.

- [ ] **Verify current Azure deployment state**
  - **Impact**: The repository contains Azure infrastructure and deployment
    workflows, but the current deployed resource state is not captured here.
  - **Action**: Run `azd show` and verify the Container App endpoint, revision
    status, database connection, and Application Insights connection.
  - **Document**: Add the verified endpoint and troubleshooting notes to the
    deployment documentation.

- [ ] **Confirm Azure CI/CD credentials and variables**
  - **Impact**: `.github/workflows/azure-dev.yml` expects Azure variables or
    secrets configured outside the repository.
  - **Action**: Run `azd pipeline config` or verify `AZURE_CLIENT_ID`,
    `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_ENV_NAME`, and
    `AZURE_LOCATION` in GitHub repository variables/secrets.
  - **Verify**: Trigger the workflow manually and confirm both provisioning and
    smoke tests complete successfully.

### Medium Priority

- [ ] **Validate Azure database connection variables end-to-end**
  - **Current state**: `infra/app/src.bicep` injects `DB_HOST`, `DB_USERNAME`,
    `DB_NAME`, `DB_PASSWORD`, `POSTGRES_PORT`, and `PORT=8000`.
  - **Action**: Confirm Django production settings consume these values in Azure
    and document the expected variable names. Avoid older `POSTGRES_*` wording
    except where it is specifically used by the database container.

- [ ] **Add Azure cost monitoring and budget alerts**
  - **Action**: Configure Cost Management budgets and alerts in Azure Portal.
  - **Reference**: [Azure billing overview](https://learn.microsoft.com/azure/developer/intro/azure-developer-billing).

- [ ] **Add Azure deployment smoke-test runbook**
  - **Action**: Document the expected `azd provision`, `azd deploy`, workflow
    dispatch, and rollback checks in one place.
  - **Include**: Portal links to Container Apps revisions, log streams,
    Application Insights, and PostgreSQL diagnostics.

### Infrastructure Overview

Core Azure files:

- `azure.yaml`: Azure Developer CLI project configuration.
- `infra/main.bicep`: Main Bicep deployment entry point.
- `infra/main.parameters.json`: Parameter defaults used by deployments.
- `infra/app/src.bicep`: Azure Container Apps module for the Django service.
- `infra/app/db-postgres.bicep`: PostgreSQL Flexible Server module.
- `infra/app/db-postgres-minimal.bicep`: Lower-cost PostgreSQL variant.
- `infra/shared/keyvault.bicep`: Azure Key Vault module.
- `infra/shared/monitoring.bicep`: Log Analytics and Application Insights.
- `infra/shared/registry.bicep`: Azure Container Registry module.

Container build notes:

- The application currently builds from `src/Dockerfile`, not Oryx buildpacks.
- `src/Dockerfile` exposes port `8000`.
- `infra/app/src.bicep` configures Container Apps ingress `targetPort: 8000`.

---

## Configuration & Setup Issues

### Critical

- [ ] **License inconsistency**
  - **Impact**: `pyproject.toml` declares `GPL-3.0-or-later`, while `LICENSE`
    contains the MIT License.
  - **Recommendation**: Choose one license and update both the classifier and
    license metadata. The previous recommendation was to use MIT.
  - **Files**: `LICENSE`, `pyproject.toml`.

### Medium Priority

- [ ] **Duplicate dependency management**
  - **Impact**: Runtime and development dependencies are split across
    `src/requirements.txt`, `requirements-dev.txt`, and `pyproject.toml`.
  - **Action**: Decide on a source of truth. If keeping requirements files for
    Docker compatibility, document the sync workflow and regenerate process.
  - **Files**: `src/requirements.txt`, `requirements-dev.txt`, `pyproject.toml`.

- [ ] **Keep `.env.example` aligned with settings**
  - **Impact**: A template now exists, but it needs to stay synchronized with
    split settings, Azure variable names, and production expectations.
  - **Action**: Review `.env.example` whenever settings or compose variables
    change.

---

## CI/CD & Automation

### Critical

- [ ] **Add Dependabot configuration**
  - **Impact**: Dependency and GitHub Actions updates are not automated.
  - **Action**: Add `.github/dependabot.yml` for Python dependencies, Docker,
    and GitHub Actions.

- [ ] **Add pre-commit hooks**
  - **Impact**: CI enforces several checks, but local commits are not guarded.
  - **Action**: Add `.pre-commit-config.yaml` for Ruff, Black, isort, secret
    scanning, and whitespace checks.

### Medium Priority

- [ ] **Add Bicep validation to CI**
  - **Impact**: Existing workflows validate Docker and run infrastructure tests,
    but Bicep lint/build validation should be explicit.
  - **Action**: Add `az bicep build` or an equivalent Azure validation step for
    files under `infra/`.

- [ ] **Set coverage thresholds and publish coverage results**
  - **Current state**: pytest-cov is configured in `pyproject.toml`, and CI runs
    tests with coverage.
  - **Action**: Add a minimum coverage threshold, publish a coverage artifact or
    badge, and decide which files count toward the threshold.

- [ ] **Audit CI scanner failure behavior**
  - **Current state**: Quality workflows run Bandit, Safety, pip-audit, Trivy,
    and a secrets scan.
  - **Action**: Confirm which scanners are blocking, which only upload reports,
    and document the intended policy.

### Low Priority

- [ ] **Add release automation**
  - **Impact**: Version bumps and changelog updates remain manual.
  - **Action**: Add semantic-release, release-please, or a documented manual
    release checklist tied to the `VERSION` file and `CHANGELOG.md`.

---

## Documentation Gaps

### Critical

- [ ] **Missing root `SECURITY.md`**
  - **Impact**: Security reporting guidance is not visible in GitHub's standard
    security policy location.
  - **Current state**: `docs/SECURITY_DOCUMENTATION.md` exists, but root
    `SECURITY.md` does not.
  - **Action**: Add root `SECURITY.md` with supported versions, reporting
    process, and security update policy.

- [ ] **Missing root `CODE_OF_CONDUCT.md`**
  - **Impact**: `CONTRIBUTING.md` references community standards that are not
    present at the expected root path.
  - **Action**: Add `CODE_OF_CONDUCT.md`, preferably based on Contributor
    Covenant.

### Medium Priority

- [ ] **Add OpenAPI documentation**
  - **Impact**: REST API consumers do not have interactive endpoint docs.
  - **Action**: Install and configure drf-spectacular or another OpenAPI
    generator, then expose schema, Swagger UI, and ReDoc URLs.

- [ ] **Create a development guide**
  - **Impact**: There is no root `docs/DEVELOPMENT.md` that explains the current
    container-first workflow.
  - **Action**: Document dev container startup, debugpy behavior, Django command
    execution, tests, migrations, and common troubleshooting.

- [ ] **Consolidate deployment documentation**
  - **Impact**: Deployment information exists across multiple docs and Azure
    files, which makes it easy for runbooks to drift.
  - **Action**: Create or update a single deployment runbook that links to the
    deeper Azure, Docker, database, and troubleshooting documents.

- [ ] **Add architecture diagrams**
  - **Impact**: The system architecture is still mostly text-based.
  - **Action**: Add diagrams for application architecture, Azure deployment,
    request flow, and content generation/data flow.

### Low Priority

- [ ] **Consolidate scattered README files**
  - **Impact**: Many directory-level READMEs can become stale or duplicative.
  - **Action**: Keep high-value directory READMEs, remove obsolete ones, and link
    common material back to `docs/`.

- [ ] **Keep database schema docs current**
  - **Current state**: `src/parodynews/docs/source/reference/database-schema.rst`
    exists.
  - **Action**: Add generation instructions and optional ER diagrams so schema
    docs stay synchronized with migrations.

---

## Code Quality & Testing

### Medium Priority

- [ ] **Document integration and E2E testing procedures**
  - **Impact**: Tests exist, but contributors need clearer guidance on when and
    how to run integration, infrastructure, and Playwright suites.
  - **Action**: Add testing guidance to `CONTRIBUTING.md` or a dedicated
    development guide.

- [ ] **Add dedicated accessibility tests**
  - **Impact**: Accessibility tooling is listed in development dependencies, but
    regular accessibility checks are not documented or enforced.
  - **Action**: Add axe/Playwright examples and decide which routes are covered
    in CI.

- [ ] **Add performance and load testing**
  - **Impact**: Container workflows include basic performance checks, but there
    are no load-test baselines.
  - **Action**: Add Locust, k6, or a documented benchmark script for critical
    pages and API endpoints.

### Low Priority

- [ ] **Review lint/type-check coverage**
  - **Current state**: Workflows run Black, isort, Ruff, Flake8, Pylint, MyPy,
    Xenon, and Radon.
  - **Action**: Confirm the overlap is intentional and trim redundant checks if
    maintenance cost becomes high.

---

## Security & Best Practices

### Critical

- [ ] **Remove insecure Azure secret defaults**
  - **Impact**: `infra/app/src.bicep` contains a literal insecure Django
    `SECRET_KEY` fallback.
  - **Action**: Use Key Vault or secure Container Apps secrets for production
    values, and fail deployment when required values are missing.

- [ ] **Add repository security policy**
  - **Impact**: Automated scanners exist, but vulnerability reporting still needs
    a standard process.
  - **Action**: Add root `SECURITY.md` and link it from `README.md` and
    `CONTRIBUTING.md`.

### Medium Priority

- [ ] **Document CORS and trusted-origin policy**
  - **Impact**: CSRF trusted origins are configured, but CORS expectations for
    external frontends are not documented.
  - **Action**: Document whether cross-origin API use is supported and add
    `django-cors-headers` only if needed.

- [ ] **Review CSP requirements**
  - **Current state**: Security headers are configured, and `django-csp` is in
    optional dependencies, but no CSP policy is enforced by default.
  - **Action**: Decide whether to enable CSP for production and document any
    required exceptions for Jekyll assets, admin pages, and third-party services.

- [ ] **Verify DRF throttling coverage**
  - **Current state**: Global DRF throttling exists for anonymous and user
    requests.
  - **Action**: Confirm custom API views and non-DRF endpoints have appropriate
    rate limiting or abuse protection.

---

## Infrastructure & Deployment

### Critical

- [ ] **Add root health/readiness/liveness endpoints or configure probes**
  - **Current state**: `/setup/health/` exists, but root `/health/`,
    `/readiness/`, and `/liveness/` routes are not defined.
  - **Impact**: Container Apps probes may need stable unauthenticated endpoints.
  - **Action**: Add root probe endpoints or explicitly configure Azure to use
    `/setup/health/`.

- [ ] **Document production configuration in one place**
  - **Impact**: Production settings and deployment docs exist, but environment
    variables, scaling, logging, and database settings need one authoritative
    runbook.
  - **Action**: Consolidate production configuration guidance and link to Azure
    deployment docs.

### Medium Priority

- [ ] **Optimize Docker image build**
  - **Current state**: `src/Dockerfile` is single-stage and installs build tools
    in the final image.
  - **Action**: Consider a multi-stage build, smaller runtime image, and improved
    layer caching.

- [ ] **Align logging with Azure runtime expectations**
  - **Current state**: Django logging exists, including file logging and Azure
    Monitor initialization when an Application Insights connection string is set.
  - **Action**: Ensure production logs reach stdout/stderr or Azure Monitor
    reliably, and document JSON logging expectations.

- [ ] **Add monitoring and alert runbook**
  - **Current state**: Application Insights and Log Analytics infrastructure
    modules exist.
  - **Action**: Document alerts, dashboards, log queries, and incident response
    checks.

- [ ] **Document backup and recovery procedures**
  - **Impact**: PostgreSQL recovery steps are not captured in a runbook.
  - **Action**: Document retention, point-in-time restore, restore testing, and
    disaster recovery expectations for Azure PostgreSQL Flexible Server.

### Low Priority

- [ ] **Document CDN/static-file strategy**
  - **Impact**: Static files are served by the app today.
  - **Action**: Decide whether Azure CDN or Blob Storage is needed for production.

- [ ] **Document caching strategy**
  - **Current state**: Production settings include Redis cache configuration with
    a fallback.
  - **Action**: Document whether Azure Cache for Redis is required, how to set
    `REDIS_URL`, and how cache invalidation should work.

- [ ] **Document scaling and traffic strategy**
  - **Impact**: Container Apps scale bounds exist, but operational guidance is
    thin.
  - **Action**: Document autoscaling triggers, minimum replicas, traffic
    splitting, and rollback procedures.

- [ ] **Document SSL/TLS and custom-domain management**
  - **Action**: Document Azure Container Apps custom domains, certificate
    ownership, renewal, and DNS expectations.

---

## Project Organization

### Medium Priority

- [ ] **Rationalize root test directories**
  - **Impact**: The repository has `test/`, workflow-driven tests, and
    application tests under `src/parodynews/tests/`.
  - **Action**: Document the purpose of each location or consolidate where
    practical.

- [ ] **Document Jekyll integration**
  - **Impact**: The Django app includes a Jekyll site under `src/pages/`, but the
    architecture boundary is easy to miss.
  - **Action**: Document why Jekyll is used, how it is built, and when content
    belongs in Django versus Jekyll.

### Low Priority

- [ ] **Document version management strategy**
  - **Impact**: `VERSION`, `pyproject.toml`, and changelog files need a clear
    release relationship.
  - **Action**: Define when to bump versions, how versions relate to deployments,
    and where release notes are maintained.

- [ ] **Document configuration file roles**
  - **Impact**: The project uses YAML, TOML, JSON, Bicep, and requirements files.
  - **Action**: Document which files are source-of-truth configuration versus
    generated or environment-specific files.

---

## Feature Enhancements

### Medium Priority

- [ ] **Add OpenAPI/Swagger UI**
  - **Impact**: API discoverability remains limited.
  - **Action**: Configure schema generation and interactive documentation for the
    Django REST Framework endpoints.

- [ ] **Improve Azure-oriented logging**
  - **Impact**: Logging exists, but production observability should be verified
    against Azure Container Apps and Application Insights.
  - **Action**: Prefer structured stdout logging for containers, keep file logs
    only if there is a clear retention plan, and document expected log fields.

### Low Priority

- [ ] **Document admin actions**
  - **Impact**: Admin users may not know which bulk actions and custom admin
    features exist.
  - **Action**: Add admin interface documentation.

- [ ] **Document management commands**
  - **Impact**: Custom Django commands are discoverable only by reading source.
  - **Action**: Document commands under `src/parodynews/management/commands/`
    and `src/setup/management/commands/`.

- [ ] **Add webhook support**
  - **Impact**: Integration capabilities remain limited.
  - **Action**: Add webhook handlers for GitHub events, OpenAI callbacks, or
    other third-party integrations when product requirements are defined.

- [ ] **Add HTML email templates**
  - **Impact**: Plain text email output is less polished for production use.
  - **Action**: Add responsive HTML templates with text fallbacks.

- [ ] **Add Celery for background tasks**
  - **Impact**: Long-running work can block request/response flows.
  - **Action**: Add Celery and Redis for AI content generation, email delivery,
    report generation, or other slow tasks once workload justifies it.

---

## Resolved Since Previous Review

- [x] **Created root `.env.example`**
  - **Evidence**: `.env.example` exists and includes Django, database, Docker,
    Azure, OpenAI, email, Jekyll, E2E, and production variables.

- [x] **Split Django settings by environment**
  - **Evidence**: `src/barodybroject/settings/base.py`, `development.py`,
    `production.py`, and `testing.py` exist.

- [x] **Tracked Django migration files**
  - **Evidence**: `src/parodynews/migrations/0001_initial.py` exists and
    `.gitignore` no longer ignores `src/parodynews/migrations/0*`.

- [x] **Added GitHub Actions workflows**
  - **Evidence**: `.github/workflows/ci.yml`, `quality.yml`, `container.yml`,
    `infrastructure-test.yml`, and `azure-dev.yml` exist.

- [x] **Added automated testing workflow**
  - **Evidence**: CI runs Django checks, migrations, pytest, Docker Compose
    validation, and infrastructure tests.

- [x] **Added security scanning workflows**
  - **Evidence**: Quality/container workflows include Bandit, Safety,
    pip-audit, Trivy, and a secrets scan.

- [x] **Added container image scanning**
  - **Evidence**: Trivy runs in both quality/container-related workflows.

- [x] **Created changelog files**
  - **Evidence**: Root `CHANGELOG.md` and `docs/changelog/CHANGELOG.md` exist.

- [x] **Removed `src/parodynews/foobar/` test code directory**
  - **Evidence**: No `src/parodynews/foobar/` directory was found.

- [x] **Removed committed `src/src_env/` virtual environment**
  - **Evidence**: No `src/src_env/` directory was found, and `.gitignore`
    covers common virtual environment patterns.

- [x] **Resolved root archive directory concern**
  - **Evidence**: No root `/archive/` directory was found. Archived workflow
    material is under `.github/workflows/archive/` with a README.

- [x] **Configured DRF throttling defaults**
  - **Evidence**: `REST_FRAMEWORK` includes anonymous and user throttles in
    `src/barodybroject/settings/base.py`.

- [x] **Added optional Django Debug Toolbar configuration**
  - **Evidence**: `ENABLE_DEBUG_TOOLBAR` support exists in settings and docs.

- [x] **Added django-extensions dependency**
  - **Evidence**: `django-extensions` is listed in `requirements-dev.txt` and
    `pyproject.toml` optional monitoring dependencies.

- [x] **Added baseline logging configuration**
  - **Evidence**: `LOGGING` is configured in `src/barodybroject/settings/base.py`.

- [x] **Verified Azure/Docker port alignment**
  - **Evidence**: `src/Dockerfile` exposes `8000`, and `infra/app/src.bicep`
    uses `targetPort: 8000`.

---

## Priority Summary

### Immediate Actions

1. Remove the insecure Azure `SECRET_KEY` fallback and correct production flags.
2. Verify Azure deployment state and Azure workflow secrets/variables.
3. Fix the license inconsistency between `LICENSE` and `pyproject.toml`.
4. Add root `SECURITY.md` and `CODE_OF_CONDUCT.md`.
5. Add Dependabot and pre-commit configuration.
6. Add or configure stable health/readiness/liveness probes.

### Short Term

1. Add OpenAPI/Swagger documentation.
2. Add explicit Bicep validation to CI.
3. Set coverage thresholds and publish coverage output.
4. Consolidate development and deployment runbooks.
5. Document production monitoring, alerts, backups, and restore procedures.
6. Review scanner failure behavior and document security gates.

### Medium Term

1. Optimize the Docker image build.
2. Document Jekyll integration and root test directory organization.
3. Add architecture diagrams and keep schema docs generated/current.
4. Add accessibility and performance/load testing.
5. Document CDN, cache, scaling, SSL/TLS, and custom-domain strategies.

### Long Term

1. Add Celery and Redis-backed background tasks when workload requires it.
2. Add webhook support for external integrations.
3. Improve email templates with HTML and text alternatives.
4. Add release automation or a documented release checklist.
5. Continue reducing duplicated or stale documentation.

---

## Contributing to This TODO

This TODO is a living document. When you complete an item or discover a new one:

1. Update this file with the current status.
2. Move completed work into the resolved section with evidence.
3. Add new issues with impact, action, and file references.
4. Update priorities as project needs change.
5. Keep dates current during each review.

**Note**: This document originally consolidated information from the Azure
Developer CLI `next-steps.md` output and the previous project roadmap.
