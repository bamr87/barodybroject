
# .github Directory

## Purpose
This directory contains GitHub-specific configuration files that control repository behavior, CI/CD workflows, issue templates, and development tools integration. It provides automated workflows for building, testing, and deploying the parody news generator application along with development guidelines and contributor support.

## Contents
- `ISSUE_TEMPLATE/`: GitHub issue templates for bug reports, feature requests, and other standardized issue types
- `copilot-instructions.md`: Comprehensive AI-powered development guidelines and coding standards for GitHub Copilot integration
- `instructions/`: Additional development and contribution guidelines for maintaining code quality and consistency
- `workflows/`: GitHub Actions workflow definitions for CI/CD, automated testing, and deployment pipelines

## Usage
GitHub configuration files are automatically recognized and used by GitHub:

```yaml
# Example workflow trigger
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# Container build and deployment
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build container
        run: docker build -t barodybroject .
```

Key features:
- **Automated CI/CD**: Container builds, tests, and deployments
- **Code Quality**: Linting, testing, and security scanning
- **Issue Management**: Standardized templates for community contributions
- **Development Guidelines**: AI-assisted coding standards and best practices
- **Container Registry**: Automated image publishing to container registries

## Container Configuration
GitHub Actions workflows build and deploy containers:
- Multi-stage Docker builds for development and production
- Container registry integration for image storage
- Azure Container Apps deployment automation
- Environment-specific configuration management

## Related Paths
- Incoming: Triggered by Git operations (push, pull requests, releases)
- Outgoing: Deploys containers to Azure and updates container registries
