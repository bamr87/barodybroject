# tests

## Purpose

The test suite for the parodynews application: 349 Python tests covering models, the AI provider layer, services, the REST API, templates, plus a Playwright end-to-end suite.

## Contents

| File | Covers |
|---|---|
| `conftest.py` | Shared fixtures — model factories, API clients, the mock-provider reset, and the Playwright session fixtures |
| `test_ai_layer.py` | [`parodynews.ai`](../ai/README.md): the provider contract, the registry, and each built-in provider |
| `test_api.py` | The REST API: authentication, permissions, pagination, and the AI error → status mapping |
| `test_models_*.py` | One module per `models/` module, one-for-one |
| `test_services_*.py` | Content generation, thread runs, publishing |
| `test_post_publish.py` | Publication **failure** reporting (issue #114): every GitHub refusal becomes a reader-facing message, a non-404 is never answered by a second write, and the endpoint returns it instead of a 500 |
| `test_templates.py` | The SPA shell, the Vite manifest branches, and the auth pages |
| `e2e/test_spa.py` | Playwright specs against a running server, marked `@pytest.mark.e2e` |
| `data/` | Real exports the factories build from |

## Running

From `src/`:

```bash
python -m pytest                      # e2e deselected by default (pytest.ini)
python -m pytest -k "test_models"     # one area
python -m pytest -m e2e --browser chromium   # needs a running server
python -m pytest --cov=parodynews --cov-report=term-missing
```

## The mock provider is the point

Tests do not reach a real AI vendor, and they also do not monkey-patch one. `settings.testing` sets `AI_DEFAULT_PROVIDER = "mock"`, so the *registry itself* resolves to `MockProvider` and every layer above it runs its real code path — services, serializers, views, error mapping.

```python
def test_generation_records_the_model(mock_provider, assistant, content_detail):
    mock_provider.queue_response(build_example(assistant.json_schema.schema))
    outcome = generate_content(assistant, content_detail)
    assert outcome.result.provider == "mock"
```

Two things make this trustworthy rather than a comfortable fiction:

- **The mock validates against the caller's schema like any other provider.** Queue a response that does not satisfy the schema and the test fails exactly where production would.
- **`queue_response()` accepts an exception.** Failure paths — a provider erroring mid-thread, a configuration error surfacing as a 400 — are tested with the same seam as the happy path.

An autouse `reset_mock_provider` fixture clears the recorded calls and the queue between tests, so ordering never leaks.

## Fixtures compose

The factories chain: asking for `post` transitively creates the `user`, `content_detail`, `thread`, `message`, `assistant`, `ai_model` and `json_schema` it needs. Each depends on `db`, so requesting one is enough to get database access — no extra `@pytest.mark.django_db`.

```python
def test_a_post_belongs_to_its_author(post, user):
    assert post.user == user
```

Factories live in `conftest.py`, not per file, so a field rename breaks in one place. The `*_export` fixtures read `data/*.json` — real exports, not invented literals — so a test that passes against a fabricated shape cannot pass against a shape the application never produces.

API tests get `api_client`, `staff_api_client` and `anon_api_client` rather than building clients inline, which keeps the permission boundary explicit in the test's signature.

## End-to-end

`e2e/test_spa.py` drives the real SPA in Chromium against a real server. It is deselected by default because it needs one; CI runs it in the `e2e` job, which builds the frontend bundle first — without it Django renders a shell with nothing in it.

## Conventions

- Test names are sentences: `test_a_disabled_provider_cannot_be_used`, not `test_provider_disabled_1`. The failure output should read as the claim that broke.
- One behaviour per test. If the name needs "and", it is two tests.
- `test_models_publishing.py` carries a completeness guard: it fails if a name in `parodynews.models.__all__` is not referenced by any `test_models_*.py` module. Add a model and the suite tells you it is untested.

## Related paths

- [`../ai/README.md`](../ai/README.md) — the layer `test_ai_layer.py` pins
- [`../../frontend/README.md`](../../frontend/README.md) — Vitest lives there, run separately
