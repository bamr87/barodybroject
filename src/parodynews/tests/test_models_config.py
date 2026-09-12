"""
File: test_models_config.py
Description: Unit tests for parodynews.models.config — PoweredBy, AppConfig, FieldDefaults
Author: Barodybroject Team <team@example.com>
Created: 2026-09-11
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_models_config.py (run from src/)
"""

import json

import pytest
from django.core.cache import cache
from django.db import models

from parodynews.models import AppConfig, FieldDefaults, PoweredBy

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# PoweredBy
# --------------------------------------------------------------------------- #
def test_powered_by_round_trips():
    powered_by = PoweredBy.objects.create(
        name="OpenAI", icon="fa-robot", url="https://openai.com"
    )
    stored = PoweredBy.objects.get(pk=powered_by.pk)
    assert (stored.name, stored.icon, stored.url) == (
        "OpenAI",
        "fa-robot",
        "https://openai.com",
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
# AppConfig
# --------------------------------------------------------------------------- #
def test_app_config_round_trips():
    config = AppConfig.objects.create(
        api_key="sk-test",
        project_id="proj_test",
        org_id="org_test",
        github_pages_repo="bamr87/blog",
        github_pages_token="ghp_test",
    )
    stored = AppConfig.objects.get(pk=config.pk)
    assert stored.api_key == "sk-test"
    assert stored.github_pages_repo == "bamr87/blog"


def test_app_config_str_is_constant():
    """It is a singleton, so its label carries no instance data."""
    config = AppConfig.objects.create(
        api_key="k",
        project_id="p",
        org_id="o",
        github_pages_repo="r",
        github_pages_token="t",
    )
    assert str(config) == "App Configuration"


def test_app_config_publishing_defaults():
    """Two fields are omitted by every caller in the tree; the defaults are the
    contract those callers rely on."""
    config = AppConfig.objects.create(
        api_key="k",
        project_id="p",
        org_id="o",
        github_pages_repo="r",
        github_pages_token="t",
    )
    assert config.github_pages_branch == "main"
    assert config.github_pages_post_dir == "posts/"


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
