---
file: project.instructions.md
description: Project-level AI instructions for the barodybroject repository, defining standards and practices specific to this parody news generator project
author: AI-Seed Team <team@ai-seed.org>
created: 2025-07-19
lastModified: 2025-07-19
version: 1.0.0
relatedIssues: []
relatedEvolutions: []
dependencies:
  - space.instructions.md: Repository-wide foundational instructions
containerRequirements:
  baseImage: null
  exposedPorts: null
  volumes: null
  environment: null
  resources: null
  healthCheck: null
paths:
  project-setup-path: Guides initial project structure and configuration setup
  development-workflow-path: Defines coding, testing, and deployment patterns for this project
changelog:
  - date: 2025-07-19
    change: Initial creation
    author: AI-Seed Team
usage: Reference this file for project-specific development standards in the ai-seed repository
notes: This file extends space.instructions.md with project-specific guidance
---

# Project Instructions - Barodybroject Repository

The `barodybroject` repository is designed as a parody news generator using Django and OpenAI integration, emphasizing container-first development for Azure deployment.

## Project Overview

The `ai-seed` repository is designed as a foundational template for AI-assisted development projects, emphasizing:
- **Organic Growth**: Code and documentation evolve through AI-guided paths
- **Container-First Development**: All operations occur within isolated, reproducible environments
- **Path-Based Architecture**: Natural flow patterns guide development decisions
- **AI Agent Integration**: Multiple AI agents collaborate to enhance development workflows

## Project Structure and Organization

### Core Directories
- `src/`: Django source code and application logic
- `scripts/`: Automation and deployment scripts
- `infra/`: Azure Bicep infrastructure definitions
- `assets/`: Static assets and images
- `docs/`: Project documentation

### Path-Based File Organization
Files should be organized to follow natural usage patterns:
- **Execution Paths**: Scripts flow from setup → development → testing → deployment
- **Documentation Paths**: Information flows from general concepts → specific implementations
- **Code Paths**: Modules connect through clear dependency chains

## Development Workflow Paths

### Primary Development Path
1. **Environment Setup**: Create virtual environment and install dependencies from requirements.txt
2. **Database Migrations**: Run python manage.py migrate
3. **Feature Development**: Develop Django models, views, and templates
4. **Testing**: Run tests with pytest
5. **Deployment**: Deploy to Azure using Bicep and Container Apps

### AI Agent Integration Points
- **Code Generation**: Use AI for boilerplate, following established patterns
- **Path Optimization**: AI agents analyze and suggest workflow improvements
- **Documentation**: Automated generation with manual refinement
- **Testing**: AI-assisted test case generation and validation

## Container-Specific Requirements

### Development Environment
- **Base Image**: python:3.8-slim or as defined in Dockerfile
- **Development Stage**: Install dev requirements
- **Production Stage**: Use gunicorn for serving

### Testing Environment
- **Isolation**: Each test suite runs in isolated containers
- **Parallel Execution**: Multiple test containers for speed
- **Clean State**: Fresh containers for each test run
- **Reporting**: Centralized test result aggregation

## Code Quality Standards

### AI-Assisted Code Review
- **Pattern Recognition**: AI identifies code smells and suggests improvements
- **Best Practice Enforcement**: Automated checking against project standards
- **Path Analysis**: Ensure code follows optimal execution paths
- **Container Compatibility**: Verify all code works within container constraints

### Documentation Standards
- **Auto-Generation**: Use AI to generate initial documentation drafts
- **Path Documentation**: Every feature must document its execution paths
- **Container Context**: Include container-specific setup and usage information
- **Evolution Tracking**: Document how features evolve through AI iterations

## Testing Strategy

### Container-Based Testing
- **Unit Tests**: Test Django models and views in isolated environments
- **Integration Tests**: Test API endpoints and OpenAI integration
- **Container Testing**: Run tests in Docker containers matching production

### AI-Enhanced Testing
- **Test Generation**: AI creates test cases based on code analysis
- **Coverage Analysis**: AI identifies untested paths and suggests improvements
- **Mutation Testing**: AI generates code variants to test robustness
- **Regression Testing**: Automated detection of path degradation

## Deployment Patterns

### Container Orchestration
- **Local Development**: Docker Compose for multi-service development
- **Staging**: Kubernetes manifests for production-like testing
- **Production**: Optimized container images with minimal attack surface
- **Rollback Strategy**: Immutable deployments with quick rollback paths

### Path-Based Deployment
- **Blue-Green**: Parallel deployment paths for zero-downtime updates
- **Canary**: Gradual traffic shifting along new deployment paths
- **Feature Flags**: Runtime path selection for gradual feature rollouts
- **Health Monitoring**: Continuous path health validation

## Project-Specific Conventions

### Naming Conventions
- **Containers**: `ai-seed-[service]-[environment]` (e.g., `ai-seed-api-dev`)
- **Volumes**: `ai-seed-[purpose]` (e.g., `ai-seed-data`, `ai-seed-cache`)
- **Networks**: `ai-seed-[environment]` (e.g., `ai-seed-development`)
- **Images**: `ai-seed/[service]:[tag]` (e.g., `ai-seed/api:latest`)

### Environment Variables
- **AI_SEED_ENV**: Environment name (development, staging, production)
- **AI_SEED_LOG_LEVEL**: Logging verbosity (debug, info, warn, error)
- **AI_SEED_CONTAINER_REGISTRY**: Container registry URL for image storage
- **AI_SEED_PATH_MONITORING**: Enable/disable path performance monitoring

### Configuration Management
- **Environment-Specific**: Use `.env.[environment]` files for settings
- **Container Secrets**: Manage sensitive data through container secret stores
- **Path Configuration**: Define optimal paths through configuration files
- **AI Parameters**: Centralized configuration for AI agent behavior

## Integration with Other Instructions

This file works in conjunction with:
- **space.instructions.md**: Foundation principles and universal standards
- **language.instructions.md**: Language-specific implementation details
- **test.instructions.md**: Detailed testing strategies and frameworks
- **ci-cd.instructions.md**: Automation and deployment pipeline configurations
- **ai-agent.instructions.md**: AI agent behavior and integration patterns

## Future Evolution

### Planned Enhancements
- **Advanced Path Analytics**: Real-time development workflow optimization
- **Multi-AI Orchestration**: Coordination between specialized AI agents
- **Predictive Development**: AI-powered feature and bug prediction
- **Automated Architecture**: AI-suggested architectural improvements

### Adaptation Strategy
- **Feedback Loops**: Continuous collection of development experience data
- **Pattern Evolution**: Allow successful patterns to propagate naturally
- **Tool Integration**: Seamless adoption of emerging AI development tools
- **Knowledge Export**: Share learnings with the broader AI development community
