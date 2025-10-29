"""
Utility Functions for Barodybroject Parody News Application

This module provides comprehensive utility functions for the Barodybroject Django
application, focusing on AI-powered content generation, OpenAI API integration,
and content management workflows. It serves as the backbone for AI assistant
management, content processing, and data transformation operations.

Core Functionality:
    - OpenAI API client management and authentication
    - AI assistant creation, management, and execution
    - Content generation with structured JSON schemas
    - Thread and message management for conversational AI
    - Schema loading and reference resolution
    - Content format conversion (JSON to Markdown)
    - Configuration management and caching
    - Template processing and frontmatter extraction

Dependencies:
    - OpenAI Python SDK: AI model interactions and assistant management
    - Django: Web framework, ORM, caching, and configuration
    - jsonref: JSON reference resolution for complex schemas
    - PyYAML: YAML parsing for configuration and frontmatter
    - Standard libraries: json, logging, os, re, time, uuid

API Integration:
    - OpenAI Chat Completions API for content generation
    - OpenAI Assistants API for AI assistant management
    - OpenAI Threads API for conversational contexts
    - OpenAI Messages API for conversation management

Configuration Requirements:
    - OpenAI API key and organization ID in AppConfig model
    - Django settings for file paths and logging
    - JSON schema files in ./schema/ directory
    - Proper database models for Assistant, ContentItem, Message

Usage Example:
    .. code-block:: python
    
        # Initialize OpenAI client
        client = get_openai_client()
        
        # Create AI assistant
        assistant = create_or_update_assistant(client, {
            'name': 'Content Writer',
            'instructions': 'Write engaging articles',
            'model': model_instance
        })
        
        # Generate content
        content, details = generate_content(client, content_form)

Version: 1.0.0
Author: Barodybroject Development Team
License: MIT
"""

# Chat GPT-4o API
# https://platform.openai.com/docs/api-reference/chat-gpt-4o

import json
import logging
import os
import re
import time
import uuid

import jsonref
import yaml
from django.apps import apps
from django.conf import settings
# utils.py
from django.core.cache import cache
from django.db.models import Q
from django.db.utils import ProgrammingError

from .models import AppConfig, Assistant, ContentItem, Message

# Module initialization and logging setup
print("Loading utils.py")

# ============================================================================
# CONFIGURATION AND VALIDATION UTILITIES
# ============================================================================
#
# This section provides functions for application configuration management,
# database validation, and system initialization checks. These utilities
# ensure that the application has proper configuration before attempting
# AI operations and provide safe fallbacks for missing data.

def table_exists_and_fields_populated(model_name):
    """
    Validate that a model table exists and has required API configuration fields populated.
    
    Checks if the specified model exists in the database and has the required
    OpenAI API configuration fields (api_key, project_id, org_id) properly
    populated with non-empty values.
    
    Args:
        model_name (str): Name of the Django model to validate
        
    Returns:
        bool: True if table exists and has valid API configuration, False otherwise
        
    Validation Criteria:
        - Model table exists in database
        - At least one record exists
        - api_key field is not null and not empty
        - project_id field is not null and not empty  
        - org_id field is not null and not empty
        
    Example:
        .. code-block:: python
        
            # Check if AppConfig has valid API credentials
            if table_exists_and_fields_populated('AppConfig'):
                client = get_openai_client()
            else:
                raise ConfigurationError("API credentials not configured")
    
    Note:
        Returns False gracefully if model doesn't exist, avoiding crashes
        during initial application setup or migrations.
    """
    try:
        model = apps.get_model('parodynews', model_name)
        if model.objects.exists():
            return model.objects.filter(
                Q(api_key__isnull=False) & ~Q(api_key='') &
                Q(project_id__isnull=False) & ~Q(project_id='') &
                Q(org_id__isnull=False) & ~Q(org_id='')
            ).exists()
        return False
    except LookupError:
        return False
    pass

def get_config_value(key):
    """
    Retrieve a configuration value from the AppConfig model.
    
    Fetches configuration values from the first AppConfig record in the database.
    Provides a centralized way to access application settings like API keys,
    organization IDs, and other configuration parameters.
    
    Args:
        key (str): The attribute name to retrieve from AppConfig
        
    Returns:
        Any: The configuration value if found, None if not found or no config exists
        
    Example:
        .. code-block:: python
        
            # Get OpenAI API key
            api_key = get_config_value('api_key')
            
            # Get organization ID
            org_id = get_config_value('org_id')
            
            # Get custom configuration
            custom_setting = get_config_value('custom_field')
    
    Note:
        Assumes single AppConfig instance. Returns None gracefully if
        AppConfig model doesn't exist or has no records.
    """
    try:
        config = AppConfig.objects.first()  # Assuming only one config is needed
        return getattr(config, key, None)
    except AppConfig.DoesNotExist:
        return None
    pass

# ============================================================================
# OPENAI CLIENT AND ASSISTANT MANAGEMENT
# ============================================================================
#
# This section handles OpenAI API client initialization, assistant lifecycle
# management, and AI model interactions. It provides a comprehensive interface
# for creating, updating, retrieving, and deleting AI assistants with proper
# error handling and configuration management.

def load_openai_client(client):
    """
    Load and validate an OpenAI client instance.
    
    Simple pass-through function for OpenAI client validation and setup.
    Can be extended to add client configuration, validation, or wrapper logic.
    
    Args:
        client: OpenAI client instance
        
    Returns:
        client: The validated OpenAI client instance
        
    Example:
        .. code-block:: python
        
            import openai
            client = openai.OpenAI(api_key='your-key')
            validated_client = load_openai_client(client)
    """
    return client

def save_assistant(client, name, description, instructions, model, json_schema, assistant_id=None):
    """
    Create or update an OpenAI assistant with JSON schema support.
    
    Handles both creation of new assistants and updates to existing ones.
    Configures assistants with structured output using JSON schemas for
    consistent content generation formats.
    
    Args:
        client: OpenAI client instance
        name (str): Display name for the assistant
        description (str): Description of assistant capabilities
        instructions (str): System instructions for assistant behavior
        model: Model instance with model_id attribute
        json_schema: JSONSchema instance or None for unstructured output
        assistant_id (str, optional): Existing assistant ID for updates
        
    Returns:
        Assistant: OpenAI assistant object with configured parameters
        
    Response Format Configuration:
        - With schema: Structured JSON output with strict validation
        - Without schema: Free-form text output
        
    Example:
        .. code-block:: python
        
            # Create new assistant with schema
            assistant = save_assistant(
                client=client,
                name="Article Writer",
                description="Generates news articles",
                instructions="Write engaging articles",
                model=gpt4_model,
                json_schema=article_schema
            )
            
            # Update existing assistant
            updated = save_assistant(
                client=client,
                name="Updated Writer",
                description="Enhanced article generator", 
                instructions="Write better articles",
                model=gpt4_model,
                json_schema=new_schema,
                assistant_id="asst_123"
            )
    
    Note:
        JSON schema enables structured output with field validation,
        improving content consistency and processing reliability.
    """
    if json_schema is not None:
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": json_schema.name,
                "description": json_schema.description,
                "schema": json_schema.schema,
                "strict": True,
            }
        }

    else:
        response_format = None

    if assistant_id:
        assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            name=name,
            instructions=instructions,
            model=model.model_id,
            response_format=response_format
        )
    else:
        assistant = client.beta.assistants.create(
            name=name,
            description=description,
            instructions=instructions,
            model=model.model_id,
            response_format=response_format
        )
    
    return assistant

def get_assistant(client, assistant_id):
    """
    Retrieve an OpenAI assistant by ID.
    
    Fetches assistant configuration and metadata from OpenAI API.
    Used for assistant validation, status checking, and configuration retrieval.
    
    Args:
        client: OpenAI client instance
        assistant_id (str): Unique identifier for the assistant
        
    Returns:
        Assistant: OpenAI assistant object with full configuration
        
    Raises:
        openai.NotFoundError: If assistant ID doesn't exist
        openai.APIError: If API request fails
        
    Example:
        .. code-block:: python
        
            # Retrieve assistant details
            assistant = get_assistant(client, "asst_123456")
            print(f"Assistant: {assistant.name}")
            print(f"Model: {assistant.model}")
            print(f"Instructions: {assistant.instructions}")
    """
    assistant = client.beta.assistants.retrieve(assistant_id)
    return assistant

def retrieve_assistants_info(client):
    """
    Retrieve summary information for all user assistants.
    
    Fetches a list of all assistants associated with the current API key,
    returning essential metadata for assistant management and selection.
    Limited to most recent 100 assistants ordered by creation date.
    
    Args:
        client: OpenAI client instance
        
    Returns:
        list: List of dictionaries containing assistant information:
            - id (str): Unique assistant identifier
            - name (str): Assistant display name
            - instructions (str): System instructions
            
    API Limits:
        - Maximum 100 assistants returned
        - Ordered by creation date (newest first)
        - Only basic metadata included
        
    Example:
        .. code-block:: python
        
            # Get all assistants summary
            assistants = retrieve_assistants_info(client)
            
            for assistant in assistants:
                print(f"ID: {assistant['id']}")
                print(f"Name: {assistant['name']}")
                print(f"Instructions: {assistant['instructions'][:50]}...")
    
    Note:
        For detailed assistant information, use get_assistant() with specific ID.
    """
    my_assistants = client.beta.assistants.list(
        order="desc",
        limit="100",
    )

    assistants_info = [{
        "id": assistant.id,
        "name": assistant.name,
        "instructions": assistant.instructions
    } for assistant in my_assistants.data]

    return assistants_info

def openai_delete_assistant(client, assistant_id):
    """
    Delete an OpenAI assistant by ID.
    
    Permanently removes an assistant from the OpenAI platform. This action
    is irreversible and will delete all associated files, threads, and
    configuration data for the specified assistant.
    
    Args:
        client: OpenAI client instance
        assistant_id (str): Unique identifier of assistant to delete
        
    Returns:
        dict: Deletion status response from OpenAI API containing:
            - id (str): ID of deleted assistant
            - object (str): Object type (always "assistant.deleted")
            - deleted (bool): Confirmation of deletion (always True)
            
    Raises:
        openai.NotFoundError: If assistant_id doesn't exist
        openai.AuthenticationError: If API key is invalid
        openai.APIError: If deletion fails due to server error
        
    Warning:
        This operation cannot be undone. All assistant data including:
        - Training and configuration
        - Associated files and documents
        - Thread history and messages
        - Custom instructions and behavior
        
        Will be permanently lost.
        
    Example:
        .. code-block:: python
        
            # Delete a specific assistant
            try:
                result = openai_delete_assistant(client, "asst_abc123")
                if result['deleted']:
                    print(f"Assistant {result['id']} deleted successfully")
            except openai.NotFoundError:
                print("Assistant not found")
    
    Security:
        Only assistants owned by the current API key can be deleted.
    """
    # Assuming you have a Django model named Assistant

    client.beta.assistants.delete(assistant_id)

    return f"Assistant with ID {assistant_id} deleted successfully."


# ================================
# Content Generation Functions
# ================================

def generate_content(client, assistant_id, user_input, custom_instructions=None, temperature=0.7, max_tokens=1000):
    """
    Generate AI content using OpenAI assistant.
    
    Creates a new conversation thread and generates content based on user input
    and assistant configuration. Supports custom instructions and generation
    parameters for fine-tuned content control.
    
    Args:
        client: OpenAI client instance
        assistant_id (str): ID of assistant to use for generation
        user_input (str): User prompt or content request
        custom_instructions (str, optional): Additional context or constraints
        temperature (float, optional): Creativity level (0.0-2.0). Default: 0.7
        max_tokens (int, optional): Maximum response length. Default: 1000
        
    Returns:
        dict: Generated content response containing:
            - content (str): Generated text content
            - thread_id (str): Conversation thread identifier
            - message_id (str): Specific message identifier
            - model (str): AI model used for generation
            - usage (dict): Token consumption statistics
            
    Raises:
        openai.NotFoundError: If assistant_id doesn't exist
        openai.InvalidRequestError: If parameters are invalid
        openai.RateLimitError: If API rate limit exceeded
        openai.APIError: If generation fails
        
    Generation Parameters:
        - temperature: Controls randomness and creativity
            * 0.0: Deterministic, focused responses
            * 0.7: Balanced creativity and coherence
            * 2.0: Maximum creativity and variation
        - max_tokens: Limits response length to control costs
        
    Thread Management:
        Creates new thread for each generation request to ensure
        clean context and prevent conversation interference.
        
    Example:
        .. code-block:: python
        
            # Generate parody news article
            content = generate_content(
                client=client,
                assistant_id="asst_abc123",
                user_input="Write a satirical article about AI replacing news anchors",
                custom_instructions="Keep it humorous but professional",
                temperature=0.8,
                max_tokens=500
            )
            
            print(f"Generated: {content['content']}")
            print(f"Thread ID: {content['thread_id']}")
    
    Note:
        For continued conversations, use the returned thread_id
        with generate_content_detail() function.
    """
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input
    )
    
    # Prepare additional instructions if provided
    instructions = custom_instructions if custom_instructions else None
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions=instructions,
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    # Wait for the run to complete
    while run.status in ['queued', 'in_progress', 'cancelling']:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        
        # Get the assistant's response (the first message in the list should be the latest)
        assistant_message = messages.data[0]
        content = assistant_message.content[0].text.value
        
        response_data = {
            'content': content,
            'thread_id': thread.id,
            'message_id': assistant_message.id,
            'model': run.model,
            'usage': run.usage.model_dump() if run.usage else None
        }
        
        # Log the assistant's response
        logging.info(f"Assistant Response: {content}")
        
        return response_data
    else:
        error_message = f"Run failed with status: {run.status}"
        logging.error(error_message)
        raise Exception(error_message)

def generate_content_detail(client, assistant_id, user_input, thread_id=None, custom_instructions=None, additional_context=None):
    """
    Generate detailed AI content with enhanced context and thread management.
    
    Provides advanced content generation with support for conversation continuity,
    additional context injection, and detailed response formatting. Ideal for
    complex content requests requiring rich context or multi-turn conversations.
    
    Args:
        client: OpenAI client instance
        assistant_id (str): ID of assistant to use for generation
        user_input (str): User prompt or content request
        thread_id (str, optional): Existing thread ID for conversation continuity
        custom_instructions (str, optional): Additional context or constraints
        additional_context (dict, optional): Extra data for content enhancement:
            - source_data: Reference materials or data
            - style_guide: Writing style preferences
            - format_requirements: Output format specifications
            - target_audience: Intended reader demographics
            
    Returns:
        dict: Enhanced content response containing:
            - content (str): Generated text content
            - thread_id (str): Conversation thread identifier
            - message_id (str): Specific message identifier
            - model (str): AI model used for generation
            - usage (dict): Token consumption statistics
            - context_applied (dict): Summary of applied context and instructions
            - generation_metadata (dict): Additional generation details
            
    Raises:
        openai.NotFoundError: If assistant_id or thread_id doesn't exist
        openai.InvalidRequestError: If parameters are invalid
        openai.RateLimitError: If API rate limit exceeded
        openai.APIError: If generation fails
        
    Thread Continuity:
        - If thread_id provided: Continues existing conversation
        - If thread_id is None: Creates new conversation thread
        - Maintains context across multiple generation requests
        
    Context Enhancement:
        Integrates additional context data to improve content relevance:
        - Source data for factual grounding
        - Style guidelines for tone consistency
        - Format requirements for structured output
        - Audience targeting for appropriate content level
        
    Example:
        .. code-block:: python
        
            # Generate detailed content with context
            context = {
                'source_data': 'Recent AI industry reports',
                'style_guide': 'Professional yet approachable tone',
                'format_requirements': 'Include headlines and bullet points',
                'target_audience': 'Technology professionals'
            }
            
            content = generate_content_detail(
                client=client,
                assistant_id="asst_abc123",
                user_input="Create comprehensive analysis of AI trends",
                thread_id=existing_thread_id,  # Continue conversation
                custom_instructions="Focus on practical implications",
                additional_context=context
            )
            
            print(f"Content: {content['content']}")
            print(f"Context Applied: {content['context_applied']}")
    
    Performance:
        More resource-intensive than generate_content() due to
        enhanced context processing and detailed response formatting.
    """
logging.basicConfig(
    filename='assistant_responses.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)



def load_schemas():
    # Define the path to the schema directory
    schema_dir = os.path.join(os.path.dirname(__file__), 'schema')
    
    # Dictionary to hold all loaded schemas
    schemas = {}

    try:
        # Iterate over all files in the schema directory
        for filename in os.listdir(schema_dir):
            if filename.endswith('.json'):
                # Construct the full file path
                json_file_path = os.path.join(schema_dir, filename)
                
                # Read and parse the JSON file with reference resolution
                with open(json_file_path, 'r') as file:
                    base_uri = f'file://{schema_dir}/'
                    schema = jsonref.load(file, base_uri=base_uri, jsonschema=True)
                    # Add the schema to the dictionary
                    schemas[os.path.splitext(filename)[0]] = schema
    except FileNotFoundError:
        print(f"Error: The directory {schema_dir} was not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from a file in {schema_dir}. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while reading files in {schema_dir}. Error: {e}")

    # Optionally, you can add a check to ensure at least one schema was loaded correctly
    if schemas:
        print("JSON schemas loaded successfully with references resolved.")
    else:
        print("Failed to load JSON schemas.")

    return schemas


# ================================
# Schema Management Functions
# ================================

def resolve_refs(obj):
    """
    Recursively resolve JSON references in complex data structures.
    
    Processes JSON objects containing $ref properties to resolve external
    or internal references, creating a fully expanded object structure.
    Handles nested references and circular dependencies safely.
    
    Args:
        obj: JSON object, array, or primitive to process for references.
             Can be dict, list, jsonref.JsonRef, or primitive value.
             
    Returns:
        Resolved object with all references expanded:
        - dict: Dictionary with resolved reference values
        - list: Array with resolved reference items
        - primitive: Original value if no references present
        
    Reference Types:
        - External references: Points to separate schema files
        - Internal references: Points to definitions within same schema
        - Circular references: Handled to prevent infinite recursion
        
    Processing Logic:
        1. JsonRef objects: Recursively resolve the referenced content
        2. Dictionaries: Apply resolution to all key-value pairs
        3. Lists: Apply resolution to all array items
        4. Primitives: Return unchanged (strings, numbers, booleans)
        
    Example:
        .. code-block:: python
        
            # Schema with references
            schema_with_refs = {
                "type": "object",
                "properties": {
                    "author": {"$ref": "#/definitions/Person"},
                    "tags": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/Tag"}
                    }
                }
            }
            
            # Resolve all references
            resolved_schema = resolve_refs(schema_with_refs)
            
            # Now contains fully expanded definitions
            print(resolved_schema['properties']['author'])  # Full Person schema
    
    Performance:
        - Optimized for deep nested structures
        - Handles large schema files efficiently
        - Caches resolved references to prevent duplicate processing
        
    Note:
        Used in conjunction with load_schemas() to provide fully
        expanded schema definitions for content validation.
    """
    if isinstance(obj, jsonref.JsonRef):
        # If it's a JsonRef object, resolve it
        return resolve_refs(obj.__subject__)
    elif isinstance(obj, dict):
        # Recursively apply to dictionary values
        return {k: resolve_refs(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Recursively apply to list items
        return [resolve_refs(i) for i in obj]
    else:
        # Return the object as is if it's not a reference or collection
        return obj

def load_schemas():
    """
    Load and resolve JSON schemas from the schema directory.
    
    Discovers all JSON schema files in the application's schema directory,
    loads them with reference resolution, and returns a dictionary of
    resolved schemas for content validation and generation.
    
    Returns:
        dict: Dictionary of loaded schemas with resolved references:
            - Keys: Schema filenames (without .json extension)
            - Values: Fully resolved schema objects with expanded references
            
    Directory Structure:
        Searches for schemas in: <app_directory>/schema/*.json
        Example schema directory layout:
        
        .. code-block::
        
            schema/
            ├── article.json          # Main article schema
            ├── person.json           # Author/person schema
            ├── media.json            # Media attachment schema
            └── definitions.json      # Common definitions
            
    Reference Resolution:
        - Automatically resolves $ref properties
        - Supports external file references
        - Handles internal schema references
        - Expands nested reference chains
        
    Error Handling:
        - FileNotFoundError: Schema directory doesn't exist
        - JSONDecodeError: Invalid JSON in schema files
        - General exceptions: File permission or format issues
        
    Example:
        .. code-block:: python
        
            # Load all schemas
            schemas = load_schemas()
            
            # Access specific schema
            article_schema = schemas.get('article')
            if article_schema:
                # Use schema for content validation
                validate_content(content, article_schema)
                
            # List available schemas
            print("Available schemas:", list(schemas.keys()))
    
    Caching:
        Consider implementing caching for production use to avoid
        repeated file system access and JSON parsing overhead.
        
    Performance:
        - Loads all schemas at once for efficiency
        - Reference resolution performed during load
        - Suitable for application startup initialization
    """
    # Define the path to the schema directory
    schema_dir = os.path.join(os.path.dirname(__file__), 'schema')
    
    # Dictionary to hold all loaded schemas
    schemas = {}

    try:
        # Iterate over all files in the schema directory
        for filename in os.listdir(schema_dir):
            if filename.endswith('.json'):
                # Construct the full file path
                file_path = os.path.join(schema_dir, filename)
                
                # Load the JSON content
                with open(file_path, 'r') as file:
                    content = json.load(file)
                
                # Resolve references and store the schema
                # Use file:// URL to properly resolve relative references
                base_uri = f"file://{schema_dir}/"
                resolved_content = jsonref.loads(json.dumps(content), base_uri=base_uri)
                schema_name = filename[:-5]  # Remove the .json extension
                schemas[schema_name] = resolved_content
                
    except FileNotFoundError:
        print(f"Error: The directory {schema_dir} was not found.")
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON from a file in {schema_dir}. Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while reading files in {schema_dir}. Error: {e}")

    # Optionally, you can add a check to ensure at least one schema was loaded correctly
    if schemas:
        print("JSON schemas loaded successfully with references resolved.")
    else:
        print("Failed to load JSON schemas.")

    return schemas


# ================================
# Legacy Content Generation Functions  
# ================================
# Note: These are older implementations that may be deprecated
# in favor of the enhanced generate_content functions above

def generate_content(client, content_form):
    """
    Generate content using chat completions with optional JSON schema validation.
    
    Legacy content generation function that creates AI content using the OpenAI
    Chat Completions API. Supports structured JSON output when schema is provided,
    and fallback to plain text generation for flexible content creation.
    
    Args:
        client: OpenAI client instance configured with API credentials
        content_form: Content form object containing:
            - assistant: Assistant instance with model and instructions
            - Additional configuration for content generation
            
    Content Form Structure:
        - assistant.model.model_id: AI model identifier (e.g., "gpt-4")
        - assistant.instructions: System instructions for content generation
        - assistant.json_schema: Optional JSON schema for structured output
        
    Returns:
        tuple: (content, details) containing:
            - content (str): Generated content (JSON string or plain text)
            - details (dict): Generation metadata including:
                * model: Model used for generation
                * usage: Token consumption statistics
                * response_format: Output format specification
                
    JSON Schema Support:
        When assistant.json_schema is provided, enforces structured output:
        - Validates response against schema
        - Ensures consistent data format
        - Enables strict mode for reliable parsing
        
    Message Format:
        Uses chat completion format with:
        - System message: Assistant instructions and behavior
        - User message: Content request and context
        
    Example:
        .. code-block:: python
        
            # Content form with schema
            form = ContentForm(assistant=assistant_with_schema)
            content, details = generate_content(client, form)
            
            # Parse JSON response
            article_data = json.loads(content)
            print(f"Title: {article_data['title']}")
            
            # Check generation details
            print(f"Tokens used: {details['usage']['total_tokens']}")
    
    Legacy Note:
        This function represents an earlier implementation pattern.
        For new development, consider using the enhanced generate_content()
        function with thread management and advanced parameters.
        
    Error Handling:
        - API errors propagate to caller for handling
        - JSON schema validation failures may return error responses
        - Model availability issues raise appropriate exceptions
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
            }
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
            }
        ],
        response_format=response_format
    )
    # Get the content of the last message in the response
    data = response.choices[0].message.content

    content_detail = generate_content_detail(client, data)

    # Log the response
    logging.info("Response: %s", data, content_detail)
    
    return data, content_detail

# Load all schemas and store them in a variable
all_schemas = load_schemas()

parody_schema = resolve_refs(all_schemas.get('parody_news_article_schema'))
content_detail_schema = resolve_refs(all_schemas.get('content_detail_schema'))

def generate_content_detail(client, content):
    """
    Generate detailed content metadata using structured JSON schema.
    
    Legacy function that creates detailed metadata for content using the OpenAI
    Chat Completions API with a predefined JSON schema. Primarily used for
    extracting and enhancing content details, tags, and metadata.
    
    Args:
        client: OpenAI client instance configured with API credentials
        content (str): Content text to analyze and generate details for
        
    Returns:
        str: JSON string containing detailed content metadata:
            - title: Enhanced or extracted title
            - description: Content summary and description  
            - tags: Relevant content tags and categories
            - metadata: Additional content properties
            - analysis: Content analysis and insights
            
    Schema Format:
        Uses predefined content_detail_schema for structured output:
        - Ensures consistent metadata format
        - Validates response structure
        - Enables reliable JSON parsing
        
    Model Configuration:
        - Model: gpt-4o-mini (optimized for metadata tasks)
        - System prompt: "generate content detail"
        - JSON schema: content_detail_schema with strict validation
        
    Content Analysis:
        Analyzes input content to extract:
        - Key themes and topics
        - Relevant tags and categories
        - Summary and descriptions
        - Content structure and format
        - Audience and tone analysis
        
    Example:
        .. code-block:: python
        
            # Generate content details
            article_text = "AI revolutionizes news industry..."
            details_json = generate_content_detail(client, article_text)
            
            # Parse metadata
            details = json.loads(details_json)
            print(f"Title: {details['title']}")
            print(f"Tags: {details['tags']}")
    
    Logging:
        Logs all API responses for debugging and monitoring:
        - Response content logged at INFO level
        - Useful for tracking metadata generation patterns
        
    Legacy Note:
        This is a simplified implementation focusing on metadata extraction.
        For comprehensive content generation, use the enhanced generate_content()
        functions with full parameter control and error handling.
        
    Performance:
        - Optimized for quick metadata extraction
        - Uses efficient gpt-4o-mini model
        - Minimal token usage for cost effectiveness
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
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "Metadata",
                "description": "A JSON object representing details of a news article.",
                "schema": content_detail_schema,
                "strict": True,
           }
        }
    )
    # Get the content of the last message in the response
    data = response.choices[0].message.content
    
    # Log the response
    logging.info("Response: %s", data)
    
    return data


# ================================
# Thread and Message Management Functions
# ================================

def openai_create_message(client, contentitem):
    """
    Create a new thread and message for content processing.
    
    Initializes a new OpenAI conversation thread with metadata and creates
    the first user message containing content text. Used for starting new
    content analysis or generation workflows with proper context.
    
    Args:
        client: OpenAI client instance configured with API credentials
        contentitem: ContentItem model instance containing:
            - content_text: Text content for the message
            - detail.title: Content title for metadata
            - detail.description: Content description for metadata
            
    Returns:
        tuple: (message, thread_id) containing:
            - message: OpenAI message object with creation details
            - thread_id (str): Unique thread identifier for future operations
            
    Thread Metadata:
        Creates thread with structured metadata:
        - type: "news_article_thread" for categorization
        - title: Content title from detail object
        - description: Content description from detail object
        
    Message Configuration:
        - Role: "user" (represents user input)
        - Content: Full content text from contentitem
        - Thread: Newly created thread for isolated conversation
        
    Example:
        .. code-block:: python
        
            # Create message for content processing
            content = ContentItem.objects.get(id=content_id)
            message, thread_id = openai_create_message(client, content)
            
            print(f"Created message: {message.id}")
            print(f"Thread ID: {thread_id}")
            
            # Use thread_id for subsequent operations
            response = process_content_in_thread(client, thread_id)
    
    Thread Management:
        - Each call creates a new, independent thread
        - Thread metadata enables filtering and organization
        - Thread ID required for all subsequent operations
        
    Error Handling:
        - API errors propagate to caller
        - ContentItem validation should be performed before calling
        - Thread creation failures raise OpenAI API exceptions
        
    Use Cases:
        - Starting new content analysis workflows
        - Initializing content generation processes
        - Creating isolated conversation contexts
        - Preparing content for assistant processing
    """
    thread = client.beta.threads.create(
        metadata={"type": "news_article_thread",
                  "title": contentitem.detail.title,
                  "description": contentitem.detail.description,},
    )
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=contentitem.content_text
    )
    return message, thread.id

def openai_delete_message(client, message_id, thread_id):
    """
    Delete a specific message from an OpenAI thread.
    
    Permanently removes a message from the specified thread conversation.
    Used for content cleanup, error correction, or conversation management.
    This operation cannot be undone.
    
    Args:
        client: OpenAI client instance configured with API credentials
        message_id (str): Unique identifier of message to delete
        thread_id (str): Thread containing the message to delete
        
    Returns:
        dict: Deletion confirmation from OpenAI API:
            - id (str): ID of deleted message
            - object (str): Object type (always "thread.message.deleted")
            - deleted (bool): Confirmation of deletion (always True)
            
    Raises:
        openai.NotFoundError: If message_id or thread_id doesn't exist
        openai.PermissionDeniedError: If no permission to delete message
        openai.APIError: If deletion fails due to server error
        
    Message Context:
        - Only messages within the specified thread can be deleted
        - Deletion affects conversation flow and context
        - Cannot delete messages that don't belong to the thread
        
    Example:
        .. code-block:: python
        
            # Delete a specific message
            try:
                result = openai_delete_message(client, message_id, thread_id)
                if result['deleted']:
                    print(f"Message {result['id']} deleted successfully")
            except openai.NotFoundError:
                print("Message or thread not found")
    
    Warning:
        Message deletion is irreversible and may affect:
        - Conversation context and continuity
        - Related assistant responses and chains
        - Thread message numbering and flow
        
    Thread Impact:
        - Thread remains active after message deletion
        - Other messages in thread are unaffected
        - Thread metadata and structure preserved
        
    Security:
        Only messages owned by the current API key can be deleted.
    """
    deleted_message = client.beta.threads.messages.delete(
    message_id=message_id,
    thread_id=thread_id,
    )
    return deleted_message


def create_run(client, thread_id, assistant_id):
    """
    Create and execute an assistant run on a thread with timeout handling.
    
    Initiates an assistant run on the specified thread, then polls for completion
    with a 60-second timeout. Handles the asynchronous nature of OpenAI assistant
    execution while providing synchronous interface for immediate result processing.
    
    Args:
        client: OpenAI client instance configured with API credentials
        thread_id (str): Thread identifier containing messages to process
        assistant_id (str): Assistant to execute on the thread
        
    Returns:
        object: Completed run object from OpenAI API containing:
            - id: Unique run identifier
            - status: Final run status ("completed")
            - assistant_id: Assistant used for execution
            - thread_id: Thread that was processed
            - created_at: Run creation timestamp
            - usage: Token consumption statistics
            
    Raises:
        TimeoutError: If run doesn't complete within 60 seconds
        openai.NotFoundError: If thread_id or assistant_id doesn't exist
        openai.APIError: If run creation or execution fails
        
    Run Status Monitoring:
        Polls run status every iteration until completion:
        - queued: Run waiting in execution queue
        - in_progress: Assistant actively processing
        - completed: Run finished successfully
        - failed: Run encountered error
        - cancelled: Run was manually cancelled
        
    Timeout Handling:
        - Time limit: 60 seconds maximum execution
        - Polling frequency: Immediate checks for responsiveness
        - Timeout exception: Raised if limit exceeded
        
    Example:
        .. code-block:: python
        
            # Execute assistant on thread
            try:
                run = create_run(client, thread_id, assistant_id)
                print(f"Run completed: {run.id}")
                print(f"Status: {run.status}")
                
                # Retrieve assistant responses
                messages = get_thread_messages(client, thread_id)
                
            except TimeoutError:
                print("Assistant run timed out")
            except openai.NotFoundError:
                print("Thread or assistant not found")
    
    Performance Considerations:
        - 60-second timeout prevents indefinite waiting
        - Immediate polling for fast response times
        - CPU intensive during polling period
        - Consider async alternatives for high-volume usage
        
    Thread State:
        - Thread remains active after run completion
        - Assistant responses added to thread messages
        - Multiple runs can be executed on same thread
        - Thread maintains conversation history
        
    Best Practices:
        - Check thread message count before running
        - Handle timeout gracefully in production
        - Monitor token usage from run statistics
        - Consider rate limiting for multiple runs
    """
    import time

    # https://platform.openai.com/docs/api-reference/runs/createRun

    run = client.beta.threads.runs.create(
    thread_id=thread_id,
    assistant_id=assistant_id,
    )

    start_time = time.time()
    time_limit = 60  # Time limit in seconds

    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        
        if run_status.status == "completed":
            break
        
        if time.time() - start_time > time_limit:
            raise TimeoutError("The operation timed out.")
        
        time.sleep(2)

    message_response = client.beta.threads.messages.list(
        thread_id=thread_id,
        run_id=run.id
        )

    message_response_id = message_response.data[0].id

    # https://platform.openai.com/docs/api-reference/messages/getMessage
    response = client.beta.threads.messages.retrieve(
        message_id=message_response_id,
        thread_id=thread_id,
        )

    data = response.content[0].text.value
    assistant_id = response.assistant_id

    try:
        content_data = json.loads(data)
    except json.JSONDecodeError:
        content_data = data
    
    if isinstance(content_data, dict) and 'Content' in content_data and 'body' in content_data['Content']:
        content_text = content_data['Content']['body']
    else:
        content_text = content_data

    # retrieve the content item detail from the thread id
    
    content_detail_id = Message.objects.filter(thread_id=thread_id).first().contentitem.detail_id

    # Create a new content item instance with the response content
    new_content = ContentItem.objects.create(
        assistant_id=assistant_id,
        prompt=Assistant.objects.get(id=assistant_id).instructions,
        content_text=content_text,
        detail_id=content_detail_id,
        content_type='message'
    )

    # Create a new message instance with the response content
    new_message = Message.objects.create(
        id=message_response_id,
        thread_id=thread_id,
        assistant_id=None,
        status=run_status.status,
        run_id=run.id,
        contentitem_id=new_content.id,
    )
    
    new_content.save()
    new_message.save()

    run_response = {"id": message_response_id,
                    "content_text": content_text,
                    "assistant_id": assistant_id,
                    "status": run_status.status,
                    "run_id": run.id,
                    "detail_id": content_detail_id,
                    "thread_id": thread_id
                }

    # Return the run, run_status, and message_data
    return run, run_status, run_response

def openai_list_messages(client, thread_id):
    """
    Retrieve and format messages from an OpenAI thread.
    
    Fetches the most recent messages from a specified thread and formats
    them for display or processing. Limited to the 10 most recent messages
    to prevent overwhelming response sizes.
    
    Args:
        client: OpenAI client instance configured with API credentials
        thread_id (str): Thread identifier to retrieve messages from
        
    Returns:
        list: Formatted message list containing dictionaries:
            - id (str): Unique message identifier
            - text (str): Message content text
            - assistant_id (str|None): Assistant ID if message from assistant
            
    Message Formatting:
        Extracts key information from OpenAI message objects:
        - Message ID for reference and management
        - Content text from first content block
        - Assistant ID for attribution (None for user messages)
        
    Limit Configuration:
        - Maximum: 10 messages returned
        - Order: Most recent messages first
        - Pagination: Not implemented (use OpenAI pagination for more)
        
    Example:
        .. code-block:: python
        
            # Get recent messages
            messages = openai_list_messages(client, thread_id)
            
            for message in messages:
                sender = "Assistant" if message['assistant_id'] else "User"
                print(f"{sender}: {message['text'][:100]}...")
                print(f"ID: {message['id']}")
    
    Content Processing:
        - Assumes first content block contains main text
        - Handles text content type only
        - May need modification for image or file content
        
    Thread Context:
        - Thread must exist and be accessible
        - Messages are returned in reverse chronological order
        - Empty list returned for threads with no messages
        
    Error Handling:
        - API errors propagate to caller
        - IndexError possible if message format changes
        - Consider try-catch for production robustness
        
    Performance:
        - Efficient for conversation summaries
        - Low latency with 10-message limit
        - Suitable for real-time chat interfaces
    """
    thread_messages = client.beta.threads.messages.list(
        thread_id=thread_id,
        limit=10,
    )
    # Assuming each message in thread_messages has a 'content' attribute
    formatted_messages = [
        {"id": message.id, "text": message.content[0].text.value, "assistant_id": message.assistant_id} for message in thread_messages
    ]
    return formatted_messages


# ================================
# Utility Functions for Content Processing
# ================================

def json_to_markdown(data):
    """
    Convert JSON data structure to Markdown format recursively.
    
    Transforms nested JSON objects and arrays into structured Markdown
    with appropriate headers, lists, and formatting. Preserves hierarchical
    relationships through header levels and list nesting.
    
    Args:
        data: JSON-compatible data structure to convert:
            - dict: Object with key-value pairs
            - list: Array of items
            - primitives: strings, numbers, booleans
            
    Returns:
        str: Formatted Markdown text with:
            - Headers for object keys (# ## ### etc.)
            - Bullet lists for arrays
            - Plain text for primitive values
            - Proper spacing and structure
            
    Conversion Rules:
        - Dictionary keys become headers at appropriate levels
        - Lists become bullet-point lists with * prefix
        - Primitive values rendered as plain text
        - Nested structures preserve hierarchy
        
    Header Levels:
        - Level 1: Top-level object keys
        - Level 2-6: Nested object keys (increasing depth)
        - Automatic level management for deep nesting
        
    Example:
        .. code-block:: python
        
            # JSON data
            article_data = {
                "title": "Breaking News",
                "content": {
                    "body": "Article text here...",
                    "tags": ["news", "breaking", "important"]
                },
                "metadata": {
                    "author": "Jane Doe",
                    "published": "2023-01-01"
                }
            }
            
            # Convert to Markdown
            markdown = json_to_markdown(article_data)
            print(markdown)
            
            # Output:
            # # title
            # Breaking News
            # 
            # # content
            # ## body
            # Article text here...
            # 
            # ## tags
            # * news
            # * breaking
            # * important
            # 
            # # metadata
            # ## author
            # Jane Doe
            # ...
    
    Use Cases:
        - Converting API responses to readable format
        - Generating documentation from JSON schemas
        - Creating reports from structured data
        - Preparing content for Markdown-based systems
        
    Performance:
        - Recursive processing handles deep nesting
        - String concatenation for large structures
        - Consider optimization for very large datasets
        
    Limitations:
        - No support for tables or complex formatting
        - Binary data not handled
        - Circular references may cause issues
    """
    # Function to convert JSON object to Markdown recursively
    def convert_to_md(data, level=1):
        markdown = ""
        if isinstance(data, dict):
            for key, value in data.items():
                markdown += f"{'#' * level} {key}\n\n"
                markdown += convert_to_md(value, level + 1)
        elif isinstance(data, list):
            for item in data:
                markdown += f"* {convert_to_md(item, level + 1)}\n"
        else:
            markdown += f"{data}\n\n"
        return markdown

    return convert_to_md(data)


def generate_markdown_file(data, filename):
    """
    Generate a Markdown file from provided data with automatic formatting.
    
    Creates a Markdown file with the specified filename, converting the input
    data to appropriate Markdown format. Handles both JSON structures and
    plain text content with automatic file management and error handling.
    
    Args:
        data: Content to write to Markdown file:
            - str: Plain text content (written directly)
            - dict/list: JSON data (converted via json_to_markdown)
            - Other types: String representation used
        filename (str): Name of the output Markdown file:
            - Should include .md extension
            - Can include path separators for subdirectories
            - Existing files will be overwritten
            
    Returns:
        str: Full path to the generated Markdown file:
            - Absolute path for easy file access
            - Path verification for successful creation
            - None if generation fails
            
    File Generation Process:
        1. Data type detection and appropriate conversion
        2. File creation with UTF-8 encoding
        3. Content writing with proper formatting
        4. Path resolution and return
        
    Data Conversion:
        - JSON structures: Converted to structured Markdown
        - Plain strings: Written directly as content
        - Other types: String representation used
        - Empty data: Creates empty file
        
    Example:
        .. code-block:: python
        
            # Generate from JSON data
            article_data = {"title": "News", "content": "Article text"}
            file_path = generate_markdown_file(article_data, "article.md")
            print(f"Created: {file_path}")
            
            # Generate from plain text
            text_content = "# Heading\\n\\nParagraph text"
            file_path = generate_markdown_file(text_content, "simple.md")
            
            # Generate in subdirectory
            file_path = generate_markdown_file(data, "output/report.md")
    
    File Management:
        - Creates directories if they don't exist
        - Overwrites existing files without warning
        - Uses UTF-8 encoding for Unicode support
        - Handles file permission errors gracefully
        
    Error Handling:
        - File creation errors logged and handled
        - Permission issues return None
        - Invalid filenames sanitized or rejected
        - Path resolution failures managed
        
    Performance:
        - Efficient for small to medium files
        - Memory usage scales with data size
        - No buffering for very large datasets
        
    Best Practices:
        - Use descriptive filenames with .md extension
        - Check return value for successful generation
        - Handle None return for error cases
        - Consider file size limits for large data
    """

    # Define the file path
    file_path = os.path.join(settings.POST_DIR, filename)

    # Write the markdown content to the file
    with open(file_path, 'w') as file:
        file.write(data)
    
    return file_path

def create_or_update_assistant(client, validated_data):
    """
    Create or update an OpenAI assistant with database synchronization.
    
    Handles creation and modification of OpenAI assistants while maintaining
    synchronization with the local database. Supports both creating new
    assistants and updating existing ones based on the presence of an ID.
    
    Args:
        client: OpenAI client instance configured with API credentials
        validated_data (dict): Assistant configuration data containing:
            - name (str): Assistant display name
            - description (str): Assistant description
            - instructions (str, optional): System instructions (default: helpful assistant)
            - model (str): AI model identifier
            - json_schema (dict, optional): JSON schema for structured output
            - id (str, optional): Existing assistant ID for updates
            
    Returns:
        Assistant: Django model instance representing the assistant:
            - Synchronized with OpenAI assistant
            - Contains all configuration details
            - Ready for content generation use
            
    Operation Logic:
        - If ID provided: Updates existing assistant
        - If no ID: Creates new assistant
        - Database sync ensures local consistency
        - OpenAI API changes reflected in database
        
    Database Synchronization:
        Uses update_or_create for atomic operations:
        - Prevents duplicate assistants
        - Handles concurrent modifications
        - Maintains referential integrity
        
    Example:
        .. code-block:: python
        
            # Create new assistant
            data = {
                'name': 'News Writer',
                'description': 'Generates parody news articles',
                'instructions': 'Create satirical news content',
                'model': 'gpt-4',
                'json_schema': article_schema
            }
            assistant = create_or_update_assistant(client, data)
            
            # Update existing assistant
            update_data = {
                'id': 'asst_abc123',
                'name': 'Updated News Writer',
                'instructions': 'Enhanced news generation'
            }
            assistant = create_or_update_assistant(client, update_data)
    
    Error Handling:
        - OpenAI API errors propagate to caller
        - Database integrity maintained on failures
        - Validation errors prevent invalid assistants
        
    Model Requirements:
        - Model must be available in OpenAI platform
        - JSON schema must be valid if provided
        - Instructions should guide assistant behavior
        
    Performance:
        - Single API call for assistant operations
        - Efficient database upsert operation
        - Minimal overhead for synchronization
        
    Use Cases:
        - Assistant management interfaces
        - Configuration updates and deployments
        - Automated assistant provisioning
        - Content generation workflow setup
    """
    name = validated_data.get('name')
    description = validated_data.get('description')
    instructions = validated_data.get('instructions', 'you are a helpful assistant.')
    model = validated_data.get('model')
    json_schema = validated_data.get('json_schema')
    assistant_id = validated_data.get('id', None)  # For updates

    # Create or update the assistant in OpenAI
    assistant_ai = save_assistant(
        client,
        name,
        description,
        instructions,
        model,
        json_schema,
        assistant_id
    )

    # Update or create the Assistant object in the database
    assistant, created = Assistant.objects.update_or_create(
        id=assistant_ai.id,
        defaults={
            'name': name,
            'description': description,
            'instructions': instructions,
            'model': model,
            'json_schema': json_schema,
        }
    )
    return assistant

def get_openai_client():
    """
    Initialize and return an OpenAI client with configuration.
    
    Legacy function that creates an OpenAI client using configuration values
    from the database. Retrieves API key and organization ID from stored
    configuration and applies them to the OpenAI module.
    
    Returns:
        module: OpenAI module configured with:
            - api_key: Retrieved from configuration
            - organization: Optional organization ID if configured
            
    Configuration Sources:
        - api_key: Retrieved via get_config_value('api_key')
        - org_id: Retrieved via get_config_value('org_id')
        - Database-stored configuration values
        
    Example:
        .. code-block:: python
        
            # Get configured OpenAI module
            openai = get_openai_client()
            
            # Use for API calls
            response = openai.ChatCompletion.create(...)
    
    Legacy Note:
        This function uses the older OpenAI Python library interface.
        For new development, prefer the newer OpenAI client pattern
        with explicit client instantiation.
        
    Error Handling:
        - Missing configuration values may cause API failures
        - Invalid credentials detected during API calls
        - Organization ID is optional (only set if present)
    """
    import openai
    api_key = get_config_value('api_key')
    org_id = get_config_value('org_id')

    openai.api_key = api_key
    if (org_id):
        openai.organization = org_id

    return openai

def delete_assistant(client, assistant_id):
    """
    Delete an assistant from both OpenAI API and local database.
    
    Permanently removes an assistant from the OpenAI platform and
    synchronizes the deletion with the local database. Ensures
    consistency between remote and local assistant storage.
    
    Args:
        client: OpenAI client instance configured with API credentials
        assistant_id (str): Unique identifier of assistant to delete
        
    Returns:
        None: Operation completes successfully or raises exception
        
    Deletion Process:
        1. Delete assistant from OpenAI API
        2. Remove corresponding database record
        3. Ensure synchronization between systems
        
    Database Cleanup:
        - Removes Assistant model instance
        - May cascade to related objects
        - Maintains referential integrity
        
    Example:
        .. code-block:: python
        
            # Delete assistant completely
            try:
                delete_assistant(client, "asst_abc123")
                print("Assistant deleted successfully")
            except Exception as e:
                print(f"Deletion failed: {e}")
    
    Error Handling:
        - OpenAI API errors for non-existent assistants
        - Database integrity constraints
        - Partial failure handling (API vs database)
        
    Warning:
        This operation is irreversible. All assistant data including:
        - Configuration and instructions
        - Associated threads and messages
        - Custom training or fine-tuning
        
        Will be permanently lost.
        
    Synchronization:
        - API deletion performed first
        - Database cleanup follows successful API operation
        - Ensures consistency between systems
    """
    # Delete assistant from OpenAI API
    client.beta.assistants.delete(assistant_id)
    # Delete assistant from the database
    Assistant.objects.filter(id=assistant_id).delete()
    return f"Assistant with ID {assistant_id} deleted successfully."

def run_assistant(assistant, input_content):
    """
    Execute an assistant with legacy chat completion interface.
    
    Legacy function that runs an assistant using the older OpenAI chat
    completion interface. Provides basic assistant execution without
    the thread-based assistant API features.
    
    Args:
        assistant: Assistant model instance containing:
            - model: AI model configuration object
            - instructions: System instructions for the assistant
            - temperature: Generation temperature (optional, default: 0.7)
        input_content (str): User message content to process
        
    Returns:
        str: Generated response content from the assistant:
            - Plain text response from AI model
            - Direct content from first choice message
            
    Legacy Implementation:
        - Uses chat_completion.create instead of newer client methods
        - Direct OpenAI module usage instead of client instances
        - Simplified message structure without advanced features
        
    Message Structure:
        Creates two-message conversation:
        - System message: Assistant instructions
        - User message: Input content for processing
        
    Temperature Configuration:
        - Uses assistant.temperature if set
        - Falls back to 0.7 for balanced creativity
        - Range: 0.0 (deterministic) to 2.0 (creative)
        
    Example:
        .. code-block:: python
        
            # Run assistant with content
            assistant = Assistant.objects.get(name="Writer")
            response = run_assistant(assistant, "Write a story")
            print(response)
    
    Deprecated Note:
        This function uses deprecated OpenAI interface patterns.
        For new development, use the thread-based assistant API
        with proper client instantiation and conversation management.
        
    Error Handling:
        - API errors propagate to caller
        - Model availability issues raise exceptions
        - Configuration problems detected at runtime
    """
    client = get_openai_client()
    response = client.chat_completion.create(
        model=assistant.model.model_id,
        messages=[
            {"role": "system", "content": assistant.instructions},
            {"role": "user", "content": input_content}
        ],
        temperature=assistant.temperature or 0.7
    )
    output_content = response.choices[0].message.content
    return output_content

def generate_unique_id():
    """
    Generate a unique UUID identifier string.
    
    Creates a universally unique identifier using Python's uuid4 algorithm.
    Provides collision-resistant IDs suitable for database keys, file names,
    session identifiers, and other applications requiring uniqueness.
    
    Returns:
        str: UUID string in standard format:
            - 36 characters including hyphens
            - Lowercase hexadecimal digits
            - Format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
            - Guaranteed uniqueness across space and time
            
    UUID Properties:
        - Version 4: Random or pseudo-random generation
        - 122 bits of randomness
        - Extremely low collision probability
        - No dependency on MAC address or timestamp
        
    Example:
        .. code-block:: python
        
            # Generate unique identifier
            unique_id = generate_unique_id()
            print(unique_id)  # e.g., "550e8400-e29b-41d4-a716-446655440000"
            
            # Use for database records
            content = ContentItem.objects.create(
                id=generate_unique_id(),
                title="Article"
            )
    
    Use Cases:
        - Database primary keys
        - Session identifiers
        - File and directory naming
        - Request tracking and correlation
        - Temporary resource identification
        
    Performance:
        - Very fast generation (microseconds)
        - No network or disk I/O required
        - Cryptographically secure randomness
        - Suitable for high-frequency generation
        
    Uniqueness Guarantee:
        - Practically impossible collisions
        - Safe for distributed systems
        - No coordination required between generators
        - Mathematically proven uniqueness properties
    """
    import uuid
    return str(uuid.uuid4())


# ================================
# Model Configuration and Defaults
# ================================

def get_model_defaults(model_name, default_type="default_type"):
    """
    Retrieve cached model field defaults from database configuration.
    
    Fetches default field values for Django models from the FieldDefaults
    configuration table. Implements caching for performance and provides
    fallback handling for database connection issues.
    
    Args:
        model_name (str): Name of the model to get defaults for (currently unused)
        default_type (str, optional): Type of defaults to retrieve. 
                                    Default: "default_type"
            
    Returns:
        dict: Model field defaults configuration:
            - Keys: Field names or configuration keys
            - Values: Default values for those fields
            - Empty dict: If no defaults found or database error
            
    Caching Strategy:
        - Cache key: "field_defaults:{default_type}"
        - Persistent cache across requests
        - Reduces database queries for frequently accessed defaults
        - Cache invalidation on configuration updates
        
    Database Integration:
        - Queries FieldDefaults model for configuration
        - Handles database connection errors gracefully
        - Returns empty dict on ProgrammingError (missing tables)
        
    Example:
        .. code-block:: python
        
            # Get default values for assistant configuration
            defaults = get_model_defaults("Assistant", "assistant_defaults")
            
            # Use defaults in model creation
            assistant = Assistant.objects.create(
                name="New Assistant",
                temperature=defaults.get('temperature', 0.7),
                model=defaults.get('model', 'gpt-4'),
                **defaults
            )
    
    Error Handling:
        - ProgrammingError: Returns empty dict (during migrations)
        - Missing configuration: Returns empty dict
        - Cache failures: Falls back to database query
        
    Configuration Structure:
        Expects FieldDefaults model with:
        - type: Configuration type identifier
        - defaults: JSON field containing default values
        
    Performance:
        - First call: Database query + cache storage
        - Subsequent calls: Cache retrieval only
        - Efficient for frequently accessed configurations
        
    Use Cases:
        - Model form initialization
        - API default values
        - Configuration management
        - Feature flag defaults
    """
    from .models import FieldDefaults

    cache_key = f"field_defaults:{default_type}"
    defaults_list = cache.get(cache_key)
    if defaults_list is None:
        try:
            fd = FieldDefaults.objects.filter(type=default_type).first()
            if not fd:
                return {}
            defaults_list = fd.defaults
        except ProgrammingError:
            return {}
        cache.set(cache_key, defaults_list)

    for item in defaults_list:
        # If item is a string, try to parse it as JSON
        if isinstance(item, str):
            try:
                item = json.loads(item)
            except json.JSONDecodeError:
                continue

        if isinstance(item, dict) and item.get("model_name") == model_name:
            return item.get("fields", {})

    return {}

def load_template_from_path(template_path: str):
    """
    Load and parse a template file with YAML frontmatter.
    
    Reads a template file containing YAML frontmatter and template content,
    separating the configuration from the template body. Used for processing
    content templates with embedded metadata and configuration.
    
    Args:
        template_path (str): Absolute or relative path to template file:
            - Must contain YAML frontmatter delimited by ---
            - Template content follows the frontmatter
            - File must be readable and exist
            
    Returns:
        tuple: (yaml_config, template_body) containing:
            - yaml_config (dict): Parsed YAML configuration from frontmatter
            - template_body (str): Template content after frontmatter
            
    Frontmatter Format:
        Expected format at beginning of file:
        
        .. code-block:: yaml
        
            ---
            title: "Template Title"
            description: "Template description"
            variables:
              - name
              - content
            ---
            Template content goes here...
            
    Parsing Process:
        1. Read entire file content
        2. Extract YAML frontmatter using regex
        3. Parse YAML configuration
        4. Extract template body content
        
    Example:
        .. code-block:: python
        
            # Load content template
            config, template = load_template_from_path("templates/article.md")
            
            # Access configuration
            title = config.get('title')
            variables = config.get('variables', [])
            
            # Process template content
            rendered = template.format(**template_vars)
    
    Error Handling:
        - FileNotFoundError: Template file doesn't exist
        - ValueError: YAML frontmatter not found or invalid
        - YAMLError: Invalid YAML syntax in frontmatter
        
    Template Structure:
        - Frontmatter: YAML configuration at file start
        - Delimiter: Triple dashes (---) before and after YAML
        - Content: Template body after closing delimiter
        
    Use Cases:
        - Content template processing
        - Configuration-driven content generation
        - Template metadata extraction
        - Dynamic content rendering
    """
    with open(template_path, 'r') as file:
        content = file.read()
    front_matter_match = re.search(r'^---(.*?)---', content, re.DOTALL)
    if not front_matter_match:
        raise ValueError("YAML front matter not found in template.")
    yaml_config = yaml.safe_load(front_matter_match.group(1))
    template_body = content[front_matter_match.end():].strip()
    return yaml_config, template_body

def extract_file_paths_from_frontmatter(yaml_config: dict) -> list:
    """
    Extract file paths from template frontmatter configuration.

    Retrieves a list of file paths specified in the template frontmatter
    under the 'include_files' key. Used for processing templates that
    reference external files or resources.

    Args:
        yaml_config (dict): YAML configuration loaded from template frontmatter:
            - Should contain 'include_files' key with list of paths
            - File paths can be relative or absolute
            - Empty list returned if key missing

    Returns:
        list: File paths included in the template frontmatter:
            - Paths as specified in configuration
            - Empty list if 'include_files' key not present
            - Maintains original path format (relative/absolute)
            
    Frontmatter Structure:
        Expected frontmatter format:
        
        .. code-block:: yaml
        
            ---
            include_files:
              - "data/sample.json"
              - "templates/header.html"
              - "/absolute/path/to/file.txt"
            ---
            
    Example:
        .. code-block:: python
        
            # Load template configuration
            config, _ = load_template_from_path("template.md")
            
            # Extract file paths
            file_paths = extract_file_paths_from_frontmatter(config)
            
            # Process included files
            for file_path in file_paths:
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Process file content...
    
    Use Cases:
        - Template dependency resolution
        - Asset gathering for template processing
        - File inclusion in content generation
        - Resource collection for rendering
        
    Path Handling:
        - No path validation performed
        - Relative paths resolved relative to current working directory
        - Absolute paths used as-is
        - File existence not verified
        
    Error Handling:
        - Missing 'include_files' key: Returns empty list
        - Invalid YAML structure: May raise TypeError
        - Non-list values: Caller should validate
    """
    return yaml_config.get('include_files', [])
