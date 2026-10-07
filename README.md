# Barodybroject

Barodybroject is a Django 5.2 application for generating and managing parody news content with AI. It runs against PostgreSQL, serves a React frontend over a Django REST Framework API, includes a Jekyll static-site sidecar for published content, and deploys to Azure Container Apps with Bicep infrastructure.

The AI layer is **provider-agnostic**: no application code imports a vendor SDK. Claude Code is the default provider, driven by a `CLAUDE_CODE_OAUTH_TOKEN`; Anthropic and OpenAI are built in, and adding another is one class plus a registry entry. Switching providers is a configuration change.

## Start Here

| Need | Link |
|---|---|
| AI provider layer | [src/parodynews/ai/README.md](src/parodynews/ai/README.md) |
| Frontend | [src/frontend/README.md](src/frontend/README.md) |
| Developer commands and architecture | [.github/README.md](.github/README.md) |
| AI agent guidance | [CLAUDE.md](CLAUDE.md) |
| Documentation index | [docs/README.md](docs/README.md) |
| Deployment guide | [docs/deployment/README.md](docs/deployment/README.md) |
| Configuration guide | [docs/configuration/README.md](docs/configuration/README.md) |
| Infrastructure | [infra/README.md](infra/README.md) |
| Scripts | [scripts/README.md](scripts/README.md) |
| Contribution guide | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

## Current Stack

**Backend**
- Python 3.10+ and Django 5.2 (LTS)
- Django REST Framework (session-cookie authenticated)
- PostgreSQL
- Claude Agent SDK (default), Anthropic SDK, OpenAI SDK — reached only through `parodynews.ai`
- Django Allauth for accounts

**Frontend**
- React 19, TypeScript, Vite 7, React Router 7
- Bootstrap 5, served by WhiteNoise from the Django container

**Tooling**
- Docker Compose for local/dev/prod-like workflows
- Azure Container Apps, Azure Developer CLI, and Bicep
- Pytest, Playwright, Vitest, Ruff, Black, and Sphinx

## Repository Layout

```text
barodybroject/
├── .devcontainer/        # Development compose stack used by VS Code tasks
├── .github/              # Copilot instructions, agents, prompts, workflows
├── docs/                 # Maintained project documentation
├── infra/                # Azure Bicep infrastructure
├── scripts/              # Host-side automation scripts
├── src/                  # Django project root
│   ├── barodybroject/    # Django project configuration
│   ├── parodynews/       # Main Django app
│   │   ├── ai/           # Provider-agnostic AI layer
│   │   ├── api/          # REST API the frontend consumes
│   │   └── services/     # Use cases
│   ├── frontend/         # React + Vite user interface
│   ├── pages/            # Jekyll site content
│   └── manage.py
├── test/                 # Ancillary infrastructure tests
└── docker-compose.yml    # Production-like compose stack
```

## Development Quick Start

The dev workflow is container-first. Use the dev compose file explicitly:

```bash
docker compose -f .devcontainer/docker-compose_dev.yml up -d barodydb python
docker compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py migrate
```

That compose file also starts a Vite dev server for the frontend, so the SPA hot-reloads while Django serves the API.

The dev container starts Django under `debugpy --wait-for-client` on port `5678`, so `localhost:8000` will not respond until a debugger attaches or that wait flag is removed. See [.github/README.md](.github/README.md) for the current workflow and caveats.

### Configuring a provider

Claude Code is the default. Mint a token on a machine where you are signed in to Claude Code:

```bash
claude setup-token          # prints a token starting sk-ant-oat...
```

Put it in `.env` as `CLAUDE_CODE_OAUTH_TOKEN`, or set `AI_DEFAULT_PROVIDER` to `anthropic` or `openai` and supply that provider's key instead. See [.env.example](.env.example) for every supported variable, and the [AI layer README](src/parodynews/ai/README.md) for how credentials resolve.

## Using the Application

Django owns a handful of prefixes, routed in [`src/barodybroject/urls.py`](src/barodybroject/urls.py); everything else is handed to the React SPA by the catch-all in [`src/parodynews/urls.py`](src/parodynews/urls.py).

| Path | What it is |
|---|---|
| `/setup/` | Installation wizard — runs first and handles redirects, see [docs/installation-wizard.md](docs/installation-wizard.md) |
| `/admin/` | Django admin |
| `/accounts/` | Sign-in and registration (Django Allauth), server-rendered |
| `/api/` | Django REST Framework browsable API |

The parody-content workflow is a client-side route in [`src/frontend/`](src/frontend/README.md): `/assistants` and `/assistant-groups` to configure assistants, `/content` to manage content items, `/threads` to run generation, `/messages` to review the results, `/posts` to edit and publish them, `/schemas` for the JSON schemas that shape assistant output, and `/settings` to configure AI providers. These are React routes, not Django views — the server returns the same SPA shell for all of them.

Publishing a post writes into the Jekyll sidecar in [`src/pages/`](src/pages/), which renders the public site with the `bamr87/zer0-mistakes` remote theme.

The REST API exposes the same objects as viewsets under `/api/`: `assistants`, `assistant-groups`, `content-items`, `content-details`, `threads`, `messages`, `posts`, `post-front-matters`, `post-versions`, `json-schemas`, `ai-models`, `providers` and `powered-by`.

Remember that the dev container starts Django under `debugpy --wait-for-client`, so none of these respond until a debugger attaches — see the caveat in [Development Quick Start](#development-quick-start).

## Testing

Pytest is configured in [src/pytest.ini](src/pytest.ini). Run tests from `src/` inside the dev container once development dependencies are installed:

```bash
docker compose -f .devcontainer/docker-compose_dev.yml exec -e DJANGO_SETTINGS_MODULE=barodybroject.settings.testing python python -m pytest
```

E2E tests are marked `e2e` and are excluded by default.

The frontend has its own suite:

```bash
cd src/frontend && npm install && npm run test
```

Tests never reach a real AI vendor: the testing settings resolve the provider registry to a mock that is held to the same JSON-schema contract as the real providers.

## Cleanup Status

This repository previously contained generated README mirrors, one-shot AI implementation reports, disabled Django CMS shims, and placeholder models. Those artifacts have been removed so the codebase reflects the current Django/React/Azure application.
