"""Vault index build CLI (#21). Core run() tested with a fake embedder over temp
vaults — no torch, no model download. The real e5 path is wired in main()."""

from pathlib import Path

import pytest

from vaos.config import Settings
from vaos.index import run
from vaos.modules.retrieval.faiss_vault import FaissVault


class FakeEmbedder:
    def _vectors(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t)), 1.0] for t in texts]  # non-zero dim + vector

    def embed_passage(self, texts: list[str]) -> list[list[float]]:
        return self._vectors(texts)

    def embed_query(self, texts: list[str]) -> list[list[float]]:
        return self._vectors(texts)


def _settings(tmp: Path) -> Settings:
    return Settings(vault_path=str(tmp / "vault"), faiss_index_path=str(tmp / "v.faiss"))


def _vault(settings: Settings) -> FaissVault:
    return FaissVault(FakeEmbedder(), index_path=settings.faiss_index_path)


def test_build_indexes_notes_and_reports(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = tmp_path / "vault"
    (root / "02_REGULATION").mkdir(parents=True)
    (root / "02_REGULATION" / "a.md").write_text("permendag impor", encoding="utf-8")
    (root / "b.md").write_text("vpti surveyor", encoding="utf-8")
    settings = _settings(tmp_path)

    rc = run(settings, build_vault=_vault(settings))

    assert rc == 0
    assert "indexed 2" in capsys.readouterr().out
    assert Path(settings.faiss_index_path).exists()


def test_empty_vault_exits_nonzero(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / "vault").mkdir()
    settings = _settings(tmp_path)

    rc = run(settings, build_vault=_vault(settings))

    assert rc == 1
    assert "no notes" in capsys.readouterr().err.lower()


def test_missing_vault_path_exits_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # Bails before constructing any embedder/index (so the real e5 model is never touched).
    rc = run(_settings(tmp_path))

    assert rc == 1
    assert "not found" in capsys.readouterr().err.lower()
