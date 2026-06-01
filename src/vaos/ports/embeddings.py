"""Embeddings port (ADR-0007). Default adapter is local multilingual-e5 — Vault
content never leaves the machine."""

from typing import Protocol


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...
