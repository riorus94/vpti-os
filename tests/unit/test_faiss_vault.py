"""FaissVault — FAISS over the Obsidian vault (vaos-mvp/04, ADR-0006/0007).

Real faiss, fake (keyword) Embedder — no model download, deterministic scoring.
Builds over a tiny temp vault so retrieval assertions are exact."""

from pathlib import Path

from vaos.domain.grounding import GroundingSource
from vaos.modules.retrieval.faiss_vault import FaissVault


class FakeEmbedder:
    """Deterministic bag-of-vocab vectors: related text overlaps, unrelated is orthogonal."""

    VOCAB = ("dicabut", "vpti", "surveyor", "permendag", "oss", "impor")

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[float(t.lower().count(w)) for w in self.VOCAB] for t in texts]


def _vault(tmp: Path) -> Path:
    root = tmp / "vault"
    (root / "02_REGULATION").mkdir(parents=True)
    (root / "07_VPTI_OPERATION").mkdir(parents=True)
    (root / "02_REGULATION" / "reg.md").write_text(
        "permendag dicabut dicabut impor", encoding="utf-8"
    )
    (root / "07_VPTI_OPERATION" / "ops.md").write_text("vpti surveyor", encoding="utf-8")
    return root


async def test_build_then_query_returns_the_most_relevant_note(tmp_path: Path) -> None:
    vault = _vault(tmp_path)
    faiss_vault = FaissVault(FakeEmbedder(), index_path=str(tmp_path / "v.faiss"))
    faiss_vault.build(str(vault))

    grounding = await faiss_vault.query("apakah regulasi dicabut?")

    assert not grounding.is_empty
    top = grounding.chunks[0]
    assert top.reference.endswith("reg.md")     # the note carrying 'dicabut'
    assert top.source is GroundingSource.VAULT
    assert top.status is None                    # internal notes have no regulation status
    assert 0.0 < top.score <= 1.0001


async def test_query_below_threshold_returns_empty(tmp_path: Path) -> None:
    # 'oss' appears in no note -> every match scores 0, under the min_score floor.
    vault = _vault(tmp_path)
    faiss_vault = FaissVault(FakeEmbedder(), index_path=str(tmp_path / "v.faiss"), min_score=0.5)
    faiss_vault.build(str(vault))

    grounding = await faiss_vault.query("oss")
    assert grounding.is_empty


async def test_query_before_build_returns_empty(tmp_path: Path) -> None:
    # Wired but not yet indexed: internal grounding is simply absent (safe), not a crash.
    faiss_vault = FaissVault(FakeEmbedder(), index_path=str(tmp_path / "missing.faiss"))
    assert (await faiss_vault.query("dicabut")).is_empty


async def test_query_loads_persisted_index_without_rebuilding(tmp_path: Path) -> None:
    index_path = str(tmp_path / "v.faiss")
    FaissVault(FakeEmbedder(), index_path=index_path).build(str(_vault(tmp_path)))

    # A fresh instance (separate "process") queries off disk — build and query are decoupled.
    reader = FaissVault(FakeEmbedder(), index_path=index_path)
    grounding = await reader.query("vpti surveyor")

    assert grounding.chunks[0].reference.endswith("ops.md")
