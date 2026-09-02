"""Independent clean-room implementation of Contract E candidate RC1."""

from __future__ import annotations

import copy
import datetime as _dt
import hashlib
import json
import math
import re
from fractions import Fraction
from typing import Any


_STATE_SCHEMA = "contract-e-authority-state-candidate-rc1"
_REQUEST_SCHEMA = "contract-e-authorization-request-candidate-rc1"
_RECEIPT_SCHEMA = "contract-e-authorization-receipt-candidate-rc1"
_SHA_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_TS_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?Z$"
)

_STATE_KEYS = {"schema", "authority_state_id", "records"}
_RECORD_KEYS = {
    "id",
    "basis_type",
    "subject_id",
    "domain",
    "operation",
    "scope",
    "target_class",
    "target_ref",
    "valid_from",
    "valid_until",
    "revoked_at",
    "parent_id",
    "delegated_by",
}
_REQUEST_KEYS = {
    "schema",
    "request_id",
    "authority_state_id",
    "evaluation_time",
    "subject_id",
    "jurisdiction",
    "references",
    "supporting_artifacts",
    "conflicts",
    "residues",
}
_JURISDICTION_KEYS = {"domain", "operation", "scope", "target_class", "target_ref"}
_REFERENCE_KEYS = {"ref_id", "kind", "version", "immutable_id", "identity_sha256"}
_ARTIFACT_KEYS = {"id", "artifact_type", "ref_id"}
_BLOCKER_KEYS = {"id", "relevant", "status"}


class _CanonicalizationError(ValueError):
    pass


def _is_nonempty_string(value: Any) -> bool:
    return type(value) is str and len(value) > 0


def _is_sha256(value: Any) -> bool:
    return type(value) is str and _SHA_RE.fullmatch(value) is not None


def _validate_json_value(value: Any, active: set[int]) -> None:
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise _CanonicalizationError("non-finite number")
        return
    if type(value) is list:
        marker = id(value)
        if marker in active:
            raise _CanonicalizationError("cyclic container")
        active.add(marker)
        try:
            for item in value:
                _validate_json_value(item, active)
        finally:
            active.remove(marker)
        return
    if type(value) is dict:
        marker = id(value)
        if marker in active:
            raise _CanonicalizationError("cyclic container")
        active.add(marker)
        try:
            for key, item in value.items():
                if type(key) is not str:
                    raise _CanonicalizationError("non-string object key")
                _validate_json_value(item, active)
        finally:
            active.remove(marker)
        return
    raise _CanonicalizationError("host-only/non-JSON value")


def _canonical_bytes(value: Any) -> bytes:
    _validate_json_value(value, set())
    try:
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ) + "\n"
        return rendered.encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise _CanonicalizationError(str(exc)) from exc


def _identity(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _parse_timestamp(value: Any):
    if type(value) is not str:
        return None
    match = _TS_RE.fullmatch(value)
    if match is None:
        return None
    year, month, day, hour, minute, second = map(int, match.groups()[:6])
    fraction_text = match.group(7)
    try:
        base = _dt.datetime(
            year, month, day, hour, minute, second, tzinfo=_dt.timezone.utc
        )
    except ValueError:
        return None
    fraction = (
        Fraction(int(fraction_text), 10 ** len(fraction_text))
        if fraction_text is not None
        else Fraction(0, 1)
    )
    return base, fraction


def _valid_nullable_nonempty(value: Any) -> bool:
    return value is None or _is_nonempty_string(value)


def _valid_nullable_timestamp(value: Any) -> bool:
    return value is None or _parse_timestamp(value) is not None


def _valid_jurisdiction(value: Any) -> bool:
    return (
        type(value) is dict
        and set(value) == _JURISDICTION_KEYS
        and _is_nonempty_string(value["domain"])
        and _is_nonempty_string(value["operation"])
        and _is_nonempty_string(value["scope"])
        and _is_nonempty_string(value["target_class"])
        and _is_sha256(value["target_ref"])
    )


def _valid_record_schema(record: Any) -> bool:
    return (
        type(record) is dict
        and set(record) == _RECORD_KEYS
        and _is_nonempty_string(record["id"])
        and type(record["basis_type"]) is str
        and record["basis_type"] in {"grant", "policy", "delegation"}
        and _is_nonempty_string(record["subject_id"])
        and _is_nonempty_string(record["domain"])
        and _is_nonempty_string(record["operation"])
        and _is_nonempty_string(record["scope"])
        and _is_nonempty_string(record["target_class"])
        and _is_sha256(record["target_ref"])
        and _parse_timestamp(record["valid_from"]) is not None
        and _valid_nullable_timestamp(record["valid_until"])
        and _valid_nullable_timestamp(record["revoked_at"])
        and _valid_nullable_nonempty(record["parent_id"])
        and _valid_nullable_nonempty(record["delegated_by"])
    )


def _valid_reference_schema(reference: Any) -> bool:
    return (
        type(reference) is dict
        and set(reference) == _REFERENCE_KEYS
        and _is_nonempty_string(reference["ref_id"])
        and _is_nonempty_string(reference["kind"])
        and (reference["version"] is None or _is_nonempty_string(reference["version"]))
        and _is_nonempty_string(reference["immutable_id"])
        and _is_sha256(reference["identity_sha256"])
    )


def _reference_identity_valid(reference: dict) -> bool:
    payload = {
        "kind": reference["kind"],
        "version": reference["version"],
        "immutable_id": reference["immutable_id"],
    }
    try:
        return reference["identity_sha256"] == _identity(payload)
    except _CanonicalizationError:
        return False


def _valid_artifact_schema(artifact: Any) -> bool:
    return (
        type(artifact) is dict
        and set(artifact) == _ARTIFACT_KEYS
        and _is_nonempty_string(artifact["id"])
        and _is_nonempty_string(artifact["artifact_type"])
        and _is_nonempty_string(artifact["ref_id"])
    )


def _valid_blocker_schema(blocker: Any) -> bool:
    return (
        type(blocker) is dict
        and set(blocker) == _BLOCKER_KEYS
        and _is_nonempty_string(blocker["id"])
        and type(blocker["relevant"]) is bool
        and type(blocker["status"]) is str
        and blocker["status"] in {"unresolved", "contested"}
    )


def _list_of(value: Any, predicate, *, min_items: int = 0) -> bool:
    return (
        type(value) is list
        and len(value) >= min_items
        and all(predicate(x) for x in value)
    )


def _validate_authority_state(authority_state: Any, diagnostics: set[str]):
    recomputed_id = None
    json_safe = True
    try:
        if type(authority_state) is not dict:
            raise _CanonicalizationError("authority state is not an object")
        payload = {
            key: value
            for key, value in authority_state.items()
            if key != "authority_state_id"
        }
        recomputed_id = _identity(payload)
    except _CanonicalizationError:
        json_safe = False
        diagnostics.add("INVALID_AUTHORITY_STATE_JSON")

    structural = (
        type(authority_state) is dict
        and set(authority_state) == _STATE_KEYS
        and authority_state.get("schema") == _STATE_SCHEMA
        and _is_sha256(authority_state.get("authority_state_id"))
        and _list_of(authority_state.get("records"), _valid_record_schema, min_items=1)
    )
    if not structural:
        diagnostics.add("INVALID_AUTHORITY_STATE_SCHEMA")

    chain_valid = structural
    if structural:
        records = authority_state["records"]
        seen: set[str] = set()
        root = records[0]
        if root["basis_type"] not in {"grant", "policy"}:
            chain_valid = False
        if root["parent_id"] is not None or root["delegated_by"] is not None:
            chain_valid = False
        for index, record in enumerate(records):
            if record["id"] in seen:
                chain_valid = False
            seen.add(record["id"])
            if index == 0:
                continue
            parent = records[index - 1]
            if record["basis_type"] != "delegation":
                chain_valid = False
            if record["parent_id"] != parent["id"]:
                chain_valid = False
            if record["delegated_by"] != parent["subject_id"]:
                chain_valid = False
            for field in ("domain", "operation", "scope", "target_class", "target_ref"):
                if record[field] != parent[field]:
                    chain_valid = False
        if not chain_valid:
            diagnostics.add("INVALID_AUTHORITY_CHAIN")

    identity_valid = (
        json_safe
        and structural
        and recomputed_id is not None
        and authority_state["authority_state_id"] == recomputed_id
    )
    if structural and json_safe and not identity_valid:
        diagnostics.add("AUTHORITY_STATE_ID_MISMATCH")

    return structural and chain_valid and identity_valid, recomputed_id


def _validate_request(request: Any, diagnostics: set[str]):
    request_sha = None
    json_safe = True
    try:
        request_sha = _identity(request)
    except _CanonicalizationError:
        json_safe = False
        diagnostics.add("INVALID_REQUEST_JSON")

    structural = (
        type(request) is dict
        and set(request) == _REQUEST_KEYS
        and request.get("schema") == _REQUEST_SCHEMA
        and _is_nonempty_string(request.get("request_id"))
        and _is_sha256(request.get("authority_state_id"))
        and _parse_timestamp(request.get("evaluation_time")) is not None
        and _is_nonempty_string(request.get("subject_id"))
        and _valid_jurisdiction(request.get("jurisdiction"))
        and _list_of(request.get("references"), _valid_reference_schema, min_items=1)
        and _list_of(request.get("supporting_artifacts"), _valid_artifact_schema)
        and _list_of(request.get("conflicts"), _valid_blocker_schema)
        and _list_of(request.get("residues"), _valid_blocker_schema)
    )
    if not structural:
        diagnostics.add("INVALID_REQUEST_SCHEMA")
        return False, request_sha, set()

    valid_reference_ids: set[str] = set()
    reference_identities_valid = True
    for reference in request["references"]:
        if not _reference_identity_valid(reference):
            reference_identities_valid = False
        else:
            valid_reference_ids.add(reference["identity_sha256"])
    if not reference_identities_valid:
        diagnostics.add("INVALID_REFERENCE_IDENTITY")

    local_ref_ids = {reference["ref_id"] for reference in request["references"]}
    artifacts_resolve = all(
        artifact["ref_id"] in local_ref_ids for artifact in request["supporting_artifacts"]
    )
    if not artifacts_resolve:
        diagnostics.add("INVALID_SUPPORTING_ARTIFACT_REFERENCE")

    return json_safe and reference_identities_valid and artifacts_resolve, request_sha, valid_reference_ids


def _current_at(record: dict, evaluation_time) -> bool:
    valid_from = _parse_timestamp(record["valid_from"])
    valid_until = (
        _parse_timestamp(record["valid_until"])
        if record["valid_until"] is not None
        else None
    )
    revoked_at = (
        _parse_timestamp(record["revoked_at"])
        if record["revoked_at"] is not None
        else None
    )
    if evaluation_time < valid_from:
        return False
    if valid_until is not None and evaluation_time > valid_until:
        return False
    if revoked_at is not None and evaluation_time >= revoked_at:
        return False
    return True


def _safe_preserved(request: Any) -> dict:
    empty = {
        "references": [],
        "supporting_artifacts": [],
        "conflicts": [],
        "residues": [],
    }
    if type(request) is not dict:
        return empty
    result = {}
    result["references"] = (
        copy.deepcopy(request["references"])
        if _list_of(request.get("references"), _valid_reference_schema)
        else []
    )
    result["supporting_artifacts"] = (
        copy.deepcopy(request["supporting_artifacts"])
        if _list_of(request.get("supporting_artifacts"), _valid_artifact_schema)
        else []
    )
    result["conflicts"] = (
        copy.deepcopy(request["conflicts"])
        if _list_of(request.get("conflicts"), _valid_blocker_schema)
        else []
    )
    result["residues"] = (
        copy.deepcopy(request["residues"])
        if _list_of(request.get("residues"), _valid_blocker_schema)
        else []
    )
    return result


def evaluate(authority_state: dict, request: dict) -> dict:
    """Evaluate exact standing authority against an exact authorization request."""

    diagnostics: set[str] = set()
    state_valid, recomputed_state_id = _validate_authority_state(authority_state, diagnostics)
    request_valid, request_sha, valid_reference_ids = _validate_request(request, diagnostics)

    authorized = state_valid and request_valid

    if authorized:
        if request["authority_state_id"] != authority_state["authority_state_id"]:
            diagnostics.add("AUTHORITY_STATE_REQUEST_MISMATCH")
            authorized = False

    if authorized:
        resolution_request = (
            request["jurisdiction"]["domain"] == "resolution"
            and request["jurisdiction"]["operation"] == "resolve"
        )
        if not resolution_request:
            blockers = request["conflicts"] + request["residues"]
            if any(
                blocker["relevant"]
                and blocker["status"] in {"unresolved", "contested"}
                for blocker in blockers
            ):
                diagnostics.add("BLOCKING_CONFLICT_OR_RESIDUE")
                authorized = False

    if authorized:
        evaluation_time = _parse_timestamp(request["evaluation_time"])
        if not all(_current_at(record, evaluation_time) for record in authority_state["records"]):
            diagnostics.add("AUTHORITY_RECORD_NOT_CURRENT")
            authorized = False

    if authorized:
        terminal = authority_state["records"][-1]
        if terminal["subject_id"] != request["subject_id"]:
            diagnostics.add("SUBJECT_MISMATCH")
            authorized = False

    if authorized:
        terminal = authority_state["records"][-1]
        jurisdiction = request["jurisdiction"]
        for field in ("domain", "operation", "scope", "target_class", "target_ref"):
            if terminal[field] != jurisdiction[field]:
                diagnostics.add("JURISDICTION_MISMATCH")
                authorized = False
                break

    if authorized:
        if request["jurisdiction"]["target_ref"] not in valid_reference_ids:
            diagnostics.add("TARGET_REFERENCE_NOT_FOUND")
            authorized = False

    request_canonicalizable = request_sha is not None
    request_id = (
        request.get("request_id")
        if (
            request_canonicalizable
            and type(request) is dict
            and _is_nonempty_string(request.get("request_id"))
        )
        else None
    )
    evaluation_time_text = (
        request.get("evaluation_time")
        if (
            request_canonicalizable
            and type(request) is dict
            and _parse_timestamp(request.get("evaluation_time")) is not None
        )
        else None
    )
    subject_id = (
        request.get("subject_id")
        if (
            request_canonicalizable
            and type(request) is dict
            and _is_nonempty_string(request.get("subject_id"))
        )
        else None
    )
    jurisdiction = (
        copy.deepcopy(request["jurisdiction"])
        if (
            request_canonicalizable
            and type(request) is dict
            and _valid_jurisdiction(request.get("jurisdiction"))
        )
        else None
    )

    receipt = {
        "schema": _RECEIPT_SCHEMA,
        "receipt_id": None,
        "authority_conferring": False,
        "authorized": bool(authorized),
        "request_id": request_id,
        "request_sha256": request_sha,
        "authority_state_id": recomputed_state_id,
        "evaluation_time": evaluation_time_text,
        "subject_id": subject_id,
        "jurisdiction": jurisdiction,
        "authority_basis_id": authority_state["records"][-1]["id"] if authorized else None,
        "preserved": (
            _safe_preserved(request)
            if request_canonicalizable
            else {
                "references": [],
                "supporting_artifacts": [],
                "conflicts": [],
                "residues": [],
            }
        ),
        "diagnostics": sorted(diagnostics),
    }
    semantic_receipt = {
        key: value
        for key, value in receipt.items()
        if key not in {"receipt_id", "diagnostics"}
    }
    receipt["receipt_id"] = _identity(semantic_receipt)
    return receipt
