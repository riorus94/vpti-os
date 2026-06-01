# 09 — Durable logging + Knowledge-Gap / feedback capture

Status: ready-for-agent
Type: AFK
Blocked by: 01

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS MVP. See Q9.

## What to build

The durable persistence and self-improvement-signal capture (the MVP portion of the Feedback Loop). Persist every Query, confirmed Context, Finding, and output to PostgreSQL, along with structured **Knowledge-Gap** and stale-regulation events emitted by the compliance path (slice 06). Provide a way to query the Knowledge-Gap backlog so the Vault owner can see what to add. Collect feedback signals for future learning, but do **not** act on them — no retrieval re-weighting yet (that is Phase 2).

## Acceptance criteria

- [ ] Queries, confirmed Contexts, Findings, and outputs are persisted to PostgreSQL
- [ ] Knowledge-Gap and stale-regulation events are stored as structured records
- [ ] The Knowledge-Gap backlog is queryable (what regulation/process is missing)
- [ ] Feedback signals are captured but no retrieval re-weighting occurs
- [ ] Persisted records preserve the asker identity for audit (ADR-0003)

## Blocked by

- 01 — Walking skeleton: authorized Telegram round-trip
