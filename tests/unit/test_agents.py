"""Agent-layer unit tests (ADR-0009). Each agent's core is testable with injected
fakes — no scheduler, no network. Stubs until implemented per agent issue."""


from vaos.adapters.store.memory import InMemoryStore
from vaos.agents.knowledge_gap_resolver import digest
from vaos.agents.market_intel import scan
from vaos.agents.regulation_watch import find_stale
from vaos.domain.grounding import RegulationStatus


async def test_find_stale_returns_only_revoked_or_amended() -> None:
    statuses = {
        "Permendag 16/2025": (RegulationStatus.BERLAKU, None),
        "Permendag 36/2023": (RegulationStatus.DICABUT, "Permendag 16/2025"),
        "Permendag 3/2024": (RegulationStatus.DIUBAH, "Permendag 8/2024"),
    }

    async def status_of(ref: str) -> tuple[RegulationStatus, str | None]:
        return statuses[ref]

    stale = await find_stale(list(statuses), status_of)

    assert [(s.reference, s.status, s.superseded_by) for s in stale] == [
        ("Permendag 36/2023", RegulationStatus.DICABUT, "Permendag 16/2025"),
        ("Permendag 3/2024", RegulationStatus.DIUBAH, "Permendag 8/2024"),
    ]  # in-force Permendag 16/2025 excluded; superseding ref carried


async def test_find_stale_empty_when_all_in_force() -> None:
    async def status_of(ref: str) -> tuple[RegulationStatus, str | None]:
        return (RegulationStatus.BERLAKU, None)

    assert await find_stale(["A", "B"], status_of) == []


async def test_digest_ranks_gaps_by_frequency() -> None:
    store = InMemoryStore()
    for _ in range(3):
        await store.record_knowledge_gap("wajib LS untuk ban truk?", "ctx")
    await store.record_knowledge_gap("HS 3824.99 wajib LS?", "ctx")
    for _ in range(2):
        await store.record_knowledge_gap("izin impor besi baja?", "ctx")

    items = await digest(store)

    assert [(i.query, i.count) for i in items] == [
        ("wajib LS untuk ban truk?", 3),
        ("izin impor besi baja?", 2),
        ("HS 3824.99 wajib LS?", 1),
    ]


async def test_digest_of_empty_backlog_is_empty() -> None:
    assert await digest(InMemoryStore()) == []


class _FakeSearch:
    async def search(self, query: str) -> list[str]:
        return [f"{query}: tren naik", f"{query}: permintaan stabil"]


async def test_scan_distills_one_insight_per_topic() -> None:
    insights = await scan(["baja", "tekstil"], _FakeSearch())

    assert [i.topic for i in insights] == ["baja", "tekstil"]   # one per topic, in order
    assert "baja: tren naik" in insights[0].summary             # built from that topic's results
    assert all(i.summary for i in insights)


async def test_scan_yields_an_insight_even_with_no_results() -> None:
    class _Empty:
        async def search(self, query: str) -> list[str]:
            return []

    insights = await scan(["garam"], _Empty())
    assert len(insights) == 1
    assert insights[0].topic == "garam" and insights[0].summary  # non-empty placeholder summary
