# Contributing to tessera-pydantic-ai

Thanks for your interest. The package is Apache-2.0 licensed and PRs are welcome.

For the canonical contributing rules (style, what we want, what we do not want, PR review expectations) see [`tessera-llm/tessera-sdk/CONTRIBUTING.md`](https://github.com/tessera-llm/tessera-sdk/blob/main/CONTRIBUTING.md). This file documents the package-specific bits.

## Reporting bugs

Open an issue at [github.com/tessera-llm/tessera-pydantic-ai/issues](https://github.com/tessera-llm/tessera-pydantic-ai/issues) with:

- Package version (`pip show tessera-pydantic-ai`)
- Pydantic AI version
- Language runtime version
- Minimum reproduction snippet
- Expected vs. actual behaviour

For security vulnerabilities, see [`SECURITY.md`](./SECURITY.md) -- please do not file public issues.

## Development setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

The CI workflow under `.github/workflows/` runs the same checks on every push and pull request -- keep it green.

## Package-specific scope

This package is a thin adapter on top of the Pydantic AI framework. The Tessera wrapper exposes a one-line config helper that routes Pydantic AI's LLM calls through the Tessera proxy at `api.tesseraai.io`. Keep new helpers tiny -- one config-factory per upstream provider, no business logic inside the wrapper.

## Contact

- Bug reports: GitHub Issues.
- Security: [security@tesseraai.io](mailto:security@tesseraai.io).
- Code of Conduct enforcement: [conduct@tesseraai.io](mailto:conduct@tesseraai.io).
- General: [founder@tesseraai.io](mailto:founder@tesseraai.io).