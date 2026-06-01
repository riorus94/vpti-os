# 05 — Regulation retrieval via pasal-id + status check (the router)

Status: ready-for-agent
Type: AFK
Blocked by: 04

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS MVP. See ADR-0002.

## What to build

The **regulation leg** plus the unifying **Retrieval Layer router**. Regulation sub-queries (pasal text, obligations, HS/commodity rules) route to `pasal-id`; internal sub-queries route to the FAISS leg from slice 04. For regulation grounding, fetch the official text **and** the **Regulation Status** (`get_law_status`) so a `dicabut`/`diubah` regulation is surfaced and never cited as current. Grounding returned by the router is tagged by source (official pasal cite vs internal note id).

Headless degradation: when `pasal-id` is unavailable, regulation grounding is reported as **unavailable** — never silently substituted from FAISS.

## Acceptance criteria

- [ ] Router sends regulation sub-queries to pasal-id and internal sub-queries to FAISS
- [ ] Regulation grounding includes official text and current Regulation Status
- [ ] A revoked/amended (`dicabut`/`diubah`) regulation is flagged in the grounding
- [ ] Grounding is tagged by source so citations can render correctly downstream
- [ ] When pasal-id is unavailable, regulation grounding is reported unavailable (no FAISS substitution)
- [ ] Router behavior is tested with a stubbed pasal-id (incl. a dicabut case and an unavailable case)

## Blocked by

- 04 — Internal retrieval: FAISS + local multilingual embeddings
