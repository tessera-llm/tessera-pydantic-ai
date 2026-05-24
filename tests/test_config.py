"""Unit tests for config-shape correctness. No third-party deps required."""

from __future__ import annotations

import pytest

from tessera_pydantic_ai import (
    TESSERA_BASE_URL,
    tessera_anthropic_config,
    tessera_config,
    tessera_openai_config,
)


def test_openai_config_returns_base_url_and_headers():
    cfg = tessera_openai_config(api_key='tk_test')
    assert cfg['base_url'] == f'{TESSERA_BASE_URL}/v1/openai'
    assert cfg['default_headers'] == {'x-tessera-api-key': 'tk_test'}


def test_openai_config_merges_extra_headers():
    cfg = tessera_openai_config(
        api_key='tk_test',
        extra_headers={'x-trace-id': 'abc'},
    )
    assert cfg['default_headers'] == {
        'x-trace-id': 'abc',
        'x-tessera-api-key': 'tk_test',
    }


def test_openai_config_accepts_custom_base_url():
    cfg = tessera_openai_config(
        api_key='tk_test',
        base_url='https://staging.tesseraai.io/v1/openai',
    )
    assert cfg['base_url'] == 'https://staging.tesseraai.io/v1/openai'


def test_openai_config_rejects_empty_api_key():
    with pytest.raises(ValueError, match='non-empty'):
        tessera_openai_config(api_key='')


def test_anthropic_config_returns_base_url_and_headers():
    cfg = tessera_anthropic_config(api_key='tk_test')
    assert cfg['base_url'] == f'{TESSERA_BASE_URL}/v1/anthropic'
    assert cfg['default_headers'] == {'x-tessera-api-key': 'tk_test'}


def test_anthropic_config_rejects_empty_api_key():
    with pytest.raises(ValueError, match='non-empty'):
        tessera_anthropic_config(api_key='')


class TestGenericDispatcher:
    def test_routes_openai(self):
        cfg = tessera_config('openai', api_key='tk_test')
        assert cfg['base_url'] == f'{TESSERA_BASE_URL}/v1/openai'

    def test_routes_anthropic(self):
        cfg = tessera_config('anthropic', api_key='tk_test')
        assert cfg['base_url'] == f'{TESSERA_BASE_URL}/v1/anthropic'

    def test_rejects_unknown_provider(self):
        with pytest.raises(ValueError, match='Unknown provider'):
            tessera_config('unknown', api_key='tk_test')  # type: ignore[arg-type]

    def test_rejects_unverified_provider_with_v02_pointer(self):
        # The error message must guide users toward the v0.2 backlog for
        # the providers we explicitly didn't ship yet — silent rejection
        # would create false-discovery friction.
        with pytest.raises(ValueError, match=r'v0\.2'):
            tessera_config('mistral', api_key='tk_test')  # type: ignore[arg-type]
