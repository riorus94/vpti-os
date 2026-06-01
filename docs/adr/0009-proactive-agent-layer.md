# Proactive agent layer — scheduled runners over the existing ports

**Status:** accepted

Beyond the reactive request pipeline (Telegram → orchestrator), VAOS gains an **agent layer**:
named, goal-driven runners that execute on a schedule or trigger and act **proactively** —
not waiting for a user question. They live in `src/vaos/agents/` and **reuse the existing
domain + ports** (Retrieval, Reasoning, Decision Engine, Store, Execution, WebSearch); they
add no new external concepts, only new *initiators*.

First three:

- **Regulation-Watch** — checks the `Regulation Status` of cited regulations; surfaces any now
  `dicabut`/`diubah` and the stale answers/Vault notes they affect. Extends ADR-0002 from
  per-query to continuous.
- **Knowledge-Gap Resolver** — consumes the Knowledge-Gap backlog (refusals, vaos-mvp/09) and
  produces a "what the Vault is missing" worklist for the owner. Closes the feedback loop.
- **Market-Intel** — scheduled WebSearch (Tavily) sweep feeding opportunity briefs.

## Why

The durable edge over a generic search tool is *acting on change you didn't ask about* —
catching a revoked regulation before it bites, or a knowledge gap before it recurs. The
reactive pipeline can't do that; an agent layer can.

## Design rules

- Each agent's **core logic is a pure/deep function with injected ports** (e.g. a status-checker,
  the Store, a WebSearch) so it is unit-testable with fakes — no scheduler, no network in tests.
- The **scheduler/trigger is an adapter concern** (cron/worker), kept out of the agent's logic.
- Agents that produce work do so as **Actions through the Decision Engine + approval gate**
  (ADR-0008) — proactivity does **not** bypass human approval.
- Agents that touch compliance obey grounded-or-refuse (ADR-0001): a Regulation-Watch alert
  names its source; it never asserts an ungrounded claim.
