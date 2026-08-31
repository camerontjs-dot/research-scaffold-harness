"""Propagation modes, never-implicit fields, and relisted reestablishment."""

from __future__ import annotations

from research_scaffold_harness.contract_e_rc3c import evaluate_envelope, evaluate_propagation
from tests.contract_e_rc3c.factories import pair


def test_unknown_propagation_mode() -> None:
    envelope, registry = pair()
    envelope["propagation"] = "telepathy"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "unknown_propagation_mode"


def test_none_mode_object_accepted() -> None:
    envelope, registry = pair()
    envelope["propagation"] = {"mode": "none"}
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True


def test_identity_provenance_only_allowed_fields() -> None:
    envelope, registry = pair()
    envelope["propagation"] = {
        "mode": "identity_provenance_only",
        "fields": ["source_id", "content_hash"],
    }
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True


def test_explicit_decision_mandate_propagation_requires_reestablishment() -> None:
    envelope, registry = pair()
    envelope["propagation"] = {
        "mode": "explicit",
        "fields": ["decision_mandate"],
    }
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is False
    assert decision.primary_reason == "authority_requires_reestablishment"
    assert decision.reason_is_normative is True


def test_explicit_task_dispatch_propagation_requires_reestablishment() -> None:
    envelope, registry = pair()
    envelope["propagation"] = {"mode": "explicit", "fields": ["task_dispatch"]}
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_requires_reestablishment"


def test_separately_reauthorized_explicit_decision_mandate_accepted() -> None:
    envelope, registry = pair()
    envelope["propagation"] = {
        "mode": "explicit",
        "fields": ["decision_mandate"],
        "separately_reauthorized": True,
    }
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True


def test_none_mode_with_fields_forbidden() -> None:
    envelope, registry = pair()
    envelope["propagation"] = {"mode": "none", "fields": ["source_id"]}
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is False
    assert decision.primary_reason == "propagation_forbidden_fields"
    assert decision.reason_is_normative is False


def test_identity_mode_cannot_carry_competence() -> None:
    envelope, registry = pair()
    envelope["propagation"] = {
        "mode": "identity_provenance_only",
        "fields": ["source_id", "competence"],
    }
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "propagation_forbidden_fields"


def test_propagation_request_surface_none() -> None:
    decision = evaluate_propagation({"mode": "none"})
    assert decision.accepted is True
    assert decision.evaluation_kind == "propagation"


def test_propagation_request_unknown_mode() -> None:
    decision = evaluate_propagation({"mode": "broadcast"})
    assert decision.primary_reason == "unknown_propagation_mode"
