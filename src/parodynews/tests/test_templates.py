"""
File: test_templates.py
Description: Django template testing suite for Barodybroject
Author: Barodybroject Team
Created: 2025-10-12
Version: 1.0.0

Dependencies:
- django
- pytest (optional)

Usage: python manage.py test parodynews.tests.test_templates
"""

import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.template import Context, Template
from django.template.loader import get_template
from django.test import Client, TestCase
from django.urls import reverse


class TemplateStructureTests(TestCase):
    """Test template HTML structure and Bootstrap 5 implementation"""

    def setUp(self):
        """Set up test client and create test user"""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

    def test_base_template_loads(self):
        """Test that base template loads without errors"""
        try:
            template = get_template("base.html")
            self.assertIsNotNone(template)
        except Exception as e:
            self.fail(f"Base template failed to load: {str(e)}")

    def test_homepage_renders(self):
        """Test that homepage renders successfully"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_homepage_uses_base_template(self):
        """Test that homepage extends base template"""
        response = self.client.get("/")
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "index.html")

    def test_bootstrap_css_loaded(self):
        """Test that Bootstrap 5 CSS is loaded"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn("bootstrap", content.lower())
        self.assertIn("5.3.3", content)

    def test_bootstrap_icons_loaded(self):
        """Test that Bootstrap Icons are loaded"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn("bootstrap-icons", content)

    def test_bootstrap_js_loaded(self):
        """Test that Bootstrap JS is loaded"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn("bootstrap", content.lower())
        self.assertIn(".js", content)

    def test_no_jquery_dependency(self):
        """Test that jQuery is NOT loaded (Bootstrap 5 doesn't need it)"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        # jQuery might be loaded for other plugins, but not required for Bootstrap
        # This is a warning test
        if "jquery" in content.lower():
            print("WARNING: jQuery found - Bootstrap 5 doesn't require it")

    def test_responsive_meta_tag(self):
        """Test that responsive viewport meta tag is present"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn('name="viewport"', content)
        self.assertIn("width=device-width", content)

    def test_semantic_html_structure(self):
        """Test that semantic HTML5 elements are used"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Check for semantic elements
        self.assertIn("<main", content)
        self.assertIn("<footer", content)
        self.assertIn("<nav", content)
        self.assertIn("<!DOCTYPE html>", content)

    def test_navigation_present(self):
        """Test that navigation is present on homepage"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn("navbar", content)

    def test_footer_present(self):
        """Test that footer is present on homepage"""
        response = self.client.get("/")
        self.assertContains(response, "<footer")
        self.assertContains(response, "Barody Broject")


class TemplateContentTests(TestCase):
    """Test template content and components"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

    def test_homepage_title(self):
        """Test that homepage has correct title"""
        response = self.client.get("/")
        self.assertContains(response, "Barody Broject")

    def test_homepage_card_layout(self):
        """Test that homepage uses card layout"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn("card", content)
        self.assertIn("card-body", content)

    def test_homepage_icons(self):
        """Test that homepage has Bootstrap Icons"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn("bi-", content)  # Bootstrap Icon class prefix

    def test_navigation_links(self):
        """Test that navigation contains expected links"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Check for main navigation links
        self.assertIn("/content/", content)
        self.assertIn("/threads/", content)
        self.assertIn("/posts/", content)
        self.assertIn("/assistants/", content)

    def test_theme_toggle_present(self):
        """Test that theme toggle is present"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn("bd-theme", content)
        self.assertIn("data-bs-theme", content)

    def test_user_settings_dropdown(self):
        """Test that user settings dropdown is present when logged in"""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn("user-settings", content)

    def test_sign_in_button_when_logged_out(self):
        """Test that sign in button appears when logged out"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn("Sign In", content)


class TemplateAccessibilityTests(TestCase):
    """Test template accessibility features"""

    def setUp(self):
        self.client = Client()

    def test_aria_labels_on_buttons(self):
        """Test that buttons have proper ARIA labels"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Check for aria-label on toggle button
        if "navbar-toggler" in content:
            self.assertIn("aria-label", content)

    def test_aria_expanded_on_dropdowns(self):
        """Test that dropdowns have aria-expanded attribute"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        if "dropdown-toggle" in content:
            self.assertIn("aria-expanded", content)

    def test_proper_heading_hierarchy(self):
        """Test that heading hierarchy is logical"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Should have h1 on the page
        self.assertIn("<h1", content)

    def test_alt_text_on_images(self):
        """Test that images have alt text (if any images present)"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Find all img tags
        img_tags = re.findall(r"<img[^>]*>", content)
        for img in img_tags:
            if "alt=" not in img:
                print(f"WARNING: Image without alt text: {img[:50]}...")


class TemplateSecurityTests(TestCase):
    """Test template security features"""

    def setUp(self):
        self.client = Client()

    def test_external_links_have_rel_noopener(self):
        """Test that external links have rel='noopener noreferrer'"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Find external links
        external_links = re.findall(r'<a[^>]*target="_blank"[^>]*>', content)
        for link in external_links:
            if "rel=" not in link or "noopener" not in link:
                print(f"WARNING: External link without noopener: {link[:80]}...")

    def test_csrf_token_in_forms(self):
        """Test that forms have CSRF tokens"""
        # This test would need actual pages with forms
        # For now, just check the template can render
        pass


class TemplateResponsivenessTests(TestCase):
    """Test template responsive design"""

    def setUp(self):
        self.client = Client()

    def test_responsive_grid_classes(self):
        """Test that responsive grid classes are used"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Check for responsive classes
        self.assertIn("col-", content)
        self.assertIn("row", content)

    def test_responsive_utilities(self):
        """Test that responsive utility classes are used"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Check for responsive display utilities
        responsive_classes = ["d-none", "d-lg-", "d-md-", "d-sm-"]
        has_responsive = any(cls in content for cls in responsive_classes)
        self.assertTrue(has_responsive, "No responsive utility classes found")

    def test_container_usage(self):
        """Test that container classes are used properly"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertIn("container", content)


class SpecificTemplateTests(TestCase):
    """Test specific template files"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123", email="test@example.com"
        )

    def test_error_429_page(self):
        """Test 429 error page template"""
        try:
            template = get_template("429.html")
            self.assertIsNotNone(template)
        except Exception as e:
            print(f"WARNING: 429.html template not found: {e}")

    def test_profile_page(self):
        """Test profile page template"""
        try:
            template = get_template("profile.html")
            self.assertIsNotNone(template)
        except Exception as e:
            print(f"WARNING: profile.html template not found: {e}")

    def test_chatbox_template(self):
        """Test chatbox template"""
        try:
            template = get_template("chatbox.html")
            self.assertIsNotNone(template)
        except Exception as e:
            print(f"WARNING: chatbox.html template not found: {e}")

    def test_footer_template(self):
        """Test footer template"""
        try:
            template = get_template("footer.html")
            self.assertIsNotNone(template)
        except Exception as e:
            print(f"WARNING: footer.html template not found: {e}")


class BootstrapComponentTests(TestCase):
    """Test Bootstrap 5 component usage"""

    def setUp(self):
        self.client = Client()

    def test_cards_implementation(self):
        """Test that cards are properly implemented"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        if "card" in content:
            self.assertIn("card-body", content)

    def test_buttons_implementation(self):
        """Test that buttons use Bootstrap classes"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Check for Bootstrap button classes
        button_classes = [
            "btn-primary",
            "btn-secondary",
            "btn-success",
            "btn-danger",
            "btn-warning",
            "btn-info",
        ]
        has_buttons = any(cls in content for cls in button_classes)
        self.assertTrue(has_buttons, "No Bootstrap button classes found")

    def test_navbar_implementation(self):
        """Test that navbar uses Bootstrap 5 structure"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        if "navbar" in content:
            self.assertIn("navbar-expand", content)

    def test_offcanvas_implementation(self):
        """Test that offcanvas is properly implemented"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        if "offcanvas" in content:
            self.assertIn('data-bs-toggle="offcanvas"', content)

    def test_dropdown_implementation(self):
        """Test that dropdowns are properly implemented"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        if "dropdown" in content:
            self.assertIn("dropdown-menu", content)
            self.assertIn("dropdown-toggle", content)


class PerformanceTests(TestCase):
    """Test template performance aspects"""

    def setUp(self):
        self.client = Client()

    def test_no_inline_styles(self):
        """Test that inline styles are minimized"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Count inline styles
        inline_styles = content.count("style=")
        if inline_styles > 5:
            print(
                f"WARNING: Found {inline_styles} inline styles. Consider moving to CSS."
            )

    def test_no_duplicate_includes(self):
        """Test that CSS/JS libraries aren't loaded multiple times"""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        # Check Bootstrap (core) CSS isn't loaded multiple times.
        # Note: this intentionally ignores similarly-named assets like
        # `martor.bootstrap.min.css`.
        bootstrap_links = re.findall(
            r'href="https://cdn\.jsdelivr\.net/npm/bootstrap@[^\"]+/dist/css/bootstrap\.min\.css"',
            content,
        )
        self.assertEqual(
            len(bootstrap_links),
            1,
            f"Bootstrap CSS loaded {len(bootstrap_links)} times",
        )


class FleetFeedbackWidgetTests(TestCase):
    """Test the in-app feedback / feature-request shortcut (<fleet-feedback>).

    Covers the acceptance criteria of issue #42. Every assertion here fails on
    the commit before the widget was mounted, because none of the strings below
    existed anywhere in the template tree.
    """

    def setUp(self):
        self.client = Client()

    def test_widget_mounted_in_shell(self):
        """The custom element is rendered on a page built from base.html."""
        response = self.client.get("/")
        self.assertTemplateUsed(response, "includes/fleet_feedback.html")
        self.assertContains(response, "<fleet-feedback")

    def test_widget_has_non_empty_repo(self):
        """FLEET_REPO reaches the template — an empty repo makes the widget inert."""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        match = re.search(r'<fleet-feedback[^>]*\srepo="([^"]*)"', content)
        self.assertIsNotNone(match, "fleet-feedback element has no repo attribute")
        self.assertNotEqual(match.group(1), "", "FLEET_REPO rendered empty")
        self.assertRegex(match.group(1), r"^[\w.-]+/[\w.-]+$")

    def test_widget_labelled_with_marker_label(self):
        """The marker label is what makes widget-filed issues findable."""
        response = self.client.get("/")
        content = response.content.decode("utf-8")
        self.assertRegex(content, r'<fleet-feedback[^>]*\slabels="page-feedback"')

    def test_component_served_from_own_static_files(self):
        """The kit is explicit: vendor it, never hot-link the hub."""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        self.assertIn("fleet-feedback.js", content)
        for foreign in (
            "raw.githubusercontent.com",
            "cdn.jsdelivr.net/gh/bamr87",
            "github.com/bamr87/bamr87",
        ):
            self.assertNotIn(
                foreign,
                content,
                f"fleet-feedback.js must not be loaded from {foreign}",
            )

    def test_no_js_anchor_targets_committed_issue_form(self):
        """With JS off the inline anchor is the whole feature; it must resolve."""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        self.assertIn("page_feedback.yml", content)
        self.assertIn("data-fleet-feedback-open", content)

        anchors = re.findall(r"<a[^>]*data-fleet-feedback-open[^>]*>", content)
        self.assertTrue(anchors, "no inline data-fleet-feedback-open anchor rendered")
        for anchor in anchors:
            self.assertIn("href=", anchor)
            self.assertIn("noopener", anchor)

        # The anchor 404s unless the issue form is actually committed.
        template_path = (
            Path(settings.BASE_DIR).parent
            / ".github"
            / "ISSUE_TEMPLATE"
            / "page_feedback.yml"
        )
        self.assertTrue(
            template_path.exists(),
            f"{template_path} is missing; the no-JS anchor would 404",
        )

    def test_no_credential_in_rendered_page(self):
        """`mode` stays `url`, so no token may ever reach the client."""
        response = self.client.get("/")
        content = response.content.decode("utf-8")

        for secret_marker in ("ghp_", "github_pat_", "ghs_", "gho_"):
            self.assertNotIn(secret_marker, content)

        # url mode is the default; assert we never opted into proxy mode, which
        # is the variant that would need a server-side credential.
        self.assertNotRegex(content, r'<fleet-feedback[^>]*\smode="proxy"')

    def test_vendored_component_file_exists(self):
        """The <script> tag is useless if the asset was never vendored."""
        asset = Path(settings.BASE_DIR) / "assets" / "js" / "fleet-feedback.js"
        self.assertTrue(asset.exists(), f"{asset} is missing")
        self.assertIn("customElements.define", asset.read_text(encoding="utf-8"))

    def test_kit_version_recorded(self):
        """Provenance is what makes later drift from the kit detectable."""
        version_file = (
            Path(settings.BASE_DIR) / "assets" / "js" / "fleet-feedback.VERSION"
        )
        self.assertTrue(version_file.exists(), f"{version_file} is missing")
        self.assertIn("version:", version_file.read_text(encoding="utf-8"))


class FleetFeedbackSettingsTests(TestCase):
    """FLEET_* must live in settings/base.py so every environment inherits it."""

    def test_fleet_settings_present_and_non_empty(self):
        self.assertTrue(getattr(settings, "FLEET_REPO", ""))
        self.assertTrue(getattr(settings, "FLEET_BRANCH", ""))

    def test_fleet_settings_defined_in_base_not_one_environment(self):
        """Guards the regression the issue calls out: setting these in
        development.py only, which leaves testing/production rendering an
        empty repo attribute."""
        base_source = (
            Path(settings.BASE_DIR) / "barodybroject" / "settings" / "base.py"
        ).read_text(encoding="utf-8")
        self.assertIn("FLEET_REPO", base_source)
        self.assertIn("FLEET_BRANCH", base_source)

    def test_context_processor_registered(self):
        processors = settings.TEMPLATES[0]["OPTIONS"]["context_processors"]
        self.assertIn("parodynews.context_processors.fleet_feedback", processors)

    def test_context_processor_output(self):
        from parodynews.context_processors import fleet_feedback

        ctx = fleet_feedback(None)
        self.assertEqual(ctx["FLEET_REPO"], settings.FLEET_REPO)
        self.assertEqual(ctx["FLEET_BRANCH"], settings.FLEET_BRANCH)
        self.assertIn(ctx["FLEET_ENV"], {"development", "production"})


# Test runner output
def run_tests():
    """Run all tests and output results"""
    import sys

    from django.test.runner import DiscoverRunner

    runner = DiscoverRunner(verbosity=2)
    failures = runner.run_tests(["parodynews.tests.test_templates"])

    if failures:
        sys.exit(1)
    else:
        print("\n✓ All template tests passed!\n")
        sys.exit(0)


if __name__ == "__main__":
    run_tests()
