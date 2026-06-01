"""Agent-layer unit tests (ADR-0009). Each agent's core is testable with injected
fakes — no scheduler, no network. Stubs until implemented per agent issue."""

import pytest


@pytest.mark.skip(reason="implement in vaos-agents/regulation-watch")
def test_find_stale_returns_only_revoked_or_amended() -> None:
    # given cited refs + a fake status checker, returns the diubah/dicabut ones.
    ...


@pytest.mark.skip(reason="implement in vaos-agents/knowledge-gap-resolver")
def test_digest_ranks_gaps_by_frequency() -> None:
    # InMemoryStore with repeated gaps -> ranked digest, most frequent first.
    ...


@pytest.mark.skip(reason="implement in vaos-agents/market-intel")
def test_scan_distills_one_insight_per_topic() -> None:
    # fake WebSearch -> one Insight per topic.
    ...
