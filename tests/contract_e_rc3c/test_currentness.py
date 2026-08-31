"""RC3C currentness conjunction, inclusive validity, and revocation bounds."""

from __future__ import annotations

import pytest

from research_scaffold_harness.contract_e_rc3c import evaluate_envelope
from tests.contract_e_rc3c.factories import EVALUATED_AT, pair


def test_reference_false_rejects_even_when_record_current() -> None:
    envelope, registry = pair()
    envelope["authority_basis"][0]["current"] = False
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is False
    assert decision.primary_reason == "authority_basis_not_current"
    assert registry["grant-1"]["current"] is True


def test_record_false_rejects_even_when_reference_current() -> None:
    envelope, registry = pair()
    registry["grant-1"]["current"] = False
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_not_current"


def test_reference_true_cannot_override_noncurrent_record() -> None:
    envelope, registry = pair()
    envelope["authority_basis"][0]["current"] = True
    registry["grant-1"]["current"] = False
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_not_current"


@pytest.mark.parametrize(
    "evaluated_at",
    ["2026-01-01T00:00:00Z", "2026-12-31T23:59:59Z", EVALUATED_AT],
)
def test_inclusive_validity_bounds_accept(evaluated_at: str) -> None:
    envelope, registry = pair()
    envelope["evaluated_at"] = evaluated_at
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True, decision.to_dict()


@pytest.mark.parametrize(
    "evaluated_at",
    ["2025-12-31T23:59:59Z", "2027-01-01T00:00:00Z"],
)
def test_outside_validity_interval_rejects(evaluated_at: str) -> None:
    envelope, registry = pair()
    envelope["evaluated_at"] = evaluated_at
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_outside_validity_interval"


def test_revoked_at_equal_evaluated_at_rejects() -> None:
    envelope, registry = pair()
    registry["grant-1"]["revoked_at"] = EVALUATED_AT
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_not_current"


def test_revoked_at_before_evaluated_at_rejects() -> None:
    envelope, registry = pair()
    registry["grant-1"]["revoked_at"] = "2026-06-15T11:59:59Z"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_not_current"


def test_revoked_at_after_evaluated_at_accepts() -> None:
    envelope, registry = pair()
    registry["grant-1"]["revoked_at"] = "2026-06-15T12:00:01Z"
    decision = evaluate_envelope(envelope, registry)
    assert decision.accepted is True


def test_not_current_precedes_outside_interval() -> None:
    envelope, registry = pair()
    registry["grant-1"]["current"] = False
    envelope["evaluated_at"] = "2020-01-01T00:00:00Z"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_not_current"


def test_equal_revocation_and_valid_until_is_not_current() -> None:
    envelope, registry = pair()
    envelope["evaluated_at"] = "2026-12-31T23:59:59Z"
    registry["grant-1"]["revoked_at"] = "2026-12-31T23:59:59Z"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_not_current"


def test_non_boolean_reference_current_fails_closed() -> None:
    envelope, registry = pair()
    envelope["authority_basis"][0]["current"] = "true"
    decision = evaluate_envelope(envelope, registry)
    assert decision.primary_reason == "authority_basis_not_current"
