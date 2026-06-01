# 02 — Context Builder (infer + confirm)

Status: ready-for-agent
Type: AFK
Blocked by: 01

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS MVP. See Q1 and the Context invariant.

## What to build

The **Context Builder**. When an Authorized User sends a Query, the system infers an **Inferred Context** — the five fields `Client`, `Objective`, `Audience`, `Decision Required`, `Constraints` — from the Query, presents a one-line summary in Telegram, and waits for the user to confirm or correct. On confirmation the request proceeds (to the stub reasoning from slice 01) carrying a validated **Context** with the asker's identity stamped on it. The system never proceeds without a confirmed Context, satisfying the invariant by infer-plus-confirm rather than interrogation.

Split the module at the testable seam: **inference** is behind the `LLMClient` port (stubbable); **validation** (all five fields present after confirmation; empty/whitespace treated as missing) is pure and deterministic.

## Acceptance criteria

- [ ] A Query yields an Inferred Context summarized back to the user in one line
- [ ] User can confirm (proceed) or correct (re-infer/adjust, then proceed)
- [ ] A confirmed Context carries all five fields plus the asker identity
- [ ] Validation rejects a Context missing any field, naming the missing field; empty/whitespace counts as missing
- [ ] The pipeline does not proceed to reasoning without a confirmed Context
- [ ] Pure-validation unit tests cover each missing-field case (no mocks)

## Blocked by

- 01 — Walking skeleton: authorized Telegram round-trip
