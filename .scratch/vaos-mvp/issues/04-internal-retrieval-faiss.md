# 04 — Internal retrieval: FAISS + local multilingual embeddings

Status: ready-for-agent
Type: AFK
Blocked by: 01

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS MVP. See ADR-0006, ADR-0007.

## What to build

The **internal leg** of the Retrieval Layer. Build a FAISS index over a small, fixed **Vault** fixture (internal VPTI process / system / market-intelligence notes) using the local `multilingual-e5-large` embedding model — no data leaves the machine. Given an internal sub-query, return the top-k notes ranked by relevance, each tagged with its source note id. When nothing clears the relevance threshold, return an **empty** result rather than a low-relevance match.

Keep index build/refresh separate from query-time retrieval. This is the thin-custom path (no LangChain).

## Acceptance criteria

- [ ] FAISS index builds over the Vault fixture using local multilingual-e5 embeddings
- [ ] An internal sub-query with an obvious match returns that note ranked first
- [ ] A sub-query with no relevant match returns an empty result (not a weak match)
- [ ] Results carry source note ids and are tagged as internal-Vault origin
- [ ] Ranking is deterministic for the fixed fixture (golden-set top-k tests)
- [ ] No internal note content is sent to any external service

## Blocked by

- 01 — Walking skeleton: authorized Telegram round-trip
