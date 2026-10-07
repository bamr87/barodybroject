"""
File: views.py
Description: REST endpoints behind the React frontend
Author: Barodybroject Team <team@example.com>
Created: 2026-09-14
Version: 0.6.0

Dependencies:
- djangorestframework: >=3.15

Every AI-backed action funnels through ``parodynews.services`` and reports
``AIError`` subclasses as JSON: configuration problems are 400s (the operator
must act), provider failures are 502s (retry later).
"""

from __future__ import annotations

import json
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse
from django.middleware.csrf import get_token
from django.urls import reverse
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from parodynews.ai import (
    AIConfigurationError,
    AIError,
    available_providers,
    describe_providers,
    get_default_provider_slug,
    get_provider,
)
from parodynews.context_processors import list_issue_templates
from parodynews.models import (
    AIModel,
    AIProviderConfig,
    Assistant,
    AssistantGroup,
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
from parodynews.services import assistants as assistant_services
from parodynews.services import content as content_services
from parodynews.services import publishing as publishing_services
from parodynews.services import threads as thread_services
from parodynews.utils.schemas import load_schemas

from .serializers import (
    AIModelSerializer,
    AIProviderConfigSerializer,
    AssistantGroupSerializer,
    AssistantSerializer,
    ContentDetailSerializer,
    ContentItemSerializer,
    JSONSchemaSerializer,
    MessageSerializer,
    PostFrontMatterSerializer,
    PostSerializer,
    PostVersionSerializer,
    PoweredBySerializer,
    ThreadDetailSerializer,
    ThreadSerializer,
    UserSerializer,
)


def ai_error_response(exc: AIError) -> Response:
    code = (
        status.HTTP_400_BAD_REQUEST
        if isinstance(exc, AIConfigurationError)
        else (status.HTTP_502_BAD_GATEWAY)
    )
    return Response(
        {
            "detail": str(exc),
            "provider": exc.provider,
            "error_type": type(exc).__name__,
        },
        status=code,
    )


def _own_or_shared(queryset, request):
    """Rows owned by the user or by nobody; staff see everything."""
    if request.user.is_staff:
        return queryset
    return queryset.filter(Q(user=request.user) | Q(user__isnull=True))


def _read_version() -> str:
    version_file = Path(settings.BASE_DIR).parent / "VERSION"
    try:
        return version_file.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


# ------------------------------------------------------------------- session
class AuthMeView(APIView):
    """Who am I, plus the CSRF token the SPA must send on unsafe requests."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.user
        payload = {
            "authenticated": user.is_authenticated,
            "user": UserSerializer(user).data if user.is_authenticated else None,
            "csrf_token": get_token(request),
            "login_url": reverse("account_login"),
            "logout_url": reverse("account_logout"),
            "signup_url": reverse("account_signup"),
            "profile_url": reverse("account_email") if user.is_authenticated else None,
        }
        return Response(payload)


class SiteInfoView(APIView):
    """Static-ish data for the navbar and footer."""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response(
            {
                "name": "Barody Broject",
                "version": _read_version(),
                "default_provider": get_default_provider_slug(),
                "providers": available_providers(),
                "publications_url": getattr(
                    settings,
                    "PUBLICATIONS_URL",
                    "https://bamr87.github.io/barodybroject/posts/",
                ),
                "github_issue_repo": getattr(settings, "GITHUB_ISSUE_REPO", ""),
                "issue_templates": list_issue_templates(),
                "powered_by": PoweredBySerializer(
                    PoweredBy.objects.all(), many=True
                ).data,
                "admin_url": reverse("admin:index"),
            }
        )


# ----------------------------------------------------------------- providers
class ProviderViewSet(viewsets.ViewSet):
    """Registered AI providers, their configuration, and their models.

    ``pk`` is the provider slug. Reading is open to every signed-in user;
    changing configuration or the default requires staff.
    """

    permission_classes = [permissions.IsAuthenticated]

    def _staff_only(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only staff can change provider configuration."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    def _get_provider(self, slug):
        try:
            return get_provider(slug, require_enabled=False)
        except AIConfigurationError as exc:
            return ai_error_response(exc)

    def _serialize(self, slug):
        provider = get_provider(slug, require_enabled=False)
        info = provider.describe()
        info["is_default"] = slug == get_default_provider_slug()
        row = AIProviderConfig.objects.filter(provider=slug).first()
        info["config"] = AIProviderConfigSerializer(row).data if row else None
        info["catalogue_count"] = AIModel.objects.filter(provider=slug).count()
        return info

    def list(self, request):
        summaries = describe_providers()
        rows = {row.provider: row for row in AIProviderConfig.objects.all()}
        counts = {
            slug: AIModel.objects.filter(provider=slug).count()
            for slug in available_providers()
        }
        for info in summaries:
            row = rows.get(info["slug"])
            info["config"] = AIProviderConfigSerializer(row).data if row else None
            info["catalogue_count"] = counts.get(info["slug"], 0)
        return Response(summaries)

    def retrieve(self, request, pk=None):
        if pk not in available_providers():
            return Response({"detail": f"Unknown provider {pk!r}."}, status=404)
        return Response(self._serialize(pk))

    @action(detail=True, methods=["get"])
    def models(self, request, pk=None):
        provider = self._get_provider(pk)
        if isinstance(provider, Response):
            return provider
        try:
            models = provider.list_models()
        except AIError as exc:
            return ai_error_response(exc)
        return Response([model.as_dict() for model in models])

    @action(detail=True, methods=["post"])
    def sync(self, request, pk=None):
        try:
            report = assistant_services.sync_models(pk)
        except AIError as exc:
            return ai_error_response(exc)
        return Response(report.as_dict())

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        provider = self._get_provider(pk)
        if isinstance(provider, Response):
            return provider
        try:
            return Response(provider.health_check())
        except AIError as exc:
            return ai_error_response(exc)

    @action(detail=True, methods=["put", "patch"])
    def config(self, request, pk=None):
        denied = self._staff_only(request)
        if denied:
            return denied
        if pk not in available_providers():
            return Response({"detail": f"Unknown provider {pk!r}."}, status=404)
        row = AIProviderConfig.objects.filter(provider=pk).first()
        data = dict(request.data.items())
        data["provider"] = pk
        clear_api_key = bool(data.pop("clear_api_key", False))
        if not data.get("api_key") and not clear_api_key:
            data.pop("api_key", None)  # blank means "leave the stored credential alone"
        serializer = AIProviderConfigSerializer(row, data=data, partial=row is not None)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            row = serializer.save()
            if clear_api_key:
                row.api_key = ""
                row.save(update_fields=["api_key"])
        return Response(self._serialize(pk))

    @action(detail=True, methods=["post"], url_path="set-default")
    def set_default(self, request, pk=None):
        denied = self._staff_only(request)
        if denied:
            return denied
        if pk not in available_providers():
            return Response({"detail": f"Unknown provider {pk!r}."}, status=404)
        row, _ = AIProviderConfig.objects.get_or_create(provider=pk)
        row.is_default = True
        row.is_enabled = True
        row.save()
        return Response(self._serialize(pk))


class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["model_id", "display_name", "provider"]
    ordering_fields = ["provider", "model_id", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        provider = self.request.query_params.get("provider")
        if provider:
            queryset = queryset.filter(provider=provider)
        if self.request.query_params.get("active") in ("1", "true"):
            queryset = queryset.filter(is_active=True)
        return queryset


class JSONSchemaViewSet(viewsets.ModelViewSet):
    queryset = JSONSchema.objects.all().order_by("name")
    serializer_class = JSONSchemaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "id"]

    @action(detail=True, methods=["get"])
    def export(self, request, pk=None):
        schema = self.get_object()
        response = HttpResponse(
            json.dumps(schema.schema, indent=2), content_type="application/json"
        )
        response["Content-Disposition"] = f'attachment; filename="{schema.name}.json"'
        return response

    @action(detail=False, methods=["get"])
    def bundled(self, request):
        """The schemas shipped with the app, for one-click import."""
        return Response(
            [
                {"name": name, "schema": schema}
                for name, schema in load_schemas().items()
            ]
        )


# ---------------------------------------------------------------- assistants
class AssistantViewSet(viewsets.ModelViewSet):
    queryset = Assistant.objects.select_related(
        "model", "json_schema"
    ).prefetch_related("assistant_groups")
    serializer_class = AssistantSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description", "instructions"]
    ordering_fields = ["name", "created_at"]

    def perform_destroy(self, instance):
        assistant_services.delete_assistant(instance)


class AssistantGroupViewSet(viewsets.ModelViewSet):
    queryset = AssistantGroup.objects.prefetch_related(
        "assistantgroupmembership_set__assistant"
    )
    serializer_class = AssistantGroupSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "group_type"]
    ordering_fields = ["sequence", "name", "priority", "created_at"]


# ------------------------------------------------------------------- content
class ContentDetailViewSet(viewsets.ModelViewSet):
    queryset = ContentDetail.objects.select_related("user").prefetch_related(
        "contentitem__assistant"
    )
    serializer_class = ContentDetailSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description", "author", "slug"]
    ordering_fields = ["published_at", "title", "id"]

    def get_queryset(self):
        return _own_or_shared(super().get_queryset(), self.request)

    def _first_item(self, detail) -> ContentItem | None:
        return detail.contentitem.order_by("line_number", "id").first()

    @action(detail=True, methods=["post"])
    def generate(self, request, pk=None):
        detail = self.get_object()
        item = self._first_item(detail)
        if item is None:
            return Response({"detail": "Add a prompt before generating."}, status=400)
        try:
            outcome = content_services.generate_content(
                item, provider_slug=request.data.get("provider") or None
            )
        except AIError as exc:
            return ai_error_response(exc)
        detail.refresh_from_db()
        return Response(
            {
                "content_detail": ContentDetailSerializer(detail).data,
                **outcome.as_dict(),
            }
        )

    @action(detail=True, methods=["post"], url_path="create-thread")
    def create_thread(self, request, pk=None):
        detail = self.get_object()
        group = None
        group_id = request.data.get("assistant_group")
        if group_id:
            group = AssistantGroup.objects.filter(pk=group_id).first()
        try:
            thread, _message = thread_services.create_thread_from_content(
                detail,
                request.user,
                assistant_group=group,
                name=request.data.get("name", ""),
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(
            ThreadDetailSerializer(thread).data, status=status.HTTP_201_CREATED
        )


class ContentItemViewSet(viewsets.ModelViewSet):
    queryset = ContentItem.objects.select_related("assistant", "detail")
    serializer_class = ContentItemSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        detail = self.request.query_params.get("detail")
        if detail:
            queryset = queryset.filter(detail_id=detail)
        return queryset


# -------------------------------------------------------------- conversation
class ThreadViewSet(viewsets.ModelViewSet):
    queryset = Thread.objects.select_related("assistant_group", "user")
    serializer_class = ThreadSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "name"]

    def get_queryset(self):
        return _own_or_shared(super().get_queryset(), self.request)

    def get_serializer_class(self):
        if self.action in ("retrieve", "run", "run_group", "add_message"):
            return ThreadDetailSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        thread = self.get_object()
        return Response(MessageSerializer(thread.ordered_messages(), many=True).data)

    @action(detail=True, methods=["post"], url_path="add-message")
    def add_message(self, request, pk=None):
        thread = self.get_object()
        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"detail": "text is required."}, status=400)
        assistant = None
        if request.data.get("assistant"):
            assistant = Assistant.objects.filter(pk=request.data["assistant"]).first()
        thread_services.add_user_message(thread, text, assistant=assistant)
        return Response(
            ThreadDetailSerializer(thread).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        thread = self.get_object()
        assistant = Assistant.objects.filter(pk=request.data.get("assistant")).first()
        if assistant is None:
            return Response({"detail": "assistant is required."}, status=400)
        try:
            reply = thread_services.run_assistant(
                thread, assistant, provider_slug=request.data.get("provider") or None
            )
        except AIError as exc:
            return ai_error_response(exc)
        return Response(
            {
                "message": MessageSerializer(reply).data,
                "thread": ThreadDetailSerializer(thread).data,
            }
        )

    @action(detail=True, methods=["post"], url_path="run-group")
    def run_group(self, request, pk=None):
        thread = self.get_object()
        group = None
        if request.data.get("assistant_group"):
            group = AssistantGroup.objects.filter(
                pk=request.data["assistant_group"]
            ).first()
        try:
            replies = thread_services.run_assistant_group(
                thread, group=group, provider_slug=request.data.get("provider") or None
            )
        except AIError as exc:
            return ai_error_response(exc)
        return Response(
            {
                "messages": MessageSerializer(replies, many=True).data,
                "thread": ThreadDetailSerializer(thread).data,
            }
        )


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related("thread", "assistant", "contentitem")
    serializer_class = MessageSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["created_at", "status"]

    def get_queryset(self):
        queryset = super().get_queryset()
        thread = self.request.query_params.get("thread")
        if thread:
            queryset = queryset.filter(thread_id=thread)
        return queryset

    @action(detail=True, methods=["post"])
    def assign(self, request, pk=None):
        message = self.get_object()
        assistant = None
        if request.data.get("assistant"):
            assistant = Assistant.objects.filter(pk=request.data["assistant"]).first()
            if assistant is None:
                return Response({"detail": "Unknown assistant."}, status=400)
        thread_services.assign_assistant(message, assistant)
        return Response(MessageSerializer(message).data)

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        message = self.get_object()
        if message.thread is None:
            return Response(
                {"detail": "This message is not part of a thread."}, status=400
            )
        assistant = message.assistant
        if request.data.get("assistant"):
            assistant = Assistant.objects.filter(pk=request.data["assistant"]).first()
        if assistant is None:
            return Response({"detail": "Assign an assistant first."}, status=400)
        try:
            reply = thread_services.run_assistant(
                message.thread,
                assistant,
                provider_slug=request.data.get("provider") or None,
            )
        except AIError as exc:
            return ai_error_response(exc)
        return Response(MessageSerializer(reply).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="create-content")
    def create_content(self, request, pk=None):
        message = self.get_object()
        if not message.text.strip():
            return Response({"detail": "The message has no content."}, status=400)
        try:
            detail = content_services.create_content_from_text(
                message.text,
                user=request.user,
                assistant=message.assistant,
                prompt=message.text,
            )
        except AIError as exc:
            return ai_error_response(exc)
        return Response(
            ContentDetailSerializer(detail).data, status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=["post"], url_path="create-post")
    def create_post(self, request, pk=None):
        message = self.get_object()
        try:
            post = publishing_services.create_post_from_message(message, request.user)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        except AIError as exc:
            return ai_error_response(exc)
        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------- publishing
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("content_detail", "assistant", "user")
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["content_detail__title", "post_content", "status"]
    ordering_fields = ["created_at", "updated_at", "status"]

    def get_queryset(self):
        return _own_or_shared(super().get_queryset(), self.request)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        post = self.get_object()
        try:
            version, url = publishing_services.publish_post(post)
        except publishing_services.PublishingNotConfigured as exc:
            return Response({"detail": str(exc)}, status=400)
        except publishing_services.PublicationError as exc:
            # Already phrased for a reader: pass it through verbatim rather
            # than burying it under a generic "Publishing failed" prefix.
            body = {"detail": exc.message}
            if exc.url:
                body["url"] = exc.url
            return Response(body, status=502)
        except Exception as exc:  # noqa: BLE001 - GitHub client raises many types
            return Response({"detail": f"Publishing failed: {exc}"}, status=502)
        return Response(
            {
                "url": url,
                "version": PostVersionSerializer(version).data,
                "post": PostSerializer(post).data,
            }
        )

    @action(detail=True, methods=["get"])
    def versions(self, request, pk=None):
        post = self.get_object()
        return Response(PostVersionSerializer(post.versions.all(), many=True).data)

    @action(detail=True, methods=["get"])
    def render(self, request, pk=None):
        post = self.get_object()
        rendered = publishing_services.render_post(post)
        return Response(
            {
                "filename": rendered.filename,
                "frontmatter": rendered.frontmatter_yaml,
                "document": rendered.document,
            }
        )


class PostFrontMatterViewSet(viewsets.ModelViewSet):
    queryset = PostFrontMatter.objects.all()
    serializer_class = PostFrontMatterSerializer


class PostVersionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PostVersion.objects.all()
    serializer_class = PostVersionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        post = self.request.query_params.get("post")
        if post:
            queryset = queryset.filter(post_id=post)
        return queryset


class PoweredByViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PoweredBy.objects.all()
    serializer_class = PoweredBySerializer
    permission_classes = [permissions.AllowAny]
