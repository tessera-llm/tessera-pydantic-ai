# `tessera-pydantic-ai`

**Drop-in cost optimization for [Pydantic AI](https://pydantic.dev/docs/ai/).** Two function calls (one for the underlying SDK client kwargs, one for the Pydantic AI Provider wrapper) and every `agent.run_sync()` / `agent.run()` call lands on the [Tessera](https://tesseraai.io) optimization proxy. Auto-route to cheaper-equivalent models, exact + provider-prompt-cache hits, prompt compression with per-stack quality canary, batch arbitrage on async-tolerant calls. Free Sandbox tier: **60M tokens/month, no card**. Paid tiers: **flat monthly subscription by token volume — keep 100% of savings**.

<!-- COMPANION-PACKAGES-START -->
Companion to [`tessera-sdk`](https://github.com/tessera-llm/tessera-sdk) (vanilla provider SDKs), [`tessera-langchain`](https://github.com/tessera-llm/tessera-langchain) (LangChain integration), [`tessera-vercel-ai`](https://github.com/tessera-llm/tessera-vercel-ai) (Vercel AI SDK integration), [`tessera-llamaindex`](https://github.com/tessera-llm/tessera-llamaindex) (LlamaIndex integration), [`tessera-mastra`](https://www.npmjs.com/package/@tessera-llm/mastra) (Mastra Agent framework integration), [`tessera-crewai`](https://pypi.org/project/tessera-crewai/) (CrewAI multi-agent integration), and [`tessera-autogen`](https://pypi.org/project/tessera-autogen/) (AutoGen 0.4+ multi-agent integration). Same proxy, same mechanic stack, Pydantic AI-shaped API.
<!-- COMPANION-PACKAGES-END -->

[![PyPI version](https://img.shields.io/pypi/v/tessera-pydantic-ai.svg)](https://pypi.org/project/tessera-pydantic-ai/) [![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

---

## What it looks like

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from tessera_pydantic_ai import tessera_openai_provider

provider = tessera_openai_provider(
    openai_api_key="sk-...",        # your OpenAI key
    tessera_api_key="tk_...",      # free from tesseraai.io/dev
)

agent = Agent(OpenAIChatModel("gpt-4o", provider=provider))

result = agent.run_sync("Summarize this customer support ticket in 2 sentences.")
```

One factory call, one Model wrap, one Agent. Your existing Pydantic AI code (tools, structured outputs, run_sync/run, streaming) works unchanged. Anthropic mirror:

```python
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from tessera_pydantic_ai import tessera_anthropic_provider

provider = tessera_anthropic_provider(
    anthropic_api_key="sk-ant-...",
    tessera_api_key="tk_...",
)
agent = Agent(AnthropicModel("claude-sonnet-4-6", provider=provider))
```

Prefer explicit control over the underlying `AsyncOpenAI` / `AsyncAnthropic` client? Use the pass-through config functions:

```python
from openai import AsyncOpenAI
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai import Agent
from tessera_pydantic_ai import tessera_openai_config

client = AsyncOpenAI(
    api_key="sk-...",
    organization="org-mine",
    **tessera_openai_config(api_key="tk_..."),
)
provider = OpenAIProvider(openai_client=client)
agent = Agent(OpenAIChatModel("gpt-4o", provider=provider))
```

---

## Install

```bash
pip install tessera-pydantic-ai pydantic-ai openai anthropic
```

Pydantic AI + the underlying SDK clients (`openai`, `anthropic`) are NOT declared as dependencies of this package. Install whichever providers you actually use. Tessera's factories `import` them lazily at call time so importing this package never blows up over missing optional deps.

Get a free Tessera API key (60M tokens/mo, no card) at **[tesseraai.io/dev](https://tesseraai.io/dev)**. Sign-up takes ~30 seconds and returns an instant `tk_…` key plus magic-link dashboard access.

---

## Provider support

| Provider | Pydantic AI Provider class | Tessera config function | Convenience factory |
|---|---|---|---|
| OpenAI | `OpenAIProvider` | `tessera_openai_config` | `tessera_openai_provider` |
| Anthropic | `AnthropicProvider` | `tessera_anthropic_config` | `tessera_anthropic_provider` |

**v0.1 ships OpenAI + Anthropic.** Mistral / Groq / Cohere are queued for v0.2; the Pydantic AI Provider classes for those have a similar custom-client pattern but the exact signature has not been end-to-end verified. Per our diagnostic-vocab-in-writing discipline (every public-surface claim verified before publish), we'd rather ship 2 honest-and-tested providers than 5 claimed-but-unverified ones. See [`tessera-langchain`](https://github.com/tessera-llm/tessera-langchain), [`tessera-llamaindex`](https://github.com/tessera-llm/tessera-llamaindex), or [`tessera-vercel-ai`](https://github.com/tessera-llm/tessera-vercel-ai) for verified Mistral / Groq / Cohere integrations on those frameworks today.

The generic dispatcher `tessera_config("openai" | "anthropic", api_key="tk_...")` returns the right kwargs dict regardless of provider. Unknown-provider calls raise `ValueError` with a v0.2 pointer.

---

## Worked example

Real customer-support agent on `gpt-4o`, 5B tokens/month, OpenAI list prices:

| Stage | Cost / mo | Saved |
|---|---:|---:|
| Baseline (OpenAI direct via Pydantic AI) | $24,000 | n/a |
| + Tessera (route, cache, prompt-cache headers, compress, M9 ceiling, batch) | $9,400 | $14,600 |
| Tessera subscription (Scale tier, flat) | $3,999 | n/a |
| **You net pay** | **$13,399** | **$10,601 / mo saved** |

**Verify the savings math yourself.** Every billable line traces back to two immutable cost figures pinned to a multi-source pricing catalog snapshot captured at request time. Two engineers, three hours, can re-derive any month from raw inputs. Full procedure at [tesseraai.io/trust](https://tesseraai.io/trust).

Quality canary across the full mechanic stack: mean-score 0.96 (floor 0.95). 0.95 SLA held all 30 days. Full breakdown: [worked example with mechanic-level numbers + canary results](https://tesseraai.io/blog/cut-openai-bill-48-percent-without-quality-regression).

---

## What Tessera does on every Agent call

Same mechanic stack as the main [`tessera-sdk`](https://github.com/tessera-llm/tessera-sdk). Each mechanic is opt-in per workload, observable per request, and bypasses when its quality canary drops below the per-stack 0.95 floor.

| Mechanic | What it does | Typical savings |
|---|---|---|
| **Auto-route** <sub>(m1)</sub> | Route to a cheaper-equivalent model gated by a daily promptfoo canary on your eval set | 15–35% on routed calls |
| **Auto-cache** <sub>(m2)</sub> | sha256 cache on the canonical request body, 7-day TTL, Cloudflare edge KV | 5–40% depending on prompt repetition |
| **Auto-compress** <sub>(m3)</sub> | Per-role heuristic compression (system + user toggles independent). Preserves code fences and JSON shapes. | 5–15% on prompt tokens |
| **Prompt cache** <sub>(m6)</sub> | Inject provider-native cache headers: OpenAI cached-input (50% off), Anthropic `cache_control: ephemeral` (90% off cache reads) | 50–90% on cached prefixes |
| **Context prune** <sub>(m7)</sub> | Conservative trim on long conversations (system + last 8 turns; TF-IDF rerank on RAG attachments) | 5–25% on multi-turn workloads |
| **Output-length ceiling** <sub>(m9)</sub> | Daily compute fits p90 of completion length per workload, injects `maxTokens = p90 × 1.3` | 5–15% on completion cost |
| **Batch arbitrage** <sub>(m10)</sub> | Route async-tolerant Agent calls to provider Batch APIs (OpenAI Batch + Anthropic Message Batches both 50% off) | 50% on batch-eligible traffic |
| **Cross-provider failover** <sub>(m11)</sub> | When primary upstream returns 5xx / connection error / timeout, retry on OpenRouter (opt-in, default OFF) | Reliability primitive, n/a cost |
| **Per-provider circuit breaker** | Rolling 5xx-rate state machine per upstream. When a provider degrades, auto-route skips its intra-provider alternative mappings until the half-open probe succeeds. | n/a (keeps the savings stack honest) |

---

## Pricing

- **Free Sandbox**: 60M tokens/month, 30 requests/minute, observability-only mechanics, no card. Forever.
- **Paid tiers** — flat monthly subscription by token volume: Starter $199 (≤1B), Growth $999 (≤5B), Scale $3,999 (≤20B), Enterprise custom (20B+). You keep 100% of measured savings.

Existing customers of `tessera-sdk`, `tessera-langchain`, `tessera-llamaindex`, `tessera-vercel-ai`, or `tessera-mastra` keep their `rate_locked_pct` (if any) on this package too. Same `tk_…` key, same billing record.

---

## FAQ

### Q: How is this different from the other tessera-* packages?

Same proxy. Same mechanics. Same billing. The six packages target different code surfaces:

- **`tessera-sdk`**: patches OpenAI / Anthropic / etc. client constructors directly via `tessera.activate(key)`. Use when calling provider SDKs without a framework.
- **`tessera-langchain`**: wires into LangChain ChatModel constructors. Use when you're on LangChain.
- **`tessera-llamaindex`**: wires into LlamaIndex `LLM` adapter constructors. Use when you're on LlamaIndex.
- **`tessera-vercel-ai`**: wires into the Vercel AI SDK provider factories. Use when you're on `ai` core + `@ai-sdk/*`.
- **`tessera-mastra`**: Vercel AI SDK shape but Mastra-positioned. Use when you're on Mastra Agents.
- **`tessera-pydantic-ai`** *(this package)*: wires into Pydantic AI Provider classes. Use when you're on Pydantic AI.

Pick whichever fits your codebase. Side-by-side install is supported: all six resolve to the same proxy and same billing record.

### Q: Why only OpenAI and Anthropic in v0.1?

Honesty over feature breadth. The Pydantic AI Provider class for each LLM accepts a custom underlying-SDK client (e.g. `OpenAIProvider(openai_client=...)`); we have end-to-end verified that pattern against the OpenAI and Anthropic SDK client constructors. The Mistral / Groq / Cohere Provider classes exist in Pydantic AI but their custom-client shape has not been tested in our CI. Per our public-surface-claim discipline (every claim verified before ship), the unverified providers stay queued for v0.2. The two shipped providers cover ~85% of customer LLM traffic per our outreach research.

### Q: Does this break my tools / structured outputs / streaming?

No. The Pydantic AI Provider object that wraps the underlying SDK client is unchanged in shape (`agent.run_sync()`, `agent.run()`, tool calls, structured outputs, and streaming all work unchanged). Auto-route gates on tool-calling capability so an agent using tools never gets routed to a non-tool-capable model.

### Q: What happens if Tessera's proxy is down?

Your Agent gets HTTP errors instead of LLM responses. On the proxy side, a per-provider circuit breaker tracks rolling 5xx rates and skips degraded providers in auto-route decisions. Cross-provider failover (m11) is opt-in and re-routes to OpenRouter when the primary upstream is down. See the workload toggle in the dashboard.

### Q: What happens to my OpenAI / Anthropic rate limits?

They pass through. Tessera does not aggregate quotas across customers. Your provider rate limits apply normally; the proxy enforces only the Tessera tier limits (30 rpm Free Sandbox, 60 rpm Production by default; higher on request).

### Q: Are you storing my prompts and completions?

No. We log only token counts, cost deltas, mechanics_stack, and provider response status. Prompts and completions are never persisted. Full data handling on [`tesseraai.io/security`](https://tesseraai.io/security).

### Q: Why are there two API surfaces (`tessera_openai_config` vs `tessera_openai_provider`)?

The config function returns the kwargs dict you spread into `AsyncOpenAI(...)`: explicit, easy to combine with other settings (organization, custom http_client, retry config, etc.). The convenience factory imports `AsyncOpenAI` + `OpenAIProvider` for you and pre-merges. Use whichever you find more readable. Both ship in the same package.

---

## Links

- **Dashboard + free signup:** [tesseraai.io/dev](https://tesseraai.io/dev)
- **How it works (per-mechanic deep dives):** [tesseraai.io/how-it-works](https://tesseraai.io/how-it-works)
- **Security + data handling:** [tesseraai.io/security](https://tesseraai.io/security)
- **Worked-numbers blog post:** [Customer-support workload, 48% saved, quality held](https://tesseraai.io/blog/cut-openai-bill-48-percent-without-quality-regression)
- **Pydantic AI docs:** [pydantic.dev/docs/ai](https://pydantic.dev/docs/ai/)

---

## About Tessera

Tessera is the **substrate layer** for **LLM cost optimization**, also called the **Optimize Layer** in our product surface. A thin proxy that sits in your application's **request-path**, applies a conservative cascade of optimization mechanics, and measures every saved dollar against an **audit-immutable** baseline. We charge a **flat monthly subscription by token volume**; you keep **100% of measured savings**. No per-token gateway fee; the category we operate in is "**LLM cost optimizer**," distinct from per-token **AI gateways** and observability dashboards.

Where observability tools tell you what you spent and AI gateways re-shape the request without measuring the cost delta, Tessera is the layer that does both, and shows you every measured saved dollar. The **verified-savings ledger** at [`ledger.tesseraai.io`](https://ledger.tesseraai.io) shows every original-vs-actual cost pair, snapshot-pinned to a `pricing_catalog` version captured at request time. Mid-contract price changes don't retroactively alter past savings. This is the **FinOps**-friendly model for AI inference: every line of the bill traces to a code-enforced rule.

Apache-2.0. Operated by Fintechagency OÜ (Tallinn, Estonia, registry code 16638667). Issues: [github.com/tessera-llm/tessera-pydantic-ai/issues](https://github.com/tessera-llm/tessera-pydantic-ai/issues).

- Developer entry: [tesseraai.io/dev](https://tesseraai.io/dev)
- Mechanic reference: [tesseraai.io/how-it-works](https://tesseraai.io/how-it-works)
- Dashboard: [ledger.tesseraai.io](https://ledger.tesseraai.io)
- Engineering blog: [tesseraai.io/blog](https://tesseraai.io/blog)
