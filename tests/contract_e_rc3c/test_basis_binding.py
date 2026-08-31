"""RC3B matching rules, conferring types, and cross-domain use."""

from __future__ import annotations

from research_scaffold_harness.contract_e_rc3c import evaluate_envelope
from tests.contract_e_rc3c.factories import make_envelope, make_record, make_registry, pair


def test_unresolvable_authority_basis() -> None:
    envelope, registry = pair()
    envelope["authority_basis"][0]["id"] = "missing-id"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "unresolvable_authority_basis"


def test_type_mismatch_grant_reference_to_policy_record() -> None:
    envelope, registry = pair()
    registry["grant-1"]["type"] = "policy"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_type_mismatch"


def test_subject_mismatch() -> None:
    envelope, registry = pair()
    registry["grant-1"]["subject_ids"] = ["other-subject"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_subject_mismatch"


def test_domain_mismatch() -> None:
    envelope, registry = pair("citation_use")
    registry["grant-1"]["authority_domain"] = "assessment_mandate"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_domain_mismatch"


def test_assessment_mandate_used_as_citation_use() -> None:
    envelope = make_envelope(domain="citation_use")
    record = make_record(domain="assessment_mandate")
    record["id"] = "grant-1"
    record["type"] = "grant"
    decision = evaluate_envelope(envelope, make_registry(record))
    assert decision.accepted is False
    assert decision.primary_reason == "authority_basis_domain_mismatch"


def test_decision_mandate_used_as_task_dispatch() -> None:
    envelope = make_envelope(domain="task_dispatch")
    record = make_record(domain="decision_mandate", basis_type="policy")
    record["id"] = "grant-1"
    record["type"] = "grant"
    envelope["authority_basis"][0]["type"] = "grant"
    decision = evaluate_envelope(envelope, make_registry(record))
    assert decision.primary_reason == "authority_basis_domain_mismatch"


def test_operation_mismatch() -> None:
    envelope, registry = pair()
    registry["grant-1"]["operations"] = ["task.dispatch"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_operation_mismatch"


def test_scope_mismatch() -> None:
    envelope, registry = pair()
    registry["grant-1"]["scopes"] = ["lab-b"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_scope_mismatch"


def test_target_class_mismatch() -> None:
    envelope, registry = pair()
    registry["grant-1"]["target_classes"] = ["other-class"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_target_class_mismatch"


def test_target_id_mismatch_when_record_target_ids_nonempty() -> None:
    envelope, registry = pair()
    registry["grant-1"]["target_ids"] = ["other-target"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_target_id_mismatch"


def test_empty_target_ids_does_not_constrain_target() -> None:
    envelope, registry = pair()
    registry["grant-1"]["target_ids"] = []
    envelope["target"]["id"] = "unlisted"
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True


def test_absent_target_ids_does_not_constrain_target() -> None:
    envelope, registry = pair()
    del registry["grant-1"]["target_ids"]
    envelope["target"]["id"] = "unlisted"
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True


def test_artifact_alone_never_satisfies() -> None:
    envelope, registry = pair()
    envelope["authority_basis"] = [{"type": "artifact", "id": "art-1", "current": True}]
    registry["art-1"] = make_record(
        domain="source_access", record_id="art-1", basis_type="artifact"
    )
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_domain_authority_basis"


def test_credential_alone_never_satisfies() -> None:
    envelope, registry = pair()
    envelope["authority_basis"] = [{"type": "credential", "id": "cred-1", "current": True}]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_domain_authority_basis"


def test_receipt_alone_never_satisfies() -> None:
    envelope, registry = pair()
    envelope["authority_basis"] = [{"type": "receipt", "id": "rcp-1", "current": True}]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_domain_authority_basis"


def test_grant_does_not_satisfy_decision_mandate() -> None:
    envelope, registry = pair("decision_mandate")
    envelope["authority_basis"] = [{"type": "grant", "id": "grant-1", "current": True}]
    grant = make_record(domain="decision_mandate", record_id="grant-1", basis_type="grant")
    decision = evaluate_envelope(envelope, make_registry(grant))
    assert decision.accepted is False
    assert decision.primary_reason == "missing_domain_authority_basis"


def test_delegation_alone_does_not_satisfy_domain_any_of() -> None:
    envelope, registry = pair()
    envelope["authority_basis"] = [{"type": "delegation", "id": "del-1", "current": True}]
    record = make_record(domain="source_access", record_id="del-1", basis_type="delegation")
    decision = evaluate_envelope(envelope, make_registry(record))
    assert decision.primary_reason == "missing_domain_authority_basis"


def test_unresolvable_precedes_subject_mismatch_across_refs() -> None:
    envelope, registry = pair()
    envelope["authority_basis"] = [
        {"type": "grant", "id": "grant-1", "current": True},
        {"type": "policy", "id": "missing-policy", "current": True},
    ]
    registry["grant-1"]["subject_ids"] = ["nope"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "unresolvable_authority_basis"


def test_current_policy_identifier_without_record_is_not_authority() -> None:
    envelope, registry = pair("decision_mandate")
    envelope["authority_basis"] = [
        {"type": "policy", "id": "policy-does-not-exist", "current": True}
    ]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "unresolvable_authority_basis"


def test_incomplete_resolved_record_is_unresolvable() -> None:
    envelope, registry = pair()
    del registry["grant-1"]["operations"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "unresolvable_authority_basis"
