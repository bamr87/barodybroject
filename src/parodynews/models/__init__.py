"""
File: __init__.py
Description: Aggregated exports for the parodynews models package
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2026-09-14
Version: 0.6.0

Dependencies:
- django: >=5.1

Usage: from parodynews.models import Post, Assistant, AIModel
"""

from .ai import (
    AIModel,
    Assistant,
    AssistantGroup,
    AssistantGroupMembership,
    JSONSchema,
)
from .config import AIProviderConfig, AppConfig, FieldDefaults, PoweredBy
from .content import ContentDetail, ContentItem
from .conversation import Message, Thread
from .publishing import Post, PostFrontMatter, PostPageConfigModel, PostVersion

__all__ = [
    # Config
    "AIProviderConfig",
    "AppConfig",
    "FieldDefaults",
    "PoweredBy",
    # AI
    "AIModel",
    "Assistant",
    "AssistantGroup",
    "AssistantGroupMembership",
    "JSONSchema",
    # Content
    "ContentDetail",
    "ContentItem",
    # Conversation
    "Message",
    "Thread",
    # Publishing
    "Post",
    "PostFrontMatter",
    "PostPageConfigModel",
    "PostVersion",
]
