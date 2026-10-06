"""
File: schema_stub.py
Description: Build a deterministic example document that satisfies a JSON schema
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Usage: from parodynews.ai.schema_stub import build_example

The mock provider uses this so the whole content pipeline (generation,
metadata extraction, thread runs, publishing) can be exercised offline with
output that passes the same ``jsonschema`` validation real providers face.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

_SLUG_KEYS = {"slug"}
_DATE_KEYS = {"date", "publication_date", "published_at", "created_at"}
_LIST_TEXT_KEYS = {"keywords", "tags", "categories"}


def _string_for(key: str, schema: dict[str, Any], seed: str) -> str:
    lowered = key.lower()
    if lowered in _SLUG_KEYS:
        base = "-".join(seed.lower().split())[:40] or "mock"
        return "".join(ch for ch in base if ch.isalnum() or ch == "-") or "mock"
    if lowered in _DATE_KEYS or schema.get("format") in {"date", "date-time"}:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        return (
            now.date().isoformat()
            if schema.get("format") == "date"
            else now.isoformat()
        )
    if lowered in _LIST_TEXT_KEYS:
        return "mock, example, generated"
    description = schema.get("description", "")
    label = key or "value"
    text = f"{label} (mock)"
    if seed and lowered in {"title", "headline", "subtitle"}:
        # The seed is whatever prompt or article text was passed in, so it can
        # be multi-line Markdown; flatten it to keep the stub a plausible
        # single-line heading.
        flattened = " ".join(seed.replace("#", " ").split())[:60].strip()
        if flattened:
            text = f"{flattened} ({label} mock)"
    if description and lowered in {"body", "content", "text"}:
        text = f"{text}: {description}"
    min_length = int(schema.get("minLength", 0) or 0)
    if len(text) < min_length:
        text = text + " " * (min_length - len(text))
    max_length = schema.get("maxLength")
    if max_length is not None:
        text = text[: int(max_length)]
    return text


def build_example(schema: dict[str, Any], *, key: str = "", seed: str = "") -> Any:
    """Return a value that validates against ``schema``.

    Handles the subset of Draft-7 the project's schemas use: ``type`` (single
    or list), ``enum``, ``const``, ``default``, ``properties``/``required``,
    ``items``/``minItems``, ``anyOf``/``oneOf``/``allOf`` (first alternative),
    ``minimum``, ``minLength``/``maxLength``. ``$ref`` must already be
    resolved (see ``parodynews.utils.schemas.resolve_refs``).
    """
    if not isinstance(schema, dict):
        return None
    if "const" in schema:
        return schema["const"]
    if "default" in schema:
        return schema["default"]
    if schema.get("enum"):
        return schema["enum"][0]
    for combinator in ("anyOf", "oneOf", "allOf"):
        options = schema.get(combinator)
        if options:
            if combinator == "allOf":
                merged: dict[str, Any] = {}
                for option in options:
                    merged.update(option)
                return build_example(merged, key=key, seed=seed)
            return build_example(options[0], key=key, seed=seed)

    schema_type = schema.get("type")
    if isinstance(schema_type, list):
        schema_type = next((t for t in schema_type if t != "null"), "null")
    if schema_type is None:
        schema_type = (
            "object"
            if "properties" in schema
            else "array" if "items" in schema else "string"
        )

    if schema_type == "object":
        properties = schema.get("properties", {})
        required = schema.get("required")
        names = list(properties) if required is None else list(required)
        # Also emit optional properties: consumers like content_detail read
        # every declared key, and additional keys are still schema-valid.
        for name in properties:
            if name not in names:
                names.append(name)
        return {
            name: build_example(properties.get(name, {}), key=name, seed=seed)
            for name in names
        }
    if schema_type == "array":
        count = max(int(schema.get("minItems", 1) or 1), 1)
        item_schema = schema.get("items", {"type": "string"})
        if isinstance(item_schema, list):  # tuple validation
            return [
                build_example(sub, key=key, seed=seed) for sub in item_schema[:count]
            ]
        return [build_example(item_schema, key=key, seed=seed) for _ in range(count)]
    if schema_type == "string":
        return _string_for(key, schema, seed)
    if schema_type == "integer":
        return int(schema.get("minimum", 0) or 0)
    if schema_type == "number":
        return float(schema.get("minimum", 0) or 0)
    if schema_type == "boolean":
        return False
    return None
