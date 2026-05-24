# Changelog — tessera-pydantic-ai

All notable changes to this package are documented here. Versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html). Wire format
compatibility across minor versions (0.X.Y) — breaking changes only on
major bumps.

## [0.1.0] — 2026-05-21 — first public release

- 2 verified provider config functions (`tessera_openai_config`,
  `tessera_anthropic_config`) returning the kwargs dict accepted by
  `openai.AsyncOpenAI` and `anthropic.AsyncAnthropic` respectively (`base_url`
  + `default_headers` with `x-tessera-api-key`).
- 2 convenience factories (`tessera_openai_provider`, `tessera_anthropic_provider`)
  returning a constructed `pydantic_ai.providers.{OpenAIProvider,AnthropicProvider}`
  pre-wired to Tessera's substrate proxy. Pass directly to
  `OpenAIChatModel(...)` / `AnthropicModel(...)`.
- Generic dispatcher `tessera_config(provider, api_key=...)` for the 2
  verified providers; unknown-provider calls raise `ValueError` with a v0.2
  backlog pointer.
- E2E gate covers constructor-survives + base_url-baked-in for both
  providers. Pydantic AI's Provider abstract base exposes `client` +
  `base_url` as public attributes — gate keys on the documented surface.
- Apache-2.0. Pydantic AI + the underlying-SDK clients (`openai`, `anthropic`)
  are NOT declared as dependencies — install whichever providers you use.
- Mistral / Groq / Cohere queued for v0.2 once their custom-client patterns
  are end-to-end verified in CI. Diagnostic-vocab-in-writing discipline
  blocks shipping unverified provider claims.
