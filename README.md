# VAOS — VPTI AI Operating System

An AI operational-intelligence platform that turns VPTI regulation and institutional
knowledge into **grounded, structured, actionable** output. Not a chatbot.

> Policy → Intelligence → Decision → Execution → Improvement

## Documentation

- [CONTEXT.md](CONTEXT.md) — domain glossary (the ubiquitous language)
- [docs/PRD.md](docs/PRD.md) — product spec
- [docs/adr/](docs/adr/) — architectural decisions (start here to understand *why*)
- [.scratch/](.scratch/) — implementation issues (`vaos-mvp/`, `vaos-phase2-execution/`)

## Architecture — hexagonal (ports & adapters)

```
src/vaos/
  domain/      pure types + rules, zero I/O        (Context, Finding, Action, Decision Engine)
  ports/       interfaces the core depends on       (LLMClient, Embedder, WebSearch, ExecutionHook, Store)
  adapters/    concrete implementations of ports    (Azure, multilingual-e5, Tavily, Linear, Postgres, Telegram)
  modules/     deep modules wired from ports        (context_builder, intent_classifier, retrieval/, reasoning/, web_search, execution)
  pipeline/    request orchestration                (orchestrator.py)
  config.py    typed settings (env / .env)
  app.py       FastAPI entry + composition root
tests/         unit / integration / eval + fixtures (mirrors src/)
vault/         internal-knowledge Obsidian vault    (FAISS-indexed; regulation comes from pasal-id)
```

**Why this shape:** the domain layer is pure and unit-testable without a network — which is
how ADR-0001's grounding invariants and the Decision Engine's pure mapping (Q8) get tested
with no mocks. Vendor/LLM messiness is confined to `adapters/`, so the LLM provider is
swappable (ADR-0007) and every external edge is stubbable in tests.

## Tech stack

Python 3.12 · FastAPI · pydantic · pytest · FAISS · sentence-transformers
(multilingual-e5) · Azure OpenAI (default LLM adapter) · pasal-id (regulation) ·
Tavily (web, non-compliance only) · PostgreSQL · Telegram (long-polling).

## Getting started

```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows
pip install -e ".[dev]"     # base + dev — works on py3.12–3.14
cp .env.example .env        # fill in tokens/keys
pytest                      # pure-domain tests run today; rest are skipped stubs
ruff check . && mypy
```

**Heavy ML extras need Python 3.12** (no py3.14 wheels yet for faiss/torch/ragas):

```bash
pip install -e ".[rag]"     # faiss-cpu + sentence-transformers (real retrieval)
pip install -e ".[eval]"    # ragas (AI eval)
```

Implementation is sliced into tracer-bullet issues under `.scratch/`. Start with
`vaos-mvp/01` (the walking skeleton everything hangs off).
