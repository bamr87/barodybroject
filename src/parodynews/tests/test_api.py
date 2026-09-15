"""
File: test_api.py
Description: Tests for the REST API the React frontend consumes
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 1.0.0

Dependencies:
- django
- djangorestframework
- pytest-django

Usage: python -m pytest parodynews/tests/test_api.py (run from src/)
"""

import pytest

from parodynews.ai import AIProviderError
from parodynews.models import (
    AIModel,
    AIProviderConfig,
    Assistant,
    ContentDetail,
    Message,
    Post,
)

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# Session and site metadata
# --------------------------------------------------------------------------- #
def test_auth_me_reports_an_anonymous_visitor(anon_api_client):
    body = anon_api_client.get("/api/auth/me/").json()
    assert body["authenticated"] is False
    assert body["user"] is None
    # The SPA needs a token before it can post the login form's successor.
    assert body["csrf_token"]


def test_auth_me_reports_the_signed_in_user(api_client, user):
    body = api_client.get("/api/auth/me/").json()
    assert body["authenticated"] is True
    assert body["user"]["username"] == user.username


def test_site_info_is_public(anon_api_client):
    """The shell renders a navbar and footer before anyone signs in."""
    response = anon_api_client.get("/api/site/")
    assert response.status_code == 200
    body = response.json()
    assert body["default_provider"] == "mock"
    assert set(body["providers"]) == {"claude_code", "anthropic", "openai", "mock"}


# --------------------------------------------------------------------------- #
# Permissions
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "path",
    [
        "/api/threads/",
        "/api/assistants/",
        "/api/content-details/",
        "/api/posts/",
        "/api/providers/",
        "/api/ai-models/",
    ],
)
def test_authoring_endpoints_require_a_session(anon_api_client, path):
    assert anon_api_client.get(path).status_code in (401, 403)


def test_a_non_staff_user_cannot_change_provider_credentials(api_client):
    response = api_client.patch(
        "/api/providers/anthropic/config/", {"api_key": "sk-ant-api-x"}, format="json"
    )
    assert response.status_code == 403
    assert not AIProviderConfig.objects.filter(provider="anthropic").exists()


def test_a_non_staff_user_cannot_switch_the_default_provider(api_client):
    assert api_client.post("/api/providers/openai/set-default/").status_code == 403


def test_a_user_sees_only_their_own_threads(api_client, staff_api_client, user, thread):
    """Threads are per-user; another account's drafts must not be listed."""
    from django.contrib.auth.models import User

    other = User.objects.create_user("someone_else", password="x")
    from parodynews.models import Thread

    Thread.objects.create(id="thread_other", name="Not yours", user=other)

    ids = {row["id"] for row in api_client.get("/api/threads/").json()["results"]}
    assert thread.id in ids
    assert "thread_other" not in ids


def test_staff_see_every_thread(staff_api_client, thread):
    ids = {row["id"] for row in staff_api_client.get("/api/threads/").json()["results"]}
    assert thread.id in ids


# --------------------------------------------------------------------------- #
# Providers
# --------------------------------------------------------------------------- #
def test_providers_list_reports_configuration_state(api_client):
    rows = api_client.get("/api/providers/").json()
    by_slug = {row["slug"]: row for row in rows}
    assert by_slug["mock"]["is_default"] is True
    assert by_slug["mock"]["configured"] is True
    assert "api_key" not in str(by_slug)  # never echoed back


def test_syncing_models_fills_the_catalogue(api_client):
    body = api_client.post("/api/providers/mock/sync/").json()
    assert body["total"] == 2
    assert AIModel.objects.filter(provider="mock").count() == 2


def test_syncing_twice_updates_rather_than_duplicates(api_client):
    api_client.post("/api/providers/mock/sync/")
    body = api_client.post("/api/providers/mock/sync/").json()
    assert body["created"] == []
    assert len(body["updated"]) == 2
    assert AIModel.objects.filter(provider="mock").count() == 2


def test_testing_a_provider_returns_its_reply(api_client):
    body = api_client.post("/api/providers/mock/test/").json()
    assert body["ok"] is True
    assert body["model"] == "mock-1"


def test_staff_can_store_a_credential(staff_api_client):
    response = staff_api_client.patch(
        "/api/providers/claude_code/config/",
        {"api_key": "sk-ant-oat01-secret", "default_model": "claude-sonnet-5"},
        format="json",
    )
    assert response.status_code == 200
    row = AIProviderConfig.objects.get(provider="claude_code")
    assert row.api_key == "sk-ant-oat01-secret"
    # The write-only field must not come back in the response.
    assert "sk-ant-oat01-secret" not in response.content.decode()


def test_saving_without_a_key_keeps_the_stored_one(staff_api_client):
    AIProviderConfig.objects.create(provider="openai", api_key="sk-existing")
    staff_api_client.patch(
        "/api/providers/openai/config/", {"default_model": "gpt-4o"}, format="json"
    )
    row = AIProviderConfig.objects.get(provider="openai")
    assert row.api_key == "sk-existing"
    assert row.default_model == "gpt-4o"


def test_a_credential_can_be_cleared_explicitly(staff_api_client):
    AIProviderConfig.objects.create(provider="openai", api_key="sk-existing")
    staff_api_client.patch(
        "/api/providers/openai/config/", {"clear_api_key": True}, format="json"
    )
    assert AIProviderConfig.objects.get(provider="openai").api_key == ""


def test_staff_can_switch_the_default_provider(staff_api_client):
    staff_api_client.post("/api/providers/openai/set-default/")
    assert AIProviderConfig.objects.get(provider="openai").is_default is True


def test_an_unknown_provider_is_a_404(api_client):
    assert api_client.get("/api/providers/gpt-9000/").status_code == 404


# --------------------------------------------------------------------------- #
# Assistants
# --------------------------------------------------------------------------- #
def test_creating_an_assistant_mints_an_id(api_client, ai_model):
    response = api_client.post(
        "/api/assistants/",
        {"name": "Satirist", "instructions": "Be funny.", "model": ai_model.id},
        format="json",
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("asst_")
    assert body["provider"] == "mock"


def test_an_assistant_reports_the_groups_it_belongs_to(
    api_client, assistant, membership
):
    body = api_client.get(f"/api/assistants/{assistant.id}/").json()
    assert [group["name"] for group in body["groups"]] == ["Content Pipeline"]


def test_deleting_an_assistant_keeps_its_content(api_client, assistant, content_item):
    api_client.delete(f"/api/assistants/{assistant.id}/")
    content_item.refresh_from_db()
    assert content_item.assistant is None
    assert content_item.content_text


# --------------------------------------------------------------------------- #
# Assistant groups
# --------------------------------------------------------------------------- #
def test_a_group_is_created_with_its_pipeline(api_client, assistant):
    response = api_client.post(
        "/api/assistant-groups/",
        {
            "name": "Pipeline",
            "memberships": [{"assistant": assistant.id, "position": 1}],
        },
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["memberships"][0]["assistant_name"] == assistant.name


def test_updating_a_group_replaces_its_pipeline(
    api_client, assistant, assistant_group, ai_model
):
    second = Assistant.objects.create(name="Editor", model=ai_model)
    response = api_client.patch(
        f"/api/assistant-groups/{assistant_group.id}/",
        {"memberships": [{"assistant": second.id, "position": 1}]},
        format="json",
    )
    assert response.status_code == 200
    assert [m["assistant"] for m in response.json()["memberships"]] == [second.id]


def test_a_group_can_be_emptied(api_client, assistant_group, membership):
    response = api_client.patch(
        f"/api/assistant-groups/{assistant_group.id}/",
        {"memberships": []},
        format="json",
    )
    assert response.json()["memberships"] == []


# --------------------------------------------------------------------------- #
# Content
# --------------------------------------------------------------------------- #
def test_creating_content_also_creates_the_prompt_item(api_client, assistant, user):
    response = api_client.post(
        "/api/content-details/",
        {"title": "Cats", "prompt": "Write about cats", "assistant": assistant.id},
        format="json",
    )
    assert response.status_code == 201
    detail = ContentDetail.objects.get(pk=response.json()["id"])
    assert detail.user == user
    assert detail.contentitem.get().prompt == "Write about cats"


def test_updating_content_updates_the_prompt_item(
    api_client, content_detail, content_item
):
    api_client.patch(
        f"/api/content-details/{content_detail.id}/",
        {"prompt": "A different prompt"},
        format="json",
    )
    content_item.refresh_from_db()
    assert content_item.prompt == "A different prompt"


def test_generating_returns_the_article_and_the_refreshed_detail(
    api_client, content_detail, content_item
):
    body = api_client.post(
        f"/api/content-details/{content_detail.id}/generate/", {}, format="json"
    ).json()
    assert body["provider"] == "mock"
    assert body["content_text"]
    assert body["content_detail"]["slug"]


def test_generating_without_a_prompt_item_is_a_400(api_client, content_detail):
    response = api_client.post(
        f"/api/content-details/{content_detail.id}/generate/", {}, format="json"
    )
    assert response.status_code == 400
    assert "prompt" in response.json()["detail"]


def test_a_provider_failure_becomes_a_502(
    api_client, content_detail, content_item, mock_provider
):
    """A provider being down is not the caller's fault, so it must not read as
    a validation error in the UI."""
    mock_provider.queue_response(AIProviderError("upstream exploded", provider="mock"))
    response = api_client.post(
        f"/api/content-details/{content_detail.id}/generate/", {}, format="json"
    )
    assert response.status_code == 502
    assert "upstream exploded" in response.json()["detail"]


def test_a_missing_credential_becomes_a_400(api_client, content_detail, content_item):
    """A configuration problem is actionable by the operator, so it is a 400
    with the message the settings screen can show."""
    content_item.assistant = None
    content_item.save()
    response = api_client.post(
        f"/api/content-details/{content_detail.id}/generate/", {}, format="json"
    )
    assert response.status_code == 400


def test_creating_a_thread_from_content(api_client, content_detail, content_item):
    response = api_client.post(
        f"/api/content-details/{content_detail.id}/create-thread/", {}, format="json"
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"].startswith("thread_")
    assert len(body["messages"]) == 1


# --------------------------------------------------------------------------- #
# Threads and messages
# --------------------------------------------------------------------------- #
def test_thread_detail_includes_the_conversation(api_client, thread, content_item):
    Message.objects.create(thread=thread, contentitem=content_item)
    body = api_client.get(f"/api/threads/{thread.id}/").json()
    assert len(body["messages"]) == 1
    assert body["messages"][0]["content_text"] == content_item.content_text


def test_running_an_assistant_returns_the_reply_and_the_thread(
    api_client, thread, content_item, assistant
):
    Message.objects.create(thread=thread, contentitem=content_item)
    body = api_client.post(
        f"/api/threads/{thread.id}/run/", {"assistant": assistant.id}, format="json"
    ).json()
    assert body["message"]["role"] == "assistant"
    assert body["message"]["status"] == "completed"
    assert len(body["thread"]["messages"]) == 2


def test_running_without_an_assistant_is_a_400(api_client, thread, content_item):
    Message.objects.create(thread=thread, contentitem=content_item)
    response = api_client.post(f"/api/threads/{thread.id}/run/", {}, format="json")
    assert response.status_code == 400


def test_running_a_group(api_client, thread, content_item, assistant_group, membership):
    Message.objects.create(thread=thread, contentitem=content_item)
    body = api_client.post(
        f"/api/threads/{thread.id}/run-group/",
        {"assistant_group": assistant_group.id},
        format="json",
    ).json()
    assert len(body["messages"]) == 1


def test_adding_a_message_to_a_thread(api_client, thread, content_item):
    Message.objects.create(thread=thread, contentitem=content_item)
    response = api_client.post(
        f"/api/threads/{thread.id}/add-message/",
        {"text": "one more thing"},
        format="json",
    )
    assert response.status_code == 201
    assert response.json()["messages"][-1]["content_text"] == "one more thing"


def test_adding_an_empty_message_is_refused(api_client, thread):
    response = api_client.post(
        f"/api/threads/{thread.id}/add-message/", {"text": "   "}, format="json"
    )
    assert response.status_code == 400


def test_assigning_an_assistant_to_a_message(api_client, message, plain_assistant):
    body = api_client.post(
        f"/api/messages/{message.id}/assign/",
        {"assistant": plain_assistant.id},
        format="json",
    ).json()
    assert body["assistant"] == plain_assistant.id


def test_assigning_an_unknown_assistant_is_a_400(api_client, message):
    response = api_client.post(
        f"/api/messages/{message.id}/assign/", {"assistant": "asst_nope"}, format="json"
    )
    assert response.status_code == 400


def test_a_message_becomes_a_post(api_client, message):
    response = api_client.post(
        f"/api/messages/{message.id}/create-post/", {}, format="json"
    )
    assert response.status_code == 201
    assert Post.objects.filter(pk=response.json()["id"]).exists()


def test_a_message_becomes_new_content(api_client, message):
    response = api_client.post(
        f"/api/messages/{message.id}/create-content/", {}, format="json"
    )
    assert response.status_code == 201
    assert ContentDetail.objects.filter(pk=response.json()["id"]).exists()


# --------------------------------------------------------------------------- #
# Posts
# --------------------------------------------------------------------------- #
def test_a_post_renders_its_published_file(api_client, post):
    body = api_client.get(f"/api/posts/{post.id}/render/").json()
    assert body["filename"].endswith(".md")
    assert body["document"].startswith("---")


def test_editing_a_post_updates_its_front_matter(api_client, post):
    api_client.patch(
        f"/api/posts/{post.id}/",
        {"post_content": "# New body", "front_matter": {"title": "New title"}},
        format="json",
    )
    post.refresh_from_db()
    assert post.post_content == "# New body"
    assert post.front_matter.title == "New title"


def test_publishing_without_github_configuration_is_a_400(api_client, post):
    response = api_client.post(f"/api/posts/{post.id}/publish/", {}, format="json")
    assert response.status_code == 400
    assert "not configured" in response.json()["detail"]


# --------------------------------------------------------------------------- #
# Schemas
# --------------------------------------------------------------------------- #
def test_bundled_schemas_are_offered_for_import(api_client):
    body = api_client.get("/api/json-schemas/bundled/").json()
    names = {row["name"] for row in body}
    assert {"content_detail_schema", "parody_news_article_schema"} <= names


def test_a_schema_can_be_exported_as_a_file(api_client, json_schema):
    response = api_client.get(f"/api/json-schemas/{json_schema.id}/export/")
    assert response.status_code == 200
    assert response["Content-Disposition"].endswith(f'"{json_schema.name}.json"')


# --------------------------------------------------------------------------- #
# AI models
# --------------------------------------------------------------------------- #
def test_ai_models_can_be_filtered_by_provider(api_client, ai_model, openai_model):
    body = api_client.get("/api/ai-models/", {"provider": "mock"}).json()
    assert [row["model_id"] for row in body["results"]] == ["mock-1"]


def test_creating_a_model_for_an_unknown_provider_is_refused(api_client):
    response = api_client.post(
        "/api/ai-models/", {"provider": "gpt-9000", "model_id": "x"}, format="json"
    )
    assert response.status_code == 400
    assert "provider" in response.json()
