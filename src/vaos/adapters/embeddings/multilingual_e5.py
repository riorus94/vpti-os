"""Local multilingual-e5 embeddings via sentence-transformers (ADR-0007).
On-prem — Vault content never leaves the machine."""

from vaos.ports.embeddings import Embedder


class MultilingualE5Embedder(Embedder):
    def __init__(self, model_name: str = "intfloat/multilingual-e5-large") -> None:
        self._model_name = model_name  # lazy-load the model on first embed

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError("vaos-mvp/04 — load sentence-transformers model, encode")
