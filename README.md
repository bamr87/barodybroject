# Barodybroject

Barodybroject is a Django 5.1 application for generating and managing parody news content with OpenAI. It runs against PostgreSQL, exposes Django REST Framework endpoints, includes a Jekyll static-site sidecar for published content, and deploys to Azure Container Apps with Bicep infrastructure.

## Start Here

| Need | Link |
|---|---|
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

## In-app feedback

Every page rendered from `base.html` carries an "Improve this page" control that
files a **prefilled GitHub issue** without leaving the app. It is the
`<fleet-feedback>` web component from the
[bamr87/bamr87 feedback kit](https://github.com/bamr87/bamr87/blob/main/templates/feedback/README.md)
(spec: [UPS-FB](https://github.com/bamr87/bamr87/blob/main/specs/FEEDBACK.md)),
vendored into this repository rather than hot-linked.

Choosing a request type and writing a description opens a GitHub issue form that
already contains the page URL and view name, the browser and OS, and any console
errors captured before the dialog was opened. The issue is labelled
`page-feedback` plus a type label, and ends with a `<!-- fleet-feedback v1 ... -->`
marker.

**No credential is involved.** The widget runs in its default `url` mode: it
builds a `github.com/.../issues/new?...` link and lets GitHub's own session
authenticate the reporter. No token is served to the browser and there is no
server-side proxy. It also degrades gracefully — with JavaScript disabled, the
inline anchor still links to the
[`page_feedback.yml`](.github/ISSUE_TEMPLATE/page_feedback.yml) issue form.

| Piece | Path |
| --- | --- |
| Component (vendored, do not edit in place) | `src/assets/js/fleet-feedback.js` |
| Vendor provenance / kit version | `src/assets/js/fleet-feedback.VERSION` |
| Template include | `src/parodynews/templates/includes/fleet_feedback.html` |
| No-JS issue form | `.github/ISSUE_TEMPLATE/page_feedback.yml` |
| Settings | `FLEET_REPO`, `FLEET_BRANCH` in `src/barodybroject/settings/base.py` |

`FLEET_REPO` and `FLEET_BRANCH` default to `bamr87/barodybroject` and `main`, and
can be overridden per environment with the environment variables of the same
name — useful when running a fork so feedback lands on your own repository.

> Every label the widget applies must exist in the target repository:
> `page-feedback`, `bug`, `docs`, `feature`, `question`, `area:a11y`, `area:perf`.
> GitHub **silently drops** unknown labels from a prefilled URL, so a missing one
> fails invisibly. Check with `gh label list`.

## Cleanup Status

This repository previously contained generated README mirrors, one-shot AI implementation reports, disabled Django CMS shims, and placeholder models. Those artifacts have been removed so the codebase reflects the current Django/OpenAI/Azure application.
