"""
File: publishing.py
Description: Django models for post publishing, front matter, and versioning
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
 - django: >=5.1
 - martor: Markdown editor field

Usage: from parodynews.models.publishing import Post
"""

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from martor.models import MartorField


class PostPageConfigModel(models.Model):
    """Configuration for post pagination settings.

    Manages pagination settings for different post namespaces, allowing
    customized page sizes for different sections or post types.

    Attributes:
        namespace (str): Unique identifier for this config (max 255 chars, unique)
        paginated_by (int): Number of posts per page (default: 5)

    Examples:
        >>> from parodynews.models import PostPageConfigModel
        >>> config = PostPageConfigModel.objects.create(
        ...     namespace="news",
        ...     paginated_by=10
        ... )
        >>> blog_config = PostPageConfigModel.objects.create(
        ...     namespace="blog",
        ...     paginated_by=5
        ... )
        >>> print(config.namespace)
        news

    Note:
        Namespace must be unique. Use descriptive names that match your
        post categories or sections (e.g., 'news', 'blog', 'articles').
    """

    namespace = models.CharField(
        _("instance namespace"), default=None, max_length=255, unique=True
    )

    paginated_by = models.IntegerField(_("paginate size"), blank=False, default=5)

    class Meta:
        app_label = "parodynews"
        verbose_name = "Post Page Config"
        verbose_name_plural = "Post Page Configs"

    def __str__(self):
        return f"{self.namespace} ({self.paginated_by} per page)"


class Post(models.Model):
    """Published content post with markdown support.

    Represents a complete, publishable post with content, metadata, and
    relationships to content generation components. Supports markdown
    formatting via Martor field.

    Attributes:
        content_detail (ContentDetail): Metadata for this post
        thread (Thread): Conversation thread that generated this post
        message (Message): Specific message that created this post
        post_content (MartorField): Markdown content with editor support
        assistant (Assistant): Assistant that generated the content
        created_at (datetime): Timestamp when post was created
        updated_at (datetime): Timestamp of last update (auto-updated)
        filename (str): Target filename for file export (max 255 chars)
        status (str): Publication status (default: 'draft', max 100 chars)
        postfrontmatter (PostFrontMatter): Front matter metadata for this post
        user (User): User who owns this post

    Examples:
        >>> from parodynews.models import Post, ContentDetail, Assistant
        >>> from django.contrib.auth.models import User
        >>> detail = ContentDetail.objects.first()
        >>> assistant = Assistant.objects.get(name="News Writer")
        >>> user = User.objects.first()
        >>> post = Post.objects.create(
        ...     content_detail=detail,
        ...     post_content="# Breaking News\n\nLocal cat declares independence...",
        ...     assistant=assistant,
        ...     filename="2024-01-15-cat-independence.md",
        ...     status="published",
        ...     user=user
        ... )
        >>> print(post.get_absolute_url())
        /post/1/
        >>> print(post.get_display_fields())
        ['id', 'content_detail', 'thread', 'message', 'assistant', 'created_at', 'status']

    Status Values:
        - draft: Not published, work in progress
        - review: Ready for review
        - published: Publicly visible
        - archived: No longer active but preserved

    Note:
        updated_at is automatically set on every save(). The MartorField
        provides a rich markdown editor in the Django admin.
    """

    content_detail = models.ForeignKey(
        "parodynews.ContentDetail",
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
    )
    thread = models.ForeignKey(
        "parodynews.Thread", on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    message = models.ForeignKey(
        "parodynews.Message", on_delete=models.SET_NULL, null=True, related_name="posts"
    )
    post_content = MartorField()
    assistant = models.ForeignKey(
        "parodynews.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        related_name="posts",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    filename = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=100, default="draft")
    postfrontmatter = models.ForeignKey(
        "PostFrontMatter",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name="posts"
    )

    class Meta:
        app_label = "parodynews"
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.

        Returns:
            list: Field names for display
        """
        return [
            "id",
            "content_detail",
            "thread",
            "message",
            "assistant",
            "created_at",
            "status",
        ]

    def get_absolute_url(self):
        """Return the canonical URL for this post.

        Returns:
            str: URL path to post detail view
        """
        return reverse("post_detail", kwargs={"pk": self.pk})

    def __str__(self):
        """Return the post title from content_detail.

        Returns:
            str: The title from the related ContentDetail
        """
        if self.content_detail:
            return self.content_detail.title
        return f"Post {self.pk}"


class PostFrontMatter(models.Model):
    """YAML front matter metadata for post export.

    Stores metadata that will be included as YAML front matter when
    exporting posts to markdown files (Jekyll, Hugo, etc.).

    Attributes:
        post (Post): One-to-one relationship to parent post
        title (str): Post title for front matter (max 255 chars)
        description (str): Full text description
        author (str): Author name (max 100 chars)
        published_at (datetime): Publication date (default: now)
        slug (str): URL slug (max 255 chars, non-unique)

    Examples:
        >>> from parodynews.models import Post, PostFrontMatter
        >>> post = Post.objects.first()
        >>> frontmatter = PostFrontMatter.objects.create(
        ...     post=post,
        ...     title="Cat Independence Day",
        ...     description="A satirical look at feline autonomy",
        ...     author="ParodyNews Staff",
        ...     slug="cat-independence-day"
        ... )
        >>> print(frontmatter)
        Cat Independence Day
        >>> print(frontmatter.get_display_fields())
        ['post', 'title', 'author', 'published_at', 'slug']

    YAML Output Format:
        ---
        title: "Cat Independence Day"
        description: "A satirical look at feline autonomy"
        author: "ParodyNews Staff"
        date: "2024-01-15 10:30:00"
        slug: "cat-independence-day"
        ---

    Note:
        One-to-one relationship with Post ensures each post has at most
        one front matter configuration.
    """

    post = models.OneToOneField(
        Post, on_delete=models.CASCADE, related_name="front_matter"
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    author = models.CharField(max_length=100)
    published_at = models.DateTimeField(default=timezone.now)
    slug = models.SlugField(max_length=255, unique=False, default="slug")

    class Meta:
        app_label = "parodynews"
        verbose_name = "Post Front Matter"
        verbose_name_plural = "Post Front Matters"

    def get_display_fields(self):
        """Return list of fields to display in admin and list views.

        Returns:
            list: Field names ['post', 'title', 'author', 'published_at', 'slug']
        """
        return ["post", "title", "author", "published_at", "slug"]

    def __str__(self):
        """Return the front matter title.

        Returns:
            str: The title field value
        """
        return self.title


class PostVersion(models.Model):
    """Version history for posts.

    Tracks changes to post content and front matter over time, allowing
    rollback and audit trail functionality.

    Attributes:
        post (Post): Foreign key to the parent post
        version_number (int): Sequential version number
        content (str): Post content at this version
        created_at (datetime): Timestamp when version was created
        frontmatter (str): Front matter at this version (JSON or YAML string)

    Examples:
        >>> from parodynews.models import Post, PostVersion
        >>> post = Post.objects.first()
        >>> version = PostVersion.objects.create(
        ...     post=post,
        ...     version_number=1,
        ...     content=post.post_content,
        ...     frontmatter="title: Original Title"
        ... )
        >>> print(version)
        Version 1 of Post 1
    """

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    frontmatter = models.TextField()

    class Meta:
        app_label = "parodynews"
        verbose_name = "Post Version"
        verbose_name_plural = "Post Versions"
        ordering = ["post", "-version_number"]
        unique_together = [["post", "version_number"]]
        indexes = [
            models.Index(fields=["post", "-version_number"]),
        ]

    def __str__(self):
        return f"Version {self.version_number} of Post {self.post.id}"
