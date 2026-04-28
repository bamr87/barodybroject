# Workflow Scripts

## Purpose
This directory contains shell scripts used by GitHub Actions workflows. The workflows should orchestrate jobs, permissions, services, and artifacts; command logic belongs here so it can be reviewed and tested more easily.

## Contents
- `check-job-results.sh`: Fail a summary job when required upstream jobs failed.
- `ci-install-system-deps.sh`: Install Ubuntu system packages needed by CI jobs.
- `compose-validation.sh`: Validate Docker Compose files and run container smoke checks.
- `deploy.sh`: Shared Azure Developer CLI deployment helpers.
- `django-prechecks.sh`: Run Django configuration and migration-plan checks.
- `e2e-tests.sh`: Prepare and run Playwright E2E tests.
- `maintenance.sh`: Scheduled dependency, container, infrastructure, and cleanup tasks.
- `python-install.sh`: Install Python dependency groups for workflow jobs.
- `quality.sh`: Run linting, audit, metrics, and environment validation checks.
- `run-pytest.sh`: Run pytest from the Django project root.

## Usage
Call scripts from workflows with `bash`:

```bash
bash .github/scripts/python-install.sh test
bash .github/scripts/run-pytest.sh
```

## Related Components
- `.github/workflows/ci.yml`: Pull request and push validation.
- `.github/workflows/deploy.yml`: Azure deployment.
- `.github/workflows/maintenance.yml`: Scheduled and manual maintenance.