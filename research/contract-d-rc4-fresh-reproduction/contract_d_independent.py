"""Independent Contract D RC4 consumer derived only from frozen public authority."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import math
import re
from typing import Any

VERSION = "0.3.0-rc4"
OUTCOME_CANDIDATE = "candidate_for_authorization"
OUTCOME_HOLD = "hold"
OUTCOME_FAILED = "evaluation_failed"
OUTCOME_NOT_APPLICABLE = "not_applicable"
OUTCOME_CANNOT_ESTABLISH = "cannot_establish"
ABSENT = object()

EFFECT_REGISTRY = {
    "effect_registry_version": "1",
    "effects": {
        "knowledge.add_verified_tag": {
            "1": {
                "params": {
                    "scope": {
                        "default": "claim",
                        "enum": ["claim", "object"],
                        "required": False,
                        "type": "string",
                    }
                }
            }
        },
        "knowledge.cite_as_evidence": {"1": {"params": {}}},
        "task.dispatch": {"1": {"params": {}}},
    },
}

_HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class ContractDError(ValueError):
    pass


def _finite_json(value: Any, active: set[int] | None = None) -> None:
    if active is None:
        active = set()
    if value is None or isinstance(value, (str, bool)):
        return
    if isinstance(value, int) and not isinstance(value, bool):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractDError("non-finite number")
        return
    if isinstance(value, dict):
        oid = id(value)
        if oid in active:
            raise ContractDError("cyclic host value")
        active.add(oid)
        try:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ContractDError("non-string object key")
                _finite_json(item, active)
        finally:
            active.remove(oid)
        return
    if isinstance(value, list):
        oid = id(value)
        if oid in active:
            raise ContractDError("cyclic host value")
        active.add(oid)
        try:
            for item in value:
                _finite_json(item, active)
        finally:
            active.remove(oid)
        return
    raise ContractDError("host-language-only value")


def _require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractDError(f"{label} must be object")
    return value


def _check_keys(obj: dict[str, Any], allowed: set[str], required: set[str], label: str) -> None:
    unknown = set(obj) - allowed
    if unknown:
        raise ContractDError(f"unknown field in {label}")
    missing = required - set(obj)
    if missing:
        raise ContractDError(f"missing field in {label}")


def _nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractDError(f"{label} must be non-empty string")
    return value


def _validate_binding(obj: Any, label: str, fields: tuple[str, ...]) -> dict[str, Any]:
    value = _require_object(obj, label)
    _check_keys(value, set(fields), set(fields), label)
    for field in fields:
        _nonempty_string(value[field], f"{label}.{field}")
    return value


def _validate_metadata(metadata: Any) -> None:
    obj = _require_object(metadata, "metadata")
    _check_keys(obj, {"reason_codes", "explanation", "diagnostics"}, set(), "metadata")
    if "reason_codes" in obj:
        codes = obj["reason_codes"]
        if not isinstance(codes, list):
            raise ContractDError("metadata.reason_codes must be array")
        for code in codes:
            _nonempty_string(code, "metadata.reason_codes[]")
    if "explanation" in obj:
        _nonempty_string(obj["explanation"], "metadata.explanation")


def _validate_param_value(name: str, value: Any, spec: dict[str, Any]) -> None:
    if spec.get("type") == "string" and not isinstance(value, str):
        raise ContractDError(f"effect param {name} has wrong type")
    if "enum" in spec and value not in spec["enum"]:
        raise ContractDError(f"effect param {name} not in enum")


def normalize_effect(effect: Any) -> dict[str, Any]:
    _finite_json(effect)
    obj = _require_object(effect, "effect")
    _check_keys(obj, {"type", "version", "params"}, {"type", "version"}, "effect")
    effect_type = _nonempty_string(obj["type"], "effect.type")
    effect_version = _nonempty_string(obj["version"], "effect.version")
    try:
        param_schema = EFFECT_REGISTRY["effects"][effect_type][effect_version]["params"]
    except KeyError as exc:
        raise ContractDError("unknown effect type/version") from exc

    params = obj.get("params", {})
    params = _require_object(params, "effect.params")
    unknown = set(params) - set(param_schema)
    if unknown:
        raise ContractDError("unknown effect parameter")

    normalized_params: dict[str, Any] = {}
    for name, spec in param_schema.items():
        if name in params:
            _validate_param_value(name, params[name], spec)
            normalized_params[name] = deepcopy(params[name])
        elif "default" in spec:
            normalized_params[name] = deepcopy(spec["default"])
        elif spec.get("required"):
            raise ContractDError(f"missing required effect parameter {name}")

    return {"type": effect_type, "version": effect_version, "params": normalized_params}


def validate_decision(decision: Any) -> dict[str, Any]:
    _finite_json(decision)
    obj = _require_object(decision, "decision")
    _check_keys(
        obj,
        {"contract_d_version", "input_authority", "policy", "target", "evaluation", "effect", "metadata"},
        {"contract_d_version", "input_authority", "policy", "target", "evaluation"},
        "decision",
    )
    if obj["contract_d_version"] != VERSION or not isinstance(obj["contract_d_version"], str):
        raise ContractDError("unsupported contract version")

    _validate_binding(obj["input_authority"], "input_authority", ("kind", "id", "immutable_id"))
    _validate_binding(obj["policy"], "policy", ("id", "version"))
    target = _validate_binding(obj["target"], "target", ("kind", "id", "content_sha256"))
    if not _HASH_RE.fullmatch(target["content_sha256"]):
        raise ContractDError("invalid target content_sha256")

    evaluation = _require_object(obj["evaluation"], "evaluation")
    state = evaluation.get("state")
    normalized = deepcopy(obj)
    if state == "completed":
        _check_keys(evaluation, {"state", "disposition"}, {"state", "disposition"}, "evaluation")
        if evaluation["disposition"] not in {"clear", "hold"}:
            raise ContractDError("unknown disposition")
        if "effect" not in obj:
            raise ContractDError("completed evaluation requires effect")
        normalized["effect"] = normalize_effect(obj["effect"])
    elif state == "failed":
        _check_keys(evaluation, {"state"}, {"state"}, "evaluation")
        if "effect" in obj:
            raise ContractDError("failed evaluation forbids effect")
    else:
        raise ContractDError("unknown evaluation state")

    if "metadata" in obj:
        _validate_metadata(obj["metadata"])
    return normalized


def parse_json_bytes(payload: bytes | bytearray) -> Any:
    if not isinstance(payload, (bytes, bytearray)):
        raise ContractDError("ingress must be bytes")
    try:
        text = bytes(payload).decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ContractDError("invalid UTF-8") from exc

    def pairs_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in pairs:
            if key in out:
                raise ContractDError("duplicate JSON object key")
            out[key] = value
        return out

    def reject_constant(token: str) -> None:
        raise ContractDError(f"non-finite JSON number {token}")

    try:
        value = json.loads(text, object_pairs_hook=pairs_hook, parse_constant=reject_constant)
    except ContractDError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ContractDError("invalid JSON") from exc
    _finite_json(value)
    return value


def validate_json_bytes(payload: bytes | bytearray) -> dict[str, Any]:
    return validate_decision(parse_json_bytes(payload))


def canonical_json_bytes(value: Any) -> bytes:
    _finite_json(value)
    try:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ContractDError("cannot canonicalize non-JSON value") from exc
    return text.encode("utf-8") + b"\n"


def authority_projection(decision: Any) -> dict[str, Any]:
    normalized = validate_decision(decision)
    projection = {
        "contract_d_version": normalized["contract_d_version"],
        "input_authority": deepcopy(normalized["input_authority"]),
        "policy": deepcopy(normalized["policy"]),
        "target": deepcopy(normalized["target"]),
        "evaluation": deepcopy(normalized["evaluation"]),
    }
    if normalized["evaluation"]["state"] == "completed":
        projection["effect"] = deepcopy(normalized["effect"])
    return projection


def semantic_identity(decision: Any) -> str:
    digest = hashlib.sha256(canonical_json_bytes(authority_projection(decision))).hexdigest()
    return "decision:sha256:" + digest


def _expected_binding_ok(expected: Any, fields: tuple[str, ...]) -> bool:
    try:
        _finite_json(expected)
        obj = _require_object(expected, "expected binding")
        _check_keys(obj, set(fields), set(fields), "expected binding")
        for field in fields:
            _nonempty_string(obj[field], f"expected.{field}")
        return True
    except ContractDError:
        return False


def consume(
    decision: Any,
    *,
    expected_upstream: Any,
    expected_policy: Any,
    expected_target: Any,
    requested_operation: Any,
    requested_effect_params: Any = ABSENT,
) -> str:
    try:
        normalized = validate_decision(decision)
    except ContractDError:
        return OUTCOME_CANNOT_ESTABLISH

    if not _expected_binding_ok(expected_upstream, ("kind", "id", "immutable_id")):
        return OUTCOME_NOT_APPLICABLE
    if not _expected_binding_ok(expected_policy, ("id", "version")):
        return OUTCOME_NOT_APPLICABLE
    if not _expected_binding_ok(expected_target, ("kind", "id", "content_sha256")):
        return OUTCOME_NOT_APPLICABLE
    if normalized["input_authority"] != expected_upstream:
        return OUTCOME_NOT_APPLICABLE
    if normalized["policy"] != expected_policy:
        return OUTCOME_NOT_APPLICABLE
    if normalized["target"] != expected_target:
        return OUTCOME_NOT_APPLICABLE

    if normalized["evaluation"]["state"] == "failed":
        return OUTCOME_FAILED

    effect = normalized["effect"]
    if requested_operation != effect["type"]:
        return OUTCOME_NOT_APPLICABLE

    if requested_effect_params is not ABSENT:
        try:
            _finite_json(requested_effect_params)
            requested = _require_object(requested_effect_params, "requested_effect_params")
        except ContractDError:
            return OUTCOME_NOT_APPLICABLE
        for key, value in requested.items():
            if key not in effect["params"] or effect["params"][key] != value:
                return OUTCOME_NOT_APPLICABLE

    return OUTCOME_HOLD if normalized["evaluation"]["disposition"] == "hold" else OUTCOME_CANDIDATE


def consume_json_bytes(payload: bytes | bytearray, **context: Any) -> str:
    try:
        decision = parse_json_bytes(payload)
    except ContractDError:
        return OUTCOME_CANNOT_ESTABLISH
    return consume(decision, **context)
