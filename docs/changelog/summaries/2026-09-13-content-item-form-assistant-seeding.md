---
title: "[Test] Pin the assistant-selection behaviour issue #3 asked for"
type: "test"
version: "0.6.0"
date: "2026-09-13"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#3"]
related_prs: ["#180"]
impact: "low"
breaking: false
severity: "low"
affected_versions: ["0.6.0"]
---

# Test: the assistant select cannot regress to seeding a random assistant

> **Summary**: The defect issue #3 describes was removed by #183, which deleted
> the form it lived in. This adds the regression test the issue's last open
> acceptance criterion asks for, against the React component that replaced the
> form, so the behaviour cannot come back unobserved.

## 🐛 Problem Description

### Issue Summary

`ContentItemForm.__init__` (`src/parodynews/forms.py`) could not tell a brand-new form from a saved `ContentItem` whose nullable `assistant` FK was `NULL`. Django's `BaseModelForm` builds `self.initial` from `model_to_dict(instance)`, which reports `assistant: None` for **both**. The code tested `if not self.initial.get("assistant")` and answered the ambiguity with:

```python
random_assistant = Assistant.objects.annotate(num=Count("id")).order_by("?").first()
```

So opening an existing item that had no assistant pre-selected a **random** one — potentially a different one on each reload — and `views/content.py:112` saved the form against the existing instance, which meant pressing Save on any unrelated edit silently persisted that random choice. `ContentItem.assistant` is `on_delete=SET_NULL`, so items reach the triggering state on their own whenever an assistant is deleted.

### Why this change is a test and not a fix

`main` @ 32a9e2f (#183, "provider-agnostic AI framework … React frontend") deleted `src/parodynews/forms.py`, `mixins.py`, every `views/*.py` except the SPA shell, and the server-rendered templates. `ContentItemForm` does not exist. The content authoring screen is `src/frontend/src/pages/Content.tsx`, and it does not carry the defect:

```tsx
assistant: item?.assistant ?? '',          // load: bound straight to the record
assistant: form.assistant || null,         // save: empty stays NULL
```

`grep -rn 'order_by("?")' src/` returns nothing, and the only surviving mentions of `ContentItemForm` are in `docs/DJANGO_BOOTSTRAP5_MIGRATION.md`.

So every behavioural criterion on #3 is already satisfied by `main`. The one that was not is the last: *"A test … covers all four cases above."*

## ✅ Solution Implementation

`src/frontend/src/pages/Content.test.tsx` — 6 Vitest specs against `ContentDetailPage` with `../api/endpoints` mocked:

| Test | Asserts |
|---|---|
| `pre-selects nothing when the item has no assistant` | The blank `<option>` is the selected one |
| `is stable across renders when the item has no assistant` | The value is `''` — asserting *empty*, not "not Alpha", which is what makes it able to fail against a non-deterministic `order_by("?")` |
| `shows the item's own assistant when it has one` | No regression on the populated case |
| `saves NULL rather than silently reassigning an unmodified item` | The `PATCH` payload carries `assistant: null` |
| `saves the assistant the user picks` | The explicit choice reaches the payload |
| `starts empty and asks for an explicit choice` | A new item seeds nothing and fetches nothing |

### One deliberate deviation from the issue

Criterion 4 reads *"A new, unsaved form still seeds a default assistant and its instructions."* The React screen deliberately does **not**: a new item starts with "Select an assistant" and the Generate button stays disabled until one is picked (`disabled={pending || !form.assistant}`, `title="Pick an assistant first"`). Seeding an arbitrary default was the mechanism behind this very bug, and an explicit choice is the better behaviour. The test pins the explicit-choice behaviour rather than the criterion as literally written.

## 🧪 Testing and Validation

```console
$ cd src/frontend && npx vitest run
Test Files  4 passed (4)
     Tests  31 passed (31)

$ npx tsc --noEmit
(clean)
```

**These tests pass on arrival — that is the point, and it is also why they were checked the other way round.** Reintroducing the defect in `Content.tsx`:

```diff
-      assistant: item?.assistant ?? '',
+      assistant: item?.assistant ?? assistantsState.data?.[1]?.id ?? '',
```

fails 4 of the 6, including both cases that matter: the select is no longer empty, and the save payload carries `asst_bravo` instead of `null`. The change was then reverted; `Content.tsx` is untouched by this PR.

## ⚠️ Breaking Changes and Migration

None. This PR adds one test file and two documentation paragraphs. No application code changes.

## 🔄 Prevention Measures

`src/frontend/README.md` now names the specs that exist to pin behaviour the Django UI got wrong — `DataTable.test.tsx` (#96) and `Content.test.tsx` (#3) — and records that each was verified by reintroducing the original defect.

## 🔗 Related Resources

- Issue [#3](https://github.com/bamr87/barodybroject/issues/3)
- [`src/frontend/README.md`](../../../src/frontend/README.md)
- `main` @ 32a9e2f — the rewrite that removed the defect
