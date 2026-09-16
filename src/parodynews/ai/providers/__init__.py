"""
Built-in AI providers.

Each module defines exactly one ``AIProvider`` subclass and imports its vendor
SDK lazily inside methods, so an SDK that is not installed only fails when
that provider is actually used.

- ``claude_code``: default. Claude via the Claude Agent SDK, authenticated with
  a Claude Code OAuth token (``CLAUDE_CODE_OAUTH_TOKEN``).
- ``anthropic``: Claude via the Anthropic Messages API (``ANTHROPIC_API_KEY``).
- ``openai``: OpenAI chat completions (``OPENAI_API_KEY``).
- ``mock``: deterministic offline provider for tests and demos.
"""
