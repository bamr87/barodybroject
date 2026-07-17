# Barodybroject — Agent Instructions

Django 5.1 + OpenAI parody news generator. Container-first, deployed to Azure Container Apps via Bicep.

## Start here

- Architecture, commands, env vars, deployment: [.github/README.md](README.md) (developer guide — read this first)
- General project overview: [README.md](../README.md)
- Domain-specific rules live in [.github/instructions/](instructions/) (auto-applied by `applyTo` globs)
- Project-specific gotchas / non-obvious facts: [.github/instructions/project.instructions.md](instructions/project.instructions.md)

## Critical project facts (don't guess these)

- **Two compose files**: `docker-compose.yml` (production-like, service `web-prod`) and `.devcontainer/docker-compose_dev.yml` (dev, service `python`). VS Code tasks use the **dev** file. Never run `docker compose up` from the root expecting hot-reload — that's prod mode.
- **Run Django commands inside the dev container**, not on host:
`docker compose -f .devcontainer/docker-compose_dev.yml exec python python manage.py <cmd>` Or use the workspace tasks (e.g. `🐍 Docker: Development Up`, `📊 Django: Run Migrations (Dev)`).
- **Working dir for Django** is `src/` (where `manage.py` lives). `pytest` must be invoked there.
- **Database is PostgreSQL only** — no SQLite fallback. Older docs may say otherwise; ignore them.
- **Settings are split by environment** under `src/barodybroject/settings/`: `base.py`, `development.py`, `production.py`, and `testing.py`.
- **`parodynews` app uses package layout**, not flat modules:
  - `parodynews/models/` (split: `ai.py`, `content.py`, `conversation.py`, `publishing.py`, `config.py`, `base.py`)
  - `parodynews/views/` (split: `api.py`, `assistants.py`, `content.py`, `posts.py`, `threads.py`, `schemas.py`, `base.py`, `utils.py`)
  - When adding/finding models or views, search the package — don't expect a single file.
- **Dev container waits for VS Code debugger** on port 5678 (`debugpy --wait-for-client`). The server won't start serving on `:8000` until the debugger attaches. To bypass, edit the `command:` block in `.devcontainer/docker-compose_dev.yml`.
- **Admin user is auto-created** on container start via `python manage.py ensure_admin` using `DJANGO_SUPERUSER_*` env vars. Don't write code that assumes a fresh DB has no superuser.

## Testing

- Config: [src/pytest.ini](../src/pytest.ini). Defaults: `--reuse-db --nomigrations -m "not e2e"`.
- Run: `pytest` from `src/` with `DJANGO_SETTINGS_MODULE=barodybroject.settings.testing` (the dev container itself exports development settings, so tests must override it). The VS Code test tasks do this for you.
- Markers: `unit`, `integration`, `api`, `e2e`, `slow`. E2E uses Playwright and is **excluded by default** — opt in with `-m e2e`.
- Test paths: `src/parodynews/tests/` and root `tests/`.
- Detailed standards: [.github/instructions/test.instructions.md](instructions/test.instructions.md).

## Conventions enforced by instruction files

| Topic | File | Applies to |
|---|---|---|
| Python/JS/Bash style | [languages.instructions.md](instructions/languages.instructions.md) | source files |
| Tests | [test.instructions.md](instructions/test.instructions.md) | `**/test_*.py`, `tests/**` |
| GitHub Actions | [workflows.instructions.md](instructions/workflows.instructions.md) | `.github/workflows/*.yml` |
| Markdown / docs | [documentation.instructions.md](instructions/documentation.instructions.md) | `**/*.md` |
| Feature pipeline | [features.instructions.md](instructions/features.instructions.md) | source files |
| Workspace layout | [space.instructions.md](instructions/space.instructions.md) | all |
| Jekyll posts | [posts.instructions.md](instructions/posts.instructions.md) | `src/pages/_posts/**` |

These files are large and aspirational. When they conflict with the actual codebase, **the codebase wins**. Note conflicts in your response and prefer the project facts above.

## Behavioral rules for agents

- **Never edit files inside running containers via terminal.** Edit on the host (volume mount handles sync).
- **Don't `pip install` on the host.** Add to `src/requirements.txt` (or `requirements-dev.txt`) and rebuild.
- **Don't commit secrets.** `.env` is gitignored; `OPENAI_API_KEY`, `SECRET_KEY`, `DJANGO_SUPERUSER_PASSWORD` come from env vars.
- **Long instruction files in `.github/instructions/` contain heavy philosophy / boilerplate code samples.** Skim, don't recite. Apply concrete rules; ignore the motivational filler.
- Do not restore the deprecated bloated version of this file from history.
