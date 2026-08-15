"""
File: test_model_table_e2e.py
Description: Playwright E2E coverage for table sorting and filtering
Author: Barodybroject Team
Created: 2026-08-15
Version: 1.0.0

Dependencies:
- pytest
- pytest-playwright
- django (template rendering only; no database access)

Usage:
  pytest -m e2e --browser chromium

The reported symptom is runtime behaviour, so it needs a real browser. Two
layers here:

1. `test_list_page_headers_are_sortable` drives the real running server and
   asserts the markup the server actually sends carries `th.sortable`. This is
   the half that fails on a pre-fix build.
2. The behaviour tests render the real `model_table.html` and load the real
   `table_utils.js` into the page, then click and type. Driving the partial
   directly rather than a seeded list page keeps row order and content
   deterministic — the app has no fixture command that guarantees two or more
   comparable rows on any list page.
"""

from pathlib import Path

import pytest
from django.contrib.auth.models import User
from django.template.loader import render_to_string

# src/parodynews/tests/e2e/ -> src/
SRC_ROOT = Path(__file__).resolve().parents[3]
TABLE_UTILS_JS = SRC_ROOT / "assets" / "js" / "table_utils.js"

DISPLAY_FIELDS = ["id", "username", "date_joined"]

# Ids chosen so numeric and lexicographic ordering disagree: sorted as text the
# order is 1, 10, 2; sorted as numbers it is 1, 2, 10. Only a column carrying
# data-type="number" gets the latter.
ROWS = [
    User(id=2, username="bravo"),
    User(id=10, username="charlie"),
    User(id=1, username="alpha"),
]


def table_html(objects):
    return render_to_string(
        "includes/model_table.html",
        {
            "objects": objects,
            "fields": User._meta.get_fields(),
            "display_fields": DISPLAY_FIELDS,
            "detail_url": "edit_content",
            "table_label": "Test Table",
        },
    )


def mount(page, objects=ROWS):
    """Put the real partial and the real script in a page and wire them up."""
    page.set_content(f"<!DOCTYPE html><html><body>{table_html(objects)}</body></html>")
    page.add_script_tag(path=str(TABLE_UTILS_JS))
    # The script binds on DOMContentLoaded, which already fired for the content
    # we injected, so fire it once more now that the listener is registered.
    page.evaluate("document.dispatchEvent(new Event('DOMContentLoaded'))")
    return page


def column_values(page, column_index):
    return page.eval_on_selector_all(
        f"tbody tr td:nth-child({column_index + 1})",
        "cells => cells.map(c => c.textContent.trim())",
    )


def visible_usernames(page):
    return page.eval_on_selector_all(
        "tbody tr",
        """rows => rows
            .filter(r => r.style.display !== 'none')
            .map(r => r.cells[1].textContent.trim())""",
    )


def click_header_label(page, index):
    """Click a header's label area — the part of the cell that sorts.

    The filter input is a full-width `.form-control` sitting below the label, so
    it covers the middle of the cell. A default Playwright click lands on the
    input and is (correctly) ignored by the sort handler, so target the top-left
    of the cell, where the label and its padding are.
    """
    header = page.locator("th.sortable").nth(index)
    header.click(position={"x": 4, "y": 4})
    return header


@pytest.mark.e2e
def test_list_page_headers_are_sortable(logged_in_page):
    """The running server must send headers the sort handler can bind to."""
    page = logged_in_page
    page.goto("/threads/")
    page.wait_for_load_state("domcontentloaded")

    assert page.locator("table.table th.sortable").count() > 0, (
        "no th.sortable on the rendered page — table_utils.js binds its click "
        "handler to that selector, so sorting is dead"
    )


@pytest.mark.e2e
def test_clicking_a_header_sorts_and_toggles_direction(page):
    mount(page)

    header = click_header_label(page, 1)  # username, a text column
    assert visible_usernames(page) == ["alpha", "bravo", "charlie"]
    assert header.get_attribute("aria-sort") == "ascending"

    click_header_label(page, 1)
    assert visible_usernames(page) == ["charlie", "bravo", "alpha"]
    assert header.get_attribute("aria-sort") == "descending"


@pytest.mark.e2e
def test_sorting_a_second_column_clears_the_first(page):
    mount(page)

    first = click_header_label(page, 1)
    second = click_header_label(page, 0)

    assert first.get_attribute("aria-sort") == "none"
    assert second.get_attribute("aria-sort") == "ascending"


@pytest.mark.e2e
def test_numeric_columns_sort_numerically_not_lexicographically(page):
    mount(page)
    click_header_label(page, 0)  # id, data-type="number"

    # Lexicographic ordering would give 1, 10, 2.
    assert column_values(page, 0) == ["1", "2", "10"]


@pytest.mark.e2e
def test_clicking_the_filter_input_does_not_sort_the_column(page):
    """Regression: the filter input is nested inside the clickable header."""
    mount(page)
    before = visible_usernames(page)

    page.locator("th.sortable").nth(1).locator("input.filter").click()

    assert visible_usernames(page) == before
    assert page.locator("th.sortable").nth(1).get_attribute("aria-sort") == "none"


@pytest.mark.e2e
def test_typing_in_a_filter_narrows_that_column_and_clearing_restores(page):
    mount(page)
    filter_input = page.locator("th.sortable").nth(1).locator("input.filter")

    filter_input.fill("al")
    assert visible_usernames(page) == ["alpha"]

    filter_input.fill("")
    assert sorted(visible_usernames(page)) == ["alpha", "bravo", "charlie"]


@pytest.mark.e2e
def test_filtering_is_case_insensitive(page):
    mount(page)
    page.locator("th.sortable").nth(1).locator("input.filter").fill("ALPHA")

    assert visible_usernames(page) == ["alpha"]


@pytest.mark.e2e
def test_the_empty_state_row_is_never_hidden_by_filtering(page):
    mount(page, objects=[])
    page.locator("th.sortable").nth(1).locator("input.filter").fill("zzz-no-match")

    empty_row = page.locator("tbody tr").first
    assert empty_row.is_visible()
    assert "No items found" in empty_row.text_content()
