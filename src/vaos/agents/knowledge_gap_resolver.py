"""Knowledge-Gap Resolver agent (ADR-0009). Turns refusal gaps into a worklist.

Reads the Knowledge-Gap backlog from the Store (vaos-mvp/09) and groups it into a
digest of what the Vault is missing, most-frequent first. Pure over an injected Store.
"""

from pydantic import BaseModel

from vaos.ports.store import Store


class GapDigestItem(BaseModel):
    query: str
    count: int


async def digest(store: Store) -> list[GapDigestItem]:
    """Group the Knowledge-Gap backlog into a ranked 'what to add to the Vault' list."""
    raise NotImplementedError("vaos-agents/knowledge-gap-resolver")
