# GitHub Actions Workflows

## Purpose
This directory contains the active GitHub Actions workflow set for Barodybroject. The workflow files stay small by delegating shell logic to scripts in `.github/scripts/`.

## Workflow map

| Workflow | File | Trigger | Purpose | Notes |
|---|---|---|---|---|
| CI - Build and Test | `ci.yml` | Push and pull request to `main`/`develop` | Django checks, tests, quality gates, container validation, and container security scan | Replaces the former separate quality and container workflows |
| Deploy to Azure | `deploy.yml` | Successful CI on `main`, or manual dispatch | Canonical Azure Developer CLI deployment to Container Apps | Only workflow that should run `azd provision` or `azd deploy` |
| Maintenance and Infrastructure | `maintenance.yml` | Daily/weekly schedules, manual dispatch | Dependency health, infrastructure tests, container environment checks, cleanup, dependency update PRs | Replaces the former environment and infrastructure-test workflows |
| Deploy Jekyll with GitHub Pages dependencies preinstalled | `jekyll-gh-pages.yml` | Push to `main` when `src/pages/**` changes, manual dispatch | Build and deploy the Jekyll site to GitHub Pages | Kept separate because Pages deployment has dedicated permissions |

Removed or consolidated workflows:

- `quality.yml` and `container.yml` were consolidated into `ci.yml`.
- `environment.yml` and `infrastructure-test.yml` were consolidated into `maintenance.yml`.
- `azure-dev.yml` was removed; use `deploy.yml` with the `development` environment.
- `openai-issue-processing.yml` was removed until the issue processor can run reviewed code behind maintainer approval.
- `cruft.yml` was removed because the repository does not currently contain `.cruft.json`.

## Script policy

- Put reusable shell logic in `.github/scripts/*.sh`.
- Keep workflow `run:` blocks to simple script invocations.
- Scripts must use `set -euo pipefail` and avoid printing secrets or raw secret-scanner findings.
- Call scripts with `bash`, so executable file mode is not required for GitHub Actions.

## Deployment policy

- `deploy.yml` is the only workflow that should run Azure deployment commands.
- Automatic deployment is limited to the `development` environment after successful CI on `main`.
- Staging and production should be run manually through `workflow_dispatch` and protected with GitHub environments.
- Deployment artifacts must not include `.azure/`, `.env`, raw `azd env get-values` output, or secret-bearing logs.

## Required Azure configuration

Set these repository or environment variables for deployment:

| Name | Type | Notes |
|---|---|---|
| `AZURE_CLIENT_ID` | Variable | Azure app/client ID for OIDC login |
| `AZURE_TENANT_ID` | Variable | Azure tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Variable | Azure subscription ID |
| `AZURE_LOCATION` | Variable | Azure region, defaults to `eastus` if omitted |
| `AZURE_ENV_NAME` | Environment variable | Azure Developer CLI environment name; set separately on each GitHub environment |
| `AZURE_CREDENTIALS` | Secret | Optional service principal JSON fallback when OIDC is not configured |

Runtime secrets such as `SECRET_KEY`, `OPENAI_API_KEY`, and `DJANGO_SUPERUSER_PASSWORD` must be supplied through Azure Developer CLI environment values or Container App secrets. Do not commit production secret values.

## Test environment rules

- Run Django commands from `src/` unless a script explicitly handles `PYTHONPATH`.
- Use PostgreSQL for all workflow tests; this project has no SQLite fallback.
- Set `DJANGO_SETTINGS_MODULE=barodybroject.settings.testing` for pytest and CI validation.
- Keep Playwright E2E as a single CI job instead of repeating it across every Python matrix version.

## Security rules

- Use minimum `permissions:` per workflow or job.
- Do not expose repository secrets to code checked out from external repositories.
- Prefer the built-in `github.token` with explicit permissions over custom personal access tokens.
- Upload reports as artifacts or SARIF, but avoid printing secret scanner findings directly to logs.
- Pin external actions to stable version tags. Avoid floating refs such as `master`.