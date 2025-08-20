
# shared Directory

## Purpose
This directory contains shared Azure Bicep infrastructure modules that provide reusable components for deploying common Azure services across different environments. These modules encapsulate best practices for Azure resource configuration and enable consistent, standardized deployments of monitoring, security, networking, and application infrastructure components.

## Contents
- `registry.bicep`: Azure Container Registry configuration for storing and managing container images
- `dashboard-web.bicep`: Azure Dashboard and web application infrastructure templates
- `apps-env.bicep`: Azure App Service Environment configuration for hosting containerized applications
- `monitoring.bicep`: Azure Monitor, Application Insights, and logging infrastructure configuration
- `keyvault.bicep`: Azure Key Vault configuration for secure secrets and certificate management

## Usage
Shared modules are imported and used by main infrastructure templates:

```bicep
// Example usage in main.bicep
param environmentName string
param location string = resourceGroup().location

// Import shared modules
module keyVault 'shared/keyvault.bicep' = {
  name: 'keyVaultDeployment'
  params: {
    environmentName: environmentName
    location: location
    keyVaultName: '${environmentName}-kv'
  }
}

module containerRegistry 'shared/registry.bicep' = {
  name: 'containerRegistryDeployment'
  params: {
    environmentName: environmentName
    location: location
    registryName: '${environmentName}registry'
  }
}

module monitoring 'shared/monitoring.bicep' = {
  name: 'monitoringDeployment'
  params: {
    environmentName: environmentName
    location: location
    appInsightsName: '${environmentName}-ai'
  }
}
```

Module features:
- **Reusable Components**: Standardized Azure service configurations that can be used across multiple deployments
- **Best Practices**: Azure resource configurations following Microsoft's recommended practices
- **Environment Agnostic**: Parameterized modules that work across development, staging, and production environments
- **Security Standards**: Secure configuration patterns for Key Vault, networking, and access control
- **Monitoring Integration**: Consistent logging and monitoring across all deployed resources

## Container Configuration
Bicep modules deployed through Azure DevOps or Azure CLI:
- Infrastructure as Code deployment through Azure Resource Manager
- Container registry support for storing and deploying application containers
- Monitoring and logging configuration for containerized applications
- Secure secrets management for container environment variables

## Related Paths
- Incoming: Imported by main infrastructure templates and deployment scripts
- Outgoing: Deploys shared Azure infrastructure components used by application-specific resources
