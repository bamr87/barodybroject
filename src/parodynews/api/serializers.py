"""
File: serializers.py
Description: Django REST Framework serializers for the parodynews API
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- djangorestframework: >=3.15
"""

from __future__ import annotations

from django.contrib.auth.models import User
from rest_framework import serializers

from parodynews.ai import available_providers
from parodynews.models import (
    AIModel,
    AIProviderConfig,
    Assistant,
    AssistantGroup,
    AssistantGroupMembership,
    ContentDetail,
    ContentItem,
    JSONSchema,
    Message,
    Post,
    PostFrontMatter,
    PostVersion,
    PoweredBy,
    Thread,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = fields


# ------------------------------------------------------------------ AI config
class AIModelSerializer(serializers.ModelSerializer):
    label = serializers.CharField(read_only=True)

    class Meta:
        model = AIModel
        fields = [
            "id",
            "provider",
            "model_id",
            "display_name",
            "description",
            "is_active",
            "label",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_provider(self, value):
        if value not in available_providers():
            raise serializers.ValidationError(f"Unknown provider {value!r}.")
        return value


class AIProviderConfigSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        style={"input_type": "password"},
    )
    has_credential = serializers.BooleanField(read_only=True)

    class Meta:
        model = AIProviderConfig
        fields = [
            "id",
            "provider",
            "display_name",
            "api_key",
            "has_credential",
            "base_url",
            "organization_id",
            "project_id",
            "default_model",
            "is_default",
            "is_enabled",
            "extra",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate_provider(self, value):
        if value not in available_providers():
            raise serializers.ValidationError(f"Unknown provider {value!r}.")
        return value

    def validate(self, attrs):
        if attrs.get("is_default") and attrs.get("is_enabled") is False:
            raise serializers.ValidationError(
                {"is_default": "The default provider must be enabled."}
            )
        return attrs


class JSONSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = JSONSchema
        fields = ["id", "name", "description", "schema"]


# -------------------------------------------------------------- assistants
class AssistantGroupSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssistantGroup
        fields = ["id", "name"]


class AssistantSerializer(serializers.ModelSerializer):
    model_detail = AIModelSerializer(source="model", read_only=True)
    json_schema_name = serializers.CharField(
        source="json_schema.name", read_only=True, default=""
    )
    provider = serializers.CharField(read_only=True)
    groups = AssistantGroupSummarySerializer(
        source="assistant_groups", many=True, read_only=True
    )

    class Meta:
        model = Assistant
        fields = [
            "id",
            "name",
            "description",
            "instructions",
            "prompt",
            "model",
            "model_detail",
            "provider",
            "remote_id",
            "json_schema",
            "json_schema_name",
            "temperature",
            "top_p",
            "tools",
            "metadata",
            "response_format",
            "groups",
            "created_at",
        ]
        read_only_fields = ["id", "remote_id", "created_at"]


class AssistantGroupMembershipSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(
        source="assistant.name", read_only=True, default=""
    )

    class Meta:
        model = AssistantGroupMembership
        fields = ["id", "assistant", "assistant_name", "position"]
        read_only_fields = ["id"]


class AssistantGroupSerializer(serializers.ModelSerializer):
    memberships = AssistantGroupMembershipSerializer(
        source="assistantgroupmembership_set", many=True, required=False
    )

    class Meta:
        model = AssistantGroup
        fields = [
            "id",
            "name",
            "group_type",
            "sequence",
            "is_active",
            "priority",
            "created_at",
            "memberships",
        ]
        read_only_fields = ["id", "created_at"]

    def _replace_memberships(self, group: AssistantGroup, memberships) -> None:
        group.assistantgroupmembership_set.all().delete()
        for index, item in enumerate(memberships):
            AssistantGroupMembership.objects.create(
                assistantgroup=group,
                assistant=item.get("assistant"),
                position=(
                    item.get("position")
                    if item.get("position") is not None
                    else index + 1
                ),
            )

    def create(self, validated_data):
        memberships = validated_data.pop("assistantgroupmembership_set", None)
        group = super().create(validated_data)
        if memberships is not None:
            self._replace_memberships(group, memberships)
        return group

    def update(self, instance, validated_data):
        memberships = validated_data.pop("assistantgroupmembership_set", None)
        group = super().update(instance, validated_data)
        if memberships is not None:
            self._replace_memberships(group, memberships)
        return group


# ------------------------------------------------------------------ content
class ContentItemSerializer(serializers.ModelSerializer):
    assistant_name = serializers.CharField(
        source="assistant.name", read_only=True, default=""
    )

    class Meta:
        model = ContentItem
        fields = [
            "id",
            "detail",
            "line_number",
            "content_type",
            "content_text",
            "assistant",
            "assistant_name",
            "prompt",
        ]
        read_only_fields = ["id", "line_number"]


class ContentDetailSerializer(serializers.ModelSerializer):
    items = ContentItemSerializer(source="contentitem", many=True, read_only=True)
    # Convenience write-only fields so the first content item (the prompt)
    # can be created or updated together with its detail, like the old form.
    prompt = serializers.CharField(write_only=True, required=False, allow_blank=True)
    assistant = serializers.PrimaryKeyRelatedField(
        queryset=Assistant.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    content_text = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    user = UserSerializer(read_only=True)

    class Meta:
        model = ContentDetail
        fields = [
            "id",
            "title",
            "description",
            "author",
            "published_at",
            "slug",
            "keywords",
            "user",
            "items",
            "prompt",
            "assistant",
            "content_text",
        ]
        read_only_fields = ["id"]

    def _pop_item_fields(self, validated_data):
        return {
            key: validated_data.pop(key)
            for key in ("prompt", "assistant", "content_text")
            if key in validated_data
        }

    def create(self, validated_data):
        item_fields = self._pop_item_fields(validated_data)
        request = self.context.get("request")
        if request is not None and request.user.is_authenticated:
            validated_data.setdefault("user", request.user)
        detail = ContentDetail.objects.create(**validated_data)
        if item_fields:
            ContentItem.objects.create(
                detail=detail,
                prompt=item_fields.get("prompt", ""),
                assistant=item_fields.get("assistant"),
                content_text=item_fields.get("content_text", ""),
            )
        return detail

    def update(self, instance, validated_data):
        item_fields = self._pop_item_fields(validated_data)
        detail = super().update(instance, validated_data)
        if item_fields:
            item = detail.contentitem.order_by("line_number", "id").first()
            if item is None:
                item = ContentItem(detail=detail, prompt="", content_text="")
            for key, value in item_fields.items():
                setattr(
                    item, key, value if value is not None or key == "assistant" else ""
                )
            item.save()
        return detail


# ------------------------------------------------------------ conversation
class MessageSerializer(serializers.ModelSerializer):
    content_text = serializers.CharField(source="text", read_only=True)
    assistant_name = serializers.CharField(
        source="assistant.name", read_only=True, default=""
    )
    thread_name = serializers.CharField(
        source="thread.name", read_only=True, default=""
    )

    class Meta:
        model = Message
        fields = [
            "id",
            "thread",
            "thread_name",
            "role",
            "contentitem",
            "content_text",
            "assistant",
            "assistant_name",
            "status",
            "run_id",
            "provider",
            "model_id",
            "remote_id",
            "usage",
            "error",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "run_id",
            "provider",
            "model_id",
            "remote_id",
            "usage",
            "error",
        ]


class ThreadSerializer(serializers.ModelSerializer):
    assistant_group_name = serializers.CharField(
        source="assistant_group.name", read_only=True, default=""
    )
    message_count = serializers.IntegerField(source="messages.count", read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Thread
        fields = [
            "id",
            "name",
            "description",
            "assistant_group",
            "assistant_group_name",
            "provider",
            "remote_id",
            "user",
            "message_count",
            "created_at",
        ]
        read_only_fields = ["id", "provider", "remote_id", "created_at"]


class ThreadDetailSerializer(ThreadSerializer):
    messages = serializers.SerializerMethodField()

    class Meta(ThreadSerializer.Meta):
        fields = ThreadSerializer.Meta.fields + ["messages"]

    def get_messages(self, thread):
        return MessageSerializer(thread.ordered_messages(), many=True).data


# --------------------------------------------------------------- publishing
class PostFrontMatterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostFrontMatter
        fields = [
            "id",
            "post",
            "title",
            "description",
            "author",
            "published_at",
            "slug",
        ]
        read_only_fields = ["id"]


class PostVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostVersion
        fields = [
            "id",
            "post",
            "version_number",
            "content",
            "frontmatter",
            "created_at",
        ]
        read_only_fields = fields


class FrontMatterInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostFrontMatter
        fields = ["title", "description", "author", "published_at", "slug"]


class PostSerializer(serializers.ModelSerializer):
    content_detail_title = serializers.CharField(
        source="content_detail.title", read_only=True, default=""
    )
    assistant_name = serializers.CharField(
        source="assistant.name", read_only=True, default=""
    )
    front_matter = FrontMatterInlineSerializer(required=False)
    version_count = serializers.IntegerField(source="versions.count", read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "content_detail",
            "content_detail_title",
            "thread",
            "message",
            "assistant",
            "assistant_name",
            "post_content",
            "filename",
            "status",
            "front_matter",
            "version_count",
            "user",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def _save_front_matter(self, post: Post, data: dict | None) -> None:
        if not data:
            return
        try:
            front_matter = post.front_matter
        except PostFrontMatter.DoesNotExist:
            front_matter = PostFrontMatter(
                post=post, title="", description="", author=""
            )
        for key, value in data.items():
            setattr(front_matter, key, value)
        front_matter.save()

    def create(self, validated_data):
        front_matter = validated_data.pop("front_matter", None)
        request = self.context.get("request")
        if request is not None and request.user.is_authenticated:
            validated_data.setdefault("user", request.user)
        post = Post.objects.create(**validated_data)
        self._save_front_matter(post, front_matter)
        return post

    def update(self, instance, validated_data):
        front_matter = validated_data.pop("front_matter", None)
        post = super().update(instance, validated_data)
        self._save_front_matter(post, front_matter)
        return post


class PoweredBySerializer(serializers.ModelSerializer):
    class Meta:
        model = PoweredBy
        fields = ["id", "name", "icon", "url"]
