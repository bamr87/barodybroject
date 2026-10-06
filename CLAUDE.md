# CLAUDE.md

Guidance for AI coding agents (Claude Code, Copilot, Cursor) working in **barodybroject**.

Barodybroject is a Django 5.2 application for generating and managing parody news content with AI. It runs against PostgreSQL, serves a React SPA (`src/frontend/`) over Django REST Framework endpoints, includes a Jekyll static-site sidecar for published content (`src/pages/`), and deploys to Azure Container Apps via the Azure Developer CLI with Bicep infrastructure (`infra/`; `azure.yaml` maps the `src` service to a container app). The Django project root is `src/` (`barodybroject` = project config, `parodynews` = main app), with settings split into `barodybroject.settings.development` / `.production` / `.testing`. Deeper developer docs live in `.github/README.md`; the documentation index is `docs/README.md`.

## Architecture rules that matter most

**Never import a vendor AI SDK outside `src/parodynews/ai/providers/`.** Application code builds a `GenerationRequest` and calls the provider the registry resolves. If a task seems to need `anthropic`/`openai`/`claude_agent_sdk` in a service or view, the right change is almost always a new capability on the provider contract, not an import. See `src/parodynews/ai/README.md`.

**The default provider is `claude_code`, authenticated by `CLAUDE_CODE_OAUTH_TOKEN`.** OAuth tokens (`sk-ant-oat…`) and API keys (`sk-ant-api…`) go in different environment variables; the provider picks by prefix and blanks the other, so don't "helpfully" set both.

**The UI is React.** `src/frontend/` is the user interface; Django renders only the SPA shell, the allauth account pages, and error pages. Don't add a Django template for an application screen. The API is session-cookie authenticated — there is no token flow to add.

**Conversations live in our database.** Threads and messages are replayed to the provider on every call; no provider is asked to keep state. Anything that would make a thread depend on a vendor's server-side conversation breaks provider portability.

## Stack & commands

The dev workflow is container-first — use the dev compose file explicitly. Caveat: the dev container starts Django under `debugpy --wait-for-client` on port `5678`, so `localhost:8000` will not respond until a debugger attaches (or that wait flag is removed).

```bash
# install dependencies (local venv; pulls in src/requirements.txt too):
pip install -r requirements-dev.txt

# run the dev stack (Django + PostgreSQL):
docker compose -f .devcontainer/docker-compose_dev.yml up -d barodydb python
docker compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py migrate

# run tests (config: src/pytest.ini; run from src/ in the container; `e2e` marker excluded by default):
docker compose -f .devcontainer/docker-compose_dev.yml exec -e DJANGO_SETTINGS_MODULE=barodybroject.settings.testing python python -m pytest

# lint (ruff/black config in pyproject.toml; CI gates on src/):
ruff check src/ && black --check src/

# frontend (from src/frontend/):
npm install && npm run dev      # Vite dev server
npm run test                    # Vitest
npm run build                   # typecheck + build (what the container serves)

# deploy (Azure Developer CLI):
azd up          # provision + deploy
azd deploy      # deploy only
```

Local (non-container) alternative: from `src/`, `python manage.py migrate && python manage.py runserver` against a `.env` in the repo root.

## Conventions

- Conventional Commits: `type(scope): description` (`feat`/`fix`/`docs`/`refactor`/`test`/`chore`/`ci`).
- Default branch is `main` — branch from it and open a PR; never push to it directly.
- README-First, README-Last: read the nearest `README.md` before changing a directory, and update it after.
- Don't suppress type errors (`as any`, `@ts-ignore`, `# type: ignore`) or leave empty exception handlers.
- `src/` is lint-clean and CI blocks on it. The root `test/` and `scripts/` directories are pre-existing debt and excluded — don't treat their findings as yours, and don't add new code there.
- Migrations must reverse. Verify forward → reverse → forward against seeded rows, not just `migrate`. See `src/parodynews/migrations/README.md` for the two traps that bite.
- Document notable changes under `docs/changelog/` per `docs/changelog/CONTRIBUTING_CHANGES.md`, and reference the change doc in the PR (see `CONTRIBUTING.md`).

## Fleet context

This repo is one of ~40 managed by the [bamr87/bamr87 dash](https://github.com/bamr87/bamr87) (registry: `_data/projects.yml`; tiered baseline: `docs/STANDARDS.md`). It is vendored there as a git submodule: commit and push changes **here** first — the hub only bumps its pointer afterwards. Shared CI, release, schema, and agent kits are seeded from the hub's `templates/`; prefer adopting those over hand-rolling equivalents.
