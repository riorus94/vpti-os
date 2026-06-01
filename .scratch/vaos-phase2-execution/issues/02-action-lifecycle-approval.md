# 02 — Action lifecycle + Approver approval flow (Telegram, stub Linear)

Status: ready-for-agent
Type: AFK
Blocked by: 01

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS Phase 2 (Execution). See ADR-0008.

## What to build

The execution walking skeleton — the human-approval gate, with Linear still stubbed. A proposed **Action** enters the lifecycle `proposed → pending-approval → approved | rejected → filed`. When an Action reaches `pending-approval`, the designated **Approver** (a subset of the Telegram allowlist) receives a Telegram prompt to approve or reject. On approval, a **stub** Execution Hook logs "would file to Linear"; on rejection, the Action is closed as rejected. The asker is **notified** of the outcome but cannot self-approve.

This establishes the lifecycle state machine, the Approver role, and the approval UX before any real external write.

## Acceptance criteria

- [ ] Proposed Actions move through proposed → pending-approval and await an Approver
- [ ] Only an Approver (allowlist subset) can approve/reject; the asker cannot self-approve
- [ ] Approval transitions the Action to approved and invokes the (stub) Execution Hook
- [ ] Rejection transitions the Action to rejected; no Hook invoked
- [ ] The asker is notified of the outcome
- [ ] Lifecycle transitions are persisted and tested (incl. the reject path)

## Blocked by

- 01 — Decision Engine: pure Finding → [Action]
