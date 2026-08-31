"""Independent Contract E authority/warrant evaluator.

Semantics follow research/contract_e_fresh_reproduction/PREREGISTRATION.md.
Labeled assumption tags in outcome notes are implementation assumptions, not
specification authority.
"""

from __future__ import annotations

from typing import Any

from . import reasons as R
from .spec_loader import Spec, load_specs
from .timeutil import in_interval, time_leq

GENERIC_AUTHORIZED_KEYS = ("authorized", "generic_authorized")
POSITIVE_RESULT_STATUSES = {"pass", "passed", "success", "ok", "true", "valid"}

ENVELOPE_SUBJECT_REQUIRED = ("id", "kind")
ENVELOPE_TARGET_REQUIRED = ("class", "id", "current_hash")
ENVELOPE_JURISDICTION_REQUIRED = ("scope", "applicable", "current")
ENVELOPE_BASIS_ENTRY_REQUIRED = ("type", "id", "current")
RECORD_REQUIRED = (
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
HISTORICAL_REQUIRED = ("evaluated_at", "authority_was_valid_at_time", "authority_basis_ids")


def evaluate(case: dict[str, Any], spec: Spec | None = None) -> dict[str, Any]:
    if spec is None:
        spec = load_specs()
    notes: list[str] = []
    violations: list[str] = []

    if not isinstance(case, dict):
        return _result(R.OUTCOME_REJECT, R.MALFORMED_ENVELOPE, [R.MALFORMED_ENVELOPE], notes, spec)

    envelope = case.get("envelope")
    if envelope is None and _looks_like_envelope(case):
        envelope = case
    if not isinstance(envelope, dict):
        return _result(R.OUTCOME_REJECT, R.MALFORMED_ENVELOPE, [R.MALFORMED_ENVELOPE], notes, spec)

    exercise_kind = case.get("exercise_kind", envelope.get("exercise_kind", "new"))
    if exercise_kind not in {"new", "historical"}:
        violations.append(R.MALFORMED_ENVELOPE)
        notes.append("H1")
        exercise_kind = "new"
    if "exercise_kind" not in case and "exercise_kind" not in envelope:
        notes.append("H1-default-new")

    _check_structural(case, envelope, spec, violations)
    _check_generic_authorized(case, envelope, violations)
    _check_domain_operation(envelope, spec, violations)
    _check_participant(envelope, spec, violations)
    _check_jurisdiction(envelope, exercise_kind, violations)
    _check_propagation(case, envelope, spec, violations)

    basis_ok = _check_basis(case, envelope, spec, exercise_kind, violations, notes)
    _check_qualification(case, envelope, spec, exercise_kind, violations, notes)
    _check_warrant(case, envelope, spec, violations, notes)
    _check_stale_target(case, envelope, violations)
    _check_claims(case, envelope, spec, violations)
    _check_result(case, envelope, basis_ok, violations)
    _check_historical(case, envelope, spec, exercise_kind, violations, notes)

    if violations:
        return _result(R.OUTCOME_REJECT, violations[0], violations, notes, spec)
    return _result(R.OUTCOME_ACCEPT, R.OK, [], notes, spec)


def _result(
    outcome: str,
    primary: str,
    violations: list[str],
    notes: list[str],
    spec: Spec,
) -> dict[str, Any]:
    seen_notes: list[str] = []
    for note in notes:
        if note not in seen_notes:
            seen_notes.append(note)
    seen_violations: list[str] = []
    for reason in violations:
        if reason not in seen_violations:
            seen_violations.append(reason)
    return {
        "outcome": outcome,
        "primary_reason": primary if outcome == R.OUTCOME_REJECT else R.OK,
        "violations": seen_violations,
        "notes": seen_notes,
        "spec_version": {
            "candidate": spec.candidate.get("version"),
            "shapes": spec.shapes.get("version"),
            "participant_boundary": spec.participant_boundary.get("version"),
            "basis_binding": spec.basis_binding.get("version"),
        },
    }


def _looks_like_envelope(case: dict[str, Any]) -> bool:
    return "authority_domain" in case and "operation" in case


def _is_true(value: Any) -> bool:
    return value is True


def _missing_fields(obj: Any, required: tuple[str, ...]) -> list[str]:
    if not isinstance(obj, dict):
        return list(required)
    return [field for field in required if field not in obj]


def _check_structural(
    case: dict[str, Any],
    envelope: dict[str, Any],
    spec: Spec,
    violations: list[str],
) -> None:
    for field in spec.envelope_required:
        if field not in envelope:
            violations.append(R.MALFORMED_ENVELOPE)
            return
    if _missing_fields(envelope.get("subject"), ENVELOPE_SUBJECT_REQUIRED):
        violations.append(R.MALFORMED_ENVELOPE)
        return
    if _missing_fields(envelope.get("target"), ENVELOPE_TARGET_REQUIRED):
        violations.append(R.MALFORMED_ENVELOPE)
        return
    if _missing_fields(envelope.get("jurisdiction"), ENVELOPE_JURISDICTION_REQUIRED):
        violations.append(R.MALFORMED_ENVELOPE)
        return
    basis = envelope.get("authority_basis")
    if not isinstance(basis, list):
        violations.append(R.MALFORMED_ENVELOPE)
        return
    if not isinstance(envelope.get("non_implications"), list):
        violations.append(R.MALFORMED_ENVELOPE)
        return
    if envelope.get("evaluated_at") in (None, ""):
        violations.append(R.MALFORMED_ENVELOPE)


def _check_generic_authorized(
    case: dict[str, Any],
    envelope: dict[str, Any],
    violations: list[str],
) -> None:
    result = _result_payload(case, envelope)
    surfaces = [case, envelope]
    if isinstance(result, dict):
        surfaces.append(result)
    for surface in surfaces:
        for key in GENERIC_AUTHORIZED_KEYS:
            if key in surface:
                violations.append(R.GENERIC_AUTHORIZED_BOOLEAN_FORBIDDEN)
                return


def _check_domain_operation(envelope: dict[str, Any], spec: Spec, violations: list[str]) -> None:
    domain = envelope.get("authority_domain")
    operation = envelope.get("operation")
    if domain not in spec.domains:
        violations.append(R.UNKNOWN_DOMAIN)
        return
    domain_spec = spec.domains[domain]
    operations = domain_spec.get("operations") or []
    if operation not in operations:
        violations.append(R.UNKNOWN_OPERATION)


def _check_participant(envelope: dict[str, Any], spec: Spec, violations: list[str]) -> None:
    participant = envelope.get("participant")
    if participant is None or participant == "":
        violations.append(R.PARTICIPANT_NOT_DECLARED)
        if isinstance(envelope.get("subject"), dict) and envelope["subject"].get("kind"):
            violations.append(R.PARTICIPANT_INFERRED_FROM_SUBJECT)
        return
    declared = spec.participants.get(participant)
    if not isinstance(declared, dict):
        violations.append(R.PARTICIPANT_NOT_DECLARED)
        return
    domain = envelope.get("authority_domain")
    operation = envelope.get("operation")
    if domain not in (declared.get("accepted_domains") or []):
        violations.append(R.PARTICIPANT_DOMAIN_NOT_ACCEPTED)
    if operation not in (declared.get("accepted_operations") or []):
        violations.append(R.PARTICIPANT_OPERATION_NOT_ACCEPTED)


def _check_jurisdiction(
    envelope: dict[str, Any],
    exercise_kind: str,
    violations: list[str],
) -> None:
    jurisdiction = envelope.get("jurisdiction")
    if not isinstance(jurisdiction, dict):
        return
    if not _is_true(jurisdiction.get("applicable")):
        violations.append(R.JURISDICTION_INAPPLICABLE)
    if exercise_kind == "new" and not _is_true(jurisdiction.get("current")):
        violations.append(R.JURISDICTION_NOT_CURRENT)


def _propagation_mode_and_fields(
    case: dict[str, Any], envelope: dict[str, Any]
) -> tuple[Any, list[str] | None]:
    raw = envelope.get("propagation")
    mode: Any
    explicit_fields: list[str] | None = None
    if isinstance(raw, dict):
        mode = raw.get("mode", raw.get("propagation"))
        if "fields" in raw and isinstance(raw["fields"], list):
            explicit_fields = [str(x) for x in raw["fields"]]
    else:
        mode = raw
    if explicit_fields is None:
        extra = case.get("explicit_propagation_fields")
        if isinstance(extra, list):
            explicit_fields = [str(x) for x in extra]
    return mode, explicit_fields


def _propagated_field_names(case: dict[str, Any], envelope: dict[str, Any]) -> list[str]:
    raw = case.get("propagated_fields", envelope.get("propagated_fields"))
    if raw is None:
        return []
    if isinstance(raw, dict):
        return [str(k) for k in raw.keys()]
    if isinstance(raw, list):
        names = []
        for item in raw:
            if isinstance(item, str):
                names.append(item)
            elif isinstance(item, dict) and "name" in item:
                names.append(str(item["name"]))
            else:
                names.append(str(item))
        return names
    return [str(raw)]


def _check_propagation(
    case: dict[str, Any],
    envelope: dict[str, Any],
    spec: Spec,
    violations: list[str],
) -> None:
    mode, explicit_fields = _propagation_mode_and_fields(case, envelope)
    if mode not in spec.propagation_modes:
        violations.append(R.UNKNOWN_PROPAGATION_MODE)
        return
    if mode == "none":
        allowed: set[str] = set()
    elif mode == "identity_provenance_only":
        allowed = set(spec.identity_provenance_fields)
    else:
        if not explicit_fields:
            violations.append(R.EXPLICIT_PROPAGATION_MISSING_FIELDS)
            return
        allowed = set(explicit_fields)
    never_implicit = set(spec.never_implicit_fields)
    presented = _propagated_field_names(case, envelope)
    for name in presented:
        if name in never_implicit:
            violations.append(R.PROPAGATION_FORBIDDEN_FIELD)
            return
        if name not in allowed:
            violations.append(R.PROPAGATION_FORBIDDEN_FIELD)
            return


def _basis_records(case: dict[str, Any], envelope: dict[str, Any]) -> dict[str, Any]:
    records = case.get("basis_records", envelope.get("basis_records"))
    if isinstance(records, dict):
        return records
    if isinstance(records, list):
        out: dict[str, Any] = {}
        for item in records:
            if isinstance(item, dict) and "id" in item:
                out[str(item["id"])] = item
        return out
    return {}


def _record_is_current(record: dict[str, Any], evaluated_at: Any, exercise_kind: str) -> bool:
    if exercise_kind != "new":
        return True
    if not _is_true(record.get("current")):
        return False
    revoked_at = record.get("revoked_at")
    if revoked_at is not None and time_leq(revoked_at, evaluated_at):
        return False
    return True


def _match_one_reference(
    ref: Any,
    envelope: dict[str, Any],
    records: dict[str, Any],
    spec: Spec,
    exercise_kind: str,
) -> list[str]:
    if not isinstance(ref, dict) or _missing_fields(ref, ENVELOPE_BASIS_ENTRY_REQUIRED):
        return [R.MALFORMED_BASIS_REFERENCE]
    record = records.get(ref["id"])
    if record is None:
        return [R.UNRESOLVABLE_AUTHORITY_BASIS]
    if not isinstance(record, dict) or _missing_fields(record, RECORD_REQUIRED):
        return [R.MALFORMED_BASIS_RECORD]
    if record.get("id") not in (None, ref["id"]) and record.get("id") != ref["id"]:
        return [R.UNRESOLVABLE_AUTHORITY_BASIS]
    if ref.get("type") != record.get("type"):
        return [R.AUTHORITY_BASIS_TYPE_MISMATCH]
    evaluated_at = envelope.get("evaluated_at")
    if not _record_is_current(record, evaluated_at, exercise_kind):
        return [R.AUTHORITY_BASIS_NOT_CURRENT]
    subject = envelope.get("subject") if isinstance(envelope.get("subject"), dict) else {}
    subject_ids = record.get("subject_ids")
    if not isinstance(subject_ids, list) or subject.get("id") not in subject_ids:
        return [R.AUTHORITY_BASIS_SUBJECT_MISMATCH]
    if envelope.get("authority_domain") != record.get("authority_domain"):
        return [R.AUTHORITY_BASIS_DOMAIN_MISMATCH]
    operations = record.get("operations")
    if not isinstance(operations, list) or envelope.get("operation") not in operations:
        return [R.AUTHORITY_BASIS_OPERATION_MISMATCH]
    scopes = record.get("scopes")
    jurisdiction = envelope.get("jurisdiction") if isinstance(envelope.get("jurisdiction"), dict) else {}
    if not isinstance(scopes, list) or jurisdiction.get("scope") not in scopes:
        return [R.AUTHORITY_BASIS_SCOPE_MISMATCH]
    target = envelope.get("target") if isinstance(envelope.get("target"), dict) else {}
    target_classes = record.get("target_classes")
    if not isinstance(target_classes, list) or target.get("class") not in target_classes:
        return [R.AUTHORITY_BASIS_TARGET_CLASS_MISMATCH]
    target_ids = record.get("target_ids")
    if isinstance(target_ids, list) and len(target_ids) > 0 and target.get("id") not in target_ids:
        return [R.AUTHORITY_BASIS_TARGET_ID_MISMATCH]
    if not in_interval(evaluated_at, record.get("valid_from"), record.get("valid_until")):
        return [R.AUTHORITY_BASIS_OUTSIDE_VALIDITY_INTERVAL]
    return []


def _delegation_reasons(
    record: dict[str, Any],
    envelope: dict[str, Any],
    records: dict[str, Any],
) -> list[str]:
    if record.get("type") != "delegation":
        return []
    parent_id = record.get("parent_authority_id")
    if not parent_id:
        return [R.MALFORMED_DELEGATION]
    parent = records.get(parent_id)
    if not isinstance(parent, dict):
        return [R.DELEGATION_PARENT_UNRESOLVABLE]
    reasons: list[str] = []
    child_ops = record.get("operations") if isinstance(record.get("operations"), list) else []
    parent_ops = parent.get("operations") if isinstance(parent.get("operations"), list) else []
    if set(child_ops) - set(parent_ops):
        reasons.append(R.DELEGATION_OPERATION_ADDED)
    parent_scopes = parent.get("scopes") if isinstance(parent.get("scopes"), list) else []
    child_scopes = record.get("scopes") if isinstance(record.get("scopes"), list) else []
    if record.get("scope") is not None:
        child_scopes = list(child_scopes) + [record.get("scope")]
    if parent.get("scope") is not None:
        parent_scopes = list(parent_scopes) + [parent.get("scope")]
    if set(child_scopes) - set(parent_scopes):
        reasons.append(R.DELEGATION_SCOPE_EXPANDED)
    if record.get("valid_until") is not None and parent.get("valid_until") is not None:
        if not time_leq(record.get("valid_until"), parent.get("valid_until")):
            reasons.append(R.DELEGATION_EXPIRY_EXTENDED)
    if record.get("valid_from") is not None and parent.get("valid_from") is not None:
        if not time_leq(parent.get("valid_from"), record.get("valid_from")):
            reasons.append(R.DELEGATION_NOT_SUBSET_OF_PARENT)
    parent_classes = parent.get("target_classes")
    child_classes = record.get("target_classes")
    if isinstance(parent_classes, list) and isinstance(child_classes, list):
        if set(child_classes) - set(parent_classes):
            reasons.append(R.DELEGATION_NOT_SUBSET_OF_PARENT)
    parent_tids = parent.get("target_ids")
    child_tids = record.get("target_ids")
    if isinstance(parent_tids, list) and parent_tids and isinstance(child_tids, list):
        if set(child_tids) - set(parent_tids):
            reasons.append(R.DELEGATION_NOT_SUBSET_OF_PARENT)
    subject = envelope.get("subject") if isinstance(envelope.get("subject"), dict) else {}
    if record.get("delegate") is not None and subject.get("id") != record.get("delegate"):
        reasons.append(R.DELEGATION_NOT_SUBSET_OF_PARENT)
    return reasons


def _type_allowed_for_domain(
    record: dict[str, Any],
    records: dict[str, Any],
    any_of: tuple[str, ...],
    conferring: set[str],
) -> bool:
    """Delegation satisfies domain any_of if a parent chain reaches an allowed type.

    Assumption D2: domain `any_of` lists root conferring types (grant/policy).
    A delegation is allowed when it chains to a parent whose type is in `any_of`.
    """
    record_type = record.get("type")
    if record_type in any_of:
        return True
    if record_type != "delegation":
        return False
    seen: set[str] = set()
    current: dict[str, Any] | None = record
    while isinstance(current, dict) and current.get("type") == "delegation":
        parent_id = current.get("parent_authority_id")
        if not parent_id or parent_id in seen:
            return False
        seen.add(str(parent_id))
        parent = records.get(parent_id)
        if not isinstance(parent, dict):
            return False
        if parent.get("type") in any_of:
            return True
        current = parent
    return isinstance(current, dict) and current.get("type") in any_of


def _pick_basis_failure(failure_lists: list[list[str]]) -> list[str]:
    if not failure_lists:
        return [R.MISSING_REQUIRED_BASIS]
    best = failure_lists[0]
    best_rank = R.basis_rank(best[0]) if best else 10**6
    for reasons in failure_lists[1:]:
        if not reasons:
            continue
        rank = R.basis_rank(reasons[0])
        if rank < best_rank:
            best = reasons
            best_rank = rank
    return best


def _check_basis(
    case: dict[str, Any],
    envelope: dict[str, Any],
    spec: Spec,
    exercise_kind: str,
    violations: list[str],
    notes: list[str],
) -> bool:
    notes.append("B1")
    basis = envelope.get("authority_basis")
    if not isinstance(basis, list):
        return False
    if len(basis) == 0:
        violations.append(R.MISSING_REQUIRED_BASIS)
        if _qualification_obj(case, envelope) is not None:
            violations.append(R.QUALIFICATION_IS_NOT_AUTHORITY_BASIS)
        if _policy_id_without_record(case, envelope):
            violations.append(R.POLICY_IDENTIFIER_WITHOUT_BOUND_RECORD)
        return False

    records = _basis_records(case, envelope)
    domain = envelope.get("authority_domain")
    any_of = spec.domain_any_of(domain) if domain in spec.domains else spec.conferring_types
    conferring = set(spec.conferring_types)

    matching = False
    conferring_failures: list[list[str]] = []
    supporting_only_failures: list[list[str]] = []

    for ref in basis:
        match_reasons = _match_one_reference(ref, envelope, records, spec, exercise_kind)
        ref_type = ref.get("type") if isinstance(ref, dict) else None
        record = None
        if isinstance(ref, dict):
            record = records.get(ref.get("id"))
        record_type = record.get("type") if isinstance(record, dict) else None
        is_conferring_ref = ref_type in conferring

        if match_reasons:
            if is_conferring_ref:
                conferring_failures.append(match_reasons)
            else:
                supporting_only_failures.append(match_reasons)
            continue

        assert isinstance(record, dict)
        extra: list[str] = []
        if record_type not in conferring:
            extra.append(R.SUPPORTING_ARTIFACT_NOT_AUTHORITY)
        elif any_of and not _type_allowed_for_domain(record, records, any_of, conferring):
            extra.append(R.AUTHORITY_BASIS_TYPE_NOT_ALLOWED_FOR_DOMAIN)
            if record_type == "delegation":
                notes.append("D2-delegation-any-of-via-parent")
        extra.extend(_delegation_reasons(record, envelope, records))
        if extra:
            if record_type in conferring or ref_type in conferring:
                conferring_failures.append(extra)
            else:
                supporting_only_failures.append(extra)
            continue
        matching = True
        if record_type == "delegation":
            notes.append("D2-delegation-any-of-via-parent")

    if matching:
        notes.append("B1-any-matching-conferring-suffices")
        return True

    if conferring_failures:
        violations.extend(_pick_basis_failure(conferring_failures))
        return False
    if supporting_only_failures:
        first = supporting_only_failures[0]
        if first and first[0] == R.UNRESOLVABLE_AUTHORITY_BASIS:
            violations.extend(first)
        elif first and first[0] == R.AUTHORITY_BASIS_TYPE_MISMATCH:
            violations.extend(first)
        else:
            if R.SUPPORTING_ARTIFACT_NOT_AUTHORITY not in first:
                violations.append(R.SUPPORTING_ARTIFACT_NOT_AUTHORITY)
            violations.extend(first)
        return False
    violations.append(R.MISSING_REQUIRED_BASIS)
    return False


def _policy_id_without_record(case: dict[str, Any], envelope: dict[str, Any]) -> bool:
    names = _propagated_field_names(case, envelope)
    payload = case.get("propagated_fields")
    if "policy_id" in names:
        return True
    if isinstance(payload, dict) and payload.get("policy_id"):
        return True
    return False


def _qualification_obj(case: dict[str, Any], envelope: dict[str, Any]) -> dict[str, Any] | None:
    for key in ("qualification", "competence"):
        value = case.get(key, envelope.get(key))
        if isinstance(value, dict):
            return value
    return None


def _warrant_obj(case: dict[str, Any], envelope: dict[str, Any]) -> dict[str, Any] | None:
    value = case.get("warrant", envelope.get("warrant"))
    if isinstance(value, dict):
        return value
    return None


def _result_payload(case: dict[str, Any], envelope: dict[str, Any]) -> Any:
    if "result" in case:
        return case.get("result")
    if "result" in envelope:
        return envelope.get("result")
    if "semantic_payload" in case:
        return case.get("semantic_payload")
    return envelope.get("semantic_payload")


def _check_qualification(
    case: dict[str, Any],
    envelope: dict[str, Any],
    spec: Spec,
    exercise_kind: str,
    violations: list[str],
    notes: list[str],
) -> None:
    notes.append("Q1")
    domain = envelope.get("authority_domain")
    required = domain in spec.domains and spec.competence_required(domain)
    qualification = _qualification_obj(case, envelope)
    if required and qualification is None:
        violations.append(R.MISSING_REQUIRED_QUALIFICATION)
        return
    if qualification is None:
        return
    if _missing_fields(qualification, QUALIFICATION_REQUIRED):
        violations.append(R.MALFORMED_QUALIFICATION)
        return
    accepted = spec.accepted_qualification_types(domain) if domain in spec.domains else ()
    if accepted and qualification.get("type") not in accepted:
        violations.append(R.QUALIFICATION_TYPE_MISMATCH)
    subject = envelope.get("subject") if isinstance(envelope.get("subject"), dict) else {}
    if qualification.get("subject_id") != subject.get("id"):
        violations.append(R.QUALIFICATION_SUBJECT_MISMATCH)
    if exercise_kind == "new" and not _is_true(qualification.get("current")):
        violations.append(R.QUALIFICATION_NOT_CURRENT)


def _check_warrant(
    case: dict[str, Any],
    envelope: dict[str, Any],
    spec: Spec,
    violations: list[str],
    notes: list[str],
) -> None:
    notes.append("W1")
    domain = envelope.get("authority_domain")
    warrant = _warrant_obj(case, envelope)
    required = domain in spec.domains and spec.warrant_required(domain)
    allowed = domain in spec.domains and spec.warrant_allowed(domain)
    if warrant is None:
        if required:
            violations.append(R.MISSING_REQUIRED_WARRANT)
        return
    if not allowed:
        violations.append(R.WARRANT_NOT_ALLOWED_FOR_DOMAIN)
        violations.append(R.WARRANT_IS_NOT_OPERATIONAL_PERMISSION)
        return
    if _missing_fields(warrant, WARRANT_REQUIRED):
        violations.append(R.MALFORMED_WARRANT)
        return
    if not isinstance(warrant.get("input_artifact_ids"), list):
        violations.append(R.MALFORMED_WARRANT)
        return
    accepted = spec.accepted_warrant_types(domain) if domain in spec.domains else ()
    if accepted and warrant.get("type") not in accepted:
        violations.append(R.WARRANT_TYPE_MISMATCH)
    table = spec.warrant_types.get(warrant.get("type")) if isinstance(warrant.get("type"), str) else None
    if table is None and warrant.get("type") not in accepted:
        # unknown warrant type already captured as type mismatch if accepted list exists
        pass
    if warrant.get("authority_domain") != envelope.get("authority_domain"):
        violations.append(R.WARRANT_DOMAIN_MISMATCH)
    if table and table.get("authority_domain") != envelope.get("authority_domain"):
        violations.append(R.WARRANT_DOMAIN_MISMATCH)
    if warrant.get("operation") != envelope.get("operation"):
        violations.append(R.WARRANT_OPERATION_MISMATCH)
    if table and table.get("operation") != envelope.get("operation"):
        violations.append(R.WARRANT_OPERATION_MISMATCH)
    target = envelope.get("target") if isinstance(envelope.get("target"), dict) else {}
    if warrant.get("target_id") != target.get("id") or warrant.get("target_hash") != target.get("current_hash"):
        violations.append(R.WARRANT_TARGET_MISMATCH)
    if not _is_true(warrant.get("applicable")):
        violations.append(R.WARRANT_INAPPLICABLE)
    if not _is_true(warrant.get("current")):
        violations.append(R.WARRANT_NOT_CURRENT)


def _check_stale_target(
    case: dict[str, Any],
    envelope: dict[str, Any],
    violations: list[str],
) -> None:
    target = envelope.get("target")
    if not isinstance(target, dict):
        return
    if target.get("current") is False:
        violations.append(R.STALE_TARGET)
        return
    warrant = _warrant_obj(case, envelope)
    if isinstance(warrant, dict) and "target_hash" in warrant:
        if warrant.get("target_hash") != target.get("current_hash"):
            violations.append(R.STALE_TARGET)


def _claimed_values(case: dict[str, Any], envelope: dict[str, Any], key: str) -> list[str]:
    raw = case.get(key, envelope.get(key))
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x) for x in raw]
    return [str(raw)]


def _check_claims(
    case: dict[str, Any],
    envelope: dict[str, Any],
    spec: Spec,
    violations: list[str],
) -> None:
    claimed_effects = _claimed_values(case, envelope, "claimed_effects")
    claimed_resp = _claimed_values(case, envelope, "claimed_responsibilities")
    blocked: set[str] = set()
    if isinstance(envelope.get("non_implications"), list):
        blocked.update(str(x) for x in envelope["non_implications"])
    warrant = _warrant_obj(case, envelope)
    if isinstance(warrant, dict):
        table = spec.warrant_types.get(warrant.get("type")) if isinstance(warrant.get("type"), str) else None
        if isinstance(table, dict) and isinstance(table.get("non_implications"), list):
            blocked.update(str(x) for x in table["non_implications"])
    if claimed_effects:
        if set(claimed_effects) & blocked:
            violations.append(R.NON_IMPLICATION_CROSS_USE)
        domain = envelope.get("authority_domain")
        if domain == "decision_mandate" and (
            "execution_permission" in claimed_effects or "task_dispatch" in claimed_effects
        ):
            violations.append(R.DECISION_USED_AS_EXECUTION_PERMISSION)

    participant = envelope.get("participant")
    declared = spec.participants.get(participant) if participant in spec.participants else None
    if isinstance(declared, dict):
        excluded = set(declared.get("excluded_responsibilities") or [])
        if set(claimed_resp) & excluded or set(claimed_effects) & excluded:
            violations.append(R.PARTICIPANT_EXCLUDED_RESPONSIBILITY)


def _result_offered_as_success(result: Any) -> bool:
    if not isinstance(result, dict):
        return False
    if result.get("success") is True:
        return True
    if result.get("positive_status") is True:
        return True
    status = result.get("status")
    if isinstance(status, str) and status.lower() in POSITIVE_RESULT_STATUSES:
        return True
    if result.get("as_authority") is True or result.get("self_authorizes") is True:
        return True
    return False


def _check_result(
    case: dict[str, Any],
    envelope: dict[str, Any],
    basis_ok: bool,
    violations: list[str],
) -> None:
    result = _result_payload(case, envelope)
    offered = case.get("result_as_authority", envelope.get("result_as_authority"))
    if offered is True or (not basis_ok and _result_offered_as_success(result)):
        violations.append(R.POSITIVE_RESULT_SELF_AUTHORIZES)
        violations.append(R.SEMANTIC_PAYLOAD_AUTHORITY_EFFECT)


def _check_historical(
    case: dict[str, Any],
    envelope: dict[str, Any],
    spec: Spec,
    exercise_kind: str,
    violations: list[str],
    notes: list[str],
) -> None:
    if case.get("assert_later_revocation_rewrites_history") is True:
        violations.append(R.HISTORICAL_VALIDITY_REWRITTEN)
    historical = case.get("historical_record", envelope.get("historical_record"))
    if historical is None:
        return
    if not isinstance(historical, dict) or _missing_fields(historical, HISTORICAL_REQUIRED):
        violations.append(R.MALFORMED_HISTORICAL_RECORD)
        return
    if historical.get("later_revocation_rewrites_authority_was_valid_at_time") is True:
        violations.append(R.HISTORICAL_VALIDITY_REWRITTEN)
    if exercise_kind != "historical":
        return
    notes.append("H2")
    claimed_valid = historical.get("authority_was_valid_at_time")
    if claimed_valid is True:
        # Recompute interval/current-ignoring match using historical evaluated_at.
        hist_case = {
            **case,
            "exercise_kind": "historical",
            "envelope": {
                **envelope,
                "evaluated_at": historical.get("evaluated_at", envelope.get("evaluated_at")),
            },
        }
        hist_env = hist_case["envelope"]
        records = _basis_records(hist_case, hist_env)
        basis = hist_env.get("authority_basis")
        ids = historical.get("authority_basis_ids")
        if isinstance(ids, list) and ids:
            basis = []
            for bid in ids:
                rec = records.get(bid)
                if isinstance(rec, dict):
                    basis.append({"type": rec.get("type"), "id": bid, "current": rec.get("current")})
                else:
                    basis.append({"type": "grant", "id": bid, "current": False})
            hist_env = {**hist_env, "authority_basis": basis}
        any_ok = False
        if isinstance(hist_env.get("authority_basis"), list):
            conferring = set(spec.conferring_types)
            domain = hist_env.get("authority_domain")
            any_of = spec.domain_any_of(domain) if domain in spec.domains else tuple(conferring)
            for ref in hist_env["authority_basis"]:
                reasons = _match_one_reference(ref, hist_env, records, spec, "historical")
                if reasons:
                    continue
                rec = records.get(ref.get("id")) if isinstance(ref, dict) else None
                if not isinstance(rec, dict):
                    continue
                if rec.get("type") not in conferring:
                    continue
                if any_of and rec.get("type") not in any_of:
                    continue
                if _delegation_reasons(rec, hist_env, records):
                    continue
                any_ok = True
                break
        if not any_ok:
            violations.append(R.HISTORICAL_VALIDITY_CLAIM_FALSE)
