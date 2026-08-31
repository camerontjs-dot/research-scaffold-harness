"""Intentionally weak consumers used as prereveal discrimination controls."""

from __future__ import annotations

from typing import Any


def clear_disposition_only(d: dict[str, Any], **_: Any) -> str:
    return "candidate_for_authorization" if d.get("evaluation", {}).get("disposition") == "clear" else "hold"


def target_id_only(d: dict[str, Any], *, expected_target: dict[str, Any], **_: Any) -> str:
    return "candidate_for_authorization" if d.get("target", {}).get("id") == expected_target.get("id") else "not_applicable"


def target_ignore_kind_content(d: dict[str, Any], *, expected_target: dict[str, Any], **_: Any) -> str:
    return "candidate_for_authorization" if d.get("target", {}).get("id") == expected_target.get("id") else "not_applicable"


def hold_failure_collapse(d: dict[str, Any], **_: Any) -> str:
    if d.get("evaluation", {}).get("disposition") == "clear":
        return "candidate_for_authorization"
    return "hold"


def reason_text_effect_inference(d: dict[str, Any], **_: Any) -> str:
    text = str(d.get("metadata", {}))
    return "candidate_for_authorization" if "clear" in text or "verified" in text else "cannot_establish"


def unknown_effect_acceptance(d: dict[str, Any], **_: Any) -> str:
    return "candidate_for_authorization" if d.get("evaluation", {}).get("state") == "completed" else "evaluation_failed"


def policy_blind(d: dict[str, Any], *, expected_input_authority: dict[str, Any], expected_target: dict[str, Any], **_: Any) -> str:
    return "candidate_for_authorization" if d.get("input_authority") == expected_input_authority and d.get("target") == expected_target else "not_applicable"


def upstream_blind(d: dict[str, Any], *, expected_policy: dict[str, Any], expected_target: dict[str, Any], **_: Any) -> str:
    return "candidate_for_authorization" if d.get("policy") == expected_policy and d.get("target") == expected_target else "not_applicable"


def omitted_params_as_defaults(d: dict[str, Any], *, requested_effect_params: Any = None, **_: Any) -> str:
    stored = d.get("effect", {}).get("params", {})
    requested = {"scope": "claim"} if requested_effect_params in (None, {}) else requested_effect_params
    return "candidate_for_authorization" if all(stored.get(k, "claim") == v for k, v in requested.items()) else "not_applicable"


def hold_before_applicability(d: dict[str, Any], **_: Any) -> str:
    if d.get("evaluation", {}).get("disposition") == "hold":
        return "hold"
    return "candidate_for_authorization"


def host_only_diagnostics_acceptance(d: dict[str, Any], **_: Any) -> str:
    return "candidate_for_authorization"


def cyclic_acceptance(d: dict[str, Any], **_: Any) -> str:
    return "candidate_for_authorization"


def identity_with_authorization_context(d: dict[str, Any], authorization_context: Any = None, **_: Any) -> str:
    return repr((d, authorization_context))
