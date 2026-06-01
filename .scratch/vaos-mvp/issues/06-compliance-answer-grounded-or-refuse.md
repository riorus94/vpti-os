# 06 — Compliance Answer: grounded-or-refuse

Status: ready-for-agent
Type: AFK
Blocked by: 03, 05

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS MVP. The core value. See ADR-0001, ADR-0002, ADR-0004.

## What to build

The real **Compliance Answer** path. For `compliance` intent, wire the Azure OpenAI adapter (behind the `LLMClient` port) to synthesize a compact, grounded answer from the router's grounding, citing official pasal text **verbatim in Bahasa Indonesia** (never machine-translated). No thinking model is used for compliance.

Enforce **grounded-or-refuse**: if grounding is empty, or the relevant regulation is `dicabut`/`diubah`, the system does **not** answer from model memory — it refuses, escalates, and logs a **Knowledge Gap** (or stale-regulation) signal. This is the behavior that makes the product trustworthy; it is a first-class tested path, not an edge case.

## Acceptance criteria

- [ ] A `compliance` query with grounding returns a compact answer citing pasal text verbatim in Indonesian
- [ ] Empty grounding → refusal + escalation message, no parametric-memory answer
- [ ] Revoked/amended regulation → refusal-or-warning naming the superseding reference, never asserted as current
- [ ] Every refusal logs a structured Knowledge-Gap / stale-regulation signal
- [ ] No thinking model is invoked for compliance intent
- [ ] Tests cover: grounded answer, empty-grounding refusal, dicabut refusal (LLM behind a stub)

## Blocked by

- 03 — Intent classification + two-shape output routing
- 05 — Regulation retrieval via pasal-id + status check
