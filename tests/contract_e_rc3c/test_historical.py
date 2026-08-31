"""Historical inspection versus new-exercise currentness recheck."""

from __future__ import annotations

from research_scaffold_harness.contract_e_rc3c import evaluate_historical
from tests.contract_e_rc3c.factories import EVALUATED_AT


def _record() -> dict:
    return {
        "evaluated_at": EVALUATED_AT,
        "authority_was_valid_at_time": True,
        "authority_basis_ids": ["grant-1"],
        "current": False,
        "revoked_at": "2026-08-01T00:00:00Z",
    }


def test_historical_inspection_accepts_later_noncurrent_record() -> None:
    decision = evaluate_historical(_record(), registry={}, mode="historical_inspection")
    assert decision.accepted is True
    assert decision.evaluation_kind == "historical"
    assert "later_currentness_does_not_rewrite_historical_fact" in decision.notes


def test_historical_inspection_does_not_rewrite_valid_at_time() -> None:
    record = _record()
    decision = evaluate_historical(record, registry={}, mode="historical_inspection")
    assert record["authority_was_valid_at_time"] is True
    assert decision.accepted is True


def test_new_exercise_from_historical_record_requires_recheck() -> None:
    decision = evaluate_historical(_record(), registry={}, mode="new_exercise")
    assert decision.accepted is False
    assert decision.primary_reason == "authority_basis_not_current"
    assert "new_exercise_requires_current_recheck" in decision.notes


def test_missing_historical_fields() -> None:
    decision = evaluate_historical({"evaluated_at": EVALUATED_AT}, registry={})
    assert decision.primary_reason == "missing_required_field"
