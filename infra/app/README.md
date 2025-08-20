
# app Directory

## Purpose
This directory contains Azure Bicep templates for deploying the application infrastructure components. These Infrastructure as Code (IaC) templates define the Azure resources needed to run the parody news generator application, including container apps, database, and associated services.

## Contents
- `db-postgres.bicep`: Bicep template for PostgreSQL flexible server deployment with security configurations, firewall rules, and Key Vault integration
- `src.bicep`: Bicep template for Azure Container Apps deployment including application configuration, environment variables, secrets management, and container registry integration

## Usage
Bicep templates are deployed through Azure Developer CLI (azd) or Azure CLI:

```bash
# Deploy using Azure Developer CLI
azd up

# Deploy individual components using Azure CLI
az deployment group create \
  --resource-group barodybroject-rg \
  --template-file db-postgres.bicep \
  --parameters databasePassword=<secure-password>

az deployment group create \
  --resource-group barodybroject-rg \
  --template-file src.bicep \
  --parameters @parameters.json
```

Key features:
- **Container Apps**: Scalable container hosting for Django application
- **PostgreSQL**: Managed database service with flexible server configuration
- **Security**: Key Vault integration for secrets management
- **Monitoring**: Application Insights integration for telemetry
- **Networking**: Container apps environment with ingress configuration

## Container Configuration
The Bicep templates configure container deployment:
- Container registry integration for image deployment
- Environment variables and secrets injection
- Scaling rules and resource allocation
- Health checks and monitoring configuration
- PostgreSQL connection string management

## Related Paths
- Incoming: Used by Azure deployment pipelines and `azd` commands
- Outgoing: Creates Azure resources that host the containerized Django application
