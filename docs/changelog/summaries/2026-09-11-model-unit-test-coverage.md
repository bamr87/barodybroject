---
title: "[Improvement] Unit-test coverage for every parodynews model"
type: "improvement"
version: "0.4.0"
date: "2026-09-11"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#51", "#50"]
related_prs: []
impact: "medium"
breaking: false
---

# Improvement: model unit tests, from 3 of 17 models covered to all of them

> **Summary**: Adds six `test_models_*.py` modules mirroring the `models/`
> package, shared model factories in `conftest.py` built from the real
> `tests/data/` exports, and fixes the `NoReverseMatch` in
> `Post.get_absolute_url()` that the new tests exposed.

## 📊 Before

`src/parodynews/models/` holds **17 model classes** across six modules. Only three — `Thread`, `Message`, `AppConfig` — were referenced by any model-level test, all of them incidentally, inside `test_thread_message_delete.py`. `test_model_table.py`'s 15 tests exercise the model-table *view*, which is a different guarantee, and `test_templates.py`'s 38 are template tests.

Statement coverage of `src/parodynews/models/` was **85%**, and `base.py` was at **0%**.

## ✅ Change

### Six test modules, mirroring the package

| module | covers |
| --- | --- |
| `test_models_base.py` | `TimestampedModel`, `DisplayFieldsMixin` |
| `test_models_config.py` | `PoweredBy`, `AppConfig`, `FieldDefaults` |
| `test_models_ai.py` | `JSONSchema`, `OpenAIModel`, `Assistant`, `AssistantGroup`, `AssistantGroupMembership` |
| `test_models_content.py` | `ContentDetail`, `ContentItem` |
| `test_models_conversation.py` | `Thread`, `Message` |
| `test_models_publishing.py` | `PostPageConfigModel`, `Post`, `PostFrontMatter`, `PostVersion` |

Each asserts field definitions and defaults, `__str__`, `get_display_fields()`, `Meta.ordering`, every `ForeignKey`/`ManyToMany`/`OneToOne`, and the `on_delete` behaviour of each relation — `CASCADE` and `SET_NULL` are asserted separately, because which one a relation uses is the difference between losing a published post and keeping it.

The two custom `save()` methods get behavioural tests rather than does-not-raise tests:

- `ContentItem.save()` numbers items **per parent detail**. An implementation
based on a global `count()` would pass a single-parent test; the added `test_save_numbers_each_detail_independently` fails it.
- `FieldDefaults.save()` exists only to `cache.delete("field_defaults")`. It is
asserted on insert, on update, and — separately — that it does *not* evict other keys, which is what a `cache.clear()` regression would do.

### Shared factories, built from the real exports

`conftest.py` gains `*_export` fixtures that read `tests/data/*.json` as-is and a chain of model factories (`user` → `openai_model` → `assistant` → `content_detail` → `content_item` → `thread` → `message` → `post`). No parallel fixture mechanism and no new dependency — `factory_boy` was deliberately not added.

`TimestampedModel` is the one class in the package that is not instantiated: it is `abstract = True` and has **no concrete subclass** in the tree (`OpenAIModel` and `Post` declare their own timestamp columns), so it is asserted through its field definitions and its abstractness.

### A completeness guard

`test_every_exported_model_has_a_test_module` asserts that every name in `parodynews.models.__all__` is referenced by one of the six modules, so a model added later without tests fails the suite instead of passing quietly.

## 🐛 Defect found and fixed

`Post.get_absolute_url()` raised on every call:

```python
# Before
return reverse("post_detail", kwargs={"pk": self.pk})
# django.urls.exceptions.NoReverseMatch: Reverse for 'post_detail' with keyword
# arguments '{'pk': 5}' not found. 1 pattern(s) tried:
# ['posts/(?P<post_id>[0-9]+)/\\Z']

# After
return reverse("post_detail", kwargs={"post_id": self.pk})
```

`parodynews/urls.py:161` declares the route as `posts/<int:post_id>/`. The method was never called by a test, and this is precisely the class of defect issue #51 was filed to surface. It is a one-word fix in `models/publishing.py`; no migration, no signature change.

## 🧪 Testing and Validation

Run from `src/` (config: `src/pytest.ini`, `e2e` excluded by default) against the project's PostgreSQL test database — `base.py` rejects SQLite outright:

```console
$ python -m pytest parodynews/tests -q
56 passed, 9 deselected          # before
173 passed, 9 deselected         # after
```

Statement coverage of `src/parodynews/models/`:

| module | before | after |
| --- | ---: | ---: |
| `__init__.py` | 100% | 100% |
| `ai.py` | 89% | 100% |
| `base.py` | **0%** | 100% |
| `config.py` | 87% | 100% |
| `content.py` | 79% | 100% |
| `conversation.py` | 95% | 100% |
| `publishing.py` | 87% | 100% |
| **TOTAL** | **85%** | **100%** |

`ruff check` and `ruff format --check` pass on every added and changed file.

## ⚠️ Breaking Changes and Migration

None. No model field changed, no migration is required, and no dependency was added to `pyproject.toml`.

## 🔗 Related Resources

- Issue: #51 (parent: #50)
- Package: `src/parodynews/models/README.md`
- Test conventions: `src/parodynews/tests/README.md`
- Fixture exports: `src/parodynews/tests/data/README.md`
- Route: `src/parodynews/urls.py` → `post_detail`
- [Django testing topics](https://docs.djangoproject.com/en/5.1/topics/testing/)
