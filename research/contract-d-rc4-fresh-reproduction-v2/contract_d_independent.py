"""Independent Contract D RC4 consumer derived only from the frozen public authority."""

from __future__ import annotations

import hashlib
import json
import math
import re
from typing import Any, Mapping

VERSION = "0.3.0-rc4"
TARGET_SHA_RE = re.compile(r"^sha256:[0-9a-f]{64}$")

REGISTRY = {
    "knowledge.add_verified_tag": {
        "1": {
            "params": {
                "scope": {
                    "type": "string",
                    "required": False,
                    "enum": ["claim", "object"],
                    "default": "claim",
                }
            }
        }
    },
    "knowledge.cite_as_evidence": {"1": {"params": {}}},
    "task.dispatch": {"1": {"params": {}}},
}


class ContractDError(ValueError):
    pass


def _reject_constant(value: str) -> None:
    raise ContractDError(f"non-finite JSON number token: {value}")


def _pairs_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ContractDError(f"duplicate JSON object key: {key}")
        out[key] = value
    return out


def parse_json_bytes(data: bytes | bytearray) -> Any:
    if not isinstance(data, (bytes, bytearray)):
        raise ContractDError("JSON ingress must be bytes")
    try:
        text = bytes(data).decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ContractDError("invalid UTF-8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_pairs_object,
            parse_constant=_reject_constant,
        )
    except ContractDError:
        raise
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ContractDError("invalid JSON") from exc
    assert_finite_json(value)
    return value


def assert_finite_json(value: Any) -> None:
    """Reject host-only values and cycles while permitting shared acyclic containers."""

    def visit(node: Any, active: set[int]) -> None:
        if node is None or isinstance(node, (str, bool)):
            return
        if isinstance(node, int) and not isinstance(node, bool):
            return
        if isinstance(node, float):
            if not math.isfinite(node):
                raise ContractDError("non-finite number")
            return
        if isinstance(node, dict):
            oid = id(node)
            if oid in active:
                raise ContractDError("cyclic decoded JSON object")
            active.add(oid)
            try:
                for key, item in node.items():
                    if not isinstance(key, str):
                        raise ContractDError("JSON object key must be string")
                    visit(item, active)
            finally:
                active.remove(oid)
            return
        if isinstance(node, list):
            oid = id(node)
            if oid in active:
                raise ContractDError("cyclic decoded JSON array")
            active.add(oid)
            try:
                for item in node:
                    visit(item, active)
            finally:
                active.remove(oid)
            return
        raise ContractDError(f"host-language-only value: {type(node).__name__}")

    visit(value, set())


def canonical_json_bytes(value: Any) -> bytes:
    assert_finite_json(value)
    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ) + "\n"
    except (TypeError, ValueError) as exc:
        raise ContractDError("cannot canonicalize non-JSON value") from exc
    return text.encode("utf-8")


def _expect_exact_keys(obj: Any, required: set[str], optional: set[str] = set()) -> dict[str, Any]:
    if not isinstance(obj, dict):
        raise ContractDError("expected object")
    keys = set(obj)
    if not required.issubset(keys):
        raise ContractDError("missing required field")
    if keys - required - optional:
        raise ContractDError("unknown structural field")
    return obj


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and len(value) > 0


def _validate_named_object(obj: Any, keys: tuple[str, ...]) -> None:
    d = _expect_exact_keys(obj, set(keys))
    if not all(_nonempty_string(d[k]) for k in keys):
        raise ContractDError("required string must be non-empty")


def _effect_schema(effect_type: str, version: str) -> dict[str, Any]:
    try:
        return REGISTRY[effect_type][version]
    except KeyError as exc:
        raise ContractDError("unknown effect type/version") from exc


def normalize_effect(effect: Any) -> dict[str, Any]:
    e = _expect_exact_keys(effect, {"type", "version"}, {"params"})
    if not _nonempty_string(e["type"]) or not _nonempty_string(e["version"]):
        raise ContractDError("effect type/version must be non-empty strings")
    schema = _effect_schema(e["type"], e["version"])
    params = e.get("params", {})
    if not isinstance(params, dict):
        raise ContractDError("effect params must be object")
    allowed = set(schema["params"])
    if set(params) - allowed:
        raise ContractDError("unknown effect parameter")
    normalized: dict[str, Any] = {}
    for name, desc in schema["params"].items():
        if name in params:
            value = params[name]
        elif "default" in desc:
            value = desc["default"]
        elif desc.get("required"):
            raise ContractDError("missing required effect parameter")
        else:
            continue
        if desc.get("type") == "string" and not isinstance(value, str):
            raise ContractDError("effect parameter type mismatch")
        if "enum" in desc and value not in desc["enum"]:
            raise ContractDError("effect parameter enum mismatch")
        normalized[name] = value
    return {"type": e["type"], "version": e["version"], "params": normalized}


def validate_decision(decision: Any) -> dict[str, Any]:
    assert_finite_json(decision)
    d = _expect_exact_keys(
        decision,
        {"contract_d_version", "input_authority", "policy", "target", "evaluation"},
        {"effect", "metadata"},
    )
    if d["contract_d_version"] != VERSION or not isinstance(d["contract_d_version"], str):
        raise ContractDError("unsupported Contract D version")

    _validate_named_object(d["input_authority"], ("kind", "id", "immutable_id"))
    _validate_named_object(d["policy"], ("id", "version"))
    _validate_named_object(d["target"], ("kind", "id", "content_sha256"))
    if not TARGET_SHA_RE.fullmatch(d["target"]["content_sha256"]):
        raise ContractDError("invalid target content_sha256")

    evaluation = d["evaluation"]
    if not isinstance(evaluation, dict) or "state" not in evaluation:
        raise ContractDError("invalid evaluation")
    state = evaluation["state"]
    if state == "completed":
        _expect_exact_keys(evaluation, {"state", "disposition"})
        if evaluation["disposition"] not in ("clear", "hold"):
            raise ContractDError("unknown disposition")
        if "effect" not in d:
            raise ContractDError("completed evaluation requires effect")
        normalize_effect(d["effect"])
    elif state == "failed":
        _expect_exact_keys(evaluation, {"state"})
        if "effect" in d:
            raise ContractDError("failed evaluation forbids effect")
    else:
        raise ContractDError("unknown evaluation state")

    if "metadata" in d:
        metadata = _expect_exact_keys(d["metadata"], set(), {"reason_codes", "explanation", "diagnostics"})
        if "reason_codes" in metadata:
            codes = metadata["reason_codes"]
            if not isinstance(codes, list) or any(not _nonempty_string(x) for x in codes):
                raise ContractDError("invalid metadata reason_codes")
        if "explanation" in metadata and not _nonempty_string(metadata["explanation"]):
            raise ContractDError("invalid metadata explanation")
        if "diagnostics" in metadata:
            assert_finite_json(metadata["diagnostics"])
    return d


def authority_projection(decision: Any) -> dict[str, Any]:
    d = validate_decision(decision)
    projection = {
        "contract_d_version": d["contract_d_version"],
        "input_authority": d["input_authority"],
        "policy": d["policy"],
        "target": d["target"],
        "evaluation": d["evaluation"],
    }
    if d["evaluation"]["state"] == "completed":
        projection["effect"] = normalize_effect(d["effect"])
    return projection


def semantic_identity(decision: Any) -> str:
    digest = hashlib.sha256(canonical_json_bytes(authority_projection(decision))).hexdigest()
    return "decision:sha256:" + digest


def _valid_expected(expected: Any, keys: tuple[str, ...], target: bool = False) -> bool:
    try:
        _validate_named_object(expected, keys)
        if target and not TARGET_SHA_RE.fullmatch(expected["content_sha256"]):
            return False
        return True
    except ContractDError:
        return False


def _constraints_match(normalized_params: Mapping[str, Any], requested: Any) -> bool:
    if requested is None:
        return True
    try:
        assert_finite_json(requested)
    except ContractDError:
        return False
    if not isinstance(requested, dict):
        return False
    for key, value in requested.items():
        if key not in normalized_params or normalized_params[key] != value:
            return False
    return True


def consume(
    decision: Any,
    *,
    expected_input_authority: Any,
    expected_policy: Any,
    expected_target: Any,
    requested_operation: Any,
    requested_effect_params: Any = None,
) -> str:
    try:
        d = validate_decision(decision)
    except ContractDError:
        return "cannot_establish"

    if not _valid_expected(expected_input_authority, ("kind", "id", "immutable_id")):
        return "cannot_establish"
    if not _valid_expected(expected_policy, ("id", "version")):
        return "cannot_establish"
    if not _valid_expected(expected_target, ("kind", "id", "content_sha256"), target=True):
        return "cannot_establish"

    if d["input_authority"] != expected_input_authority:
        return "not_applicable"
    if d["policy"] != expected_policy:
        return "not_applicable"
    if d["target"] != expected_target:
        return "not_applicable"

    if d["evaluation"]["state"] == "failed":
        return "evaluation_failed"

    effect = normalize_effect(d["effect"])
    if not isinstance(requested_operation, str) or requested_operation != effect["type"]:
        return "not_applicable"
    if not _constraints_match(effect["params"], requested_effect_params):
        return "not_applicable"

    return "hold" if d["evaluation"]["disposition"] == "hold" else "candidate_for_authorization"
