
# js Directory

## Purpose
This directory contains client-side JavaScript files that provide interactive functionality for the parody news generator's user interface. These scripts enhance the user experience with dynamic form handling, table utilities, UI frameworks, and content management features.

## Contents
- `content_detail.js`: JavaScript for dynamic content detail forms, handles assistant selection and auto-populates instructions fields via AJAX
- `halfmoon.js`: UI framework library for enhanced interface components and styling
- `issue_submission.js`: Handles form submission functionality for issue reporting and content creation
- `table_utils.js`: Provides sorting and filtering functionality for data tables throughout the application

## Usage
These JavaScript files are included in Django templates:

```html
<!-- In Django templates -->
{% load static %}
<script src="{% static 'js/content_detail.js' %}"></script>
<script src="{% static 'js/table_utils.js' %}"></script>
<script src="{% static 'js/halfmoon.js' %}"></script>
<script src="{% static 'js/issue_submission.js' %}"></script>
```

Key functionality:
- **content_detail.js**: Dynamic form field population based on assistant selection
- **table_utils.js**: Interactive table sorting and filtering for data management
- **halfmoon.js**: UI component library for consistent interface styling
- **issue_submission.js**: Form validation and submission handling

### table_utils.js markup contract

`table_utils.js` binds by selector on `DOMContentLoaded`, so a table only gets
sorting and filtering if its markup satisfies all of the following. Getting one
of these wrong fails silently — no console error, just a control that does
nothing. (`includes/model_table.html` satisfies the contract; anything hand-rolling
a table must too.)

| Requirement | Why |
| --- | --- |
| The table carries `class="table"` | the script's entry selector is `document.querySelectorAll('.table')` |
| Each sortable header carries `class="sortable"` | the click handler binds to `th.sortable`; without the class no listener is attached and clicking the header does nothing |
| Non-text columns carry `data-type="number"` or `data-type="date"` | `sortTable` reads `dataset.type` to choose its comparator; with no type it compares with `localeCompare`, so `10` sorts before `2` |
| Each filter is an `input.filter` nested inside its own `<th>` | `filterTable` maps the input back to a column via `input.closest('th').cellIndex` |
| An empty-state row is a single `<td>` with `colspan` > 1 | `filterTable` special-cases that shape so "No items found" is never filtered away |

Behaviour notes:

- Clicks originating inside an `input`, `textarea`, `select`, or `label` are
  ignored by the sort handler, so typing in a column's filter does not re-sort it.
- Sorting is single-column: activating one header clears `data-order`/`aria-sort`
  on the others.
- Binding happens once, at `DOMContentLoaded`. Tables inserted into the DOM later
  are **not** wired up.

In Django templates the `data-type` value comes from the `sort_data_type` filter
in `parodynews/templatetags/custom_filters.py`, which maps a model field's
internal type to `number`, `date`, or `""`.

## Container Configuration
JavaScript files are served as static assets:
- Collected with `python manage.py collectstatic`
- Served through Django's static file configuration
- Cached by web browsers for performance
- Minified in production deployments

## Related Paths
- Incoming: Loaded by Django templates in web browser clients
- Outgoing: Makes AJAX requests to Django views, manipulates DOM elements
