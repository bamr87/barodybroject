# infra/ Directory

## Purpose
This directory contains Azure Infrastructure as Code (IaC) using Bicep templates for deploying and managing the complete Azure infrastructure required by the parody news generator application. It provides declarative infrastructure definitions that enable consistent, repeatable deployments across different environments.

## Contents
- `abbreviations.json`: Azure resource naming abbreviations and conventions for consistent resource naming across the infrastructure
- `app/`: Application-specific Bicep templates for container apps, databases, and application services (has its own README)
- `main.bicep`: Main infrastructure orchestration template that coordinates the deployment of all infrastructure components
- `main.parameters.json`: Configuration parameters for the main template including resource naming, sizing, and environment-specific settings
- `modules/`: Reusable Bicep modules for common infrastructure patterns and components (has its own README)
- `shared/`: Shared infrastructure components like resource groups, monitoring, and cross-cutting concerns

## Usage
Infrastructure deployment using Azure CLI and Azure Developer CLI:

```bash
# Deploy using Azure Developer CLI (recommended)
azd up

# Deploy using Azure CLI
az deployment group create \
  --resource-group barodybroject-rg \
  --template-file main.bicep \
  --parameters @main.parameters.json

# Validate template before deployment
az deployment group validate \
  --resource-group barodybroject-rg \
  --template-file main.bicep \
  --parameters @main.parameters.json

# Deploy specific components
az deployment group create \
  --resource-group barodybroject-rg \
  --template-file app/src.bicep \
  --parameters name=barodybroject-app
```

Infrastructure components deployed:
- **Azure Container Apps**: Scalable container hosting for Django application
- **PostgreSQL Flexible Server**: Managed database service with backup and security
- **Container Registry**: Private registry for application container images
- **Key Vault**: Secure secrets and certificate management
- **Application Insights**: Application performance monitoring and logging
- **Storage Account**: Static file hosting and backup storage

## Container Configuration
The infrastructure defines container app environments and hosting:
- Container Apps Environment with ingress and networking configuration
- Container registry integration for private image deployment
- Environment variables and secrets injection into containers
- Auto-scaling rules based on CPU and memory usage
- Health check endpoints and monitoring configuration

## Related Paths
- Incoming: Used by Azure deployment scripts (`scripts/azure-deployment-setup.py`) and GitHub Actions workflows
- Outgoing: Creates Azure resources that host and support the containerized Django application
