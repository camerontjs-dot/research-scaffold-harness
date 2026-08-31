"""Canonical native envelopes and records for self-designed RC3C tests."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

EVALUATED_AT = "2026-06-15T12:00:00Z"
VALID_FROM = "2026-01-01T00:00:00Z"
VALID_UNTIL = "2026-12-31T23:59:59Z"

DOMAIN_PROFILES: dict[str, dict[str, Any]] = {
    "source_access": {
        "participant": "evidence-bundler",
        "operation": "source.read",
        "basis_type": "grant",
        "target_class": "source",
        "qualification_type": None,
        "warrant_type": None,
    },
    "evidence_admission": {
        "participant": "evidence-bundler",
        "operation": "evidence.admit_passage",
        "basis_type": "grant",
        "target_class": "passage",
        "qualification_type": None,
        "warrant_type": None,
    },
    "assessment_mandate": {
        "participant": "claim-audit-lab",
        "operation": "assessment.issue",
        "basis_type": "grant",
        "target_class": "assessment",
        "qualification_type": None,
        "warrant_type": None,
    },
    "numeric_relation": {
        "participant": "numeric-validator",
        "operation": "semantic.validate_numeric",
        "basis_type": "grant",
        "target_class": "claim",
        "qualification_type": "numeric_relation_validator",
        "warrant_type": "numeric-threshold-v1",
    },
    "source_boundary": {
        "participant": "source-boundary-validator",
        "operation": "semantic.validate_absence",
        "basis_type": "grant",
        "target_class": "source_packet",
        "qualification_type": "source_boundary_validator",
        "warrant_type": "source-boundary-v1",
    },
    "decision_mandate": {
        "participant": "decision-engine-policy",
        "operation": "decision.make",
        "basis_type": "policy",
        "target_class": "decision",
        "qualification_type": None,
        "warrant_type": "decision-policy-v1",
    },
    "citation_use": {
        "participant": "citation-agent",
        "operation": "citation.use",
        "basis_type": "grant",
        "target_class": "citation",
        "qualification_type": None,
        "warrant_type": None,
    },
    "task_dispatch": {
        "participant": "task-agent",
        "operation": "task.dispatch",
        "basis_type": "grant",
        "target_class": "task",
        "qualification_type": None,
        "warrant_type": None,
    },
    "outcome_verification": {
        "participant": "outcome-verifier",
        "operation": "outcome.verify",
        "basis_type": "grant",
        "target_class": "outcome",
        "qualification_type": "outcome_verifier",
        "warrant_type": "postcondition-observation-v1",
    },
}


def make_record(
    *,
    domain: str = "source_access",
    record_id: str | None = None,
    basis_type: str | None = None,
    subject_id: str = "subj-1",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    profile = DOMAIN_PROFILES[domain]
    basis_type = basis_type or profile["basis_type"]
    record_id = record_id or f"{basis_type}-1"
    record: dict[str, Any] = {
        "id": record_id,
        "type": basis_type,
        "subject_ids": [subject_id],
        "authority_domain": domain,
        "operations": [profile["operation"]],
        "scopes": ["lab-a"],
        "target_classes": [profile["target_class"]],
        "target_ids": ["tgt-1"],
        "current": True,
        "valid_from": VALID_FROM,
        "valid_until": VALID_UNTIL,
    }
    if extra:
        record.update(extra)
    return record


def make_envelope(
    *,
    domain: str = "source_access",
    extra: dict[str, Any] | None = None,
    omit: tuple[str, ...] = (),
) -> dict[str, Any]:
    profile = DOMAIN_PROFILES[domain]
    basis_type = profile["basis_type"]
    envelope: dict[str, Any] = {
        "subject": {"id": "subj-1", "kind": "agent"},
        "participant": profile["participant"],
        "authority_domain": domain,
        "operation": profile["operation"],
        "target": {
            "class": profile["target_class"],
            "id": "tgt-1",
            "current_hash": "hash-1",
        },
        "jurisdiction": {"scope": "lab-a", "applicable": True, "current": True},
        "authority_basis": [{"type": basis_type, "id": f"{basis_type}-1", "current": True}],
        "competence": [],
        "propagation": "none",
        "non_implications": [],
        "evaluated_at": EVALUATED_AT,
    }
    if profile["qualification_type"]:
        envelope["competence"] = [
            {
                "type": profile["qualification_type"],
                "id": "qual-1",
                "subject_id": "subj-1",
                "scope": "lab-a",
                "current": True,
            }
        ]
    if profile["warrant_type"]:
        envelope["warrant"] = {
            "type": profile["warrant_type"],
            "id": "warrant-1",
            "authority_domain": domain,
            "operation": profile["operation"],
            "input_artifact_ids": ["art-1"],
            "target_id": "tgt-1",
            "target_hash": "hash-1",
            "applicable": True,
            "current": True,
        }
    if extra:
        envelope.update(extra)
    for key in omit:
        envelope.pop(key, None)
    return envelope


def make_registry(*records: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["id"]: deepcopy(record) for record in records}


def pair(domain: str = "source_access") -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    envelope = make_envelope(domain=domain)
    record = make_record(domain=domain)
    return envelope, make_registry(record)


def make_delegation(
    *,
    role: str = "parent",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "id": "del-parent" if role == "parent" else "del-child",
        "delegator": "alice",
        "delegate": "bob" if role == "parent" else "carol",
        "authority_domain": "source_access",
        "operations": ["source.read"],
        "scope": ["lab-a"],
        "current": True,
        "parent_authority_id": "grant-root" if role == "parent" else "del-parent",
        "valid_until": VALID_UNTIL,
    }
    if extra:
        body.update(extra)
    return body
