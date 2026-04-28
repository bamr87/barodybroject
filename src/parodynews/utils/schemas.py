"""
File: schemas.py
Description: JSON schema loading, validation, and $ref resolution helpers
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- jsonref: >=1.1.0

Usage: from parodynews.utils.schemas import load_schemas
"""

import json
import os

import jsonref


def resolve_refs(obj):
    """
    Recursively resolve JSON references in complex data structures.

    Args:
        obj: JSON object, array, or primitive to process

    Returns:
        Resolved object with all references expanded
    """
    if isinstance(obj, jsonref.JsonRef):
        return resolve_refs(obj.__subject__)
    elif isinstance(obj, dict):
        return {k: resolve_refs(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_refs(i) for i in obj]
    else:
        return obj


def load_schemas():
    """
    Load and resolve JSON schemas from the schema directory.

    Returns:
        dict: Dictionary of loaded schemas with resolved references
    """
    schema_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema")
    schemas = {}

    try:
        for filename in os.listdir(schema_dir):
            if filename.endswith(".json"):
                file_path = os.path.join(schema_dir, filename)

                with open(file_path, "r") as file:
                    content = json.load(file)

                base_uri = f"file://{schema_dir}/"
                resolved_content = jsonref.loads(json.dumps(content), base_uri=base_uri)
                schema_name = filename[:-5]
                schemas[schema_name] = resolved_content

    except FileNotFoundError:
        pass
    except json.JSONDecodeError:
        pass
    except Exception:
        pass

    return schemas
