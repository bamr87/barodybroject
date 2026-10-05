"""
File: test_models_content.py
Description: Unit tests for parodynews.models.content — ContentDetail and ContentItem
Author: Barodybroject Team <team@example.com>
Created: 2026-09-11
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_models_content.py (run from src/)
"""

import pytest

from parodynews.models import ContentDetail, ContentItem

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# ContentDetail
# --------------------------------------------------------------------------- #
def test_content_detail_round_trips(content_detail):
    stored = ContentDetail.objects.get(pk=content_detail.pk)
    assert stored.title == "Local Cat Declares Independence"
    assert stored.author == "ParodyNews Staff"
    assert stored.keywords == ["cats", "parody"]


def test_content_detail_str_is_the_title(content_detail):
    assert str(content_detail) == "Local Cat Declares Independence"


def test_content_detail_display_fields(content_detail):
    assert content_detail.get_display_fields() == [
        "id",
        "title",
        "description",
        "author",
        "published_at",
    ]


def test_content_detail_defaults():
    bare = ContentDetail.objects.create()
    assert bare.slug == "slug"
    assert bare.keywords == []
    assert bare.published_at is not None
    assert bare.user is None


def test_content_detail_belongs_to_a_user(content_detail, user):
    assert content_detail.user == user
    assert list(user.content_details.all()) == [content_detail]


def test_deleting_the_user_deletes_their_content_details(content_detail, user):
    """CASCADE — the reverse of the SET_NULL relations elsewhere in the tree."""
    user.delete()
    assert not ContentDetail.objects.filter(pk=content_detail.pk).exists()


def test_content_details_are_newest_first():
    older = ContentDetail.objects.create(title="Older")
    newer = ContentDetail.objects.create(title="Newer")
    ContentDetail.objects.filter(pk=older.pk).update(
        published_at=newer.published_at.replace(year=newer.published_at.year - 1)
    )
    assert list(ContentDetail.objects.values_list("title", flat=True)) == [
        "Newer",
        "Older",
    ]


# --------------------------------------------------------------------------- #
# ContentItem — including the custom save()
# --------------------------------------------------------------------------- #
def test_content_item_round_trips(content_item, content_detail):
    stored = ContentItem.objects.get(pk=content_item.pk)
    assert stored.content_text == "In a shocking turn of events..."
    assert stored.detail == content_detail
    assert stored.content_type == "text"


def test_content_item_str_is_the_prompt(content_item):
    assert str(content_item) == "Write an opening paragraph"


def test_content_item_display_fields(content_item):
    assert content_item.get_display_fields() == [
        "id",
        "assistant",
        "prompt",
        "content_text",
        "detail",
    ]


def test_save_numbers_items_sequentially(content_detail):
    """The custom `save()` exists only to do this. Asserting that creating an
    item does not raise would not have caught a dropped increment."""
    first = ContentItem.objects.create(
        content_text="one", prompt="p1", detail=content_detail
    )
    second = ContentItem.objects.create(
        content_text="two", prompt="p2", detail=content_detail
    )
    third = ContentItem.objects.create(
        content_text="three", prompt="p3", detail=content_detail
    )
    assert [first.line_number, second.line_number, third.line_number] == [1, 2, 3]


def test_save_numbers_each_detail_independently(content_detail):
    """Two ContentDetails each start at 1 — the sequence is per-parent, not
    global. A `ContentItem.objects.count()`-based implementation would pass the
    test above and fail this one."""
    other = ContentDetail.objects.create(title="Another article")

    ContentItem.objects.create(content_text="a", prompt="p", detail=content_detail)
    first_of_other = ContentItem.objects.create(
        content_text="b", prompt="p", detail=other
    )
    second_of_content = ContentItem.objects.create(
        content_text="c", prompt="p", detail=content_detail
    )

    assert first_of_other.line_number == 1
    assert second_of_content.line_number == 2


def test_save_overrides_an_explicitly_supplied_line_number(content_detail):
    """Documented behaviour: "Manual assignment is overridden"."""
    item = ContentItem.objects.create(
        content_text="x", prompt="p", detail=content_detail, line_number=99
    )
    assert item.line_number == 1


def test_save_does_not_renumber_an_existing_item(content_detail):
    """The increment is guarded by `if not self.pk`, so editing an item keeps
    its place in the sequence."""
    first = ContentItem.objects.create(
        content_text="one", prompt="p1", detail=content_detail
    )
    ContentItem.objects.create(content_text="two", prompt="p2", detail=content_detail)

    first.content_text = "one, edited"
    first.save()

    first.refresh_from_db()
    assert first.line_number == 1
    assert first.content_text == "one, edited"


def test_deleting_the_detail_deletes_its_items(content_item, content_detail):
    """CASCADE: an item has no meaning without its parent."""
    content_detail.delete()
    assert not ContentItem.objects.filter(pk=content_item.pk).exists()


def test_deleting_the_assistant_keeps_the_item(content_item, assistant):
    """SET_NULL: the generated text outlives the assistant that produced it."""
    assistant.delete()
    content_item.refresh_from_db()
    assert content_item.assistant is None
    assert content_item.content_text == "In a shocking turn of events..."


def test_items_are_ordered_by_detail_then_line_number(content_detail):
    ContentItem.objects.create(content_text="one", prompt="p1", detail=content_detail)
    ContentItem.objects.create(content_text="two", prompt="p2", detail=content_detail)
    numbers = list(
        ContentItem.objects.filter(detail=content_detail).values_list(
            "line_number", flat=True
        )
    )
    assert numbers == sorted(numbers)


def test_the_detail_reaches_its_items_by_related_name(content_item, content_detail):
    assert list(content_detail.contentitem.all()) == [content_item]
