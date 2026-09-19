"""Context-free Contract C Candidate A RC2 parent-binding consumer.

The module deliberately implements only the public wire, identity, and
binding checks described by the supplied aperture.  It does not audit child
evidence or derive any operational decision.
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any


OUTER_PROFILE = "contract-c-cal-v1-parent-recomposition-rc0"
INNER_PROFILE = "contract-c-successor-candidate-a-rc2-research"

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_TAGGED_HEX64 = re.compile(r"^sha256:[0-9a-f]{64}$")
_CAL_RESULT_ID = re.compile(r"^cal-child-result:[0-9a-f]{64}$")


class ConsumerError(Exception):
    """A fail-closed validation error with a stable machine-readable code."""

    code: str

    def __init__(self, code: str, message: str | None = None) -> None:
        self.code = code
        super().__init__(message or code)


def _fail(code: str, message: str | None = None) -> None:
    raise ConsumerError(code, message)


def _strict_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail("DUPLICATE_JSON_KEY", f"duplicate key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    _fail("NONFINITE_JSON", f"non-finite JSON constant: {value}")


def _parse_json(raw: bytes, *, code_prefix: str) -> dict[str, Any]:
    if not isinstance(raw, (bytes, bytearray)):
        _fail(f"{code_prefix}_BYTES")
    try:
        text = bytes(raw).decode("utf-8")
    except UnicodeDecodeError as exc:
        _fail(f"{code_prefix}_UTF8", str(exc))
    try:
        value = json.loads(
            text,
            object_pairs_hook=_strict_pairs,
            parse_constant=_reject_constant,
        )
    except ConsumerError:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        _fail(f"{code_prefix}_JSON", str(exc))
    if not isinstance(value, dict):
        _fail(f"{code_prefix}_TOP_LEVEL")
    return value


def _canonical_json(value: Any, *, trailing_lf: bool) -> bytes:
    try:
        text = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError) as exc:
        _fail("CANONICAL_SERIALIZATION", str(exc))
    return text.encode("utf-8") + (b"\n" if trailing_lf else b"")


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _tagged_digest(raw: bytes) -> str:
    return "sha256:" + _sha256(raw)


def _require_exact_keys(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _fail(code)
    return value


def _require_keys(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not keys.issubset(value):
        _fail(code)
    return value


def _nonempty_string(value: Any, code: str, *, nonblank: bool = False) -> str:
    if not isinstance(value, str) or not value:
        _fail(code)
    if nonblank and not value.strip():
        _fail(code)
    return value


def _tagged_hex(value: Any, code: str) -> str:
    if not isinstance(value, str) or not _TAGGED_HEX64.fullmatch(value):
        _fail(code)
    return value


def _hex64(value: Any, code: str) -> str:
    if not isinstance(value, str) or not _HEX64.fullmatch(value):
        _fail(code)
    return value


def _hex40(value: Any, code: str) -> str:
    if not isinstance(value, str) or not _HEX40.fullmatch(value):
        _fail(code)
    return value


def _sequence(value: Any, code: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        _fail(code)
    return value


def _pair(value: Any, code: str) -> tuple[str, str]:
    item = _require_exact_keys(value, {"source_id", "passage_id"}, code)
    return (
        _nonempty_string(item["source_id"], code),
        _nonempty_string(item["passage_id"], code),
    )


def _alias_value(value: dict[str, Any], names: tuple[str, ...], code: str) -> Any:
    present = [name for name in names if name in value]
    if not present:
        _fail(code)
    first = value[present[0]]
    if any(value[name] != first for name in present[1:]):
        _fail(code)
    return first


def _digest_unprefixed(value: Any, code: str) -> str:
    if isinstance(value, str) and value.startswith("sha256:"):
        value = value[7:]
    return _hex64(value, code)


def _contract_b_binding(index: dict[str, Any]) -> dict[str, str]:
    if not isinstance(index, dict):
        _fail("CONTRACT_B_INDEX_SHAPE")

    candidates: list[dict[str, Any]] = []
    if {"contract_version", "bundle_id", "bundle_hash"}.issubset(index):
        candidates.append(index)
    nested = index.get("contract_b")
    if isinstance(nested, dict) and {"contract_version", "bundle_id", "bundle_hash"}.issubset(nested):
        candidates.append(nested)
    if not candidates:
        _fail("CONTRACT_B_BINDING_MISSING")

    tuples: list[tuple[str, str, str]] = []
    for candidate in candidates:
        version = _nonempty_string(candidate["contract_version"], "CONTRACT_B_VERSION")
        bundle_id = _nonempty_string(candidate["bundle_id"], "CONTRACT_B_BUNDLE_ID")
        bundle_hash = _tagged_hex(candidate["bundle_hash"], "CONTRACT_B_BUNDLE_HASH")
        tuples.append((version, bundle_id, bundle_hash))
    if len(set(tuples)) != 1:
        _fail("CONTRACT_B_BINDING_AMBIGUOUS")
    version, bundle_id, bundle_hash = tuples[0]
    return {
        "contract_version": version,
        "bundle_id": bundle_id,
        "bundle_hash": bundle_hash,
    }


def _proposition_digest(record: Any, default_id: str | None, code: str) -> tuple[str, str]:
    if isinstance(record, str):
        if default_id is None:
            _fail(code)
        return default_id, _digest_unprefixed(record, code)
    if not isinstance(record, dict):
        _fail(code)
    proposition_id = record.get("proposition_id", record.get("id", default_id))
    proposition_id = _nonempty_string(proposition_id, code)
    digest_value = None
    for name in ("content_sha256", "proposition_sha256", "sha256"):
        if name in record:
            if digest_value is not None and record[name] != digest_value:
                _fail(code)
            digest_value = record[name]
    if digest_value is None:
        _fail(code)
    return proposition_id, _digest_unprefixed(digest_value, code)


def _contract_b_propositions(index: dict[str, Any]) -> dict[str, str]:
    source = index.get("propositions")
    if source is None and isinstance(index.get("contract_b"), dict):
        source = index["contract_b"].get("propositions")
    if source is None:
        _fail("CONTRACT_B_PROPOSITIONS_MISSING")

    result: dict[str, str] = {}
    if isinstance(source, dict):
        records = list(source.items())
        for default_id, record in records:
            proposition_id, digest = _proposition_digest(record, default_id, "CONTRACT_B_PROPOSITION")
            if proposition_id != default_id and default_id:
                _fail("CONTRACT_B_PROPOSITION_ID")
            if proposition_id in result and result[proposition_id] != digest:
                _fail("CONTRACT_B_PROPOSITION_DUPLICATE")
            result[proposition_id] = digest
    elif isinstance(source, list):
        for record in source:
            proposition_id, digest = _proposition_digest(record, None, "CONTRACT_B_PROPOSITION")
            if proposition_id in result:
                _fail("CONTRACT_B_PROPOSITION_DUPLICATE")
            result[proposition_id] = digest
    else:
        _fail("CONTRACT_B_PROPOSITIONS_SHAPE")
    if not result:
        _fail("CONTRACT_B_PROPOSITIONS_EMPTY")
    return result


def _add_passage(result: set[tuple[str, str]], source_id: Any, passage_id: Any, code: str) -> None:
    pair = (
        _nonempty_string(source_id, code),
        _nonempty_string(passage_id, code),
    )
    if pair in result:
        _fail("CONTRACT_B_PASSAGE_DUPLICATE")
    result.add(pair)


def _contract_b_passages(index: dict[str, Any]) -> set[tuple[str, str]]:
    source = index.get("passages")
    if source is None and isinstance(index.get("contract_b"), dict):
        source = index["contract_b"].get("passages")
    if source is None:
        _fail("CONTRACT_B_PASSAGES_MISSING")

    result: set[tuple[str, str]] = set()
    if isinstance(source, list):
        for record in source:
            if not isinstance(record, dict):
                _fail("CONTRACT_B_PASSAGE")
            if "source_id" not in record or "passage_id" not in record:
                _fail("CONTRACT_B_PASSAGE")
            _add_passage(result, record["source_id"], record["passage_id"], "CONTRACT_B_PASSAGE")
    elif isinstance(source, dict):
        for key, record in source.items():
            if isinstance(record, dict) and "source_id" in record:
                passage_id = record.get("passage_id", key)
                _add_passage(result, record["source_id"], passage_id, "CONTRACT_B_PASSAGE")
                continue
            if isinstance(record, dict):
                source_id = _nonempty_string(key, "CONTRACT_B_PASSAGE")
                for passage_id in record:
                    _add_passage(result, source_id, passage_id, "CONTRACT_B_PASSAGE")
                continue
            _fail("CONTRACT_B_PASSAGE")
    else:
        _fail("CONTRACT_B_PASSAGES_SHAPE")
    if not result:
        _fail("CONTRACT_B_PASSAGES_EMPTY")
    return result


def _read_authority(expected_authority: Any) -> dict[str, str]:
    if not isinstance(expected_authority, dict):
        _fail("EXPECTED_AUTHORITY_SHAPE")
    explicit_outer = None
    if "outer_profile" in expected_authority:
        explicit_outer = expected_authority["outer_profile"]
    explicit_inner = None
    if "inner_profile" in expected_authority or "rc2_profile" in expected_authority:
        explicit_inner = _alias_value(
            expected_authority,
            ("inner_profile", "rc2_profile"),
            "EXPECTED_INNER_PROFILE",
        )
    supplied_profile = expected_authority.get("profile")
    if supplied_profile is not None:
        supplied_profile = _nonempty_string(supplied_profile, "EXPECTED_PROFILE")
        if supplied_profile not in {OUTER_PROFILE, INNER_PROFILE}:
            _fail("EXPECTED_PROFILE_MISMATCH")
        if supplied_profile == OUTER_PROFILE:
            if explicit_outer is not None and explicit_outer != supplied_profile:
                _fail("EXPECTED_PROFILE")
            explicit_outer = supplied_profile
        else:
            if explicit_inner is not None and explicit_inner != supplied_profile:
                _fail("EXPECTED_INNER_PROFILE")
            explicit_inner = supplied_profile
    values = {
        "profile": explicit_outer if explicit_outer is not None else OUTER_PROFILE,
        "inner_profile": explicit_inner if explicit_inner is not None else INNER_PROFILE,
        "cal_freeze_commit": _alias_value(
            expected_authority,
            ("cal_freeze_commit",),
            "EXPECTED_CAL_FREEZE_COMMIT",
        ),
        "cal_semantic_source_commit": _alias_value(
            expected_authority,
            ("cal_semantic_source_commit",),
            "EXPECTED_CAL_SOURCE_COMMIT",
        ),
        "semantic_implementation_sha": _alias_value(
            expected_authority,
            ("semantic_implementation_sha", "cal_semantic_implementation_sha"),
            "EXPECTED_SEMANTIC_IMPLEMENTATION",
        ),
        "policy_sha256": _alias_value(expected_authority, ("policy_sha256",), "EXPECTED_POLICY"),
        "policy_resolver_commit_sha": _alias_value(
            expected_authority,
            ("policy_resolver_commit_sha",),
            "EXPECTED_POLICY_RESOLVER",
        ),
        "whole_object_sha256": _alias_value(
            expected_authority,
            ("whole_object_sha256",),
            "EXPECTED_WHOLE_OBJECT",
        ),
    }
    values["profile"] = _nonempty_string(values["profile"], "EXPECTED_PROFILE")
    values["inner_profile"] = _nonempty_string(values["inner_profile"], "EXPECTED_INNER_PROFILE")
    values["cal_freeze_commit"] = _hex40(values["cal_freeze_commit"], "EXPECTED_CAL_FREEZE_COMMIT")
    values["cal_semantic_source_commit"] = _hex40(
        values["cal_semantic_source_commit"], "EXPECTED_CAL_SOURCE_COMMIT"
    )
    values["semantic_implementation_sha"] = _hex40(
        values["semantic_implementation_sha"], "EXPECTED_SEMANTIC_IMPLEMENTATION"
    )
    values["policy_sha256"] = _hex64(values["policy_sha256"], "EXPECTED_POLICY")
    values["policy_resolver_commit_sha"] = _hex40(
        values["policy_resolver_commit_sha"], "EXPECTED_POLICY_RESOLVER"
    )
    values["whole_object_sha256"] = _tagged_hex(values["whole_object_sha256"], "EXPECTED_WHOLE_OBJECT")
    if values["profile"] != OUTER_PROFILE:
        _fail("EXPECTED_PROFILE_MISMATCH")
    if values["inner_profile"] != INNER_PROFILE:
        _fail("EXPECTED_INNER_PROFILE_MISMATCH")
    return values


def _decomposition(declaration: Any) -> dict[str, Any]:
    if not isinstance(declaration, dict):
        _fail("DECOMPOSITION_SHAPE")
    state = declaration.get("state")
    if state != "declared":
        _fail("DECOMPOSITION_STATE")
    decomposition_id = _nonempty_string(
        declaration.get("decomposition_id"), "DECOMPOSITION_ID", nonblank=True
    )
    operator = declaration.get("operator")
    if operator != "all_of":
        _fail("DECOMPOSITION_OPERATOR")
    root = _require_exact_keys(
        declaration.get("root"), {"proposition_id", "text_sha256"}, "DECOMPOSITION_ROOT"
    )
    root_id = _nonempty_string(root["proposition_id"], "DECOMPOSITION_ROOT")
    root_text = _tagged_hex(root["text_sha256"], "DECOMPOSITION_ROOT")
    if "children" in declaration and "ordered_children" in declaration:
        if declaration["children"] != declaration["ordered_children"]:
            _fail("DECOMPOSITION_CHILDREN_AMBIGUOUS")
    children_value = declaration.get("children", declaration.get("ordered_children"))
    if not isinstance(children_value, list) or len(children_value) < 2:
        _fail("DECOMPOSITION_CHILDREN")

    children: dict[int, dict[str, Any]] = {}
    child_ids: set[str] = set()
    for child in children_value:
        item = _require_exact_keys(
            child,
            {"sequence", "proposition_id", "text_sha256"},
            "DECOMPOSITION_CHILD",
        )
        sequence = _sequence(item["sequence"], "DECOMPOSITION_SEQUENCE")
        proposition_id = _nonempty_string(item["proposition_id"], "DECOMPOSITION_CHILD")
        text_sha256 = _tagged_hex(item["text_sha256"], "DECOMPOSITION_CHILD")
        if sequence in children or proposition_id in child_ids:
            _fail("DECOMPOSITION_CHILD_DUPLICATE")
        if proposition_id == root_id:
            _fail("DECOMPOSITION_ROOT_CHILD_COLLISION")
        children[sequence] = {
            "sequence": sequence,
            "proposition_id": proposition_id,
            "text_sha256": text_sha256,
        }
        child_ids.add(proposition_id)
    expected_sequences = set(range(1, len(children) + 1))
    if set(children) != expected_sequences:
        _fail("DECOMPOSITION_SEQUENCE_GAP")
    return {
        "state": "declared",
        "decomposition_id": decomposition_id,
        "operator": "all_of",
        "root": {"proposition_id": root_id, "text_sha256": root_text},
        "children": [children[number] for number in sorted(children)],
    }


def _participant_map(record: dict[str, Any], passages: set[tuple[str, str]]) -> tuple[
    dict[tuple[str, str], tuple[str, str]], list[dict[str, Any]]
]:
    participants = record["participants"]
    if not isinstance(participants, list):
        _fail("PARTICIPANTS_SHAPE")
    seen: set[tuple[str, str]] = set()
    mapping: dict[tuple[str, str], tuple[str, str]] = {}
    normalized: list[dict[str, Any]] = []
    for participant in participants:
        item = _require_exact_keys(
            participant,
            {"evidence_ref", "relation", "role"},
            "PARTICIPANT_SHAPE",
        )
        ref = _pair(item["evidence_ref"], "PARTICIPANT_REFERENCE")
        if ref not in passages:
            _fail("EVIDENCE_REFERENCE_NOT_IN_CONTRACT_B")
        if ref in seen:
            _fail("DUPLICATE_PARTICIPANT")
        relation = item["relation"]
        role = item["role"]
        if relation not in {"supports", "refutes", "non_polarized"}:
            _fail("PARTICIPANT_RELATION")
        if role not in {"causal", "residual"}:
            _fail("PARTICIPANT_ROLE")
        seen.add(ref)
        mapping[ref] = (relation, role)
        normalized.append(
            {
                "evidence_ref": {"source_id": ref[0], "passage_id": ref[1]},
                "relation": relation,
                "role": role,
            }
        )
    return mapping, normalized


def _basis_groups(
    record: dict[str, Any],
    participants: dict[tuple[str, str], tuple[str, str]],
) -> tuple[list[list[dict[str, str]]], list[set[tuple[str, str]]]]:
    groups = record["basis_groups"]
    if not isinstance(groups, list):
        _fail("BASIS_GROUPS_SHAPE")
    normalized: list[list[dict[str, str]]] = []
    sets: list[set[tuple[str, str]]] = []
    seen_sets: set[frozenset[tuple[str, str]]] = set()
    for group in groups:
        if not isinstance(group, list) or not group:
            _fail("BASIS_GROUP_SHAPE")
        refs: list[tuple[str, str]] = []
        seen_in_group: set[tuple[str, str]] = set()
        for member in group:
            ref = _pair(member, "BASIS_MEMBER")
            if ref in seen_in_group:
                _fail("DUPLICATE_BASIS_MEMBER")
            if ref not in participants:
                _fail("UNKNOWN_BASIS_PARTICIPANT")
            if participants[ref][1] != "causal":
                _fail("RESIDUAL_IN_BASIS")
            seen_in_group.add(ref)
            refs.append(ref)
        group_set = frozenset(refs)
        if group_set in seen_sets:
            _fail("DUPLICATE_EQUIVALENT_BASIS_GROUP")
        seen_sets.add(group_set)
        refs.sort()
        normalized.append([{"source_id": source, "passage_id": passage} for source, passage in refs])
        sets.append(set(refs))

    for left in sets:
        for right in sets:
            if left > right:
                _fail("NONMINIMAL_BASIS_GROUP")
    causal = {ref for ref, (_, role) in participants.items() if role == "causal"}
    covered = set().union(*sets) if sets else set()
    if covered != causal:
        _fail("BASIS_COVERAGE")
    order = {tuple((member["source_id"], member["passage_id"]) for member in group): group for group in normalized}
    normalized.sort(key=lambda group: tuple((member["source_id"], member["passage_id"]) for member in group))
    del order
    return normalized, sets


def _validate_terminal(
    record: dict[str, Any],
    participant_map: dict[tuple[str, str], tuple[str, str]],
    groups: list[list[dict[str, str]]],
) -> tuple[str, str]:
    execution = _require_exact_keys(record["execution"], {"state", "completion"}, "PROPOSITION_EXECUTION")
    state = execution["state"]
    completion = execution["completion"]
    if state not in {"completed", "failed", "incomplete"}:
        _fail("PROPOSITION_EXECUTION_STATE")
    terminal = record["terminal"]
    if state in {"failed", "incomplete"}:
        if completion is not None or terminal is not None or record["participants"] or record["basis_groups"]:
            _fail("EXECUTION_TERMINAL_INCOHERENCE")
        return "", ""
    if completion not in {"assessed", "not_checkable"}:
        _fail("PROPOSITION_COMPLETION")
    terminal_obj = _require_exact_keys(
        terminal,
        {"verdict", "reason"},
        "TERMINAL_SHAPE",
    )
    verdict = terminal_obj["verdict"]
    reason = terminal_obj["reason"]
    if verdict not in {"supported", "contradicted", "not_checkable"}:
        _fail("TERMINAL_VERDICT")
    reasons = {
        "categorical_support",
        "categorical_refutation",
        "MIXED_RELATIONS",
        "unresolved_categorical_relation",
        "joint_public_cause",
        "no_deciding_relation",
        "UNSUPPORTED_SEMANTIC_FAMILY",
    }
    if reason not in reasons:
        _fail("TERMINAL_REASON")
    if completion == "assessed" and verdict not in {"supported", "contradicted"}:
        _fail("COMPLETION_VERDICT_INCOHERENCE")
    if completion == "not_checkable" and verdict != "not_checkable":
        _fail("COMPLETION_VERDICT_INCOHERENCE")
    expected_reason = {
        "supported": "categorical_support",
        "contradicted": "categorical_refutation",
    }
    if verdict in expected_reason and reason != expected_reason[verdict]:
        _fail("VERDICT_REASON_INCOHERENCE")
    if verdict == "not_checkable" and reason not in reasons - {"categorical_support", "categorical_refutation"}:
        _fail("VERDICT_REASON_INCOHERENCE")

    if verdict in {"supported", "contradicted"}:
        if not groups:
            _fail("CAUSAL_BASIS_REQUIRED")
        required_relation = verdict == "supported" and "supports" or "refutes"
        for group in groups:
            if any(
                participant_map[(member["source_id"], member["passage_id"])][0] != required_relation
                for member in group
            ):
                _fail("TERMINAL_RELATION_INCOHERENCE")
    elif reason == "MIXED_RELATIONS":
        if not groups:
            _fail("CAUSAL_BASIS_REQUIRED")
        for group in groups:
            relations = {
                participant_map[(member["source_id"], member["passage_id"])][0] for member in group
            }
            if "supports" not in relations or "refutes" not in relations or "non_polarized" in relations:
                _fail("TERMINAL_RELATION_INCOHERENCE")
    elif reason in {"unresolved_categorical_relation", "joint_public_cause"}:
        if not groups:
            _fail("CAUSAL_BASIS_REQUIRED")
        for group in groups:
            if any(
                participant_map[(member["source_id"], member["passage_id"])][0] != "non_polarized"
                for member in group
            ):
                _fail("TERMINAL_RELATION_INCOHERENCE")
    else:
        if groups:
            _fail("TERMINAL_RELATION_INCOHERENCE")
        if any(relation != "non_polarized" or role != "residual" for relation, role in participant_map.values()):
            _fail("TERMINAL_RELATION_INCOHERENCE")
    return verdict, reason


def _normalize_inner(value: dict[str, Any], *, include_result_set_id: bool) -> dict[str, Any]:
    result = copy.deepcopy(value)
    if not include_result_set_id:
        result.pop("result_set_id", None)
    propositions = []
    for proposition in result["propositions"]:
        item = copy.deepcopy(proposition)
        item["participants"] = sorted(
            item["participants"],
            key=lambda participant: (
                participant["evidence_ref"]["source_id"],
                participant["evidence_ref"]["passage_id"],
            ),
        )
        item["basis_groups"] = [
            sorted(group, key=lambda member: (member["source_id"], member["passage_id"]))
            for group in item["basis_groups"]
        ]
        item["basis_groups"].sort(
            key=lambda group: tuple((member["source_id"], member["passage_id"]) for member in group)
        )
        propositions.append(item)
    propositions.sort(
        key=lambda item: (
            item["proposition"]["proposition_id"],
            item["proposition"]["content_sha256"],
        )
    )
    result["propositions"] = propositions
    return result


def _normalize_outer(value: dict[str, Any], *, include_result_set_id: bool) -> dict[str, Any]:
    result = copy.deepcopy(value)
    if not include_result_set_id:
        result.pop("result_set_id", None)
    result["rc2_result"] = _normalize_inner(result["rc2_result"], include_result_set_id=True)
    result["recomposition"]["ordered_children"] = sorted(
        result["recomposition"]["ordered_children"],
        key=lambda child: child["sequence"],
    )
    return result


def _validate_inner(
    value: Any,
    *,
    contract_b_binding: dict[str, str],
    contract_b_propositions: dict[str, str],
    contract_b_passages: set[tuple[str, str]],
    authority: dict[str, str],
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    inner = _require_exact_keys(
        value,
        {"profile", "result_set_id", "contract_b", "producer", "execution", "propositions"},
        "INNER_SHAPE",
    )
    if inner["profile"] != INNER_PROFILE or inner["profile"] != authority["inner_profile"]:
        _fail("INNER_PROFILE")
    result_set_id = _tagged_hex(inner["result_set_id"], "INNER_RESULT_SET_ID")
    contract_b = _require_exact_keys(
        inner["contract_b"],
        {"contract_version", "bundle_id", "bundle_hash"},
        "INNER_CONTRACT_B",
    )
    actual_contract_b = {
        "contract_version": _nonempty_string(contract_b["contract_version"], "INNER_CONTRACT_B"),
        "bundle_id": _nonempty_string(contract_b["bundle_id"], "INNER_CONTRACT_B"),
        "bundle_hash": _tagged_hex(contract_b["bundle_hash"], "INNER_CONTRACT_B"),
    }
    if actual_contract_b != contract_b_binding:
        _fail("CONTRACT_B_BINDING_MISMATCH")
    producer = _require_exact_keys(
        inner["producer"],
        {"semantic_implementation_sha", "policy_sha256", "policy_resolver_commit_sha"},
        "INNER_PRODUCER",
    )
    actual_producer = {
        "semantic_implementation_sha": _hex40(
            producer["semantic_implementation_sha"], "INNER_PRODUCER"
        ),
        "policy_sha256": _hex64(producer["policy_sha256"], "INNER_PRODUCER"),
        "policy_resolver_commit_sha": _hex40(
            producer["policy_resolver_commit_sha"], "INNER_PRODUCER"
        ),
    }
    expected_producer = {
        key: authority[key]
        for key in ("semantic_implementation_sha", "policy_sha256", "policy_resolver_commit_sha")
    }
    if actual_producer != expected_producer:
        _fail("PRODUCER_AUTHORITY_MISMATCH")
    execution = _require_exact_keys(inner["execution"], {"state"}, "INNER_EXECUTION")
    execution_state = execution["state"]
    if execution_state not in {"completed", "failed", "incomplete"}:
        _fail("INNER_EXECUTION_STATE")
    propositions = inner["propositions"]
    if not isinstance(propositions, list):
        _fail("INNER_PROPOSITIONS")
    if execution_state in {"failed", "incomplete"} and propositions:
        _fail("INNER_EXECUTION_TERMINAL_INCOHERENCE")

    records: dict[str, dict[str, Any]] = {}
    for raw_record in propositions:
        record = _require_exact_keys(
            raw_record,
            {"proposition", "execution", "terminal", "participants", "basis_groups"},
            "PROPOSITION_RESULT_SHAPE",
        )
        proposition = _require_exact_keys(
            record["proposition"],
            {"proposition_id", "content_sha256"},
            "PROPOSITION_BINDING",
        )
        proposition_id = _nonempty_string(proposition["proposition_id"], "PROPOSITION_BINDING")
        content_sha256 = _tagged_hex(proposition["content_sha256"], "PROPOSITION_BINDING")
        if proposition_id in records:
            _fail("DUPLICATE_PROPOSITION")
        if proposition_id not in contract_b_propositions:
            _fail("PROPOSITION_NOT_IN_CONTRACT_B")
        if content_sha256 != "sha256:" + contract_b_propositions[proposition_id]:
            _fail("PROPOSITION_CONTENT_MISMATCH")
        participant_map, normalized_participants = _participant_map(record, contract_b_passages)
        normalized_groups, _ = _basis_groups(record, participant_map)
        verdict, reason = _validate_terminal(record, participant_map, normalized_groups)
        if record["execution"]["state"] in {"failed", "incomplete"}:
            if verdict or reason:
                _fail("EXECUTION_TERMINAL_INCOHERENCE")
        elif verdict not in {"supported", "contradicted", "not_checkable"}:
            _fail("TERMINAL_VERDICT")
        normalized = copy.deepcopy(record)
        normalized["proposition"] = {
            "proposition_id": proposition_id,
            "content_sha256": content_sha256,
        }
        normalized["participants"] = normalized_participants
        normalized["basis_groups"] = normalized_groups
        records[proposition_id] = {
            "record": normalized,
            "verdict": verdict,
            "reason": reason,
        }

    normalized_inner = _normalize_inner(inner, include_result_set_id=True)
    local_material = _canonical_json(_normalize_inner(inner, include_result_set_id=False), trailing_lf=True)
    if result_set_id != _tagged_digest(local_material):
        _fail("INNER_RESULT_SET_ID_MISMATCH")
    if _canonical_json(normalized_inner, trailing_lf=True) != _canonical_json(inner, trailing_lf=True):
        _fail("INNER_NONCANONICAL")
    return normalized_inner, records


def _native_result(raw: bytes, *, child_id: str) -> dict[str, Any]:
    native = _parse_json(raw, code_prefix="NATIVE_RESULT")
    proposition = _require_keys(native.get("proposition"), {"proposition_id", "text_sha256", "proposition_sha256"}, "NATIVE_PROPOSITION")
    result = _require_keys(native.get("result"), {"conclusion"}, "NATIVE_RESULT_FIELD")
    native_id = _nonempty_string(proposition["proposition_id"], "NATIVE_PROPOSITION")
    if native_id != child_id:
        _fail("NATIVE_PROPOSITION_ID_MISMATCH")
    text_sha256 = _tagged_hex(proposition["text_sha256"], "NATIVE_TEXT_HASH")
    proposition_sha256 = _hex64(proposition["proposition_sha256"], "NATIVE_PROPOSITION_HASH")
    conclusion = result["conclusion"]
    if conclusion not in {"supported", "contradicted", "not_checkable"}:
        _fail("NATIVE_CONCLUSION")
    return {
        "text_sha256": text_sha256,
        "proposition_sha256": proposition_sha256,
        "conclusion": conclusion,
    }


def consume_parent_bound_contract_c(
    raw: bytes,
    *,
    contract_b_index: dict,
    expected_authority: dict,
    contract_a_decomposition: dict,
    native_child_results: dict[str, bytes],
) -> dict:
    """Validate and consume one exact outer Contract C parent-bound handoff."""

    authority = _read_authority(expected_authority)
    contract_b_binding = _contract_b_binding(contract_b_index)
    contract_b_propositions = _contract_b_propositions(contract_b_index)
    contract_b_passages = _contract_b_passages(contract_b_index)
    decomposition = _decomposition(contract_a_decomposition)
    outer = _parse_json(raw, code_prefix="OUTER")
    outer = _require_exact_keys(
        outer,
        {"profile", "result_set_id", "rc2_result", "recomposition"},
        "OUTER_SHAPE",
    )
    if outer["profile"] != OUTER_PROFILE or outer["profile"] != authority["profile"]:
        _fail("OUTER_PROFILE")
    outer_result_set_id = _tagged_hex(outer["result_set_id"], "OUTER_RESULT_SET_ID")
    recomposition = _require_exact_keys(
        outer["recomposition"],
        {
            "cal_freeze_commit",
            "cal_semantic_source_commit",
            "root",
            "decomposition_id",
            "operator",
            "ordered_children",
            "decomposition_receipt_id",
            "parent_conclusion",
        },
        "RECOMPOSITION_SHAPE",
    )
    if _hex40(recomposition["cal_freeze_commit"], "CAL_FREEZE_COMMIT") != authority["cal_freeze_commit"]:
        _fail("CAL_FREEZE_COMMIT_MISMATCH")
    if _hex40(recomposition["cal_semantic_source_commit"], "CAL_SOURCE_COMMIT") != authority[
        "cal_semantic_source_commit"
    ]:
        _fail("CAL_SOURCE_COMMIT_MISMATCH")
    root = _require_exact_keys(recomposition["root"], {"proposition_id", "text_sha256"}, "ROOT_SHAPE")
    root_binding = {
        "proposition_id": _nonempty_string(root["proposition_id"], "ROOT_BINDING"),
        "text_sha256": _tagged_hex(root["text_sha256"], "ROOT_BINDING"),
    }
    if root_binding != decomposition["root"]:
        _fail("ROOT_BINDING_MISMATCH")
    if _nonempty_string(recomposition["decomposition_id"], "DECOMPOSITION_ID", nonblank=True) != decomposition[
        "decomposition_id"
    ]:
        _fail("DECOMPOSITION_ID_MISMATCH")
    if recomposition["operator"] != "all_of" or recomposition["operator"] != decomposition["operator"]:
        _fail("DECOMPOSITION_OPERATOR_MISMATCH")

    inner, inner_records = _validate_inner(
        outer["rc2_result"],
        contract_b_binding=contract_b_binding,
        contract_b_propositions=contract_b_propositions,
        contract_b_passages=contract_b_passages,
        authority=authority,
    )
    children = recomposition["ordered_children"]
    if not isinstance(children, list):
        _fail("ORDERED_CHILDREN_SHAPE")
    if not isinstance(native_child_results, dict):
        _fail("NATIVE_CHILD_RESULTS_SHAPE")
    inner_ids = set(inner_records)
    if len(children) != len(inner_ids) or {child.get("proposition_id") for child in children if isinstance(child, dict)} != inner_ids:
        _fail("CHILD_SET_MISMATCH")
    if set(native_child_results) != inner_ids:
        _fail("NATIVE_CHILD_SET_MISMATCH")

    child_by_sequence: dict[int, dict[str, Any]] = {}
    child_ids: set[str] = set()
    verified_children: list[dict[str, Any]] = []
    for raw_child in children:
        child = _require_exact_keys(
            raw_child,
            {
                "sequence",
                "proposition_id",
                "text_sha256",
                "contract_c_content_sha256",
                "native_result_sha256",
                "cal_result_id",
                "conclusion",
            },
            "ORDERED_CHILD",
        )
        sequence = _sequence(child["sequence"], "CHILD_SEQUENCE")
        proposition_id = _nonempty_string(child["proposition_id"], "CHILD_PROPOSITION_ID")
        if sequence in child_by_sequence or proposition_id in child_ids:
            _fail("DUPLICATE_CHILD")
        child_by_sequence[sequence] = child
        child_ids.add(proposition_id)

    expected_sequences = set(range(1, len(decomposition["children"]) + 1))
    if set(child_by_sequence) != expected_sequences:
        _fail("CHILD_SEQUENCE_MISMATCH")

    seen_result_ids: set[str] = set()
    conclusions: list[str] = []
    for expected_child in decomposition["children"]:
        sequence = expected_child["sequence"]
        child = child_by_sequence[sequence]
        proposition_id = expected_child["proposition_id"]
        if child["proposition_id"] != proposition_id:
            _fail("CHILD_PROPOSITION_BINDING_MISMATCH")
        text_sha256 = _tagged_hex(child["text_sha256"], "CHILD_TEXT_HASH")
        if text_sha256 != expected_child["text_sha256"]:
            _fail("CHILD_TEXT_BINDING_MISMATCH")
        record_info = inner_records.get(proposition_id)
        if record_info is None:
            _fail("CHILD_NOT_IN_INNER_RESULT")
        inner_record = record_info["record"]
        content_sha256 = inner_record["proposition"]["content_sha256"]
        if _tagged_hex(child["contract_c_content_sha256"], "CHILD_CONTENT_HASH") != content_sha256:
            _fail("CHILD_CONTENT_BINDING_MISMATCH")
        native_bytes = native_child_results[proposition_id]
        if not isinstance(native_bytes, (bytes, bytearray)):
            _fail("NATIVE_RESULT_BYTES")
        native_bytes = bytes(native_bytes)
        native_digest = _tagged_digest(native_bytes)
        if _tagged_hex(child["native_result_sha256"], "CHILD_NATIVE_HASH") != native_digest:
            _fail("NATIVE_RESULT_HASH_MISMATCH")
        native = _native_result(native_bytes, child_id=proposition_id)
        if "sha256:" + native["proposition_sha256"] != content_sha256:
            _fail("NATIVE_CONTENT_BINDING_MISMATCH")
        if native["text_sha256"] != text_sha256:
            _fail("NATIVE_TEXT_BINDING_MISMATCH")
        conclusion = child["conclusion"]
        if conclusion not in {"supported", "contradicted", "not_checkable"}:
            _fail("CHILD_CONCLUSION")
        if conclusion != native["conclusion"] or conclusion != record_info["verdict"]:
            _fail("CHILD_CONCLUSION_MISMATCH")
        cal_result_id = child["cal_result_id"]
        if not isinstance(cal_result_id, str) or not _CAL_RESULT_ID.fullmatch(cal_result_id):
            _fail("CHILD_RESULT_ID_SHAPE")
        identity = {
            "proposition_id": proposition_id,
            "text_sha256": text_sha256,
            "audit_result_sha256": native_digest,
            "conclusion": conclusion,
        }
        derived_result_id = "cal-child-result:" + _sha256(_canonical_json(identity, trailing_lf=False))
        if cal_result_id != derived_result_id:
            _fail("CHILD_RESULT_ID_MISMATCH")
        if cal_result_id in seen_result_ids:
            _fail("DUPLICATE_CHILD_RESULT_ID")
        seen_result_ids.add(cal_result_id)
        conclusions.append(conclusion)
        verified_children.append(
            {
                "proposition_id": proposition_id,
                "text_sha256": text_sha256,
                "result_id": cal_result_id,
                "conclusion": conclusion,
            }
        )

    if any(conclusion == "contradicted" for conclusion in conclusions):
        parent_conclusion = "contradicted"
    elif conclusions and all(conclusion == "supported" for conclusion in conclusions):
        parent_conclusion = "supported"
    else:
        parent_conclusion = "not_checkable"
    if recomposition["parent_conclusion"] != parent_conclusion:
        _fail("PARENT_CONCLUSION_MISMATCH")

    receipt = {
        "root_proposition_id": root_binding["proposition_id"],
        "root_text_sha256": root_binding["text_sha256"],
        "decomposition_state": "declared",
        "decomposition_id": decomposition["decomposition_id"],
        "operator": "all_of",
        "ordered_children": verified_children,
        "root_result_id": None,
        "parent_conclusion": parent_conclusion,
    }
    receipt_id = _hex64(recomposition["decomposition_receipt_id"], "DECOMPOSITION_RECEIPT_ID")
    if receipt_id != _sha256(_canonical_json(receipt, trailing_lf=False)):
        _fail("DECOMPOSITION_RECEIPT_MISMATCH")

    normalized_outer = _normalize_outer(
        {
            "profile": outer["profile"],
            "result_set_id": outer["result_set_id"],
            "rc2_result": inner,
            "recomposition": copy.deepcopy(recomposition),
        },
        include_result_set_id=True,
    )
    outer_local_material = _canonical_json(
        _normalize_outer(normalized_outer, include_result_set_id=False),
        trailing_lf=True,
    )
    if outer_result_set_id != _tagged_digest(outer_local_material):
        _fail("OUTER_RESULT_SET_ID_MISMATCH")
    canonical_outer = _canonical_json(normalized_outer, trailing_lf=True)
    if bytes(raw) != canonical_outer:
        _fail("OUTER_NONCANONICAL")
    whole_object_sha256 = _tagged_digest(bytes(raw))
    if whole_object_sha256 != authority["whole_object_sha256"]:
        _fail("WHOLE_OBJECT_AUTHORITY_MISMATCH")

    normalized_outer["whole_object_sha256"] = whole_object_sha256
    return normalized_outer
