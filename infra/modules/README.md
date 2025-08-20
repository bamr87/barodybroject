
# modules Directory

## Purpose
This directory contains reusable Azure Bicep modules for infrastructure deployment. These modules provide common functionality that can be shared across different Azure resource deployments, specifically for container application management and infrastructure provisioning.

## Contents
- `fetch-container-image.bicep`: Bicep module that retrieves container configuration from existing Azure Container Apps
- `fetch-container-image.json`: Compiled ARM template version of the Bicep module for Azure deployment

## Usage
These modules are used in Azure infrastructure deployments:

```bicep
// Use the fetch-container-image module in other Bicep templates
module fetchContainer 'modules/fetch-container-image.bicep' = {
  name: 'fetchExistingContainer'
  params: {
    exists: true
    name: 'my-container-app'
  }
}

// Access the output
var containerConfig = fetchContainer.outputs.containers
```

The module helps with:
- Retrieving existing container configurations
- Enabling infrastructure updates without losing container settings
- Supporting blue-green deployments and container updates

## Container Configuration
This module specifically works with Azure Container Apps:
- Reads container template configurations from existing deployments
- Returns container array that can be used in new deployments
- Supports conditional logic based on whether the container app exists
- Compatible with Azure Container Apps API version 2023-05-02-preview

## Related Paths
- Incoming: Used by main infrastructure Bicep templates and Azure deployment scripts
- Outgoing: Queries Azure Container Apps service and returns container configurations for deployment
