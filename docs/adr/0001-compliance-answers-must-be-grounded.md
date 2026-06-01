# Compliance answers must be grounded or refused — never answered from model memory

**Status:** accepted

For `compliance`-intent queries, the system answers **only** from retrieved knowledge-base grounding. If the Retrieval Layer returns empty, the system refuses ("not found in knowledge base"), escalates, and logs a knowledge-gap signal for the vault owner — it does **not** fall back to the LLM's parametric knowledge or to web search.

## Why

VAOS's value proposition is that every compliance answer is traceable to a pasal. Answering from model memory produces confident, cited-looking, but potentially stale/wrong regulation answers — the worst failure mode for a system whose objective is reducing revenue leakage and ensuring compliance. A "not verified" label does not survive contact with real users; the only durable guarantee is "no grounding → no answer."

## Considered and rejected

- **Answer-with-warning (parametric fallback, labeled).** Rejected: labels get ignored; a wrong-but-confident compliance answer is more damaging than a refusal.
- **Web fallback for compliance.** Already prohibited by the Web Search Strategy guardrail; reaffirmed here.

## Scope

This applies to `compliance` intent only. `strategy` / `opportunity` intents may reason from parametric knowledge and use web search, because they are advisory, not authoritative.
