"""PasalIdClient over the pasal-id MCP (#5, ADR-0002). The MCP wire is faked; this
pins the mapping search_laws -> grounding, get_law_status -> Regulation Status
flagging, and MCP-unreachable -> RegulationSourceUnavailable (so the router reports
regulation grounding unavailable and never substitutes the vault)."""

from typing import Any

import pytest

from vaos.domain.grounding import GroundingSource, RegulationStatus
from vaos.modules.retrieval.pasal_id import McpUnavailable, PasalIdClient
from vaos.ports.retrieval import RegulationSourceUnavailable


class FakeMcp:
    def __init__(self, search: dict[str, Any], status: dict[str, Any] | None = None,
                 fail: bool = False) -> None:
        self._search, self._status, self._fail = search, status, fail

    async def call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self._fail:
            raise McpUnavailable("pasal-id down")
        if tool == "search_laws":
            return self._search
        if tool == "get_law_status":
            return self._status or {}
        raise AssertionError(f"unexpected tool {tool}")


async def test_in_force_hit_is_grounded_with_pasal_source_and_status() -> None:
    mcp = FakeMcp(
        search={"results": [{
            "law": "Permendag No. 16 Tahun 2025", "pasal": "Pasal 3",
            "text": "LS wajib.", "score": 0.9,
        }]},
        status={"status": "berlaku", "superseded_by": None},
    )
    grounding = await PasalIdClient(mcp).query("wajib LS?")

    chunk = grounding.chunks[0]
    assert chunk.source is GroundingSource.PASAL_ID
    assert chunk.reference == "Permendag No. 16 Tahun 2025 Pasal 3"
    assert chunk.status is RegulationStatus.BERLAKU
    assert chunk.superseded_by is None


async def test_revoked_hit_is_flagged_dicabut_with_superseding_reference() -> None:
    mcp = FakeMcp(
        search={"results": [{
            "law": "Permendag No. 36 Tahun 2023", "pasal": "Pasal 19",
            "text": "...", "score": 0.7,
        }]},
        status={"status": "dicabut", "superseded_by": "Permendag No. 16 Tahun 2025"},
    )
    grounding = await PasalIdClient(mcp).query("kebijakan impor")

    chunk = grounding.chunks[0]
    assert chunk.status is RegulationStatus.DICABUT          # flagged, not dropped
    assert chunk.superseded_by == "Permendag No. 16 Tahun 2025"


async def test_mcp_unreachable_raises_regulation_source_unavailable() -> None:
    with pytest.raises(RegulationSourceUnavailable):
        await PasalIdClient(FakeMcp(search={}, fail=True)).query("apa pun")
