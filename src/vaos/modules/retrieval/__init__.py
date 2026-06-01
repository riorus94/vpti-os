"""Retrieval Layer — a router (ADR-0002), not a single index.

Regulation sub-queries -> pasal_id (text + get_law_status).
Internal sub-queries  -> faiss_vault (local multilingual-e5).
Returns empty rather than a low-relevance match. Headless: if pasal-id is
unavailable, regulation grounding is reported unavailable, never substituted.
"""
