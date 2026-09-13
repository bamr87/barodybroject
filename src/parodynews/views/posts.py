"""
File: posts.py
Description: Views for creating, editing, and publishing posts
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1
- PyYAML: >=6.0

Usage: Included via parodynews URL routing.
"""

import functools

import yaml
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from github import Github
from github.GithubException import GithubException

from ..forms import PostForm, PostFrontMatterForm
from ..mixins import ModelFieldsMixin
from ..models import AppConfig, Post, PostFrontMatter, PostVersion


class PublicationError(Exception):
    """A publication failure carrying a message that is safe to show a reader.

    Raised rather than returned so the caller cannot mistake a failure for a
    pull request URL and `redirect()` to it.
    """

    def __init__(self, message, *, url=None):
        super().__init__(message)
        self.message = message
        self.url = url


class ManagePostView(LoginRequiredMixin, ModelFieldsMixin, TemplateView):
    """
    Comprehensive post management interface for content creators.

    Provides unified interface for managing blog posts and articles,
    including creation, editing, publishing workflows.
    """

    model = Post
    template_name = "parodynews/pages_post_detail.html"

    def get(self, request, post_id=None):
        """Handle GET requests for post management interface."""
        if post_id:
            post = Post.objects.get(pk=post_id)
            post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)
            form_post = PostForm(instance=post)
            form_post_frontmatter = PostFrontMatterForm(instance=post_frontmatter)

        else:
            post = None
            post_frontmatter = None
            form_post = None
            form_post_frontmatter = None

        form_post = PostForm(instance=post)
        form_post_frontmatter = PostFrontMatterForm(instance=post_frontmatter)

        post_list = Post.objects.filter(user=request.user)
        fields, display_fields = self.get_model_fields()

        context = {
            "post": post,
            "form_post": form_post,
            "form_post_frontmatter": form_post_frontmatter,
            "post_list": post_list,
            "fields": fields,
            "display_fields": display_fields,
        }

        return render(request, self.template_name, context)

    def post(self, request, post_id=None):
        """Handle POST requests for post management operations."""
        if request.POST.get("_method") == "delete":
            return self.delete(request)

        if request.POST.get("_method") == "save":
            return self.save(request, post_id)

        if request.POST.get("_method") == "publish":
            return self.publish(request)

        return redirect("manage_post")

    def delete(self, request, post_id=None):
        """Delete a post from the system."""
        post_id = request.POST.get("post_id")
        post = Post.objects.get(id=post_id)
        post.delete()

        messages.success(request, "Post deleted successfully.")

        return redirect("manage_post")

    def save(self, request, post_id=None):
        """Save post changes without publishing."""
        post_id = request.POST.get("post_id")

        form_post = PostForm(request.POST)
        form_post_frontmatter = PostFrontMatterForm(request.POST)

        post_list = Post.objects.all()
        fields, display_fields = self.get_model_fields()

        if post_id:
            post = Post.objects.get(pk=post_id)
            post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)

            form_post = PostForm(request.POST, instance=post)
            form_post_frontmatter = PostFrontMatterForm(
                request.POST, instance=post_frontmatter
            )
        else:
            post = form_post.save(commit=False)
            post.user = request.user

        if form_post.is_valid() and form_post_frontmatter.is_valid():
            post_front_matter = form_post_frontmatter.save(commit=False)
            post_front_matter.save()

            post.save()

            messages.success(request, "Post and front matter saved successfully.")
            return redirect("post_detail", post_id=post.id)
        else:
            if not form_post.is_valid():
                messages.error(request, form_post.errors)
            if not form_post_frontmatter.is_valid():
                messages.error(request, form_post_frontmatter.errors)

            context = {
                "post": post,
                "form_post": form_post,
                "form_post_frontmatter": form_post_frontmatter,
                "post_list": post_list,
                "fields": fields,
                "display_fields": display_fields,
            }

            return render(request, self.template_name, context)

    def publish(self, request, post_id=None):
        """Publish post to GitHub Pages/Jekyll.

        Every failure below leaves the reader on `manage_post` with a
        `messages.error` naming what went wrong and what to change. Nothing
        raises out of this view for a bad credential, a missing repository or
        branch, a pull request that already exists, or a rate limit.
        """
        post_id = request.POST.get("post_id")

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            messages.error(
                request,
                f"Could not publish: post {post_id} no longer exists. "
                "It may have been deleted in another tab.",
            )
            return redirect("manage_post")

        try:
            post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)
        except PostFrontMatter.DoesNotExist:
            messages.error(
                request,
                "Could not publish: this post has no front matter. Add a title, "
                "author, publication date and slug, then publish again.",
            )
            return redirect("manage_post")

        if post_frontmatter.published_at is None:
            messages.error(
                request,
                "Could not publish: this post has no publication date. Set one "
                "in the front matter, then publish again.",
            )
            return redirect("manage_post")

        frontmatter = {
            "title": post_frontmatter.title,
            "description": post_frontmatter.description,
            "author": post_frontmatter.author,
            "published_at": post_frontmatter.published_at.strftime("%Y-%m-%d"),
            "slug": post_frontmatter.slug,
        }

        frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False)

        data = f"---\n{frontmatter_yaml}---\n\n{post.post_content}"

        latest_version = post.versions.order_by("-version_number").first()
        version_number = latest_version.version_number + 1 if latest_version else 1

        post_version = PostVersion.objects.create(
            post=post,
            version_number=version_number,
            content=data,
            frontmatter=frontmatter_yaml,
        )

        app_config = AppConfig.objects.first()
        if not app_config:
            messages.error(request, "GitHub configuration is missing.")
            return redirect("manage_post")

        try:
            github_url = push_to_github_and_create_pr(
                post, post_version, app_config, post_frontmatter=post_frontmatter
            )
        except PublicationError as exc:
            messages.error(request, exc.message)
            return redirect("manage_post")

        return redirect(github_url)

    def get_context_data(self, **kwargs):
        from django.shortcuts import get_object_or_404

        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, id=post_id)
        context["post"] = post
        return context


def _github_detail(exc):
    """Pull GitHub's own explanation out of an exception, if it carries one."""
    data = getattr(exc, "data", None)
    if isinstance(data, dict) and data.get("message"):
        return str(data["message"])
    return str(exc)


def _github_error_message(exc, *, action, repo_name, base_branch):
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
            f"API rate limit has been exceeded — wait for it to reset and "
            f"publish again — or the configured token has no write access to "
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


def _find_open_pull_request(repo, head_branch, base_branch):
    """Best-effort URL of the pull request already open for `head_branch`.

    Only ever used to enrich an error message, so a failure here must not
    replace the error being reported — it degrades to "no link available".
    """
    try:
        for pull in repo.get_pulls(state="open", base=base_branch):
            if pull.head.ref == head_branch:
                return pull.html_url
    except GithubException:
        return None
    return None


def push_to_github_and_create_pr(post, post_version, app_config, post_frontmatter=None):
    """
    Push post content to GitHub repository and create pull request.

    Args:
        post: The post object being published
        post_version: Specific version of the post content
        app_config: Application configuration with GitHub settings
        post_frontmatter: The post's front matter. Fetched if not supplied,
            but the caller usually already holds it.

    Returns:
        str: URL of the created pull request

    Raises:
        PublicationError: any GitHub failure, carrying a message the caller can
            show the reader directly. Never returns `None` on failure — the
            caller redirects to what this returns.
    """
    token = app_config.github_pages_token
    repo_name = app_config.github_pages_repo
    base_branch = app_config.github_pages_branch
    post_dir = app_config.github_pages_post_dir.rstrip("/")

    describe = functools.partial(
        _github_error_message, repo_name=repo_name, base_branch=base_branch
    )

    if post_frontmatter is None:
        post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)

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
        # Only a 404 means "the branch is not there yet". Anything else is a
        # real failure and must not be answered by creating a branch.
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

    content = post_version.content

    filename = f"{post_frontmatter.slug.lower().replace(' ', '-')}.md"
    date_str = post_frontmatter.published_at.strftime("%Y-%m-%d")
    formatted_filename = f"{date_str}-{filename}"
    repo_path = f"{post_dir}/{formatted_filename}"

    try:
        existing_file = repo.get_contents(repo_path, ref=new_branch_name)
    except GithubException as exc:
        # As above: 404 means "no such file yet, create it". A 403 rate limit
        # or a 401 must surface as itself, not as a confusing create_file
        # failure.
        if exc.status != 404:
            raise PublicationError(
                describe(exc, action=f"read {repo_path} in {repo_name}")
            ) from exc
        existing_file = None

    try:
        if existing_file is None:
            repo.create_file(
                path=repo_path,
                message=f"Add post {post.content_detail.title}",
                content=content,
                branch=new_branch_name,
            )
        else:
            repo.update_file(
                path=repo_path,
                message=f"Update post {post.content_detail.title}",
                content=content,
                sha=existing_file.sha,
                branch=new_branch_name,
            )
    except GithubException as exc:
        raise PublicationError(
            describe(exc, action=f"write {repo_path} in {repo_name}")
        ) from exc

    try:
        pr = repo.create_pull(
            title=f"Add post {post.content_detail.title}",
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
