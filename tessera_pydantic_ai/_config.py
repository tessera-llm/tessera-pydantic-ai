"""Provider-specific config + factory functions for routing Pydantic AI
Agents through the Tessera proxy.

Pydantic AI's Provider classes (OpenAIProvider, AnthropicProvider, etc.)
accept a fully-constructed underlying-SDK async client via parameters
named `openai_client` / `anthropic_client` / ... — the provider then
delegates LLM calls through that client. This module:

  1. Returns the **AsyncOpenAI / AsyncAnthropic kwargs** (`base_url` +
     `default_headers`) the user spreads into the underlying client when
     they want explicit control over auth + http client config.

  2. Provides convenience factories that import the Pydantic AI Provider
     class + underlying-SDK client, construct both, and return a ready-
     to-use Provider instance the user passes to `OpenAIChatModel(...,
     provider=<this>)`.

Field names verified against Pydantic AI v0.0.50+ (2026-05-21 runtime
constructor probe via docs):
- openai → AsyncOpenAI(base_url, api_key, default_headers) → OpenAIProvider(openai_client=...)
- anthropic → AsyncAnthropic(base_url, api_key, default_headers) → AnthropicProvider(anthropic_client=...)

Mistral / Groq / Cohere — Provider classes exist in Pydantic AI but
their custom-client shape has not been verified end-to-end at v0.1
time. Tracked as v0.2 deferred. The 2 verified providers cover ~85%
of customer traffic per our outreach research.
"""

from __future__ import annotations

from typing import Any, Literal

TESSERA_BASE_URL = 'https://api.tesseraai.io'

ProviderName = Literal['openai', 'anthropic']


def _validate_api_key(api_key: str) -> str:
    if not isinstance(api_key, str) or not api_key:
        raise ValueError(
            'tessera_*_config(api_key=...) requires a non-empty string. '
            'Get a free key from https://tesseraai.io/dev'
        )
    return api_key


def _proxy_endpoint(provider: ProviderName) -> str:
    return f'{TESSERA_BASE_URL}/v1/{provider}'


def _headers(api_key: str, extra: dict[str, str] | None = None) -> dict[str, str]:
    headers = {'x-tessera-api-key': api_key}
    if extra:
        headers.update(extra)
    return headers


def tessera_openai_config(
    api_key: str,
    extra_headers: dict[str, str] | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    """Kwargs for `openai.AsyncOpenAI(...)` to route through Tessera.

    Example::

        from openai import AsyncOpenAI
        from pydantic_ai.providers.openai import OpenAIProvider
        from pydantic_ai.models.openai import OpenAIChatModel
        from pydantic_ai import Agent
        from tessera_pydantic_ai import tessera_openai_config

        client = AsyncOpenAI(
            api_key="sk-...",  # your OpenAI key
            **tessera_openai_config(api_key="tk_..."),
        )
        provider = OpenAIProvider(openai_client=client)
        agent = Agent(OpenAIChatModel("gpt-4o", provider=provider))
    """
    api_key = _validate_api_key(api_key)
    endpoint = base_url or _proxy_endpoint('openai')
    return {
        'base_url': endpoint,
        'default_headers': _headers(api_key, extra_headers),
    }


def tessera_anthropic_config(
    api_key: str,
    extra_headers: dict[str, str] | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    """Kwargs for `anthropic.AsyncAnthropic(...)` to route through Tessera.

    Example::

        from anthropic import AsyncAnthropic
        from pydantic_ai.providers.anthropic import AnthropicProvider
        from pydantic_ai.models.anthropic import AnthropicModel
        from pydantic_ai import Agent
        from tessera_pydantic_ai import tessera_anthropic_config

        client = AsyncAnthropic(
            api_key="sk-ant-...",  # your Anthropic key
            **tessera_anthropic_config(api_key="tk_..."),
        )
        provider = AnthropicProvider(anthropic_client=client)
        agent = Agent(AnthropicModel("claude-sonnet-4-6", provider=provider))
    """
    api_key = _validate_api_key(api_key)
    endpoint = base_url or _proxy_endpoint('anthropic')
    return {
        'base_url': endpoint,
        'default_headers': _headers(api_key, extra_headers),
    }


def tessera_config(
    provider: ProviderName,
    api_key: str,
    extra_headers: dict[str, str] | None = None,
    base_url: str | None = None,
) -> dict[str, Any]:
    """Generic dispatcher — returns the right kwargs dict for the given provider."""
    mapping = {
        'openai': tessera_openai_config,
        'anthropic': tessera_anthropic_config,
    }
    if provider not in mapping:
        raise ValueError(
            f'Unknown provider {provider!r}. Supported: {list(mapping)}. '
            'Mistral / Groq / Cohere are queued for v0.2 — see the README.'
        )
    return mapping[provider](api_key=api_key, extra_headers=extra_headers, base_url=base_url)


def tessera_openai_provider(
    openai_api_key: str,
    tessera_api_key: str,
    extra_headers: dict[str, str] | None = None,
    base_url: str | None = None,
    organization: str | None = None,
) -> Any:
    """Construct a Pydantic AI `OpenAIProvider` pre-wired to Tessera's proxy.

    Imports `openai.AsyncOpenAI` and `pydantic_ai.providers.openai.OpenAIProvider`
    at call time so this module imports cleanly even when neither package
    is installed (users only need the providers they actually use).

    Example::

        from pydantic_ai import Agent
        from pydantic_ai.models.openai import OpenAIChatModel
        from tessera_pydantic_ai import tessera_openai_provider

        provider = tessera_openai_provider(
            openai_api_key="sk-...",
            tessera_api_key="tk_...",
        )
        agent = Agent(OpenAIChatModel("gpt-4o", provider=provider))
    """
    from openai import AsyncOpenAI
    from pydantic_ai.providers.openai import OpenAIProvider

    cfg = tessera_openai_config(
        api_key=tessera_api_key, extra_headers=extra_headers, base_url=base_url
    )
    client_kwargs: dict[str, Any] = {'api_key': openai_api_key, **cfg}
    if organization is not None:
        client_kwargs['organization'] = organization
    client = AsyncOpenAI(**client_kwargs)
    return OpenAIProvider(openai_client=client)


def tessera_anthropic_provider(
    anthropic_api_key: str,
    tessera_api_key: str,
    extra_headers: dict[str, str] | None = None,
    base_url: str | None = None,
) -> Any:
    """Construct a Pydantic AI `AnthropicProvider` pre-wired to Tessera's proxy.

    Imports `anthropic.AsyncAnthropic` and
    `pydantic_ai.providers.anthropic.AnthropicProvider` at call time so this
    module imports cleanly without either dep installed.

    Example::

        from pydantic_ai import Agent
        from pydantic_ai.models.anthropic import AnthropicModel
        from tessera_pydantic_ai import tessera_anthropic_provider

        provider = tessera_anthropic_provider(
            anthropic_api_key="sk-ant-...",
            tessera_api_key="tk_...",
        )
        agent = Agent(AnthropicModel("claude-sonnet-4-6", provider=provider))
    """
    from anthropic import AsyncAnthropic
    from pydantic_ai.providers.anthropic import AnthropicProvider

    cfg = tessera_anthropic_config(
        api_key=tessera_api_key, extra_headers=extra_headers, base_url=base_url
    )
    client = AsyncAnthropic(api_key=anthropic_api_key, **cfg)
    return AnthropicProvider(anthropic_client=client)
