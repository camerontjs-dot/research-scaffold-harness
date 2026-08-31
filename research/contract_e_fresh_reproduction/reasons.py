"""Structured outcome and reason codes derived from the authorized specification files."""

from __future__ import annotations

OUTCOME_ACCEPT = "accept"
OUTCOME_REJECT = "reject"

OK = "ok"

# Structural
MALFORMED_ENVELOPE = "malformed_envelope"
MALFORMED_BASIS_REFERENCE = "malformed_basis_reference"
MALFORMED_BASIS_RECORD = "malformed_basis_record"
MALFORMED_WARRANT = "malformed_warrant"
MALFORMED_QUALIFICATION = "malformed_qualification"
MALFORMED_DELEGATION = "malformed_delegation"
MALFORMED_HISTORICAL_RECORD = "malformed_historical_record"
GENERIC_AUTHORIZED_BOOLEAN_FORBIDDEN = "generic_authorized_boolean_forbidden"

# Domain / operation
UNKNOWN_DOMAIN = "unknown_domain"
UNKNOWN_OPERATION = "unknown_operation"

# Participant
PARTICIPANT_NOT_DECLARED = "participant_not_declared"
PARTICIPANT_DOMAIN_NOT_ACCEPTED = "participant_domain_not_accepted"
PARTICIPANT_OPERATION_NOT_ACCEPTED = "participant_operation_not_accepted"
PARTICIPANT_EXCLUDED_RESPONSIBILITY = "participant_excluded_responsibility"
PARTICIPANT_INFERRED_FROM_SUBJECT = "participant_inferred_from_subject"

# Jurisdiction / target
JURISDICTION_INAPPLICABLE = "jurisdiction_inapplicable"
JURISDICTION_NOT_CURRENT = "jurisdiction_not_current"
STALE_TARGET = "stale_target"

# Propagation
UNKNOWN_PROPAGATION_MODE = "unknown_propagation_mode"
PROPAGATION_FORBIDDEN_FIELD = "propagation_forbidden_field"
EXPLICIT_PROPAGATION_MISSING_FIELDS = "explicit_propagation_missing_fields"

# Basis-binding reason_precedence (order is normative for primary_reason)
UNRESOLVABLE_AUTHORITY_BASIS = "unresolvable_authority_basis"
AUTHORITY_BASIS_TYPE_MISMATCH = "authority_basis_type_mismatch"
AUTHORITY_BASIS_NOT_CURRENT = "authority_basis_not_current"
AUTHORITY_BASIS_SUBJECT_MISMATCH = "authority_basis_subject_mismatch"
AUTHORITY_BASIS_DOMAIN_MISMATCH = "authority_basis_domain_mismatch"
AUTHORITY_BASIS_OPERATION_MISMATCH = "authority_basis_operation_mismatch"
AUTHORITY_BASIS_SCOPE_MISMATCH = "authority_basis_scope_mismatch"
AUTHORITY_BASIS_TARGET_CLASS_MISMATCH = "authority_basis_target_class_mismatch"
AUTHORITY_BASIS_TARGET_ID_MISMATCH = "authority_basis_target_id_mismatch"
AUTHORITY_BASIS_OUTSIDE_VALIDITY_INTERVAL = "authority_basis_outside_validity_interval"

BASIS_REASON_PRECEDENCE: tuple[str, ...] = (
    UNRESOLVABLE_AUTHORITY_BASIS,
    AUTHORITY_BASIS_TYPE_MISMATCH,
    AUTHORITY_BASIS_NOT_CURRENT,
    AUTHORITY_BASIS_SUBJECT_MISMATCH,
    AUTHORITY_BASIS_DOMAIN_MISMATCH,
    AUTHORITY_BASIS_OPERATION_MISMATCH,
    AUTHORITY_BASIS_SCOPE_MISMATCH,
    AUTHORITY_BASIS_TARGET_CLASS_MISMATCH,
    AUTHORITY_BASIS_TARGET_ID_MISMATCH,
    AUTHORITY_BASIS_OUTSIDE_VALIDITY_INTERVAL,
)

MISSING_REQUIRED_BASIS = "missing_required_basis"
SUPPORTING_ARTIFACT_NOT_AUTHORITY = "supporting_artifact_not_authority"
AUTHORITY_BASIS_TYPE_NOT_ALLOWED_FOR_DOMAIN = "authority_basis_type_not_allowed_for_domain"
POLICY_IDENTIFIER_WITHOUT_BOUND_RECORD = "policy_identifier_without_bound_record"

# Competence / warrant
MISSING_REQUIRED_QUALIFICATION = "missing_required_qualification"
QUALIFICATION_NOT_CURRENT = "qualification_not_current"
QUALIFICATION_TYPE_MISMATCH = "qualification_type_mismatch"
QUALIFICATION_SUBJECT_MISMATCH = "qualification_subject_mismatch"
QUALIFICATION_IS_NOT_AUTHORITY_BASIS = "qualification_is_not_authority_basis"
MISSING_REQUIRED_WARRANT = "missing_required_warrant"
WARRANT_NOT_ALLOWED_FOR_DOMAIN = "warrant_not_allowed_for_domain"
WARRANT_TYPE_MISMATCH = "warrant_type_mismatch"
WARRANT_DOMAIN_MISMATCH = "warrant_domain_mismatch"
WARRANT_OPERATION_MISMATCH = "warrant_operation_mismatch"
WARRANT_TARGET_MISMATCH = "warrant_target_mismatch"
WARRANT_NOT_CURRENT = "warrant_not_current"
WARRANT_INAPPLICABLE = "warrant_inapplicable"
WARRANT_IS_NOT_OPERATIONAL_PERMISSION = "warrant_is_not_operational_permission"

# Delegation
DELEGATION_PARENT_UNRESOLVABLE = "delegation_parent_unresolvable"
DELEGATION_OPERATION_ADDED = "delegation_operation_added"
DELEGATION_SCOPE_EXPANDED = "delegation_scope_expanded"
DELEGATION_EXPIRY_EXTENDED = "delegation_expiry_extended"
DELEGATION_NOT_SUBSET_OF_PARENT = "delegation_not_subset_of_parent"

# Non-implication / result / history
NON_IMPLICATION_CROSS_USE = "non_implication_cross_use"
POSITIVE_RESULT_SELF_AUTHORIZES = "positive_result_self_authorizes"
SEMANTIC_PAYLOAD_AUTHORITY_EFFECT = "semantic_payload_authority_effect"
DECISION_USED_AS_EXECUTION_PERMISSION = "decision_used_as_execution_permission"
HISTORICAL_VALIDITY_REWRITTEN = "historical_validity_rewritten"
HISTORICAL_VALIDITY_CLAIM_FALSE = "historical_validity_claim_false"

# Extra post-precedence basis reasons used in primary-reason ranking among failed refs.
POST_PRECEDENCE_BASIS_REASONS: tuple[str, ...] = (
    MALFORMED_BASIS_REFERENCE,
    MALFORMED_BASIS_RECORD,
    MALFORMED_DELEGATION,
    SUPPORTING_ARTIFACT_NOT_AUTHORITY,
    AUTHORITY_BASIS_TYPE_NOT_ALLOWED_FOR_DOMAIN,
    DELEGATION_PARENT_UNRESOLVABLE,
    DELEGATION_OPERATION_ADDED,
    DELEGATION_SCOPE_EXPANDED,
    DELEGATION_EXPIRY_EXTENDED,
    DELEGATION_NOT_SUBSET_OF_PARENT,
    MISSING_REQUIRED_BASIS,
    POLICY_IDENTIFIER_WITHOUT_BOUND_RECORD,
)


def basis_rank(reason: str) -> int:
    if reason in BASIS_REASON_PRECEDENCE:
        return BASIS_REASON_PRECEDENCE.index(reason)
    if reason in POST_PRECEDENCE_BASIS_REASONS:
        return len(BASIS_REASON_PRECEDENCE) + POST_PRECEDENCE_BASIS_REASONS.index(reason)
    return len(BASIS_REASON_PRECEDENCE) + len(POST_PRECEDENCE_BASIS_REASONS) + 50
