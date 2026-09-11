"""
File: test_models_publishing.py
Description: Unit tests for parodynews.models.publishing — PostPageConfigModel, Post, PostFrontMatter, PostVersion
Author: Barodybroject Team <team@example.com>
Created: 2026-09-11
Version: 1.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_models_publishing.py (run from src/)
"""

import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse

from parodynews.models import (
    ContentDetail,
    Post,
    PostFrontMatter,
    PostPageConfigModel,
    PostVersion,
)

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# PostPageConfigModel
# --------------------------------------------------------------------------- #
def test_post_page_config_round_trips():
    config = PostPageConfigModel.objects.create(namespace="news", paginated_by=10)
    stored = PostPageConfigModel.objects.get(pk=config.pk)
    assert (stored.namespace, stored.paginated_by) == ("news", 10)


def test_post_page_config_str_reports_the_page_size():
    config = PostPageConfigModel.objects.create(namespace="news", paginated_by=10)
    assert str(config) == "news (10 per page)"


def test_post_page_config_default_page_size():
    assert PostPageConfigModel.objects.create(namespace="blog").paginated_by == 5


def test_namespace_is_unique():
    PostPageConfigModel.objects.create(namespace="news")
    with pytest.raises(IntegrityError), transaction.atomic():
        PostPageConfigModel.objects.create(namespace="news")


# --------------------------------------------------------------------------- #
# Post
# --------------------------------------------------------------------------- #
def test_post_round_trips(post, content_detail, thread, message, assistant, user):
    stored = Post.objects.get(pk=post.pk)
    assert stored.content_detail == content_detail
    assert stored.thread == thread
    assert stored.message == message
    assert stored.assistant == assistant
    assert stored.user == user
    assert stored.post_content.startswith("# Breaking News")


def test_post_str_is_the_content_detail_title(post):
    assert str(post) == "Local Cat Declares Independence"


def test_post_str_falls_back_when_it_has_no_content_detail():
    """`content_detail` is SET_NULL, so this branch is reachable in production."""
    orphan = Post.objects.create(post_content="body")
    assert str(orphan) == f"Post {orphan.pk}"


def test_post_display_fields(post):
    assert post.get_display_fields() == [
        "id",
        "content_detail",
        "thread",
        "message",
        "assistant",
        "created_at",
        "status",
    ]


def test_post_absolute_url_resolves(post):
    """`get_absolute_url()` must return the route `urls.py` actually declares.

    This is the assertion that caught the `NoReverseMatch` fixed alongside these
    tests: the method passed `pk=` while `post_detail` is declared as
    `posts/<int:post_id>/`, so every call raised.
    """
    assert post.get_absolute_url() == reverse(
        "post_detail", kwargs={"post_id": post.pk}
    )
    assert post.get_absolute_url() == f"/posts/{post.pk}/"


def test_post_defaults():
    bare = Post.objects.create(post_content="body")
    assert bare.status == "draft"
    assert bare.filename == ""
    assert bare.created_at is not None
    assert bare.updated_at is not None


def test_updated_at_moves_on_every_save(post):
    """`auto_now`, unlike `created_at`'s `default=timezone.now`."""
    original_created = post.created_at
    original_updated = post.updated_at

    post.status = "published"
    post.save()
    post.refresh_from_db()

    assert post.updated_at > original_updated
    assert post.created_at == original_created


def test_deleting_the_content_detail_keeps_the_post(post, content_detail):
    """SET_NULL on all four content-side FKs — the published post outlives the
    machinery that generated it."""
    content_detail.delete()
    post.refresh_from_db()
    assert post.content_detail is None
    assert Post.objects.filter(pk=post.pk).exists()


def test_deleting_the_thread_keeps_the_post(post, thread):
    thread.delete()
    post.refresh_from_db()
    assert post.thread is None


def test_deleting_the_message_keeps_the_post(post, message):
    message.delete()
    post.refresh_from_db()
    assert post.message is None


def test_deleting_the_assistant_keeps_the_post(post, assistant):
    assistant.delete()
    post.refresh_from_db()
    assert post.assistant is None


def test_deleting_the_user_deletes_their_posts(post, user):
    """CASCADE — the one relation on Post that is not SET_NULL."""
    user.delete()
    assert not Post.objects.filter(pk=post.pk).exists()


def test_posts_are_newest_first():
    older = Post.objects.create(post_content="older")
    newer = Post.objects.create(post_content="newer")
    Post.objects.filter(pk=older.pk).update(
        created_at=newer.created_at.replace(year=newer.created_at.year - 1)
    )
    assert list(Post.objects.values_list("post_content", flat=True)) == [
        "newer",
        "older",
    ]


def test_the_content_detail_reaches_its_posts_by_related_name(post, content_detail):
    assert list(content_detail.posts.all()) == [post]


# --------------------------------------------------------------------------- #
# PostFrontMatter
# --------------------------------------------------------------------------- #
@pytest.fixture
def front_matter(db, post) -> PostFrontMatter:
    return PostFrontMatter.objects.create(
        post=post,
        title="Cat Independence Day",
        description="A satirical look at feline autonomy",
        author="ParodyNews Staff",
        slug="cat-independence-day",
    )


def test_front_matter_round_trips(front_matter, post):
    stored = PostFrontMatter.objects.get(pk=front_matter.pk)
    assert stored.post == post
    assert stored.title == "Cat Independence Day"
    assert stored.slug == "cat-independence-day"


def test_front_matter_str_is_the_title(front_matter):
    assert str(front_matter) == "Cat Independence Day"


def test_front_matter_display_fields(front_matter):
    assert front_matter.get_display_fields() == [
        "post",
        "title",
        "author",
        "published_at",
        "slug",
    ]


def test_a_post_has_at_most_one_front_matter(front_matter, post):
    """OneToOne, not ForeignKey — a second row for the same post is rejected."""
    with pytest.raises(IntegrityError), transaction.atomic():
        PostFrontMatter.objects.create(
            post=post, title="Duplicate", description="d", author="a"
        )


def test_deleting_the_post_deletes_its_front_matter(front_matter, post):
    post.delete()
    assert not PostFrontMatter.objects.filter(pk=front_matter.pk).exists()


def test_the_post_reaches_its_front_matter_by_related_name(front_matter, post):
    assert post.front_matter == front_matter


# --------------------------------------------------------------------------- #
# PostVersion
# --------------------------------------------------------------------------- #
@pytest.fixture
def version(db, post) -> PostVersion:
    return PostVersion.objects.create(
        post=post,
        version_number=1,
        content=post.post_content,
        frontmatter="title: Original Title",
    )


def test_post_version_round_trips(version, post):
    stored = PostVersion.objects.get(pk=version.pk)
    assert stored.post == post
    assert stored.version_number == 1
    assert stored.frontmatter == "title: Original Title"
    assert stored.created_at is not None


def test_post_version_str_names_the_version_and_post(version, post):
    assert str(version) == f"Version 1 of Post {post.pk}"


def test_a_version_number_is_unique_per_post(version, post):
    """`unique_together` — the audit trail is meaningless if two rows can claim
    the same version."""
    with pytest.raises(IntegrityError), transaction.atomic():
        PostVersion.objects.create(
            post=post, version_number=1, content="other", frontmatter=""
        )


def test_the_same_version_number_is_allowed_on_a_different_post(version, post):
    other = Post.objects.create(post_content="another post")
    duplicate = PostVersion.objects.create(
        post=other, version_number=1, content="c", frontmatter=""
    )
    assert duplicate.version_number == version.version_number


def test_deleting_the_post_deletes_its_versions(version, post):
    post.delete()
    assert not PostVersion.objects.filter(pk=version.pk).exists()


def test_versions_are_newest_first_within_a_post(version, post):
    PostVersion.objects.create(
        post=post, version_number=2, content="v2", frontmatter=""
    )
    numbers = list(
        PostVersion.objects.filter(post=post).values_list("version_number", flat=True)
    )
    assert numbers == [2, 1]


def test_the_post_reaches_its_versions_by_related_name(version, post):
    assert list(post.versions.all()) == [version]


# --------------------------------------------------------------------------- #
# Completeness guard for issue #51
# --------------------------------------------------------------------------- #
def test_every_exported_model_has_a_test_module():
    """A reviewer should not have to diff a grep by hand.

    `parodynews.models.__all__` is the package's public model list; this asserts
    each name is referenced by one of the six `test_models_*.py` modules, so a
    model added later without tests fails here rather than passing silently.
    """
    import re
    from pathlib import Path

    import parodynews.models as models_pkg

    tests_dir = Path(__file__).parent
    sources = "\n".join(
        path.read_text() for path in sorted(tests_dir.glob("test_models_*.py"))
    )
    untested = [
        name for name in models_pkg.__all__ if not re.search(rf"\b{name}\b", sources)
    ]
    assert untested == [], f"models with no test module reference: {untested}"


def test_the_abstract_base_is_accounted_for():
    """`TimestampedModel` is in the `^class .*(models\\.` grep but absent from
    `__all__` because it is abstract — covered by `test_models_base.py`."""
    from parodynews.models.base import TimestampedModel

    assert TimestampedModel._meta.abstract is True


def test_content_detail_is_reachable_from_the_package_root():
    assert ContentDetail.__module__ == "parodynews.models.content"
