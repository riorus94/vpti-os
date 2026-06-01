# 01 — Decision Engine: pure Finding → [Action]

Status: ready-for-agent
Type: AFK
Blocked by: vaos-mvp/07, vaos-mvp/09

## Parent

[docs/PRD.md](../../../docs/PRD.md) — VAOS Phase 2 (Execution). See Q8, ADR-0008.

## What to build

The **Decision Engine** — a pure function `Finding → [Action]`, the highest-value module in the system. It reads the typed flags on a **Finding** (emitted by the Advisory Brief path, vaos-mvp/07) and maps them to **Actions**:

- `compliance_status == non_compliant` → remediation task Action
- each `risk` → flag + task Action
- each `opportunity` → strategy-assignment Action
- `compliant` / `not_applicable` / `unknown`, no risks, no opportunities → **no Action**

It never interprets prose — only flags. Wire it so the Actions it produces are **persisted/logged** to the durable store (vaos-mvp/09), not yet filed to Linear. End-to-end demoable: a strategy/compliance query produces a Finding, which produces logged Actions (or none, for a routine lookup).

## Acceptance criteria

- [ ] Pure function with no I/O; identical Finding always yields identical Actions
- [ ] Each rule branch covered: non_compliant → remediation; each risk → flag+task; each opportunity → strategy
- [ ] A compliant / not_applicable / unknown Finding with no risks/opportunities produces zero Actions
- [ ] A combined Finding (e.g. non_compliant AND a risk) produces all applicable Actions
- [ ] Produced Actions are persisted to the durable store with their source Finding
- [ ] Table-driven tests over (Finding → expected Actions), including the no-Action case

## Blocked by

- vaos-mvp/07 — Advisory Brief + Thinking Engine + Finding emission
- vaos-mvp/09 — Durable logging + Knowledge-Gap capture
