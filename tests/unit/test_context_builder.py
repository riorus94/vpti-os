"""Context validation — pure half of the Context Builder (vaos-mvp/02).

Cover: full Context validates; each missing field rejected naming it; blank/
whitespace treated as missing; asker identity present. Inference (LLM) is out of
unit scope — it lives behind the port.
"""

import pytest

from vaos.domain.context import Context


def test_blank_field_rejected() -> None:
    with pytest.raises(ValueError):
        Context(
            client="KSO", objective="", audience="analyst",
            decision_required="proceed?", constraints="none", asker_id=1,
        )
