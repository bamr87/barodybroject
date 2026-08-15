"""
File: test_model_table.py
Description: Regression tests for the model_table.html / table_utils.js contract
Author: Barodybroject Team
Created: 2026-08-15
Version: 1.0.0

Dependencies:
- django

Usage: python -m pytest parodynews/tests/test_model_table.py

Background: table_utils.js binds its sort handler to `th.sortable`, but
model_table.html rendered `<th scope="col">` with no such class. The selector
matched zero elements, no listener was ever attached, and clicking a column
header did nothing on every list page in the app. These tests pin both halves
of that contract — the class that makes the binding possible, and the
`data-type` that makes the ordering correct.
"""

import re

from django.contrib.auth.models import User
from django.template import Context, Template
from django.test import SimpleTestCase, TestCase

from parodynews.templatetags.custom_filters import sort_data_type

# Rendered by the {% render_model_table %} inclusion tag. `edit_content` takes a
# single int pk, which is all the template's {% url %} call needs.
TABLE_SOURCE = (
    "{% load custom_filters %}"
    "{% render_model_table objects fields display_fields 'edit_content' 'Test Table' %}"
)

DISPLAY_FIELDS = ["id", "username", "date_joined"]


def render_table(objects):
    """Render the shared table partial with real model fields, no DB access."""
    return Template(TABLE_SOURCE).render(
        Context(
            {
                "objects": objects,
                "fields": User._meta.get_fields(),
                "display_fields": DISPLAY_FIELDS,
            }
        )
    )


# `\b` keeps this from matching <thead>, and the opening tag spans several lines.
HEADER_CELL_RE = re.compile(r"(<th\b[^>]*>)(.*?)</th>", flags=re.DOTALL)


def header_cells(html):
    """Return the opening <th ...> tag of every rendered header cell."""
    return [match.group(1) for match in HEADER_CELL_RE.finditer(html)]


def header_for(html, verbose_name):
    """Return the opening <th> tag whose filter input targets `verbose_name`."""
    # Each header carries `aria-label="Filter <verbose name>"` on its input, so
    # the column can be identified without depending on _meta field ordering.
    for match in HEADER_CELL_RE.finditer(html):
        if f'aria-label="Filter {verbose_name}"' in match.group(2):
            return match.group(1)
    raise AssertionError(f"no header cell found for {verbose_name!r}")


class SortDataTypeFilterTests(SimpleTestCase):
    """The filter that tells table_utils.js how to order each column."""

    def test_integer_fields_sort_as_numbers(self):
        self.assertEqual(sort_data_type(User._meta.get_field("id")), "number")

    def test_datetime_fields_sort_as_dates(self):
        self.assertEqual(sort_data_type(User._meta.get_field("date_joined")), "date")

    def test_text_fields_get_no_type_and_sort_lexicographically(self):
        self.assertEqual(sort_data_type(User._meta.get_field("username")), "")

    def test_boolean_fields_get_no_type(self):
        self.assertEqual(sort_data_type(User._meta.get_field("is_staff")), "")

    def test_pseudo_fields_without_get_internal_type_are_tolerated(self):
        # Model._meta.get_fields() also yields reverse relations, which have no
        # get_internal_type(). They must degrade to text, not raise.
        reverse_rels = [
            f for f in User._meta.get_fields() if not hasattr(f, "get_internal_type")
        ]
        self.assertTrue(reverse_rels, "expected at least one reverse relation on User")
        for rel in reverse_rels:
            self.assertEqual(sort_data_type(rel), "")


class ModelTableMarkupTests(SimpleTestCase):
    """The rendered markup must satisfy table_utils.js's selectors."""

    def setUp(self):
        self.html = render_table(
            [User(id=2, username="bravo"), User(id=10, username="alpha")]
        )

    def test_every_header_carries_the_sortable_class(self):
        # The defect: `th.sortable` matched nothing, so no click handler was
        # ever bound and clicking a column header did nothing at all.
        headers = header_cells(self.html)
        self.assertEqual(len(headers), len(DISPLAY_FIELDS))
        for header in headers:
            self.assertIn('class="sortable"', header)

    def test_numeric_columns_are_typed_for_numeric_ordering(self):
        self.assertIn('data-type="number"', header_for(self.html, "ID"))

    def test_date_columns_are_typed_for_chronological_ordering(self):
        self.assertIn('data-type="date"', header_for(self.html, "date joined"))

    def test_text_columns_carry_no_type_and_fall_back_to_string_ordering(self):
        self.assertNotIn("data-type", header_for(self.html, "username"))

    def test_headers_start_unsorted(self):
        for header in header_cells(self.html):
            self.assertIn('aria-sort="none"', header)

    def test_filter_inputs_remain_inside_their_header(self):
        # table_utils.js maps an input back to its column via input.closest('th'),
        # so the filter must stay nested in the header it filters.
        self.assertEqual(
            len(re.findall(r'class="form-control form-control-sm filter"', self.html)),
            len(DISPLAY_FIELDS),
        )

    def test_empty_state_row_spans_the_displayed_columns(self):
        # filterTable() identifies this row by `cells.length === 1 && colSpan > 1`
        # and never hides it; that only holds while the colspan is emitted.
        html = render_table([])
        self.assertIn(f'colspan="{len(DISPLAY_FIELDS)}"', html)
        self.assertIn("No items found", html)


class ModelTablePageTests(TestCase):
    """The contract must hold on a real page, not only in isolated renders."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="tableuser", password="tablepass123", email="table@example.com"
        )
        self.client.login(username="tableuser", password="tablepass123")

    def test_thread_listing_renders_sortable_headers(self):
        response = self.client.get("/threads/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertIn('class="sortable"', content)

    def test_thread_listing_loads_the_table_script(self):
        response = self.client.get("/threads/")
        self.assertIn("js/table_utils.js", response.content.decode("utf-8"))
