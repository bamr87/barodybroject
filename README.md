# Barodybroject

Barodybroject is a Django 5.1 application for generating and managing parody news content with OpenAI. It runs against PostgreSQL, exposes Django REST Framework endpoints, includes a Jekyll static-site sidecar for published content, and deploys to Azure Container Apps with Bicep infrastructure.

## Start Here

| Need | Link |
|---|---|
| Developer commands and architecture | [.github/README.md](.github/README.md) |
| Documentation index | [docs/README.md](docs/README.md) |
| Deployment guide | [docs/deployment/README.md](docs/deployment/README.md) |
| Configuration guide | [docs/configuration/README.md](docs/configuration/README.md) |
| Infrastructure | [infra/README.md](infra/README.md) |
| Scripts | [scripts/README.md](scripts/README.md) |
| Contribution guide | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |

## Current Stack

- Python 3.10+ and Django 5.1
- Django REST Framework
- PostgreSQL
- OpenAI Python SDK
- Bootstrap templates and Django Allauth
- Docker Compose for local/dev/prod-like workflows
- Azure Container Apps, Azure Developer CLI, and Bicep
- Pytest, Playwright, Selenium, Ruff, and Sphinx

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

The dev container starts Django under `debugpy --wait-for-client` on port `5678`, so `localhost:8000` will not respond until a debugger attaches or that wait flag is removed. See [.github/README.md](.github/README.md) for the current workflow and caveats.

## Testing

Pytest is configured in [src/pytest.ini](src/pytest.ini). Run tests from `src/` inside the dev container once development dependencies are installed:

```bash
docker compose -f .devcontainer/docker-compose_dev.yml exec -e DJANGO_SETTINGS_MODULE=barodybroject.settings.testing python python -m pytest
```

E2E tests are marked `e2e` and are excluded by default.

## Cleanup Status

This repository previously contained generated README mirrors, one-shot AI implementation reports, disabled Django CMS shims, and placeholder models. Those artifacts have been removed so the codebase reflects the current Django/OpenAI/Azure application.
