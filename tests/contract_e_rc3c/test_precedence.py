"""Single primary reason follows RC3C whole-envelope precedence."""

from __future__ import annotations

from research_scaffold_harness.contract_e_rc3c import evaluate_envelope
from tests.contract_e_rc3c.factories import pair


def test_malformed_basis_beats_unknown_domain() -> None:
    envelope, registry = pair()
    envelope["authority_basis"] = {"type": "grant", "id": "grant-1", "current": True}
    envelope["authority_domain"] = "not-a-domain"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "malformed_authority_basis_shape"


def test_generic_authorized_beats_missing_field() -> None:
    envelope, registry = pair()
    envelope["authorized"] = True
    del envelope["participant"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "generic_authorized_forbidden"


def test_unknown_domain_beats_unknown_participant() -> None:
    envelope, registry = pair()
    envelope["authority_domain"] = "nope"
    envelope["participant"] = "nope-agent"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "unknown_authority_domain"


def test_jurisdiction_inapplicable_beats_basis_unresolvable() -> None:
    envelope, registry = pair()
    envelope["jurisdiction"]["applicable"] = False
    envelope["authority_basis"][0]["id"] = "missing"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "jurisdiction_inapplicable"


def test_basis_not_current_beats_missing_qualification() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["authority_basis"][0]["current"] = False
    envelope["competence"] = []
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_not_current"


def test_missing_qualification_beats_missing_warrant() -> None:
    envelope, registry = pair("numeric_relation")
    envelope["competence"] = []
    del envelope["warrant"]
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "missing_required_qualification"
