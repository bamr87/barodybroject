# Frontend

React 19 + TypeScript + Vite. This is the application's user interface; the Django template UI it replaced has been removed.

## Structure

```
frontend/
├── src/
│   ├── api/          # client.ts (fetch + CSRF), endpoints.ts, types.ts
│   ├── components/   # DataTable, Layout, Markdown, RequireAuth, ui primitives
│   ├── hooks/        # useAsync, useTheme
│   ├── pages/        # One component per route
│   ├── App.tsx       # Routes
│   ├── AppContext.tsx# Session + site metadata
│   └── main.tsx      # Entry point
├── vite.config.ts
└── package.json
```

## Running it

```bash
# Alongside a running Django server:
cd src/frontend
npm install
npm run dev          # http://localhost:5173, proxying /api to Django

# Or bring up the whole dev stack, which includes a `frontend` service:
docker compose -f .devcontainer/docker-compose_dev.yml up -d
```

In development, Django detects `FRONTEND_DEV_SERVER_URL` and points the page at Vite so you get hot reload. With it unset, Django serves the built bundle instead.

| Command | Does |
|---|---|
| `npm run dev` | Vite dev server with HMR |
| `npm run build` | Typecheck, then build to `dist/` |
| `npm run test` | Vitest |
| `npm run lint` | `tsc --noEmit` |

## How Django serves the build

Not with a separate web server or a CDN. `vite build` writes hashed assets plus a `dist/.vite/manifest.json`; `parodynews/views/spa.py` reads that manifest and emits the right `<script>`/`<link>` tags, and WhiteNoise serves the files out of the Django container. The Dockerfile builds the bundle in a Node stage and copies `dist` into the Python image before `collectstatic`.

The upshot is that a deploy is still one container, and the asset hashes come from the manifest rather than being guessed or hardcoded.

## Authentication

Session cookies. The SPA does not implement login — `/accounts/login/` is a server-rendered allauth page — so there is no token to store or refresh. `api/client.ts` reads the CSRF token from the `csrf` meta tag and attaches it to writes; a 403 with an authentication error redirects to the login page.

## `DataTable`

Worth knowing about because it carries a contract forward. The Django UI had a `table_utils.js` that gave every table sortable headers, per-column filters that combine, and — importantly — two *different* empty states:

- **"No items found"** — the server returned nothing
- **"No matching records"** — the server returned rows but your filters excluded them all

Collapsing those two into one message is the kind of small regression that makes a UI feel broken ("where did my data go?"). `DataTable.tsx` keeps them distinct, and `DataTable.test.tsx` asserts it.

## Testing

Vitest with Testing Library, run in CI by the `frontend` job alongside a typecheck and a build.

One gotcha that cost real time: when stubbing `fetch`, use `mockImplementation(async () => jsonResponse(...))`, not `mockResolvedValue(jsonResponse(...))`. The latter hands the *same* `Response` object to every call, and a `Response` body can only be read once — the second call fails with "Body is unusable". A fresh object per call is what the real `fetch` does anyway.

Some specs exist to pin behaviour the Django UI got **wrong**, so the component that replaced it cannot regress to it:

| Spec | Pins |
|---|---|
| `components/DataTable.test.tsx` | The sorting and empty-state contract the old `table_utils.js` carried (issue #96) |
| `pages/Content.test.tsx` | The assistant select: an existing item with no assistant pre-selects **nothing** and saves `null`, rather than being given an arbitrary one (issue #3) |

They pass on arrival — that is the point. Each was checked by reintroducing the original defect and confirming it fails.

## Conventions

- `api/types.ts` mirrors the DRF serializers. When an API shape changes, change it there first and let the typechecker find the call sites.
- Styling is Bootstrap 5 plus `styles.css`; there is no CSS-in-JS.
- Theme is stored per-viewer in `localStorage`, with a small pre-paint script in the Django template so a dark-mode reload doesn't flash white.

## See also

- [`../parodynews/api/README.md`](../parodynews/api/README.md) — the API this consumes
- [`../parodynews/views/spa.py`](../parodynews/views/spa.py) — manifest reading and the dev-server branch
