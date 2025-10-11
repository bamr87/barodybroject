
# scripts Directory

## Purpose
This directory contains test scripts and utilities for automated testing of specific functionality within the parodynews Django application. It provides specialized test scripts for API testing, user authentication, assistant management, and content creation workflows that complement the main test suite.

## Contents
- `test_user_login_or_create.py`: Test script for user authentication and account creation workflows
- `test_assistant_group_create.py`: Test script for creating and managing assistant groups and collections
- `test_assistant_create.py`: Test script for individual assistant creation and configuration
- `test_assistant_create_api.py`: Test script for assistant creation through API endpoints
- `test_content_create.py`: Test script for content generation and creation workflows
- `test_api.py`: General API testing script for endpoint validation and integration testing
- `__init__.py`: Python package initialization making this directory a test module
- `functions/`: Subdirectory containing reusable test functions and utilities (has its own README)
- `__pycache__/`: Subdirectory for Python bytecode cache (auto-generated)

## Usage
Test scripts are executed independently or as part of the test suite:

```bash
# Run individual test scripts
python src/parodynews/tests/scripts/test_api.py
python src/parodynews/tests/scripts/test_user_login_or_create.py

# Run all test scripts
python -m pytest src/parodynews/tests/scripts/

# Example test script structure
# test_assistant_create.py
import pytest
from django.test import TestCase
from parodynews.models import Assistant

class TestAssistantCreation(TestCase):
    def test_create_assistant_with_defaults(self):
        """Test creating assistant with default configuration."""
        assistant = Assistant.objects.create(
            name="Test Assistant",
            model="gpt-3.5-turbo"
        )
        assert assistant.name == "Test Assistant"
        assert assistant.is_active is True
    
    def test_create_assistant_api_endpoint(self):
        """Test assistant creation through API."""
        response = self.client.post('/api/assistants/', {
            'name': 'API Assistant',
            'model': 'gpt-4'
        })
        assert response.status_code == 201
```

Script features:
- **Focused Testing**: Each script tests specific functionality or workflow
- **API Integration**: Direct testing of REST API endpoints and responses
- **User Workflows**: End-to-end testing of user authentication and account management
- **Assistant Management**: Comprehensive testing of AI assistant creation and configuration
- **Content Generation**: Testing of content creation and OpenAI integration
- **Reusable Utilities**: Shared functions and helpers in the functions subdirectory

## Container Configuration
Test scripts execute within containerized test environment:
- Scripts run in Django test container with full application context
- Database transactions properly isolated for each test script
- OpenAI API mocking for offline testing capabilities
- Test results and coverage integrated with main test suite reporting

## Related Paths
- Incoming: Part of the comprehensive test suite validating application functionality
- Outgoing: Generates test results and validation reports for CI/CD pipelines and quality assurance
