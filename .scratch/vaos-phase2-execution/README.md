# VAOS Phase 2 — Execution

Tracer-bullet slices for the Decision Engine + Execution (Linear) layer. Builds on the MVP (the **Finding** is emitted by `vaos-mvp/07`). Canonical spec: [docs/PRD.md](../../docs/PRD.md). Decisions: [ADR-0008](../../docs/adr/0008-execution-human-approval-gate.md). Glossary: [CONTEXT.md](../../CONTEXT.md).

| # | Slice | Type | Blocked by | Status |
|---|-------|------|-----------|--------|
| 01 | Decision Engine: pure Finding → [Action] | AFK | vaos-mvp/07, vaos-mvp/09 | ready-for-agent |
| 02 | Action lifecycle + Approver approval (stub Linear) | AFK | 01 | ready-for-agent |
| 03 | Execution Hooks: real Linear + assignment + dedup | HITL | 02 | ready-for-human |

## Dependency order

```
vaos-mvp/07 ─┐
             ├─ 01 ── 02 ── 03
vaos-mvp/09 ─┘
```

Linear chain. 01–02 are AFK and can be built once the MVP Finding + persistence exist. 03 is HITL — it's the first external production write (Linear) and needs the org's concrete Action-type → team mapping plus Linear credentials.

## Covered user stories

21, 22, 23 (Decision Engine rules), 24, 25 (Execution/assignment). Dedup encodes ADR-0008 (no original story).

## Out of scope (later)

Tiered auto-filing (relaxing the approve-all-Actions gate), retrieval re-weighting from feedback.
