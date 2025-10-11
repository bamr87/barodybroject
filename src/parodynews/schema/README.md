
# schema Directory

## Purpose
This directory contains JSON schemas and prompt templates that define the structure and format for AI-generated parody news content. These schemas ensure consistent data formats for content creation and validation, while the prompt templates guide the OpenAI integration for generating satirical articles.

## Contents
- `content_detail_schema.json`: JSON schema defining the structure for detailed content objects including headers, author information, and publication metadata
- `news_article_schema.json`: JSON schema for standard news article format and structure validation
- `parody_news_article_schema.json`: Specialized schema for parody news articles with fields specific to satirical content generation
- `parody_prompt.md`: Detailed prompt template and style guide for AI content generation, defining tone, structure, and content guidelines for satirical news creation

## Usage
Schemas are used for data validation and content generation:

```python
# In Django models/forms for validation
import json
import jsonschema

def validate_content_structure(content_data):
    with open('parodynews/schema/content_detail_schema.json') as f:
        schema = json.load(f)
    jsonschema.validate(content_data, schema)

# In OpenAI integration for content generation
def generate_parody_article(topic):
    with open('parodynews/schema/parody_prompt.md') as f:
        prompt_template = f.read()
    
    # Use prompt with OpenAI API
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": prompt_template}]
    )
```

Key features:
- **JSON Schema validation**: Ensures generated content matches expected format
- **Structured data format**: Defines author, publication date, content fields
- **Prompt engineering**: Detailed style guide for satirical content generation
- **Content consistency**: Maintains format standards across generated articles

## Container Configuration
Schemas are loaded as static files within the Django application:
- Read during content generation and validation processes
- Cached for performance in production environments
- Version controlled for consistency across deployments

## Related Paths
- Incoming: Used by content generation views and OpenAI integration modules
- Outgoing: Validates data structure for database storage and API responses
