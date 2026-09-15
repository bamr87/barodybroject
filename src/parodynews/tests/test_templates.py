"""
File: test_templates.py
Description: Tests for the templates Django still renders after the React migration
Author: Barodybroject Team
Created: 2025-10-12
Last Modified: 2026-09-14
Version: 2.0.0

Dependencies:
- django
- pytest-django

Usage: python -m pytest parodynews/tests/test_templates.py (run from src/)

Django renders two things now: the SPA shell (`spa/index.html`, which boots
the React app) and the allauth account pages (`base.html`). The application UI
itself is tested by the frontend suite (`src/frontend`, Vitest) and by the
Playwright specs under `tests/e2e/`.
"""

import json
from pathlib import Path

import pytest
from django.contrib.auth.models import User
from django.template.loader import get_template
from django.test import Client, TestCase, override_settings

from parodynews.views.spa import manifest_assets


class SPAShellTests(TestCase):
    """`spa/index.html` — the only page the React app needs from Django."""

    def setUp(self):
        self.client = Client()

    def test_the_root_url_serves_the_shell(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "spa/index.html")

    def test_the_shell_provides_the_mount_point(self):
        """React renders into #root; without it the app never starts."""
        self.assertContains(self.client.get("/"), '<div id="root">')

    def test_the_shell_publishes_a_csrf_token(self):
        """The SPA reads this meta tag to make its first unsafe request."""
        self.assertContains(self.client.get("/"), 'name="csrf-token"')

    def test_the_shell_sets_the_theme_before_paint(self):
        """Applying the stored theme in <head> avoids a flash of the wrong one."""
        self.assertContains(self.client.get("/"), "data-bs-theme")

    def test_unknown_paths_fall_through_to_the_app(self):
        """Routing is client-side, so a deep link must reach React rather than
        Django's 404 page."""
        response = self.client.get("/threads/thread_whatever/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "spa/index.html")

    def test_django_owned_prefixes_are_not_swallowed(self):
        """The catch-all must not shadow the admin, the API or the auth pages.

        An unknown path under one of them is Django's to answer — admin sends
        an anonymous visitor to its login page, the API 404s — and in neither
        case should the SPA shell be rendered instead.
        """
        for path in ("/admin/does-not-exist/", "/api/does-not-exist/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertNotIn(
                    "spa/index.html", [template.name for template in response.templates]
                )

    def test_the_api_is_not_swallowed(self):
        response = self.client.get("/api/site/")
        self.assertEqual(response["Content-Type"], "application/json")

    def test_the_post_route_still_reverses(self):
        """`Post.get_absolute_url()` points at a React route; the name has to
        keep resolving so model code does not raise NoReverseMatch."""
        from django.urls import reverse

        self.assertEqual(reverse("post_detail", kwargs={"post_id": 7}), "/posts/7/")

    @override_settings(FRONTEND_DEV_SERVER_URL="http://localhost:5173")
    def test_the_dev_server_is_used_when_configured(self):
        """With Vite running, the shell loads the app from the dev server so
        edits hot-reload while Django keeps serving auth and the API."""
        content = self.client.get("/").content.decode()
        self.assertIn("http://localhost:5173/@vite/client", content)
        self.assertIn("http://localhost:5173/src/main.tsx", content)

    @override_settings(FRONTEND_DIST_DIR="/nonexistent", FRONTEND_DEV_SERVER_URL="")
    def test_an_unbuilt_frontend_explains_itself(self):
        """A blank page would look like a crash; say what to run instead."""
        self.assertContains(self.client.get("/"), "npm run build")


class ManifestTests(TestCase):
    """The Vite manifest is what maps the entry point to hashed filenames."""

    def test_no_manifest_means_no_assets(self):
        self.assertIsNone(manifest_assets("/nonexistent"))

    def test_assets_are_read_from_the_manifest(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            (dist / ".vite").mkdir()
            (dist / ".vite" / "manifest.json").write_text(
                json.dumps(
                    {
                        "src/main.tsx": {
                            "file": "assets/main-abc123.js",
                            "isEntry": True,
                            "css": ["assets/main-def456.css"],
                        }
                    }
                )
            )
            assets = manifest_assets(dist)

        self.assertEqual(assets["scripts"], ["/static/frontend/assets/main-abc123.js"])
        self.assertEqual(assets["styles"], ["/static/frontend/assets/main-def456.css"])

    def test_a_manifest_without_the_entry_is_ignored(self):
        """A partial build must fall back to the "not built" message rather
        than emit a <script> tag pointing at nothing."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            (dist / ".vite").mkdir()
            (dist / ".vite" / "manifest.json").write_text(json.dumps({"other.ts": {}}))
            self.assertIsNone(manifest_assets(dist))


class AuthTemplateTests(TestCase):
    """`base.html` wraps the allauth pages, which stayed server-rendered."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

    def test_base_template_loads(self):
        self.assertIsNotNone(get_template("base.html"))

    def test_the_login_page_renders(self):
        response = self.client.get("/accounts/login/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")

    def test_the_login_page_has_a_form(self):
        self.assertContains(self.client.get("/accounts/login/"), "<form")

    def test_the_login_page_carries_a_csrf_token(self):
        self.assertContains(self.client.get("/accounts/login/"), "csrfmiddlewaretoken")

    def test_semantic_landmarks_are_present(self):
        content = self.client.get("/accounts/login/").content.decode()
        for element in ("<main", "<footer", "<nav", "<!DOCTYPE html>"):
            self.assertIn(element, content)

    def test_the_footer_is_rendered(self):
        self.assertContains(self.client.get("/accounts/login/"), "Barody Broject")

    def test_a_signed_out_visitor_is_offered_a_way_in(self):
        self.assertContains(self.client.get("/accounts/login/"), "Sign In")

    def test_a_signed_in_visitor_is_offered_the_app_and_a_way_out(self):
        self.client.login(username="testuser", password="testpass123")
        content = self.client.get("/accounts/email/").content.decode()
        self.assertIn("Sign Out", content)

    def test_the_auth_pages_load_no_third_party_resources(self):
        """They run inside the same deployment as the API; a CDN dependency
        breaks them on an air-gapped or offline install. The React bundle
        already carries Bootstrap, so there is nothing to fetch."""
        content = self.client.get("/accounts/login/").content.decode()
        self.assertNotIn("https://cdn.jsdelivr.net", content)

    def test_the_auth_pages_run_no_javascript_of_their_own(self):
        """Nothing on them needs it, and not loading Bootstrap's bundle is what
        lets the previous assertion hold."""
        content = self.client.get("/accounts/login/").content.decode()
        self.assertNotIn("bootstrap.bundle", content)

    def test_the_error_page_template_still_extends_a_layout_that_exists(self):
        """It used to extend `auth/layouts/entrance.html`, which is not a
        template this project has — rendering it raised instead of showing
        the error."""
        self.assertIsNotNone(get_template("429.html"))

    def test_the_profile_template_still_extends_a_layout_that_exists(self):
        self.assertIsNotNone(get_template("profile.html"))


@pytest.mark.django_db
def test_the_profile_page_renders(client):
    User.objects.create_user(
        username="profileuser", password="pw", email="p@example.com"
    )
    client.login(username="profileuser", password="pw")
    response = client.get("/accounts/profile/")
    assert response.status_code == 200
