# ruff: noqa: RUF002
# (U+00D7 MULTIPLICATION SIGN in docstrings is intentional branding glyph, not letter x.)
"""Tessera × Pydantic AI integration — drop-in cost optimization for any
Pydantic AI Agent.

Usage (most common):

    from pydantic_ai import Agent
    from pydantic_ai.models.openai import OpenAIChatModel
    from tessera_pydantic_ai import tessera_openai_provider

    provider = tessera_openai_provider(
        openai_api_key="sk-...",
        tessera_api_key="tk_...",
    )
    agent = Agent(OpenAIChatModel("gpt-4o", provider=provider))

    # Existing Pydantic AI code runs unchanged — agent.run_sync,
    # agent.run, tool calls, structured outputs all route through
    # Tessera proxy.

See https://tesseraai.io/dev for the dashboard, free tier, and full
mechanic documentation.
"""

from tessera_pydantic_ai._config import (
    TESSERA_BASE_URL,
    tessera_anthropic_config,
    tessera_anthropic_provider,
    tessera_config,
    tessera_openai_config,
    tessera_openai_provider,
)
from tessera_pydantic_ai._version import __version__

__all__ = [
    'TESSERA_BASE_URL',
    '__version__',
    'tessera_anthropic_config',
    'tessera_anthropic_provider',
    'tessera_config',
    'tessera_openai_config',
    'tessera_openai_provider',
]
