""" 
File: __init__.py
Description: Utility helpers for OpenAI integration, schemas, and content generation
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
 - django: >=5.1
 - openai: >=1.57.0

Usage: import from parodynews.utils.<module>
"""

# Assistant management utilities
from .assistants import (
    create_or_update_assistant,
    delete_assistant,
    get_assistant,
    openai_delete_assistant,
    retrieve_assistants_info,
    run_assistant,
    save_assistant,
)

# Configuration utilities
from .config import (
    get_config_value,
    get_openai_client,
    table_exists_and_fields_populated,
)

# Content generation utilities
from .content import generate_content, generate_content_detail

# Defaults utilities
from .defaults import (
    extract_file_paths_from_frontmatter,
    generate_unique_id,
    get_model_defaults,
    load_template_from_path,
)

# Keep dkim_backend accessible
from .dkim_backend import DKIMEmailBackend

# Markdown utilities
from .markdown import generate_markdown_file, json_to_markdown

# OpenAI client utilities
from .openai_client import load_openai_client

# Schema utilities
from .schemas import load_schemas, resolve_refs

# Thread and message utilities
from .threads import (
    create_run,
    openai_create_message,
    openai_delete_message,
    openai_list_messages,
)

__all__ = [
    # Config
    "table_exists_and_fields_populated",
    "get_config_value",
    "get_openai_client",
    # OpenAI Client
    "load_openai_client",
    # Assistants
    "save_assistant",
    "get_assistant",
    "retrieve_assistants_info",
    "openai_delete_assistant",
    "create_or_update_assistant",
    "delete_assistant",
    "run_assistant",
    # Content
    "generate_content",
    "generate_content_detail",
    # Threads
    "openai_create_message",
    "openai_delete_message",
    "create_run",
    "openai_list_messages",
    # Schemas
    "load_schemas",
    "resolve_refs",
    # Markdown
    "json_to_markdown",
    "generate_markdown_file",
    # Defaults
    "get_model_defaults",
    "load_template_from_path",
    "extract_file_paths_from_frontmatter",
    "generate_unique_id",
    "DKIMEmailBackend",
]
