"""
File: test_environment_theme.py
Description: Tests for the environment-derived colour treatment (prod/test/dev)
Author: Barodybroject Team
Created: 2026-09-05
Version: 1.0.0

Dependencies:
- django

Usage: python manage.py test parodynews.tests.test_environment_theme

These are SimpleTestCase / plain unittest cases on purpose: none of this
behaviour touches the ORM, so the suite stays runnable without a database.
"""

import importlib
import os
import unittest
from contextlib import contextmanager

from django.core.exceptions import ImproperlyConfigured
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, override_settings

from parodynews.context_processors import ENVIRONMENT_TREATMENTS, environment


@contextmanager
def environ(**overrides):
    """Temporarily patch os.environ, restoring exactly what was there before."""
    sentinel = object()
    previous = {k: os.environ.get(k, sentinel) for k in overrides}
    os.environ.update(overrides)
    try:
        yield
    finally:
        for key, old in previous.items():
            if old is sentinel:
                os.environ.pop(key, None)
            else:
                os.environ[key] = old


class EnvironmentSettingTests(SimpleTestCase):
    """The three-valued environment name each settings module resolves to."""

    def test_each_settings_module_declares_its_own_environment(self):
        """production/development/testing resolve to distinct, expected names."""
        expected = {
            "barodybroject.settings.production": "production",
            "barodybroject.settings.development": "development",
            "barodybroject.settings.testing": "test",
        }
        # production.py refuses to import without a SECRET_KEY; set one rather
        # than relying on the testing settings having already seeded it.
        with environ(SECRET_KEY=os.environ.get("SECRET_KEY", "test-only-key")):
            for module_path, name in expected.items():
                with self.subTest(module=module_path):
                    module = importlib.import_module(module_path)
                    self.assertEqual(module.ENVIRONMENT, name)

    def test_development_and_testing_are_distinguishable(self):
        """
        The defect this feature exposes: development.py and testing.py are
        byte-identical on IS_PRODUCTION and DEBUG, so before ENVIRONMENT existed
        nothing could tell them apart at runtime.
        """
        dev = importlib.import_module("barodybroject.settings.development")
        test = importlib.import_module("barodybroject.settings.testing")

        # The pre-existing flags genuinely cannot distinguish them...
        self.assertEqual(dev.IS_PRODUCTION, test.IS_PRODUCTION)
        self.assertEqual(dev.DEBUG, test.DEBUG)
        # ...and ENVIRONMENT is what finally does.
        self.assertNotEqual(dev.ENVIRONMENT, test.ENVIRONMENT)

    def test_invalid_environment_fails_loudly(self):
        """
        An unrecognised value must raise at startup, not fall through. A silent
        fallback would render as production — the one appearance that must never
        be wrong.
        """
        with environ(ENVIRONMENT="banana"):
            with self.assertRaises(ImproperlyConfigured) as ctx:
                importlib.reload(importlib.import_module("barodybroject.settings.base"))
            self.assertIn("banana", str(ctx.exception))

        # Restore the module to the real test configuration for later tests.
        with environ(ENVIRONMENT="test"):
            importlib.reload(importlib.import_module("barodybroject.settings.base"))


class EnvironmentContextProcessorTests(SimpleTestCase):
    """The processor that carries the treatment into every template."""

    def setUp(self):
        self.request = RequestFactory().get("/")

    @override_settings(ENVIRONMENT="production")
    def test_production_gets_no_badge(self):
        ctx = environment(self.request)
        self.assertEqual(ctx["environment"], "production")
        self.assertFalse(ctx["show_environment_badge"])
        self.assertEqual(ctx["environment_label"], "")
        self.assertEqual(ctx["environment_badge_class"], "")
        self.assertEqual(ctx["environment_border_class"], "")

    @override_settings(ENVIRONMENT="test")
    def test_test_environment_is_labelled(self):
        ctx = environment(self.request)
        self.assertTrue(ctx["show_environment_badge"])
        self.assertEqual(ctx["environment_label"], "TEST")
        self.assertEqual(ctx["environment_badge_class"], "text-bg-warning")

    @override_settings(ENVIRONMENT="development")
    def test_development_environment_is_labelled(self):
        ctx = environment(self.request)
        self.assertTrue(ctx["show_environment_badge"])
        self.assertEqual(ctx["environment_label"], "DEV")
        self.assertEqual(ctx["environment_badge_class"], "text-bg-info")

    @override_settings(ENVIRONMENT="staging")
    def test_unmapped_environment_degrades_to_no_badge(self):
        """
        A name that is valid but has no treatment yet must not crash the render
        — it simply gets no badge until someone adds a row to the map.
        """
        ctx = environment(self.request)
        self.assertEqual(ctx["environment"], "staging")
        self.assertFalse(ctx["show_environment_badge"])


class EnvironmentTreatmentContractTests(unittest.TestCase):
    """The colour map's own invariants."""

    def test_production_is_the_unstyled_baseline(self):
        self.assertNotIn("production", ENVIRONMENT_TREATMENTS)

    def test_every_treatment_uses_semantic_bootstrap_classes(self):
        """
        The treatment must ride Bootstrap's colour-mode-aware semantic classes,
        never literal colours — that is what makes it legible in both light and
        dark mode and keeps it from fighting `data-bs-theme`.
        """
        for name, treatment in ENVIRONMENT_TREATMENTS.items():
            with self.subTest(environment=name):
                self.assertTrue(treatment["badge_class"].startswith("text-bg-"))
                self.assertTrue(treatment["border_class"].startswith("border-"))
                # The label is text, so the signal is never colour alone.
                self.assertTrue(treatment["label"].strip())


class EnvironmentTemplateRenderTests(SimpleTestCase):
    """base.html actually shows (or hides) the treatment."""

    def _render(self, context):
        return render_to_string("base.html", context)

    def test_non_production_renders_the_label_as_text(self):
        for name, treatment in ENVIRONMENT_TREATMENTS.items():
            with self.subTest(environment=name):
                html = self._render(
                    {
                        "environment": name,
                        "show_environment_badge": True,
                        "environment_label": treatment["label"],
                        "environment_badge_class": treatment["badge_class"],
                        "environment_border_class": treatment["border_class"],
                    }
                )
                # The name is present as TEXT, not merely as a colour class.
                self.assertIn(treatment["label"], html)
                self.assertIn(treatment["badge_class"], html)
                self.assertIn(treatment["border_class"], html)
                self.assertIn(f'data-environment="{name}"', html)

    def test_production_renders_no_badge_markup(self):
        html = self._render(
            {
                "environment": "production",
                "show_environment_badge": False,
                "environment_label": "",
                "environment_badge_class": "",
                "environment_border_class": "",
            }
        )
        self.assertNotIn("data-environment=", html)
        self.assertNotIn("text-bg-warning", html)
        self.assertNotIn("text-bg-info", html)
        self.assertNotIn("border-top border-3", html)

    def test_production_render_is_unchanged_from_the_baseline_navbar(self):
        """Production keeps today's exact navbar classes."""
        html = self._render(
            {"environment": "production", "show_environment_badge": False}
        )
        self.assertIn('class="navbar navbar-expand-lg bg-body-tertiary"', html)

    def test_environment_treatment_does_not_touch_the_theme_switcher(self):
        """
        The environment signal and the user's light/dark/auto choice must
        compose. The treatment must never write `data-bs-theme` or the stored
        theme, so `<html>` keeps its `auto` default and the switcher still owns
        that attribute.
        """
        dev_html = self._render(
            {
                "environment": "development",
                "show_environment_badge": True,
                "environment_label": "DEV",
                "environment_badge_class": "text-bg-info",
                "environment_border_class": "border-info",
            }
        )
        prod_html = self._render(
            {"environment": "production", "show_environment_badge": False}
        )

        self.assertIn('data-bs-theme="auto"', dev_html)
        # The treatment adds no `data-bs-theme` of its own: whatever the page
        # says about the theme, it says identically with and without the badge.
        # (A bare count would also catch the `[data-bs-theme="dark"]` CSS
        # selector in the inline stylesheet, which is not an element attribute.)
        self.assertEqual(
            dev_html.count("data-bs-theme"), prod_html.count("data-bs-theme")
        )
        # ...and the switcher's own persistence code is untouched.
        self.assertIn("localStorage.getItem('theme')", dev_html)
        self.assertIn("localStorage.setItem('theme', theme)", dev_html)
