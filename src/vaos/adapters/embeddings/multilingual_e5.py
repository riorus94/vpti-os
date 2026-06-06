"""Local multilingual-e5 embeddings via sentence-transformers (ADR-0007).
On-prem — Vault content never leaves the machine.

The model (~GB) loads lazily on first embed so importing this module is cheap and
sentence-transformers stays an optional [rag] dependency. The encoder is
injectable for testing the wrapper without the real model.

Note: e5 recommends asymmetric "query:"/"passage:" prefixes for best retrieval.
The Embedder port is symmetric, so this MVP adapter omits prefixes; splitting the
port into embed_query/embed_passage is a future refinement.
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

    def embed(self, texts: list[str]) -> list[list[float]]:
        vectors = self._load().encode(texts, normalize_embeddings=True)
        return [[float(x) for x in row] for row in vectors]
