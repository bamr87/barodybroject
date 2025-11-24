# Deployment Documentation

This directory contains comprehensive deployment documentation for the Barodybroject Django application.

## Contents

### Deployment Guides

- **[DEPLOYMENT-GUIDE-MINIMAL.md](./DEPLOYMENT-GUIDE-MINIMAL.md)** - Step-by-step minimal cost deployment guide
  - Prerequisites and setup
  - Docker image preparation
  - Azure environment configuration
  - Deployment commands
  - Troubleshooting common issues

- **[DEPLOYMENT-SUCCESS.md](./DEPLOYMENT-SUCCESS.md)** - Successful Azure Container Apps deployment report
  - Deployment timeline and results
  - Resource inventory
  - Testing procedures
  - Cost breakdown
  - Management commands
  - Monitoring setup

### Infrastructure Documentation

- **[INFRASTRUCTURE_CHANGES.md](./INFRASTRUCTURE_CHANGES.md)** - Comprehensive infrastructure evolution documentation
  - Port configuration standardization
  - Container Apps migration details
  - Cost-optimized templates
  - Deployment strategy evolution
  - Technical implementation details

### Troubleshooting

- **[QUOTA_ISSUE_SOLUTIONS.md](./QUOTA_ISSUE_SOLUTIONS.md)** - Azure subscription quota troubleshooting
  - Common quota issues
  - Solution options (quota increase, Container Apps, alternative platforms)
  - Cost comparisons
  - Alternative deployment strategies

## Quick Start

For your first deployment:

1. Review [DEPLOYMENT-GUIDE-MINIMAL.md](./DEPLOYMENT-GUIDE-MINIMAL.md) for prerequisites
2. Follow the step-by-step instructions
3. If you encounter quota issues, see [QUOTA_ISSUE_SOLUTIONS.md](./QUOTA_ISSUE_SOLUTIONS.md)
4. Verify deployment success using [DEPLOYMENT-SUCCESS.md](./DEPLOYMENT-SUCCESS.md) as reference

## Related Documentation

- [Migration Documentation](../migration/) - Database and application migrations
- [Infrastructure Testing](../INFRASTRUCTURE_TESTING.md) - Infrastructure validation
- [CI/CD Pipeline](../ci-cd-pipeline.md) - Continuous deployment setup

## Container-First Development

All deployment documentation follows the project's container-first development philosophy:
- All services run in Docker containers
- Development environment matches production
- No local dependency installation required
- Infrastructure as Code with Azure Bicep

## Cost Optimization

This project emphasizes minimal cost deployment:
- Burstable database tiers
- Basic service tiers where appropriate
- Container Apps consumption-based pricing
- Estimated cost: ~$25-37/month for production

For detailed cost analysis, see the cost sections in each deployment guide.
