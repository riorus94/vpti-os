"""Vault index build CLI (vaos-mvp/04): `python -m vaos.index`.

Builds the FAISS index over the Obsidian vault so `internal_source=faiss` is
usable at runtime. Build is offline and decoupled from query time — run it once
at setup and again whenever vault notes change. The real multilingual-e5 model is
only constructed for an actual build (run() accepts an injected vault for tests).
"""

import sys
from pathlib import Path

from vaos.config import Settings
from vaos.modules.retrieval.faiss_vault import FaissVault


def _default_vault(settings: Settings) -> FaissVault:
    from vaos.adapters.embeddings.multilingual_e5 import MultilingualE5Embedder

    return FaissVault(MultilingualE5Embedder(settings.embedding_model), settings.faiss_index_path)


def run(settings: Settings, build_vault: FaissVault | None = None) -> int:
    if not Path(settings.vault_path).is_dir():
        print(f"vault path not found: {settings.vault_path}", file=sys.stderr)
        return 1

    vault = build_vault or _default_vault(settings)
    count = vault.build(settings.vault_path)
    if count == 0:
        print(f"no notes found in {settings.vault_path}", file=sys.stderr)
        return 1

    print(f"indexed {count} note(s) -> {settings.faiss_index_path}")
    return 0


def main() -> int:
    return run(Settings())


if __name__ == "__main__":
    raise SystemExit(main())
