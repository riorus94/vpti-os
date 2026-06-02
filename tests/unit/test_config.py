"""Settings allowlist / approver parsing (ADR-0003 / ADR-0008).

The allowlist gates access; the approver subset gates Action approval. Both are
parsed from comma-separated env strings — pure, security-relevant, cheap to test.
"""

import pytest

from vaos.config import Settings


def _settings(**over: str) -> Settings:
    return Settings(**over)


def test_empty_allowlist_yields_empty_set() -> None:
    # No allowlist configured => nobody is authorized (fail closed).
    assert _settings(telegram_allowlist="").allowlist_ids() == set()


def test_allowlist_parses_comma_separated_ids() -> None:
    assert _settings(telegram_allowlist="7,8,9").allowlist_ids() == {7, 8, 9}


def test_allowlist_tolerates_surrounding_whitespace() -> None:
    assert _settings(telegram_allowlist=" 7 , 8 , 9 ").allowlist_ids() == {7, 8, 9}


def test_allowlist_ignores_blank_segments() -> None:
    # Trailing/duplicate commas must not produce a spurious entry or crash.
    assert _settings(telegram_allowlist="7,,8,").allowlist_ids() == {7, 8}


def test_allowlist_deduplicates() -> None:
    assert _settings(telegram_allowlist="7,7,8").allowlist_ids() == {7, 8}


def test_allowlist_rejects_non_integer() -> None:
    with pytest.raises(ValueError):
        _settings(telegram_allowlist="7,abc").allowlist_ids()


def test_empty_approvers_yields_empty_set() -> None:
    # No approver configured => no Action can be approved (ADR-0008, fail closed).
    assert _settings(telegram_approvers="").approver_ids() == set()


def test_approvers_parse_independently_of_allowlist() -> None:
    s = _settings(telegram_allowlist="7,8,9", telegram_approvers="8")
    assert s.approver_ids() == {8}
    assert s.allowlist_ids() == {7, 8, 9}


def test_approvers_tolerate_whitespace_and_blanks() -> None:
    assert _settings(telegram_approvers=" 8 , ,9 ").approver_ids() == {8, 9}
