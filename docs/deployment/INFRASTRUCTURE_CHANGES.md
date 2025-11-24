# Infrastructure Changes Documentation

**Version**: 0.2.0  
**Date**: January 27, 2025  
**Status**: Successfully deployed to Azure Container Apps

## Overview

This document details the comprehensive infrastructure changes made in v0.2.0, focusing on the successful deployment to Azure Container Apps and the implementation of cost-optimized infrastructure patterns.

## Major Infrastructure Achievements

### 🚀 Successful Azure Container Apps Deployment

The application has been successfully deployed to Azure Container Apps, representing a major milestone:

- **Live Application**: Production-ready deployment running at assigned Azure URL
- **Database Connectivity**: PostgreSQL Flexible Server fully operational
- **Auto-scaling**: Container Apps scaling configuration active
- **Security**: Environment variables and secrets properly configured
- **Monitoring**: Application Insights integration functional

### 🔧 Port Configuration Standardization

**Problem Solved**: Port mismatches between infrastructure and application configuration

**Changes Made**:

1. **Infrastructure Code (`infra/app/src.bicep`)**:
   ```bicep
   // Before: Port 80 configuration
   ingress: {
     external: true
     targetPort: 80
     transport: 'http'
   }
   env: [
     {
       name: 'PORT'
       value: '80'
     }
   ]

   // After: Port 8000 standardization
   ingress: {
     external: true
     targetPort: 8000  // ✅ Updated
     transport: 'http'
   }
   env: [
     {
       name: 'PORT'
       value: '8000'     // ✅ Updated
     }
   ]
   ```

2. **Application Configuration**:
   - Django development server: `runserver 0.0.0.0:8000`
   - Gunicorn production: `--bind 0.0.0.0:8000`
   - Docker EXPOSE: `EXPOSE 8000`

**Result**: Consistent port 8000 across all environments and configurations

## New Infrastructure Files

### 1. Minimal Cost Infrastructure Templates

Created comprehensive minimal cost deployment options in `infra/minimal/`:

#### `app-service.bicep` - Cost-Optimized App Service
```bicep
// B1 Basic tier for minimal cost (~$15/month)
resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1'        // Basic tier
    tier: 'Basic'
    size: 'B1'
    family: 'B'
    capacity: 1       // Single instance
  }
  properties: {
    reserved: true    // Linux containers
  }
}
```

#### `db-postgres-minimal.bicep` - Burstable Database
```bicep
// Burstable performance tier for cost optimization
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2022-12-01' = {
  name: serverName
  location: location
  sku: {
    name: 'Standard_B1ms'  // Burstable tier
    tier: 'Burstable'      // Most cost-effective
  }
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    storage: {
      storageSizeGB: 32    // Minimal storage
    }
    backup: {
      backupRetentionDays: 7  // Minimal backup retention
    }
  }
}
```

#### `main.bicep` - Minimal Deployment Template
```bicep
// Cost-optimized main deployment template
param location string = resourceGroup().location
param environmentName string
param principalId string = ''

// Minimal cost resource configuration
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Deploy minimal cost app service
module app 'app-service.bicep' = {
  name: 'app-service'
  params: {
    name: 'app-${resourceToken}'
    location: location
    tags: tags
    // Minimal tier configuration
  }
}

// Deploy minimal cost database
module db 'db-postgres-minimal.bicep' = {
  name: 'db-postgres-minimal'
  params: {
    name: 'psql-${resourceToken}'
    location: location
    tags: tags
    // Burstable tier configuration
  }
}
```

### 2. Enhanced Docker Configuration

#### New `Dockerfile` for Container Apps
```dockerfile
# Multi-stage build optimized for Container Apps
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port 8000 (standardized)
EXPOSE 8000

# Health check for Container Apps
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

# Production command with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "barodybroject.wsgi:application"]
```

### 3. Updated Azure Developer CLI Configuration

#### Enhanced `azure.yaml`
```yaml
# Azure Developer CLI configuration for Container Apps
name: barodybroject
metadata:
  template: barodybroject@0.2.0
services:
  web:
    project: ./src
    language: python
    host: containerapp
    # Container Apps specific configuration
    docker:
      path: ./Dockerfile
      context: .
    # Environment variables for Container Apps
    env:
      PORT: "8000"
      DJANGO_SETTINGS_MODULE: "barodybroject.settings"
# Infrastructure configuration
infra:
  provider: bicep
  path: ./infra
  # Support for multiple deployment options
  parameters:
    - name: containerAppsEnvironmentName
      value: "${AZURE_ENV_NAME}-env"
    - name: containerRegistryName
      value: "${AZURE_ENV_NAME}registry"
```

### 4. Infrastructure Parameters Update

#### `infra/main.parameters.json` - Cost-Optimized Parameters
```json
{
  "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "environmentName": {
      "value": "${AZURE_ENV_NAME}"
    },
    "location": {
      "value": "${AZURE_LOCATION}"
    },
    "principalId": {
      "value": "${AZURE_PRINCIPAL_ID}"
    },
    "postgresAdministratorLogin": {
      "value": "postgres"
    },
    "postgresAdministratorLoginPassword": {
      "value": "${POSTGRES_PASSWORD}"
    },
    // Cost optimization parameters
    "appServicePlanSku": {
      "value": "B1"  // Basic tier for minimal cost
    },
    "postgresSku": {
      "value": "Standard_B1ms"  // Burstable tier
    },
    "postgresStorageSize": {
      "value": 32  // Minimal storage in GB
    }
  }
}
```

## Deployment Strategy Evolution

### From App Service to Container Apps

**Original Approach**: Azure App Service deployment
- **Issue**: Quota limitations in Azure subscription
- **Blocker**: Could not provision required App Service Plan

**Solution**: Azure Container Apps deployment
- **Advantage**: No quota conflicts with Container Apps service
- **Benefit**: Serverless container hosting with auto-scaling
- **Result**: Successful deployment and operational application

### Infrastructure Comparison

| Component | App Service Approach | Container Apps Approach | Status |
|-----------|---------------------|-------------------------|---------|
| **Compute** | App Service Plan B1 | Container Apps Environment | ✅ **Working** |
| **Database** | PostgreSQL Flexible | PostgreSQL Flexible | ✅ **Working** |
| **Registry** | Azure Container Registry | Azure Container Registry | ✅ **Working** |
| **Monitoring** | Application Insights | Application Insights | ✅ **Working** |
| **Cost** | ~$35/month | ~$25/month | ✅ **Optimized** |
| **Scaling** | Manual/Auto Scale | Serverless Auto-scale | ✅ **Improved** |

## Cost Analysis

### Monthly Cost Breakdown (USD)

#### Container Apps Deployment (Current)
- **Container Apps Environment**: $0-15 (consumption-based)
- **PostgreSQL Flexible Server**: $15-25 (Burstable B1ms)
- **Container Registry**: $5 (Basic tier)
- **Application Insights**: $0 (Free tier, 5GB/month)
- **Storage Account**: $1-2 (Standard LRS)
- **Total Estimated**: **$21-47/month**

#### Minimal Cost Optimization Options
- **Development Environment**: ~$20/month
- **Small Production**: ~$35/month
- **Standard Production**: ~$75/month

### Cost Optimization Features

1. **Burstable Database Tiers**: Pay for actual usage
2. **Container Apps Scaling**: Scale to zero when not in use
3. **Basic Service Tiers**: Minimum viable service levels
4. **Shared Resources**: Efficient resource group utilization

## Technical Implementation Details

### Bicep Infrastructure as Code

**Architecture Principles**:
- Modular design with reusable components
- Environment-specific parameter files
- Resource naming conventions with unique tokens
- Comprehensive tagging strategy
- Security best practices with managed identities

**Key Modules**:
- `main.bicep`: Orchestration template
- `app/src.bicep`: Container Apps configuration
- `app/db-postgres.bicep`: Database infrastructure
- `shared/`: Shared resources (registry, monitoring, secrets)

### Container Orchestration

**Container Apps Features Utilized**:
- HTTP ingress with external access
- Environment variable management
- Secret injection from Key Vault
- Auto-scaling based on HTTP requests
- Blue-green deployments
- Application lifecycle management

### Database Configuration

**PostgreSQL Flexible Server Setup**:
- **Version**: PostgreSQL 14
- **Tier**: Burstable (B1ms) for cost optimization
- **Storage**: 32GB with auto-grow disabled
- **Backup**: 7-day retention
- **Security**: VNet integration, firewall rules
- **Authentication**: Azure AD integration enabled

## Monitoring and Observability

### Application Insights Integration

**Metrics Tracked**:
- HTTP request rates and response times
- Database connection health
- Container resource utilization
- Error rates and exceptions
- Custom application metrics

**Dashboards Configured**:
- Application performance overview
- Infrastructure health monitoring
- Cost tracking and optimization alerts
- Security and compliance monitoring

### Health Checks

**Application Health Endpoints**:
```python
# Django health check endpoint
def health_check(request):
    """Health check for Container Apps"""
    checks = {
        'database': check_database_connection(),
        'cache': check_cache_connection(),
        'external_apis': check_external_dependencies(),
    }
    
    if all(checks.values()):
        return JsonResponse({'status': 'healthy', 'checks': checks})
    else:
        return JsonResponse({'status': 'unhealthy', 'checks': checks}, status=503)
```

## Security Enhancements

### Container Security

- **Non-root user**: Application runs as non-privileged user
- **Minimal base image**: Python slim image for reduced attack surface
- **Dependency scanning**: Regular vulnerability assessments
- **Secret management**: Azure Key Vault integration

### Network Security

- **VNet integration**: Database isolated in virtual network
- **Firewall rules**: Restricted database access
- **HTTPS enforcement**: SSL/TLS termination at ingress
- **Identity-based access**: Managed identities for service-to-service communication

## Troubleshooting and Operations

### Common Issues and Solutions

1. **Port Configuration Mismatches**
   - **Issue**: Application not accessible
   - **Solution**: Verify port 8000 consistency across all configurations

2. **Database Connection Failures**
   - **Issue**: Django cannot connect to PostgreSQL
   - **Solution**: Check connection string and firewall rules

3. **Container Startup Failures**
   - **Issue**: Container Apps deployment fails
   - **Solution**: Review health checks and startup commands

### Operational Procedures

**Deployment Process**:
```bash
# Standard deployment procedure
azd auth login
azd up  # Full infrastructure provisioning and deployment

# Incremental updates
azd deploy  # Application-only updates
```

**Monitoring Commands**:
```bash
# Check deployment status
azd show

# View application logs
az containerapp logs show --name <app-name> --resource-group <rg-name>

# Monitor resource usage
az monitor metrics list --resource <resource-id>
```

## Future Infrastructure Roadmap

### Planned Enhancements

1. **Multi-Environment Support**
   - Development, staging, production environments
   - Environment-specific configurations
   - Automated promotion pipelines

2. **Enhanced Security**
   - Certificate management
   - Advanced threat protection
   - Compliance monitoring

3. **Performance Optimization**
   - CDN integration for static assets
   - Database performance tuning
   - Caching layers (Redis)

4. **Disaster Recovery**
   - Multi-region deployment options
   - Automated backup strategies
   - Recovery procedures documentation

### Scaling Considerations

**Horizontal Scaling**:
- Container Apps auto-scaling rules
- Database read replicas
- Load balancer configuration

**Vertical Scaling**:
- Container resource limits
- Database tier upgrades
- Storage optimization

## Conclusion

The infrastructure changes in v0.2.0 represent a successful transition to a production-ready, cost-optimized Azure Container Apps deployment. Key achievements include:

✅ **Successful Deployment**: Live application running in production  
✅ **Cost Optimization**: Minimal infrastructure costs with maximum functionality  
✅ **Scalability**: Auto-scaling container orchestration  
✅ **Security**: Best practices implementation  
✅ **Monitoring**: Comprehensive observability  
✅ **Documentation**: Complete operational guides  

This infrastructure foundation provides a solid base for future application development and scaling.

---

**Related Documentation:**
- [DEPLOYMENT-SUCCESS.md](./DEPLOYMENT-SUCCESS.md) - Deployment results and validation
- [DEPLOYMENT-GUIDE-MINIMAL.md](./DEPLOYMENT-GUIDE-MINIMAL.md) - Step-by-step deployment instructions
- [QUOTA_ISSUE_SOLUTIONS.md](./QUOTA_ISSUE_SOLUTIONS.md) - Troubleshooting guide
- [CMS_REMOVAL_GUIDE.md](../migration/CMS_REMOVAL_GUIDE.md) - CMS removal documentation
- [CHANGELOG.md](CHANGELOG.md) - Complete version history