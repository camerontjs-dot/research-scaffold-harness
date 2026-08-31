from __future__ import annotations

import copy
from typing import Any

from research.contract_e_fresh_reproduction.spec_loader import load_specs
from research.contract_e_fresh_reproduction.validator import evaluate

VALID_FROM = "2026-01-01T00:00:00Z"
VALID_UNTIL = "2026-12-31T23:59:59Z"
EVALUATED_AT = "2026-06-01T00:00:00Z"


def grant_record(**overrides: Any) -> dict[str, Any]:
    record = {
        "id": "grant-1",
        "type": "grant",
        "subject_ids": ["sub-1"],
        "authority_domain": "source_access",
        "operations": ["source.read"],
        "scopes": ["org-a"],
        "target_classes": ["document"],
        "current": True,
        "valid_from": VALID_FROM,
        "valid_until": VALID_UNTIL,
    }
    record.update(overrides)
    return record


def policy_record(**overrides: Any) -> dict[str, Any]:
    record = {
        "id": "policy-1",
        "type": "policy",
        "subject_ids": ["sub-1"],
        "authority_domain": "decision_mandate",
        "operations": ["decision.make"],
        "scopes": ["org-a"],
        "target_classes": ["decision"],
        "current": True,
        "valid_from": VALID_FROM,
        "valid_until": VALID_UNTIL,
    }
    record.update(overrides)
    return record


def numeric_grant(**overrides: Any) -> dict[str, Any]:
    record = grant_record(
        id="grant-numeric",
        authority_domain="numeric_relation",
        operations=["semantic.validate_numeric"],
        target_classes=["measurement"],
    )
    record.update(overrides)
    return record


def assessment_grant(**overrides: Any) -> dict[str, Any]:
    record = grant_record(
        id="grant-assess",
        authority_domain="assessment_mandate",
        operations=["assessment.issue"],
        target_classes=["assessment"],
    )
    record.update(overrides)
    return record


def artifact_record(**overrides: Any) -> dict[str, Any]:
    record = {
        "id": "art-1",
        "type": "artifact",
        "subject_ids": ["sub-1"],
        "authority_domain": "source_access",
        "operations": ["source.read"],
        "scopes": ["org-a"],
        "target_classes": ["document"],
        "current": True,
        "valid_from": VALID_FROM,
        "valid_until": VALID_UNTIL,
    }
    record.update(overrides)
    return record


def source_envelope(**overrides: Any) -> dict[str, Any]:
    envelope = {
        "subject": {"id": "sub-1", "kind": "agent"},
        "authority_domain": "source_access",
        "operation": "source.read",
        "target": {"class": "document", "id": "doc-1", "current_hash": "hash-1"},
        "jurisdiction": {"scope": "org-a", "applicable": True, "current": True},
        "authority_basis": [{"type": "grant", "id": "grant-1", "current": True}],
        "propagation": "none",
        "non_implications": ["decision_mandate", "citation_use", "task_dispatch"],
        "evaluated_at": EVALUATED_AT,
        "participant": "evidence-bundler",
    }
    envelope.update(overrides)
    return envelope


def source_case(**overrides: Any) -> dict[str, Any]:
    grant = grant_record()
    case = {
        "exercise_kind": "new",
        "envelope": source_envelope(),
        "basis_records": {grant["id"]: grant},
    }
    case.update(overrides)
    if "envelope" in overrides:
        case["envelope"] = overrides["envelope"]
    return case


def numeric_qualification(**overrides: Any) -> dict[str, Any]:
    obj = {
        "type": "numeric_relation_validator",
        "id": "qual-1",
        "subject_id": "sub-1",
        "scope": "org-a",
        "current": True,
    }
    obj.update(overrides)
    return obj


def numeric_warrant(**overrides: Any) -> dict[str, Any]:
    obj = {
        "type": "numeric-threshold-v1",
        "id": "warrant-1",
        "authority_domain": "numeric_relation",
        "operation": "semantic.validate_numeric",
        "input_artifact_ids": ["artifact-1"],
        "target_id": "msr-1",
        "target_hash": "hash-n",
        "applicable": True,
        "current": True,
    }
    obj.update(overrides)
    return obj


def numeric_case(**overrides: Any) -> dict[str, Any]:
    grant = numeric_grant()
    envelope = source_envelope(
        authority_domain="numeric_relation",
        operation="semantic.validate_numeric",
        target={"class": "measurement", "id": "msr-1", "current_hash": "hash-n"},
        authority_basis=[{"type": "grant", "id": grant["id"], "current": True}],
        participant="numeric-validator",
        non_implications=[
            "source_boundary.validity",
            "decision_mandate",
            "citation_use",
            "task_dispatch",
        ],
    )
    case = {
        "exercise_kind": "new",
        "envelope": envelope,
        "basis_records": {grant["id"]: grant},
        "qualification": numeric_qualification(),
        "warrant": numeric_warrant(),
    }
    case.update(overrides)
    return case


def decision_warrant(**overrides: Any) -> dict[str, Any]:
    obj = {
        "type": "decision-policy-v1",
        "id": "warrant-d",
        "authority_domain": "decision_mandate",
        "operation": "decision.make",
        "input_artifact_ids": ["artifact-d"],
        "target_id": "dec-1",
        "target_hash": "hash-d",
        "applicable": True,
        "current": True,
    }
    obj.update(overrides)
    return obj


def decision_case(**overrides: Any) -> dict[str, Any]:
    policy = policy_record()
    envelope = source_envelope(
        authority_domain="decision_mandate",
        operation="decision.make",
        target={"class": "decision", "id": "dec-1", "current_hash": "hash-d"},
        authority_basis=[{"type": "policy", "id": policy["id"], "current": True}],
        participant="decision-engine-policy",
        non_implications=["epistemic_truth", "citation_use", "task_dispatch"],
    )
    case = {
        "exercise_kind": "new",
        "envelope": envelope,
        "basis_records": {policy["id"]: policy},
        "warrant": decision_warrant(),
    }
    case.update(overrides)
    return case


def assessment_case(**overrides: Any) -> dict[str, Any]:
    grant = assessment_grant()
    envelope = source_envelope(
        authority_domain="assessment_mandate",
        operation="assessment.issue",
        target={"class": "assessment", "id": "as-1", "current_hash": "hash-a"},
        authority_basis=[{"type": "grant", "id": grant["id"], "current": True}],
        participant="claim-audit-lab",
        non_implications=["source_access", "decision_mandate", "citation_use", "task_dispatch"],
    )
    case = {
        "exercise_kind": "new",
        "envelope": envelope,
        "basis_records": {grant["id"]: grant},
    }
    case.update(overrides)
    return case


def parent_grant() -> dict[str, Any]:
    return grant_record(id="parent-grant", subject_ids=["sub-root", "sub-1"])


def delegation_record(**overrides: Any) -> dict[str, Any]:
    record = {
        "id": "del-1",
        "type": "delegation",
        "subject_ids": ["sub-1"],
        "authority_domain": "source_access",
        "operations": ["source.read"],
        "scopes": ["org-a"],
        "target_classes": ["document"],
        "current": True,
        "valid_from": VALID_FROM,
        "valid_until": VALID_UNTIL,
        "parent_authority_id": "parent-grant",
        "delegator": "sub-root",
        "delegate": "sub-1",
        "scope": "org-a",
    }
    record.update(overrides)
    return record


def delegation_case(**overrides: Any) -> dict[str, Any]:
    parent = parent_grant()
    child = delegation_record()
    envelope = source_envelope(
        authority_basis=[{"type": "delegation", "id": child["id"], "current": True}],
    )
    case = {
        "exercise_kind": "new",
        "envelope": envelope,
        "basis_records": {parent["id"]: parent, child["id"]: child},
    }
    case.update(overrides)
    return case


def run(case: dict[str, Any]) -> dict[str, Any]:
    spec = load_specs()
    return evaluate(copy.deepcopy(case), spec)


def assert_accept(result: dict[str, Any]) -> None:
    assert result["outcome"] == "accept", result
    assert result["primary_reason"] == "ok", result
    assert result["violations"] == [], result


def assert_reject(
    result: dict[str, Any],
    *reasons: str,
    primary: str | None = None,
    primary_in: tuple[str, ...] | None = None,
) -> None:
    assert result["outcome"] == "reject", result
    for reason in reasons:
        assert reason in result["violations"], (reason, result)
    if primary is not None:
        assert result["primary_reason"] == primary, result
    if primary_in is not None:
        assert result["primary_reason"] in primary_in, result
