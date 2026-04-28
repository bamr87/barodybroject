"""
File: __init__.py
Description: View package for parodynews (template, CRUD, API, and AI workflows)
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: from parodynews.views.base import index
"""

# Base views
from .base import FooterView, UserLoginView, index

# Content management views
from .content import ManageContentView

# Thread and message views
from .threads import ManageMessageView, ProcessContentView

# Assistant management views
from .assistants import (
    ManageAssistantGroupsView,
    ManageAssistantsView,
    get_assistant_details,
)

# Post management views
from .posts import ManagePostView, push_to_github_and_create_pr

# Schema management views
from .schemas import create_schema, delete_schema, edit_schema, export_schema, list_schemas

# REST API ViewSets
from .api import (
    AssistantGroupViewSet,
    AssistantViewSet,
    ContentDetailViewSet,
    ContentItemViewSet,
    JSONSchemaViewSet,
    MessageViewSet,
    PostFrontMatterViewSet,
    PostViewSet,
    PoweredByViewSet,
    ThreadViewSet,
)

# Utility views and functions
from .utils import post_detail, send_welcome_email

__all__ = [
    # Base
    "FooterView",
    "UserLoginView",
    "index",
    # Content
    "ManageContentView",
    # Threads
    "ProcessContentView",
    "ManageMessageView",
    # Assistants
    "ManageAssistantsView",
    "ManageAssistantGroupsView",
    "get_assistant_details",
    # Posts
    "ManagePostView",
    "push_to_github_and_create_pr",
    # Schemas
    "list_schemas",
    "create_schema",
    "edit_schema",
    "export_schema",
    "delete_schema",
    # API ViewSets
    "AssistantViewSet",
    "AssistantGroupViewSet",
    "ContentItemViewSet",
    "ContentDetailViewSet",
    "ThreadViewSet",
    "MessageViewSet",
    "PostViewSet",
    "PostFrontMatterViewSet",
    "JSONSchemaViewSet",
    "PoweredByViewSet",
    # Utils
    "post_detail",
    "send_welcome_email",
]

