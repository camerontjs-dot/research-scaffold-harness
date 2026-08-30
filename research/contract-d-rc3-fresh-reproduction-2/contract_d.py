import copy
import hashlib
import json
import math
from typing import Any, Dict, Mapping, Optional, Tuple

VERSION = "0.3.0-rc3"

EFFECT_REGISTRY = {
    "knowledge.add_verified_tag": {
        "1": {
            "params": {
                "scope": {"type": "string", "required": False, "default": "claim", "enum": ["claim", "object"]}
            }
        }
    },
    "knowledge.cite_as_evidence": {"1": {"params": {}}},
    "task.dispatch": {"1": {"params": {}}},
}

TOP_KEYS = {"contract_d_version", "input_authority", "policy", "target", "evaluation", "effect", "metadata"}
INPUT_KEYS = {"kind", "id", "immutable_id"}
POLICY_KEYS = {"id", "version"}
TARGET_KEYS = {"kind", "id", "content_sha256"}
EVAL_KEYS = {"state", "disposition"}
EFFECT_KEYS = {"type", "version", "params"}
METADATA_KEYS = {"reason_codes", "explanation", "diagnostics"}

class ContractDError(ValueError):
    pass


def _pairs_no_duplicates(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ContractDError(f"duplicate key: {key}")
        out[key] = value
    return out


def _reject_constant(value):
    raise ContractDError(f"non-finite JSON number: {value}")


def parse_json(data: Any) -> Dict[str, Any]:
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    if isinstance(data, str):
        try:
            obj = json.loads(data, object_pairs_hook=_pairs_no_duplicates, parse_constant=_reject_constant)
        except ContractDError:
            raise
        except Exception as exc:
            raise ContractDError(f"invalid JSON: {exc}") from exc
    elif isinstance(data, Mapping):
        obj = copy.deepcopy(dict(data))
    else:
        raise ContractDError("Contract D input must be JSON text/bytes or an object")
    if not isinstance(obj, dict):
        raise ContractDError("top-level value must be an object")
    _assert_finite_json(obj)
    return obj


def _assert_finite_json(value: Any) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractDError("non-finite JSON number")
        return
    if isinstance(value, list):
        for item in value:
            _assert_finite_json(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ContractDError("object keys must be strings")
            _assert_finite_json(item)
        return
    raise ContractDError("value is not finite JSON")


def _object(value: Any, name: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractDError(f"{name} must be an object")
    return value


def _exact_keys(obj: Dict[str, Any], allowed, name: str) -> None:
    extra = set(obj) - set(allowed)
    if extra:
        raise ContractDError(f"unknown {name} field(s): {sorted(extra)}")


def _required(obj: Dict[str, Any], required, name: str) -> None:
    missing = set(required) - set(obj)
    if missing:
        raise ContractDError(f"missing {name} field(s): {sorted(missing)}")


def _nonempty_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or value == "":
        raise ContractDError(f"{name} must be a non-empty string")
    return value


def _validate_metadata(metadata: Dict[str, Any]) -> None:
    _exact_keys(metadata, METADATA_KEYS, "metadata")
    if "reason_codes" in metadata:
        codes = metadata["reason_codes"]
        if not isinstance(codes, list):
            raise ContractDError("metadata.reason_codes must be an array")
        for code in codes:
            _nonempty_string(code, "metadata.reason_codes item")
    if "explanation" in metadata:
        _nonempty_string(metadata["explanation"], "metadata.explanation")
    if "diagnostics" in metadata:
        _assert_finite_json(metadata["diagnostics"])


def _normalize_params(effect_type: str, effect_version: str, params_value: Any) -> Dict[str, Any]:
    declared = EFFECT_REGISTRY[effect_type][effect_version]["params"]
    params = _object(params_value, "effect.params")
    _exact_keys(params, declared.keys(), "effect.params")
    normalized = {}
    for name, spec in declared.items():
        if name in params:
            value = params[name]
        elif "default" in spec:
            value = spec["default"]
        elif spec.get("required"):
            raise ContractDError(f"missing required effect parameter: {name}")
        else:
            continue
        if spec.get("type") == "string" and not isinstance(value, str):
            raise ContractDError(f"effect.params.{name} must be string")
        if "enum" in spec and value not in spec["enum"]:
            raise ContractDError(f"effect.params.{name} not in registry enum")
        normalized[name] = value
    return normalized


def normalize_effect(effect: Dict[str, Any]) -> Dict[str, Any]:
    effect = _object(effect, "effect")
    _exact_keys(effect, EFFECT_KEYS, "effect")
    _required(effect, {"type", "version"}, "effect")
    effect_type = _nonempty_string(effect["type"], "effect.type")
    effect_version = _nonempty_string(effect["version"], "effect.version")
    versions = EFFECT_REGISTRY.get(effect_type)
    if versions is None or effect_version not in versions:
        raise ContractDError("unknown effect type/version")
    normalized = _normalize_params(effect_type, effect_version, effect.get("params", {}))
    return {"type": effect_type, "version": effect_version, "params": normalized}


def validate_object(data: Any) -> Dict[str, Any]:
    obj = parse_json(data)
    _exact_keys(obj, TOP_KEYS, "top-level")
    _required(obj, {"contract_d_version", "input_authority", "policy", "target", "evaluation"}, "top-level")
    if obj["contract_d_version"] != VERSION or not isinstance(obj["contract_d_version"], str):
        raise ContractDError("unsupported Contract D version")

    ia = _object(obj["input_authority"], "input_authority")
    _exact_keys(ia, INPUT_KEYS, "input_authority")
    _required(ia, INPUT_KEYS, "input_authority")
    for key in ("kind", "id", "immutable_id"):
        _nonempty_string(ia[key], f"input_authority.{key}")

    policy = _object(obj["policy"], "policy")
    _exact_keys(policy, POLICY_KEYS, "policy")
    _required(policy, POLICY_KEYS, "policy")
    _nonempty_string(policy["id"], "policy.id")
    _nonempty_string(policy["version"], "policy.version")

    target = _object(obj["target"], "target")
    _exact_keys(target, TARGET_KEYS, "target")
    _required(target, TARGET_KEYS, "target")
    _nonempty_string(target["kind"], "target.kind")
    _nonempty_string(target["id"], "target.id")
    content = _nonempty_string(target["content_sha256"], "target.content_sha256")
    if len(content) != 71 or not content.startswith("sha256:") or any(c not in "0123456789abcdef" for c in content[7:]):
        raise ContractDError("target.content_sha256 must be sha256: plus 64 lowercase hex characters")

    ev = _object(obj["evaluation"], "evaluation")
    _exact_keys(ev, EVAL_KEYS, "evaluation")
    _required(ev, {"state"}, "evaluation")
    state = ev["state"]
    if state == "completed":
        _required(ev, {"disposition"}, "evaluation")
        if ev["disposition"] not in {"clear", "hold"}:
            raise ContractDError("unknown completed disposition")
        if "effect" not in obj:
            raise ContractDError("completed evaluation requires effect")
        normalize_effect(obj["effect"])
    elif state == "failed":
        if "disposition" in ev:
            raise ContractDError("failed evaluation cannot have disposition")
        if "effect" in obj:
            raise ContractDError("failed evaluation cannot have effect")
    else:
        raise ContractDError("unknown evaluation state")

    if "metadata" in obj:
        _validate_metadata(_object(obj["metadata"], "metadata"))
    return obj


def canonical_bytes(value: Any) -> bytes:
    _assert_finite_json(value)
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except Exception as exc:
        raise ContractDError(f"cannot canonicalize: {exc}") from exc
    return (text + "\n").encode("utf-8")


def authority_projection(data: Any) -> Dict[str, Any]:
    obj = validate_object(data)
    projection = {
        "contract_d_version": obj["contract_d_version"],
        "input_authority": copy.deepcopy(obj["input_authority"]),
        "policy": copy.deepcopy(obj["policy"]),
        "target": copy.deepcopy(obj["target"]),
        "evaluation": copy.deepcopy(obj["evaluation"]),
    }
    if obj["evaluation"]["state"] == "completed":
        projection["effect"] = normalize_effect(obj["effect"])
    return projection


def semantic_identity(data: Any) -> str:
    digest = hashlib.sha256(canonical_bytes(authority_projection(data))).hexdigest()
    return "decision:sha256:" + digest


def _same_fields(actual: Dict[str, Any], expected: Mapping[str, Any], keys) -> bool:
    return all(actual.get(key) == expected.get(key) for key in keys)


def consume(
    data: Any,
    *,
    expected_input_authority: Mapping[str, Any],
    expected_policy: Mapping[str, Any],
    expected_target: Mapping[str, Any],
    requested_operation: str,
    requested_effect_params: Optional[Mapping[str, Any]] = None,
) -> str:
    try:
        obj = validate_object(data)
    except ContractDError:
        return "cannot_establish"

    if not _same_fields(obj["input_authority"], expected_input_authority, ("kind", "id", "immutable_id")):
        return "not_applicable"
    if not _same_fields(obj["policy"], expected_policy, ("id", "version")):
        return "not_applicable"
    if not _same_fields(obj["target"], expected_target, ("kind", "id", "content_sha256")):
        return "not_applicable"

    state = obj["evaluation"]["state"]
    if state == "failed":
        return "evaluation_failed"

    normalized = normalize_effect(obj["effect"])
    if requested_operation != normalized["type"]:
        return "not_applicable"
    try:
        requested = _normalize_params(normalized["type"], normalized["version"], {} if requested_effect_params is None else dict(requested_effect_params))
    except ContractDError:
        return "not_applicable"
    if requested != normalized["params"]:
        return "not_applicable"

    if obj["evaluation"]["disposition"] == "hold":
        return "hold"
    return "candidate_for_authorization"


def evaluation_signature(data: Any) -> Tuple[str, Optional[str]]:
    obj = validate_object(data)
    return obj["evaluation"]["state"], obj["evaluation"].get("disposition")
