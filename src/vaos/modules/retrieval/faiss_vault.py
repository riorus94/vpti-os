"""Internal Vault retrieval — FAISS over the Obsidian vault, local embeddings
(vaos-mvp/04, ADR-0006/0007). Index build/refresh is separate from query time:
build() persists the index + a metadata sidecar so query() can run in a fresh
process without re-embedding.

Cosine similarity via an inner-product index over L2-normalized vectors. Internal
notes carry no Regulation Status (status stays None) — regulation text and its
dicabut/diubah status come from pasal-id, never from here (ADR-0002).
"""

import json
from pathlib import Path

import faiss
import numpy as np

from vaos.domain.grounding import Grounding, GroundingChunk, GroundingSource
from vaos.ports.embeddings import Embedder

_Meta = list[dict[str, str]]


def _strip_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            return text[end + 4 :].lstrip()
    return text


def _matrix(vectors: list[list[float]]) -> np.ndarray:
    return np.asarray(vectors, dtype="float32")


class FaissVault:
    def __init__(self, embedder: Embedder, index_path: str, min_score: float = 0.0) -> None:
        self._embedder = embedder
        self._index_path = Path(index_path)
        self._meta_path = self._index_path.with_suffix(self._index_path.suffix + ".meta.json")
        self._min_score = min_score
        self._index: faiss.Index | None = None
        self._meta: _Meta | None = None

    def build(self, vault_path: str) -> int:
        """Embed every *.md note and persist the index + metadata sidecar. Returns
        the number of notes indexed (0 if the vault has none)."""
        root = Path(vault_path)
        refs: list[str] = []
        texts: list[str] = []
        for path in sorted(root.rglob("*.md")):
            refs.append(str(path.relative_to(root)))
            texts.append(_strip_frontmatter(path.read_text(encoding="utf-8")))

        vectors = _matrix(self._embedder.embed(texts)) if texts else np.zeros((0, 1), "float32")
        faiss.normalize_L2(vectors)
        index = faiss.IndexFlatIP(vectors.shape[1])
        if vectors.shape[0]:
            index.add(vectors)

        self._index_path.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(index, str(self._index_path))
        meta: _Meta = [{"reference": r, "text": t} for r, t in zip(refs, texts, strict=True)]
        self._meta_path.write_text(json.dumps(meta), encoding="utf-8")
        self._index, self._meta = index, meta
        return len(meta)

    async def query(self, text: str, top_k: int = 5) -> Grounding:
        if self._index is None and not self._index_path.exists():
            return Grounding(chunks=[])  # not indexed yet: internal grounding absent (safe)
        index, meta = self._load()
        if index.ntotal == 0:
            return Grounding(chunks=[])

        vector = _matrix(self._embedder.embed([text]))
        faiss.normalize_L2(vector)
        scores, ids = index.search(vector, min(top_k, index.ntotal))

        chunks: list[GroundingChunk] = []
        for score, idx in zip(scores[0], ids[0], strict=True):
            if idx < 0 or float(score) < self._min_score:
                continue
            note = meta[idx]
            chunks.append(
                GroundingChunk(
                    source=GroundingSource.VAULT,
                    reference=note["reference"],
                    text=note["text"],
                    score=float(score),
                )
            )
        return Grounding(chunks=chunks)

    def _load(self) -> tuple[faiss.Index, _Meta]:
        if self._index is None or self._meta is None:
            self._index = faiss.read_index(str(self._index_path))
            self._meta = json.loads(self._meta_path.read_text(encoding="utf-8"))
        return self._index, self._meta
