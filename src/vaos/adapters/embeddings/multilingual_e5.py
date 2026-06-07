"""Local multilingual-e5 embeddings via sentence-transformers (ADR-0007).
On-prem — Vault content never leaves the machine.

The model (~GB) loads lazily on first embed so importing this module is cheap and
sentence-transformers stays an optional [rag] dependency. The encoder is
injectable for testing the wrapper without the real model.

e5 expects asymmetric prefixes — "passage: " for stored notes, "query: " for
search queries — which is what drives the embed_passage / embed_query split.
"""

from typing import Any, Protocol

from vaos.ports.embeddings import Embedder


class _Encoder(Protocol):
    def encode(self, sentences: list[str], **kwargs: Any) -> Any: ...


class MultilingualE5Embedder(Embedder):
    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-large",
        model: _Encoder | None = None,
    ) -> None:
        self._model_name = model_name
        self._model = model  # lazy-load the real model on first embed

    def _load(self) -> _Encoder:
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self._model_name)
        return self._model

    def _encode(self, prefix: str, texts: list[str]) -> list[list[float]]:
        vectors = self._load().encode([prefix + t for t in texts], normalize_embeddings=True)
        return [[float(x) for x in row] for row in vectors]

    def embed_passage(self, texts: list[str]) -> list[list[float]]:
        return self._encode("passage: ", texts)

    def embed_query(self, texts: list[str]) -> list[list[float]]:
        return self._encode("query: ", texts)
