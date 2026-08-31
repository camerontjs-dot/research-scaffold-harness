"""Native RC3C authority consumer/validator.

Consumes canonical JSON wire objects. Does not coerce singular/plural
forms, does not read opaque result payloads, and does not translate
hidden-vector aliases.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from research_scaffold_harness.contract_e_rc3c.spec import (
    AUTHORITY_REFERENCE_REQUIRED,
    DELEGATION_REQUIRED,
    DOMAIN_BASIS_REQUIREMENTS,
    DOMAINS,
    ENVELOPE_REQUIRED_KEYS,
    HISTORICAL_REQUIRED,
    IDENTITY_PROVENANCE_FIELDS,
    JURISDICTION_REQUIRED,
    MODES,
    NEVER_IMPLICIT_FIELDS,
    NORMATIVE_REASONS,
    PARTICIPANTS,
    PRECEDENCE_INDEX,
    PROPAGATION_MODES,
    QUALIFICATION_REQUIRED,
    REESTABLISHMENT_FIELDS,
    RESOLVED_RECORD_REQUIRED,
    SUBJECT_REQUIRED,
    SUPPORTING_BASIS_TYPES,
    TARGET_REQUIRED,
    WARRANT_REQUIRED,
)


@dataclass(frozen=True)
class Decision:
    accepted: bool
    primary_reason: str | None
    reason_is_normative: bool
    evaluation_kind: str
    mode: str
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted": self.accepted,
            "primary_reason": self.primary_reason,
            "reason_is_normative": self.reason_is_normative,
            "evaluation_kind": self.evaluation_kind,
            "mode": self.mode,
            "notes": list(self.notes),
        }


def _accept(kind: str, mode: str, notes: list[str] | tuple[str, ...] = ()) -> Decision:
    return Decision(
        accepted=True,
        primary_reason=None,
        reason_is_normative=False,
        evaluation_kind=kind,
        mode=mode,
        notes=tuple(notes),
    )


def _reject(
    reason: str,
    kind: str,
    mode: str,
    notes: list[str] | tuple[str, ...] = (),
) -> Decision:
    return Decision(
        accepted=False,
        primary_reason=reason,
        reason_is_normative=reason in NORMATIVE_REASONS,
        evaluation_kind=kind,
        mode=mode,
        notes=tuple(notes),
    )


def _earliest(reasons: list[str]) -> str:
    listed = [reason for reason in reasons if reason in PRECEDENCE_INDEX]
    if listed:
        return min(listed, key=lambda reason: PRECEDENCE_INDEX[reason])
    return reasons[0]


def parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def normalize_registry(raw: Any) -> dict[str, dict[str, Any]]:
    if raw is None:
        return {}
    records: list[Any]
    if isinstance(raw, list):
        records = raw
    elif isinstance(raw, dict):
        if isinstance(raw.get("records"), list):
            records = raw["records"]
        else:
            out: dict[str, dict[str, Any]] = {}
            for key, value in raw.items():
                if isinstance(value, dict):
                    record_id = value.get("id", key)
                    if isinstance(record_id, str):
                        out[record_id] = value
            return out
    else:
        return {}
    out = {}
    for item in records:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            out[item["id"]] = item
    return out


def evaluate(request: dict[str, Any]) -> Decision:
    if not isinstance(request, dict):
        return _reject("missing_required_field", "envelope", "new_exercise")
    kind = request.get("kind", "envelope")
    mode = request.get("mode", "new_exercise")
    if mode not in MODES:
        mode = "new_exercise"
    registry = normalize_registry(request.get("registry"))
    if kind == "envelope":
        return evaluate_envelope(request.get("envelope"), registry, mode)
    if kind == "propagation":
        return evaluate_propagation(request.get("propagation") or request.get("request"), mode)
    if kind == "delegation":
        return evaluate_delegation(
            request.get("parent"),
            request.get("child"),
            mode,
        )
    if kind == "historical":
        record = request.get("record") or request.get("historical")
        return evaluate_historical(record, registry, mode)
    return _reject("missing_required_field", "envelope", mode, notes=["unknown_evaluation_kind"])


def evaluate_envelope(
    envelope: Any,
    registry: Any,
    mode: str = "new_exercise",
) -> Decision:
    kind = "envelope"
    notes: list[str] = []
    local_reasons: list[str] = []
    if mode not in MODES:
        mode = "new_exercise"
    records = normalize_registry(registry)

    if not isinstance(envelope, dict):
        return _reject("missing_required_field", kind, mode)

    # Opaque payload is never consulted.
    envelope_view = {key: value for key, value in envelope.items() if key != "result"}

    if "authority_basis" in envelope_view and not _is_object_array(
        envelope_view.get("authority_basis")
    ):
        return _reject("malformed_authority_basis_shape", kind, mode)
    if "competence" in envelope_view and not _is_object_array(envelope_view.get("competence")):
        return _reject("malformed_competence_shape", kind, mode)

    jurisdiction = envelope_view.get("jurisdiction")
    if isinstance(jurisdiction, dict) and "scope" in jurisdiction:
        if not isinstance(jurisdiction.get("scope"), str):
            return _reject("malformed_jurisdiction_scope_shape", kind, mode)

    competence = envelope_view.get("competence")
    if isinstance(competence, list):
        for qualification in competence:
            if isinstance(qualification, dict) and "scope" in qualification:
                if not isinstance(qualification.get("scope"), str):
                    return _reject("malformed_qualification_scope_shape", kind, mode)

    if "authorized" in envelope_view:
        return _reject("generic_authorized_forbidden", kind, mode)

    if _missing_envelope_fields(envelope_view):
        return _reject("missing_required_field", kind, mode)

    if not isinstance(envelope_view.get("non_implications"), list) or not all(
        isinstance(item, str) for item in envelope_view["non_implications"]
    ):
        local_reasons.append("malformed_non_implications_shape")
        notes.append("A5_non_implications_type")

    domain = envelope_view["authority_domain"]
    if domain not in DOMAINS:
        return _reject("unknown_authority_domain", kind, mode, notes)

    domain_spec = DOMAINS[domain]
    operation = envelope_view["operation"]
    if operation not in domain_spec["operations"]:
        return _reject("domain_operation_mismatch", kind, mode, notes)

    participant = envelope_view["participant"]
    if participant not in PARTICIPANTS:
        return _reject("unknown_participant", kind, mode, notes)
    participant_spec = PARTICIPANTS[participant]
    if domain not in participant_spec["accepted_domains"]:
        return _reject("participant_domain_out_of_scope", kind, mode, notes)
    if operation not in participant_spec["accepted_operations"]:
        return _reject("participant_operation_out_of_scope", kind, mode, notes)

    jur = envelope_view["jurisdiction"]
    if jur.get("applicable") is not True:
        return _reject("jurisdiction_inapplicable", kind, mode, notes)
    if jur.get("current") is not True:
        return _reject("jurisdiction_not_current", kind, mode, notes)

    basis_reason = _basis_reason(envelope_view, records, mode, notes)
    if basis_reason is not None:
        return _reject(basis_reason, kind, mode, notes)

    qualification_reason = _qualification_reason(envelope_view, domain, domain_spec)
    if qualification_reason is not None:
        return _reject(qualification_reason, kind, mode, notes)

    warrant_reason = _warrant_reason(envelope_view, domain, domain_spec)
    if warrant_reason is not None:
        return _reject(warrant_reason, kind, mode, notes)

    propagation_listed, propagation_local, propagation_notes = _envelope_propagation_reasons(
        envelope_view
    )
    notes.extend(propagation_notes)
    if propagation_listed is not None:
        return _reject(propagation_listed, kind, mode, notes)
    if propagation_local is not None:
        local_reasons.append(propagation_local)

    if local_reasons:
        chosen = (
            _earliest(local_reasons)
            if local_reasons[0] in PRECEDENCE_INDEX
            else local_reasons[0]
        )
        return _reject(chosen, kind, mode, notes)
    return _accept(kind, mode, notes)


def _is_object_array(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    return all(isinstance(item, dict) for item in value)


def _missing_envelope_fields(envelope: dict[str, Any]) -> bool:
    for key in ENVELOPE_REQUIRED_KEYS:
        if key not in envelope:
            return True
    subject = envelope.get("subject")
    if not isinstance(subject, dict) or any(
        field_name not in subject for field_name in SUBJECT_REQUIRED
    ):
        return True
    target = envelope.get("target")
    if not isinstance(target, dict) or any(
        field_name not in target for field_name in TARGET_REQUIRED
    ):
        return True
    jurisdiction = envelope.get("jurisdiction")
    if not isinstance(jurisdiction, dict) or any(
        field_name not in jurisdiction for field_name in JURISDICTION_REQUIRED
    ):
        return True
    if not isinstance(envelope.get("authority_domain"), str) or envelope["authority_domain"] == "":
        return True
    if not isinstance(envelope.get("operation"), str) or envelope["operation"] == "":
        return True
    if "participant" not in envelope:
        return True
    if not isinstance(envelope.get("evaluated_at"), str) or envelope["evaluated_at"] == "":
        return True
    for reference in envelope.get("authority_basis", []):
        if not isinstance(reference, dict):
            return True
        if any(field_name not in reference for field_name in AUTHORITY_REFERENCE_REQUIRED):
            return True
    for qualification in envelope.get("competence", []):
        if not isinstance(qualification, dict):
            return True
        if any(field_name not in qualification for field_name in QUALIFICATION_REQUIRED):
            return True
    if "warrant" in envelope and isinstance(envelope["warrant"], dict):
        if any(field_name not in envelope["warrant"] for field_name in WARRANT_REQUIRED):
            return True
    return False


def _basis_reason(
    envelope: dict[str, Any],
    records: dict[str, dict[str, Any]],
    mode: str,
    notes: list[str],
) -> str | None:
    references: list[dict[str, Any]] = envelope["authority_basis"]
    successes: list[dict[str, Any]] = []
    failures: list[str] = []
    attempted = 0
    for reference in references:
        basis_type = reference.get("type")
        if basis_type in SUPPORTING_BASIS_TYPES:
            notes.append("supporting_reference_ignored_for_satisfaction")
            continue
        attempted += 1
        bind_reason, record = _bind_reference(reference, envelope, records, mode)
        if bind_reason is None and record is not None:
            successes.append(record)
        elif bind_reason is not None:
            failures.append(bind_reason)
        else:
            failures.append("unresolvable_authority_basis")

    domain = envelope["authority_domain"]
    allowed_types = DOMAIN_BASIS_REQUIREMENTS[domain]["any_of"]
    satisfying = [record for record in successes if record.get("type") in allowed_types]
    if satisfying:
        return None
    listed_failures = [reason for reason in failures if reason in PRECEDENCE_INDEX]
    local_failures = [reason for reason in failures if reason not in PRECEDENCE_INDEX]
    if successes and not satisfying:
        notes.append("A2_or_domain_any_of_unsatisfied")
        listed_failures.append("missing_domain_authority_basis")
    if not attempted:
        return "missing_domain_authority_basis"
    if listed_failures:
        return _earliest(listed_failures)
    if local_failures:
        return local_failures[0]
    return "missing_domain_authority_basis"


def _bind_reference(
    reference: dict[str, Any],
    envelope: dict[str, Any],
    records: dict[str, dict[str, Any]],
    mode: str,
) -> tuple[str | None, dict[str, Any] | None]:
    record_id = reference.get("id")
    if not isinstance(record_id, str) or record_id not in records:
        return "unresolvable_authority_basis", None
    record = records[record_id]
    if not isinstance(record, dict):
        return "unresolvable_authority_basis", None
    if any(field_name not in record for field_name in RESOLVED_RECORD_REQUIRED):
        return "unresolvable_authority_basis", None
    if reference.get("type") != record.get("type"):
        return "authority_basis_type_mismatch", record
    if mode == "new_exercise":
        currentness = _currentness_reason(reference, record, envelope.get("evaluated_at"))
        if currentness is not None:
            return currentness, record
    subject_ids = record.get("subject_ids")
    if not isinstance(subject_ids, list) or envelope["subject"]["id"] not in subject_ids:
        return "authority_basis_subject_mismatch", record
    if record.get("authority_domain") != envelope["authority_domain"]:
        return "authority_basis_domain_mismatch", record
    operations = record.get("operations")
    if not isinstance(operations, list) or envelope["operation"] not in operations:
        return "authority_basis_operation_mismatch", record
    scopes = record.get("scopes")
    if not isinstance(scopes, list) or envelope["jurisdiction"]["scope"] not in scopes:
        return "authority_basis_scope_mismatch", record
    target_classes = record.get("target_classes")
    if not isinstance(target_classes, list) or envelope["target"]["class"] not in target_classes:
        return "authority_basis_target_class_mismatch", record
    target_ids = record.get("target_ids")
    if isinstance(target_ids, list) and len(target_ids) > 0:
        if envelope["target"]["id"] not in target_ids:
            return "authority_basis_target_id_mismatch", record
    return None, record


def _currentness_reason(
    reference: dict[str, Any], record: dict[str, Any], evaluated_at: Any
) -> str | None:
    evaluated = parse_datetime(evaluated_at)
    valid_from = parse_datetime(record.get("valid_from"))
    valid_until = parse_datetime(record.get("valid_until"))
    if evaluated is None or valid_from is None or valid_until is None:
        return "unparseable_datetime"
    not_current = False
    if reference.get("current") is not True:
        not_current = True
    if record.get("current") is not True:
        not_current = True
    if "revoked_at" in record and record["revoked_at"] is not None:
        revoked_at = parse_datetime(record["revoked_at"])
        if revoked_at is None:
            return "unparseable_datetime"
        if evaluated >= revoked_at:
            not_current = True
    if not_current:
        return "authority_basis_not_current"
    if evaluated < valid_from or evaluated > valid_until:
        return "authority_basis_outside_validity_interval"
    return None


def _qualification_reason(
    envelope: dict[str, Any], _domain: str, domain_spec: dict[str, Any]
) -> str | None:
    if not domain_spec["competence_required"]:
        return None
    qualifications: list[dict[str, Any]] = envelope["competence"]
    if not qualifications:
        return "missing_required_qualification"
    accepted = set(domain_spec["accepted_qualification_types"])
    typed = [item for item in qualifications if item.get("type") in accepted]
    if not typed:
        return "qualification_type_mismatch"
    current = [item for item in typed if item.get("current") is True]
    if not current:
        return "qualification_not_current"
    subject_id = envelope["subject"]["id"]
    subject_ok = [item for item in current if item.get("subject_id") == subject_id]
    if not subject_ok:
        return "qualification_subject_mismatch"
    scope = envelope["jurisdiction"]["scope"]
    scope_ok = [item for item in subject_ok if item.get("scope") == scope]
    if not scope_ok:
        return "qualification_scope_mismatch"
    return None


def _warrant_reason(
    envelope: dict[str, Any], domain: str, domain_spec: dict[str, Any]
) -> str | None:
    basis_req = DOMAIN_BASIS_REQUIREMENTS[domain]
    warrant_present = "warrant" in envelope
    warrant = envelope.get("warrant")
    if not domain_spec["warrant_allowed"]:
        if warrant_present:
            return "warrant_not_allowed_for_domain"
        return None
    if "warrant" in basis_req:
        if not isinstance(warrant, dict):
            return "missing_required_warrant"
        if warrant.get("authority_domain") != envelope["authority_domain"]:
            return "warrant_domain_mismatch"
        if warrant.get("operation") != envelope["operation"]:
            return "warrant_operation_mismatch"
        accepted = domain_spec["accepted_warrant_types"]
        if warrant.get("type") not in accepted:
            return "warrant_type_mismatch"
        if warrant.get("applicable") is not True:
            return "warrant_inapplicable"
        if warrant.get("current") is not True:
            return "warrant_not_current"
        if warrant.get("target_id") != envelope["target"]["id"]:
            return "warrant_target_mismatch"
        if warrant.get("target_hash") != envelope["target"]["current_hash"]:
            return "warrant_target_hash_mismatch"
    return None


def _field_names(fields: Any) -> list[str] | None:
    if fields is None:
        return []
    if isinstance(fields, list):
        if not all(isinstance(item, str) for item in fields):
            return None
        return list(fields)
    if isinstance(fields, dict):
        return [str(key) for key in fields]
    return None


def _parse_propagation(value: Any) -> tuple[Any, Any, bool]:
    if isinstance(value, str):
        return value, None, False
    if isinstance(value, dict):
        return (
            value.get("mode"),
            value.get("fields"),
            value.get("separately_reauthorized") is True,
        )
    return None, None, False


def _envelope_propagation_reasons(
    envelope: dict[str, Any],
) -> tuple[str | None, str | None, list[str]]:
    notes: list[str] = []
    mode_value, fields, reauthorized = _parse_propagation(envelope.get("propagation"))
    if mode_value not in PROPAGATION_MODES:
        return "unknown_propagation_mode", None, notes
    names = _field_names(fields)
    if names is None:
        notes.append("A7_propagation_fields_unreadable")
        return None, "propagation_forbidden_fields", notes
    never_present = [name for name in names if name in NEVER_IMPLICIT_FIELDS]
    reestablishment = [name for name in names if name in REESTABLISHMENT_FIELDS]
    if mode_value == "none":
        if names:
            if reestablishment and not reauthorized:
                return "authority_requires_reestablishment", None, notes
            return None, "propagation_forbidden_fields", notes
        return None, None, notes
    if mode_value == "identity_provenance_only":
        extra = [name for name in names if name not in IDENTITY_PROVENANCE_FIELDS]
        if extra:
            if any(name in REESTABLISHMENT_FIELDS for name in extra) and not reauthorized:
                return "authority_requires_reestablishment", None, notes
            return None, "propagation_forbidden_fields", notes
        return None, None, notes
    # explicit
    if fields is None:
        notes.append("explicit_requires_fields")
        return None, "propagation_forbidden_fields", notes
    if reauthorized:
        return None, None, notes
    if reestablishment:
        return "authority_requires_reestablishment", None, notes
    if never_present:
        return None, "propagation_forbidden_fields", notes
    return None, None, notes


def evaluate_propagation(request: Any, mode: str = "new_exercise") -> Decision:
    kind = "propagation"
    notes: list[str] = []
    if mode not in MODES:
        mode = "new_exercise"
    if not isinstance(request, dict):
        return _reject("missing_required_field", kind, mode)
    if "mode" not in request and "propagation" in request:
        listed, local, extra_notes = _envelope_propagation_reasons(request)
    else:
        listed, local, extra_notes = _envelope_propagation_reasons({"propagation": request})
    notes.extend(extra_notes)
    if listed is not None:
        return _reject(listed, kind, mode, notes)
    if local is not None:
        return _reject(local, kind, mode, notes)
    return _accept(kind, mode, notes)


def _delegation_shape_reason(obj: Any) -> str | None:
    if not isinstance(obj, dict):
        return "missing_required_field"
    if "operations" in obj:
        operations = obj["operations"]
        if not isinstance(operations, list) or len(operations) < 1:
            return "malformed_delegation_operations_shape"
        if not all(isinstance(item, str) for item in operations):
            return "malformed_delegation_operations_shape"
    if "scope" in obj:
        scope = obj["scope"]
        if not isinstance(scope, list) or len(scope) < 1:
            return "malformed_delegation_scope_shape"
        if not all(isinstance(item, str) for item in scope):
            return "malformed_delegation_scope_shape"
    return None


def evaluate_delegation(parent: Any, child: Any, mode: str = "new_exercise") -> Decision:
    kind = "delegation"
    notes: list[str] = []
    if mode not in MODES:
        mode = "new_exercise"
    for obj in (parent, child):
        shape = _delegation_shape_reason(obj)
        if shape is not None:
            return _reject(shape, kind, mode, notes)
    assert isinstance(parent, dict)
    assert isinstance(child, dict)
    for obj in (parent, child):
        if any(field_name not in obj for field_name in DELEGATION_REQUIRED):
            return _reject("missing_required_field", kind, mode, notes)
    if mode == "new_exercise":
        if parent.get("current") is not True or child.get("current") is not True:
            return _reject("authority_basis_not_current", kind, mode, notes)
    if not set(child["operations"]) <= set(parent["operations"]):
        return _reject("delegation_operation_amplification", kind, mode, notes)
    if not set(child["scope"]) <= set(parent["scope"]):
        return _reject("delegation_scope_amplification", kind, mode, notes)
    parent_until = parent.get("valid_until")
    child_until = child.get("valid_until")
    if parent_until is not None and parent_until != "":
        if child_until is None or child_until == "":
            notes.append("A_child_unbounded_vs_parent_expiry")
            return _reject("delegation_expiry_amplification", kind, mode, notes)
        parent_dt = parse_datetime(parent_until)
        child_dt = parse_datetime(child_until)
        if parent_dt is None or child_dt is None:
            return _reject("unparseable_datetime", kind, mode, notes)
        if child_dt > parent_dt:
            return _reject("delegation_expiry_amplification", kind, mode, notes)
    return _accept(kind, mode, notes)


def evaluate_historical(
    record: Any, registry: Any = None, mode: str = "historical_inspection"
) -> Decision:
    kind = "historical"
    notes: list[str] = []
    if mode not in MODES:
        mode = "historical_inspection"
    if not isinstance(record, dict):
        return _reject("missing_required_field", kind, mode)
    if any(field_name not in record for field_name in HISTORICAL_REQUIRED):
        return _reject("missing_required_field", kind, mode, notes)
    if registry is not None:
        notes.append("registry_not_used_to_rewrite_historical_fact")
    # Never rewrite the stored fact from later currentness or revocation.
    if mode == "historical_inspection":
        notes.append("later_currentness_does_not_rewrite_historical_fact")
        return _accept(kind, mode, notes)
    notes.append("new_exercise_requires_current_recheck")
    notes.append("historical_record_lacks_live_reference_current_conjunction")
    return _reject("authority_basis_not_current", kind, mode, notes)
