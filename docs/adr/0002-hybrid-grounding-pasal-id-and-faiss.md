# Regulation grounding via pasal-id; internal knowledge via FAISS/Obsidian

**Status:** accepted (supersedes the PRD's "FAISS over Obsidian for everything" assumption)

The Retrieval Layer is a **router**, not a single index:

- **Regulation** sub-queries (pasal text, obligations, HS/commodity rules, amendment status) → the **`pasal-id`** service. Compliance assertions about an obligation must check `get_law_status` so a *dicabut/diubah* (revoked/amended) regulation is never cited as current.
- **Internal** sub-queries (VPTI process, OSS/INATRADE, market intelligence) → the **FAISS** index built over the Obsidian vault.

## Why

The grounding promise (ADR-0001) is only as good as the freshness of the source. A self-maintained FAISS corpus has no inherent amendment-status signal, so it can serve a confidently-wrong, since-revoked regulation. `pasal-id` carries official text and live status, directly closing that gap. But `pasal-id` knows nothing of internal process or market intelligence — those stay in the vault.

## Consequences

- A compliance refusal (ADR-0001) now has a second trigger: *regulation found but status = revoked/amended* → refuse-or-warn with the superseding reference.
- `pasal-id` is an interactively-authed MCP and "may be absent in headless/cron runs." Scheduled/headless flows must degrade gracefully (treat regulation grounding as unavailable → refuse compliance, rather than silently falling back to FAISS regulation notes).
- The Retrieval Layer's interface must distinguish *which source* grounding came from, so citations render correctly (official pasal cite vs. internal note id).
