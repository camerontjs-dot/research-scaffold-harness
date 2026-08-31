"""Intentionally weak Contract D consumers used only as evaluator controls."""
from __future__ import annotations

from copy import deepcopy
import hashlib

from contract_d_independent import (
    ABSENT,
    OUTCOME_CANDIDATE,
    OUTCOME_CANNOT_ESTABLISH,
    OUTCOME_FAILED,
    OUTCOME_HOLD,
    OUTCOME_NOT_APPLICABLE,
    authority_projection,
    canonical_json_bytes,
    consume,
    semantic_identity,
    validate_decision,
)


def disposition_only(decision, **ctx):
    try:
        n = validate_decision(decision)
    except Exception:
        return OUTCOME_CANNOT_ESTABLISH
    if n["evaluation"]["state"] == "failed":
        return OUTCOME_FAILED
    return OUTCOME_HOLD if n["evaluation"]["disposition"] == "hold" else OUTCOME_CANDIDATE


def target_id_only(decision, **ctx):
    try:
        if decision["target"]["id"] != ctx["expected_target"]["id"]:
            return OUTCOME_NOT_APPLICABLE
        altered = dict(ctx)
        altered["expected_target"] = deepcopy(decision["target"])
        return consume(decision, **altered)
    except Exception:
        return OUTCOME_CANNOT_ESTABLISH


def target_ignores_kind_content(decision, **ctx):
    return target_id_only(decision, **ctx)


def hold_failure_collapse(decision, **ctx):
    out = consume(decision, **ctx)
    return OUTCOME_FAILED if out == OUTCOME_HOLD else out


def reason_text_effect_inference(decision, **ctx):
    meta = decision.get("metadata", {}) if isinstance(decision, dict) else {}
    text = str(meta.get("explanation", "")) + " " + " ".join(meta.get("reason_codes", []) if isinstance(meta.get("reason_codes", []), list) else [])
    if any(token in text for token in ("task.dispatch", "knowledge.add_verified_tag", "knowledge.cite_as_evidence")):
        return OUTCOME_CANDIDATE
    return consume(decision, **ctx)


def unknown_effect_acceptance(decision, **ctx):
    try:
        ev = decision["evaluation"]
        if ev.get("state") == "completed" and decision.get("effect", {}).get("type") == ctx.get("requested_operation"):
            return OUTCOME_HOLD if ev.get("disposition") == "hold" else OUTCOME_CANDIDATE
    except Exception:
        pass
    return consume(decision, **ctx)


def policy_blind(decision, **ctx):
    altered = dict(ctx)
    altered["expected_policy"] = deepcopy(decision.get("policy"))
    return consume(decision, **altered)


def upstream_blind(decision, **ctx):
    altered = dict(ctx)
    altered["expected_upstream"] = deepcopy(decision.get("input_authority"))
    return consume(decision, **altered)


def omitted_params_become_defaults(decision, **ctx):
    altered = dict(ctx)
    if altered.get("requested_effect_params", ABSENT) is ABSENT or altered.get("requested_effect_params") == {}:
        if decision.get("effect", {}).get("type") == "knowledge.add_verified_tag":
            altered["requested_effect_params"] = {"scope": "claim"}
    return consume(decision, **altered)


def hold_before_applicability(decision, **ctx):
    try:
        n = validate_decision(decision)
        if n["evaluation"] == {"state": "completed", "disposition": "hold"}:
            return OUTCOME_HOLD
    except Exception:
        return OUTCOME_CANNOT_ESTABLISH
    return consume(decision, **ctx)


def accepts_host_only_diagnostics(decision, **ctx):
    cleaned = deepcopy(decision)
    try:
        if "diagnostics" in cleaned.get("metadata", {}):
            cleaned["metadata"].pop("diagnostics")
        return consume(cleaned, **ctx)
    except Exception:
        return OUTCOME_CANNOT_ESTABLISH


def authorization_contaminated_identity(decision, authorization_context):
    projection = authority_projection(decision)
    projection["authorization_context"] = deepcopy(authorization_context)
    return "decision:sha256:" + hashlib.sha256(canonical_json_bytes(projection)).hexdigest()


WEAK_OUTCOME_CONSUMERS = {
    "CLEAR/disposition-only": disposition_only,
    "target-id-only": target_id_only,
    "target ignores kind/content": target_ignores_kind_content,
    "HOLD/failure collapse": hold_failure_collapse,
    "reason-text effect inference": reason_text_effect_inference,
    "unknown-effect acceptance": unknown_effect_acceptance,
    "policy-blind": policy_blind,
    "upstream-blind": upstream_blind,
    "omitted requested params become defaults": omitted_params_become_defaults,
    "HOLD before applicability": hold_before_applicability,
    "host-language-only diagnostics accepted": accepts_host_only_diagnostics,
}
