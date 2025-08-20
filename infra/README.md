# infra/ Directory

## Purpose
This directory contains Azure infrastructure as code using Bicep templates.

## Contents
- `abbreviations.json`: Abbreviations used in naming
- `app/`: Application-specific Bicep files
- `main.bicep`: Main infrastructure template
- `main.parameters.json`: Parameters for main template
- `modules/`: Reusable Bicep modules
- `shared/`: Shared infrastructure components

## Usage
Deploy using Azure CLI: az deployment group create --resource-group <rg> --template-file main.bicep

## Container Configuration
Not directly applicable, but defines container app environments.

## Related Paths
- Incoming: From scripts/azure-deployment-setup.py
- Outgoing: To Azure deployment
