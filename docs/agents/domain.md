# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, or
- **`CONTEXT-MAP.md`** at the repo root if it exists — it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **`docs/adr/`** — read ADRs that touch the area you're about to work in. In multi-context repos, also check `src/<context>/docs/adr/` for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The producer skill (`/grill-with-docs`) creates them lazily when terms or decisions actually get resolved.

## File structure

This is a **single-context** repo:

```
/
├── CONTEXT.md
├── docs/
│   ├── PRD.md
│   └── adr/
│       ├── 0001-compliance-answers-must-be-grounded.md
│       ├── 0002-hybrid-grounding-pasal-id-and-faiss.md
│       └── … (sequential)
└── src/   (to be created)
```

(If the project ever splits into bounded contexts — e.g. separate retrieval vs execution services — introduce a `CONTEXT-MAP.md` at the root pointing to per-context `CONTEXT.md` files.)

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids — e.g. say **Compliance Answer** / **Advisory Brief**, **Grounding**, **Finding**, **Action**, **Context** (the five-field frame), not "report", "source", "result", or "metadata".

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/grill-with-docs`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0001 (compliance answers must be grounded) — but worth reopening because…_
