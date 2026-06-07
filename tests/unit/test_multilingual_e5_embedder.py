"""MultilingualE5Embedder wrapper logic (vaos-mvp/04, ADR-0007).

The real sentence-transformers model is lazy-loaded I/O (not unit-tested here);
this pins the wrapper: passages/queries get e5's asymmetric prefixes, encoding is
L2-normalized, and the (numpy) output becomes plain Python float lists."""

import numpy as np

from vaos.adapters.embeddings.multilingual_e5 import MultilingualE5Embedder


class FakeModel:
    def __init__(self) -> None:
        self.sentences: list[str] = []
        self.kwargs: dict[str, object] = {}

    def encode(self, sentences: list[str], **kwargs: object) -> np.ndarray:
        self.sentences = sentences
        self.kwargs = kwargs
        return np.array([[float(len(s))] for s in sentences], dtype="float32")


def test_embed_passage_applies_passage_prefix_and_normalizes() -> None:
    model = FakeModel()
    out = MultilingualE5Embedder(model=model).embed_passage(["regulasi"])

    assert model.sentences == ["passage: regulasi"]
    assert model.kwargs.get("normalize_embeddings") is True
    assert out == [[float(len("passage: regulasi"))]]
    assert all(isinstance(x, float) for row in out for x in row)


def test_embed_query_applies_query_prefix() -> None:
    model = FakeModel()
    MultilingualE5Embedder(model=model).embed_query(["wajib LS?"])

    assert model.sentences == ["query: wajib LS?"]
