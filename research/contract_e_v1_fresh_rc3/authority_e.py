"""Fresh independent Contract E RC3 authority evaluation reproduction.

This module is intentionally self-contained.  It implements the public RC3
specification and its machine-schema constraints without relying on any
project-specific implementation.
"""

from __future__ import annotations

import copy
import hashlib
import math
import re
from typing import Any, Callable, Optional


_STATE_SCHEMA = "contract-e-authority-state-candidate-rc3"
_REQUEST_SCHEMA = "contract-e-authorization-request-candidate-rc3"
_RECEIPT_SCHEMA = "contract-e-authorization-receipt-candidate-rc3"
_SHA_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
_TS_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?Z$"
)
_SAFE_INTEGER = 9007199254740991


class _CanonicalizationError(ValueError):
    pass


def _valid_unicode_string(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    # RFC 8785 operates on Unicode scalar values; lone surrogates are not
    # valid I-JSON strings.
    return not any(0xD800 <= ord(ch) <= 0xDFFF for ch in value)


def _nonempty(value: Any) -> bool:
    return _valid_unicode_string(value) and len(value) > 0


def _sha256_string(value: Any) -> bool:
    return _valid_unicode_string(value) and _SHA_RE.fullmatch(value) is not None


def _json_quote(value: str) -> str:
    if not _valid_unicode_string(value):
        raise _CanonicalizationError("invalid Unicode string")
    out = ['"']
    escapes = {
        '"': '\\"',
        "\\": "\\\\",
        "\b": "\\b",
        "\t": "\\t",
        "\n": "\\n",
        "\f": "\\f",
        "\r": "\\r",
    }
    for ch in value:
        escaped = escapes.get(ch)
        if escaped is not None:
            out.append(escaped)
        elif ord(ch) < 0x20:
            out.append("\\u%04x" % ord(ch))
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def _float_to_ecmascript(value: float) -> str:
    if not math.isfinite(value):
        raise _CanonicalizationError("non-finite number")
    if value == 0.0:
        return "0"

    sign = "-" if value < 0 else ""
    text = repr(abs(value)).lower()
    if "e" in text:
        mantissa, exponent_text = text.split("e", 1)
        exponent = int(exponent_text)
    else:
        mantissa = text
        exponent = 0

    if "." in mantissa:
        point = mantissa.index(".")
        raw_digits = mantissa.replace(".", "")
    else:
        point = len(mantissa)
        raw_digits = mantissa

    leading = len(raw_digits) - len(raw_digits.lstrip("0"))
    digits = raw_digits.lstrip("0").rstrip("0")
    if not digits:
        return "0"

    k = point + exponent - leading
    n = len(digits)

    if 0 < k <= 21:
        if n <= k:
            rendered = digits + ("0" * (k - n))
        else:
            rendered = digits[:k] + "." + digits[k:]
    elif -6 < k <= 0:
        rendered = "0." + ("0" * (-k)) + digits
    else:
        if n == 1:
            rendered = digits
        else:
            rendered = digits[0] + "." + digits[1:]
        exp = k - 1
        rendered += "e" + ("+" if exp >= 0 else "") + str(exp)
    return sign + rendered


def _number_to_jcs(value: Any) -> str:
    if isinstance(value, bool):
        raise _CanonicalizationError("boolean is not a number here")
    if isinstance(value, int):
        if value < -_SAFE_INTEGER or value > _SAFE_INTEGER:
            raise _CanonicalizationError("integer outside interoperable IEEE-754 domain")
        return str(value)
    if isinstance(value, float):
        return _float_to_ecmascript(value)
    raise _CanonicalizationError("unsupported number")


def _utf16_sort_key(value: str) -> bytes:
    if not _valid_unicode_string(value):
        raise _CanonicalizationError("invalid object key")
    return value.encode("utf-16-be")


def _canonical_text(value: Any, active: Optional[set[int]] = None) -> str:
    if active is None:
        active = set()

    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, str):
        return _json_quote(value)
    if isinstance(value, int) and not isinstance(value, bool):
        return _number_to_jcs(value)
    if isinstance(value, float):
        return _number_to_jcs(value)

    if isinstance(value, list):
        identity = id(value)
        if identity in active:
            raise _CanonicalizationError("cyclic array")
        active.add(identity)
        try:
            return "[" + ",".join(_canonical_text(item, active) for item in value) + "]"
        finally:
            active.remove(identity)

    if isinstance(value, dict):
        identity = id(value)
        if identity in active:
            raise _CanonicalizationError("cyclic object")
        for key in value:
            if not isinstance(key, str):
                raise _CanonicalizationError("non-string object key")
            if not _valid_unicode_string(key):
                raise _CanonicalizationError("invalid Unicode object key")
        active.add(identity)
        try:
            pieces = []
            for key in sorted(value.keys(), key=_utf16_sort_key):
                pieces.append(_json_quote(key) + ":" + _canonical_text(value[key], active))
            return "{" + ",".join(pieces) + "}"
        finally:
            active.remove(identity)

    raise _CanonicalizationError("unsupported host value")


def _canonical_bytes(value: Any) -> bytes:
    return (_canonical_text(value) + "\n").encode("utf-8")


def _hash_json(value: Any) -> Optional[str]:
    try:
        return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()
    except (TypeError, ValueError, OverflowError, UnicodeError):
        return None


def _is_canonicalizable(value: Any) -> bool:
    return _hash_json(value) is not None


def _exact_keys(value: Any, required: set[str]) -> bool:
    return isinstance(value, dict) and set(value.keys()) == required


def _valid_gregorian_date(year: int, month: int, day: int) -> bool:
    if year < 1 or year > 9999 or month < 1 or month > 12 or day < 1:
        return False
    month_lengths = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    if leap:
        month_lengths[1] = 29
    return day <= month_lengths[month - 1]


def _parse_timestamp(value: Any) -> Optional[tuple[tuple[int, int, int, int, int, int], str]]:
    if not _valid_unicode_string(value):
        return None
    match = _TS_RE.fullmatch(value)
    if match is None:
        return None
    year, month, day, hour, minute, second = map(int, match.groups()[:6])
    fraction = match.group(7) or ""
    if not _valid_gregorian_date(year, month, day):
        return None
    if hour > 23 or minute > 59 or second > 59:
        return None
    return ((year, month, day, hour, minute, second), fraction.rstrip("0"))


def _timestamp_valid(value: Any) -> bool:
    return _parse_timestamp(value) is not None


def _compare_timestamps(left: str, right: str) -> int:
    lparsed = _parse_timestamp(left)
    rparsed = _parse_timestamp(right)
    if lparsed is None or rparsed is None:
        raise ValueError("invalid timestamp")
    lbase, lfrac = lparsed
    rbase, rfrac = rparsed
    if lbase < rbase:
        return -1
    if lbase > rbase:
        return 1
    width = max(len(lfrac), len(rfrac))
    lpadded = lfrac.ljust(width, "0")
    rpadded = rfrac.ljust(width, "0")
    if lpadded < rpadded:
        return -1
    if lpadded > rpadded:
        return 1
    return 0


def _valid_jurisdiction(value: Any) -> bool:
    required = {"domain", "operation", "scope", "target_class", "target_ref"}
    if not _exact_keys(value, required):
        return False
    return (
        _nonempty(value["domain"])
        and _nonempty(value["operation"])
        and _nonempty(value["scope"])
        and _nonempty(value["target_class"])
        and _sha256_string(value["target_ref"])
    )


def _valid_authority_record_shape(value: Any) -> bool:
    required = {
        "id", "basis_type", "subject_id", "domain", "operation", "scope",
        "target_class", "target_ref", "valid_from", "valid_until",
        "revoked_at", "parent_id", "delegated_by",
    }
    if not _exact_keys(value, required):
        return False
    if not _nonempty(value["id"]):
        return False
    if value["basis_type"] not in {"grant", "policy", "delegation"}:
        return False
    for key in ("subject_id", "domain", "operation", "scope", "target_class"):
        if not _nonempty(value[key]):
            return False
    if not _sha256_string(value["target_ref"]):
        return False
    if not _timestamp_valid(value["valid_from"]):
        return False
    if value["valid_until"] is not None and not _timestamp_valid(value["valid_until"]):
        return False
    if value["revoked_at"] is not None and not _timestamp_valid(value["revoked_at"]):
        return False
    if value["parent_id"] is not None and not _nonempty(value["parent_id"]):
        return False
    if value["delegated_by"] is not None and not _nonempty(value["delegated_by"]):
        return False
    return True


def _valid_state_shape(value: Any) -> bool:
    required = {"schema", "authority_state_id", "records"}
    if not _exact_keys(value, required):
        return False
    if value["schema"] != _STATE_SCHEMA or not _sha256_string(value["authority_state_id"]):
        return False
    records = value["records"]
    return isinstance(records, list) and len(records) >= 1 and all(
        _valid_authority_record_shape(record) for record in records
    )


def _valid_reference_shape(value: Any) -> bool:
    required = {"ref_id", "kind", "version", "immutable_id", "identity_sha256"}
    if not _exact_keys(value, required):
        return False
    return (
        _nonempty(value["ref_id"])
        and _nonempty(value["kind"])
        and (value["version"] is None or _nonempty(value["version"]))
        and _nonempty(value["immutable_id"])
        and _sha256_string(value["identity_sha256"])
    )


def _valid_supporting_artifact_shape(value: Any) -> bool:
    required = {"id", "artifact_type", "ref_id"}
    return _exact_keys(value, required) and (
        _nonempty(value["id"])
        and _nonempty(value["artifact_type"])
        and _nonempty(value["ref_id"])
    )


def _valid_blocker_shape(value: Any) -> bool:
    required = {"id", "relevant", "status"}
    return _exact_keys(value, required) and (
        _nonempty(value["id"])
        and type(value["relevant"]) is bool
        and value["status"] in {"unresolved", "contested"}
    )


def _valid_request_shape(value: Any) -> bool:
    required = {
        "schema", "request_id", "authority_state_id", "evaluation_time",
        "subject_id", "jurisdiction", "references", "supporting_artifacts",
        "conflicts", "residues",
    }
    if not _exact_keys(value, required):
        return False
    if value["schema"] != _REQUEST_SCHEMA:
        return False
    if not _nonempty(value["request_id"]) or not _sha256_string(value["authority_state_id"]):
        return False
    if not _timestamp_valid(value["evaluation_time"]) or not _nonempty(value["subject_id"]):
        return False
    if not _valid_jurisdiction(value["jurisdiction"]):
        return False
    if not isinstance(value["references"], list) or len(value["references"]) < 1:
        return False
    if not all(_valid_reference_shape(item) for item in value["references"]):
        return False
    if not isinstance(value["supporting_artifacts"], list) or not all(
        _valid_supporting_artifact_shape(item) for item in value["supporting_artifacts"]
    ):
        return False
    if not isinstance(value["conflicts"], list) or not all(
        _valid_blocker_shape(item) for item in value["conflicts"]
    ):
        return False
    if not isinstance(value["residues"], list) or not all(
        _valid_blocker_shape(item) for item in value["residues"]
    ):
        return False
    return True


def _safe_preserve_list(request: Any, key: str, item_validator: Callable[[Any], bool], request_shape_valid: bool) -> list:
    if not isinstance(request, dict) or key not in request:
        return []
    value = request[key]
    if request_shape_valid:
        # The complete request shape guarantees all four list values are safe
        # schema-shaped observations.
        return copy.deepcopy(value)
    if isinstance(value, list) and all(item_validator(item) for item in value):
        return copy.deepcopy(value)
    return []


def _state_identity(state: Any) -> Optional[str]:
    if not isinstance(state, dict):
        return None
    candidate = {key: value for key, value in state.items() if key != "authority_state_id"}
    return _hash_json(candidate)


def _reference_identity(reference: dict) -> Optional[str]:
    projection = {
        "kind": reference["kind"],
        "version": reference["version"],
        "immutable_id": reference["immutable_id"],
    }
    return _hash_json(projection)


def _unique_by(items: list[dict], key: str) -> bool:
    seen = set()
    for item in items:
        value = item[key]
        if value in seen:
            return False
        seen.add(value)
    return True


def _chain_valid(records: list[dict]) -> bool:
    if not records:
        return False
    root = records[0]
    if root["basis_type"] not in {"grant", "policy"}:
        return False
    if root["parent_id"] is not None or root["delegated_by"] is not None:
        return False

    seen_ids = {root["id"]}
    invariant_keys = ("domain", "operation", "scope", "target_class", "target_ref")
    previous = root
    for record in records[1:]:
        if record["id"] in seen_ids:
            return False
        seen_ids.add(record["id"])
        if record["basis_type"] != "delegation":
            return False
        if record["parent_id"] != previous["id"]:
            return False
        if record["delegated_by"] != previous["subject_id"]:
            return False
        if any(record[key] != previous[key] for key in invariant_keys):
            return False
        previous = record
    return True


def _all_records_current(records: list[dict], evaluation_time: str) -> bool:
    for record in records:
        if _compare_timestamps(evaluation_time, record["valid_from"]) < 0:
            return False
        if record["valid_until"] is not None and _compare_timestamps(evaluation_time, record["valid_until"]) > 0:
            return False
        if record["revoked_at"] is not None and _compare_timestamps(evaluation_time, record["revoked_at"]) >= 0:
            return False
    return True


def _request_semantics_valid(request: dict) -> bool:
    references = request["references"]
    if not _unique_by(references, "ref_id"):
        return False
    for reference in references:
        if _reference_identity(reference) != reference["identity_sha256"]:
            return False

    target_matches = [
        reference for reference in references
        if reference["identity_sha256"] == request["jurisdiction"]["target_ref"]
    ]
    if len(target_matches) != 1:
        return False

    artifacts = request["supporting_artifacts"]
    if not _unique_by(artifacts, "id"):
        return False
    ref_ids = {reference["ref_id"] for reference in references}
    if any(artifact["ref_id"] not in ref_ids for artifact in artifacts):
        return False

    if not _unique_by(request["conflicts"], "id"):
        return False
    if not _unique_by(request["residues"], "id"):
        return False
    return True


def _has_relevant_blocker(request: dict) -> bool:
    return any(item["relevant"] for item in request["conflicts"]) or any(
        item["relevant"] for item in request["residues"]
    )


def _individual_request_id(request: Any) -> Optional[str]:
    if isinstance(request, dict) and _nonempty(request.get("request_id")):
        return request["request_id"]
    return None


def _individual_timestamp(request: Any) -> Optional[str]:
    if isinstance(request, dict) and _timestamp_valid(request.get("evaluation_time")):
        return request["evaluation_time"]
    return None


def _individual_subject(request: Any) -> Optional[str]:
    if isinstance(request, dict) and _nonempty(request.get("subject_id")):
        return request["subject_id"]
    return None


def _individual_jurisdiction(request: Any) -> Optional[dict]:
    if isinstance(request, dict) and _valid_jurisdiction(request.get("jurisdiction")):
        return copy.deepcopy(request["jurisdiction"])
    return None


def _diagnose(condition: bool, code: str, diagnostics: list[str]) -> None:
    if not condition and code not in diagnostics:
        diagnostics.append(code)


def evaluate(authority_state: dict, request: dict) -> dict:
    """Evaluate one AuthorityState against one AuthorizationRequest.

    The returned AuthorizationReceipt is deterministic apart from diagnostics,
    which are deliberately excluded from the receipt's semantic identity.
    """

    diagnostics: list[str] = []

    claimed_state_id = None
    if isinstance(authority_state, dict) and _sha256_string(authority_state.get("authority_state_id")):
        claimed_state_id = authority_state["authority_state_id"]

    recomputed_state_id = _state_identity(authority_state)
    request_sha256 = _hash_json(request)

    state_shape_valid = _valid_state_shape(authority_state)
    request_shape_valid = _valid_request_shape(request)

    _diagnose(state_shape_valid, "invalid_authority_state", diagnostics)
    _diagnose(claimed_state_id is not None, "invalid_claimed_authority_state_id", diagnostics)
    _diagnose(recomputed_state_id is not None, "authority_state_not_canonicalizable", diagnostics)
    _diagnose(request_shape_valid, "invalid_authorization_request", diagnostics)

    preserved = {
        "references": _safe_preserve_list(request, "references", _valid_reference_shape, request_shape_valid),
        "supporting_artifacts": _safe_preserve_list(
            request, "supporting_artifacts", _valid_supporting_artifact_shape, request_shape_valid
        ),
        "conflicts": _safe_preserve_list(request, "conflicts", _valid_blocker_shape, request_shape_valid),
        "residues": _safe_preserve_list(request, "residues", _valid_blocker_shape, request_shape_valid),
    }

    identity_matches = (
        state_shape_valid
        and claimed_state_id is not None
        and recomputed_state_id is not None
        and claimed_state_id == recomputed_state_id
    )
    _diagnose(identity_matches, "authority_state_identity_mismatch", diagnostics)

    request_state_binding = False
    request_semantics_valid = False
    blocker_free = False
    current = False
    chain_valid = False
    terminal_matches = False

    if request_shape_valid:
        request_state_binding = identity_matches and request["authority_state_id"] == claimed_state_id
        _diagnose(request_state_binding, "request_authority_state_mismatch", diagnostics)

        request_semantics_valid = _request_semantics_valid(request)
        _diagnose(request_semantics_valid, "invalid_request_references_or_local_ids", diagnostics)

        blocker_free = not _has_relevant_blocker(request)
        _diagnose(blocker_free, "relevant_blocker", diagnostics)

    if state_shape_valid:
        chain_valid = _chain_valid(authority_state["records"])
        _diagnose(chain_valid, "invalid_authority_chain", diagnostics)

    if state_shape_valid and request_shape_valid:
        try:
            current = _all_records_current(authority_state["records"], request["evaluation_time"])
        except ValueError:
            current = False
        _diagnose(current, "authority_not_current", diagnostics)

        terminal = authority_state["records"][-1]
        jurisdiction = request["jurisdiction"]
        terminal_matches = (
            terminal["subject_id"] == request["subject_id"]
            and terminal["domain"] == jurisdiction["domain"]
            and terminal["operation"] == jurisdiction["operation"]
            and terminal["scope"] == jurisdiction["scope"]
            and terminal["target_class"] == jurisdiction["target_class"]
            and terminal["target_ref"] == jurisdiction["target_ref"]
        )
        _diagnose(terminal_matches, "terminal_authority_mismatch", diagnostics)

    authorized = all(
        (
            state_shape_valid,
            identity_matches,
            request_shape_valid,
            request_state_binding,
            request_semantics_valid,
            blocker_free,
            current,
            chain_valid,
            terminal_matches,
        )
    )

    receipt = {
        "schema": _RECEIPT_SCHEMA,
        "receipt_id": None,
        "authority_conferring": False,
        "authorized": authorized,
        "request_id": _individual_request_id(request),
        "request_sha256": request_sha256,
        "claimed_authority_state_id": claimed_state_id,
        "recomputed_authority_state_id": recomputed_state_id,
        "evaluation_time": _individual_timestamp(request),
        "subject_id": _individual_subject(request),
        "jurisdiction": _individual_jurisdiction(request),
        "authority_basis_id": authority_state["records"][-1]["id"] if authorized else None,
        "preserved": preserved,
        "diagnostics": diagnostics,
    }

    semantic_projection = {
        key: value for key, value in receipt.items() if key not in {"receipt_id", "diagnostics"}
    }
    receipt["receipt_id"] = _hash_json(semantic_projection)
    return receipt
