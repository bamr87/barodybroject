"""
File: test_models_base.py
Description: Unit tests for parodynews.models.base — the abstract timestamp base and display mixin
Author: Barodybroject Team <team@example.com>
Created: 2026-09-11
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_models_base.py (run from src/)

Note on completeness (issue #51): `TimestampedModel` is the one class in
`grep -rn "^class .*(models\\." src/parodynews/models/` that is NOT instantiated
anywhere in this suite, because it is `abstract = True` — Django creates no table
for it and instantiating it is meaningless. It has no concrete subclass in the
tree either (`OpenAIModel` and `Post` declare their own timestamp columns rather
than inheriting), so it is asserted on through its field definitions and its
abstractness instead. `DisplayFieldsMixin` is a plain Python mixin, not a model
at all, so it is exercised through an ordinary subclass with no database.
"""

from django.db import models

from parodynews.models.base import DisplayFieldsMixin, TimestampedModel


# --------------------------------------------------------------------------- #
# TimestampedModel — field definitions (no database; the model is abstract)
# --------------------------------------------------------------------------- #
def test_timestamped_model_is_abstract():
    """It must stay abstract: making it concrete would add a stray table."""
    assert TimestampedModel._meta.abstract is True


def test_timestamped_model_declares_both_timestamp_fields():
    field_names = {f.name for f in TimestampedModel._meta.fields}
    assert {"created_at", "updated_at"} <= field_names


def test_created_at_is_set_once_on_insert():
    """`auto_now_add` — written on INSERT and never touched again."""
    created_at = TimestampedModel._meta.get_field("created_at")
    assert isinstance(created_at, models.DateTimeField)
    assert created_at.auto_now_add is True
    assert created_at.auto_now is False


def test_updated_at_is_rewritten_on_every_save():
    """`auto_now` — rewritten on every save, which is the whole point."""
    updated_at = TimestampedModel._meta.get_field("updated_at")
    assert isinstance(updated_at, models.DateTimeField)
    assert updated_at.auto_now is True
    assert updated_at.auto_now_add is False


def test_a_concrete_subclass_inherits_both_columns():
    """Declared without a database: an abstract parent contributes its fields."""

    class Concrete(TimestampedModel):
        class Meta:
            abstract = True

    field_names = {f.name for f in Concrete._meta.fields}
    assert {"created_at", "updated_at"} <= field_names


# --------------------------------------------------------------------------- #
# DisplayFieldsMixin — plain Python, no model machinery
# --------------------------------------------------------------------------- #
def test_display_fields_defaults_to_empty():
    """The base returns [], so a model that forgets to override shows nothing
    rather than raising in an admin list view."""

    class Bare(DisplayFieldsMixin):
        pass

    assert Bare().get_display_fields() == []


def test_display_fields_is_overridable():
    class Named(DisplayFieldsMixin):
        def get_display_fields(self):
            return ["id", "title"]

    assert Named().get_display_fields() == ["id", "title"]
