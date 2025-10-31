
# scripts Directory

## Purpose
This directory contains utility scripts and management tools specific to the parodynews Django application. These scripts provide specialized functionality for content management, testing workflows, and administrative tasks that support the parody news generation system.

## Contents
- `manage_content_test.py`: Python script for testing and managing content creation workflows, validation, and data processing
- `__pycache__/`: Subdirectory for Python bytecode cache (auto-generated)

## Usage
Scripts are executed for content management and testing:

```bash
# Run content management test script
python src/parodynews/scripts/manage_content_test.py

# Example script functionality
python src/parodynews/scripts/manage_content_test.py \
    --test-content-creation \
    --validate-openai-integration \
    --check-database-connections
```

Script features:
- **Content Testing**: Validation of content creation and generation workflows
- **Integration Testing**: Testing of OpenAI API integration and response handling
- **Database Management**: Content database operations and data validation
- **Workflow Validation**: End-to-end testing of content publishing processes
- **Administrative Tools**: Utilities for managing content lifecycle and system health

## Container Configuration
Scripts execute within Django application container:
- Full access to Django models and database connections
- OpenAI API integration available for content generation testing
- Container environment variables and configuration accessible
- Script output and logging integrated with application logging system

## Related Paths
- Incoming: Provides utilities for managing and testing content within the parodynews application
- Outgoing: Generates content validation reports and administrative task results
