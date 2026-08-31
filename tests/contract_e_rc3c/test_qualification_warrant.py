"""Qualification and warrant attacks for domains that require them."""

from __future__ import annotations

from research_scaffold_harness.contract_e_rc3c import evaluate_envelope
from tests.contract_e_rc3c.factories import pair


def test_missing_required_qualification() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["competence"] = []
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_required_qualification"


def test_qualification_type_mismatch() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["competence"][0]["type"] = "source_boundary_validator"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "qualification_type_mismatch"


def test_qualification_not_current() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["competence"][0]["current"] = False
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "qualification_not_current"


def test_qualification_subject_mismatch() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["competence"][0]["subject_id"] = "someone-else"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "qualification_subject_mismatch"


def test_qualification_scope_mismatch() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["competence"][0]["scope"] = "lab-b"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "qualification_scope_mismatch"


def test_qualification_is_not_authority_basis() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["authority_basis"] = []
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_domain_authority_basis"


def test_missing_required_warrant() -> None:
    envelope, registry = pair("numeric_relation")
    del envelope["warrant"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_required_warrant"


def test_warrant_domain_mismatch() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["warrant"]["authority_domain"] = "source_boundary"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "warrant_domain_mismatch"


def test_warrant_operation_mismatch() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["warrant"]["operation"] = "semantic.validate_absence"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "warrant_operation_mismatch"


def test_warrant_type_mismatch() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["warrant"]["type"] = "source-boundary-v1"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "warrant_type_mismatch"


def test_warrant_inapplicable() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["warrant"]["applicable"] = False
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "warrant_inapplicable"


def test_warrant_not_current() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["warrant"]["current"] = False
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "warrant_not_current"


def test_warrant_target_mismatch() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["warrant"]["target_id"] = "other-target"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "warrant_target_mismatch"


def test_warrant_target_hash_mismatch() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["warrant"]["target_hash"] = "stale-hash"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "warrant_target_hash_mismatch"


def test_warrant_not_allowed_for_source_access() -> None:
    envelope, registry = pair("source_access")
    envelope["warrant"] = {
        "type": "numeric-threshold-v1",
        "id": "w",
        "authority_domain": "source_access",
        "operation": "source.read",
        "input_artifact_ids": [],
        "target_id": "tgt-1",
        "target_hash": "hash-1",
        "applicable": True,
        "current": True,
    }
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "warrant_not_allowed_for_domain"


def test_warrant_does_not_repair_missing_basis() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["authority_basis"] = [{"type": "artifact", "id": "art-1", "current": True}]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_domain_authority_basis"


def test_decision_mandate_requires_warrant() -> None:
    envelope, registry = pair("decision_mandate")
    del envelope["warrant"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_required_warrant"
