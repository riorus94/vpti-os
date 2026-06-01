# 07 — Advisory Brief + Thinking Engine + Finding emission

Status: ready-for-agent
Type: AFK
Blocked by: 06

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS MVP. See Q5, Q8.

## What to build

The **Advisory Brief** path for `risk`/`opportunity`/`strategy` intents. Select a **Thinking Model** from a registry whose entries carry "use when" criteria: the LLM picks and justifies a model, the chosen model is named in the output, and a deterministic per-intent default is used on ambiguity/failure. Produce the six-section brief (`Ringkasan Eksekutif, Konteks, Analisis, Risiko, Peluang, Rekomendasi`) and emit a typed **Finding** (`compliance_status`, `risks[]`, `opportunities[]`) for downstream Phase-2 use. A general rule lookup yields `not_applicable`/`unknown`, never `non_compliant`.

## Acceptance criteria

- [ ] Advisory intents produce a six-section brief with localized Indonesian headers
- [ ] A Thinking Model is selected, named in the output, and chosen from the registry
- [ ] Deterministic per-intent default is used when selection is ambiguous or the LLM call fails
- [ ] A typed Finding is emitted alongside the brief
- [ ] Tests pin the registry lookup and default fallback (deterministic); LLM choice behind a stub
- [ ] `compliance` intent still routes to slice 06, not here

## Blocked by

- 06 — Compliance Answer: grounded-or-refuse
