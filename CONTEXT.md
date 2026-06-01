# VPTI AI Operating System (VAOS)

The operational-intelligence platform that turns VPTI regulation and institutional knowledge into grounded, structured, actionable output. This glossary defines the domain language; it is not a spec.

## Language

**Context**:
The five-field frame that scopes a request to a real decision: `Client`, `Objective`, `Audience`, `Decision Required`, `Constraints`. Every output carries a Context — it is inferred from the user's query and confirmed by the user, never absent.
_Avoid_: metadata, parameters, prompt

**Inferred Context**:
A Context the system proposes by reading the user's query, before the user has confirmed it. Becomes a (confirmed) **Context** once the user accepts or corrects it.

**Query**:
The natural-language request a user sends (via Telegram in the MVP). The raw input from which an **Inferred Context** is built.
_Avoid_: prompt, message, question

**Intent**:
The classification of a **Query** into one of `compliance`, `risk`, `opportunity`, or `strategy`. Selects both the retrieval/web mode and the output shape.

**Compliance Answer**:
A compact, grounded, source-cited response to a `compliance`-intent **Query** (e.g. "does X require VPTI / which LS / which HS code"). Direct, no padding. The output shape for `compliance` intent.
_Avoid_: brief, report

**Advisory Brief**:
The full six-section structured output — `Executive Summary, Context, Analysis, Risk, Opportunity, Recommendation` — produced for `risk`, `opportunity`, and `strategy` intents. A thinking model is applied to produce it.
_Avoid_: answer, summary, memo

**Grounding**:
The retrieved knowledge-base notes that a **Compliance Answer** is built from and cited against. A compliance output with no Grounding is not produced (see ADR-0001).
_Avoid_: source, context (reserve "Context" for the five-field frame)

**Knowledge Gap**:
A `compliance` **Query** for which retrieval returned no **Grounding**. The system refuses, escalates, and logs the gap so the vault owner knows what to add.
_Avoid_: miss, no-result

**Regulation Status**:
Whether a cited regulation is currently in force — `berlaku` (in force), `diubah` (amended), or `dicabut` (revoked). Sourced from `pasal-id`. A **Compliance Answer** must not assert an obligation from a regulation that is `dicabut`/`diubah` without naming the superseding reference.

**Vault**:
The Obsidian knowledge base holding **internal** knowledge — VPTI process, OSS/INATRADE system notes, market intelligence — indexed in FAISS. Distinct from regulation text, which comes from `pasal-id`.
_Avoid_: knowledge base (ambiguous — could mean regulation too), corpus

**Thinking Model**:
A named reasoning method (First Principles, Systems Thinking, Pre-mortem, Five Whys, Second-order Thinking) applied when producing an **Advisory Brief**. Selected per request and named in the output. Not used for a **Compliance Answer**.
_Avoid_: framework (reserve for the consultant layer generally), method

**Authorized User**:
A person whose Telegram user ID is on the allowlist and who may therefore receive answers. Their identity is stamped onto every **Context** they create. A non-authorized sender is rejected.
_Avoid_: account, member

**Finding**:
The typed result the AI Reasoning layer emits: a `compliance_status` (`compliant` / `non_compliant` / `not_applicable` / `unknown`) plus lists of risks and opportunities. The judgment about a concrete case lives here. A general rule lookup yields `not_applicable`/`unknown`, not `non_compliant`.
_Avoid_: result, verdict, output

**Action**:
A unit of work the Decision Engine produces from a **Finding** — a remediation task, a risk flag+task, or a strategy assignment. A compliant or informational **Finding** produces no Action. An Action is *proposed*, not auto-executed: it moves `proposed → pending-approval → approved | rejected → filed` and becomes a Linear task only after an **Approver** approves it (Phase 2; see ADR-0008).
_Avoid_: task (reserve "task" for the Linear artifact specifically), ticket

**Approver**:
A member of the Telegram allowlist holding approval authority for **Actions** — a subset of **Authorized Users**. Only an Approver can turn a proposed Action into a filed Linear task. Distinct from the asker, who is notified but cannot self-approve. Separates *asking a question* from *dispatching enforcement*.
_Avoid_: admin, reviewer, owner

**Agent**:
A proactive, scheduled/triggered runner (in `src/vaos/agents/`) that pursues a standing goal
without waiting for a **Query** — e.g. Regulation-Watch, Knowledge-Gap Resolver, Market-Intel.
Reuses the same domain + ports as the request pipeline; produces work only via **Actions**
through the approval gate (ADR-0008/0009). Distinct from the reactive orchestrator.
_Avoid_: bot, job, worker (reserve "worker" for the async-processing infra)

**Action Dedup Key**:
The identity used to prevent duplicate **Actions** — derived from the confirmed **Context** (Client/Objective/Decision) + Action type + regulation reference (not raw query text). On collision, the recurrence is attached to the existing open Action rather than filed again or silently dropped.
_Avoid_: hash, fingerprint

## Example dialogue

> **Analyst:** "Apakah impor ban truk wajib VPTI?"
> **VAOS:** *(infers a Context)* "I read this as — Objective: determine VPTI obligation for truck tyres; Audience: importer/analyst; Decision: whether to proceed with import. Correct?"
> **Analyst:** "Yes."
> **VAOS:** *(now has a confirmed **Context**, proceeds to retrieve and answer)*

This shows the rule in practice: the **Context** invariant is never skipped, but it is satisfied by inference-plus-confirmation rather than by interrogation.
