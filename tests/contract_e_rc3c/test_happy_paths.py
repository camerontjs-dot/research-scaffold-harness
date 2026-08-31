"""Predicted accepts: one native happy path per authority domain."""

from __future__ import annotations

import pytest

from research_scaffold_harness.contract_e_rc3c import evaluate_envelope
from tests.contract_e_rc3c.factories import DOMAIN_PROFILES, pair


@pytest.mark.parametrize("domain", list(DOMAIN_PROFILES))
def test_canonical_positive_envelope_accepted(domain: str) -> None:
    envelope, registry = pair(domain)
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True
    assert decision.primary_reason is None
    assert decision.evaluation_kind == "envelope"


def test_policy_satisfies_source_access() -> None:
    envelope, registry = pair("source_access")
    envelope["authority_basis"] = [{"type": "policy", "id": "policy-1", "current": True}]
    registry["policy-1"] = registry.pop("grant-1")
    registry["policy-1"]["id"] = "policy-1"
    registry["policy-1"]["type"] = "policy"
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True


def test_supporting_artifact_does_not_block_valid_grant() -> None:
    envelope, registry = pair("source_access")
    envelope["authority_basis"] = [
        {"type": "artifact", "id": "art-9", "current": True},
        envelope["authority_basis"][0],
    ]
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True
