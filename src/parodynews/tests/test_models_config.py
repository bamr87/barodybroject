"""
File: test_models_config.py
Description: Unit tests for parodynews.models.config — PoweredBy, AppConfig, AIProviderConfig, FieldDefaults
Author: Barodybroject Team <team@example.com>
Created: 2026-09-11
Last Modified: 2026-09-14
Version: 2.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_models_config.py (run from src/)
"""

import json

import pytest
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models, transaction

from parodynews.models import AIProviderConfig, AppConfig, FieldDefaults, PoweredBy

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# PoweredBy
# --------------------------------------------------------------------------- #
def test_powered_by_round_trips():
    powered_by = PoweredBy.objects.create(
        name="Anthropic", icon="robot", url="https://anthropic.com"
    )
    stored = PoweredBy.objects.get(pk=powered_by.pk)
    assert (stored.name, stored.icon, stored.url) == (
        "Anthropic",
        "robot",
        "https://anthropic.com",
    )


def test_powered_by_str_is_the_name():
    assert (
        str(PoweredBy.objects.create(name="Django", icon="fa", url="https://d.jp"))
        == "Django"
    )


def test_powered_by_url_is_a_url_field():
    """A plain CharField here would accept anything; the model promises a URL,
    and it is the field class — not the column type, which is CharField for
    both — that carries the URL validator."""
    assert isinstance(PoweredBy._meta.get_field("url"), models.URLField)


# --------------------------------------------------------------------------- #
# AppConfig — publishing only, since the AI credentials moved out
# --------------------------------------------------------------------------- #
def test_app_config_round_trips():
    config = AppConfig.objects.create(
        github_pages_repo="bamr87/blog", github_pages_token="ghp_test"
    )
    stored = AppConfig.objects.get(pk=config.pk)
    assert stored.github_pages_repo == "bamr87/blog"


def test_app_config_str_is_constant():
    """It is a singleton, so its label carries no instance data."""
    config = AppConfig.objects.create(github_pages_repo="r", github_pages_token="t")
    assert str(config) == "App Configuration"


def test_app_config_publishing_defaults():
    config = AppConfig.objects.create(github_pages_repo="r", github_pages_token="t")
    assert config.github_pages_branch == "main"
    assert config.github_pages_post_dir == "posts/"


def test_app_config_no_longer_stores_ai_credentials():
    """The OpenAI columns moved to AIProviderConfig. Asserting their absence
    keeps a well-meaning re-add from quietly reintroducing two sources of
    truth for one credential."""
    fields = {field.name for field in AppConfig._meta.fields}
    assert not fields & {"api_key", "org_id", "project_id"}


# --------------------------------------------------------------------------- #
# AIProviderConfig
# --------------------------------------------------------------------------- #
def test_provider_config_round_trips():
    row = AIProviderConfig.objects.create(
        provider="anthropic",
        display_name="Anthropic",
        api_key="sk-ant-api-test",
        default_model="claude-opus-5",
    )
    stored = AIProviderConfig.objects.get(pk=row.pk)
    assert stored.api_key == "sk-ant-api-test"
    assert stored.has_credential is True


def test_provider_config_without_a_key_reports_no_credential():
    """An empty key is meaningful: the provider falls back to its environment
    variables, and the settings UI says so."""
    row = AIProviderConfig.objects.create(provider="openai")
    assert row.has_credential is False


def test_provider_config_str_prefers_the_display_name():
    assert str(AIProviderConfig.objects.create(provider="mock")) == "mock"
    assert (
        str(AIProviderConfig.objects.create(provider="openai", display_name="OpenAI"))
        == "OpenAI"
    )


def test_provider_is_unique():
    AIProviderConfig.objects.create(provider="openai")
    with pytest.raises(IntegrityError), transaction.atomic():
        AIProviderConfig.objects.create(provider="openai")


def test_saving_a_default_demotes_the_previous_one():
    """Exactly one default at a time, enforced in save() rather than left to
    whichever row the resolver happened to read first."""
    first = AIProviderConfig.objects.create(provider="openai", is_default=True)
    second = AIProviderConfig.objects.create(provider="anthropic", is_default=True)

    first.refresh_from_db()
    assert first.is_default is False
    assert second.is_default is True
    assert AIProviderConfig.objects.filter(is_default=True).count() == 1


def test_resaving_the_default_keeps_it_default():
    """The demotion excludes the row being saved, or saving the default would
    clear the application's only default."""
    row = AIProviderConfig.objects.create(provider="mock", is_default=True)
    row.default_model = "mock-fast"
    row.save()

    row.refresh_from_db()
    assert row.is_default is True


def test_clean_rejects_an_unknown_provider():
    row = AIProviderConfig(provider="not-a-provider")
    with pytest.raises(ValidationError) as excinfo:
        row.clean()
    assert "provider" in excinfo.value.message_dict


def test_clean_rejects_a_disabled_default():
    row = AIProviderConfig(provider="mock", is_default=True, is_enabled=False)
    with pytest.raises(ValidationError) as excinfo:
        row.clean()
    assert "is_default" in excinfo.value.message_dict


def test_clean_accepts_every_registered_provider():
    from parodynews.ai import available_providers

    for slug in available_providers():
        AIProviderConfig(provider=slug).clean()  # must not raise


def test_provider_configs_list_the_default_first():
    AIProviderConfig.objects.create(provider="openai")
    AIProviderConfig.objects.create(provider="mock", is_default=True)
    assert list(AIProviderConfig.objects.values_list("provider", flat=True)) == [
        "mock",
        "openai",
    ]


# --------------------------------------------------------------------------- #
# FieldDefaults — including the custom save()
# --------------------------------------------------------------------------- #
def test_field_defaults_round_trips_the_json_structure(default_value_config_export):
    """Built from the real 2025-02-18 export rather than an invented literal."""
    row = default_value_config_export[0]
    payload = [{"model_name": row["model_name"], "fields": json.loads(row["defaults"])}]

    defaults = FieldDefaults.objects.create(type="content_defaults", defaults=payload)

    stored = FieldDefaults.objects.get(pk=defaults.pk)
    assert stored.defaults == payload
    assert stored.defaults[0]["model_name"] == "ContentDetail"
    assert stored.defaults[0]["fields"]["title"] == "Default Title"


def test_field_defaults_str_names_the_type():
    assert str(FieldDefaults.objects.create(type="post_defaults")) == (
        "Defaults for post_defaults"
    )


def test_field_defaults_defaults():
    empty = FieldDefaults.objects.create()
    assert empty.type == "default_type"
    assert empty.defaults == []


def test_save_clears_the_field_defaults_cache():
    """The custom `save()` exists ONLY to invalidate this key. Asserting that
    saving does not raise would not have caught a dropped `cache.delete`."""
    cache.set("field_defaults", "stale value", 300)
    assert cache.get("field_defaults") == "stale value"

    FieldDefaults.objects.create(type="post_defaults")

    assert cache.get("field_defaults") is None


def test_save_clears_the_cache_on_update_too():
    """Not just on insert — an edited default is exactly the case that matters."""
    defaults = FieldDefaults.objects.create(type="post_defaults")
    cache.set("field_defaults", "stale value", 300)

    defaults.defaults = [{"model_name": "Post", "fields": {"status": "draft"}}]
    defaults.save()

    assert cache.get("field_defaults") is None
    assert FieldDefaults.objects.get(pk=defaults.pk).defaults[0]["model_name"] == "Post"


def test_save_leaves_other_cache_keys_alone():
    """A `cache.clear()` here would silently evict the whole application cache."""
    cache.set("some_other_key", "keep me", 300)

    FieldDefaults.objects.create(type="post_defaults")

    assert cache.get("some_other_key") == "keep me"
