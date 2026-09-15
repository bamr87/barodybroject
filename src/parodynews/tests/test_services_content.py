"""
File: test_services_content.py
Description: Tests for parodynews.services.content — generation, Markdown rendering, metadata
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_services_content.py (run from src/)
"""

import pytest

from parodynews.ai import AIConfigurationError, AIProviderError, GenerationResult
from parodynews.models import Assistant, ContentDetail, ContentItem
from parodynews.services import content as content_services

pytestmark = pytest.mark.django_db


PARODY_ARTICLE = {
    "Content": {
        "Headline": ["Cats Declare Independence"],
        "Introduction": ["It began at dawn."],
        "Body": {
            "DarkHumor": ["The litter box was the first casualty."],
            "Facts": ["Cats sleep 16 hours a day."],
            "OptimisticTurn": ["But there is hope."],
        },
        "Conclusion": ["Adopt, do not shop."],
    }
}


# --------------------------------------------------------------------------- #
# render_article_markdown
# --------------------------------------------------------------------------- #
def test_render_turns_the_parody_schema_into_markdown():
    markdown = content_services.render_article_markdown(PARODY_ARTICLE)
    assert markdown.startswith("# Cats Declare Independence")
    assert "## Dark Humor" in markdown
    assert "## Optimistic Turn" in markdown
    assert "The litter box was the first casualty." in markdown
    assert markdown.rstrip().endswith("Adopt, do not shop.")


def test_render_uses_the_body_of_the_simple_news_schema():
    """`news_article_schema` carries one prose string instead of sections."""
    markdown = content_services.render_article_markdown(
        {"Content": {"body": "A single block of prose.", "images": []}}
    )
    assert markdown == "A single block of prose."


def test_render_never_drops_unrecognised_output():
    """A schema the renderer does not know still has to reach the editor."""
    markdown = content_services.render_article_markdown({"Something": {"Else": "kept"}})
    assert "kept" in markdown


def test_render_passes_plain_text_through():
    assert content_services.render_article_markdown("just text") == "just text"


def test_result_text_prefers_structured_data_over_raw_text():
    result = GenerationResult(
        text='{"Content": {"body": "rendered"}}', data=PARODY_ARTICLE
    )
    assert content_services.result_text(result).startswith(
        "# Cats Declare Independence"
    )


def test_result_text_falls_back_to_raw_text():
    assert content_services.result_text(GenerationResult(text="plain")) == "plain"


# --------------------------------------------------------------------------- #
# apply_content_detail
# --------------------------------------------------------------------------- #
def test_apply_content_detail_copies_the_metadata(content_detail):
    content_services.apply_content_detail(
        content_detail,
        {
            "Header": {
                "title": "Cats Declare Independence",
                "author": {"name": "A. Cat"},
                "publication_date": "2026-01-01",
                "subtitle": "s",
            },
            "Metadata": {
                "description": "A satirical look at feline autonomy",
                "slug": "Cats Declare Independence!",
                "keywords": "cats, parody",
                "tags": ["satire"],
                "excerpt": "e",
                "prompt": "p",
                "categories": ["news"],
            },
        },
    )
    content_detail.refresh_from_db()
    assert content_detail.title == "Cats Declare Independence"
    assert content_detail.author == "A. Cat"
    assert content_detail.description == "A satirical look at feline autonomy"
    # The model's slug is free text; it has to be URL-safe before it is used
    # as a filename by the publisher.
    assert content_detail.slug == "cats-declare-independence"
    assert content_detail.keywords == ["cats", "parody", "satire"]


def test_apply_content_detail_keeps_existing_values_when_fields_are_missing(
    content_detail,
):
    """A provider may omit an optional field; that must not blank the record."""
    original_title = content_detail.title
    content_services.apply_content_detail(
        content_detail, {"Header": {}, "Metadata": {}}
    )
    content_detail.refresh_from_db()
    assert content_detail.title == original_title


def test_apply_content_detail_accepts_keywords_as_a_list(content_detail):
    content_services.apply_content_detail(
        content_detail,
        {"Header": {}, "Metadata": {"keywords": ["a", "b"], "tags": ["b"]}},
    )
    content_detail.refresh_from_db()
    # `b` appears in both keywords and tags but must not be duplicated.
    assert content_detail.keywords == ["a", "b"]


# --------------------------------------------------------------------------- #
# provider_for
# --------------------------------------------------------------------------- #
def test_provider_follows_the_assistants_model(assistant):
    assert content_services.provider_for(assistant).slug == "mock"


def test_an_explicit_provider_wins(assistant):
    assert content_services.provider_for(assistant, "openai").slug == "openai"


def test_an_assistant_without_a_model_uses_the_default():
    bare = Assistant.objects.create(name="Default runner")
    assert content_services.provider_for(bare).slug == "mock"


# --------------------------------------------------------------------------- #
# request_for_assistant
# --------------------------------------------------------------------------- #
def test_the_request_carries_the_assistants_persona_and_schema(assistant):
    from parodynews.ai import ChatMessage, get_provider

    request = content_services.request_for_assistant(
        assistant, [ChatMessage("user", "go")], provider=get_provider("mock")
    )
    assert request.system == assistant.instructions
    assert request.json_schema == assistant.json_schema.schema
    assert request.model == "mock-1"


def test_the_model_is_left_blank_for_a_different_provider(assistant):
    """An assistant configured for one provider must not send that provider's
    model id to another one, which would be rejected as unknown."""
    from parodynews.ai import ChatMessage, get_provider

    request = content_services.request_for_assistant(
        assistant, [ChatMessage("user", "go")], provider=get_provider("openai")
    )
    assert request.model == ""


# --------------------------------------------------------------------------- #
# generate_content
# --------------------------------------------------------------------------- #
def test_generate_content_stores_the_article_and_refreshes_the_detail(content_item):
    outcome = content_services.generate_content(content_item)

    content_item.refresh_from_db()
    assert content_item.content_text
    assert outcome.content_text == content_item.content_text
    assert outcome.result.provider == "mock"
    assert outcome.detail_data is not None


def test_generate_content_uses_the_assistants_schema(content_item, mock_provider):
    content_services.generate_content(content_item)
    # Two calls: the article, then the metadata extraction.
    assert (
        mock_provider.calls[0].json_schema == content_item.assistant.json_schema.schema
    )


def test_generate_content_falls_back_to_the_bundled_article_schema(
    content_detail, plain_assistant, mock_provider
):
    """Without an assistant schema the output would be unstructured prose, and
    the metadata step would have nothing reliable to read."""
    item = ContentItem.objects.create(
        detail=content_detail,
        assistant=plain_assistant,
        prompt="write",
        content_text="",
    )
    content_services.generate_content(item)
    assert mock_provider.calls[0].json_schema["title"] == "Satirical News Content"


def test_generate_content_needs_an_assistant(content_detail):
    item = ContentItem.objects.create(
        detail=content_detail, prompt="write", content_text=""
    )
    with pytest.raises(AIConfigurationError, match="no assistant"):
        content_services.generate_content(item)


def test_a_failed_metadata_step_keeps_the_generated_article(
    content_item, mock_provider
):
    """The article is the expensive part. A metadata failure must degrade to a
    warning, not discard what the model just wrote."""
    from parodynews.ai.schema_stub import build_example

    # First call: a valid article for whatever schema the assistant carries.
    # Second call: the metadata step falls over.
    article = build_example(content_item.assistant.json_schema.schema, seed="Cats")
    mock_provider.queue_response(article)
    mock_provider.queue_response(
        AIProviderError("metadata provider down", provider="mock")
    )

    outcome = content_services.generate_content(content_item)

    content_item.refresh_from_db()
    assert content_item.content_text.strip()
    assert outcome.content_text == content_item.content_text
    assert outcome.detail_data is None
    assert any("metadata extraction failed" in w for w in outcome.warnings)


def test_generation_failure_propagates(content_item, mock_provider):
    mock_provider.queue_response(AIProviderError("provider down", provider="mock"))
    with pytest.raises(AIProviderError):
        content_services.generate_content(content_item)


def test_generate_content_can_skip_the_metadata_step(content_item, mock_provider):
    content_services.generate_content(content_item, update_detail=False)
    assert len(mock_provider.calls) == 1


# --------------------------------------------------------------------------- #
# create_content_from_text
# --------------------------------------------------------------------------- #
def test_create_content_from_text_builds_a_detail_and_item(user):
    detail = content_services.create_content_from_text(
        "An article that already exists.", user=user, prompt="the prompt"
    )
    assert isinstance(detail, ContentDetail)
    assert detail.user == user
    item = detail.contentitem.get()
    assert item.content_text == "An article that already exists."
    assert item.prompt == "the prompt"


def test_create_content_from_text_survives_a_metadata_failure(user, mock_provider):
    mock_provider.queue_response(AIProviderError("down", provider="mock"))
    detail = content_services.create_content_from_text("text", user=user)
    assert detail.contentitem.count() == 1
