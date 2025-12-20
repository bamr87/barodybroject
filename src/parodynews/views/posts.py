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

import yaml
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from github import Github

from ..forms import PostForm, PostFrontMatterForm
from ..mixins import ModelFieldsMixin
from ..models import AppConfig, Post, PostFrontMatter, PostVersion


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
        """Publish post to GitHub Pages/Jekyll."""
        post_id = request.POST.get("post_id")
        post = Post.objects.get(id=post_id)

        post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)

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

        github_url = push_to_github_and_create_pr(post, post_version, app_config)

        return redirect(github_url)

    def get_context_data(self, **kwargs):
        from django.shortcuts import get_object_or_404
        context = super().get_context_data(**kwargs)
        post_id = self.kwargs.get("post_id")
        post = get_object_or_404(Post, id=post_id)
        context["post"] = post
        return context


def push_to_github_and_create_pr(post, post_version, app_config):
    """
    Push post content to GitHub repository and create pull request.

    Args:
        post: The post object being published
        post_version: Specific version of the post content
        app_config: Application configuration with GitHub settings

    Returns:
        str: URL of the created pull request
    """
    from github.GithubException import GithubException

    token = app_config.github_pages_token
    repo_name = app_config.github_pages_repo
    base_branch = app_config.github_pages_branch
    post_dir = app_config.github_pages_post_dir.rstrip("/")

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
    content = post_version.content

    post_frontmatter = PostFrontMatter.objects.get(post_id=post.id)

    filename = f"{post_frontmatter.slug.lower().replace(' ', '-')}.md"
    date_str = post_frontmatter.published_at.strftime("%Y-%m-%d")
    formatted_filename = f"{date_str}-{filename}"
    repo_path = f"{post_dir}/{formatted_filename}"

    try:
        existing_file = repo.get_contents(repo_path, ref=new_branch_name)
        repo.update_file(
            path=repo_path,
            message=f"Update post {post.content_detail.title}",
            content=content,
            sha=existing_file.sha,
            branch=new_branch_name,
        )
    except Exception:
        repo.create_file(
            path=repo_path,
            message=f"Add post {post.content_detail.title}",
            content=content,
            branch=new_branch_name,
        )

    pr = repo.create_pull(
        title=f"Add post {post.content_detail.title}",
        body="Please review the new post.",
        head=new_branch_name,
        base=base_branch,
    )
    return pr.html_url

