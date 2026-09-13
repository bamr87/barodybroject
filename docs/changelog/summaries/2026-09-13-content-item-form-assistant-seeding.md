---
title: "[Bug Fix] ContentItemForm seeded a random assistant onto saved items that had none"
type: "bugfix"
version: "0.4.0"
date: "2026-09-13"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#3"]
related_prs: []
impact: "medium"
breaking: false
severity: "high"
affected_versions: ["0.4.0"]
---

# Bug Fix: the Assistant Name field on the content form did not reflect the record being edited

> **Summary**: `ContentItemForm` could not tell a brand-new form from a saved
> `ContentItem` whose `assistant` is `NULL`, so it treated the second as the
> first — showing an arbitrary assistant's instructions and offering a select
> with no empty option, which made "no assistant" unrepresentable and
> un-saveable.

## 🐛 Problem Description

### Issue Summary

Opening an existing `ContentItem` whose `assistant` is `NULL` showed a populated
**Assistant Name** select and a populated read-only **instructions** textarea,
neither of which belonged to the record. Because `ContentItem.assistant` is
`on_delete=SET_NULL`, *every* item whose assistant is later deleted lands in
exactly this state without anyone having created it that way.

### Affected Components

- **`src/parodynews/forms.py`**: `ContentItemForm.__init__` — the seeding branch
  and the `widget.choices` override.
- **User Experience**: `/content/<id>/` displayed another assistant's
  instructions, and pressing *Save* persisted that assistant onto the record.

### Reproduction Steps

1. Create a `ContentItem` whose `assistant` is `NULL` — or create one with an
   assistant and then delete that `Assistant`, which `SET_NULL` turns into the
   same state.
2. Open it for editing: `GET /content/<content_detail_id>/`.
3. Observe the **Assistant Name** select and the **instructions** textarea.

## 🔍 Root Cause Analysis

### Root Cause

The seeding branch was guarded by the value of `self.initial`:

```python
# Only set the assistant field to a random record if the form is new
if not self.initial.get("assistant"):
```

The comment states the intent; the condition does not test it. Django's
`BaseModelForm.__init__` builds `self.initial` from `model_to_dict(instance)`,
which yields `assistant: None` for **both** a brand-new form and a saved record
whose `assistant` is `NULL`. The two are indistinguishable to `self.initial`.
Whether the instance has been saved — `self.instance.pk is None` — is the
discriminator the code actually needed.

### Contributing Factors

Two details decided how the defect surfaced, and are worth recording because the
obvious reading of the code is wrong about one of them:

- **The randomly-seeded assistant never reached the select.**
  `BoundField.value()` resolves to `self.form.initial.get(name, field.initial)`,
  and for a saved instance the key `"assistant"` *exists* with value `None` — so
  it shadows the `self.fields["assistant"].initial` the branch had just set.
  What the user saw came from the second factor.
- **The `widget.choices` override dropped the blank option.** `__init__`
  replaced the field's `ModelChoiceIterator` with a plain list of
  `(id, name)` pairs, which does not include `ModelChoiceField.empty_label`. A
  `<select>` with no empty option and nothing marked `selected` displays its
  first entry, so the browser showed an arbitrary assistant — and submitted it
  on the next *Save*, writing it to the record (`views/content.py:112` binds the
  form to the existing instance).
- **`instructions` is a plain form field**, not a model field, so it is absent
  from `self.initial` and `self.fields["instructions"].initial` *did* take
  effect — which is why the textarea showed a stranger's instructions.
- The declared `assistant = forms.ModelChoiceField(...)` defaulted to
  `required=True`, contradicting the model's `null=True, blank=True`.

## ✅ Solution Implementation

### Fix Description

Seed a default assistant only when `self.instance.pk is None`; keep the blank
choice when overriding the widget's choices; and make the form field optional so
it matches the model.

### Code Changes

```python
# Before
self.fields["assistant"].widget.choices = [
    (assistant.id, assistant.name) for assistant in Assistant.objects.all()
]
if not self.initial.get("assistant"):
    random_assistant = (
        Assistant.objects.annotate(num=Count("id")).order_by("?").first()
    )
    ...

# After
self.fields["assistant"].widget.choices = [
    ("", self.fields["assistant"].empty_label),
    *((assistant.id, assistant.name) for assistant in Assistant.objects.all()),
]
assistant_id = self.initial.get("assistant")
if assistant_id:
    ...                                   # show the record's own assistant
elif self.instance.pk is None:
    default_assistant = Assistant.objects.order_by("?").first()
    ...                                   # seed only a genuinely new form
else:
    self.fields["instructions"].initial = ""
```

The unused `.annotate(num=Count("id"))` is removed — the annotation was never
read and `.order_by("?")` ignores it — along with the now-unused `Count` import.

No configuration or database changes.

## 🧪 Testing and Validation

### Test Cases Added

`src/parodynews/tests/test_forms_content.py` — four tests built on the existing
`conftest.py` factories:

- `test_new_form_seeds_a_default_assistant` — an unsaved form still gets one.
- `test_existing_item_shows_its_own_assistant` — no regression for the normal case.
- `test_saved_item_without_assistant_preselects_nothing` — the select rests on the
  empty choice and the instructions textarea is empty. Asserted as *empty*, never
  as "≠ this particular assistant": the old code picked with `.order_by("?")`, so
  a value-inequality assertion would pass at random.
- `test_saving_an_untouched_null_assistant_item_leaves_it_null` — an unrelated
  edit round-trips without acquiring an assistant.

### Test Results

Run from `src/` against the project's PostgreSQL test database (`base.py` rejects
SQLite outright):

```bash
DJANGO_SETTINGS_MODULE=barodybroject.settings.testing python -m pytest \
  src/parodynews/tests
```

Before the change, two of the four fail — `This field is required.` on the save
round-trip, and a stranger's instructions in the textarea. After it:

```
183 passed, 15 deselected in 16.35s
```

`ruff check` is clean on both changed files.

## ⚠️ Breaking Changes and Migration

None. `assistant` becoming `required=False` on the form widens what is accepted
and matches the model's existing `blank=True`; no migration is involved.

## 🔄 Prevention Measures

- The new-vs-saved distinction is now asserted rather than implied by a comment.
- The blank choice is covered by a rendering assertion, so an override that drops
  it again fails the suite.

## 🔗 Related Resources

- Original Bug Report: #3
- Form: `src/parodynews/forms.py` → `ContentItemForm.__init__`
- Model: `src/parodynews/models/content.py` → `ContentItem.assistant` (`SET_NULL`)
- Call sites: `src/parodynews/views/content.py:55,62,112`
- [Django `ModelForm` — initial data from an instance](https://docs.djangoproject.com/en/5.1/topics/forms/modelforms/)
