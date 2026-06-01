"""Regulation retrieval via pasal-id — official text + get_law_status
(vaos-mvp/05, ADR-0002). A dicabut/diubah status must surface to the refusal path."""

from vaos.domain.grounding import Grounding


class PasalIdClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url

    async def query(self, text: str) -> Grounding:
        raise NotImplementedError(
            "vaos-mvp/05 — fetch pasal text + status; raise/flag if unavailable (no FAISS fallback)"
        )
