"""MultilingualE5Embedder wrapper logic (vaos-mvp/04, ADR-0007).

The real sentence-transformers model is lazy-loaded I/O (not unit-tested here);
this pins the wrapper: an injected encoder is called with L2 normalization on, and
its (numpy) output is returned as plain Python float lists for the FAISS leg."""

import numpy as np

from vaos.adapters.embeddings.multilingual_e5 import MultilingualE5Embedder


class FakeModel:
    def __init__(self) -> None:
        self.kwargs: dict[str, object] = {}

    def encode(self, sentences: list[str], **kwargs: object) -> np.ndarray:
        self.kwargs = kwargs
        rows = [[float(i), float(i) + 0.5] for i, _ in enumerate(sentences)]
        return np.array(rows, dtype="float32")


def test_embed_normalizes_and_returns_plain_float_lists() -> None:
    model = FakeModel()
    embedder = MultilingualE5Embedder(model=model)

    out = embedder.embed(["satu", "dua"])

    assert out == [[0.0, 0.5], [1.0, 1.5]]
    assert all(isinstance(x, float) for row in out for x in row)
    assert model.kwargs.get("normalize_embeddings") is True
