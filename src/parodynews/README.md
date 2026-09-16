# parodynews

The main Django application: creating, generating, and publishing parody news content.

## What changed in v0.6.0

Two structural changes worth reading before you work in here.

**The AI layer is provider-agnostic.** No application code imports a vendor SDK. Everything goes through [`ai/`](ai/README.md), which defines one provider contract and resolves the configured implementation at runtime. Claude Code is the default, driven by a `CLAUDE_CODE_OAUTH_TOKEN`; Anthropic, OpenAI, and a test mock are also built in. Switching providers is configuration, not code.

**The UI is React.** The Django template UI and its view modules are gone, replaced by [`../frontend/`](../frontend/README.md) talking to [`api/`](api/README.md). What remains server-rendered is the allauth account pages and the SPA shell.

## Contents

### Core files
- `admin.py` — Django admin configuration
- `apps.py` — app config (`ParodynewsConfig`)
- `context_processors.py` — `site_links`, which also hands the allauth pages the React bundle's CSS so they need no third-party requests
- `resources.py` — import/export resource definitions
- `serializers.py` — legacy serializers (the API's own live in `api/serializers.py`)
- `urls.py` — routing; Django-owned prefixes first, then a catch-all that hands everything else to the SPA

### Packages

| Directory | Contains |
|---|---|
| [`ai/`](ai/README.md) | The provider contract, registry, and the four providers |
| [`api/`](api/README.md) | DRF viewsets, serializers, pagination — the SPA's only interface |
| [`services/`](services/README.md) | Use cases: generate content, run assistants, publish posts |
| [`models/`](models/README.md) | Domain models, organized by area |
| [`views/`](views/) | Just `spa.py` now — reads the Vite manifest and renders the shell |
| [`management/`](management/README.md) | Management commands, including `sync_models` |
| [`migrations/`](migrations/README.md) | Database migrations |
| [`schema/`](schema/README.md) | Bundled JSON schemas for structured output |
| [`templates/`](templates/README.md) | The SPA shell and the server-rendered account pages |
| [`tests/`](tests/README.md) | Test suite |
| [`utils/`](utils/README.md) | Markdown rendering, DKIM email backend, schema helpers, field defaults |

## How a request flows

```
React (frontend/)
  -> /api/...            api/views.py      parse, authorize
  -> services/...        services/*.py     the actual use case
  -> parodynews.ai       ai/registry.py    pick the configured provider
  -> provider            ai/providers/*    one vendor call
  <- GenerationResult    validated against the caller's JSON schema
```

Each layer has one job, and the boundary that matters most is the last one: everything above `ai/` is written against `GenerationRequest`/`GenerationResult` and never sees a vendor's vocabulary.

## Running it

See [the repository README](../../README.md) for the dev stack. Quick reference, from `src/`:

```bash
python manage.py migrate
python manage.py sync_models          # populate the AIModel catalogue
python manage.py runserver
python -m pytest                      # from src/
```

## See also

- [`../frontend/README.md`](../frontend/README.md) — the user interface
- [`../../CLAUDE.md`](../../CLAUDE.md) — conventions for AI coding agents
- [`../../docs/changelog/`](../../docs/changelog/) — change records
