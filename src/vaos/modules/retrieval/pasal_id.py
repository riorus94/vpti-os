"""Regulation retrieval via the pasal-id MCP (vaos-mvp/05, ADR-0002).

pasal-id exposes MCP tools (search_laws, get_pasal, get_law_status, list_laws).
This adapter grounds a query with search_laws and stamps each hit's Regulation
Status via get_law_status, so a dicabut/diubah regulation is FLAGGED (with its
superseding reference) and never silently cited as current. When the MCP is
unreachable it raises RegulationSourceUnavailable — the router then reports
regulation grounding as unavailable and never substitutes the internal vault.

NOTE: the MCP wire contract (tool argument + response field names) is ASSUMED and
isolated behind McpToolCaller; verify it against the live pasal-id MCP and adjust
the mapping below. The transport client satisfying McpToolCaller (HTTP + headless
auth) is a thin dependency wired separately.
"""

from typing import Any, Protocol

from vaos.domain.grounding import (
    Grounding,
    GroundingChunk,
    GroundingSource,
    RegulationStatus,
)
from vaos.ports.retrieval import RegulationSourceUnavailable


class McpUnavailable(Exception):
    """The pasal-id MCP could not be reached (transport/auth failure)."""


class McpToolCaller(Protocol):
    async def call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]: ...


_STATUS = {
    "berlaku": RegulationStatus.BERLAKU,
    "diubah": RegulationStatus.DIUBAH,
    "dicabut": RegulationStatus.DICABUT,
}


class PasalIdClient:
    def __init__(self, mcp: McpToolCaller) -> None:
        self._mcp = mcp

    async def query(self, text: str) -> Grounding:
        try:
            found = await self._mcp.call("search_laws", {"query": text})
            statuses: dict[str, tuple[RegulationStatus | None, str | None]] = {}
            chunks: list[GroundingChunk] = []
            for hit in found.get("results", []):
                law = hit["law"]
                if law not in statuses:
                    statuses[law] = await self._status(law)
                status, superseded_by = statuses[law]
                reference = f"{law} {hit.get('pasal', '')}".strip()
                chunks.append(
                    GroundingChunk(
                        source=GroundingSource.PASAL_ID,
                        reference=reference,
                        text=hit["text"],
                        score=float(hit.get("score", 1.0)),
                        status=status,
                        superseded_by=superseded_by,
                    )
                )
            return Grounding(chunks=chunks)
        except McpUnavailable as exc:
            raise RegulationSourceUnavailable(str(exc)) from exc

    async def _status(self, law: str) -> tuple[RegulationStatus | None, str | None]:
        info = await self._mcp.call("get_law_status", {"law": law})
        return _STATUS.get(str(info.get("status", "")).lower()), info.get("superseded_by")
