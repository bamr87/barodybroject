"""
File: __init__.py
Description: Aggregated, backward-compatible exports for parodynews models package
Author: Barodybroject Team <team@example.com>
Created: 2025-11-30
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1

Usage: from parodynews.models import Post, Assistant
"""

# Configuration models
# AI models
from .ai import (
    Assistant,
    AssistantGroup,
    AssistantGroupMembership,
    JSONSchema,
    OpenAIModel,
)
from .config import AppConfig, FieldDefaults, PoweredBy

# Content models
from .content import ContentDetail, ContentItem

# Conversation models
from .conversation import Message, Thread

# Publishing models
from .publishing import Post, PostFrontMatter, PostPageConfigModel, PostVersion

# Define __all__ for explicit exports
__all__ = [
    # Config
    "AppConfig",
    "FieldDefaults",
    "PoweredBy",
    # AI
    "Assistant",
    "AssistantGroup",
    "AssistantGroupMembership",
    "JSONSchema",
    "OpenAIModel",
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
