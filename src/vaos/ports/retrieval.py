"""Retrieval source ports — the two legs the RetrievalRouter depends on (ADR-0002).

Symmetric seams so the router is testable through its interface with in-memory
fakes (no FAISS, no pasal-id HTTP):

- RegulationSource — official regulation text (pasal-id). LOAD-BEARING: when it
  cannot be reached it raises RegulationSourceUnavailable. The router must report
  the regulation grounding as unavailable, never substitute the internal leg.
- InternalSource — the FAISS-indexed Vault of internal notes.

Adapters: adapters/.../pasal_id.PasalIdClient and .../faiss_vault.FaissVault
satisfy these structurally.
"""

from typing import Protocol

from vaos.domain.grounding import Grounding


class RegulationSourceUnavailable(Exception):
    """The regulation source could not be reached. Distinct from an empty result:
    'unavailable' is an ops failure (retry later), not a missing-content gap."""


class RegulationSource(Protocol):
    async def query(self, text: str) -> Grounding: ...


class InternalSource(Protocol):
    async def query(self, text: str) -> Grounding: ...
