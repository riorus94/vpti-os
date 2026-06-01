# 08 — Web Search Strategy (Tavily)

Status: ready-for-agent
Type: AFK
Blocked by: 07

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS MVP. See the Web Search Strategy module.

## What to build

The **Web Search Strategy** module: a pure routing decision over query type → mode ∈ {`internal` (default), `web` (fallback), `hybrid` (strategy)}, integrated with **Tavily** as the search provider. Web search is used only for `strategy`/`opportunity` advisory briefs. The hard guardrail is authoritative: `compliance` / regulation / internal-process queries always resolve to `internal` and never reach Tavily, regardless of any other signal. (Bing Search API is retired and is not used.)

## Acceptance criteria

- [ ] Routing returns internal/web/hybrid per query type
- [ ] `strategy`/`opportunity` briefs can incorporate Tavily web results (hybrid)
- [ ] Compliance / regulation / internal-process queries never trigger a web call (guardrail)
- [ ] Routing logic is pure and unit-tested, including the guardrail and a blocked-query case
- [ ] Web results are clearly distinguished from internal/regulation grounding in the brief

## Blocked by

- 07 — Advisory Brief + Thinking Engine + Finding emission
