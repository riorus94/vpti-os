# Testing convention

Red-green-refactor, behavior over implementation. A good test asserts what a
module's interface *does*, not how it does it.

## What gets a test file

- **Every module with logic** gets a unit test mirror under `tests/unit/` (or
  `tests/integration/` when it composes ports): `domain/*`, all `modules/*`,
  `pipeline/*`. These are the red-green targets.
- **Thin I/O adapters** (`adapters/llm/azure_openai`, `adapters/search/tavily`,
  `adapters/execution/linear`, `adapters/store/postgres`, `adapters/telegram/bot`)
  do **not** get 1:1 unit files. A unit test of an adapter only asserts "it calls
  the SDK I told it to" — testing mocks, not behavior. They are covered by
  integration/contract tests instead.

This is a deliberate deviation from strict 1:1 mirroring (decided in the grilling
session): honest coverage over symmetric coverage.

## Layers

- `tests/unit/` — pure, fast, no network. Stub the ports (`StubLLM`, in-memory
  Store). The domain layer (`decision_engine`, `Context` validation, output types)
  is testable here with **no mocks at all**.
- `tests/integration/` — wire real modules with stubbed external edges (e.g. the
  retrieval router against a fixture vault + stubbed pasal-id).
- `tests/eval/` — Ragas groundedness/relevance/correctness against a golden set.
  May be slow/costed; keep separate from the fast suite.

## Fixtures

`tests/fixtures/vault/` holds a tiny fixed corpus so FAISS retrieval tests are
deterministic. Never point retrieval tests at the live `vault/`.
