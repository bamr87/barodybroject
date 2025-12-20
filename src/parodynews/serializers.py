# serializers.py
"""
Django REST Framework serializers for parodynews application.

Organized by model category matching the new models package structure.
"""

from rest_framework import serializers

from .models import (  # AI models; Content models; Deprecated models; Conversation models; Publishing models; Config models
    Assistant,
    AssistantGroup,
    ContentDetail,
    ContentItem,
    GeneralizedCodes,
    JSONSchema,
    Message,
    MyObject,
    Post,
    PostFrontMatter,
    PoweredBy,
    Thread,
)


class AssistantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assistant
        fields = "__all__"


class AssistantGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantGroup
        fields = "__all__"


class ContentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        fields = "__all__"


class ContentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentDetail
        fields = "__all__"


class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class PostFrontMatterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostFrontMatter
        fields = "__all__"


class JSONSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JSONSchema
        fields = "__all__"


class PoweredBySerializer(serializers.ModelSerializer):
    class Meta:
        model = PoweredBy
        fields = "__all__"


# Deprecated models
class GeneralizedCodesSerializer(serializers.ModelSerializer):
    """DEPRECATED: This serializer is for a deprecated model."""

    class Meta:
        model = GeneralizedCodes
        fields = "__all__"


class MyObjectSerializer(serializers.ModelSerializer):
    """DEPRECATED: This serializer is for a deprecated model."""

    class Meta:
        model = MyObject
        fields = "__all__"
