# Modular LLM port (Azure default), local embeddings — driven by data residency

**Status:** accepted

- **LLM:** a provider-agnostic `LLMClient` port with swappable adapters. **Azure OpenAI is the default production adapter** (no-training-by-default, Southeast Asia regional deployment). OpenAI-direct is an alternative; a self-hosted open model (Llama/Qwen) is the escape-hatch adapter if regulation text may never leave Indonesia. The port also serves as the test stub seam.
- **Embeddings:** local `multilingual-e5-large` via sentence-transformers. Multilingual (satisfies ADR-0004), free, offline — the entire internal Vault is embedded **on-prem** and never sent to a third party. Decoupled from the LLM vendor.
- **Web search:** Tavily, used only for `strategy`/`opportunity` intents, never compliance.

## Why

Compliance grounding is sacred (ADR-0001/0002), so what text leaves the country, and to whom, is a first-class constraint. The LLM call inherently sends query+grounding to a provider, so that exposure is concentrated there and is managed by choosing Azure (enterprise data handling) as the default adapter. Embeddings need not leave at all, so they don't — local embeddings keep the most sensitive internal asset (the Vault) fully on-prem.

## Note for future readers

The port makes the *provider* swappable but does not make the *residency decision* go away. Whatever adapter is wired as the production default governs data flow. Re-open this ADR if the residency policy hardens to "nothing leaves Indonesia" — then the self-hosted adapter becomes the required default, not an option.
