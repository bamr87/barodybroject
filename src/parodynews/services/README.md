# Services

## Purpose

The application's use cases live here: generating content, running assistants on a thread, publishing a post. Views stay thin — they parse input and render output — and anything worth testing without HTTP lives in this package.

## Structure

```
services/
├── content.py      # Generate content from an assistant; apply the result to a ContentDetail
├── threads.py      # Build conversation history, run an assistant or a group
├── publishing.py   # Render a Jekyll post, version it, push it to GitHub
└── assistants.py   # Sync the model catalogue, delete assistants safely
```

## content.py

`generate_content()` is the main entry point. It returns a `GenerationOutcome` rather than raising on every problem, because the two failure modes are genuinely different:

- The **article body** failing is fatal — there is nothing to show the user.
- The **metadata** (title, slug, keywords) failing is a warning. The body is still good, so the outcome carries the text plus a note about what could not be derived.

`apply_content_detail()` takes the structured result and writes it onto a `ContentDetail`, slugifying the title and merging keywords with existing tags.

## threads.py

`build_history()` turns a thread's messages into the `ChatMessage` list a provider expects, skipping empty and failed turns so a previous error does not poison the next run.

`run_assistant()` records a `failed` message *and then re-raises*. Persisting the failure before propagating it is deliberate: the user can see what went wrong in the thread rather than losing the turn entirely.

`run_assistant_group()` runs each member in position order, and every member sees the output of those before it.

## publishing.py

`render_post()` produces the Jekyll file — YAML front matter plus body, named `YYYY-MM-DD-slug.md`. `publish_post()` pushes it to the configured GitHub repository and opens a pull request, raising `PublishingNotConfigured` when the GitHub settings are missing, so "you haven't set this up" doesn't surface as a confusing API error.

## assistants.py

`sync_models()` asks the configured provider for its catalogue and reconciles the `AIModel` table, returning a `SyncReport` (created / updated / deactivated). Providers that cannot enumerate models report `supports_model_discovery = False` and are skipped rather than failing.

## Conventions

- Services raise the `parodynews.ai` exception types; `parodynews/api/views.py` maps them to status codes in one place (`ai_error_response()`).
- No service imports a vendor SDK. If you find yourself wanting to, the thing you need probably belongs in [`../ai/`](../ai/README.md) instead.
- Services take and return model instances and dataclasses, never `Request`/`Response`.

## See also

- [`../ai/README.md`](../ai/README.md) — the provider layer these call
- [`../api/README.md`](../api/README.md) — the HTTP surface that calls these
