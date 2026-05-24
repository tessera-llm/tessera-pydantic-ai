"""E2E shape compatibility tests against the real Pydantic AI provider
classes + underlying SDK clients. Gated by `pydantic-ai`, `openai`, and
`anthropic` being installed in the test env.

The minimal contract verified: each convenience factory's return value
is the exact shape `pydantic_ai.models.{openai,anthropic}.<Model>(...,
provider=<this>)` accepts without raising. We probe the constructor
chain end-to-end rather than introspecting attributes — Pydantic AI
wraps inputs through pydantic field renaming + internal storage that
varies across versions; constructor-survives is the strongest portable
check.

These tests are SKIPPED when the upstream deps aren't installed so the
unit-test-only suite still passes for downstream users who never install
Pydantic AI itself.

Locked 2026-05-21 — same pattern as tessera-llamaindex/tests/test_e2e.py
+ tessera-langchain/python/tests/test_e2e.py per the multi-framework
distribution playbook (2026-05-19).
"""

from __future__ import annotations

import importlib

import pytest

from tessera_pydantic_ai import (
    tessera_anthropic_provider,
    tessera_openai_provider,
)


def _has(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False


@pytest.mark.skipif(
    not (_has('pydantic_ai') and _has('openai')),
    reason='pydantic-ai or openai not installed',
)
def test_openai_factory_returns_provider_that_constructs_chat_model():
    from pydantic_ai.models.openai import OpenAIChatModel

    provider = tessera_openai_provider(
        openai_api_key='sk-fake',
        tessera_api_key='tk_test',
    )
    # Constructor must accept the provider object directly. Should not raise.
    OpenAIChatModel('gpt-4o', provider=provider)


@pytest.mark.skipif(
    not (_has('pydantic_ai') and _has('anthropic')),
    reason='pydantic-ai or anthropic not installed',
)
def test_anthropic_factory_returns_provider_that_constructs_chat_model():
    from pydantic_ai.models.anthropic import AnthropicModel

    provider = tessera_anthropic_provider(
        anthropic_api_key='sk-ant-fake',
        tessera_api_key='tk_test',
    )
    AnthropicModel('claude-sonnet-4-6', provider=provider)


@pytest.mark.skipif(
    not (_has('pydantic_ai') and _has('openai')),
    reason='pydantic-ai or openai not installed',
)
def test_openai_provider_has_proxy_url_baked_into_client():
    # Defensive sanity: the provider's underlying client must point at
    # api.tesseraai.io/v1/openai, not the default OpenAI endpoint. Probe
    # via the Pydantic AI base attribute surface (`base_url` + `client`).
    # Both are public attributes documented on the Provider abstract base
    # class (pydantic_ai.providers.Provider).
    provider = tessera_openai_provider(
        openai_api_key='sk-fake',
        tessera_api_key='tk_test',
    )
    assert 'tesseraai.io' in str(provider.base_url)
    assert 'tesseraai.io' in str(provider.client.base_url)


@pytest.mark.skipif(
    not (_has('pydantic_ai') and _has('anthropic')),
    reason='pydantic-ai or anthropic not installed',
)
def test_anthropic_provider_has_proxy_url_baked_into_client():
    provider = tessera_anthropic_provider(
        anthropic_api_key='sk-ant-fake',
        tessera_api_key='tk_test',
    )
    assert 'tesseraai.io' in str(provider.base_url)
    assert 'tesseraai.io' in str(provider.client.base_url)
