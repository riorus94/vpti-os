# PRD: VPTI AI Operating System (VAOS) — MVP

> Status: `ready-for-agent`
> Source: Handoff Document v1.0 ("VPTI AI Operating System")
> Open-source working name: `policy-ai-engine`
> Scope: **MVP-first** — RAG + Telegram + Context Builder + Thinking Engine. Decision Engine and Execution layers are specified but staged for Phase 2.
> Glossary: [CONTEXT.md](../CONTEXT.md). Architectural decisions: [docs/adr/](adr/).

## Decisions (grilling session, 2026-06-02)

Nine load-bearing decisions were resolved with the author. These supersede the original draft below where they conflict:

1. **Context = infer + confirm**, not interrogate. The bot infers the five-field Context from the query and shows a one-line summary to confirm/correct. The invariant ("never output without Context") stays literally true; UX stays usable.
2. **Two output shapes by intent.** `compliance` → a compact, grounded, cited **Compliance Answer**; `risk`/`opportunity`/`strategy` → the full six-section **Advisory Brief**. The 6-section template is the *Advisory* contract, not universal.
3. **Grounded-or-refuse for compliance** ([ADR-0001](adr/0001-compliance-answers-must-be-grounded.md)). Empty retrieval on a compliance query → refuse + escalate + log a Knowledge Gap. Never answer compliance from parametric memory.
4. **Hybrid grounding** ([ADR-0002](adr/0002-hybrid-grounding-pasal-id-and-faiss.md)). Regulation text + amendment status from `pasal-id`; internal process/system/market knowledge from FAISS/Obsidian. The Retrieval Layer is a router.
5. **Thinking model: compliance exempt; hybrid selection.** Advisory Briefs only require a thinking model; the LLM picks from a registry (with "use when" criteria) and names its choice, with a deterministic per-intent default fallback.
6. **Telegram-ID allowlist + discrete requests** ([ADR-0003](adr/0003-discrete-requests-no-conversational-memory.md)). Authorized users only; identity stamped on each Context; no conversational memory — each Query is self-contained with only short-lived pending-confirmation state.
7. **Indonesian-first; cite pasal verbatim** ([ADR-0004](adr/0004-indonesian-first-cite-pasal-verbatim.md)). Operate in Bahasa Indonesia, localized template headers, multilingual FAISS embeddings, official regulation text never machine-translated.
8. **Decision Engine = pure `Finding → [Action]`.** The Reasoning layer emits a typed Finding (`compliance_status`, `risks`, `opportunities`); the Decision Engine maps flags to Actions. A routine compliance *lookup* never creates a task — only a flagged *case* does.
9. **MVP feedback = logging + Knowledge-Gap capture.** Persist queries/contexts/findings/outputs and gap/stale-reg events; collect signals for later learning, but no thumbs-up/down or retrieval re-weighting yet.

---

## Problem Statement

VPTI (Verifikasi atau Penelusuran Teknis Impor) work depends on a large, fragmented body of regulation (WTO, UU, PP, Permendag), pasal-level rules, import-process knowledge, and system documentation (OSS, INATRADE). Today this knowledge lives in documents and people's heads. When an analyst or executive needs an answer, they must:

- Manually locate the relevant regulation and interpret it,
- Reason about compliance, risk, and opportunity without a consistent method, and
- Translate any conclusion into action by hand.

This is slow, inconsistent, and error-prone. Inconsistent interpretation creates compliance exposure and contributes to revenue leakage (PNBP). Generic chatbots make this worse: they answer from an opaque prior, with no grounding in the actual regulation and no enforced reasoning, so their output cannot be trusted for compliance decisions.

The user needs a system that turns regulation and institutional knowledge into **grounded, structured, actionable** output — not a chatbot that emits plausible text.

## Solution

The VPTI AI Operating System (VAOS) is an operational intelligence platform that runs every request through a fixed pipeline:

> **Policy → Intelligence → Decision → Execution → Improvement**

A user sends a query (via Telegram in the MVP). The system classifies intent, retrieves the relevant grounding notes from the knowledge base, forces a structured thinking pass, and returns a structured brief (Executive Summary, Context, Analysis, Risk, Opportunity, Recommendation). In later phases a rule-based Decision Engine converts insights into tasks and an Execution layer pushes those tasks to Linear. Every interaction is logged and fed back to improve retrieval over time.

The core, non-negotiable behavior: **the system never produces output without (a) a complete context block and (b) a selected thinking model.** Compliance and regulation answers are always grounded in the internal knowledge base, never in a web search.

From the user's perspective:
- Ask a question in Telegram, get back a consistent, structured, regulation-grounded brief.
- Trust that compliance answers come from the actual regulation, not the model's guess.
- (Phase 2) See actionable items automatically created and assigned in Linear.

## User Stories

### Interface & Request Handling
1. As a VPTI analyst, I want to send a question to a Telegram bot, so that I can get answers in the tool I already use without opening a new app.
2. As a VPTI analyst, I want the bot to acknowledge my message and show it is working, so that I know my request was received.
3. As a VPTI analyst, I want to receive the structured response back in Telegram, so that I can read and act on it in one place.
4. As a VPTI analyst, I want the system to classify the intent of my query (compliance / risk / opportunity / strategy), so that it applies the right reasoning path.
5. As a VPTI analyst, I want a clear error message when my request cannot be completed, so that I am not left guessing whether it failed.

### Context Builder (mandatory)
6. As a compliance lead, I want every request to carry an explicit context block (Client, Objective, Audience, Decision Required, Constraints), so that outputs are scoped to a real decision rather than generic.
7. As a compliance lead, I want the system to refuse to generate output when context is incomplete, so that no ungrounded or unscoped answer is ever produced.
8. As a VPTI analyst, I want the system to prompt me for missing context fields, so that I can complete the request quickly instead of guessing the format.
9. As an auditor, I want the context block stored with each output, so that I can later verify what decision the output was meant to support.

### Retrieval (RAG)
10. As a VPTI analyst, I want the system to retrieve the most relevant regulation and process notes for my query, so that the answer is grounded in actual source material.
11. As a compliance lead, I want retrieved notes to be cited/identifiable in the output, so that I can trace a recommendation back to its pasal-level source.
12. As a knowledge owner, I want the knowledge base organized by the standard folder taxonomy (Policy, Regulation, Standards, Process, System, Data, VPTI Operation, Market Intelligence, AI Insights, Execution), so that retrieval and maintenance are predictable.
13. As a VPTI analyst, I want retrieval to return nothing rather than something irrelevant when the knowledge base has no match, so that the system does not fabricate grounding.

### Thinking Engine
14. As a VPTI analyst, I want the system to select an appropriate thinking model (First Principles, Systems Thinking, Pre-mortem, Five Whys, Second-order Thinking), so that my problem is analyzed with a deliberate method.
15. As an executive, I want every answer to follow the same structured output format (Executive Summary, Context, Analysis, Risk, Opportunity, Recommendation), so that I can scan any brief quickly and consistently.
16. As a VPTI analyst, I want the system to follow the standard thinking flow (identify context → select model → frame problem → analyze → generate structured output), so that reasoning is transparent and repeatable.
17. As a compliance lead, I want the system to never emit output without a selected thinking model, so that no answer skips structured reasoning.

### Web Search Strategy
18. As a strategy analyst, I want the system to use web search for latest updates, market trends, and external benchmarking, so that strategic answers reflect current information.
19. As a compliance lead, I want the system to never use web search for compliance decisions, regulation interpretation, or internal process, so that those answers stay grounded in authoritative internal sources.
20. As a strategy analyst, I want hybrid mode (internal + web) for strategy queries, so that I get both grounded knowledge and current context.

### Decision Engine (Phase 2)
21. As a compliance lead, I want a non-compliant finding to automatically generate a task, so that violations are never silently dropped.
22. As a risk owner, I want a detected risk to be flagged and turned into a task, so that risks are tracked and owned.
23. As a strategy lead, I want an identified opportunity routed to the strategy function, so that upside is captured.

### Execution (Phase 2)
24. As a team lead, I want insights converted into Linear tasks, so that follow-up work enters our existing workflow.
25. As a team lead, I want tasks auto-assigned to the right team, so that ownership is clear from creation.

### Feedback & Self-Improvement
26. As a knowledge owner, I want every query and output logged, so that we have an audit trail and material to learn from.
27. As a VPTI analyst, I want to tag an output as helpful or not, so that the system learns which retrievals were useful.
28. As a knowledge owner, I want retrieval to be re-weighted based on feedback, so that future answers improve over time.

### Return to Government (outcome-level)
29. As a government stakeholder, I want consistent, automated compliance checks, so that revenue leakage (PNBP) is reduced.
30. As a government stakeholder, I want faster, consistent processing of import-technical queries, so that operational cost falls and throughput rises.
31. As a government stakeholder, I want a policy feedback loop and market intelligence, so that trade competitiveness and enforcement improve.

## Implementation Decisions

### Architecture
- The system is a modular FastAPI backend fronted by an API Gateway, with Telegram as the MVP interface. Async workers handle long-running reasoning/retrieval.
- Request flow is a fixed pipeline: **receive → classify intent → build/validate context → select thinking model → retrieve knowledge → generate structured output → (Phase 2: apply decision rules → create task) → return response.**
- The pipeline is orchestrated by a thin coordinator; each stage below is a deep module with a narrow interface so it can be tested and replaced independently.

### Modules (MVP)
- **Context Builder** — Input: raw query. Output: an **Inferred Context** (`Client`, `Objective`, `Audience`, `DecisionRequired`, `Constraints`) for the user to confirm/correct, then a validated (confirmed) `Context`. The asker's identity is stamped on it. Encapsulates the rule *"never output without Context"* via infer-plus-confirm, not rejection. Validation (all fields present after confirmation) is pure and testable; inference is behind the LLM port.
- **Intent Classifier** — Input: query (+ context). Output: an intent label (`compliance`, `risk`, `opportunity`, `strategy`). Selects both the output shape (Compliance Answer vs Advisory Brief) and the web/retrieval mode.
- **Retrieval Layer (RAG) — a router** — Input: query + context. Output: ordered grounding with source identifiers **tagged by source** (official pasal cite vs internal note id). Regulation sub-queries → `pasal-id` (incl. `get_law_status` to detect `dicabut`/`diubah`); internal sub-queries → FAISS over the Obsidian Vault. Returns empty rather than a low-relevance match. In headless runs where `pasal-id` is unavailable, regulation grounding is treated as unavailable (→ compliance refusal), never silently substituted. The FAISS index build/refresh is a separate concern from query-time retrieval.
- **Reasoning + Thinking Engine** — Input: query + context + grounding. For `compliance`: produces a grounded **Compliance Answer** with verbatim Indonesian pasal citations — **or refuses** if grounding is empty or the regulation is revoked/amended (ADR-0001/0002); no thinking model used. For `risk`/`opportunity`/`strategy`: emits a typed **Finding** and produces a six-section **Advisory Brief**, selecting a **Thinking Model** from a registry (LLM picks + justifies; named in output; deterministic per-intent default on fallback). The LLM call is behind a port so it can be stubbed.
- **Web Search Strategy** — Input: intent / query type. Output: mode ∈ {`internal` (default), `web` (fallback), `hybrid` (strategy)}. Hard guardrail: returns `internal` for compliance / regulation / internal-process queries regardless of other signals. Pure routing logic, no I/O.

### Modules (Phase 2 — specified, staged)
- **Decision Engine** — Input: a typed **Finding** (`compliance_status` ∈ {compliant, non_compliant, not_applicable, unknown}, `risks[]`, `opportunities[]`). Output: zero or more **Actions**: `compliance_status == non_compliant → remediation task`; each `risk → flag + task`; each `opportunity → assign to strategy`; everything else (compliant / not_applicable / unknown) → no action. Pure function reading flags, never interpreting prose; no I/O. A routine compliance lookup yields no Action.
- **Execution Hooks** — Input: an approved **Action**. Output: a Linear task (assignee/team from a configurable Action-type → team table). Port/adapter over the Linear API. Actions are **not** auto-filed: every Action passes a human-approval gate held by a designated **Approver** (a subset of the allowlist), approved in Telegram; the asker is notified but cannot self-approve. Duplicates are prevented by an **Action Dedup Key** derived from the confirmed Context + Action type + regulation reference — on collision the recurrence is attached to the existing open Action, never silently dropped. Lifecycle: `proposed → pending-approval → approved | rejected → filed` ([ADR-0008](adr/0008-execution-human-approval-gate.md)).
- **Feedback Loop** — *MVP portion ships:* persist every Query, confirmed Context, Finding, and output, plus Knowledge-Gap and stale-regulation events (required by ADR-0001/0002). *Phase 2:* user feedback tagging + retrieval re-weighting. The MVP **collects** signals but does not yet **act** on them.

### Knowledge base layout
The Obsidian vault follows the standard taxonomy, which the RAG indexer treats as the corpus root:
`/00_ORG_STANDARD/` (incl. `THINKING_ENGINE.md`, `OUTPUT_TEMPLATE.md`), `/01_POLICY/`, `/02_REGULATION/`, `/03_STANDARDS/`, `/04_PROCESS/`, `/05_SYSTEM/`, `/06_DATA/`, `/07_VPTI_OPERATION/`, `/08_MARKET_INTELLIGENCE/`, `/09_AI_INSIGHTS/`, `/10_EXECUTION/`.

### Tech stack
- Language: **Python** — FastAPI, pydantic (Context/Finding validation), pytest ([ADR-0005](adr/0005-python-implementation-language.md)).
- LLM: **modular `LLMClient` port**, default adapter **Azure OpenAI**; self-hosted adapter is the residency escape hatch ([ADR-0007](adr/0007-modular-llm-port-local-embeddings-residency.md)).
- Regulation grounding: **`pasal-id`** (text + `get_law_status`). Internal grounding: **FAISS** over the Obsidian Vault, **Qdrant** as the documented upgrade path ([ADR-0002](adr/0002-hybrid-grounding-pasal-id-and-faiss.md)).
- Embeddings: **local `multilingual-e5-large`** (sentence-transformers) — on-prem, multilingual, no Vault data leaves ([ADR-0007](adr/0007-modular-llm-port-local-embeddings-residency.md)).
- RAG orchestration: **thin custom** (no LangChain); LlamaIndex optional for Vault ingestion only ([ADR-0006](adr/0006-thin-custom-rag-no-langchain.md)).
- Web search: **Tavily** (strategy/opportunity only, never compliance). Bing Search API is retired (Aug 2025) and is not an option.
- Database: PostgreSQL. Queue/Cache: Redis. Execution: Linear (Phase 2). Interface: Telegram.
- Testing/eval: pytest (unit), pipeline integration tests, **Ragas** for AI eval (groundedness/relevance/correctness). Observability: loguru/OpenTelemetry.
- Infra add-ons: API Gateway, async workers, logging/monitoring, secrets management, Docker.

### Key behavioral contracts
- Invariants enforced at the orchestrator boundary: **(1)** no output without a confirmed `Context`; **(2)** no **Advisory Brief** without a named Thinking Model (compliance answers are exempt — they are grounded lookups, not analysis).
- **Grounded-or-refuse:** a `compliance` answer is produced only from retrieved grounding; empty grounding or a revoked/amended regulation → refuse + escalate + log a Knowledge Gap (ADR-0001/0002). Never from parametric memory.
- Compliance / regulation / internal-process answers are **internal-only** — the Web Search Strategy guardrail is authoritative and overrides any other mode signal.
- Official pasal text is cited **verbatim in Indonesian**, never machine-translated (ADR-0004).

## Testing Decisions

A good test here verifies **external, observable behavior through a module's public interface** — given an input, assert the output/decision — not internal implementation details (no asserting on private state, prompt strings, or call counts beyond what the contract guarantees). Modules are designed with narrow interfaces and minimal I/O specifically so they can be tested in isolation without the LLM, FAISS, or network.

Tests will be written for the three modules selected:

- **Decision Engine** — The highest-value tests; pure `Finding → [Action]`, no I/O. Cover each branch: `compliance_status == non_compliant` → remediation task; each risk → flag **and** task; each opportunity → strategy assignment; `compliant` / `not_applicable` / `unknown` → **no** Action (proves a routine lookup spawns nothing); combined Findings (e.g. non_compliant **and** a risk) → all applicable Actions. Table-driven over (Finding → expected Actions).
- **Context Builder** — Test the **pure validation** half (post-confirmation), not the LLM inference. Cover: a fully-populated Context validates; each missing field (`Client`, `Objective`, `Audience`, `DecisionRequired`, `Constraints`) is individually rejected naming the missing field; empty/whitespace treated as missing; identity-stamp present. Inference is behind the LLM port and out of scope for unit tests. This proves the *"never output without Context"* invariant at the point it's enforced.
- **Retrieval Layer (RAG) router** — Tested against a small fixed in-repo corpus and a **stubbed `pasal-id`**, so results are deterministic. Cover: a regulation sub-query routes to the pasal-id stub and a `dicabut` status surfaces (feeding the refusal path); an internal sub-query routes to FAISS and an obvious match ranks first; no relevant match → empty result (the "nothing over irrelevant" contract); `pasal-id` unavailable → regulation grounding reported unavailable, **never** substituted from FAISS. Grounding is tagged by source. The embedding call is a deterministic fake; the pasal-id client is a stub.

Prior art: none yet (greenfield repo). Establish the conventions with these three modules — pure-function table tests for Decision Engine and Context Builder, fixture-corpus tests for RAG — as the template later modules follow.

## Out of Scope

- **Decision Engine, Execution Hooks (Linear integration), and Feedback Loop implementation.** They are specified above but staged for Phase 2 per the handoff guidance ("Add decision engine after MVP"). Their interfaces are fixed now so the MVP orchestrator can leave clean seams.
- Authentication/authorization, multi-tenant access control, and role-based permissions beyond what Telegram identity provides.
- The web UI / executive slide-deck output, GitHub repo scaffold, and Obsidian vault starter content (these were offered as separate follow-up artifacts in the handoff).
- Production-grade evaluation/quality scoring of LLM output beyond the structured-format contract.
- Migration/ingestion tooling for the full historical regulation corpus — the MVP assumes the Obsidian vault exists and is maintained out-of-band.
- Non-functional targets (latency SLAs, throughput, cost ceilings) are not yet specified and are deferred.

## Further Notes

- This is explicitly **not a chatbot**. The differentiation is the enforced pipeline: traditional AI is `Input → Output`; this system is `Input → Think → Analyze → Decide → Act → Improve`. Reviewers should treat the two invariants (context-required, thinking-model-required) as the product, not as nice-to-haves.
- The repository is currently empty (greenfield, no VCS initialized). This PRD is published as a markdown file at `docs/PRD.md`; there is no issue tracker configured. Recommend initializing git and, if a tracker is adopted later, importing this PRD as the seed epic.
- Open questions still to resolve before/at build time:
  - Who maintains the Obsidian Vault and how is the FAISS index refresh triggered (on write, scheduled, manual)?
  - **Concrete** Action-type → Linear team/project values (the *mechanism* is decided — a configurable table — but the team names are owed by the org before Phase 2 Execution Hooks; ADR-0008).
  - Who holds the Approver role (which subset of the allowlist)? (ADR-0008)
  - Is there a hard "regulation/internal text must never leave Indonesia" policy? If yes, the self-hosted LLM adapter becomes the required default (ADR-0007).
- Resolved in the grilling session: Context collection (infer + confirm, Q1), output shapes (Q2), grounding policy & source (ADR-0001/0002), thinking-model scope & selection (Q5), identity & session model (ADR-0003), operating language (ADR-0004), Decision Engine contract (Q8), MVP feedback scope (Q9), language/framework (ADR-0005), RAG stack & orchestration (ADR-0006), LLM/embeddings/web-search providers & residency posture (ADR-0007), Phase-2 Execution approval gate / Approver role / dedup / assignment mechanism (ADR-0008).
- Domain language used throughout: VPTI (Verifikasi atau Penelusuran Teknis Impor), PNBP (state revenue / leakage), LS/LVS, Permendag, OSS, INATRADE. A formal glossary (`UBIQUITOUS_LANGUAGE.md`) is recommended as a follow-up.
