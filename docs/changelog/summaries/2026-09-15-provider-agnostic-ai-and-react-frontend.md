---
title: "[BREAKING] Provider-agnostic AI framework with Claude Code as the default, and a React frontend"
type: "breaking"
version: "0.6.0"
date: "2026-09-15"
author: "Barodybroject Team <team@example.com>"
reviewers: []
related_issues: []
related_prs: []
impact: "high"
breaking: true
migration_required: true
affected_versions: ["0.5.0"]
---

# Breaking Change: the AI layer is provider-agnostic and the UI is React

> **⚠️ BREAKING CHANGE**: Deployments must configure an AI provider credential, and the Django template UI has been replaced. Database migrations are required and are reversible.

## 🚨 Breaking Change Summary

### What changed

Two things, in one release because they touch the same code.

**The application is no longer built around one AI vendor.** Every AI call now goes through `parodynews.ai`, which defines a single provider contract and resolves the configured implementation at runtime. Claude Code is the default, authenticated with a `CLAUDE_CODE_OAUTH_TOKEN`. Anthropic, OpenAI, and a test mock are also built in. No application code imports a vendor SDK.

**The user interface is a React single-page app.** The Django template UI, its view modules, its forms, and its hand-written JavaScript are gone, replaced by `src/frontend/` talking to a REST API. What remains server-rendered is the SPA shell and the django-allauth account pages.

### Who is affected

- **Operators**: A provider credential is now required. `OPENAI_API_KEY` alone still works if you set `AI_DEFAULT_PROVIDER=openai`, but the default has changed.
- **Database**: Two migrations. Both reversible, both tested in both directions.
- **API consumers**: The API moved to `/api/` and is session-cookie authenticated.
- **Anyone with a custom template override**: Application templates no longer exist.

### Impact level

**High.** The application will start without a provider credential but cannot generate content until one is configured. The failure is explicit — an `AIConfigurationError` surfacing as HTTP 400 with the missing variable named — rather than a silent 500.

## 📋 Detailed changes

### The provider contract

```python
from parodynews.ai import ChatMessage, GenerationRequest, get_provider

provider = get_provider()             # resolves the configured default
result = provider.generate(
    GenerationRequest(
        messages=[ChatMessage("user", "Write a headline about a cat mayor.")],
        system="You are a parody news writer.",
        json_schema=schema,           # optional structured output
    )
)
```

Four providers ship: `claude_code` (default, via the Claude Agent SDK), `anthropic`, `openai`, and `mock`. Adding a fifth is one subclass plus a line in `BUILTIN_PROVIDERS`.

Three decisions are worth recording, because they are what make the abstraction hold up rather than leak:

**Structured output is validated identically everywhere.** Each provider asks for JSON in its own dialect — the Agent SDK takes an `output_format`, the Anthropic API an `output_config.format`, OpenAI a strict `response_format` — but all four then parse and validate against the caller's JSON Schema with `jsonschema`. A provider that returns almost-valid JSON fails loudly instead of quietly writing malformed content. The mock provider is held to the same standard: its canned responses are generated from the schema, so a test cannot pass against a shape production would reject.

**Message normalization lives in the base class.** `AIProvider.normalize()` folds system turns into the system prompt and guarantees the first *and last* turn are user turns. That last part is not stylistic — current Claude models reject a trailing assistant turn, so when a thread ends with an assistant reply the layer appends a continuation prompt. Putting this in the base class means a provider author cannot forget it.

**Conversation state is ours.** Threads and messages are stored locally and replayed to the provider on every call. Nothing depends on a provider remembering anything, which is exactly what lets a thread started on Claude continue on GPT — and is why the OpenAI Assistants/Threads API could be dropped entirely.

### Configuration breaking changes

```bash
# Before
OPENAI_API_KEY=sk-...

# After — the default provider
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat...      # from `claude setup-token`

# ...or keep using OpenAI, explicitly
AI_DEFAULT_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

Credentials resolve database row → environment variable → class default, so a deployment can be reconfigured from the settings UI without a redeploy.

One subtlety that will otherwise cost someone an afternoon: Claude accepts both OAuth tokens (`sk-ant-oat…`) and API keys (`sk-ant-api…`), and they must be passed in *different* environment variables. `ClaudeCodeProvider.credential_env()` picks by prefix and **blanks the other variable**. Without that, a stale `ANTHROPIC_API_KEY` left in a container environment silently wins over the OAuth token you just configured, and the resulting failure looks like a billing problem.

### Database schema changes

`0002_provider_agnostic_ai`:

| Before | After |
|---|---|
| `OpenAIModel` | `AIModel`, with a `provider` field; unique on `(provider, model_id)` |
| `AppConfig.api_key` / `org_id` / `project_id` | Copied into an `AIProviderConfig` row for `openai`, then dropped |
| `AssistantGroupMembership.assistants` | `assistant` (singular) |
| Integer thread/message ids | Locally minted `thread_…` / `msg_…` |
| — | `Message.role`, `.provider`, `.model_id`, `.remote_id`, `.usage`, `.error` |

Existing assistant replies are identified by the OpenAI `run_id` they carry and tagged `role="assistant"`, `provider="openai"`, so old threads read correctly.

`0003_drop_nullable_text_columns` backfills NULLs in `Assistant.name`, `Assistant.description` and `Message.run_id`, then makes those columns `NOT NULL` with a default.

### API breaking changes

The API is at `/api/`, paginated, and authenticated by session cookie plus CSRF — the same login as the server-rendered account pages, so there is no second token flow. Errors distinguish the two failure modes that matter:

| Exception | Status | Meaning |
|---|---|---|
| `AIConfigurationError` | 400 | The deployment is misconfigured; retrying will not help |
| `AIProviderError` | 502 | The upstream vendor failed |
| `AIResponseError` | 502 | The model answered unusably |

## 🔄 Migration guide

```bash
# 1. Set a provider credential in .env (see .env.example)
CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat...

# 2. Apply migrations — stored OpenAI credentials are copied automatically
python manage.py migrate

# 3. Populate the model catalogue
python manage.py sync_models

# 4. Build the frontend (the container image does this for you)
cd src/frontend && npm ci && npm run build
```

Nothing else is required. Existing content, threads, assistants and posts are preserved.

### Rollback

```bash
python manage.py migrate parodynews 0001
```

Both migrations reverse, and `0002` restores the OpenAI credentials it moved. This was verified against a database seeded with legacy-shaped rows, forward → reverse → forward.

## ⚠️ Issues found along the way

Recorded because each is a trap that will recur.

**Reversing a `RemoveField` re-adds the column with no default.** If the column was `NOT NULL`, the reverse fails on any populated table — before the restore step that would have repopulated it. The fix is to `AlterField` to a defaulted, blankable column *before* removing it, so the reverse `AddField` succeeds.

**`null=True` → `NOT NULL` fails while NULLs remain.** Postgres refuses `SET NOT NULL` outright; Django will not add a backfill for you. `0003` does it explicitly in a `RunPython` step.

**The ruff configuration was inert.** `select` sat under `[tool.ruff]` instead of `[tool.ruff.lint]`, so the rule set was silently ignored — which explains a standing CI note about roughly 75 unenforced findings. Moving it surfaced 81 in `src/`. All are now fixed and the CI lint step blocks again instead of running with `continue-on-error`.

**Enabling the debug toolbar would have crashed Django.** Three separate blocks in `settings/base.py` each added `debug_toolbar` to `INSTALLED_APPS`, and Django refuses to start on duplicate app labels. Nobody had hit it because the toolbar was never switched on. Consolidated to a single `ENABLE_DEBUG_TOOLBAR` flag.

**The auth pages depended on a CDN.** `base.html` pulled Bootstrap's CSS and JS from jsDelivr, so every login page load depended on that host resolving and its certificate validating. They now reuse the React bundle's stylesheet and load no JavaScript at all.

## ✅ Verification

- 349 Python tests, 25 Vitest tests, all passing
- `ruff`, `black` and `isort` clean across `src/`
- Migrations verified forward → reverse → forward against seeded legacy rows
- Playwright end-to-end run through login, settings, model sync, schema import, assistant creation, content generation, thread run and publishing — zero console errors, checked at desktop and mobile widths

## 🔗 Additional resources

- [AI layer README](../../../src/parodynews/ai/README.md) — the contract, and how to add a provider
- [Frontend README](../../../src/frontend/README.md) — build, dev server, and how Django serves the bundle
- [Migrations README](../../../src/parodynews/migrations/README.md) — reversibility traps in detail
