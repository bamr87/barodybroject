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

import functools
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


class PublicationError(Exception):
    """A publication failure carrying a message that is safe to show a reader.

    Raised rather than returned so a caller cannot mistake a failure for a
    pull request URL. `url` is set only when the failure itself points at
    something worth linking — today, a pull request that is already open.
    """

    def __init__(self, message: str, *, url: str | None = None):
        super().__init__(message)
        self.message = message
        self.url = url


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


def _github_detail(exc) -> str:
    """Pull GitHub's own explanation out of an exception, if it carries one."""
    data = getattr(exc, "data", None)
    if isinstance(data, dict) and data.get("message"):
        return str(data["message"])
    return str(exc)


def _github_error_message(exc, *, action: str, repo_name: str, base_branch: str) -> str:
    """Translate a `GithubException` into something the reader can act on."""
    status = getattr(exc, "status", None)

    if status == 401:
        return (
            f"Could not {action}: GitHub rejected the credential (401). The "
            "GitHub token in the application configuration is invalid or has "
            "expired — update the token and publish again."
        )
    if status == 403:
        return (
            f"Could not {action}: GitHub refused the request (403). Either the "
            "API rate limit has been exceeded — wait for it to reset and "
            "publish again — or the configured token has no write access to "
            f"{repo_name}."
        )
    if status == 404:
        return (
            f"Could not {action}: GitHub returned 404. Check that the "
            f"repository {repo_name} and the branch {base_branch} exist and "
            "that the configured token can see them."
        )
    return (
        f"Could not {action}: GitHub returned an error "
        f"({status}). {_github_detail(exc)}"
    )


def _find_open_pull_request(repo, head_branch: str, base_branch: str) -> str | None:
    """Best-effort URL of the pull request already open for `head_branch`.

    Only ever used to enrich an error message, so a failure here must not
    replace the error being reported — it degrades to "no link available".
    """
    from github.GithubException import GithubException

    try:
        for pull in repo.get_pulls(state="open", base=base_branch):
            if pull.head.ref == head_branch:
                return pull.html_url
    except GithubException:
        return None
    return None


def push_to_github_and_create_pr(
    post: Post, post_version: PostVersion, app_config: AppConfig
) -> str:
    """Push the version to a branch of the configured repo and open a PR.

    Every GitHub failure below is translated into a `PublicationError` whose
    message names what failed and what the reader can change. A 404 is the
    only status that means "not there yet, create it" — anything else is a
    real failure and must surface as itself rather than being answered with a
    second, unrelated write.

    Returns:
        str: URL of the created pull request

    Raises:
        PublicationError: any GitHub failure, carrying a reader-facing message.
    """
    from github import Github
    from github.GithubException import GithubException

    token = app_config.github_pages_token
    repo_name = app_config.github_pages_repo
    base_branch = app_config.github_pages_branch or "main"
    post_dir = (app_config.github_pages_post_dir or "posts/").rstrip("/")

    describe = functools.partial(
        _github_error_message, repo_name=repo_name, base_branch=base_branch
    )
    new_branch_name = f"publish/{post.id}-v{post_version.version_number}"

    try:
        g = Github(token)
        repo = g.get_repo(repo_name)
        main_branch = repo.get_branch(base_branch)
    except GithubException as exc:
        raise PublicationError(
            describe(exc, action=f"open the repository {repo_name}")
        ) from exc

    try:
        repo.get_branch(new_branch_name)
    except GithubException as exc:
        # Only a 404 means "the branch is not there yet". A 401 or a rate-limit
        # 403 must not be answered by trying to create a branch.
        if exc.status != 404:
            raise PublicationError(
                describe(exc, action=f"look up the branch {new_branch_name}")
            ) from exc
        try:
            repo.create_git_ref(
                ref=f"refs/heads/{new_branch_name}", sha=main_branch.commit.sha
            )
        except GithubException as create_exc:
            raise PublicationError(
                describe(create_exc, action=f"create the branch {new_branch_name}")
            ) from create_exc

    rendered = render_post(post)
    repo_path = f"{post_dir}/{rendered.filename}"
    title = str(post)

    try:
        existing_file = repo.get_contents(repo_path, ref=new_branch_name)
    except GithubException as exc:
        # As above: 404 means "no such file yet, create it". Anything else —
        # an expired token, an exhausted rate limit — must be reported as
        # itself, not as a confusing `create_file` failure.
        if exc.status != 404:
            raise PublicationError(
                describe(exc, action=f"read {repo_path} in {repo_name}")
            ) from exc
        existing_file = None

    try:
        if existing_file is None:
            repo.create_file(
                path=repo_path,
                message=f"Add post {title}",
                content=post_version.content,
                branch=new_branch_name,
            )
        else:
            repo.update_file(
                path=repo_path,
                message=f"Update post {title}",
                content=post_version.content,
                sha=existing_file.sha,
                branch=new_branch_name,
            )
    except GithubException as exc:
        raise PublicationError(
            describe(exc, action=f"write {repo_path} in {repo_name}")
        ) from exc

    try:
        pr = repo.create_pull(
            title=f"Add post {title}",
            body="Please review the new post.",
            head=new_branch_name,
            base=base_branch,
        )
    except GithubException as exc:
        if exc.status == 422:
            existing_url = _find_open_pull_request(repo, new_branch_name, base_branch)
            if existing_url:
                raise PublicationError(
                    "A pull request for this post version is already open: "
                    f"{existing_url}. Review or close it, then publish again.",
                    url=existing_url,
                ) from exc
            raise PublicationError(
                "GitHub would not open a pull request for this post version "
                f"({new_branch_name} into {base_branch}). A pull request for it "
                "may already exist, or the branch may have nothing to merge. "
                f"GitHub said: {_github_detail(exc)}"
            ) from exc
        raise PublicationError(
            describe(exc, action=f"open the pull request for {new_branch_name}")
        ) from exc

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
