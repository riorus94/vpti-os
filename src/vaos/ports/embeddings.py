"""Embeddings port (ADR-0007). Default adapter is local multilingual-e5 — Vault
content never leaves the machine.

Asymmetric: e5 (and most retrieval models) embed a stored passage differently from
a search query, so the port distinguishes the two roles."""

from typing import Protocol


class Embedder(Protocol):
    def embed_passage(self, texts: list[str]) -> list[list[float]]: ...
    def embed_query(self, texts: list[str]) -> list[list[float]]: ...
