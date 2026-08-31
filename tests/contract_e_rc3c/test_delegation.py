"""Delegation subset, amplification, and expiry rules."""

from __future__ import annotations

from research_scaffold_harness.contract_e_rc3c import evaluate_delegation
from tests.contract_e_rc3c.factories import VALID_UNTIL, make_delegation


def test_child_subset_accepted() -> None:
    parent = make_delegation(
        role="parent",
        extra={
            "operations": ["source.read", "evidence.admit_passage"],
            "scope": ["lab-a", "lab-b"],
        },
    )
    child = make_delegation(
        role="child",
        extra={
            "operations": ["source.read"],
            "scope": ["lab-a"],
            "valid_until": "2026-06-30T00:00:00Z",
        },
    )
    decision = evaluate_delegation(parent, child)
    assert decision.accepted is True, decision.to_dict()


def test_operation_amplification_rejected() -> None:
    parent = make_delegation(role="parent")
    child = make_delegation(role="child", extra={"operations": ["source.read", "task.dispatch"]})
    decision = evaluate_delegation(parent, child)
    assert decision.primary_reason == "delegation_operation_amplification"
    assert decision.reason_is_normative is True


def test_scope_amplification_rejected() -> None:
    parent = make_delegation(role="parent")
    child = make_delegation(role="child", extra={"scope": ["lab-a", "lab-z"]})
    decision = evaluate_delegation(parent, child)
    assert decision.primary_reason == "delegation_scope_amplification"


def test_expiry_amplification_later_valid_until() -> None:
    parent = make_delegation(role="parent", extra={"valid_until": "2026-06-30T00:00:00Z"})
    child = make_delegation(role="child", extra={"valid_until": "2026-12-31T00:00:00Z"})
    decision = evaluate_delegation(parent, child)
    assert decision.primary_reason == "delegation_expiry_amplification"


def test_child_unbounded_when_parent_has_expiry() -> None:
    parent = make_delegation(role="parent", extra={"valid_until": VALID_UNTIL})
    child = make_delegation(role="child")
    del child["valid_until"]
    decision = evaluate_delegation(parent, child)
    assert decision.primary_reason == "delegation_expiry_amplification"


def test_equal_valid_until_accepted() -> None:
    parent = make_delegation(role="parent")
    child = make_delegation(role="child", extra={"valid_until": VALID_UNTIL})
    decision = evaluate_delegation(parent, child)
    assert decision.accepted is True


def test_noncurrent_child_rejected_for_new_exercise() -> None:
    parent = make_delegation(role="parent")
    child = make_delegation(role="child", extra={"current": False})
    decision = evaluate_delegation(parent, child)
    assert decision.primary_reason == "authority_basis_not_current"


def test_identical_operations_different_order_is_subset() -> None:
    parent = make_delegation(
        role="parent", extra={"operations": ["source.read", "x.y"], "scope": ["lab-a"]}
    )
    # parent does not actually have x.y as a domain operation; subset test is structural.
    parent["operations"] = ["source.read", "other.op"]
    child = make_delegation(role="child", extra={"operations": ["other.op", "source.read"]})
    decision = evaluate_delegation(parent, child)
    assert decision.accepted is True
