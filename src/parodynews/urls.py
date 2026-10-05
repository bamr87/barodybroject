"""
URL routes for the parodynews app.

The REST API lives under ``api/``; everything else that is not claimed by
Django (admin, accounts, setup, static/media, martor, i18n) is handed to the
React application, which does its own client-side routing.
"""

from django.urls import include, path, re_path

from .views import SPAView

# Paths Django itself owns. Requests starting with one of these never reach
# the SPA catch-all, so a typo there gives Django's 404 instead of a blank
# React page.
DJANGO_OWNED_PREFIXES = (
    "api/",
    "admin/",
    "accounts/",
    "setup/",
    "static/",
    "media/",
    "martor/",
    "i18n/",
)

urlpatterns = [
    path("api/", include("parodynews.api.urls")),
    # Named so ``Post.get_absolute_url()`` keeps resolving to the React route.
    path("posts/<int:post_id>/", SPAView.as_view(), name="post_detail"),
    re_path(
        r"^(?!(?:{})).*$".format("|".join(DJANGO_OWNED_PREFIXES)),
        SPAView.as_view(),
        name="spa",
    ),
]
