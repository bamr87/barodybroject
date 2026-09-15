"""
File: schemas.py
Description: JSON schema loading, validation, and $ref resolution helpers
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2026-09-14
Version: 0.6.0

Dependencies:
- jsonref: >=1.1.0

Usage: from parodynews.utils.schemas import get_schema
"""

import json
import logging
import os
from functools import lru_cache

import jsonref

logger = logging.getLogger(__name__)

SCHEMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "schema")


def resolve_refs(obj):
    """Recursively replace ``jsonref`` proxies with plain Python structures."""
    if isinstance(obj, jsonref.JsonRef):
        return resolve_refs(obj.__subject__)
    elif isinstance(obj, dict):
        return {k: resolve_refs(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_refs(i) for i in obj]
    else:
        return obj


def load_schemas(schema_dir: str = SCHEMA_DIR) -> dict:
    """Load every ``*.json`` schema in ``schema_dir`` with ``$ref`` resolved.

    Returns:
        dict: schema name (file name without extension) -> schema
    """
    schemas = {}
    if not os.path.isdir(schema_dir):
        return schemas
    base_uri = f"file://{schema_dir}/"
    for filename in sorted(os.listdir(schema_dir)):
        if not filename.endswith(".json"):
            continue
        file_path = os.path.join(schema_dir, filename)
        try:
            with open(file_path, encoding="utf-8") as file:
                content = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Skipping schema %s: %s", filename, exc)
            continue
        resolved = jsonref.loads(json.dumps(content), base_uri=base_uri)
        schemas[filename[:-5]] = resolve_refs(resolved)
    return schemas


@lru_cache(maxsize=1)
def _cached_schemas() -> dict:
    return load_schemas()


def get_schema(name: str) -> dict:
    """Return the bundled schema called ``name`` (e.g. ``content_detail_schema``)."""
    try:
        return _cached_schemas()[name]
    except KeyError as exc:
        raise KeyError(
            f"unknown schema {name!r}; available: {sorted(_cached_schemas())}"
        ) from exc
