"""Non-implication invariants and registry/resolver shapes."""

from __future__ import annotations

from research_scaffold_harness.contract_e_rc3c import evaluate, evaluate_envelope
from tests.contract_e_rc3c.factories import make_record, pair


def test_competence_does_not_imply_jurisdiction() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["jurisdiction"]["applicable"] = False
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "jurisdiction_inapplicable"


def test_jurisdiction_does_not_imply_competence() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["competence"] = []
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_required_qualification"


def test_registry_as_records_list() -> None:
    envelope, registry = pair()
    decision = evaluate_envelope(envelope, {"records": list(registry.values())})
    assert decision.accepted is True


def test_registry_as_list() -> None:
    envelope, registry = pair()
    decision = evaluate_envelope(envelope, list(registry.values()))
    assert decision.accepted is True


def test_unified_evaluate_dispatcher() -> None:
    envelope, registry = pair("source_boundary")
    decision = evaluate({"kind": "envelope", "envelope": envelope, "registry": registry})
    assert decision.accepted is True


def test_unknown_evaluation_kind() -> None:
    decision = evaluate({"kind": "telepathy", "envelope": {}})
    assert decision.accepted is False


def test_policy_id_alone_without_bound_matching_record() -> None:
    envelope, _registry = pair("decision_mandate")
    # Keep the identifier but bind it to a record whose domain/operation do not match.
    other = make_record(domain="source_access", record_id="policy-1", basis_type="policy")
    decision = evaluate_envelope(envelope, {"policy-1": other})
    assert decision.accepted is False
    assert decision.primary_reason == "authority_basis_domain_mismatch"
