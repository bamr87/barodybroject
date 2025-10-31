
# data Directory

## Purpose
This directory contains test data files including JSON fixtures, sample API responses, and mock data used for automated testing of the parodynews Django application. It provides realistic test data for validating models, API integrations, and data processing functionality without relying on external services during testing.

## Contents
- `Assistant-2024-10-22.json`: Test data for OpenAI Assistant API responses from October 2024
- `Assistant-2024-10-01.json`: Earlier version of Assistant API test data from October 2024
- `Assistant-2024-11-29.json`: Updated Assistant API test data from November 2024
- `OpenAIModel-2024-11-29.json`: Test data for OpenAI model configurations and capabilities
- `JSONSchema-2024-10-01.json`: JSON schema definitions for validating API request/response structures
- `DefaultValueConfig-2025-02-18.json`: Test configuration data for default values and application settings

## Usage
Test data files are loaded by pytest fixtures and test utilities:

```python
# Example test data usage
import json
from pathlib import Path

@pytest.fixture
def assistant_test_data():
    """Load Assistant API test data."""
    data_path = Path(__file__).parent / 'data' / 'Assistant-2024-11-29.json'
    with open(data_path, 'r') as f:
        return json.load(f)

@pytest.fixture  
def openai_model_data():
    """Load OpenAI model configuration test data."""
    data_path = Path(__file__).parent / 'data' / 'OpenAIModel-2024-11-29.json'
    with open(data_path, 'r') as f:
        return json.load(f)

# Example test using fixtures
def test_assistant_creation(assistant_test_data):
    """Test creating assistant from API response data."""
    assistant = Assistant.from_api_response(assistant_test_data)
    assert assistant.name == assistant_test_data['name']
    assert assistant.model == assistant_test_data['model']
```

Test data features:
- **Realistic API Responses**: Actual structure and content from OpenAI API calls
- **Version Evolution**: Multiple versions showing API changes over time
- **Schema Validation**: JSON schemas for ensuring data structure compliance
- **Configuration Testing**: Default value and settings validation data
- **Mock Service Responses**: Offline testing without external API dependencies
- **Date-Stamped Files**: Clear versioning and evolution tracking

## Container Configuration
Test data accessed within containerized test environment:
- JSON files included in test container builds
- Data files loaded during pytest execution
- Fixture data available for isolated test runs
- Version-controlled test data ensures consistent testing across environments

## Related Paths
- Incoming: Used by test fixtures and utilities in parent tests directory
- Outgoing: Provides mock data for testing models, views, and API integrations
