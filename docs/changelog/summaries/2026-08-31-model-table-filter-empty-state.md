---
title: "[Bug Fix] Model table — explain an empty result instead of blanking silently"
type: "bugfix"
version: "0.4.0"
date: "2026-08-31"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#96", "#87", "#95"]
related_prs: ["#161"]
impact: "low"
breaking: false
severity: "medium"
affected_versions: ["0.4.0"]
---

# Bug Fix: filtering a model table to zero matches emptied it with no message

> **Summary**: Adds the filter-empty state to `model_table.html` and makes
> `filterTable()` evaluate all active column filters at once, so filtering to
> nothing says so — and so two filters combine instead of overwriting each other.

## 🐛 Problem Description

### Issue Summary

Issue [#96](https://github.com/bamr87/barodybroject/issues/96) reported that the per-column filter inputs did nothing. Most of that was **already fixed** by [#161](https://github.com/bamr87/barodybroject/pull/161) (merged 2026-08-20), which repaired the `model_table.html` ⇄ `table_utils.js` selector contract. Two of the issue's three acceptance criteria passed on `main` @ `23ad0ad`.

The third did not. Typing a string that matched no rows hid every data row and left the user looking at a header above an empty body, with nothing to say whether the filter was too narrow or the data was missing.

Investigating it surfaced a second, unreported defect in the same function: **`filterTable` only ever considered one column.** It took `(table, columnIndex, query)` and set `row.style.display` for *every* row from that one column's value, so typing in a second column silently un-hid everything the first had filtered out. The two are fixed together because the "no matches" message cannot be correct while the match count is computed from one filter.

### Affected Components

- **`src/parodynews/templates/includes/model_table.html`** — the shared partial behind every model list, so this affected all of them at once.
- **`src/assets/js/table_utils.js`** — `filterTable()`.
- **User experience**: rows vanished with no explanation; multiple filters did not combine.

### Reproduction Steps

1. Open any model list page with at least one row.
2. Type `zzzzzz` into any column filter.
3. Observed: all rows disappear, no message.
4. Expected: a visible "No matching records" row, which clears when the filter is relaxed.

For the multi-filter half: filter column A to narrow the list, then type in column B. Observed: rows column A had excluded reappear.

## 🔍 Root Cause Analysis

### Root Cause

`filterTable` preserved the server-side `{% empty %}` row (a single `<td>` with `colspan > 1`) but never **created** an empty state of its own, and no such row existed in the template for it to show. There was no code path that could produce the message.

The multi-column defect had the same shape: the function's signature only admitted one column, so per-column state could not be combined.

### Contributing Factors

- The `{% empty %}` row made the table *look* like it had an empty state; the case it covers (server returned nothing) is not the case users hit.
- Nothing pinned "filtering to zero matches" in either test suite.

## ✅ Solution Implementation

### Fix Description

1. **Template** — `model_table.html` now renders a second empty-state row,
   always present and shipping hidden:

   ```html
   <tr data-filter-empty style="display: none;">
       <td colspan="{{ display_fields|length }}" class="text-center text-muted"
           role="status" aria-live="polite">
           No matching records
       </td>
   </tr>
   ```

   It lives in the template, not in JavaScript, so the message stays translatable and the `colspan` tracks `display_fields`. It replaces content that otherwise disappears unannounced, hence `role="status"`.

2. **JavaScript** — `filterTable(table)` now takes only the table and re-reads every `input.filter` on each keystroke. A row survives if it matches **all** active filters. The function counts data rows and survivors, then shows the message only when `filters.length > 0 && dataRows > 0 && matches === 0` — so it never stacks on top of the server's own "No items found".

   Re-reading every filter (rather than only the one that changed) is what makes clearing one filter re-apply the rest instead of revealing rows they still exclude.

`style.display` is the toggle for both, matching how the rest of the function works and keeping the row out of "visible row" queries while hidden.

## 🧪 Testing and Validation

### Test Cases Added

`src/parodynews/tests/test_model_table.py` — `FilterEmptyStateMarkupTests`, six tests asserting the row renders, starts hidden, spans the displayed columns, carries `role="status"` / `aria-live="polite"`, appears exactly once, and is present whether or not the server returned rows. These run in the **default** suite (`-m "not e2e"`), so the markup half is covered where no browser is available.

`src/parodynews/tests/e2e/test_model_table_e2e.py` — six Playwright tests for the behaviour: the message appears on zero matches, clears when the filter is relaxed *or* cleared, appears exactly once with two filters active, is announced to assistive technology, does not stack on the server empty state, and — the multi-filter regression — clearing one of two filters re-evaluates rather than revealing rows the other still excludes.

Two existing helpers (`visible_usernames`, `column_values`) now skip single-cell rows, since the partial has a second full-width row for them to trip over.

### Test Results

Run from `src/` (config: `src/pytest.ini`; `e2e` is deselected by default):

```bash
python -m pytest parodynews/tests/test_model_table.py
python -m pytest -m e2e --browser chromium parodynews/tests/e2e/test_model_table_e2e.py
```

The behaviour was additionally verified by executing the **real** `table_utils.js` against the rendered markup in a jsdom document. Against the new template row with the **pre-fix** `filterTable`, six checks fail — the message never clears, the two filters do not combine, clearing one filter reveals everything, and the message stacks on the server empty state — which is what shows the JavaScript change is required and not only the template row.

## ⚠️ Breaking Changes and Migration

`filterTable`'s signature changed from `(table, columnIndex, query)` to `(table)`. It is not exported and the only call site is its own `input` handler, so nothing else needs updating. Any hand-rolled table calling it directly must drop the extra arguments; the markup contract is unchanged and is documented in `src/assets/js/README.md`.

No migrations, no configuration changes.

## 🔄 Prevention Measures

- Both empty states are now described side by side in `src/assets/js/README.md` and `src/parodynews/templates/includes/README.md`, with what each one means.
- The template's own contract comment states that removing the row removes the message, since `table_utils.js` only toggles it.
- The markup half is asserted in the default (non-e2e) suite, so it cannot regress unnoticed on a build without browsers.

## 🔗 Related Resources

- Original bug report: [#96](https://github.com/bamr87/barodybroject/issues/96) (parent [#95](https://github.com/bamr87/barodybroject/issues/95))
- Prior fix for the same partial: [#161](https://github.com/bamr87/barodybroject/pull/161), opened against [#87](https://github.com/bamr87/barodybroject/issues/87)
- Partial: `src/parodynews/templates/includes/model_table.html`
- Script: `src/assets/js/table_utils.js`
