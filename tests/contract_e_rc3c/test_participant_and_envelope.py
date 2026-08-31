"""Participant boundary, required fields, generic authorized, unknown domain."""

from __future__ import annotations

from research_scaffold_harness.contract_e_rc3c import evaluate_envelope
from tests.contract_e_rc3c.factories import pair


def test_missing_participant() -> None:
    envelope, registry = pair()
    del envelope["participant"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_required_field"


def test_missing_competence_key() -> None:
    envelope, registry = pair()
    del envelope["competence"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_required_field"


def test_unknown_participant() -> None:
    envelope, registry = pair()
    envelope["participant"] = "not-a-declared-participant"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "unknown_participant"


def test_participant_domain_out_of_scope() -> None:
    envelope, registry = pair("citation_use")
    envelope["participant"] = "evidence-bundler"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "participant_domain_out_of_scope"


def test_participant_not_inferred_from_subject() -> None:
    envelope, registry = pair("citation_use")
    envelope["subject"] = {"id": "evidence-bundler", "kind": "participant"}
    envelope["participant"] = "not-a-declared-participant"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "unknown_participant"


def test_unknown_authority_domain() -> None:
    envelope, registry = pair()
    envelope["authority_domain"] = "epistemic_truth"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "unknown_authority_domain"


def test_domain_operation_mismatch() -> None:
    envelope, registry = pair()
    envelope["operation"] = "citation.use"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "domain_operation_mismatch"


def test_jurisdiction_inapplicable() -> None:
    envelope, registry = pair()
    envelope["jurisdiction"]["applicable"] = False
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "jurisdiction_inapplicable"


def test_jurisdiction_not_current() -> None:
    envelope, registry = pair()
    envelope["jurisdiction"]["current"] = False
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "jurisdiction_not_current"


def test_generic_authorized_boolean_forbidden() -> None:
    envelope, registry = pair()
    envelope["authorized"] = True
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "generic_authorized_forbidden"
    assert decision.reason_is_normative is True


def test_generic_authorized_false_still_forbidden() -> None:
    envelope, registry = pair()
    envelope["authorized"] = False
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "generic_authorized_forbidden"


def test_missing_subject_id() -> None:
    envelope, registry = pair()
    del envelope["subject"]["id"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_required_field"
