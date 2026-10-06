from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"providers", views.ProviderViewSet, basename="provider")
router.register(r"ai-models", views.AIModelViewSet)
router.register(r"assistants", views.AssistantViewSet)
router.register(r"assistant-groups", views.AssistantGroupViewSet)
router.register(r"json-schemas", views.JSONSchemaViewSet)
router.register(r"content-details", views.ContentDetailViewSet)
router.register(r"content-items", views.ContentItemViewSet)
router.register(r"threads", views.ThreadViewSet)
router.register(r"messages", views.MessageViewSet)
router.register(r"posts", views.PostViewSet)
router.register(r"post-front-matters", views.PostFrontMatterViewSet)
router.register(r"post-versions", views.PostVersionViewSet)
router.register(r"powered-by", views.PoweredByViewSet)

urlpatterns = [
    path("auth/me/", views.AuthMeView.as_view(), name="api-auth-me"),
    path("site/", views.SiteInfoView.as_view(), name="api-site"),
    *router.urls,
]
