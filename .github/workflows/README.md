
# workflows Directory

## Purpose
This directory contains GitHub Actions workflow definitions that automate CI/CD, testing, deployment, code quality, and AI-enhanced development processes for the parody news generator. These workflows provide continuous integration, automated deployments to Azure, and AI-driven code evolution capabilities.

## Contents
- `azure-dev.yml`: Azure deployment workflow using Azure Developer CLI for infrastructure and application deployment
- `container.yml`: Container image building and publishing to container registries
- `cruft.yml`: Project template synchronization and updates using Cruft tool
- `daily-evolution.yml`: AI-powered daily code evolution and improvement automation
- `devcontainer-ci.yml`: Development container testing and validation workflow
- `format.yml`: Code formatting and style checking with Black, flake8, and other tools
- `jekyll-gh-pages.yml`: Jekyll static site building and deployment to GitHub Pages
- `monthly-evolution-report.yml`: Monthly AI-driven analysis and evolution reporting
- `openai-issue-processing.yml`: Automated issue processing and categorization using OpenAI
- `quarterly-major-evolution.yml`: Comprehensive quarterly AI-driven codebase evolution
- `tests.yml`: Django application testing including unit tests, integration tests, and coverage reporting
- `weekly-health-check.yml`: Automated health monitoring and system validation

## Usage
Workflows are automatically triggered by Git events and schedules:

```yaml
# Example trigger configuration
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

Workflow categories:
- **CI/CD**: Automated testing, building, and deployment to Azure
- **Code Quality**: Formatting, linting, and style enforcement
- **AI Evolution**: Automated code improvement and modernization
- **Health Monitoring**: System health checks and performance monitoring
- **Container Management**: Image building and registry publishing

## Container Configuration
Workflows utilize container environments:
- Build and test in consistent container environments
- Deploy containerized applications to Azure Container Apps
- Publish container images to Azure Container Registry
- Use development containers for CI/CD consistency

## Related Paths
- Incoming: Triggered by Git operations (push, PR, releases) and scheduled events
- Outgoing: Deploys to Azure infrastructure, publishes containers, updates code through AI evolution
