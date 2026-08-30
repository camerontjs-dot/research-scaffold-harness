import hashlib
import json


def clear_disposition_only(decision, **_):
    return "candidate_for_authorization" if decision.get("evaluation", {}).get("disposition") == "clear" else "not_applicable"


def target_id_only(decision, *, expected_target, **_):
    return "candidate_for_authorization" if decision.get("target", {}).get("id") == expected_target.get("id") else "not_applicable"


def target_ignore_kind_content(decision, *, expected_target, **_):
    return "candidate_for_authorization" if decision.get("target", {}).get("id") == expected_target.get("id") else "not_applicable"


def hold_failure_collapse(decision, **_):
    ev = decision.get("evaluation", {})
    if ev.get("state") == "failed" or ev.get("disposition") == "hold":
        return "hold"
    return "candidate_for_authorization"


def reason_text_effect_inference(decision, *, requested_operation, **_):
    text = json.dumps(decision.get("metadata", {}), sort_keys=True)
    if "dispatch" in text and requested_operation == "task.dispatch":
        return "candidate_for_authorization"
    return "not_applicable"


def unknown_effect_acceptance(decision, *, requested_operation, **_):
    effect = decision.get("effect", {})
    return "candidate_for_authorization" if effect.get("type") == requested_operation else "not_applicable"


def policy_blind(decision, *, expected_input_authority, expected_target, requested_operation, **_):
    if decision.get("input_authority") != dict(expected_input_authority):
        return "not_applicable"
    if decision.get("target") != dict(expected_target):
        return "not_applicable"
    if decision.get("effect", {}).get("type") != requested_operation:
        return "not_applicable"
    return "candidate_for_authorization"


def upstream_blind(decision, *, expected_policy, expected_target, requested_operation, **_):
    if decision.get("policy") != dict(expected_policy):
        return "not_applicable"
    if decision.get("target") != dict(expected_target):
        return "not_applicable"
    if decision.get("effect", {}).get("type") != requested_operation:
        return "not_applicable"
    return "candidate_for_authorization"


def authorization_identity_contaminated(decision, authorization_context):
    payload = {"decision": decision, "authorization": authorization_context}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()
