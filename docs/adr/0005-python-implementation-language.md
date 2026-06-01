# Python (FastAPI / pydantic / pytest) as the implementation language

**Status:** accepted

The core application is built in Python: FastAPI (web/Telegram-webhook layer), pydantic (Context/Finding validation), pytest (tests).

## Why

VAOS is AI-heavy — RAG, embeddings, and AI-specific evaluation. The mature tooling for all three is Python-native: Ragas (the chosen eval framework) is Python-only, `sentence-transformers` and FAISS are Python, and LangChain/LlamaIndex are Python-first. The original handoff already specified FastAPI. TypeScript's main advantage — one language shared with a web frontend — does not apply: the interface is Telegram, not a web app.

## Considered and rejected

- **TypeScript (NestJS/zod/Jest).** Defensible only for a TS-native team; rejected because the team is not TS-locked and the Python AI ecosystem advantage is decisive here. The pure modules (Decision Engine, Context Builder) would have been equally clean in TS, but the RAG/eval layers would have fought the ecosystem.
