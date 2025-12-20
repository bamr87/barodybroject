"""
File: config.py
Description: Django models for application-wide configuration (keys, settings, attribution)
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: from parodynews.models.config import AppConfig
"""

from django.core.cache import cache
from django.db import models
from django.utils import timezone


class PoweredBy(models.Model):
    """Configuration for 'Powered By' attribution links.
    
    This model stores information about technologies and services that power
    the application, typically displayed in the footer or about page.
    
    Attributes:
        name (str): Display name of the technology/service (max 100 chars)
        icon (str): CSS class or icon identifier for visual representation
        url (str): URL to the technology's website or documentation
    
    Examples:
        >>> powered_by = PoweredBy.objects.create(
        ...     name="OpenAI",
        ...     icon="fa-robot",
        ...     url="https://openai.com"
        ... )
        >>> str(powered_by)
        'OpenAI'
    """
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=100)
    url = models.URLField()

    class Meta:
        app_label = 'parodynews'
        verbose_name = 'Powered By'
        verbose_name_plural = 'Powered By'

    def __str__(self):
        """Return the name of the technology/service.
        
        Returns:
            str: The name field value
        """
        return self.name


class AppConfig(models.Model):
    """Application-wide configuration settings.
    
    Singleton model that stores API keys, project identifiers, and GitHub Pages
    configuration. Should only have one instance in the database.
    
    Attributes:
        api_key (str): OpenAI API key for authentication (max 255 chars)
        project_id (str): Project identifier for OpenAI API (max 255 chars)
        org_id (str): Organization identifier for OpenAI API (max 255 chars)
        github_pages_repo (str): GitHub repository for publishing (format: 'owner/repo')
        github_pages_branch (str): Target branch for publishing (default: 'main')
        github_pages_token (str): GitHub Personal Access Token for API authentication
        github_pages_post_dir (str): Directory path for posts (default: 'posts/')
    
    Note:
        API keys and tokens should be kept secure. Consider using environment
        variables or secret management systems in production.
    
    Examples:
        >>> config = AppConfig.objects.first()
        >>> if config:
        ...     print(f"Publishing to {config.github_pages_repo}")
        Publishing to username/my-blog
    """
    api_key = models.CharField(max_length=255)
    project_id = models.CharField(max_length=255)
    org_id = models.CharField(max_length=255)
    github_pages_repo = models.CharField(max_length=255)
    github_pages_branch = models.CharField(max_length=255, default="main")
    github_pages_token = models.CharField(max_length=255)
    github_pages_post_dir = models.CharField(max_length=255, default="posts/")

    class Meta:
        app_label = 'parodynews'
        verbose_name = 'App Configuration'
        verbose_name_plural = 'App Configurations'

    def __str__(self):
        """Return a human-readable string representation.
        
        Returns:
            str: Always returns 'App Configuration'
        """
        return "App Configuration"


class FieldDefaults(models.Model):
    """Stores default values grouped by type for model fields.
    
    Provides centralized default value management for dynamically configuring
    model instances. Supports multiple models with their field defaults in
    a single JSON structure.
    
    Attributes:
        type (str): Category or purpose of these defaults (max 255 chars)
        defaults (list): List of model definitions with fields and default values
    
    JSON Structure:
        defaults = [
            {
                "model_name": "MyModel",
                "fields": {
                    "field1": "some default",
                    "field2": 42
                }
            },
            ...
        ]
    
    Examples:
        >>> from parodynews.models import FieldDefaults
        >>> defaults = FieldDefaults.objects.create(
        ...     type="post_defaults",
        ...     defaults=[
        ...         {
        ...             "model_name": "Post",
        ...             "fields": {
        ...                 "status": "draft",
        ...                 "author": "ParodyNews Staff"
        ...             }
        ...         },
        ...         {
        ...             "model_name": "ContentDetail",
        ...             "fields": {
        ...                 "keywords": ["news", "parody"],
        ...                 "description": "AI-generated content"
        ...             }
        ...         }
        ...     ]
        ... )
        >>> print(defaults)
        Defaults for post_defaults
    
    Note:
        Saving this model clears the 'field_defaults' cache to ensure
        updated defaults are immediately available.
    """

    type = models.CharField(max_length=255, default="default_type")
    defaults = models.JSONField(
        default=list,
        help_text="A list of model definitions with their fields and default values.",
    )

    class Meta:
        app_label = 'parodynews'
        verbose_name = 'Field Defaults'
        verbose_name_plural = 'Field Defaults'

    def __str__(self):
        """Return the type description.
        
        Returns:
            str: Formatted string 'Defaults for {type}'
        """
        return f"Defaults for {self.type}"

    def save(self, *args, **kwargs):
        """Clear cached defaults and save.
        
        Ensures the cache is invalidated whenever defaults are updated.
        """
        # Clear cached defaults when updated
        cache.delete("field_defaults")
        super().save(*args, **kwargs)

