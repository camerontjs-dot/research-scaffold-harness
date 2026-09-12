"""Minimal clean-room consumer for the bounded Contract C research handoff."""

from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any


_VERSION = "research-non-deciding-rc0"
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_PLAIN_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_RESULT_SET = re.compile(r"^result-set:[0-9a-f]{64}$")
_CONTRIBUTION_ID = re.compile(r"^contribution:[0-9a-f]{64}$")
_CHANNELS = {"support", "counterevidence", "non_deciding"}
_CAUSAL_FORMS = {
    "single_necessary",
    "independent_sufficient_alternatives",
    "jointly_sufficient",
    "redundant_non_deciding",
}


class ConsumerError(Exception):
    """Fail-closed validation error with a stable short code."""

    def __init__(self, code: str, message: str = "") -> None:
        self.code = code
        super().__init__(message or code)


def _fail(code: str, message: str = "") -> None:
    raise ConsumerError(code, message)


def _require_dict(value: Any, code: str) -> dict:
    if not isinstance(value, dict):
        _fail(code)
    return value


def _require_list(value: Any, code: str) -> list:
    if not isinstance(value, list):
        _fail(code)
    return value


def _require_nonempty_str(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(code)
    return value


def _canonical_bytes(value: Any) -> bytes:
    try:
        text = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        return (text + "\n").encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise ConsumerError("INVALID_CANONICAL_JSON") from exc


def _object_pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _reject_nonfinite(token: str) -> None:
    _fail("NONFINITE_NUMBER", token)


def _parse_json(raw: bytes) -> dict:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ConsumerError("INVALID_UTF8") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_object_pairs_no_duplicates,
            parse_constant=_reject_nonfinite,
        )
    except ConsumerError:
        raise
    except (json.JSONDecodeError, ValueError) as exc:
        raise ConsumerError("INVALID_JSON") from exc
    return _require_dict(value, "TOP_LEVEL_NOT_OBJECT")


def _validate_expected_profile(expected_profile: Any) -> dict:
    profile = _require_dict(expected_profile, "EXPECTED_PROFILE_INVALID")
    version = _require_nonempty_str(
        profile.get("contract_c_version"), "EXPECTED_PROFILE_INVALID"
    )
    whole_digest = _require_nonempty_str(
        profile.get("whole_object_sha256"), "EXPECTED_PROFILE_INVALID"
    )
    result_set_id = _require_nonempty_str(
        profile.get("result_set_id"), "EXPECTED_PROFILE_INVALID"
    )
    if version != _VERSION:
        _fail("EXPECTED_PROFILE_VERSION_UNSUPPORTED")
    if not _SHA256.fullmatch(whole_digest):
        _fail("EXPECTED_PROFILE_INVALID")
    if not _RESULT_SET.fullmatch(result_set_id):
        _fail("EXPECTED_PROFILE_INVALID")
    return profile


def _validate_contract_b_index(value: Any) -> dict:
    index = _require_dict(value, "CONTRACT_B_INDEX_INVALID")
    for field in ("contract_version", "bundle_id", "bundle_hash"):
        _require_nonempty_str(index.get(field), "CONTRACT_B_INDEX_INVALID")
    propositions = _require_dict(
        index.get("propositions"), "CONTRACT_B_INDEX_INVALID"
    )
    passages = _require_dict(index.get("passages"), "CONTRACT_B_INDEX_INVALID")
    for proposition_id, text_sha256 in propositions.items():
        if not isinstance(proposition_id, str) or not proposition_id:
            _fail("CONTRACT_B_INDEX_INVALID")
        if not isinstance(text_sha256, str) or not text_sha256:
            _fail("CONTRACT_B_INDEX_INVALID")
    for passage_id, passage in passages.items():
        if not isinstance(passage_id, str) or not passage_id:
            _fail("CONTRACT_B_INDEX_INVALID")
        passage = _require_dict(passage, "CONTRACT_B_INDEX_INVALID")
        _require_nonempty_str(passage.get("source_id"), "CONTRACT_B_INDEX_INVALID")
        digest = _require_nonempty_str(
            passage.get("passage_sha256"), "CONTRACT_B_INDEX_INVALID"
        )
        if not _SHA256.fullmatch(digest):
            _fail("CONTRACT_B_INDEX_INVALID")
    return index


def _validate_policy_binding(root: dict) -> None:
    producer = _require_dict(root.get("producer"), "PRODUCER_POLICY_INVALID")
    policy = _require_dict(producer.get("policy"), "PRODUCER_POLICY_INVALID")
    if "canonical" not in policy:
        _fail("PRODUCER_POLICY_INVALID")
    claimed = _require_nonempty_str(
        policy.get("sha256"), "PRODUCER_POLICY_INVALID"
    )
    if not _PLAIN_SHA256.fullmatch(claimed):
        _fail("PRODUCER_POLICY_INVALID")
    actual = hashlib.sha256(_canonical_bytes(policy["canonical"])).hexdigest()
    if actual != claimed:
        _fail("PRODUCER_POLICY_HASH_MISMATCH")


def _validate_contract_b_binding(root: dict, index: dict) -> dict:
    input_object = _require_dict(root.get("input"), "CONTRACT_B_BINDING_INVALID")
    binding = _require_dict(
        input_object.get("contract_b"), "CONTRACT_B_BINDING_INVALID"
    )
    normalized: dict[str, str] = {}
    for field in ("contract_version", "bundle_id", "bundle_hash"):
        actual = binding.get(field)
        if actual != index[field]:
            _fail("CONTRACT_B_BINDING_MISMATCH")
        normalized[field] = actual
    return normalized


def _validate_evidence_ref(evidence_ref: Any, index: dict) -> dict:
    ref = _require_dict(evidence_ref, "EVIDENCE_REF_INVALID")
    passage_id = _require_nonempty_str(ref.get("passage_id"), "EVIDENCE_REF_INVALID")
    source_id = _require_nonempty_str(ref.get("source_id"), "EVIDENCE_REF_INVALID")
    passage_sha256 = _require_nonempty_str(
        ref.get("passage_sha256"), "EVIDENCE_REF_INVALID"
    )
    expected = index["passages"].get(passage_id)
    if not isinstance(expected, dict):
        _fail("EVIDENCE_REF_MISMATCH")
    if source_id != expected.get("source_id"):
        _fail("EVIDENCE_REF_MISMATCH")
    if passage_sha256 != expected.get("passage_sha256"):
        _fail("EVIDENCE_REF_MISMATCH")
    return {
        "source_id": source_id,
        "passage_id": passage_id,
        "passage_sha256": passage_sha256,
    }


def _normalize_proposition(prop: Any, index: dict) -> dict:
    item = _require_dict(prop, "PROPOSITION_INVALID")
    proposition = _require_dict(item.get("proposition"), "PROPOSITION_INVALID")
    proposition_id = _require_nonempty_str(
        proposition.get("proposition_id"), "PROPOSITION_INVALID"
    )
    text_sha256 = _require_nonempty_str(
        proposition.get("text_sha256"), "PROPOSITION_INVALID"
    )
    expected_text_sha = index["propositions"].get(proposition_id)
    if expected_text_sha is None or text_sha256 != expected_text_sha:
        _fail("PROPOSITION_BINDING_MISMATCH")

    execution = _require_dict(item.get("execution"), "PROPOSITION_EXECUTION_INVALID")
    if execution.get("state") == "completed" and execution.get("completion") not in {
        "assessed",
        "not_checkable",
    }:
        _fail("PROPOSITION_EXECUTION_INVALID")

    contributions_raw = _require_list(item.get("contributions"), "CONTRIBUTIONS_INVALID")
    contributions: dict[str, dict] = {}
    for raw_contribution in contributions_raw:
        contribution = _require_dict(raw_contribution, "CONTRIBUTION_INVALID")
        contribution_id = _require_nonempty_str(
            contribution.get("contribution_id"), "CONTRIBUTION_INVALID"
        )
        if not _CONTRIBUTION_ID.fullmatch(contribution_id):
            _fail("CONTRIBUTION_ID_INVALID")
        if contribution_id in contributions:
            _fail("DUPLICATE_CONTRIBUTION_ID")
        channel = _require_nonempty_str(
            contribution.get("channel"), "CONTRIBUTION_INVALID"
        )
        if channel not in _CHANNELS:
            _fail("CONTRIBUTION_CHANNEL_INVALID")
        contributions[contribution_id] = {
            "contribution_id": contribution_id,
            "channel": channel,
            "evidence_ref": _validate_evidence_ref(
                contribution.get("evidence_ref"), index
            ),
        }

    conclusion_present = "conclusion" in item and item["conclusion"] is not None
    if not conclusion_present:
        if contributions:
            _fail("UNCLASSIFIED_CONTRIBUTION")
        return {
            "proposition": {
                "proposition_id": proposition_id,
                "text_sha256": text_sha256,
            },
            "execution": copy.deepcopy(execution),
            "reported_verdict": None,
            "terminal_branch": None,
            "causal_form": None,
            "causal_contributions": [],
            "residual_contributions": [],
        }

    conclusion = _require_dict(item["conclusion"], "CONCLUSION_INVALID")
    basis_members = _require_list(
        conclusion.get("basis_members"), "CONCLUSION_BASIS_INVALID"
    )
    residual_ids = _require_list(
        conclusion.get("residual_contribution_ids"), "CONCLUSION_RESIDUAL_INVALID"
    )

    causal_ids: list[str] = []
    causal_seen: set[str] = set()
    for member_raw in basis_members:
        member = _require_dict(member_raw, "CONCLUSION_BASIS_INVALID")
        if member.get("namespace") != "contribution":
            continue
        contribution_id = _require_nonempty_str(
            member.get("id"), "CONCLUSION_BASIS_INVALID"
        )
        if contribution_id in causal_seen:
            _fail("DUPLICATE_CAUSAL_CONTRIBUTION")
        if contribution_id not in contributions:
            _fail("UNKNOWN_CAUSAL_CONTRIBUTION")
        causal_seen.add(contribution_id)
        causal_ids.append(contribution_id)

    residual_seen: set[str] = set()
    normalized_residual_ids: list[str] = []
    for contribution_id_raw in residual_ids:
        contribution_id = _require_nonempty_str(
            contribution_id_raw, "CONCLUSION_RESIDUAL_INVALID"
        )
        if contribution_id in residual_seen:
            _fail("DUPLICATE_RESIDUAL_CONTRIBUTION")
        if contribution_id not in contributions:
            _fail("UNKNOWN_RESIDUAL_CONTRIBUTION")
        if contribution_id in causal_seen:
            _fail("CAUSAL_RESIDUAL_OVERLAP")
        residual_seen.add(contribution_id)
        normalized_residual_ids.append(contribution_id)

    classified = causal_seen | residual_seen
    if classified != set(contributions):
        _fail("UNCLASSIFIED_CONTRIBUTION")

    causal_form = _require_nonempty_str(
        conclusion.get("causal_form"), "CAUSAL_FORM_INVALID"
    )
    if causal_form not in _CAUSAL_FORMS:
        _fail("CAUSAL_FORM_INVALID")
    causal_count = len(causal_ids)
    if causal_form == "single_necessary" and causal_count != 1:
        _fail("CAUSAL_CARDINALITY_INVALID")
    if causal_form in {
        "independent_sufficient_alternatives",
        "jointly_sufficient",
    } and causal_count < 2:
        _fail("CAUSAL_CARDINALITY_INVALID")
    if causal_form == "redundant_non_deciding" and causal_count != 0:
        _fail("CAUSAL_CARDINALITY_INVALID")

    causal_contributions = [contributions[cid] for cid in sorted(causal_ids)]
    residual_contributions = [
        contributions[cid] for cid in sorted(normalized_residual_ids)
    ]

    return {
        "proposition": {
            "proposition_id": proposition_id,
            "text_sha256": text_sha256,
        },
        "execution": copy.deepcopy(execution),
        "reported_verdict": conclusion.get("reported_verdict"),
        "terminal_branch": conclusion.get("terminal_branch"),
        "causal_form": causal_form,
        "causal_contributions": causal_contributions,
        "residual_contributions": residual_contributions,
    }


def consume_contract_c(
    raw: bytes,
    contract_b_index: dict,
    expected_profile: dict,
) -> dict:
    """Validate and normalize the bounded Contract C handoff."""

    profile = _validate_expected_profile(expected_profile)
    if not isinstance(raw, bytes):
        _fail("RAW_NOT_BYTES")

    whole_digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    if whole_digest != profile["whole_object_sha256"]:
        _fail("WHOLE_OBJECT_DIGEST_MISMATCH")

    root = _parse_json(raw)
    if _canonical_bytes(root) != raw:
        _fail("NONCANONICAL_OBJECT_BYTES")

    version = root.get("contract_c_version")
    if version != _VERSION or version != profile["contract_c_version"]:
        _fail("CONTRACT_C_VERSION_MISMATCH")

    object_result_set_id = root.get("result_set_id")
    if object_result_set_id != profile["result_set_id"]:
        _fail("EXTERNAL_RESULT_SET_ID_MISMATCH")
    if not isinstance(object_result_set_id, str) or not _RESULT_SET.fullmatch(
        object_result_set_id
    ):
        _fail("RESULT_SET_ID_INVALID")
    result_identity_object = dict(root)
    result_identity_object.pop("result_set_id", None)
    computed_result_set_id = (
        "result-set:"
        + hashlib.sha256(_canonical_bytes(result_identity_object)).hexdigest()
    )
    if computed_result_set_id != object_result_set_id:
        _fail("RESULT_SET_ID_MISMATCH")

    index = _validate_contract_b_index(contract_b_index)
    _require_dict(root.get("execution"), "RESULT_EXECUTION_INVALID")
    contract_b = _validate_contract_b_binding(root, index)
    _validate_policy_binding(root)

    propositions_raw = _require_list(root.get("propositions"), "PROPOSITIONS_INVALID")
    normalized_propositions: list[dict] = []
    proposition_ids: set[str] = set()
    for raw_proposition in propositions_raw:
        normalized = _normalize_proposition(raw_proposition, index)
        proposition_id = normalized["proposition"]["proposition_id"]
        if proposition_id in proposition_ids:
            _fail("DUPLICATE_PROPOSITION_ID")
        proposition_ids.add(proposition_id)
        normalized_propositions.append(normalized)
    normalized_propositions.sort(
        key=lambda item: item["proposition"]["proposition_id"]
    )

    return {
        "contract_c_version": version,
        "result_set_id": object_result_set_id,
        "whole_object_sha256": whole_digest,
        "contract_b": contract_b,
        "propositions": normalized_propositions,
    }


def evaluate_supported_claim(consumed: dict, proposition_id: str) -> dict:
    """Apply the narrow downstream policy probe specified by the aperture."""

    if not isinstance(consumed, dict) or not isinstance(proposition_id, str):
        _fail("POLICY_PROBE_INPUT_INVALID")
    propositions = consumed.get("propositions")
    if not isinstance(propositions, list):
        _fail("POLICY_PROBE_INPUT_INVALID")

    target = None
    for proposition in propositions:
        if (
            isinstance(proposition, dict)
            and isinstance(proposition.get("proposition"), dict)
            and proposition["proposition"].get("proposition_id") == proposition_id
        ):
            target = proposition
            break
    if target is None:
        _fail("PROPOSITION_NOT_FOUND")

    execution = target.get("execution")
    if not isinstance(execution, dict):
        _fail("POLICY_PROBE_INPUT_INVALID")
    if (
        execution.get("state") == "completed"
        and execution.get("completion") == "assessed"
        and target.get("reported_verdict") == "supported"
    ):
        return {
            "state": "completed",
            "disposition": "clear",
            "reason": "completed_assessed_supported",
        }
    return {
        "state": "completed",
        "disposition": "hold",
        "reason": "not_completed_assessed_supported",
    }
