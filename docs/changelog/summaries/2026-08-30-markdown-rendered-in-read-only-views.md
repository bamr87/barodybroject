---
title: "[Feature] Render Markdown in read-only views, raw source only when editing"
type: "feature"
version: "0.4.0"
date: "2026-08-30"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: ["#56", "#57"]
related_prs: ["#165"]
impact: "medium"
breaking: false
affected_versions: ["0.4.0"]
---

# Feature: Markdown renders as HTML when you are viewing a field, raw when you are editing it

> **Summary**: `content_detail.html` displayed raw Markdown in form widgets — including a
> read-only one — while four other templates rendered the same content correctly. Markdown-bearing
> fields now render through the app's one server-side renderer, revealing raw source only where the
> field is actually editable. A sanitizer allow-list was added so headings and paragraphs stop being
> deleted after they are rendered.

## 🎯 Motivation

From #56: *"I'm always frustrated when i see raw markdown text when viewing fields."* #57 is the expanded specification.

`content_detail.html` loaded `{% load markdownify %}` and never applied the filter, rendering every field through `{% bootstrap_form content_form %}` instead. `ContentItemForm.instructions` is a read-only `Textarea`, so a field the user can only *view* displayed raw Markdown.

## ✅ What changed

### The field partial

`parodynews/templates/parodynews/_markdown_field.html` renders one Markdown-bearing field in two shapes, chosen by whether the widget is read-only:

| shape | rendered HTML | raw source |
| --- | --- | --- |
| read-only | yes | **not in the DOM at all** — a hidden input carries the value forward so POST semantics are unchanged |
| editable | yes | the real widget, hidden by `content_detail.js` on load |

`content_detail.html` renders field-by-field and includes the partial for the names in `ContentItemForm.markdown_fields`; every other field keeps its identical `django-bootstrap5` rendering.

The editor is hidden by JavaScript rather than by the template, deliberately: with JavaScript off the field stays editable instead of becoming permanently invisible.

### The blur round trip

`content_detail.js` re-renders a field on blur by POSTing to the new `markdown_preview` view (`parodynews/views/content.py`, `@login_required @require_POST`), which returns `render_markdown(...)` output — already sanitized. **No client-side Markdown library was added.** One would bypass bleach and inject unsanitized HTML into the DOM, which is a stored-XSS path in an app whose content is AI-generated and user-editable, in a public repository. A test asserts none was introduced.

On a failed request the preview is left as it was and the editor stays open, so a dropped request can never blank a field or destroy what the user typed.

### The sanitizer allow-list (`MARKDOWNIFY["default"]`)

Wiring the renderer up exposed a second, older defect. The project had **no `MARKDOWNIFY` setting**, so django-markdownify fell back to `bleach.sanitizer.ALLOWED_TAGS` — a comment-thread allow-list of `a, abbr, acronym, b, blockquote, code, em, i, li, ol, strong, ul`. It contains no `h1`-`h6` and no `p`. Markdown rendered headings and paragraphs correctly and the sanitizer then
deleted them, on **every** page that used `|markdownify`:

```
# Heading

Some **bold** text.
```

rendered as `Heading Some <strong>bold</strong> text.` — a wall of unstructured text. "The HTML output format should be rendered" was only half-true.

`settings/base.py` now declares the allow-list explicitly: block structure (`p`, `br`, `hr`, `h1`-`h6`, `blockquote`, `pre`), lists, and inline formatting; `href`/`title` as the only attributes; `http`/`https`/`mailto` as the only protocols; no inline CSS.

Two deliberate omissions:

- **`img` stays out.** It was already excluded by the bleach default. An allowed `<img>` in
  AI-generated, user-editable content is a remote-resource beacon that fires on view.
- **`STRIP` stays at its default (`True`).** A disallowed tag is removed and its text kept — the
behaviour the four already-shipping templates have always had. `STRIP: False` (escape to `&lt;script&gt;`) is equally inert but would change the output of every one of those pages, which #57 does not ask for.

### `|linebreaksbr` dropped from the new partial

The partial's rendered div is replaced on blur by the raw body of `markdown_preview`. A filter applied only in the template made the field reflow the first time the user focused and left it — the same content with two renderings on one page. With `p` and `br` now allowed, Markdown's own paragraphing does the job. The three static templates keep the filter; they have no blur round trip.

### `|safe` dropped from `pages_post_detail.html`

`|markdownify` already returns a sanitized `SafeString`, so the trailing `|safe` was a no-op that
read like autoescaping being switched off deliberately. Output is unchanged.

## 🧪 Testing

`src/parodynews/tests/test_markdown_rendering.py` — the renderer, the endpoint, the partial, and static guarantees about the wiring:

- `test_headings_and_paragraphs_survive_sanitization` — fails without the `MARKDOWNIFY` block.
- `test_output_matches_the_filter_the_other_templates_use` — one renderer, one result.
- `test_blur_round_trip_reproduces_the_server_rendered_field` — the partial's rendered region is
  byte-identical to the preview endpoint's body. Fails with `|linebreaksbr` in the template.
- `test_readonly_field_has_no_editor_to_reveal_raw_source` — no `<textarea>` in the DOM for a
  read-only field, and the value still submits.
- `test_editor_is_visible_without_javascript` — the partial emits no `d-none`.
- Sanitization: script tags, event-handler attributes, `javascript:` URLs, and a payload stored in
a field value (checked in both the rendered half and the escaped source half, with the rendered half's emitted tags diffed against the allow-list in settings).
- `test_no_client_side_markdown_renderer_was_introduced` — no `marked`/`showdown` anywhere.

These need the project's PostgreSQL test database (`base.py` rejects SQLite outright), so the DB-backed run happens in the `tests` job of `.github/workflows/ci.yml` on Python 3.10, 3.11 and 3.12.

## ⚠️ Breaking changes and migration

None. No migrations, no new dependencies, no configuration a deployment must supply.

Behavioural note for reviewers: adding `MARKDOWNIFY["default"]` changes rendered output on `message_detail.html`, `thread_detail.html`, `content_processing.html` and `pages_post_detail.html` too — headings and paragraphs now appear where they were previously deleted. That is the intended fix, applied once, in one place.

## 🔗 Related resources

- Issues: #56 (original report), #57 (specification)
- Renderer: `src/parodynews/utils/markdown.py` → `render_markdown`
- Allow-list: `src/barodybroject/settings/base.py` → `MARKDOWNIFY`
- Partial: `src/parodynews/templates/parodynews/_markdown_field.html`
- Endpoint: `src/parodynews/views/content.py` → `markdown_preview`
- Directory guide: `src/parodynews/templates/parodynews/README.md`
