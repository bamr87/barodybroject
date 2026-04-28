#!/usr/bin/env bash
set -euo pipefail

command=${1:-}

case "$command" in
  select-environment)
    event_name=${2:-}
    requested_environment=${3:-}
    github_output=${GITHUB_OUTPUT:?GITHUB_OUTPUT is required}

    if [[ "$event_name" == "workflow_dispatch" ]]; then
      deploy_environment=${requested_environment:-development}
    else
      deploy_environment=development
    fi

    echo "environment=$deploy_environment" >> "$github_output"
    echo "should-deploy=true" >> "$github_output"
    echo "Deployment environment: $deploy_environment"
    ;;
  validate-config)
    if [[ ! -f azure.yaml ]]; then
      echo "azure.yaml not found in the repository root."
      exit 1
    fi

    grep -q "^  src:" azure.yaml
    echo "Azure Developer CLI configuration is present."
    ;;
  login-oidc)
    : "${AZURE_CLIENT_ID:?AZURE_CLIENT_ID is required}"
    : "${AZURE_TENANT_ID:?AZURE_TENANT_ID is required}"

    azd auth login \
      --client-id "$AZURE_CLIENT_ID" \
      --federated-credential-provider github \
      --tenant-id "$AZURE_TENANT_ID"
    ;;
  login-service-principal)
    : "${AZURE_CREDENTIALS:?AZURE_CREDENTIALS is required}"

    client_id=$(jq -r .clientId <<< "$AZURE_CREDENTIALS")
    client_secret=$(jq -r .clientSecret <<< "$AZURE_CREDENTIALS")
    tenant_id=$(jq -r .tenantId <<< "$AZURE_CREDENTIALS")

    echo "::add-mask::$client_secret"

    azd auth login \
      --client-id "$client_id" \
      --client-secret "$client_secret" \
      --tenant-id "$tenant_id"
    ;;
  configure-azd)
    deploy_environment=${2:-development}
    github_output=${GITHUB_OUTPUT:?GITHUB_OUTPUT is required}
    azure_env_name=${AZURE_ENV_NAME:-}
    azure_location=${AZURE_LOCATION:-eastus}

    if [[ -z "$azure_env_name" ]]; then
      if [[ "$deploy_environment" == "development" ]]; then
        azure_env_name=barodybroject-dev
      else
        echo "AZURE_ENV_NAME must be configured on the $deploy_environment GitHub environment."
        exit 1
      fi
    fi

    : "${AZURE_SUBSCRIPTION_ID:?AZURE_SUBSCRIPTION_ID is required}"

    echo "azure-env-name=$azure_env_name" >> "$github_output"
    azd env set AZURE_ENV_NAME "$azure_env_name"
    azd env set AZURE_LOCATION "$azure_location"
    azd env set AZURE_SUBSCRIPTION_ID "$AZURE_SUBSCRIPTION_ID"
    ;;
  deploy)
    github_output=${GITHUB_OUTPUT:?GITHUB_OUTPUT is required}

    azd provision --no-prompt
    azd deploy --no-prompt

    set -a
    source <(azd env get-values)
    set +a

    deployment_uri=${BACKEND_URI:-${WEBSITE_URI:-}}
    if [[ -z "$deployment_uri" ]]; then
      echo "Deployment completed, but azd did not provide BACKEND_URI or WEBSITE_URI."
      exit 1
    fi

    echo "uri=$deployment_uri" >> "$github_output"
    ;;
  smoke)
    : "${DEPLOYMENT_URL:?DEPLOYMENT_URL is required}"

    for path in / /admin/ /api/; do
      echo "Testing $DEPLOYMENT_URL$path"
      max_attempts=30
      attempt=1

      until curl -fsS "$DEPLOYMENT_URL$path" > /dev/null; do
        if [[ "$attempt" -eq "$max_attempts" ]]; then
          echo "Smoke test failed for $path after $max_attempts attempts."
          exit 1
        fi

        attempt=$((attempt + 1))
        sleep 10
      done

      echo "Smoke test passed for $path"
    done
    ;;
  summary)
    github_step_summary=${GITHUB_STEP_SUMMARY:?GITHUB_STEP_SUMMARY is required}

    {
      echo "## Deployment Summary"
      echo
      echo "- **Environment**: ${DEPLOY_ENVIRONMENT:-unknown}"
      echo "- **Azure environment**: ${AZURE_ENV_NAME_OUTPUT:-unknown}"
      echo "- **Status**: ${DEPLOY_RESULT:-unknown}"
      echo "- **Post-deployment tests**: ${POST_DEPLOYMENT_RESULT:-unknown}"

      if [[ "${DEPLOY_RESULT:-}" == "success" ]]; then
        echo "- **URL**: ${DEPLOYMENT_URL:-unknown}"
        echo
        echo "Deployment completed successfully."
      else
        echo
        echo "Deployment failed. Review the workflow logs."
      fi
    } >> "$github_step_summary"
    ;;
  *)
    echo "Usage: $0 {select-environment|validate-config|login-oidc|login-service-principal|configure-azd|deploy|smoke|summary}"
    exit 1
    ;;
esac