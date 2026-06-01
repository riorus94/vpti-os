# Phase-2 Execution: human-approval gate on all Actions, designated Approver, auto-dedup

**Status:** accepted (Phase 2 — interface fixed now, implementation deferred)

When the Decision Engine emits an **Action**, it does **not** auto-file a Linear task. The Action lifecycle is:

`proposed → pending-approval → approved | rejected → (if approved) filed to Linear`

- **Human gate on every Action (v1).** Nothing reaches Linear without approval. Relaxing to a tiered model (auto-file low-stakes `opportunity` Actions) is a later, deliberate change once Finding quality is trusted — not a default.
- **Designated Approver role.** Approval authority belongs to an **Approver** — a subset of the Telegram allowlist — not to the asker. The asker is notified of the outcome but cannot self-approve. Approval happens in Telegram, keeping the single-interface story intact. This separates *asking a question* from *dispatching enforcement*.
- **Auto-dedup on a Context-derived key.** Duplicates are prevented by a key built from the **confirmed Context** (Client/Objective/Decision) + Action type + regulation reference — deliberately keyed off the user-confirmed structured Context, not the raw free-text query, to reduce free-text fragility. On a key collision the new occurrence is **attached** to the existing open Action (occurrence count + annotation) and the Approver is still notified — dedup never silently suppresses a signal.
- **Assignment via a configurable table.** Action type → Linear team/project is a config table (`non_compliant → remediation/enforcement`, `risk → risk owner`, `opportunity → strategy`). The mechanism is fixed; the concrete team names are an open question the org must supply before build.

## Why

Everything upstream is informational/advisory and self-correcting (ADR-0001). An Action is the first thing with **external real-world weight** — a `non_compliant` Action names a real case and dispatches work against it. A false-positive Finding auto-filed becomes a real enforcement consequence against a possibly-compliant party. The conservative gate mirrors the care ADR-0001 takes elsewhere, and "collect data first, automate later" mirrors the feedback-loop decision (PRD Q9). Tightening *after* a wrong auto-filed accusation is far more expensive than relaxing a gate later.

## Known limitation

The auto-dedup key can still mis-group two genuinely different cases that share a Context+regulation signature, or fail to group two that should match. This was accepted over the alternative (surface-similars-to-approver) deliberately; the attach-not-suppress rule and the mandatory Approver review are the backstops. Revisit if mis-grouping shows up in practice.
