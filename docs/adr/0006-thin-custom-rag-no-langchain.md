# Thin custom RAG orchestration; no LangChain

**Status:** accepted

The retrieval/reasoning pipeline is hand-written: `sentence-transformers` for embeddings, `faiss` directly for the internal Vault index, and a custom router (pasal-id vs FAISS, per ADR-0002). FAISS is the MVP vector store; Qdrant (self-hosted) is the documented upgrade path. We do **not** use LangChain. LlamaIndex may be added later for Vault ingestion/chunking only.

## Why

The pipeline is small and opinionated — a source router, two output shapes, a refusal path, and a thinking-model registry. LangChain's abstractions tend to obscure exactly the routing logic that is the heart of ADR-0002, and `pasal-id` is an MCP/API call that lives outside any RAG framework regardless. Legibility of the router beats the connectors/retries a framework would provide at this scale.

## Note for future readers

If you are about to "add LangChain to simplify this," check whether it actually simplifies the router or just wraps it. The deliberate choice is a thin, readable pipeline.
