"""Semantic result payloads must not affect the common authority signature."""

from __future__ import annotations

import pytest

from research_scaffold_harness.contract_e_rc3c import evaluate_envelope
from tests.contract_e_rc3c.factories import pair

PAYLOADS = [
    None,
    {"status": "positive"},
    {"status": "negative"},
    {"status": "indeterminate"},
    {"success": True, "confidence": 1.0},
    {"success": False, "confidence": 0.0},
    {"authorized": True, "status": "positive", "verdict": "permit"},
]


@pytest.mark.parametrize("payload", PAYLOADS)
def test_result_metamorphism_on_positive_numeric_relation(payload: object) -> None:
    envelope, registry = pair("numeric_relation")
    if payload is not None:
        envelope["result"] = payload
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True
    assert decision.primary_reason is None


@pytest.mark.parametrize("payload", PAYLOADS)
def test_result_metamorphism_cannot_repair_missing_basis(payload: object) -> None:
    envelope, registry = pair("numeric_relation")
    envelope["authority_basis"] = []
    if payload is not None:
        envelope["result"] = payload
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is False
    assert decision.primary_reason == "missing_domain_authority_basis"


def test_positive_result_cannot_bypass_participant() -> None:
    envelope, registry = pair()
    del envelope["participant"]
    envelope["result"] = {"status": "positive", "success": True}
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_required_field"


def test_nested_authorized_in_result_is_ignored() -> None:
    envelope, registry = pair()
    envelope["result"] = {"authorized": True}
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True
