# 03 — Execution Hooks: real Linear task + assignment + dedup

Status: ready-for-human
Type: HITL
Blocked by: 02

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS Phase 2 (Execution). See ADR-0008. Stories 24, 25.

## What to build

Replace the stub Execution Hook with **real Linear task creation** via the Linear port, plus assignment and deduplication — the slice that actually writes to the external production tool.

- **Filing:** an approved Action creates a Linear task through the Linear adapter.
- **Assignment:** the task lands on the right team/project per a configurable **Action-type → Linear team** table (`non_compliant → remediation/enforcement`, `risk → risk owner`, `opportunity → strategy`).
- **Dedup:** before filing, compute the **Action Dedup Key** (confirmed Context + Action type + regulation reference — not raw query text). If an open Action with the same key exists, **attach** the new occurrence to it (occurrence count + annotation) and notify the Approver, instead of filing a duplicate. Never silently drop.

This slice is HITL: it requires the org to supply the concrete Action-type → team mapping values, Linear workspace credentials, and a review that auto-creating tasks in the real Linear workspace (post-approval) is acceptable.

## Acceptance criteria

- [ ] Decisions/values supplied before build: concrete Action-type → Linear team/project mapping; Linear workspace + credentials
- [ ] An approved, non-duplicate Action creates a Linear task on the mapped team/project
- [ ] A new Action whose Dedup Key matches an open Action is attached to it (occurrence + annotation), not filed twice
- [ ] Dedup attaches/notifies — it never silently suppresses an Action
- [ ] Dedup Key is derived from the confirmed Context + Action type + regulation reference
- [ ] Linear interaction is behind a port; tests use a stubbed Linear client (incl. a dedup-collision case)

## Blocked by

- 02 — Action lifecycle + Approver approval flow
