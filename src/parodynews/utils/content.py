"""
File: content.py
Description: Content-generation helpers built on OpenAI and JSON schemas
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- openai: >=1.57.0

Usage: from parodynews.utils.content import generate_content
"""

import logging

from .schemas import load_schemas, resolve_refs

logging.basicConfig(
    filename="assistant_responses.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Load all schemas and store them in module-level variables
all_schemas = load_schemas()
parody_schema = resolve_refs(all_schemas.get("parody_news_article_schema"))
content_detail_schema = resolve_refs(all_schemas.get("content_detail_schema"))


def generate_content(client, content_form):
    """
    Generate content using chat completions with optional JSON schema validation.

    Args:
        client: OpenAI client instance
        content_form: Content form object containing assistant and prompt

    Returns:
        tuple: (content, details) - generated content and metadata
    """
    model = content_form.assistant.model.model_id

    if content_form.assistant.json_schema is not None:
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "News_Article",
                "description": "A JSON object representing a news article.",
                "schema": content_form.assistant.json_schema.schema,
                "strict": True,
            },
        }
    else:
        response_format = None

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": content_form.assistant.instructions,
                    },
                ],
            },
            {
                "role": "user",
                "content": content_form.prompt,
            },
        ],
        response_format=response_format,
    )

    data = response.choices[0].message.content
    content_detail = generate_content_detail(client, data)

    logging.info("Response: %s", data, content_detail)

    return data, content_detail


def generate_content_detail(client, content):
    """
    Generate detailed content metadata using structured JSON schema.

    Args:
        client: OpenAI client instance
        content: Content text to analyze

    Returns:
        str: JSON string containing detailed content metadata
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "generate content detail",
                    },
                ],
            },
            {
                "role": "user",
                "content": content,
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Metadata",
                "description": "A JSON object representing details of a news article.",
                "schema": content_detail_schema,
                "strict": True,
            },
        },
    )

    data = response.choices[0].message.content
    logging.info("Response: %s", data)

    return data
