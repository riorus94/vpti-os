"""Execution logic (vaos-phase2-execution/02 & 03).

Cover: dedup_key derives from the confirmed Context (not raw query); a key
collision attaches (occurrences++) instead of filing twice and never silently
drops; only an Approver can approve; reject path. ExecutionHook + Store stubbed.
"""

import pytest


@pytest.mark.skip(reason="implement in vaos-phase2-execution/02 & 03")
def test_dedup_collision_attaches_not_duplicates() -> None:
    ...
