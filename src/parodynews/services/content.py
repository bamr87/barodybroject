"""
File: content.py
Description: Content generation and metadata extraction workflows
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1

Usage:
    from parodynews.services import content
    outcome = content.generate_content(content_item)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from django.utils import timezone
from django.utils.text import slugify

from parodynews.ai import (
    AIConfigurationError,
    AIProvider,
    ChatMessage,
    GenerationRequest,
    GenerationResult,
    get_provider,
)
from parodynews.models import Assistant, ContentDetail, ContentItem
from parodynews.utils.markdown import json_to_markdown
from parodynews.utils.schemas import get_schema

logger = logging.getLogger(__name__)

DEFAULT_ARTICLE_SCHEMA = "parody_news_article_schema"
CONTENT_DETAIL_SCHEMA = "content_detail_schema"

CONTENT_DETAIL_INSTRUCTIONS = (
    "You extract publication metadata for a satirical news article. "
    "Read the article and return the metadata as JSON matching the schema: "
    "an eye-catching title of at most seven words, a one-sentence subtitle, "
    "the author's name (use 'ParodyNews Staff' if unknown), an ISO-8601 "
    "publication date, a one-paragraph description, a short excerpt, the "
    "prompt that could have produced the article, a URL-safe slug, and "
    "categories, keywords and tags."
)


@dataclass
class GenerationOutcome:
    """What a generation workflow produced, for API responses and logs."""

    result: GenerationResult
    content_text: str
    detail_data: dict[str, Any] | None = None
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "provider": self.result.provider,
            "model": self.result.model,
            "usage": self.result.usage,
            "content_text": self.content_text,
            "detail": self.detail_data,
            "warnings": self.warnings,
        }


# --------------------------------------------------------------------- helpers
def provider_for(
    assistant: Assistant | None = None, provider_slug: str | None = None
) -> AIProvider:
    """Pick the provider: explicit slug, then the assistant's model, then default."""
    if provider_slug:
        return get_provider(provider_slug)
    if assistant is not None and assistant.model_id and assistant.model.provider:
        return get_provider(assistant.model.provider)
    return get_provider()


def request_for_assistant(
    assistant: Assistant,
    messages: list[ChatMessage],
    *,
    provider: AIProvider,
    json_schema: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> GenerationRequest:
    """Build a request that carries the assistant's persona and schema."""
    schema_row = assistant.json_schema
    schema = (
        json_schema
        if json_schema is not None
        else (schema_row.schema if schema_row is not None else None)
    )
    model = ""
    if assistant.model_id and assistant.model.provider == provider.slug:
        model = assistant.model.model_id
    return GenerationRequest(
        system=assistant.instructions or "",
        messages=messages,
        model=model,
        json_schema=schema,
        schema_name=(schema_row.name if schema_row is not None else "article"),
        schema_description=(schema_row.description if schema_row is not None else ""),
        temperature=assistant.temperature,
        metadata={"assistant_id": assistant.id, **(metadata or {})},
    )


def _paragraphs(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, dict):
        out: list[str] = []
        for key, sub in value.items():
            out.append(f"**{key}**")
            out.extend(_paragraphs(sub))
        return out
    return [str(value)]


def _humanize(key: str) -> str:
    words: list[str] = []
    current = ""
    for ch in key:
        if ch.isupper() and current:
            words.append(current)
            current = ch
        else:
            current += ch
    if current:
        words.append(current)
    return " ".join(words).replace("_", " ").strip().title()


def render_article_markdown(data: Any) -> str:
    """Turn a structured article into Markdown for editors and posts.

    Understands the bundled ``parody_news_article_schema`` (``Content`` with
    ``Headline``/``Introduction``/``Body``/``Conclusion``) and the simpler
    ``news_article_schema`` (``Content.body``); anything else is rendered
    generically so no provider output is ever lost.
    """
    if not isinstance(data, dict):
        return str(data)
    content = data.get("Content")
    if isinstance(content, dict):
        if isinstance(content.get("body"), str):
            return content["body"].strip()
        if any(
            key in content for key in ("Headline", "Introduction", "Body", "Conclusion")
        ):
            lines: list[str] = []
            headlines = _paragraphs(content.get("Headline"))
            if headlines:
                lines.append(f"# {headlines[0]}")
                lines.append("")
                for alternative in headlines[1:]:
                    lines.append(f"*{alternative}*")
                    lines.append("")
            for paragraph in _paragraphs(content.get("Introduction")):
                lines.append(paragraph)
                lines.append("")
            body = content.get("Body")
            if isinstance(body, dict):
                for section, value in body.items():
                    lines.append(f"## {_humanize(section)}")
                    lines.append("")
                    for paragraph in _paragraphs(value):
                        lines.append(paragraph)
                        lines.append("")
            else:
                for paragraph in _paragraphs(body):
                    lines.append(paragraph)
                    lines.append("")
            conclusion = _paragraphs(content.get("Conclusion"))
            if conclusion:
                lines.append("## Conclusion")
                lines.append("")
                for paragraph in conclusion:
                    lines.append(paragraph)
                    lines.append("")
            return "\n".join(lines).strip()
    return json_to_markdown(data).strip()


def result_text(result: GenerationResult) -> str:
    """Markdown for structured results, raw text otherwise."""
    if result.data is not None:
        return render_article_markdown(result.data)
    return result.text


def _keywords(metadata: dict[str, Any]) -> list[str]:
    keywords: list[str] = []
    raw = metadata.get("keywords")
    if isinstance(raw, str):
        keywords.extend(k.strip() for k in raw.split(",") if k.strip())
    elif isinstance(raw, list):
        keywords.extend(str(k).strip() for k in raw if str(k).strip())
    for tag in metadata.get("tags") or []:
        tag = str(tag).strip()
        if tag and tag not in keywords:
            keywords.append(tag)
    return keywords


def apply_content_detail(detail: ContentDetail, data: dict[str, Any]) -> ContentDetail:
    """Copy a ``content_detail_schema`` document onto a ``ContentDetail``."""
    header = data.get("Header") or {}
    metadata = data.get("Metadata") or {}
    author = header.get("author") or {}

    title = (header.get("title") or "").strip()
    if title:
        detail.title = title[:255]
    author_name = (author.get("name") if isinstance(author, dict) else author) or ""
    if author_name:
        detail.author = str(author_name)[:100]
    description = (metadata.get("description") or "").strip()
    if description:
        detail.description = description
    slug = slugify(metadata.get("slug") or title or detail.slug or "post")
    detail.slug = (slug or "post")[:255]
    keywords = _keywords(metadata)
    if keywords:
        detail.keywords = keywords
    detail.published_at = timezone.now()
    detail.save()
    return detail


# ------------------------------------------------------------------ workflows
def generate_content_detail(
    text: str, *, provider: AIProvider | None = None
) -> dict[str, Any]:
    """Ask the provider for publication metadata that matches ``content_detail_schema``."""
    provider = provider or get_provider()
    request = GenerationRequest(
        system=CONTENT_DETAIL_INSTRUCTIONS,
        messages=[ChatMessage("user", text)],
        json_schema=get_schema(CONTENT_DETAIL_SCHEMA),
        schema_name="content_detail",
        schema_description="Publication metadata for a news article.",
    )
    return provider.generate(request).data


def generate_content(
    content_item: ContentItem,
    *,
    provider_slug: str | None = None,
    update_detail: bool = True,
) -> GenerationOutcome:
    """Generate the article for ``content_item`` and refresh its detail record.

    The assistant attached to the item supplies the instructions, the model
    and (optionally) the output schema. Without an assistant schema the
    bundled parody article schema is used so the output is always
    structured. When ``update_detail`` is set, a second, smaller call
    extracts the title/author/description/slug/keywords for the parent
    ``ContentDetail``.
    """
    assistant = content_item.assistant
    if assistant is None:
        raise AIConfigurationError("this content item has no assistant to run")
    provider = provider_for(assistant, provider_slug)
    request = request_for_assistant(
        assistant,
        [ChatMessage("user", content_item.prompt)],
        provider=provider,
        json_schema=(
            None
            if assistant.json_schema is not None
            else get_schema(DEFAULT_ARTICLE_SCHEMA)
        ),
        metadata={"content_item_id": content_item.id},
    )
    result = provider.generate(request)
    text = result_text(result)
    content_item.content_text = text
    content_item.save(update_fields=["content_text"])

    outcome = GenerationOutcome(result=result, content_text=text)
    if update_detail:
        try:
            detail_data = generate_content_detail(text, provider=provider)
        except Exception as exc:  # noqa: BLE001 - the article is already saved
            logger.warning("content detail extraction failed: %s", exc)
            outcome.warnings.append(f"metadata extraction failed: {exc}")
        else:
            apply_content_detail(content_item.detail, detail_data)
            outcome.detail_data = detail_data
    return outcome


def create_content_from_text(
    text: str,
    *,
    user=None,
    assistant: Assistant | None = None,
    prompt: str = "",
    provider: AIProvider | None = None,
) -> ContentDetail:
    """Create a ``ContentDetail`` + first ``ContentItem`` from existing text,
    using the provider to fill in the publication metadata."""
    detail = ContentDetail.objects.create(user=user, title=(prompt or text)[:255])
    try:
        detail_data = generate_content_detail(text, provider=provider)
    except Exception as exc:  # noqa: BLE001 - keep the content even if metadata fails
        logger.warning("content detail extraction failed: %s", exc)
    else:
        apply_content_detail(detail, detail_data)
    ContentItem.objects.create(
        detail=detail,
        assistant=assistant,
        prompt=prompt or text,
        content_text=text,
        content_type="text",
    )
    return detail
