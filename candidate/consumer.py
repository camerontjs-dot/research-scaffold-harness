"""Context-free verifier for the Contract C parent-recomposition wire.

The module intentionally contains only public-wire validation and identity
derivation.  It does not perform CAL auditing or derive any destination
policy, authorization, or action semantics.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any, Mapping


INNER_PROFILE = "contract-c-successor-candidate-a-rc2-research"
OUTER_PROFILE = "contract-c-cal-v1-parent-recomposition-rc0"

_INNER_KEYS = {
    "profile",
    "result_set_id",
    "contract_b",
    "producer",
    "execution",
    "propositions",
}
_OUTER_KEYS = {"profile", "result_set_id", "rc2_result", "recomposition"}
_INNER_CONTRACT_B_KEYS = {"contract_version", "bundle_id", "bundle_hash"}
_PRODUCER_KEYS = {
    "semantic_implementation_sha",
    "policy_sha256",
    "policy_resolver_commit_sha",
}
_PROPOSITION_KEYS = {"proposition", "execution", "terminal", "participants", "basis_groups"}
_PROPOSITION_BINDING_KEYS = {"proposition_id", "content_sha256"}
_PROPOSITION_EXECUTION_KEYS = {"state", "completion"}
_TERMINAL_KEYS = {"verdict", "reason"}
_PARTICIPANT_KEYS = {"evidence_ref", "relation", "role"}
_EVIDENCE_REF_KEYS = {"source_id", "passage_id"}
_RECOMPOSITION_KEYS = {
    "cal_freeze_commit",
    "cal_semantic_source_commit",
    "root",
    "decomposition_id",
    "operator",
    "ordered_children",
    "decomposition_receipt_id",
    "parent_conclusion",
}
_ROOT_KEYS = {"proposition_id", "text_sha256"}
_CHILD_KEYS = {
    "sequence",
    "proposition_id",
    "text_sha256",
    "contract_c_content_sha256",
    "native_result_sha256",
    "cal_result_id",
    "conclusion",
}

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_TAGGED64 = re.compile(r"^sha256:[0-9a-f]{64}$")
_CAL_RESULT_ID = re.compile(r"^cal-child-result:[0-9a-f]{64}$")


class ConsumerError(Exception):
    """Raised for every invalid or unauthorised handoff condition."""

    code: str

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _fail(code: str) -> None:
    raise ConsumerError(code)


def _expect_dict(value: Any, code: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(code)
    return value


def _expect_list(value: Any, code: str) -> list[Any]:
    if not isinstance(value, list):
        _fail(code)
    return value


def _expect_exact_keys(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    obj = _expect_dict(value, code)
    if set(obj) != keys:
        _fail(code)
    return obj


def _nonempty_string(value: Any, code: str) -> str:
    if type(value) is not str or not value:
        _fail(code)
    return value


def _tagged_hash(value: Any, code: str) -> str:
    if type(value) is not str or _TAGGED64.fullmatch(value) is None:
        _fail(code)
    return value


def _untagged_hash(value: Any, code: str) -> str:
    if type(value) is not str or _HEX64.fullmatch(value) is None:
        _fail(code)
    return value


def _sha40(value: Any, code: str) -> str:
    if type(value) is not str or _HEX40.fullmatch(value) is None:
        _fail(code)
    return value


def _sha256_tagged(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _canonical_bytes(value: Any, *, trailing_lf: bool) -> bytes:
    try:
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        result = rendered.encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise ConsumerError("CANONICAL_SERIALIZATION_FAILED") from exc
    if trailing_lf:
        result += b"\n"
    return result


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate object key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _parse_json_object(raw: bytes, code: str) -> dict[str, Any]:
    if type(raw) is not bytes:
        _fail(code)
    try:
        text = raw.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ConsumerError(code) from exc
    return _expect_dict(value, code)


def _authority_value(authority: dict[str, Any], *names: str) -> Any:
    present = [(name, authority[name]) for name in names if name in authority]
    if not present:
        _fail("MISSING_EXPECTED_AUTHORITY")
    first = present[0][1]
    if any(value != first for _, value in present[1:]):
        _fail("CONFLICTING_EXPECTED_AUTHORITY")
    return first


def _validate_authority(expected_authority: Any) -> dict[str, Any]:
    authority = _expect_dict(expected_authority, "INVALID_EXPECTED_AUTHORITY")
    profile = _authority_value(authority, "profile")
    if profile != INNER_PROFILE:
        _fail("WRONG_EXPECTED_PROFILE")
    _sha40(
        _authority_value(authority, "semantic_implementation_sha", "cal_semantic_implementation_sha"),
        "INVALID_EXPECTED_SEMANTIC_IMPLEMENTATION",
    )
    _untagged_hash(_authority_value(authority, "policy_sha256"), "INVALID_EXPECTED_POLICY_HASH")
    _sha40(
        _authority_value(authority, "policy_resolver_commit_sha"),
        "INVALID_EXPECTED_POLICY_RESOLVER",
    )
    _tagged_hash(_authority_value(authority, "whole_object_sha256"), "INVALID_EXPECTED_WHOLE_OBJECT_HASH")
    _sha40(_authority_value(authority, "cal_freeze_commit"), "INVALID_EXPECTED_CAL_FREEZE")
    _sha40(_authority_value(authority, "cal_semantic_source_commit"), "INVALID_EXPECTED_CAL_SOURCE")
    return authority


def _extract_contract_b_tuple(contract_b_index: Any) -> tuple[str, str, str]:
    index = _expect_dict(contract_b_index, "INVALID_CONTRACT_B_INDEX")
    candidates: list[dict[str, Any]] = []
    if _INNER_CONTRACT_B_KEYS.issubset(index):
        candidates.append(index)
    nested = index.get("contract_b")
    if isinstance(nested, dict) and _INNER_CONTRACT_B_KEYS.issubset(nested):
        candidates.append(nested)
    if not candidates:
        _fail("MISSING_CONTRACT_B_TUPLE")
    values: list[tuple[str, str, str]] = []
    for candidate in candidates:
        version = _nonempty_string(candidate["contract_version"], "INVALID_CONTRACT_B_VERSION")
        bundle_id = _nonempty_string(candidate["bundle_id"], "INVALID_CONTRACT_B_BUNDLE_ID")
        bundle_hash = _tagged_hash(candidate["bundle_hash"], "INVALID_CONTRACT_B_BUNDLE_HASH")
        values.append((version, bundle_id, bundle_hash))
    if any(value != values[0] for value in values[1:]):
        _fail("CONFLICTING_CONTRACT_B_TUPLE")
    return values[0]


def _extract_passage_refs(contract_b_index: Any) -> set[tuple[str, str]]:
    index = _expect_dict(contract_b_index, "INVALID_CONTRACT_B_INDEX")
    passages = index.get("passages")
    if passages is None:
        _fail("MISSING_CONTRACT_B_PASSAGES")
    refs: set[tuple[str, str]] = set()

    if isinstance(passages, list):
        entries = passages
        for entry in entries:
            item = _expect_dict(entry, "INVALID_CONTRACT_B_PASSAGE")
            source_id = _nonempty_string(item.get("source_id"), "INVALID_CONTRACT_B_SOURCE_ID")
            passage_id = _nonempty_string(item.get("passage_id"), "INVALID_CONTRACT_B_PASSAGE_ID")
            refs.add((source_id, passage_id))
        return refs

    if isinstance(passages, dict):
        # Also accept the common index form {source_id: [passage_id, ...]} or
        # {source_id: {passage_id: metadata, ...}}.  The public wire only
        # depends on exact source/passage membership.
        for source_id, entries in passages.items():
            source = _nonempty_string(source_id, "INVALID_CONTRACT_B_SOURCE_ID")
            if isinstance(entries, list):
                for passage_id in entries:
                    refs.add((source, _nonempty_string(passage_id, "INVALID_CONTRACT_B_PASSAGE_ID")))
            elif isinstance(entries, dict):
                for passage_id in entries:
                    refs.add((source, _nonempty_string(passage_id, "INVALID_CONTRACT_B_PASSAGE_ID")))
            else:
                _fail("INVALID_CONTRACT_B_PASSAGES")
        return refs

    _fail("INVALID_CONTRACT_B_PASSAGES")


def _extract_proposition_digests(contract_b_index: Any) -> dict[str, str]:
    index = _expect_dict(contract_b_index, "INVALID_CONTRACT_B_INDEX")
    propositions = index.get("propositions")
    if propositions is None:
        _fail("MISSING_CONTRACT_B_PROPOSITIONS")
    result: dict[str, str] = {}

    if isinstance(propositions, list):
        for entry in propositions:
            item = _expect_dict(entry, "INVALID_CONTRACT_B_PROPOSITION")
            proposition_id = _nonempty_string(item.get("proposition_id"), "INVALID_PROPOSITION_ID")
            digest = _tagged_hash(item.get("content_sha256"), "INVALID_PROPOSITION_CONTENT_HASH")
            if proposition_id in result:
                _fail("DUPLICATE_CONTRACT_B_PROPOSITION")
            result[proposition_id] = digest
        return result

    if isinstance(propositions, dict):
        for proposition_id, value in propositions.items():
            proposition_id = _nonempty_string(proposition_id, "INVALID_PROPOSITION_ID")
            if isinstance(value, str):
                digest_value = value
            else:
                item = _expect_dict(value, "INVALID_CONTRACT_B_PROPOSITION")
                digest_value = item.get("content_sha256")
            digest = _tagged_hash(digest_value, "INVALID_PROPOSITION_CONTENT_HASH")
            if proposition_id in result:
                _fail("DUPLICATE_CONTRACT_B_PROPOSITION")
            result[proposition_id] = digest
        return result

    _fail("INVALID_CONTRACT_B_PROPOSITIONS")


def _evidence_key(ref: dict[str, Any], *, code: str) -> tuple[str, str]:
    item = _expect_exact_keys(ref, _EVIDENCE_REF_KEYS, code)
    source_id = _nonempty_string(item["source_id"], code)
    passage_id = _nonempty_string(item["passage_id"], code)
    return source_id, passage_id


def _validate_inner_proposition(
    proposition: Any,
    *,
    passage_refs: set[tuple[str, str]],
    proposition_digests: dict[str, str],
) -> tuple[dict[str, Any], str, str]:
    item = _expect_exact_keys(proposition, _PROPOSITION_KEYS, "INVALID_PROPOSITION_RECORD")
    binding = _expect_exact_keys(item["proposition"], _PROPOSITION_BINDING_KEYS, "INVALID_PROPOSITION_BINDING")
    proposition_id = _nonempty_string(binding["proposition_id"], "INVALID_PROPOSITION_ID")
    content_sha256 = _tagged_hash(binding["content_sha256"], "INVALID_PROPOSITION_CONTENT_HASH")
    if proposition_id not in proposition_digests:
        _fail("UNKNOWN_PROPOSITION")
    if proposition_digests[proposition_id] != content_sha256:
        _fail("PROPOSITION_CONTENT_MISMATCH")

    execution = _expect_exact_keys(
        item["execution"], _PROPOSITION_EXECUTION_KEYS, "INVALID_PROPOSITION_EXECUTION"
    )
    proposition_state = execution["state"]
    if proposition_state not in {"completed", "failed", "incomplete"}:
        _fail("INVALID_PROPOSITION_EXECUTION_STATE")
    completion = execution["completion"]
    if completion not in {"assessed", "not_checkable", None}:
        _fail("INVALID_PROPOSITION_COMPLETION")

    participants = _expect_list(item["participants"], "INVALID_PARTICIPANTS")
    participant_by_ref: dict[tuple[str, str], tuple[str, str]] = {}
    normalized_participants: list[dict[str, Any]] = []
    for participant in participants:
        participant_item = _expect_exact_keys(participant, _PARTICIPANT_KEYS, "INVALID_PARTICIPANT")
        ref = _expect_exact_keys(participant_item["evidence_ref"], _EVIDENCE_REF_KEYS, "INVALID_EVIDENCE_REF")
        ref_key = _evidence_key(ref, code="INVALID_EVIDENCE_REF")
        if ref_key not in passage_refs:
            _fail("UNKNOWN_EVIDENCE_REFERENCE")
        if ref_key in participant_by_ref:
            _fail("DUPLICATE_PARTICIPANT")
        relation = participant_item["relation"]
        if relation not in {"supports", "refutes", "non_polarized"}:
            _fail("INVALID_PARTICIPANT_RELATION")
        role = participant_item["role"]
        if role not in {"causal", "residual"}:
            _fail("INVALID_PARTICIPANT_ROLE")
        participant_by_ref[ref_key] = (relation, role)
        normalized_participants.append(copy.deepcopy(participant_item))

    basis_groups = _expect_list(item["basis_groups"], "INVALID_BASIS_GROUPS")
    normalized_groups: list[list[dict[str, Any]]] = []
    group_sets: list[set[tuple[str, str]]] = []
    for group in basis_groups:
        members = _expect_list(group, "INVALID_BASIS_GROUP")
        if not members:
            _fail("EMPTY_BASIS_GROUP")
        member_keys: list[tuple[str, str]] = []
        normalized_group: list[dict[str, Any]] = []
        for member in members:
            member_item = _expect_exact_keys(member, _EVIDENCE_REF_KEYS, "INVALID_BASIS_MEMBER")
            member_key = _evidence_key(member_item, code="INVALID_BASIS_MEMBER")
            if member_key in member_keys:
                _fail("DUPLICATE_BASIS_MEMBER")
            if member_key not in participant_by_ref:
                _fail("UNKNOWN_BASIS_PARTICIPANT")
            member_keys.append(member_key)
            normalized_group.append(copy.deepcopy(member_item))
        member_set = set(member_keys)
        if member_set in group_sets:
            _fail("DUPLICATE_BASIS_GROUP")
        group_sets.append(member_set)
        normalized_group.sort(key=lambda ref: _evidence_key(ref, code="INVALID_BASIS_MEMBER"))
        normalized_groups.append(normalized_group)

    for left_index, left in enumerate(group_sets):
        for right_index, right in enumerate(group_sets):
            if left_index != right_index and left > right:
                _fail("NON_MINIMAL_BASIS_GROUP")

    causal_refs = {ref for ref, (_, role) in participant_by_ref.items() if role == "causal"}
    covered_refs = set().union(*group_sets) if group_sets else set()
    if covered_refs != causal_refs:
        _fail("BASIS_COVERAGE_MISMATCH")

    terminal_value = item["terminal"]
    if proposition_state in {"failed", "incomplete"}:
        if completion is not None or terminal_value is not None or participants or basis_groups:
            _fail("EXECUTION_TERMINAL_LAUNDERING")
    else:
        if completion not in {"assessed", "not_checkable"}:
            _fail("COMPLETED_PROPOSITION_WITHOUT_COMPLETION")
        terminal = _expect_exact_keys(terminal_value, _TERMINAL_KEYS, "INVALID_TERMINAL")
        verdict = terminal["verdict"]
        reason = terminal["reason"]
        if verdict not in {"supported", "contradicted", "not_checkable"}:
            _fail("INVALID_TERDICT")
        if completion == "assessed" and verdict not in {"supported", "contradicted"}:
            _fail("COMPLETION_VERDICT_MISMATCH")
        if completion == "not_checkable" and verdict != "not_checkable":
            _fail("COMPLETION_VERDICT_MISMATCH")
        if verdict == "supported" and reason != "categorical_support":
            _fail("VERDICT_REASON_MISMATCH")
        if verdict == "contradicted" and reason != "categorical_refutation":
            _fail("VERDICT_REASON_MISMATCH")
        if verdict == "not_checkable" and reason not in {
            "MIXED_RELATIONS",
            "unresolved_categorical_relation",
            "joint_public_cause",
            "no_deciding_relation",
            "UNSUPPORTED_SEMANTIC_FAMILY",
        }:
            _fail("VERDICT_REASON_MISMATCH")

        if verdict in {"supported", "contradicted"}:
            if not group_sets:
                _fail("MISSING_CATEGORICAL_BASIS")
            expected_relation = "supports" if verdict == "supported" else "refutes"
            for group_set in group_sets:
                if any(participant_by_ref[ref][0] != expected_relation for ref in group_set):
                    _fail("RELATION_TERMINAL_MISMATCH")
        elif reason == "MIXED_RELATIONS":
            if not group_sets:
                _fail("MISSING_MIXED_BASIS")
            for group_set in group_sets:
                relations = {participant_by_ref[ref][0] for ref in group_set}
                if "supports" not in relations or "refutes" not in relations or "non_polarized" in relations:
                    _fail("MIXED_RELATION_TERMINAL_MISMATCH")
        elif reason in {"unresolved_categorical_relation", "joint_public_cause"}:
            if not group_sets:
                _fail("MISSING_NONPOLARIZED_BASIS")
            for group_set in group_sets:
                if any(participant_by_ref[ref][0] != "non_polarized" for ref in group_set):
                    _fail("NONPOLARIZED_TERMINAL_MISMATCH")
        else:
            if group_sets:
                _fail("UNEXPECTED_EMPTY_BASIS_TERMINAL")
            if any(relation != "non_polarized" or role != "residual" for relation, role in participant_by_ref.values()):
                _fail("RESIDUAL_TERMINAL_MISMATCH")

    normalized_participants.sort(
        key=lambda participant: _evidence_key(participant["evidence_ref"], code="INVALID_EVIDENCE_REF")
    )
    normalized_groups.sort(
        key=lambda group: tuple(_evidence_key(member, code="INVALID_BASIS_MEMBER") for member in group)
    )

    normalized = copy.deepcopy(item)
    normalized["participants"] = normalized_participants
    normalized["basis_groups"] = normalized_groups
    terminal_verdict = None
    if proposition_state == "completed":
        terminal_verdict = item["terminal"]["verdict"]
    return normalized, proposition_id, terminal_verdict or ""


def _validate_inner(
    rc2: Any,
    *,
    contract_b_tuple: tuple[str, str, str],
    passage_refs: set[tuple[str, str]],
    proposition_digests: dict[str, str],
    authority: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, tuple[dict[str, Any], str]]]:
    item = _expect_exact_keys(rc2, _INNER_KEYS, "INVALID_INNER_OBJECT")
    if item["profile"] != INNER_PROFILE:
        _fail("WRONG_INNER_PROFILE")
    if _authority_value(authority, "profile") != item["profile"]:
        _fail("INNER_PROFILE_AUTHORITY_MISMATCH")

    contract_b = _expect_exact_keys(item["contract_b"], _INNER_CONTRACT_B_KEYS, "INVALID_INNER_CONTRACT_B")
    actual_contract_b = (
        _nonempty_string(contract_b["contract_version"], "INVALID_CONTRACT_B_VERSION"),
        _nonempty_string(contract_b["bundle_id"], "INVALID_CONTRACT_B_BUNDLE_ID"),
        _tagged_hash(contract_b["bundle_hash"], "INVALID_CONTRACT_B_BUNDLE_HASH"),
    )
    if actual_contract_b != contract_b_tuple:
        _fail("CONTRACT_B_TUPLE_MISMATCH")

    producer = _expect_exact_keys(item["producer"], _PRODUCER_KEYS, "INVALID_PRODUCER")
    semantic_implementation_sha = _sha40(
        producer["semantic_implementation_sha"], "INVALID_SEMANTIC_IMPLEMENTATION"
    )
    policy_sha256 = _untagged_hash(producer["policy_sha256"], "INVALID_POLICY_HASH")
    policy_resolver_commit_sha = _sha40(
        producer["policy_resolver_commit_sha"], "INVALID_POLICY_RESOLVER"
    )
    if semantic_implementation_sha != _authority_value(
        authority, "semantic_implementation_sha", "cal_semantic_implementation_sha"
    ):
        _fail("SEMANTIC_IMPLEMENTATION_AUTHORITY_MISMATCH")
    if policy_sha256 != _authority_value(authority, "policy_sha256"):
        _fail("POLICY_AUTHORITY_MISMATCH")
    if policy_resolver_commit_sha != _authority_value(authority, "policy_resolver_commit_sha"):
        _fail("POLICY_RESOLVER_AUTHORITY_MISMATCH")

    result_execution = _expect_exact_keys(item["execution"], {"state"}, "INVALID_RESULT_EXECUTION")
    result_state = result_execution["state"]
    if result_state not in {"completed", "failed", "incomplete"}:
        _fail("INVALID_RESULT_EXECUTION_STATE")
    propositions = _expect_list(item["propositions"], "INVALID_PROPOSITIONS")
    if result_state in {"failed", "incomplete"} and propositions:
        _fail("RESULT_EXECUTION_PROPOSITION_LAUNDERING")

    normalized_propositions: list[dict[str, Any]] = []
    proposition_details: dict[str, tuple[dict[str, Any], str]] = {}
    for proposition in propositions:
        normalized, proposition_id, verdict = _validate_inner_proposition(
            proposition,
            passage_refs=passage_refs,
            proposition_digests=proposition_digests,
        )
        if proposition_id in proposition_details:
            _fail("DUPLICATE_PROPOSITION")
        normalized_propositions.append(normalized)
        proposition_details[proposition_id] = (normalized, verdict)

    normalized_propositions.sort(
        key=lambda proposition: (
            proposition["proposition"]["proposition_id"],
            proposition["proposition"]["content_sha256"],
        )
    )
    without_id = copy.deepcopy(item)
    without_id.pop("result_set_id")
    without_id["propositions"] = normalized_propositions
    expected_result_set_id = _sha256_tagged(_canonical_bytes(without_id, trailing_lf=True))
    result_set_id = _tagged_hash(item["result_set_id"], "INVALID_INNER_RESULT_SET_ID")
    if result_set_id != expected_result_set_id:
        _fail("INNER_RESULT_SET_ID_MISMATCH")

    normalized_item = copy.deepcopy(without_id)
    normalized_item["result_set_id"] = result_set_id
    return normalized_item, proposition_details


def _read_decomposition(decomposition: Any) -> tuple[str, tuple[str, str], list[dict[str, Any]]]:
    item = _expect_dict(decomposition, "INVALID_CONTRACT_A_DECOMPOSITION")
    if item.get("state") != "declared":
        _fail("INVALID_DECOMPOSITION_STATE")
    decomposition_id = _nonempty_string(item.get("decomposition_id"), "INVALID_DECOMPOSITION_ID")
    if item.get("operator") != "all_of":
        _fail("INVALID_DECOMPOSITION_OPERATOR")

    root_value = item.get("root")
    if root_value is None and {"root_proposition_id", "root_text_sha256"}.issubset(item):
        root_value = {
            "proposition_id": item["root_proposition_id"],
            "text_sha256": item["root_text_sha256"],
        }
    root = _expect_exact_keys(root_value, _ROOT_KEYS, "INVALID_DECOMPOSITION_ROOT")
    root_id = _nonempty_string(root["proposition_id"], "INVALID_ROOT_PROPOSITION_ID")
    root_text = _tagged_hash(root["text_sha256"], "INVALID_ROOT_TEXT_HASH")

    children_value = item.get("children")
    if children_value is None:
        children_value = item.get("ordered_children")
    children = _expect_list(children_value, "INVALID_DECOMPOSITION_CHILDREN")
    if len(children) < 2:
        _fail("INSUFFICIENT_DECOMPOSITION_CHILDREN")
    normalized_children: list[dict[str, Any]] = []
    seen_sequences: set[int] = set()
    seen_ids: set[str] = set()
    for child in children:
        child_item = _expect_dict(child, "INVALID_DECOMPOSITION_CHILD")
        sequence = child_item.get("sequence")
        if type(sequence) is not int or sequence < 1:
            _fail("INVALID_DECOMPOSITION_SEQUENCE")
        proposition_id = _nonempty_string(child_item.get("proposition_id"), "INVALID_CHILD_PROPOSITION_ID")
        text_sha256 = _tagged_hash(child_item.get("text_sha256"), "INVALID_CHILD_TEXT_HASH")
        if sequence in seen_sequences or proposition_id in seen_ids:
            _fail("DUPLICATE_DECOMPOSITION_CHILD")
        if proposition_id == root_id:
            _fail("ROOT_AS_DECOMPOSITION_CHILD")
        seen_sequences.add(sequence)
        seen_ids.add(proposition_id)
        normalized_children.append(
            {
                "sequence": sequence,
                "proposition_id": proposition_id,
                "text_sha256": text_sha256,
            }
        )
    expected_sequences = set(range(1, len(normalized_children) + 1))
    if seen_sequences != expected_sequences:
        _fail("NONCONTIGUOUS_DECOMPOSITION_SEQUENCE")
    normalized_children.sort(key=lambda child: child["sequence"])
    return decomposition_id, (root_id, root_text), normalized_children


def _parse_native_child(raw: bytes) -> tuple[str, str, str, str]:
    native = _parse_json_object(raw, "INVALID_NATIVE_RESULT_JSON")
    proposition = _expect_dict(native.get("proposition"), "INVALID_NATIVE_PROPOSITION")
    result = _expect_dict(native.get("result"), "INVALID_NATIVE_RESULT")
    proposition_id = _nonempty_string(proposition.get("proposition_id"), "INVALID_NATIVE_PROPOSITION_ID")
    text_sha256 = _untagged_hash(proposition.get("text_sha256"), "INVALID_NATIVE_TEXT_HASH")
    proposition_sha256 = _untagged_hash(
        proposition.get("proposition_sha256"), "INVALID_NATIVE_PROPOSITION_HASH"
    )
    conclusion = result.get("conclusion")
    if conclusion not in {"supported", "contradicted", "not_checkable"}:
        _fail("INVALID_NATIVE_CONCLUSION")
    return proposition_id, text_sha256, proposition_sha256, conclusion


def consume_parent_bound_contract_c(
    raw: bytes,
    *,
    contract_b_index: dict,
    expected_authority: dict,
    contract_a_decomposition: dict,
    native_child_results: dict[str, bytes],
) -> dict:
    """Validate and return a deterministic public Contract C projection."""

    authority = _validate_authority(expected_authority)
    contract_b_tuple = _extract_contract_b_tuple(contract_b_index)
    passage_refs = _extract_passage_refs(contract_b_index)
    proposition_digests = _extract_proposition_digests(contract_b_index)
    outer = _parse_json_object(raw, "INVALID_OUTER_JSON")
    outer = _expect_exact_keys(outer, _OUTER_KEYS, "INVALID_OUTER_OBJECT")
    if outer["profile"] != OUTER_PROFILE:
        _fail("WRONG_OUTER_PROFILE")

    rc2_normalized, proposition_details = _validate_inner(
        outer["rc2_result"],
        contract_b_tuple=contract_b_tuple,
        passage_refs=passage_refs,
        proposition_digests=proposition_digests,
        authority=authority,
    )

    recomposition = _expect_exact_keys(outer["recomposition"], _RECOMPOSITION_KEYS, "INVALID_RECOMPOSITION")
    cal_freeze_commit = _sha40(recomposition["cal_freeze_commit"], "INVALID_CAL_FREEZE_COMMIT")
    cal_semantic_source_commit = _sha40(
        recomposition["cal_semantic_source_commit"], "INVALID_CAL_SOURCE_COMMIT"
    )
    if cal_freeze_commit != _authority_value(authority, "cal_freeze_commit"):
        _fail("CAL_FREEZE_AUTHORITY_MISMATCH")
    if cal_semantic_source_commit != _authority_value(authority, "cal_semantic_source_commit"):
        _fail("CAL_SOURCE_AUTHORITY_MISMATCH")

    decomposition_id, (root_id, root_text), declared_children = _read_decomposition(contract_a_decomposition)
    outer_root = _expect_exact_keys(recomposition["root"], _ROOT_KEYS, "INVALID_OUTER_ROOT")
    if (
        _nonempty_string(outer_root["proposition_id"], "INVALID_OUTER_ROOT_ID"),
        _tagged_hash(outer_root["text_sha256"], "INVALID_OUTER_ROOT_HASH"),
    ) != (root_id, root_text):
        _fail("ROOT_BINDING_MISMATCH")
    if _nonempty_string(recomposition["decomposition_id"], "INVALID_RECOMPOSITION_ID") != decomposition_id:
        _fail("DECOMPOSITION_ID_MISMATCH")
    if recomposition["operator"] != "all_of":
        _fail("INVALID_RECOMPOSITION_OPERATOR")

    ordered_children = _expect_list(recomposition["ordered_children"], "INVALID_ORDERED_CHILDREN")
    if len(ordered_children) != len(declared_children) or len(ordered_children) < 2:
        _fail("CHILD_COUNT_MISMATCH")
    children_by_sequence: dict[int, dict[str, Any]] = {}
    child_ids: set[str] = set()
    for child in ordered_children:
        child_item = _expect_exact_keys(child, _CHILD_KEYS, "INVALID_ORDERED_CHILD")
        sequence = child_item["sequence"]
        if type(sequence) is not int or sequence < 1 or sequence in children_by_sequence:
            _fail("INVALID_ORDERED_CHILD_SEQUENCE")
        proposition_id = _nonempty_string(child_item["proposition_id"], "INVALID_ORDERED_CHILD_ID")
        if proposition_id in child_ids:
            _fail("DUPLICATE_ORDERED_CHILD")
        child_ids.add(proposition_id)
        _tagged_hash(child_item["text_sha256"], "INVALID_ORDERED_CHILD_TEXT_HASH")
        _tagged_hash(child_item["contract_c_content_sha256"], "INVALID_CHILD_CONTENT_HASH")
        _tagged_hash(child_item["native_result_sha256"], "INVALID_NATIVE_RESULT_HASH")
        if _CAL_RESULT_ID.fullmatch(child_item["cal_result_id"]) is None:
            _fail("INVALID_CAL_RESULT_ID")
        if child_item["conclusion"] not in {"supported", "contradicted", "not_checkable"}:
            _fail("INVALID_CHILD_CONCLUSION")
        children_by_sequence[sequence] = child_item

    if set(children_by_sequence) != set(range(1, len(declared_children) + 1)):
        _fail("NONCONTIGUOUS_ORDERED_CHILD_SEQUENCE")
    ordered_by_sequence = [children_by_sequence[sequence] for sequence in sorted(children_by_sequence)]
    declared_by_sequence = {child["sequence"]: child for child in declared_children}
    if set(child_ids) != set(proposition_details):
        _fail("NESTED_PROPOSITION_SET_MISMATCH")
    if set(native_child_results) != child_ids:
        _fail("NATIVE_CHILD_SET_MISMATCH")

    seen_result_ids: set[str] = set()
    for child in ordered_by_sequence:
        sequence = child["sequence"]
        declared = declared_by_sequence[sequence]
        if (
            child["proposition_id"],
            child["text_sha256"],
        ) != (declared["proposition_id"], declared["text_sha256"]):
            _fail("CHILD_DECLARATION_BINDING_MISMATCH")
        proposition_id = child["proposition_id"]
        if proposition_id != declared["proposition_id"]:
            _fail("CHILD_PROPOSITION_MISMATCH")
        proposition_record, inner_verdict = proposition_details[proposition_id]
        native_raw = native_child_results[proposition_id]
        if type(native_raw) is not bytes:
            _fail("INVALID_NATIVE_RESULT_BYTES")
        native_id, native_text, native_content, native_conclusion = _parse_native_child(native_raw)
        if native_id != proposition_id:
            _fail("NATIVE_PROPOSITION_MISMATCH")
        if "sha256:" + native_text != child["text_sha256"]:
            _fail("NATIVE_TEXT_BINDING_MISMATCH")
        if child["contract_c_content_sha256"] != "sha256:" + native_content:
            _fail("NATIVE_CONTENT_BINDING_MISMATCH")
        native_hash = _sha256_tagged(native_raw)
        if child["native_result_sha256"] != native_hash:
            _fail("NATIVE_RESULT_HASH_MISMATCH")
        if child["conclusion"] != native_conclusion:
            _fail("CHILD_NATIVE_CONCLUSION_MISMATCH")
        if child["conclusion"] != inner_verdict:
            _fail("CHILD_INNER_CONCLUSION_MISMATCH")

        identity_material = {
            "proposition_id": proposition_id,
            "text_sha256": child["text_sha256"],
            "audit_result_sha256": native_hash,
            "conclusion": child["conclusion"],
        }
        derived_result_id = "cal-child-result:" + hashlib.sha256(
            _canonical_bytes(identity_material, trailing_lf=False)
        ).hexdigest()
        if child["cal_result_id"] != derived_result_id:
            _fail("CAL_RESULT_ID_MISMATCH")
        if child["cal_result_id"] in seen_result_ids:
            _fail("REUSED_CAL_RESULT_ID")
        seen_result_ids.add(child["cal_result_id"])
        if proposition_record["terminal"]["verdict"] != child["conclusion"]:
            _fail("INNER_TERMINAL_CONCLUSION_MISMATCH")

    child_conclusions = [child["conclusion"] for child in ordered_by_sequence]
    if any(conclusion == "contradicted" for conclusion in child_conclusions):
        parent_conclusion = "contradicted"
    elif all(conclusion == "supported" for conclusion in child_conclusions):
        parent_conclusion = "supported"
    else:
        parent_conclusion = "not_checkable"
    if recomposition["parent_conclusion"] != parent_conclusion:
        _fail("PARENT_CONCLUSION_MISMATCH")

    receipt_material = {
        "root_proposition_id": root_id,
        "root_text_sha256": root_text,
        "decomposition_state": "declared",
        "decomposition_id": decomposition_id,
        "operator": "all_of",
        "ordered_children": [
            {
                "proposition_id": child["proposition_id"],
                "text_sha256": child["text_sha256"],
                "result_id": child["cal_result_id"],
                "conclusion": child["conclusion"],
            }
            for child in ordered_by_sequence
        ],
        "root_result_id": None,
        "parent_conclusion": parent_conclusion,
    }
    receipt_id = recomposition["decomposition_receipt_id"]
    if type(receipt_id) is not str or _HEX64.fullmatch(receipt_id) is None:
        _fail("INVALID_DECOMPOSITION_RECEIPT_ID")
    derived_receipt_id = hashlib.sha256(_canonical_bytes(receipt_material, trailing_lf=False)).hexdigest()
    if receipt_id != derived_receipt_id:
        _fail("DECOMPOSITION_RECEIPT_ID_MISMATCH")

    normalized_outer = copy.deepcopy(outer)
    normalized_outer["rc2_result"] = rc2_normalized
    normalized_recomposition = normalized_outer["recomposition"]
    normalized_recomposition["ordered_children"] = [copy.deepcopy(child) for child in ordered_by_sequence]
    normalized_outer["recomposition"] = normalized_recomposition
    without_outer_id = copy.deepcopy(normalized_outer)
    without_outer_id.pop("result_set_id")
    expected_outer_id = _sha256_tagged(_canonical_bytes(without_outer_id, trailing_lf=True))
    outer_result_set_id = _tagged_hash(outer["result_set_id"], "INVALID_OUTER_RESULT_SET_ID")
    if outer_result_set_id != expected_outer_id:
        _fail("OUTER_RESULT_SET_ID_MISMATCH")
    normalized_outer["result_set_id"] = outer_result_set_id
    canonical_outer = _canonical_bytes(normalized_outer, trailing_lf=True)
    if raw != canonical_outer:
        _fail("NON_CANONICAL_OUTER_BYTES")
    expected_whole_object = _authority_value(authority, "whole_object_sha256")
    if _sha256_tagged(raw) != expected_whole_object:
        _fail("WHOLE_OBJECT_AUTHORITY_MISMATCH")
    return normalized_outer


__all__ = ["ConsumerError", "consume_parent_bound_contract_c"]
