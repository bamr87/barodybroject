# AI Provider Layer

## Purpose

This package is the only place in the codebase that knows how a specific AI vendor works. Everything else — services, views, management commands — describes *what* it wants and lets the layer pick an implementation. Swapping providers is a configuration change, not a code change.

## Structure

```
ai/
├── base.py           # The contract: AIProvider, GenerationRequest, GenerationResult
├── registry.py       # Resolves the configured provider and its credentials
├── exceptions.py     # AIError hierarchy (configuration vs. upstream vs. response)
├── schema_stub.py    # Builds schema-valid example documents (used by the mock)
├── _async.py         # run_sync(): calls an async provider from sync Django code
└── providers/
    ├── claude_code.py  # DEFAULT — Claude via the Claude Agent SDK
    ├── anthropic.py    # Claude via the Anthropic Messages API
    ├── openai.py       # GPT via chat completions
    └── mock.py         # Deterministic responses for tests
```

## The contract

A caller builds a `GenerationRequest` and gets back a `GenerationResult`:

```python
from parodynews.ai import ChatMessage, GenerationRequest, get_provider

provider = get_provider()            # whatever is configured as default
result = provider.generate(
    GenerationRequest(
        messages=[ChatMessage("user", "Write a headline about a cat mayor.")],
        system="You are a parody news writer.",
        json_schema=schema,          # optional; enables structured output
    )
)
result.text       # the raw text
result.data       # parsed + schema-validated, when json_schema was given
result.usage      # token counts, when the provider reports them
```

`GenerationRequest` is deliberately small. It carries the things every provider can honour, and anything vendor-specific goes in `metadata`, where a provider is free to ignore it.

## Why normalization lives in the base class

`AIProvider.normalize()` folds system turns into the system prompt and guarantees the first *and* last turn are user turns. That last part is not fussiness: current Claude models reject a trailing assistant turn, so when a thread ends with an assistant reply the layer appends a short continuation prompt. Doing this once in the base class means a provider author cannot forget it.

## Structured output

Every provider takes the same `json_schema` and is held to the same standard: parse the response, then validate it with `jsonschema` (Draft 7). How each provider *asks* for JSON differs — the Claude Agent SDK takes an `output_format`, the Anthropic API takes `output_config.format`, OpenAI takes a strict `response_format` — but the validation afterwards is shared, so a provider that returns almost-valid JSON fails loudly instead of quietly corrupting content.

This is also why the `mock` provider builds its canned responses with `schema_stub.build_example()` rather than returning a fixed blob: the test double is held to the same contract as the real thing.

## Credentials

`registry.py` resolves credentials in this order, first hit wins:

1. An enabled `AIProviderConfig` row for that provider (set in the app's settings UI)
2. The provider's environment variables
3. Class defaults

The default provider is resolved the same way: an `AIProviderConfig` flagged `is_default`, then `settings.AI_DEFAULT_PROVIDER`, then `claude_code`.

### The OAuth-token detail worth knowing

Claude accepts two credential shapes and they are *not* interchangeable:

| Prefix | What it is | Variable |
|---|---|---|
| `sk-ant-oat…` | Claude Code OAuth token (`claude setup-token`) | `CLAUDE_CODE_OAUTH_TOKEN` |
| `sk-ant-api…` | Anthropic API key | `ANTHROPIC_API_KEY` |

`ClaudeCodeProvider.credential_env()` picks the right variable by prefix **and blanks the other one**. Without that, a stale `ANTHROPIC_API_KEY` left in a container environment silently wins over the OAuth token you just configured, and the failure looks like a billing problem rather than a configuration one.

## Errors

| Exception | Means | HTTP |
|---|---|---|
| `AIConfigurationError` | An operator has to do something (missing credential, unknown model) | 400 |
| `AIProviderError` | The upstream call failed; `retryable` says whether a retry may help | 502 |
| `AIResponseError` | The model answered, but unusably (refusal, empty, invalid JSON) | 502 |

The split exists so the API can tell a caller "fix your configuration" apart from "the vendor is having a bad day".

## Adding a provider

1. Subclass `AIProvider` in `providers/`, set the class variables (`slug`, `default_model`, `credential_env_vars`, `model_env_var`), and implement `generate()`.
2. Use `self.normalize(request)` for the message history and `self.parse_structured(...)` for schema output — don't hand-roll either.
3. Register the dotted path in `BUILTIN_PROVIDERS` in `registry.py`.
4. Add a test to `tests/test_ai_layer.py`. The suite runs the same expectations against every registered provider, so most of the coverage is free.

## See also

- [`../services/README.md`](../services/README.md) — the callers
- [`../../../docs/changelog/`](../../../docs/changelog/) — the change record for this refactor
