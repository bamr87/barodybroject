"""
File: test_services_publishing.py
Description: Tests for parodynews.services.publishing — post creation, rendering, versioning
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 1.0.0

Dependencies:
- django
- pytest-django
- PyYAML

Usage: python -m pytest parodynews/tests/test_services_publishing.py (run from src/)

The GitHub call itself is not exercised — it needs a repository and a token —
but everything up to it is: what gets rendered, what gets versioned, and the
guard that stops an unconfigured deployment from trying.
"""

import pytest
import yaml

from parodynews.models import AppConfig, Post, PostFrontMatter, PostVersion
from parodynews.services import publishing as publishing_services

pytestmark = pytest.mark.django_db


# --------------------------------------------------------------------------- #
# frontmatter_for
# --------------------------------------------------------------------------- #
def test_front_matter_is_created_from_the_content_detail(post, content_detail):
    """A post promoted from a message may have no front matter yet; publishing
    it must not fail for want of one."""
    front_matter = publishing_services.frontmatter_for(post)
    assert front_matter.title == content_detail.title
    assert front_matter.slug == content_detail.slug


def test_existing_front_matter_is_reused(post):
    first = publishing_services.frontmatter_for(post)
    first.title = "Edited by hand"
    first.save()

    assert publishing_services.frontmatter_for(post).title == "Edited by hand"


def test_front_matter_falls_back_when_the_post_has_no_content_detail():
    orphan = Post.objects.create(post_content="body")
    assert publishing_services.frontmatter_for(orphan).title == f"Post {orphan.pk}"


# --------------------------------------------------------------------------- #
# render_post
# --------------------------------------------------------------------------- #
def test_render_produces_yaml_front_matter_then_the_body(post):
    rendered = publishing_services.render_post(post)

    assert rendered.document.startswith("---\n")
    head, body = rendered.document.split("---\n", 2)[1:]
    parsed = yaml.safe_load(head)
    assert parsed["title"] == post.content_detail.title
    assert body.strip() == post.post_content.strip()


def test_render_names_the_file_for_jekyll(post):
    """Jekyll requires `YYYY-MM-DD-slug.md`, so the date and slug both matter."""
    rendered = publishing_services.render_post(post)
    date = post.content_detail.published_at.strftime("%Y-%m-%d")
    assert rendered.filename == f"{date}-cat-independence.md"


def test_render_keeps_unicode_readable(post, content_detail):
    """`allow_unicode` is set, so an accented title is not escaped into
    `\\uXXXX` noise in the published file."""
    content_detail.title = "Le Chat Déclare son Indépendance"
    content_detail.save()
    PostFrontMatter.objects.filter(post=post).delete()

    rendered = publishing_services.render_post(post)
    assert "Déclare" in rendered.frontmatter_yaml


# --------------------------------------------------------------------------- #
# create_version
# --------------------------------------------------------------------------- #
def test_the_first_version_is_numbered_one(post):
    assert publishing_services.create_version(post).version_number == 1


def test_versions_increment(post):
    publishing_services.create_version(post)
    assert publishing_services.create_version(post).version_number == 2


def test_creating_a_version_stamps_the_filename_on_the_post(post):
    publishing_services.create_version(post)
    post.refresh_from_db()
    assert post.filename.endswith("-cat-independence.md")


def test_a_version_captures_the_document_at_that_moment(post):
    first = publishing_services.create_version(post)
    post.post_content = "# Rewritten"
    post.save()
    second = publishing_services.create_version(post)

    assert "Breaking News" in first.content
    assert "Rewritten" in second.content


# --------------------------------------------------------------------------- #
# create_post_from_message
# --------------------------------------------------------------------------- #
def test_a_message_becomes_a_draft_post_with_metadata(message, user):
    post = publishing_services.create_post_from_message(message, user)

    assert post.status == "draft"
    assert post.user == user
    assert post.message == message
    assert post.post_content == message.text
    assert post.content_detail is not None
    assert PostFrontMatter.objects.filter(post=post).exists()


def test_an_empty_message_cannot_become_a_post(thread):
    from parodynews.models import Message

    empty = Message.objects.create(thread=thread, status="failed", error="boom")
    with pytest.raises(ValueError, match="no content"):
        publishing_services.create_post_from_message(empty, None)


# --------------------------------------------------------------------------- #
# publish_post — the configuration guard
# --------------------------------------------------------------------------- #
def test_publishing_without_configuration_is_refused(post):
    with pytest.raises(
        publishing_services.PublishingNotConfigured, match="not configured"
    ):
        publishing_services.publish_post(post)


def test_publishing_without_a_token_is_refused(post):
    AppConfig.objects.create(github_pages_repo="bamr87/blog", github_pages_token="")
    with pytest.raises(publishing_services.PublishingNotConfigured):
        publishing_services.publish_post(post)


def test_a_refused_publish_creates_no_version(post):
    """The guard runs before the snapshot, so a misconfigured deployment does
    not accumulate versions that were never published."""
    with pytest.raises(publishing_services.PublishingNotConfigured):
        publishing_services.publish_post(post)
    assert PostVersion.objects.count() == 0
