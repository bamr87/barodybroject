# REST API

## Purpose

The JSON API the React frontend talks to. It is the only interface to the application's data — the Django template UI it replaced is gone.

## Structure

```
api/
├── urls.py         # Router registration; mounted at /api/
├── views.py        # ViewSets and the AI error -> HTTP status mapping
├── serializers.py  # DRF serializers for every exposed model
└── pagination.py   # StandardPagination (page size 25, max 200)
```

## Authentication

Session cookies plus CSRF, not tokens. The SPA and the server-rendered allauth pages share one login, so signing in at `/accounts/login/` is all the frontend needs; there is no second token flow to keep in sync or to leak.

Requests therefore need:

- The `sessionid` cookie (the browser sends it)
- An `X-CSRFToken` header on anything that writes — the SPA reads it from the `csrf` meta tag that `templates/spa/index.html` renders

Everything requires authentication by default (`IsAuthenticated`). Provider configuration endpoints additionally require staff.

## Error mapping

`ai_error_response()` translates the `parodynews.ai` exception hierarchy into status codes, in one place:

| Exception | Status | Why |
|---|---|---|
| `AIConfigurationError` | 400 | The deployment is misconfigured — a retry will not help |
| `AIProviderError` | 502 | The upstream vendor failed |
| `AIResponseError` | 502 | The model answered unusably |

The 400/502 split matters to the frontend: a 400 shows the operator a "check your settings" message, a 502 offers a retry.

## Provider endpoints

`ProviderViewSet` is how the settings screen works:

| Route | Does |
|---|---|
| `GET /api/providers/` | List providers with their configured/unconfigured state |
| `GET /api/providers/{slug}/models/` | The `AIModel` rows for that provider |
| `POST /api/providers/{slug}/sync/` | Refresh the catalogue from the vendor |
| `POST /api/providers/{slug}/test/` | Send one trivial generation to prove the credential works |
| `PUT /api/providers/{slug}/config/` | Save credentials and defaults |
| `POST /api/providers/{slug}/set-default/` | Make it the default provider |

`config` never returns a stored API key, and an empty `api_key` in a request means "leave the stored credential alone" — otherwise opening and saving the settings form would wipe the key. Clearing one is explicit: `clear_api_key: true`.

## Conventions

- Views contain no business logic; they call [`../services/`](../services/README.md).
- Every list endpoint is paginated. The frontend's `DataTable` assumes the `{count, next, previous, results}` envelope.
- Throttling is 120/hour anonymous, 2000/hour authenticated, and disabled entirely in the testing settings.

## See also

- [`../../frontend/README.md`](../../frontend/README.md) — the client
- [`../services/README.md`](../services/README.md) — where the work happens
