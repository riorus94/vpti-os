"""Execution logic (vaos-phase2-execution, ADR-0008).

dedup_key derives from the confirmed Context (not raw query) + action type +
regulation ref. approve files via the ExecutionHook; only an Approver may approve.
"""

import asyncio

import pytest

from vaos.adapters.execution.stub import StubExecutionHook
from vaos.domain.action import Action, ActionState, ActionType
from vaos.domain.context import Context
from vaos.modules.execution import approve, dedup_key


def _ctx() -> Context:
    return Context(client="KSO", objective="cek wajib VPTI", audience="importer",
                   decision_required="lanjut?", constraints="-", asker_id=1)


def test_dedup_key_is_deterministic() -> None:
    k1 = dedup_key(_ctx(), ActionType.REMEDIATION, "Permendag X Pasal 3")
    k2 = dedup_key(_ctx(), ActionType.REMEDIATION, "Permendag X Pasal 3")
    assert k1 == k2 and k1 != ""


def test_dedup_key_differs_on_regulation() -> None:
    k1 = dedup_key(_ctx(), ActionType.REMEDIATION, "Permendag X")
    k2 = dedup_key(_ctx(), ActionType.REMEDIATION, "Permendag Y")
    assert k1 != k2


def test_dedup_key_differs_on_action_type() -> None:
    # Same Context + reg, different action type => distinct keys, so a risk flag
    # never dedups against a remediation for the same case (ADR-0008).
    k1 = dedup_key(_ctx(), ActionType.REMEDIATION, "Permendag X")
    k2 = dedup_key(_ctx(), ActionType.RISK_FLAG, "Permendag X")
    assert k1 != k2


def test_dedup_key_differs_on_context_field() -> None:
    # The key is derived from the confirmed Context, not the raw query: two
    # Contexts differing only in objective must not collide.
    other = _ctx().model_copy(update={"objective": "cek wajib lain"})
    k1 = dedup_key(_ctx(), ActionType.REMEDIATION, "Permendag X")
    k2 = dedup_key(other, ActionType.REMEDIATION, "Permendag X")
    assert k1 != k2


def test_dedup_key_normalizes_case_and_whitespace() -> None:
    # ADR-0008 normalization: casing/padding differences collapse so the same
    # case keys identically (otherwise dedup would silently miss duplicates).
    base = _ctx()
    padded = Context(client="  KSO ", objective="CEK WAJIB VPTI", audience="Importer",
                     decision_required="LANJUT?", constraints="-", asker_id=base.asker_id)
    k1 = dedup_key(base, ActionType.REMEDIATION, "Permendag X Pasal 3")
    k2 = dedup_key(padded, ActionType.REMEDIATION, "  permendag x pasal 3 ")
    assert k1 == k2


def test_approver_files_action() -> None:
    a = Action(type=ActionType.REMEDIATION, summary="remediate")
    res = asyncio.run(approve(a, approver_id=7, approvers={7}, hook=StubExecutionHook()))
    assert res.state is ActionState.FILED
    assert res.linear_task_id


def test_non_approver_cannot_approve() -> None:
    a = Action(type=ActionType.REMEDIATION, summary="remediate")
    with pytest.raises(PermissionError):
        asyncio.run(approve(a, approver_id=9, approvers={7}, hook=StubExecutionHook()))
