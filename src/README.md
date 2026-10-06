# src/

The application source: the Django project, the React frontend, and the Jekyll sidecar that publishes finished articles.

## Contents

| Path | What it is |
|---|---|
| `barodybroject/` | Django project configuration — split settings, URLs, WSGI/ASGI |
| `parodynews/` | The main Django app ([README](parodynews/README.md)) |
| `frontend/` | The React + Vite user interface ([README](frontend/README.md)) |
| `setup/` | First-run installation wizard |
| `pages/` | Jekyll site for published content |
| `assets/`, `static/` | Static assets and collected static output |
| `posthog/` | Analytics integration |
| `manage.py` | Django management entry point |
| `requirements.txt` | Python dependencies |
| `pytest.ini` | Test configuration (run pytest from this directory) |
| `Dockerfile` | Two-stage build: Node builds the frontend, Python serves it |
| `gunicorn.conf.py` | Production WSGI configuration |

## Running it

The dev workflow is container-first:

```bash
docker compose -f ../.devcontainer/docker-compose_dev.yml up -d
```

That brings up PostgreSQL, Django, and the Vite dev server together. Note that the dev container starts Django under `debugpy --wait-for-client`, so port 8000 stays silent until a debugger attaches.

Locally, without containers:

```bash
python manage.py migrate
python manage.py sync_models     # populate the AI model catalogue
python manage.py runserver

cd frontend && npm install && npm run dev    # in a second terminal
```

## How the frontend reaches the browser

There is no separate web server for assets. `vite build` emits hashed files and a `dist/.vite/manifest.json`; `parodynews/views/spa.py` reads that manifest to emit the correct tags, and WhiteNoise serves the files from the Django container. The `Dockerfile` builds the bundle in a Node stage and copies it in before `collectstatic`, so a deploy stays a single container.

In development, setting `FRONTEND_DEV_SERVER_URL` makes Django point at Vite instead, which gives hot reload without changing any template.

## Tests

```bash
python -m pytest                 # from this directory; e2e excluded by default
python -m pytest -m e2e          # Playwright, needs a running server
cd frontend && npm run test      # Vitest
```

## See also

- [`parodynews/README.md`](parodynews/README.md) — the application
- [`frontend/README.md`](frontend/README.md) — the UI
- [`../.github/README.md`](../.github/README.md) — developer and CI documentation
