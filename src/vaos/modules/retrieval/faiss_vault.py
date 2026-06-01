"""Internal Vault retrieval — FAISS over the Obsidian vault, local embeddings
(vaos-mvp/04, ADR-0006/0007). Index build/refresh is separate from query time."""

from vaos.domain.grounding import Grounding
from vaos.ports.embeddings import Embedder


class FaissVault:
    def __init__(self, embedder: Embedder, index_path: str) -> None:
        self._embedder = embedder
        self._index_path = index_path

    def build(self, vault_path: str) -> None:
        raise NotImplementedError("vaos-mvp/04 — embed vault notes, write FAISS index")

    async def query(self, text: str, top_k: int = 5) -> Grounding:
        raise NotImplementedError("vaos-mvp/04 — empty result below threshold")
