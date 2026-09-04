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

That fix reached the shared component only. Four list templates hand-rolled
their own tables and kept the pre-fix markup, so on those pages the filter box
worked, the sort affordance rendered, and clicking a header still did nothing.
`SortableHeaderPartialTests` and `TemplateSourceContractTests` below extend the
same contract to them, and the source-level sweep is what stops the next
hand-rolled table from re-introducing it.
"""

import re
from pathlib import Path

from django import forms
from django.contrib.auth.models import User
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase

import parodynews
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
        # Model._meta.get_fields() can yield reverse relations and other
        # pseudo-fields with no get_internal_type(). model_table.html iterates
        # that list verbatim, so the filter must degrade to text, not raise.
        # (Whether any such field exists depends on which apps are installed —
        # this asserts the tolerance, not the presence.)
        class PseudoField:
            name = "logentry"

        self.assertEqual(sort_data_type(PseudoField()), "")
        self.assertEqual(sort_data_type(None), "")

    def test_no_field_on_a_real_model_raises(self):
        for field in User._meta.get_fields():
            self.assertIn(sort_data_type(field), {"", "number", "date"})


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


# ---------------------------------------------------------------------------
# The four hand-rolled list tables
# ---------------------------------------------------------------------------

TEMPLATES_DIR = Path(parodynews.__file__).resolve().parent / "templates"

# Every template that renders a list table but cannot use {% render_model_table %},
# because its rows carry click-through handlers, embedded forms, or static columns.
HAND_ROLLED_TEMPLATES = [
    "parodynews/assistant_detail.html",
    "parodynews/assistant_group_detail.html",
    "parodynews/thread_detail.html",
    "parodynews/message_detail.html",
]


class _StubForm(forms.Form):
    """Minimal stand-in so {% bootstrap_form %} renders without the database."""

    name = forms.CharField(required=False)


_StubFormSet = forms.formset_factory(_StubForm, extra=0)


class _StubThread:
    """`thread_detail.html` only renders its table when a thread is selected."""

    thread_id = "thread_stub"


def render_page(template_name):
    """Render one of the list templates with no database access.

    Headers come from `fields`/`display_fields`, not from the row querysets, so
    empty object lists still exercise every <th> the page can emit.
    """
    return render_to_string(
        template_name,
        {
            "fields": User._meta.get_fields(),
            "display_fields": DISPLAY_FIELDS,
            # Row sources — empty, so each table renders its empty state.
            "assistants_info": [],
            "assistant_groups_info": [],
            "thread_messages": [],
            "message_list": [],
            "threads": [],
            "assistants": [],
            # Selected-object flags.
            "current_thread": _StubThread(),
            "current_message": None,
            "assistant_id": None,
            "assistant_group_id": None,
            # Forms.
            "assistant_form": _StubForm(),
            "assistant_group_form": _StubForm(),
            "assistant_group_formset": _StubFormSet(),
        },
    )


COMMENT_RE = re.compile(
    r"\{%\s*comment\s*%\}.*?\{%\s*endcomment\s*%\}|\{#.*?#\}", flags=re.DOTALL
)


def strip_template_comments(source):
    """Drop Django template comments so their example markup is not scanned."""
    return COMMENT_RE.sub("", source)


def headers_with_filters(html):
    """Opening <th> tags whose cell contains a per-column filter input."""
    return [
        match.group(1)
        for match in HEADER_CELL_RE.finditer(html)
        if "filter" in match.group(2)
    ]


class SortableHeaderPartialTests(SimpleTestCase):
    """The shared header partial emits the same contract as model_table.html."""

    def render_header(self, label="Title", sort_type=""):
        return render_to_string(
            "includes/sortable_header.html",
            {"label": label, "sort_type": sort_type},
        )

    def test_header_carries_the_sortable_class(self):
        self.assertIn('class="sortable"', self.render_header())

    def test_header_starts_unsorted(self):
        self.assertIn('aria-sort="none"', self.render_header())

    def test_header_nests_its_filter_input(self):
        header = self.render_header()
        self.assertIn("form-control-sm filter", header)
        self.assertLess(header.index("filter"), header.index("</th>"))

    def test_typed_columns_emit_their_comparator(self):
        self.assertIn('data-type="number"', self.render_header(sort_type="number"))
        self.assertIn('data-type="date"', self.render_header(sort_type="date"))

    def test_text_columns_emit_no_comparator(self):
        # A stray data-type="" would make sortTable's `type` truthy-check wrong.
        self.assertNotIn("data-type", self.render_header(sort_type=""))


class HandRolledTableContractTests(SimpleTestCase):
    """The four templates that cannot use the inclusion tag must still comply.

    This is the regression the issue describes: each of these rendered a filter
    box and a sort indicator inside a plain `<th scope="col">`, so
    `table_utils.js:7` matched zero elements and clicking a header did nothing
    while the page advertised that it would.
    """

    def test_every_filterable_header_is_also_sortable(self):
        for template_name in HAND_ROLLED_TEMPLATES:
            with self.subTest(template=template_name):
                headers = headers_with_filters(render_page(template_name))
                self.assertTrue(
                    headers, f"{template_name} rendered no filterable header"
                )
                for header in headers:
                    self.assertIn('class="sortable"', header)

    def test_every_filterable_header_starts_unsorted(self):
        for template_name in HAND_ROLLED_TEMPLATES:
            with self.subTest(template=template_name):
                for header in headers_with_filters(render_page(template_name)):
                    self.assertIn('aria-sort="none"', header)

    def test_the_dead_sort_indicator_span_is_gone(self):
        # A decorative empty <span class="sort-indicator"> that no CSS styles and
        # no JS reads. It was the visible half of the false affordance.
        for template_name in HAND_ROLLED_TEMPLATES:
            with self.subTest(template=template_name):
                self.assertNotIn("sort-indicator", render_page(template_name))

    def test_message_id_column_sorts_numerically(self):
        # The static-column case: without data-type this sorts 1, 10, 2.
        html = render_page("parodynews/message_detail.html")
        self.assertIn('data-type="number"', header_for(html, "ID"))

    def test_message_actions_column_advertises_nothing(self):
        # It holds only buttons, so it carries neither a filter nor a sort class.
        html = render_page("parodynews/message_detail.html")
        actions = [
            match.group(1)
            for match in HEADER_CELL_RE.finditer(html)
            if "Actions" in match.group(2)
        ]
        self.assertEqual(len(actions), 1)
        self.assertNotIn("sortable", actions[0])
        self.assertNotIn("filter", actions[0])

    def test_assistant_rows_keep_their_click_through(self):
        # Migrating these onto render_model_table would have dropped this, which
        # is why they use the header partial instead.
        for template_name, url_name in (
            ("parodynews/assistant_detail.html", "assistant_detail"),
            ("parodynews/assistant_group_detail.html", "assistant_group_detail"),
        ):
            with self.subTest(template=template_name):
                # No rows are rendered here, so assert the row-link machinery is
                # still in the template source rather than in the output.
                source = (TEMPLATES_DIR / template_name).read_text(encoding="utf-8")
                self.assertIn('role="link"', source)
                self.assertIn('tabindex="0"', source)
                self.assertIn(url_name, source)


class TemplateSourceContractTests(SimpleTestCase):
    """A sweep over template SOURCE, so a new hand-rolled table cannot regress.

    The rendering tests above only cover templates someone remembered to list.
    This one reads every template in the app and fails on any header that
    advertises filtering without opting into sorting — the exact shape of the
    original defect.
    """

    def all_template_sources(self):
        for path in sorted(TEMPLATES_DIR.rglob("*.html")):
            # allauth's vendored templates are not project list views.
            if "allauth" in path.parts:
                continue
            # Comments are not markup: model_table.html and sortable_header.html
            # both quote `<th scope="col">` in their contract notes, and matching
            # those would report the two compliant components as offenders.
            yield path, strip_template_comments(path.read_text(encoding="utf-8"))

    def test_no_template_has_a_filterable_but_unsortable_header(self):
        offenders = []
        for path, source in self.all_template_sources():
            for match in HEADER_CELL_RE.finditer(source):
                opening, body = match.group(1), match.group(2)
                if "filter" in body and "sortable" not in opening:
                    offenders.append(path.relative_to(TEMPLATES_DIR).as_posix())
        self.assertEqual(
            offenders,
            [],
            "these templates render a column filter in a header that "
            f"table_utils.js will never bind a sort handler to: {offenders}",
        )

    def test_no_template_still_renders_the_dead_sort_indicator(self):
        offenders = [
            path.relative_to(TEMPLATES_DIR).as_posix()
            for path, source in self.all_template_sources()
            if "sort-indicator" in source
        ]
        self.assertEqual(offenders, [])
