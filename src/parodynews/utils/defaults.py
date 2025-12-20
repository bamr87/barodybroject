"""
File: defaults.py
Description: Default generation helpers for model fields and front matter
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- python: >=3.10

Usage: from parodynews.utils.defaults import generate_field_defaults
"""

import json
import re
import uuid

import yaml
from django.core.cache import cache
from django.db.utils import ProgrammingError


def get_model_defaults(model_name, default_type="default_type"):
    """
    Retrieve cached model field defaults from database configuration.

    Args:
        model_name: Name of the model to get defaults for
        default_type: Type of defaults to retrieve

    Returns:
        dict: Model field defaults configuration
    """
    from ..models import FieldDefaults

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

    Args:
        template_path: Path to template file

    Returns:
        tuple: (yaml_config, template_body)
    """
    with open(template_path, "r") as file:
        content = file.read()
    front_matter_match = re.search(r"^---(.*?)---", content, re.DOTALL)
    if not front_matter_match:
        raise ValueError("YAML front matter not found in template.")
    yaml_config = yaml.safe_load(front_matter_match.group(1))
    template_body = content[front_matter_match.end() :].strip()
    return yaml_config, template_body


def extract_file_paths_from_frontmatter(yaml_config: dict) -> list:
    """
    Extract file paths from template frontmatter configuration.

    Args:
        yaml_config: YAML configuration loaded from template frontmatter

    Returns:
        list: File paths included in the template frontmatter
    """
    return yaml_config.get("include_files", [])


def generate_unique_id():
    """
    Generate a unique UUID identifier string.

    Returns:
        str: UUID string in standard format
    """
    return str(uuid.uuid4())

