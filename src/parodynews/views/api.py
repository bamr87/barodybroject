"""
File: api.py
Description: Django REST Framework viewsets for parodynews API endpoints
Author: Barodybroject Team <team@example.com>
Created: 2025-12-19
Last Modified: 2025-12-20
Version: 0.4.0

Dependencies:
- django: >=5.1
- djangorestframework: >=3.15.0

Usage: Included via parodynews URL routing.
"""

from rest_framework import status, viewsets
from rest_framework.response import Response

from ..models import (
    Assistant,
    AssistantGroup,
    ContentDetail,
    ContentItem,
    JSONSchema,
    Message,
    Post,
    PostFrontMatter,
    PoweredBy,
    Thread,
)
from ..serializers import (
    AssistantGroupSerializer,
    AssistantSerializer,
    ContentDetailSerializer,
    ContentItemSerializer,
    JSONSchemaSerializer,
    MessageSerializer,
    PostFrontMatterSerializer,
    PostSerializer,
    PoweredBySerializer,
    ThreadSerializer,
)
from ..utils import create_or_update_assistant


class AssistantViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing AI Assistant configurations."""

    queryset = Assistant.objects.all()
    serializer_class = AssistantSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            assistant = create_or_update_assistant(serializer.validated_data)
            output_serializer = self.get_serializer(assistant)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssistantGroupViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing Assistant Groups."""

    queryset = AssistantGroup.objects.all()
    serializer_class = AssistantGroupSerializer


class ContentItemViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing Content Items."""

    queryset = ContentItem.objects.all()
    serializer_class = ContentItemSerializer


class ContentDetailViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing Content Details."""

    queryset = ContentDetail.objects.all()
    serializer_class = ContentDetailSerializer


class ThreadViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing Conversation Threads."""

    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing Messages within Threads."""

    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class PostViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing Blog Posts."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer


class PostFrontMatterViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing Post FrontMatter metadata."""

    queryset = PostFrontMatter.objects.all()
    serializer_class = PostFrontMatterSerializer


class JSONSchemaViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing JSON Schema definitions."""

    queryset = JSONSchema.objects.all()
    serializer_class = JSONSchemaSerializer


class PoweredByViewSet(viewsets.ModelViewSet):
    """API ViewSet for managing PoweredBy attribution records."""

    queryset = PoweredBy.objects.all()
    serializer_class = PoweredBySerializer
