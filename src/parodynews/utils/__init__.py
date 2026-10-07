"""
File: __init__.py
Description: Utility helpers for schemas, markdown, defaults, and email
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2026-09-14
Version: 0.6.0

Dependencies:
 - django: >=5.1

Usage: import from parodynews.utils.<module>

AI calls no longer live here: see ``parodynews.ai`` (providers) and
``parodynews.services`` (workflows built on top of them).
"""

from .defaults import (
    extract_file_paths_from_frontmatter,
    generate_unique_id,
    get_model_defaults,
    load_template_from_path,
)
from .dkim_backend import DKIMEmailBackend
from .markdown import generate_markdown_file, json_to_markdown
from .schemas import get_schema, load_schemas, resolve_refs

__all__ = [
    "DKIMEmailBackend",
    "extract_file_paths_from_frontmatter",
    "generate_markdown_file",
    "generate_unique_id",
    "get_model_defaults",
    "get_schema",
    "json_to_markdown",
    "load_schemas",
    "load_template_from_path",
    "resolve_refs",
]
