"""
File: publishing.py
Description: Turn messages into posts, version them, and publish to GitHub Pages
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1
- PyYAML: >=6.0
- pygithub: >=2.5

Usage:
    from parodynews.services import publishing
    post = publishing.create_post_from_message(message, user)
    version, url = publishing.publish_post(post)
"""

from __future__ import annotations

from dataclasses import dataclass

import yaml
from django.db import transaction

from parodynews.ai import AIProvider
from parodynews.models import (
    AppConfig,
    ContentDetail,
    ContentItem,
    Message,
    Post,
    PostFrontMatter,
    PostVersion,
)

from .content import apply_content_detail, generate_content_detail


class PublishingNotConfigured(Exception):
    """GitHub publishing settings are missing."""


@dataclass
class RenderedPost:
    frontmatter_yaml: str
    document: str
    filename: str


def frontmatter_for(post: Post) -> PostFrontMatter:
    """The post's front matter, created from its content detail when missing."""
    try:
        return post.front_matter
    except PostFrontMatter.DoesNotExist:
        detail = post.content_detail
        return PostFrontMatter.objects.create(
            post=post,
            title=(detail.title if detail else f"Post {post.pk}")[:255],
            description=(detail.description if detail else ""),
            author=(detail.author if detail else "")[:100],
            published_at=(detail.published_at if detail else post.created_at),
            slug=(detail.slug if detail else f"post-{post.pk}")[:255],
        )


def render_post(post: Post) -> RenderedPost:
    """Render the Jekyll document (YAML front matter + Markdown body)."""
    front_matter = frontmatter_for(post)
    data = {
        "title": front_matter.title,
        "description": front_matter.description,
        "author": front_matter.author,
        "published_at": front_matter.published_at.strftime("%Y-%m-%d"),
        "slug": front_matter.slug,
    }
    frontmatter_yaml = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    document = f"---\n{frontmatter_yaml}---\n\n{post.post_content}"
    date_str = front_matter.published_at.strftime("%Y-%m-%d")
    slug = front_matter.slug.lower().replace(" ", "-")
    return RenderedPost(frontmatter_yaml, document, f"{date_str}-{slug}.md")


@transaction.atomic
def create_post_from_message(
    message: Message, user=None, *, provider: AIProvider | None = None
) -> Post:
    """Promote an assistant reply to a draft post with generated metadata."""
    text = message.text
    if not text.strip():
        raise ValueError("the message has no content to publish")
    detail = ContentDetail.objects.create(user=user, title=text[:255])
    detail_data = generate_content_detail(text, provider=provider)
    apply_content_detail(detail, detail_data)
    ContentItem.objects.create(
        detail=detail,
        assistant=message.assistant,
        prompt=text,
        content_text=text,
        content_type="post",
    )
    post = Post.objects.create(
        thread=message.thread,
        message=message,
        assistant=message.assistant,
        content_detail=detail,
        post_content=text,
        user=user,
    )
    PostFrontMatter.objects.create(
        post=post,
        title=detail.title[:255],
        description=detail.description,
        author=detail.author[:100],
        published_at=detail.published_at,
        slug=detail.slug[:255],
    )
    return post


def create_version(post: Post) -> PostVersion:
    rendered = render_post(post)
    latest = post.versions.order_by("-version_number").first()
    number = latest.version_number + 1 if latest else 1
    version = PostVersion.objects.create(
        post=post,
        version_number=number,
        content=rendered.document,
        frontmatter=rendered.frontmatter_yaml,
    )
    if post.filename != rendered.filename:
        post.filename = rendered.filename
        post.save(update_fields=["filename"])
    return version


def push_to_github_and_create_pr(
    post: Post, post_version: PostVersion, app_config: AppConfig
) -> str:
    """Push the version to a branch of the configured repo and open a PR.

    Returns:
        str: URL of the created pull request
    """
    from github import Github
    from github.GithubException import GithubException

    token = app_config.github_pages_token
    repo_name = app_config.github_pages_repo
    base_branch = app_config.github_pages_branch or "main"
    post_dir = (app_config.github_pages_post_dir or "posts/").rstrip("/")

    g = Github(token)
    repo = g.get_repo(repo_name)
    main_branch = repo.get_branch(base_branch)
    new_branch_name = f"publish/{post.id}-v{post_version.version_number}"

    try:
        repo.get_branch(new_branch_name)
    except GithubException:
        repo.create_git_ref(
            ref=f"refs/heads/{new_branch_name}", sha=main_branch.commit.sha
        )

    rendered = render_post(post)
    repo_path = f"{post_dir}/{rendered.filename}"
    title = str(post)

    try:
        existing_file = repo.get_contents(repo_path, ref=new_branch_name)
        repo.update_file(
            path=repo_path,
            message=f"Update post {title}",
            content=post_version.content,
            sha=existing_file.sha,
            branch=new_branch_name,
        )
    except GithubException:
        repo.create_file(
            path=repo_path,
            message=f"Add post {title}",
            content=post_version.content,
            branch=new_branch_name,
        )

    pr = repo.create_pull(
        title=f"Add post {title}",
        body="Please review the new post.",
        head=new_branch_name,
        base=base_branch,
    )
    return pr.html_url


def publish_post(post: Post) -> tuple[PostVersion, str]:
    """Snapshot the post as a new version and open a GitHub pull request."""
    app_config = AppConfig.objects.first()
    if (
        app_config is None
        or not app_config.github_pages_repo
        or not app_config.github_pages_token
    ):
        raise PublishingNotConfigured(
            "GitHub publishing is not configured. Add the repository and token "
            "under App Configuration in the admin."
        )
    version = create_version(post)
    url = push_to_github_and_create_pr(post, version, app_config)
    if post.status != "published":
        post.status = "published"
        post.save(update_fields=["status"])
    return version, url
