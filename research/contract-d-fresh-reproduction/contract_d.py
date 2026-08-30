"""Independent Contract D candidate reproduction.

This module is intentionally written from the frozen public semantic artifacts only.
It does not import Decision Engine code.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Mapping

CONTRACT_VERSION = "0.research-d"
EVALUATION_STATES = {"completed", "failed"}
DISPOSITIONS = {"CLEAR", "HOLD"}

TOP_LEVEL_FIELDS = {
    "contract_version",
    "input_authority",
    "policy",
    "target",
    "evaluation_state",
    "disposition",
    "effect",
    "metadata",
    "decision_id",
}
AUTHORITY_FIELDS = {"kind", "id"}
POLICY_FIELDS = {"id", "version"}
TARGET_FIELDS = {"kind", "id", "content_hash"}
EFFECT_FIELDS = {"type", "version", "params"}

KNOWN_EFFECTS = {
    ("knowledge.tag", 1): {
        "operation": "knowledge.apply_tag",
        "defaults": {},
        "params": {
            "tag": {"required": True, "enum": {"audited_verified"}},
        },
    },
    ("citation.use", 1): {
        "operation": "citation.use",
        "defaults": {"scope": "same_target"},
        "params": {
            "scope": {"required": False, "enum": {"same_target"}},
        },
    },
    ("task.dispatch", 1): {
        "operation": "task.dispatch",
        "defaults": {},
        "params": {
            "dispatch_class": {
                "required": True,
                "enum": {"human_review_queue", "standard"},
            },
        },
    },
}


class ContractDValidationError(ValueError):
    pass


@dataclass(frozen=True)
class ParsedDecision:
    value: dict[str, Any]
    semantic_projection: dict[str, Any]
    semantic_identity: str
    canonical_bytes: bytes


def _is_json_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _reject_non_finite(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractDValidationError(f"{path}: non-finite numbers are not allowed")
    if isinstance(value, list):
        for i, item in enumerate(value):
            _reject_non_finite(item, f"{path}[{i}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            _reject_non_finite(item, f"{path}.{key}")


def _require_exact_fields(obj: Mapping[str, Any], allowed: set[str], path: str) -> None:
    unknown = set(obj) - allowed
    if unknown:
        raise ContractDValidationError(
            f"{path}: unknown fields are rejected for declared version: {sorted(unknown)}"
        )


def _require_nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractDValidationError(f"{path}: expected non-empty string")
    return value


def _validate_identity_object(
    value: Any, allowed: set[str], required: set[str], path: str
) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ContractDValidationError(f"{path}: expected object")
    _require_exact_fields(value, allowed, path)
    missing = required - set(value)
    if missing:
        raise ContractDValidationError(f"{path}: missing fields {sorted(missing)}")
    return {key: _require_nonempty_string(value[key], f"{path}.{key}") for key in required}


def _validate_effect_shape(effect: Any, path: str = "$.effect") -> dict[str, Any]:
    if not isinstance(effect, dict):
        raise ContractDValidationError(f"{path}: expected object")
    _require_exact_fields(effect, EFFECT_FIELDS, path)
    missing = EFFECT_FIELDS - set(effect)
    if missing:
        raise ContractDValidationError(f"{path}: missing fields {sorted(missing)}")
    effect_type = _require_nonempty_string(effect["type"], f"{path}.type")
    version = effect["version"]
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        raise ContractDValidationError(f"{path}.version: expected positive integer")
    params = effect["params"]
    if not isinstance(params, dict):
        raise ContractDValidationError(f"{path}.params: expected object")
    _reject_non_finite(params, f"{path}.params")
    return {"type": effect_type, "version": version, "params": copy.deepcopy(params)}


def _normalize_known_effect(effect: dict[str, Any]) -> dict[str, Any]:
    schema = KNOWN_EFFECTS.get((effect["type"], effect["version"]))
    if schema is None:
        return copy.deepcopy(effect)
    params = copy.deepcopy(effect["params"])
    known_names = set(schema["params"])
    unknown = set(params) - known_names
    if unknown:
        raise ContractDValidationError(
            f"$.effect.params: unknown parameters for known effect/version: {sorted(unknown)}"
        )
    for name, spec in schema["params"].items():
        if spec["required"] and name not in params:
            raise ContractDValidationError(
                f"$.effect.params.{name}: required for {effect['type']} v{effect['version']}"
            )
        if name in params and spec.get("enum") is not None and params[name] not in spec["enum"]:
            raise ContractDValidationError(
                f"$.effect.params.{name}: unsupported value {params[name]!r}"
            )
    normalized = copy.deepcopy(schema["defaults"])
    normalized.update(params)
    return {"type": effect["type"], "version": effect["version"], "params": normalized}


def canonical_json_bytes(value: Any) -> bytes:
    _reject_non_finite(value)
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def semantic_projection(decision: Mapping[str, Any]) -> dict[str, Any]:
    projection: dict[str, Any] = {
        "contract_version": decision["contract_version"],
        "input_authority": copy.deepcopy(decision["input_authority"]),
        "policy": copy.deepcopy(decision["policy"]),
        "target": copy.deepcopy(decision["target"]),
        "evaluation_state": decision["evaluation_state"],
    }
    if decision["evaluation_state"] == "completed":
        projection["disposition"] = decision["disposition"]
        projection["effect"] = _normalize_known_effect(decision["effect"])
    return projection


def semantic_identity_from_projection(projection: Mapping[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json_bytes(projection)).hexdigest()
    return f"sha256:{digest}"


def parse_and_validate(value: Any) -> ParsedDecision:
    if not isinstance(value, dict):
        raise ContractDValidationError("$: expected object")
    _require_exact_fields(value, TOP_LEVEL_FIELDS, "$")
    required = {
        "contract_version",
        "input_authority",
        "policy",
        "target",
        "evaluation_state",
    }
    missing = required - set(value)
    if missing:
        raise ContractDValidationError(f"$: missing fields {sorted(missing)}")

    version = _require_nonempty_string(value["contract_version"], "$.contract_version")
    if version != CONTRACT_VERSION:
        raise ContractDValidationError(
            f"$.contract_version: unsupported declared contract version {version!r}"
        )

    input_authority = _validate_identity_object(
        value["input_authority"], AUTHORITY_FIELDS, AUTHORITY_FIELDS, "$.input_authority"
    )
    policy = _validate_identity_object(value["policy"], POLICY_FIELDS, POLICY_FIELDS, "$.policy")
    target = _validate_identity_object(value["target"], TARGET_FIELDS, TARGET_FIELDS, "$.target")

    evaluation_state = value["evaluation_state"]
    if evaluation_state not in EVALUATION_STATES:
        raise ContractDValidationError(
            f"$.evaluation_state: expected one of {sorted(EVALUATION_STATES)}"
        )

    normalized: dict[str, Any] = {
        "contract_version": version,
        "input_authority": input_authority,
        "policy": policy,
        "target": target,
        "evaluation_state": evaluation_state,
    }

    if evaluation_state == "completed":
        if "disposition" not in value:
            raise ContractDValidationError("$.disposition: required when evaluation completed")
        if value["disposition"] not in DISPOSITIONS:
            raise ContractDValidationError(
                f"$.disposition: unknown disposition {value['disposition']!r}"
            )
        if "effect" not in value:
            raise ContractDValidationError("$.effect: required when evaluation completed")
        normalized["disposition"] = value["disposition"]
        normalized["effect"] = _validate_effect_shape(value["effect"])
        # Known effect/version gets semantic validation. Unknown future effects remain parseable.
        _normalize_known_effect(normalized["effect"])
    else:
        if "disposition" in value:
            raise ContractDValidationError(
                "$.disposition: forbidden when evaluation failed because no policy conclusion exists"
            )
        if "effect" in value:
            raise ContractDValidationError(
                "$.effect: forbidden when evaluation failed in this independent candidate"
            )

    if "metadata" in value:
        if not isinstance(value["metadata"], dict):
            raise ContractDValidationError("$.metadata: expected object")
        _reject_non_finite(value["metadata"], "$.metadata")
        normalized["metadata"] = copy.deepcopy(value["metadata"])

    projection = semantic_projection(normalized)
    identity = semantic_identity_from_projection(projection)

    if "decision_id" in value:
        decision_id = _require_nonempty_string(value["decision_id"], "$.decision_id")
        if decision_id != identity:
            raise ContractDValidationError(
                "$.decision_id: when present it must equal the derived semantic identity"
            )
        normalized["decision_id"] = decision_id

    canonical = canonical_json_bytes(normalized)
    return ParsedDecision(
        value=normalized,
        semantic_projection=projection,
        semantic_identity=identity,
        canonical_bytes=canonical,
    )




def produce_decision(
    *,
    input_authority: Mapping[str, str],
    policy: Mapping[str, str],
    target: Mapping[str, str],
    evaluation_state: str,
    disposition: str | None = None,
    effect: Mapping[str, Any] | None = None,
    metadata: Mapping[str, Any] | None = None,
    include_decision_id: bool = True,
) -> dict[str, Any]:
    """Independently produce one candidate Contract D object from semantic inputs."""
    obj: dict[str, Any] = {
        "contract_version": CONTRACT_VERSION,
        "input_authority": dict(input_authority),
        "policy": dict(policy),
        "target": dict(target),
        "evaluation_state": evaluation_state,
    }
    if disposition is not None:
        obj["disposition"] = disposition
    if effect is not None:
        obj["effect"] = copy.deepcopy(dict(effect))
    if metadata is not None:
        obj["metadata"] = copy.deepcopy(dict(metadata))
    parsed = parse_and_validate(obj)
    if include_decision_id:
        obj["decision_id"] = parsed.semantic_identity
        # Re-validate the stored id before returning.
        parse_and_validate(obj)
    return obj

def known_effect_operation(effect: Mapping[str, Any]) -> str | None:
    schema = KNOWN_EFFECTS.get((effect["type"], effect["version"]))
    return None if schema is None else schema["operation"]


def _authority_key(obj: Mapping[str, Any]) -> tuple[str, str]:
    return obj["kind"], obj["id"]


def _policy_key(obj: Mapping[str, Any]) -> tuple[str, str]:
    return obj["id"], obj["version"]


def _effect_matches_request(effect: Mapping[str, Any], operation: str, context: Mapping[str, Any]) -> bool:
    schema = KNOWN_EFFECTS.get((effect["type"], effect["version"]))
    if schema is None or schema["operation"] != operation:
        return False
    normalized = _normalize_known_effect(dict(effect))
    params = normalized["params"]
    if effect["type"] == "knowledge.tag":
        return context.get("tag") == params["tag"]
    if effect["type"] == "citation.use":
        # same_target is enforced by the exact target binding outside this helper.
        return params["scope"] == "same_target"
    if effect["type"] == "task.dispatch":
        return context.get("dispatch_class") == params["dispatch_class"]
    return False


def authorization_evaluate(
    decision_obj: Any,
    *,
    actor: str,
    requested_operation: str,
    request_target: Mapping[str, str],
    context: Mapping[str, Any],
    authorization_profile: Mapping[str, Any],
    human_approval: bool | None = None,
) -> dict[str, str]:
    """Consume Decision authority without letting Decision confer execution authority."""
    try:
        parsed = parse_and_validate(decision_obj)
    except ContractDValidationError:
        return {"decision_status": "invalid_decision", "authorization": "cannot_establish"}

    decision = parsed.value

    if decision["evaluation_state"] != "completed":
        return {"decision_status": "not_candidate", "authorization": "cannot_establish"}
    if decision["disposition"] != "CLEAR":
        return {"decision_status": "not_candidate", "authorization": "deny"}

    effect = decision["effect"]
    if known_effect_operation(effect) is None:
        return {"decision_status": "unknown_effect", "authorization": "cannot_establish"}

    required_target_fields = {"kind", "id", "content_hash"}
    if set(request_target) != required_target_fields:
        return {"decision_status": "not_applicable", "authorization": "cannot_establish"}
    if any(decision["target"][k] != request_target[k] for k in required_target_fields):
        return {"decision_status": "not_applicable", "authorization": "cannot_establish"}

    accepted_authorities = {
        tuple(x) for x in authorization_profile.get("accepted_input_authorities", [])
    }
    if accepted_authorities and _authority_key(decision["input_authority"]) not in accepted_authorities:
        return {"decision_status": "not_applicable", "authorization": "cannot_establish"}

    accepted_policies = {tuple(x) for x in authorization_profile.get("accepted_policies", [])}
    if accepted_policies and _policy_key(decision["policy"]) not in accepted_policies:
        return {"decision_status": "not_applicable", "authorization": "cannot_establish"}

    if not _effect_matches_request(effect, requested_operation, context):
        return {"decision_status": "not_applicable", "authorization": "cannot_establish"}

    decision_status = "candidate_for_authorization"

    allowed_operations = set(authorization_profile.get("allowed_operations", []))
    if requested_operation not in allowed_operations:
        return {"decision_status": decision_status, "authorization": "deny"}

    allowed_actors = set(authorization_profile.get("allowed_actors", []))
    if actor not in allowed_actors:
        return {"decision_status": decision_status, "authorization": "deny"}

    required_context = authorization_profile.get("required_context", {})
    if not isinstance(required_context, dict):
        return {"decision_status": decision_status, "authorization": "cannot_establish"}
    for key, expected in required_context.items():
        if key not in context:
            return {"decision_status": decision_status, "authorization": "cannot_establish"}
        if context[key] != expected:
            return {"decision_status": decision_status, "authorization": "deny"}

    if authorization_profile.get("require_human_approval", False):
        if human_approval is None:
            return {"decision_status": decision_status, "authorization": "cannot_establish"}
        if human_approval is False:
            return {"decision_status": decision_status, "authorization": "deny"}

    return {"decision_status": decision_status, "authorization": "permit"}
