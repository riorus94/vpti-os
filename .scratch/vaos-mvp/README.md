# VAOS MVP — issue breakdown

Tracer-bullet vertical slices for the VAOS MVP. Canonical spec: [docs/PRD.md](../../docs/PRD.md). Decisions: [docs/adr/](../../docs/adr/). Glossary: [CONTEXT.md](../../CONTEXT.md).

| # | Slice | Type | Blocked by | Status |
|---|-------|------|-----------|--------|
| 01 | Walking skeleton: authorized Telegram round-trip (long-polling) | AFK | — | ready-for-agent |
| 02 | Context Builder (infer + confirm) | AFK | 01 | ready-for-agent |
| 03 | Intent classification + two-shape routing | AFK | 02 | ready-for-agent |
| 04 | Internal retrieval: FAISS + local embeddings | AFK | 01 | ready-for-agent |
| 05 | Regulation retrieval via pasal-id + status (router) | AFK | 04 | ready-for-agent |
| 06 | Compliance Answer: grounded-or-refuse | AFK | 03, 05 | ready-for-agent |
| 07 | Advisory Brief + Thinking Engine + Finding | AFK | 06 | ready-for-agent |
| 08 | Web Search Strategy (Tavily) | AFK | 07 | ready-for-agent |
| 09 | Durable logging + Knowledge-Gap capture | AFK | 01 | ready-for-agent |

## Dependency order

```
01 ──┬─ 02 ── 03 ──────────────┐
     │                          ├─ 06 ── 07 ── 08
     ├─ 04 ── 05 ───────────────┘
     └─ 09
```

01 unblocks everything. 02→03 and 04→05 can proceed in parallel; both feed 06 (the core grounded-or-refuse path). 07→08 extend the advisory side. 09 (persistence) only needs 01. All slices are AFK (long-polling pre-decided in 01); the only prerequisites are config/secrets (bot token, allowlist, Azure keys).

## Out of scope (Phase 2)

Decision Engine, Execution/Linear, retrieval re-weighting (stories 21–25). Outcome stories 29–31 are emergent.
