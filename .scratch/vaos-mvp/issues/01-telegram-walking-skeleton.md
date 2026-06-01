# 01 — Walking skeleton: authorized Telegram round-trip

Status: ready-for-agent
Type: AFK
Blocked by: None — can start immediately

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS MVP. See also ADR-0003, ADR-0005.

## What to build

The end-to-end walking skeleton. An **Authorized User** sends a message to the Telegram bot; the FastAPI backend receives it, runs it through a minimal orchestrator that calls a **stub** `LLMClient` (the modular port from ADR-0007) returning a canned structured reply, and the reply is delivered back in Telegram. A sender whose Telegram user ID is **not** on the allowlist is rejected. Each request is logged. No real reasoning, retrieval, or context inference yet — this slice exists to prove the whole pipe and the seams (Telegram I/O adapter, allowlist auth, orchestrator, `LLMClient` port).

**Decided:** use **long-polling** (`getUpdates`) for the MVP/dev — no public HTTPS endpoint needed, simplest to run locally. Webhook delivery is deferred to production hardening. **Prerequisite (config, not a code gate):** the Telegram bot token and allowlist are supplied via environment/secrets. The Telegram-ID allowlist is the MVP auth posture per ADR-0003.

## Acceptance criteria

- [ ] Inbound messages received via long-polling (`getUpdates`)
- [ ] An allowlisted user's message produces a reply round-trip through the stub orchestrator
- [ ] A non-allowlisted sender receives a rejection and no answer is generated
- [ ] The asker's identity is captured and attached to the in-flight request (audit seam for the Context, per ADR-0003)
- [ ] Each inbound request is logged
- [ ] `LLMClient` is a port with a stub adapter; no real provider wired yet
- [ ] No conversational memory retained beyond the in-flight request

## Blocked by

- None — can start immediately
