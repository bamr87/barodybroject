# serializers.py
from rest_framework import serializers
from .models import (
    Assistant,
    AssistantGroup,
    ContentItem,
    ContentDetail,
    Thread,
    Message,
    Post,
    PostFrontMatter,
    JSONSchema,
    PoweredBy,
    MyObject,
    GeneralizedCodes,
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


class MyObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyObject
        fields = "__all__"


class GeneralizedCodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralizedCodes
        fields = "__all__"
