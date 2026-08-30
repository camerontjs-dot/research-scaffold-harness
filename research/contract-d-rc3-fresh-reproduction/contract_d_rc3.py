"""Independent Contract D RC3 consumer derived only from the frozen public authority."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from typing import Any, Mapping

RC3_VERSION = "0.3.0-rc3"
CONTENT_SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

_EFFECTS: dict[str, dict[str, dict[str, dict[str, Any]]]] = {
    "knowledge.add_verified_tag": {
        "1": {
            "scope": {
                "type": "string",
                "required": False,
                "default": "claim",
                "enum": ("claim", "object"),
            }
        }
    },
    "knowledge.cite_as_evidence": {"1": {}},
    "task.dispatch": {"1": {}},
}


class ContractDInvalid(ValueError):
    """Raised when input cannot carry Contract D RC3 authority."""


def _fail(message: str) -> None:
    raise ContractDInvalid(message)


def _pairs_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            _fail(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def _reject_constant(token: str) -> None:
    _fail(f"non-finite JSON number: {token}")


def _assert_finite_json(value: Any, path: str = "$", *, require_string_keys: bool = True) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            _fail(f"non-finite JSON number at {path}")
        return
    if isinstance(value, list):
        for i, item in enumerate(value):
            _assert_finite_json(item, f"{path}[{i}]", require_string_keys=require_string_keys)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if require_string_keys and not isinstance(key, str):
                _fail(f"non-string JSON object key at {path}")
            _assert_finite_json(item, f"{path}.{key}", require_string_keys=require_string_keys)
        return
    _fail(f"non-JSON value at {path}")


def parse_json_document(data: str | bytes) -> Any:
    """Parse JSON while rejecting duplicate keys and non-finite numbers."""
    if isinstance(data, bytes):
        try:
            data = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ContractDInvalid("input is not UTF-8") from exc
    if not isinstance(data, str):
        _fail("JSON input must be str or bytes")
    try:
        value = json.loads(
            data,
            object_pairs_hook=_pairs_without_duplicates,
            parse_constant=_reject_constant,
        )
    except ContractDInvalid:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ContractDInvalid("malformed JSON") from exc
    _assert_finite_json(value)
    return value


def canonical_json_bytes(value: Any) -> bytes:
    """Return normative canonical JSON bytes for finite JSON data."""
    _assert_finite_json(value)
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ContractDInvalid("value is not canonicalizable finite JSON") from exc
    return (text + "\n").encode("utf-8")


def _object(value: Any, path: str, allowed: set[str], required: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(f"{path} must be an object")
    unknown = set(value) - allowed
    if unknown:
        _fail(f"unknown field(s) at {path}: {sorted(unknown)}")
    missing = required - set(value)
    if missing:
        _fail(f"missing field(s) at {path}: {sorted(missing)}")
    return value


def _nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(f"{path} must be a non-empty string")
    return value


def _validate_identity_triple(value: Any, path: str, names: tuple[str, str, str]) -> dict[str, str]:
    obj = _object(value, path, set(names), set(names))
    return {name: _nonempty_string(obj[name], f"{path}.{name}") for name in names}


def _validate_policy(value: Any) -> dict[str, str]:
    obj = _object(value, "$.policy", {"id", "version"}, {"id", "version"})
    return {
        "id": _nonempty_string(obj["id"], "$.policy.id"),
        "version": _nonempty_string(obj["version"], "$.policy.version"),
    }


def _validate_target(value: Any) -> dict[str, str]:
    obj = _object(
        value,
        "$.target",
        {"kind", "id", "content_sha256"},
        {"kind", "id", "content_sha256"},
    )
    out = {
        "kind": _nonempty_string(obj["kind"], "$.target.kind"),
        "id": _nonempty_string(obj["id"], "$.target.id"),
        "content_sha256": _nonempty_string(obj["content_sha256"], "$.target.content_sha256"),
    }
    if not CONTENT_SHA256_RE.fullmatch(out["content_sha256"]):
        _fail("$.target.content_sha256 must be sha256: followed by 64 lowercase hex characters")
    return out


def _normalize_params(effect_type: str, effect_version: str, params: Any, path: str) -> dict[str, Any]:
    versions = _EFFECTS.get(effect_type)
    if versions is None:
        _fail(f"unknown effect type: {effect_type}")
    rules = versions.get(effect_version)
    if rules is None:
        _fail(f"unknown effect version: {effect_type}@{effect_version}")
    if params is None:
        supplied: dict[str, Any] = {}
    else:
        if not isinstance(params, dict):
            _fail(f"{path} must be an object")
        supplied = params
    unknown = set(supplied) - set(rules)
    if unknown:
        _fail(f"unknown effect parameter(s): {sorted(unknown)}")
    normalized: dict[str, Any] = {}
    for name, rule in rules.items():
        if name in supplied:
            value = supplied[name]
        elif "default" in rule:
            value = rule["default"]
        elif rule.get("required"):
            _fail(f"missing required effect parameter: {name}")
        else:
            continue
        if rule.get("type") == "string" and not isinstance(value, str):
            _fail(f"{path}.{name} must be a string")
        if "enum" in rule and value not in rule["enum"]:
            _fail(f"{path}.{name} is outside the registered enum")
        normalized[name] = copy.deepcopy(value)
    return normalized


def normalize_effect(value: Any) -> dict[str, Any]:
    obj = _object(value, "$.effect", {"type", "version", "params"}, {"type", "version"})
    effect_type = _nonempty_string(obj["type"], "$.effect.type")
    effect_version = _nonempty_string(obj["version"], "$.effect.version")
    params = _normalize_params(effect_type, effect_version, obj.get("params"), "$.effect.params")
    return {"type": effect_type, "version": effect_version, "params": params}


def _validate_metadata(value: Any) -> None:
    obj = _object(value, "$.metadata", {"reason_codes", "explanation", "diagnostics"}, set())
    if "reason_codes" in obj:
        if not isinstance(obj["reason_codes"], list):
            _fail("$.metadata.reason_codes must be an array")
        for i, code in enumerate(obj["reason_codes"]):
            _nonempty_string(code, f"$.metadata.reason_codes[{i}]")
    if "explanation" in obj:
        _nonempty_string(obj["explanation"], "$.metadata.explanation")
    if "diagnostics" in obj:
        _assert_finite_json(obj["diagnostics"], "$.metadata.diagnostics")


def validate_contract_d(value: Any) -> dict[str, Any]:
    """Validate one exact Contract D RC3 object and return it unchanged."""
    _assert_finite_json(value)
    obj = _object(
        value,
        "$",
        {"contract_d_version", "input_authority", "policy", "target", "evaluation", "effect", "metadata"},
        {"contract_d_version", "input_authority", "policy", "target", "evaluation"},
    )
    if obj["contract_d_version"] != RC3_VERSION or not isinstance(obj["contract_d_version"], str):
        _fail("unsupported Contract D version")
    _validate_identity_triple(obj["input_authority"], "$.input_authority", ("kind", "id", "immutable_id"))
    _validate_policy(obj["policy"])
    _validate_target(obj["target"])

    evaluation = _object(obj["evaluation"], "$.evaluation", {"state", "disposition"}, {"state"})
    state = evaluation["state"]
    if state == "completed":
        if set(evaluation) != {"state", "disposition"}:
            _fail("completed evaluation requires exactly state and disposition")
        if evaluation["disposition"] not in {"clear", "hold"} or not isinstance(evaluation["disposition"], str):
            _fail("unknown completed disposition")
        if "effect" not in obj:
            _fail("completed evaluation requires effect")
        normalize_effect(obj["effect"])
    elif state == "failed":
        if set(evaluation) != {"state"}:
            _fail("failed evaluation must not contain disposition")
        if "effect" in obj:
            _fail("failed evaluation must not contain effect")
    else:
        _fail("unknown evaluation state")

    if "metadata" in obj:
        _validate_metadata(obj["metadata"])
    return obj


def load_contract_d(data: str | bytes | Mapping[str, Any]) -> dict[str, Any]:
    """Parse/validate a Contract D RC3 object without permissive coercions."""
    if isinstance(data, (str, bytes)):
        value = parse_json_document(data)
    elif isinstance(data, Mapping):
        value = copy.deepcopy(dict(data))
    else:
        _fail("Contract D input must be JSON text/bytes or an object mapping")
    return validate_contract_d(value)


def authority_projection(value: Any) -> dict[str, Any]:
    obj = validate_contract_d(value)
    projection: dict[str, Any] = {
        "contract_d_version": obj["contract_d_version"],
        "input_authority": copy.deepcopy(obj["input_authority"]),
        "policy": copy.deepcopy(obj["policy"]),
        "target": copy.deepcopy(obj["target"]),
        "evaluation": copy.deepcopy(obj["evaluation"]),
    }
    if obj["evaluation"]["state"] == "completed":
        projection["effect"] = normalize_effect(obj["effect"])
    return projection


def semantic_identity(value: Any) -> str:
    payload = canonical_json_bytes(authority_projection(value))
    return "decision:sha256:" + hashlib.sha256(payload).hexdigest()


def _exact_mapping(actual: Any, expected: Mapping[str, Any], keys: tuple[str, ...]) -> bool:
    return all(actual.get(key) == expected.get(key) for key in keys)


def consume(
    decision: str | bytes | Mapping[str, Any],
    *,
    expected_input_authority: Mapping[str, Any],
    expected_policy: Mapping[str, Any],
    expected_target: Mapping[str, Any],
    requested_operation: str,
    requested_effect_params: Mapping[str, Any] | None = None,
) -> str:
    """Evaluate applicability at the Contract-D/Authorization boundary."""
    try:
        obj = load_contract_d(decision)
    except ContractDInvalid:
        return "cannot_establish"

    if not _exact_mapping(obj["input_authority"], expected_input_authority, ("kind", "id", "immutable_id")):
        return "not_applicable"
    if not _exact_mapping(obj["policy"], expected_policy, ("id", "version")):
        return "not_applicable"
    if not _exact_mapping(obj["target"], expected_target, ("kind", "id", "content_sha256")):
        return "not_applicable"

    if obj["evaluation"]["state"] == "failed":
        return "evaluation_failed"

    normalized_effect = normalize_effect(obj["effect"])
    if not isinstance(requested_operation, str) or requested_operation != normalized_effect["type"]:
        return "not_applicable"
    try:
        normalized_requested = _normalize_params(
            normalized_effect["type"],
            normalized_effect["version"],
            {} if requested_effect_params is None else dict(requested_effect_params),
            "$requested_effect_params",
        )
    except (ContractDInvalid, TypeError, ValueError):
        return "not_applicable"
    if normalized_requested != normalized_effect["params"]:
        return "not_applicable"

    if obj["evaluation"]["disposition"] == "hold":
        return "hold"
    return "candidate_for_authorization"
