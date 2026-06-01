# 03 — Intent classification + two-shape output routing

Status: ready-for-agent
Type: AFK
Blocked by: 02

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS MVP. See Q2.

## What to build

The **Intent Classifier** and the output-shape router. After a Context is confirmed, classify the Query into one **Intent**: `compliance`, `risk`, `opportunity`, or `strategy`. Route `compliance` to the **Compliance Answer** renderer and `risk`/`opportunity`/`strategy` to the **Advisory Brief** renderer. Renderer bodies remain stubbed in this slice — the point is that intent selects the correct output shape (and, downstream, the retrieval/web mode) end-to-end and visibly in Telegram.

## Acceptance criteria

- [ ] A Query is classified into exactly one of the four Intents
- [ ] `compliance` intent routes to the compact Compliance Answer shape (stub body)
- [ ] `risk`/`opportunity`/`strategy` route to the six-section Advisory Brief shape (stub body)
- [ ] The selected Intent is recorded on the request for logging/audit
- [ ] Classification logic is exercised by tests over representative queries per intent

## Blocked by

- 02 — Context Builder (infer + confirm)
