"""Pre-reveal adversarial tests preregistered in PREREGISTRATION.md."""

from __future__ import annotations

import copy

from research.contract_e_fresh_reproduction.tests.helpers import (
    artifact_record,
    assert_accept,
    assert_reject,
    assessment_case,
    decision_case,
    delegation_case,
    grant_record,
    numeric_case,
    numeric_qualification,
    numeric_warrant,
    policy_record,
    run,
    source_case,
)


def test_t00_source_access_happy_path_accepts() -> None:
    assert_accept(run(source_case()))


def test_t01_subject_principal_substitution() -> None:
    case = source_case()
    case["envelope"]["subject"]["id"] = "sub-2"
    assert_reject(run(case), "authority_basis_subject_mismatch", primary="authority_basis_subject_mismatch")


def test_t02_authority_domain_substitution() -> None:
    case = source_case()
    case["basis_records"]["grant-1"]["authority_domain"] = "evidence_admission"
    assert_reject(run(case), "authority_basis_domain_mismatch", primary="authority_basis_domain_mismatch")


def test_t03_typed_operation_substitution_unknown_for_domain() -> None:
    case = source_case()
    case["envelope"]["operation"] = "evidence.admit_passage"
    assert_reject(run(case), "unknown_operation", primary="unknown_operation")


def test_t03b_typed_operation_substitution_record_operations() -> None:
    case = source_case()
    case["basis_records"]["grant-1"]["operations"] = ["evidence.admit_passage"]
    assert_reject(
        run(case), "authority_basis_operation_mismatch", primary="authority_basis_operation_mismatch"
    )


def test_t04_scope_substitution() -> None:
    case = source_case()
    case["envelope"]["jurisdiction"]["scope"] = "org-b"
    assert_reject(run(case), "authority_basis_scope_mismatch", primary="authority_basis_scope_mismatch")


def test_t05_target_class_substitution() -> None:
    case = source_case()
    case["envelope"]["target"]["class"] = "passage"
    assert_reject(
        run(case), "authority_basis_target_class_mismatch", primary="authority_basis_target_class_mismatch"
    )


def test_t06_exact_target_substitution() -> None:
    case = source_case()
    case["basis_records"]["grant-1"]["target_ids"] = ["tgt-1"]
    case["envelope"]["target"]["id"] = "tgt-2"
    assert_reject(run(case), "authority_basis_target_id_mismatch", primary="authority_basis_target_id_mismatch")


def test_t06b_absent_target_ids_unbound() -> None:
    case = source_case()
    case["envelope"]["target"]["id"] = "tgt-2"
    assert_accept(run(case))


def test_t07_stale_record_rejected_for_new_exercise() -> None:
    case = source_case()
    case["basis_records"]["grant-1"]["current"] = False
    assert_reject(run(case), "authority_basis_not_current", primary="authority_basis_not_current")


def test_t07b_historical_accepts_later_noncurrent_record() -> None:
    case = source_case()
    case["exercise_kind"] = "historical"
    case["basis_records"]["grant-1"]["current"] = False
    case["historical_record"] = {
        "evaluated_at": case["envelope"]["evaluated_at"],
        "authority_was_valid_at_time": True,
        "authority_basis_ids": ["grant-1"],
    }
    assert_accept(run(case))


def test_t08_outside_validity_interval() -> None:
    case = source_case()
    case["envelope"]["evaluated_at"] = "2027-01-01T00:00:00Z"
    assert_reject(
        run(case),
        "authority_basis_outside_validity_interval",
        primary="authority_basis_outside_validity_interval",
    )


def test_t08b_later_revocation_must_not_rewrite_history() -> None:
    case = source_case()
    case["exercise_kind"] = "historical"
    case["basis_records"]["grant-1"]["current"] = False
    case["basis_records"]["grant-1"]["revoked_at"] = "2026-07-01T00:00:00Z"
    case["assert_later_revocation_rewrites_history"] = True
    case["historical_record"] = {
        "evaluated_at": "2026-06-01T00:00:00Z",
        "authority_was_valid_at_time": True,
        "authority_basis_ids": ["grant-1"],
        "later_revocation_rewrites_authority_was_valid_at_time": True,
    }
    assert_reject(run(case), "historical_validity_rewritten")


def test_t09_authority_reference_type_mismatch() -> None:
    case = source_case()
    case["envelope"]["authority_basis"] = [{"type": "grant", "id": "policy-1", "current": True}]
    rec = policy_record(id="policy-1", authority_domain="source_access", operations=["source.read"])
    case["basis_records"] = {rec["id"]: rec}
    assert_reject(run(case), "authority_basis_type_mismatch", primary="authority_basis_type_mismatch")


def test_t10_unresolvable_authority_basis() -> None:
    case = source_case()
    case["envelope"]["authority_basis"] = [{"type": "grant", "id": "missing-grant", "current": True}]
    assert_reject(run(case), "unresolvable_authority_basis", primary="unresolvable_authority_basis")


def test_t11_competence_present_mandate_absent() -> None:
    case = decision_case()
    case["envelope"]["authority_basis"] = []
    case["qualification"] = numeric_qualification()
    result = run(case)
    assert_reject(result, "missing_required_basis")
    assert "ok" != result["primary_reason"]


def test_t11b_credential_is_not_authority() -> None:
    case = numeric_case()
    cred = grant_record(
        id="cred-1",
        type="credential",
        authority_domain="numeric_relation",
        operations=["semantic.validate_numeric"],
        target_classes=["measurement"],
    )
    case["envelope"]["authority_basis"] = [{"type": "credential", "id": "cred-1", "current": True}]
    case["basis_records"] = {cred["id"]: cred}
    assert_reject(run(case), "supporting_artifact_not_authority")


def test_t12_mandate_present_required_competence_absent() -> None:
    case = numeric_case()
    del case["qualification"]
    assert_reject(
        run(case), "missing_required_qualification", primary="missing_required_qualification"
    )


def test_t13_valid_warrant_missing_mandate() -> None:
    case = numeric_case()
    case["envelope"]["authority_basis"] = []
    result = run(case)
    assert_reject(result, "missing_required_basis")
    assert result["primary_reason"] != "ok"


def test_t13b_decision_warrant_with_grant_not_policy() -> None:
    case = decision_case()
    grant = grant_record(
        id="grant-decision",
        authority_domain="decision_mandate",
        operations=["decision.make"],
        target_classes=["decision"],
    )
    case["envelope"]["authority_basis"] = [{"type": "grant", "id": grant["id"], "current": True}]
    case["basis_records"] = {grant["id"]: grant}
    assert_reject(run(case), "authority_basis_type_not_allowed_for_domain")


def test_t14_valid_mandate_missing_required_warrant() -> None:
    case = decision_case()
    del case["warrant"]
    assert_reject(run(case), "missing_required_warrant", primary="missing_required_warrant")


def test_t14b_wrong_warrant_type_for_decision() -> None:
    case = decision_case()
    case["warrant"] = numeric_warrant(
        authority_domain="decision_mandate",
        operation="decision.make",
        target_id="dec-1",
        target_hash="hash-d",
    )
    assert_reject(run(case), "warrant_type_mismatch")


def test_t15_result_payload_mutation_does_not_affect_accept() -> None:
    base = source_case()
    fail = copy.deepcopy(base)
    fail["result"] = {"status": "fail", "success": False, "confidence": 0, "body": "no"}
    ok = copy.deepcopy(base)
    ok["result"] = {"status": "pass", "success": True, "confidence": 1, "body": "yes-mutated"}
    r_fail = run(fail)
    r_ok = run(ok)
    assert_accept(r_fail)
    assert_accept(r_ok)
    assert r_fail["outcome"] == r_ok["outcome"]
    assert r_fail["primary_reason"] == r_ok["primary_reason"]


def test_t15b_positive_result_does_not_self_authorize() -> None:
    case = source_case()
    case["envelope"]["authority_basis"] = []
    case["result"] = {"status": "pass", "success": True, "confidence": 1}
    result = run(case)
    assert_reject(result, "missing_required_basis", "positive_result_self_authorizes")


def test_t16_delegation_amplification_added_operation() -> None:
    case = delegation_case()
    case["basis_records"]["del-1"]["operations"] = ["source.read", "task.dispatch"]
    assert_reject(run(case), "delegation_operation_added")


def test_t16b_delegation_amplification_extended_expiry() -> None:
    case = delegation_case()
    case["basis_records"]["del-1"]["valid_until"] = "2027-12-31T00:00:00Z"
    assert_reject(run(case), "delegation_expiry_extended")


def test_t16c_delegation_amplification_expanded_scope() -> None:
    case = delegation_case()
    case["basis_records"]["del-1"]["scopes"] = ["org-a", "org-b"]
    case["basis_records"]["del-1"]["scope"] = "org-b"
    case["envelope"]["jurisdiction"]["scope"] = "org-b"
    assert_reject(run(case), "delegation_scope_expanded")


def test_t16d_delegation_true_subset_accepts() -> None:
    assert_accept(run(delegation_case()))


def test_t17a_identity_provenance_cannot_carry_competence() -> None:
    case = source_case()
    case["envelope"]["propagation"] = "identity_provenance_only"
    case["propagated_fields"] = ["source_id", "competence"]
    assert_reject(run(case), "propagation_forbidden_field", primary="propagation_forbidden_field")


def test_t17b_none_propagation_rejects_any_propagated_fields() -> None:
    case = source_case()
    case["envelope"]["propagation"] = "none"
    case["propagated_fields"] = ["source_id"]
    assert_reject(run(case), "propagation_forbidden_field")


def test_t17c_reestablished_authority_with_identity_provenance_accepts() -> None:
    case = source_case()
    case["envelope"]["propagation"] = "identity_provenance_only"
    case["propagated_fields"] = {"source_id": "src-1", "content_hash": "hash-1"}
    assert_accept(run(case))


def test_t17d_explicit_propagation_of_warrant_forbidden() -> None:
    case = source_case()
    case["envelope"]["propagation"] = {"mode": "explicit", "fields": ["warrant"]}
    case["propagated_fields"] = ["warrant"]
    assert_reject(run(case), "propagation_forbidden_field")


def test_t18_participant_domain_substitution() -> None:
    case = source_case()
    case["envelope"]["authority_domain"] = "decision_mandate"
    case["envelope"]["operation"] = "decision.make"
    case["envelope"]["participant"] = "evidence-bundler"
    assert_reject(run(case), "participant_domain_not_accepted", primary="participant_domain_not_accepted")


def test_t18b_participant_excluded_responsibility() -> None:
    case = assessment_case()
    case["claimed_responsibilities"] = ["decision_mandate"]
    assert_reject(run(case), "participant_excluded_responsibility")


def test_t18c_participant_not_inferred_from_subject() -> None:
    case = source_case()
    case["envelope"]["subject"]["kind"] = "evidence-bundler"
    del case["envelope"]["participant"]
    result = run(case)
    assert_reject(
        result,
        primary_in=("malformed_envelope", "participant_not_declared"),
    )
    assert "participant_not_declared" in result["violations"] or result["primary_reason"] == "malformed_envelope"


def test_t19a_unknown_domain() -> None:
    case = source_case()
    case["envelope"]["authority_domain"] = "frobnicate"
    assert_reject(run(case), "unknown_domain", primary="unknown_domain")


def test_t19b_unknown_operation() -> None:
    case = source_case()
    case["envelope"]["operation"] = "source.write"
    assert_reject(run(case), "unknown_operation", primary="unknown_operation")


def test_t19c_malformed_missing_target_hash() -> None:
    case = source_case()
    del case["envelope"]["target"]["current_hash"]
    assert_reject(run(case), "malformed_envelope", primary="malformed_envelope")


def test_t20_supporting_artifact_as_sole_basis() -> None:
    art = artifact_record()
    case = source_case()
    case["envelope"]["authority_basis"] = [{"type": "artifact", "id": art["id"], "current": True}]
    case["basis_records"] = {art["id"]: art}
    assert_reject(run(case), "supporting_artifact_not_authority")


def test_t21_reference_current_cannot_override_record() -> None:
    case = source_case()
    case["envelope"]["authority_basis"][0]["current"] = True
    case["basis_records"]["grant-1"]["current"] = False
    assert_reject(run(case), "authority_basis_not_current", primary="authority_basis_not_current")


def test_t22a_historical_valid_despite_later_revocation() -> None:
    case = source_case()
    case["exercise_kind"] = "historical"
    case["basis_records"]["grant-1"]["current"] = False
    case["basis_records"]["grant-1"]["revoked_at"] = "2026-08-01T00:00:00Z"
    case["historical_record"] = {
        "evaluated_at": "2026-06-01T00:00:00Z",
        "authority_was_valid_at_time": True,
        "authority_basis_ids": ["grant-1"],
    }
    assert_accept(run(case))


def test_t22b_new_exercise_after_revocation_rejected() -> None:
    case = source_case()
    case["exercise_kind"] = "new"
    case["envelope"]["evaluated_at"] = "2026-09-01T00:00:00Z"
    case["basis_records"]["grant-1"]["current"] = False
    case["basis_records"]["grant-1"]["revoked_at"] = "2026-08-01T00:00:00Z"
    assert_reject(run(case), "authority_basis_not_current")


def test_t23_cross_domain_warrant() -> None:
    case = numeric_case()
    case["envelope"]["authority_domain"] = "source_boundary"
    case["envelope"]["operation"] = "semantic.validate_absence"
    case["envelope"]["participant"] = "source-boundary-validator"
    grant = grant_record(
        id="grant-sb",
        authority_domain="source_boundary",
        operations=["semantic.validate_absence"],
        target_classes=["measurement"],
    )
    case["envelope"]["authority_basis"] = [{"type": "grant", "id": grant["id"], "current": True}]
    case["basis_records"] = {grant["id"]: grant}
    case["qualification"] = numeric_qualification(type="source_boundary_validator")
    # warrant remains numeric-threshold-v1
    result = run(case)
    assert_reject(result)
    assert (
        "warrant_type_mismatch" in result["violations"]
        or "warrant_domain_mismatch" in result["violations"]
    )


def test_t24_jurisdiction_inapplicable() -> None:
    case = source_case()
    case["envelope"]["jurisdiction"]["applicable"] = False
    assert_reject(run(case), "jurisdiction_inapplicable", primary="jurisdiction_inapplicable")


def test_t25_stale_target_hash() -> None:
    case = numeric_case()
    case["warrant"]["target_hash"] = "hash-old"
    result = run(case)
    assert_reject(result, "warrant_target_mismatch")
    assert "stale_target" in result["violations"]
    assert result["primary_reason"] == "warrant_target_mismatch"


def test_t26_non_implication_cross_use() -> None:
    case = numeric_case()
    case["claimed_effects"] = ["source_boundary.validity"]
    assert_reject(run(case), "non_implication_cross_use", primary="non_implication_cross_use")


def test_t27_non_implication_not_inferred() -> None:
    case = numeric_case()
    case["claimed_effects"] = ["unrelated.foo"]
    result = run(case)
    assert_accept(result)
    assert "non_implication_cross_use" not in result["violations"]


def test_t28_grant_not_allowed_for_decision_mandate() -> None:
    case = decision_case()
    grant = grant_record(
        id="grant-decision",
        authority_domain="decision_mandate",
        operations=["decision.make"],
        target_classes=["decision"],
    )
    case["envelope"]["authority_basis"] = [{"type": "grant", "id": grant["id"], "current": True}]
    case["basis_records"] = {grant["id"]: grant}
    assert_reject(run(case), "authority_basis_type_not_allowed_for_domain")


def test_t29_identity_policy_id_is_not_bound_record() -> None:
    case = source_case()
    case["envelope"]["authority_basis"] = []
    case["envelope"]["propagation"] = "identity_provenance_only"
    case["propagated_fields"] = {"policy_id": "policy-1", "policy_version": "1"}
    result = run(case)
    assert_reject(result, "missing_required_basis")
    assert result["primary_reason"] != "ok"


def test_t30_jurisdiction_not_current_on_new_exercise() -> None:
    case = source_case()
    case["envelope"]["jurisdiction"]["current"] = False
    assert_reject(run(case), "jurisdiction_not_current", primary="jurisdiction_not_current")


def test_t31_generic_authorized_boolean_forbidden() -> None:
    case = source_case()
    case["envelope"]["authorized"] = True
    assert_reject(
        run(case),
        "generic_authorized_boolean_forbidden",
        primary="generic_authorized_boolean_forbidden",
    )


def test_t31b_generic_authorized_cannot_repair_missing_basis() -> None:
    case = source_case()
    case["envelope"]["authority_basis"] = []
    case["envelope"]["authorized"] = True
    result = run(case)
    assert_reject(result, "generic_authorized_boolean_forbidden")
    assert result["outcome"] == "reject"


def test_t32_qualification_cannot_substitute_for_basis() -> None:
    case = numeric_case()
    case["envelope"]["authority_basis"] = []
    result = run(case)
    assert_reject(result, "missing_required_basis")
    assert "qualification_is_not_authority_basis" in result["violations"]


def test_t33_qualification_subject_mismatch() -> None:
    case = numeric_case()
    case["qualification"]["subject_id"] = "other-sub"
    assert_reject(run(case), "qualification_subject_mismatch")


def test_t33b_qualification_scope_need_not_match_jurisdiction() -> None:
    case = numeric_case()
    case["qualification"]["scope"] = "other-scope"
    assert_accept(run(case))


def test_t34_warrant_operation_mismatch() -> None:
    case = numeric_case()
    case["warrant"]["operation"] = "semantic.validate_absence"
    assert_reject(run(case), "warrant_operation_mismatch")


def test_t35_empty_authority_basis_list() -> None:
    case = source_case()
    case["envelope"]["authority_basis"] = []
    assert_reject(run(case), "missing_required_basis", primary="missing_required_basis")


def test_t35b_single_basis_object_is_malformed() -> None:
    case = source_case()
    case["envelope"]["authority_basis"] = {"type": "grant", "id": "grant-1", "current": True}
    assert_reject(run(case), "malformed_envelope", primary="malformed_envelope")


def test_t36_unknown_propagation_mode() -> None:
    case = source_case()
    case["envelope"]["propagation"] = "inherit_all"
    assert_reject(run(case), "unknown_propagation_mode", primary="unknown_propagation_mode")


def test_t37_evaluated_at_on_valid_from_inclusive() -> None:
    case = source_case()
    case["envelope"]["evaluated_at"] = case["basis_records"]["grant-1"]["valid_from"]
    assert_accept(run(case))


def test_t37b_evaluated_at_on_valid_until_inclusive() -> None:
    case = source_case()
    case["envelope"]["evaluated_at"] = case["basis_records"]["grant-1"]["valid_until"]
    assert_accept(run(case))


def test_t38_irrelevant_payload_fields_do_not_affect_outcome() -> None:
    case = source_case()
    case["envelope"]["comment"] = "narrative"
    case["envelope"]["subject"]["display_name"] = "Agent One"
    case["result"] = {"confidence": 0.12, "status": "fail"}
    assert_accept(run(case))


def test_t39_mixed_artifact_and_matching_grant_accepts() -> None:
    art = artifact_record()
    grant = grant_record()
    case = source_case()
    case["envelope"]["authority_basis"] = [
        {"type": "artifact", "id": art["id"], "current": True},
        {"type": "grant", "id": grant["id"], "current": True},
    ]
    case["basis_records"] = {art["id"]: art, grant["id"]: grant}
    assert_accept(run(case))


def test_t40_delegation_parent_unresolvable() -> None:
    case = delegation_case()
    del case["basis_records"]["parent-grant"]
    assert_reject(run(case), "delegation_parent_unresolvable")


def test_extra_qualification_not_current() -> None:
    case = numeric_case()
    case["qualification"]["current"] = False
    assert_reject(run(case), "qualification_not_current")


def test_extra_warrant_inapplicable() -> None:
    case = numeric_case()
    case["warrant"]["applicable"] = False
    assert_reject(run(case), "warrant_inapplicable")


def test_extra_warrant_not_allowed_on_operational_domain() -> None:
    case = source_case()
    case["warrant"] = numeric_warrant(
        authority_domain="source_access",
        operation="source.read",
        target_id="doc-1",
        target_hash="hash-1",
    )
    result = run(case)
    assert_reject(result, "warrant_not_allowed_for_domain")


def test_extra_revoked_at_before_evaluated_at_not_current() -> None:
    case = source_case()
    case["basis_records"]["grant-1"]["revoked_at"] = "2026-05-01T00:00:00Z"
    case["basis_records"]["grant-1"]["current"] = True
    assert_reject(run(case), "authority_basis_not_current")


def test_loader_exposes_nine_domains() -> None:
    from research.contract_e_fresh_reproduction.spec_loader import load_specs

    spec = load_specs()
    assert len(spec.domains) == 9
    assert spec.warrant_required("decision_mandate") is True
    assert spec.warrant_required("source_access") is False
    assert spec.competence_required("numeric_relation") is True
    assert spec.competence_required("source_access") is False
    assert "grant" in spec.conferring_types
    assert "artifact" not in spec.conferring_types
