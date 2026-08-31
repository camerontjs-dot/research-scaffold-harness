"""Closed tables copied from the five authorized RC3C blobs.

Blob identities (git SHA-1):
- SPEC-CANDIDATE.json 9c1090335d87eb5e4885a755542923b453c45317
- SPEC-SHAPES.json c3f293430ae6ddb87523d83ea6e5380b8b832136
- SPEC-PARTICIPANT-BOUNDARY.json 8b1d292a240300388949d502e7b656e7a23a0b8e
- BASIS-BINDING-SPEC.json 63c952c9c28f1be2173e69c79976c7dfe5880c10
- RC3C-SPEC.json f05feac88128fd693cca2fb25a0b2951654377eb
"""

from __future__ import annotations

AUTHORITY_BASIS_TYPES = (
    "grant",
    "policy",
    "credential",
    "receipt",
    "artifact",
    "delegation",
)

AUTHORITY_CONFERING_TYPES = frozenset({"grant", "policy", "delegation"})
SUPPORTING_BASIS_TYPES = frozenset({"credential", "receipt", "artifact"})

ENVELOPE_REQUIRED_KEYS = (
    "subject",
    "authority_domain",
    "operation",
    "target",
    "jurisdiction",
    "authority_basis",
    "propagation",
    "non_implications",
    "evaluated_at",
    "participant",
    "competence",
)

SUBJECT_REQUIRED = ("id", "kind")
TARGET_REQUIRED = ("class", "id", "current_hash")
JURISDICTION_REQUIRED = ("scope", "applicable", "current")
AUTHORITY_REFERENCE_REQUIRED = ("type", "id", "current")
QUALIFICATION_REQUIRED = ("type", "id", "subject_id", "scope", "current")
WARRANT_REQUIRED = (
    "type",
    "id",
    "authority_domain",
    "operation",
    "input_artifact_ids",
    "target_id",
    "target_hash",
    "applicable",
    "current",
)
RESOLVED_RECORD_REQUIRED = (
    "id",
    "type",
    "subject_ids",
    "authority_domain",
    "operations",
    "scopes",
    "target_classes",
    "current",
    "valid_from",
    "valid_until",
)
DELEGATION_REQUIRED = (
    "id",
    "delegator",
    "delegate",
    "authority_domain",
    "operations",
    "scope",
    "current",
    "parent_authority_id",
)
HISTORICAL_REQUIRED = ("evaluated_at", "authority_was_valid_at_time", "authority_basis_ids")

DOMAINS: dict[str, dict] = {
    "source_access": {
        "kind": "operational",
        "operations": ("source.read",),
        "competence_required": False,
        "warrant_allowed": False,
        "accepted_qualification_types": (),
        "accepted_warrant_types": (),
    },
    "evidence_admission": {
        "kind": "operational",
        "operations": ("evidence.admit_passage",),
        "competence_required": False,
        "warrant_allowed": False,
        "accepted_qualification_types": (),
        "accepted_warrant_types": (),
    },
    "assessment_mandate": {
        "kind": "mandate",
        "operations": ("assessment.issue",),
        "competence_required": False,
        "warrant_allowed": False,
        "accepted_qualification_types": (),
        "accepted_warrant_types": (),
    },
    "numeric_relation": {
        "kind": "informational",
        "operations": ("semantic.validate_numeric",),
        "competence_required": True,
        "warrant_allowed": True,
        "accepted_qualification_types": ("numeric_relation_validator",),
        "accepted_warrant_types": ("numeric-threshold-v1",),
    },
    "source_boundary": {
        "kind": "informational",
        "operations": ("semantic.validate_absence",),
        "competence_required": True,
        "warrant_allowed": True,
        "accepted_qualification_types": ("source_boundary_validator",),
        "accepted_warrant_types": ("source-boundary-v1",),
    },
    "decision_mandate": {
        "kind": "mandate",
        "operations": ("decision.make",),
        "competence_required": False,
        "warrant_allowed": True,
        "accepted_qualification_types": (),
        "accepted_warrant_types": ("decision-policy-v1",),
    },
    "citation_use": {
        "kind": "operational",
        "operations": ("citation.use",),
        "competence_required": False,
        "warrant_allowed": False,
        "accepted_qualification_types": (),
        "accepted_warrant_types": (),
    },
    "task_dispatch": {
        "kind": "operational",
        "operations": ("task.dispatch",),
        "competence_required": False,
        "warrant_allowed": False,
        "accepted_qualification_types": (),
        "accepted_warrant_types": (),
    },
    "outcome_verification": {
        "kind": "informational",
        "operations": ("outcome.verify",),
        "competence_required": True,
        "warrant_allowed": True,
        "accepted_qualification_types": ("outcome_verifier",),
        "accepted_warrant_types": ("postcondition-observation-v1",),
    },
}

DOMAIN_BASIS_REQUIREMENTS: dict[str, dict] = {
    "source_access": {"any_of": ("grant", "policy")},
    "evidence_admission": {"any_of": ("grant", "policy")},
    "assessment_mandate": {"any_of": ("grant", "policy")},
    "numeric_relation": {
        "any_of": ("grant", "policy"),
        "qualification": "numeric_relation_validator",
        "warrant": "numeric-threshold-v1",
    },
    "source_boundary": {
        "any_of": ("grant", "policy"),
        "qualification": "source_boundary_validator",
        "warrant": "source-boundary-v1",
    },
    "decision_mandate": {"any_of": ("policy",), "warrant": "decision-policy-v1"},
    "citation_use": {"any_of": ("grant", "policy")},
    "task_dispatch": {"any_of": ("grant", "policy")},
    "outcome_verification": {
        "any_of": ("grant", "policy"),
        "qualification": "outcome_verifier",
        "warrant": "postcondition-observation-v1",
    },
}

PARTICIPANTS: dict[str, dict] = {
    "evidence-bundler": {
        "accepted_domains": ("source_access", "evidence_admission"),
        "accepted_operations": ("source.read", "evidence.admit_passage"),
    },
    "claim-audit-lab": {
        "accepted_domains": ("assessment_mandate",),
        "accepted_operations": ("assessment.issue",),
    },
    "numeric-validator": {
        "accepted_domains": ("numeric_relation",),
        "accepted_operations": ("semantic.validate_numeric",),
    },
    "source-boundary-validator": {
        "accepted_domains": ("source_boundary",),
        "accepted_operations": ("semantic.validate_absence",),
    },
    "decision-engine-policy": {
        "accepted_domains": ("decision_mandate",),
        "accepted_operations": ("decision.make",),
    },
    "citation-agent": {
        "accepted_domains": ("citation_use",),
        "accepted_operations": ("citation.use",),
    },
    "task-agent": {
        "accepted_domains": ("task_dispatch",),
        "accepted_operations": ("task.dispatch",),
    },
    "outcome-verifier": {
        "accepted_domains": ("outcome_verification",),
        "accepted_operations": ("outcome.verify",),
    },
}

PROPAGATION_MODES = ("none", "identity_provenance_only", "explicit")

IDENTITY_PROVENANCE_FIELDS = frozenset(
    {
        "source_id",
        "artifact_id",
        "content_hash",
        "producer_id",
        "policy_id",
        "policy_version",
    }
)

NEVER_IMPLICIT_FIELDS = frozenset(
    {
        "competence",
        "authority_domain",
        "jurisdiction",
        "warrant",
        "semantic_validity",
        "decision_mandate",
        "citation_use",
        "task_dispatch",
        "outcome_verification",
    }
)

REESTABLISHMENT_FIELDS = frozenset({"decision_mandate", "task_dispatch"})

WHOLE_ENVELOPE_PRECEDENCE = (
    "malformed_authority_basis_shape",
    "malformed_competence_shape",
    "malformed_jurisdiction_scope_shape",
    "malformed_qualification_scope_shape",
    "generic_authorized_forbidden",
    "missing_required_field",
    "unknown_authority_domain",
    "domain_operation_mismatch",
    "unknown_participant",
    "participant_domain_out_of_scope",
    "participant_operation_out_of_scope",
    "jurisdiction_inapplicable",
    "jurisdiction_not_current",
    "unresolvable_authority_basis",
    "authority_basis_type_mismatch",
    "authority_basis_not_current",
    "authority_basis_subject_mismatch",
    "authority_basis_domain_mismatch",
    "authority_basis_operation_mismatch",
    "authority_basis_scope_mismatch",
    "authority_basis_target_class_mismatch",
    "authority_basis_target_id_mismatch",
    "authority_basis_outside_validity_interval",
    "missing_domain_authority_basis",
    "missing_required_qualification",
    "qualification_type_mismatch",
    "qualification_not_current",
    "qualification_subject_mismatch",
    "qualification_scope_mismatch",
    "missing_required_warrant",
    "warrant_domain_mismatch",
    "warrant_operation_mismatch",
    "warrant_type_mismatch",
    "warrant_inapplicable",
    "warrant_not_current",
    "warrant_target_mismatch",
    "warrant_target_hash_mismatch",
    "warrant_not_allowed_for_domain",
    "unknown_propagation_mode",
)

RELISTED_REASONS = (
    "authority_requires_reestablishment",
    "delegation_operation_amplification",
    "delegation_scope_amplification",
    "delegation_expiry_amplification",
)

MALFORMED_DELEGATION_REASONS = (
    "malformed_delegation_operations_shape",
    "malformed_delegation_scope_shape",
)

LOCAL_REASONS = (
    "malformed_non_implications_shape",
    "unparseable_datetime",
    "propagation_forbidden_fields",
)

NORMATIVE_REASONS = frozenset(
    WHOLE_ENVELOPE_PRECEDENCE + RELISTED_REASONS + MALFORMED_DELEGATION_REASONS
)

PRECEDENCE_INDEX = {reason: index for index, reason in enumerate(WHOLE_ENVELOPE_PRECEDENCE)}

MODES = ("new_exercise", "historical_inspection")
