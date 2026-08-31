"""Canonical wire cardinality attacks: no silent singular/plural coercion."""

from __future__ import annotations

import pytest

from research_scaffold_harness.contract_e_rc3c import evaluate_delegation, evaluate_envelope
from tests.contract_e_rc3c.factories import make_delegation, pair


def test_authority_basis_object_is_malformed() -> None:
    envelope, registry = pair()
    envelope["authority_basis"] = envelope["authority_basis"][0]
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is False
    assert decision.primary_reason == "malformed_authority_basis_shape"
    assert decision.reason_is_normative is True


def test_authority_basis_string_is_malformed() -> None:
    envelope, registry = pair()
    envelope["authority_basis"] = "grant-1"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "malformed_authority_basis_shape"


def test_competence_object_is_malformed() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["competence"] = envelope["competence"][0]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "malformed_competence_shape"


def test_jurisdiction_scope_array_is_malformed() -> None:
    envelope, registry = pair()
    envelope["jurisdiction"]["scope"] = ["lab-a"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "malformed_jurisdiction_scope_shape"


def test_qualification_scope_array_is_malformed() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["competence"][0]["scope"] = ["lab-a"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "malformed_qualification_scope_shape"


def test_empty_authority_basis_array_is_not_coerced_to_accept() -> None:
    envelope, registry = pair()
    envelope["authority_basis"] = []
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is False
    assert decision.primary_reason == "missing_domain_authority_basis"


def test_resolved_record_scopes_string_is_not_coerced() -> None:
    envelope, registry = pair()
    registry["grant-1"]["scopes"] = "lab-a"
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is False
    assert decision.primary_reason == "authority_basis_scope_mismatch"


def test_resolved_record_operations_string_is_not_coerced() -> None:
    envelope, registry = pair()
    registry["grant-1"]["operations"] = "source.read"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_operation_mismatch"


def test_resolved_record_subject_ids_string_is_not_coerced() -> None:
    envelope, registry = pair()
    registry["grant-1"]["subject_ids"] = "subj-1"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_subject_mismatch"


@pytest.mark.parametrize(
    ("field_name", "bad_value", "reason"),
    [
        ("operations", "source.read", "malformed_delegation_operations_shape"),
        ("scope", "lab-a", "malformed_delegation_scope_shape"),
        ("operations", [], "malformed_delegation_operations_shape"),
        ("scope", [], "malformed_delegation_scope_shape"),
    ],
)
def test_delegation_scalar_or_empty_not_coerced(
    field_name: str, bad_value: object, reason: str
) -> None:
    parent = make_delegation(role="parent")
    child = make_delegation(role="child")
    child[field_name] = bad_value
    decision = evaluate_delegation(parent, child)
    assert decision.accepted is False
    assert decision.primary_reason == reason
    assert decision.reason_is_normative is True


def test_non_implications_string_is_not_coerced_to_array() -> None:
    envelope, registry = pair()
    envelope["non_implications"] = "decision_mandate"
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is False
    assert decision.primary_reason == "malformed_non_implications_shape"
    assert decision.reason_is_normative is False
