# Discrete requests, not conversational memory; access by Telegram-ID allowlist

**Status:** accepted

Each **Query** is a self-contained request with its own confirmed **Context**. The bot holds only short-lived *pending-confirmation* state for the in-flight request; it keeps **no rolling conversational memory**. Access is restricted to a Telegram **user-ID allowlist**, and the asker's identity is stamped onto the Context for audit.

## Why

A future engineer will instinctively "improve" the bot by adding chat memory, because that's what Telegram bots do. We deliberately don't: conversational memory makes it ambiguous which Context produced which output, breaking the per-output audit trail that a compliance tool depends on. Discrete requests keep exactly one confirmed Context per output.

The allowlist is the only responsible default for a tool that surfaces internal VPTI process and market intelligence over a publicly-reachable Telegram handle.

## Consequence / accepted cost

Follow-ups like "what about for buses?" re-infer a fresh Context rather than resolving "it" against the prior turn. This is slightly more friction, accepted in exchange for auditability. Revisit only if the friction proves to outweigh the audit benefit.
