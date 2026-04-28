---
name: azure-deploy
description: "Deploy Barodybroject to Azure Container Apps with azd and Bicep. Use when: Azure deployment, azd up, azd provision, azd deploy, Container Apps, Bicep infrastructure, production environment variables, smoke tests, or deployment troubleshooting."
argument-hint: "[environment] [provision|deploy|up|smoke-test|troubleshoot]"
---

# Azure Deploy

Use this skill to deploy or troubleshoot Barodybroject on Azure. The current default deployment path is Azure Developer CLI plus Bicep targeting Azure Container Apps.

## When to use

- The user asks to deploy, provision, update, smoke test, or troubleshoot Azure hosting.
- The task touches `azd`, Azure Container Apps, Bicep templates, PostgreSQL Flexible Server, Azure Container Registry, Key Vault, or deployment workflows.
- The task involves production environment variables, app startup, container logs, or post-deploy validation.

## Project facts

- Run deployment commands from the repository root.
- `azure.yaml` defines one service named `src`, with project path `src`, host `containerapp`, and language `python`.
- `infra/main.bicep` is the active infrastructure entry point. It provisions the resource group, Container Registry, Key Vault, Container Apps environment, monitoring, PostgreSQL, and the `src` container app.
- `infra/app/src.bicep` configures Container Apps ingress on port `8000`; the Docker image also exposes and serves port `8000`.
- `src/Dockerfile` uses `barodybroject.settings.production` and starts Gunicorn through `src/docker-entrypoint.sh`.
- `src/docker-entrypoint.sh` waits for PostgreSQL, runs migrations, runs `ensure_admin`, collects static files, then starts the app.
- Docs that mention App Service or Docker Hub minimal-cost deployment are historical or alternate-cost paths. Prefer the current Container Apps path unless the user explicitly asks for a different target.

## Required context

Before changing deployment code or running a deploy, inspect the current versions of these files:

- `azure.yaml`
- `infra/main.bicep`
- `infra/main.parameters.json`
- `infra/app/src.bicep`
- `src/Dockerfile`
- `src/docker-entrypoint.sh`
- `.github/workflows/deploy.yml` and `.github/workflows/azure-dev.yml` if CI/CD is involved
- `docs/deployment/README.md` and any troubleshooting guide relevant to the failure

## Safety rules

- Never print secret values. Mask or describe secret presence only.
- Do not run `azd down`, delete resource groups, rotate credentials, or overwrite production app settings unless the user explicitly asks.
- Confirm the selected Azure subscription and `azd` environment before provisioning or deploying.
- Treat `.env`, `.azure/`, deployment logs, and credential files as sensitive.
- For production, do not allow default admin credentials or the development fallback `SECRET_KEY`.

## Local preflight

1. Check repository state with `git status --short` and note unrelated changes without reverting them.
2. Validate Django inside the dev container:

   ```bash
   docker compose -f .devcontainer/docker-compose_dev.yml exec -T python python manage.py check
   ```

3. Run tests with testing settings:

   ```bash
   docker compose -f .devcontainer/docker-compose_dev.yml exec -T -e DJANGO_SETTINGS_MODULE=barodybroject.settings.testing python python -m pytest
   ```

4. If container packaging changed, build the production image locally:

   ```bash
   docker build -t barodybroject:deploy-check -f src/Dockerfile src/
   ```

## Configure azd

1. Authenticate and confirm the account:

   ```bash
   azd auth login
   az account show --output table
   ```

2. Select or create the environment:

   ```bash
   azd env list
   azd env select <environment-name>
   # or
   azd env new <environment-name>
   ```

3. Set required infrastructure parameters:

   ```bash
   azd env set AZURE_LOCATION <azure-region>
   azd env set AZURE_SUBSCRIPTION_ID <subscription-id>
   azd env set DB_PASSWORD <secure-postgres-password>
   azd env set AZURE_PRINCIPAL_ID <user-or-app-object-id>
   ```

4. Set runtime app values through Bicep `srcDefinition.settings` or Container Apps app settings. Production deployments normally need:

   ```bash
   SECRET_KEY=<strong-django-secret>
   RUNNING_IN_PRODUCTION=True
   DEBUG=False
   DJANGO_SETTINGS_MODULE=barodybroject.settings.production
   ALLOWED_HOSTS=<container-app-host>,<custom-domain-if-any>
   OPENAI_API_KEY=<openai-key>
   DJANGO_SUPERUSER_USERNAME=<admin-username>
   DJANGO_SUPERUSER_EMAIL=<admin-email>
   DJANGO_SUPERUSER_PASSWORD=<strong-admin-password>
   ```

5. Verify names only, not values:

   ```bash
   azd env get-values
   ```

## Deploy

Use a preview before changing infrastructure:

```bash
azd provision --preview
```

Provision and deploy separately when debugging:

```bash
azd provision
azd deploy
```

Use the combined command for a normal full deployment:

```bash
azd up
```

## Post-deploy validation

1. Get the deployed URI:

   ```bash
   azd env get-values
   ```

2. Smoke test the app and critical endpoints:

   ```bash
   curl -fsS "$BACKEND_URI"
   curl -fsS "$BACKEND_URI/admin/"
   curl -fsS "$BACKEND_URI/api/"
   ```

3. Inspect Container Apps state and logs:

   ```bash
   az containerapp show --name src --resource-group rg-<environment-name> --output table
   az containerapp revision list --name src --resource-group rg-<environment-name> --output table
   az containerapp logs show --name src --resource-group rg-<environment-name> --follow
   # or
   azd monitor --logs
   ```

4. If browser behavior matters, open the deployed URI and verify the user-facing workflow directly.

## CI/CD workflow notes

- Prefer `azd pipeline config` for setting up GitHub OIDC credentials.
- `.github/workflows/deploy.yml` supports manual dispatch and deploys with `azd provision --no-prompt` then `azd deploy --no-prompt`.
- The workflows expect GitHub variables such as `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_ENV_NAME`, and `AZURE_LOCATION`, or a fallback `AZURE_CREDENTIALS` secret.
- Avoid enabling multiple deployment workflows for the same environment unless that is intentional.

## Troubleshooting

- 502 or app unavailable: check `az containerapp logs show`, revision status, and whether the app binds to port `8000`.
- Database failures: verify `DB_HOST`, `DB_NAME`, `DB_USERNAME`, `DB_PASSWORD`, PostgreSQL firewall settings, and SSL requirements.
- Secret key failure: ensure production has a strong `SECRET_KEY`; the development fallback is invalid in production.
- Admin login uses defaults: set `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, and `DJANGO_SUPERUSER_PASSWORD`, then restart or redeploy.
- OpenAI actions fail: set `OPENAI_API_KEY` or create an `AppConfig` row after deployment.
- Quota errors: prefer Container Apps for this repo; only switch to App Service or another platform when the user explicitly chooses that path.
- Image pull failures: verify ACR exists, the Container App has `AcrPull`, and the managed identity is assigned correctly.

## Output format

When done, report:

- Environment name, Azure region, and deployment URI if known.
- Commands run and whether they passed.
- Smoke test results.
- Any secrets or variables that are missing by name only.
- Remaining risks or manual follow-up steps.