"""Retrieval router (vaos-mvp/05) against a fixed fixture vault + stubbed pasal-id.

Cover: regulation sub-query -> pasal-id stub (incl. a dicabut case surfacing);
internal sub-query -> FAISS top-1 match; no match -> empty; pasal-id unavailable
-> regulation grounding reported unavailable (never FAISS-substituted).
"""

import pytest


@pytest.mark.skip(reason="implement in vaos-mvp/05")
def test_pasal_id_unavailable_is_not_substituted_by_faiss() -> None:
    ...
