"""Context-free Contract C Candidate A RC2 consumer (Consumer B).

Implements only the public semantics in
research/contract_c_candidate_a_rc2_consumer_b_aperture/SPEC.md
using the Python standard library.
"""

import copy
import hashlib
import json


PROFILE = "contract-c-successor-candidate-a-rc2-research"

TOP_FIELDS = frozenset({"profile", "result_set_id", "contract_b", "producer", "execution", "propositions"})
CONTRACT_B_FIELDS = frozenset({"contract_version", "bundle_id", "bundle_hash"})
PRODUCER_FIELDS = frozenset({"semantic_implementation_sha", "policy_sha256", "policy_resolver_commit_sha"})
RS_EXEC_FIELDS = frozenset({"state"})
PROP_RECORD_FIELDS = frozenset({"proposition", "execution", "terminal", "participants", "basis_groups"})
PROP_BINDING_FIELDS = frozenset({"proposition_id", "content_sha256"})
PROP_EXEC_FIELDS = frozenset({"state", "completion"})
TERMINAL_FIELDS = frozenset({"verdict", "reason"})
PARTICIPANT_FIELDS = frozenset({"evidence_ref", "relation", "role"})
EVIDENCE_REF_FIELDS = frozenset({"source_id", "passage_id"})

RS_EXEC_STATES = frozenset({"completed", "failed", "incomplete"})
PROP_EXEC_STATES = frozenset({"completed", "failed", "incomplete"})
COMPLETIONS = frozenset({"assessed", "not_checkable"})
VERDICTS = frozenset({"supported", "contradicted", "not_checkable"})
REASONS = frozenset({
    "categorical_support",
    "categorical_refutation",
    "MIXED_RELATIONS",
    "unresolved_categorical_relation",
    "joint_public_cause",
    "no_deciding_relation",
    "UNSUPPORTED_SEMANTIC_FAMILY",
})
RELATIONS = frozenset({"supports", "refutes", "non_polarized"})
ROLES = frozenset({"causal", "residual"})

_HEX_LOWER = frozenset("0123456789abcdef")


class ConsumerError(Exception):
    code: str

    def __init__(self, code: str, message: str = ""):
        super().__init__(message or code)
        self.code = code


def _fail(code: str, message: str = ""):
    raise ConsumerError(code, message or code)


def _is_lower_hex(s, length: int) -> bool:
    if not isinstance(s, str):
        return False
    if len(s) != length:
        return False
    for c in s:
        if c not in _HEX_LOWER:
            return False
    return True


def _is_sha256_prefixed(s) -> bool:
    if not isinstance(s, str):
        return False
    if not s.startswith("sha256:"):
        return False
    return _is_lower_hex(s[len("sha256:"):], 64)


def _check_exact_fields(obj, expected, what: str):
    if not isinstance(obj, dict):
        _fail("INVALID_SHAPE", "%s must be an object" % what)
    keys = set(obj.keys())
    if keys != set(expected):
        extra = keys - set(expected)
        missing = set(expected) - keys
        if extra:
            _fail("UNKNOWN_FIELD", "%s has unknown fields: %s" % (what, sorted(extra)))
        else:
            _fail("MISSING_FIELD", "%s missing fields: %s" % (what, sorted(missing)))


def _no_dup_object(pairs):
    obj = {}
    for k, v in pairs:
        if k in obj:
            _fail("DUPLICATE_KEY", "duplicate object key: %r" % (k,))
        obj[k] = v
    return obj


def _reject_constant(value):
    _fail("NON_FINITE_CONSTANT", "non-finite JSON constant: %s" % (value,))


def _parse_raw(raw: bytes):
    if not isinstance(raw, (bytes, bytearray)):
        _fail("INVALID_RAW_TYPE", "raw must be bytes")
    raw = bytes(raw)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        _fail("INVALID_UTF8", "raw is not UTF-8")
    decoder = json.JSONDecoder(object_pairs_hook=_no_dup_object, parse_constant=_reject_constant)
    try:
        obj, idx = decoder.raw_decode(text)
    except ConsumerError:
        raise
    except Exception as e:
        _fail("INVALID_JSON", "invalid JSON: %s" % (e,))
    remainder = text[idx:]
    if remainder.strip() != "":
        _fail("TRAILING_DATA", "trailing non-whitespace data")
    if not isinstance(obj, dict):
        _fail("INVALID_TOP_LEVEL", "top-level JSON value must be an object")
    return obj


def _normalize(obj):
    """Return a deep-copied normalized object per SPEC section 7."""
    n = copy.deepcopy(obj)
    props = n.get("propositions")
    if isinstance(props, list):
        for p in props:
            if isinstance(p, dict):
                parts = p.get("participants")
                if isinstance(parts, list):
                    parts.sort(key=lambda x: (
                        x.get("evidence_ref", {}).get("source_id", ""),
                        x.get("evidence_ref", {}).get("passage_id", ""),
                    ))
                groups = p.get("basis_groups")
                if isinstance(groups, list):
                    for g in groups:
                        if isinstance(g, list):
                            g.sort(key=lambda x: (x.get("source_id", ""), x.get("passage_id", "")))
                    groups.sort(key=lambda g: [(m.get("source_id", ""), m.get("passage_id", "")) for m in g] if isinstance(g, list) else [])
        props.sort(key=lambda p: (
            p.get("proposition", {}).get("proposition_id", ""),
            p.get("proposition", {}).get("content_sha256", ""),
        ))
    return n


def _canonical_bytes(normalized_obj) -> bytes:
    return json.dumps(
        normalized_obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8") + b"\n"


def _validate_contract_b_index(contract_b_index: dict):
    if not isinstance(contract_b_index, dict):
        _fail("INVALID_CONTRACT_B_INDEX", "contract_b_index must be a dict")
    for k in ("contract_version", "bundle_id", "bundle_hash", "passages", "propositions"):
        if k not in contract_b_index:
            _fail("INVALID_CONTRACT_B_INDEX", "contract_b_index missing %s" % k)
    if not isinstance(contract_b_index["contract_version"], str) or contract_b_index["contract_version"] == "":
        _fail("INVALID_CONTRACT_B_INDEX", "bad contract_version in index")
    if not isinstance(contract_b_index["bundle_id"], str) or contract_b_index["bundle_id"] == "":
        _fail("INVALID_CONTRACT_B_INDEX", "bad bundle_id in index")
    if not _is_sha256_prefixed(contract_b_index["bundle_hash"]):
        _fail("INVALID_CONTRACT_B_INDEX", "bad bundle_hash in index")
    if not isinstance(contract_b_index["passages"], dict):
        _fail("INVALID_CONTRACT_B_INDEX", "bad passages in index")
    for pid, pentry in contract_b_index["passages"].items():
        if not isinstance(pid, str) or pid == "":
            _fail("INVALID_CONTRACT_B_INDEX", "bad passage key in index")
        if not isinstance(pentry, dict):
            _fail("INVALID_CONTRACT_B_INDEX", "bad passage entry in index")
        if set(pentry.keys()) != {"source_id", "passage_sha256"}:
            # Allow no extras/missing; index shape is normative for lookup.
            _fail("INVALID_CONTRACT_B_INDEX", "bad passage entry fields in index")
        if not isinstance(pentry["source_id"], str) or pentry["source_id"] == "":
            _fail("INVALID_CONTRACT_B_INDEX", "bad source_id in index")
        if not _is_sha256_prefixed(pentry["passage_sha256"]):
            _fail("INVALID_CONTRACT_B_INDEX", "bad passage_sha256 in index")
    if not isinstance(contract_b_index["propositions"], dict):
        _fail("INVALID_CONTRACT_B_INDEX", "bad propositions in index")
    for qid, digest in contract_b_index["propositions"].items():
        if not isinstance(qid, str) or qid == "":
            _fail("INVALID_CONTRACT_B_INDEX", "bad proposition key in index")
        if not _is_lower_hex(digest, 64):
            _fail("INVALID_CONTRACT_B_INDEX", "bad proposition digest in index")


def _validate_expected_authority(expected_authority: dict):
    if not isinstance(expected_authority, dict):
        _fail("INVALID_AUTHORITY", "expected_authority must be a dict")
    for k in ("profile", "semantic_implementation_sha", "policy_sha256",
              "policy_resolver_commit_sha", "whole_object_sha256"):
        if k not in expected_authority:
            _fail("INVALID_AUTHORITY", "expected_authority missing %s" % k)
    if expected_authority["profile"] != PROFILE:
        _fail("AUTHORITY_PROFILE_MISMATCH", "expected_authority profile mismatch")
    if not _is_lower_hex(expected_authority["semantic_implementation_sha"], 40):
        _fail("INVALID_AUTHORITY", "bad semantic_implementation_sha in authority")
    if not _is_lower_hex(expected_authority["policy_sha256"], 64):
        _fail("INVALID_AUTHORITY", "bad policy_sha256 in authority")
    if not _is_lower_hex(expected_authority["policy_resolver_commit_sha"], 40):
        _fail("INVALID_AUTHORITY", "bad policy_resolver_commit_sha in authority")
    if not _is_sha256_prefixed(expected_authority["whole_object_sha256"]):
        _fail("INVALID_AUTHORITY", "bad whole_object_sha256 in authority")


def consume_contract_c(raw: bytes, contract_b_index: dict, expected_authority: dict) -> dict:
    # Validate caller-supplied bindings shape first (fail closed on malformed authority/index).
    _validate_contract_b_index(contract_b_index)
    _validate_expected_authority(expected_authority)

    obj = _parse_raw(raw)

    # --- exact top-level shape ---
    _check_exact_fields(obj, TOP_FIELDS, "top-level object")

    # --- profile ---
    if obj["profile"] != PROFILE:
        _fail("INVALID_PROFILE", "wrong profile: %r" % (obj.get("profile"),))
    if expected_authority["profile"] != obj["profile"]:
        _fail("AUTHORITY_PROFILE_MISMATCH", "object profile does not match authority")

    # --- contract_b ---
    cb = obj["contract_b"]
    _check_exact_fields(cb, CONTRACT_B_FIELDS, "contract_b")
    if not isinstance(cb["contract_version"], str) or cb["contract_version"] == "":
        _fail("INVALID_CONTRACT_B", "bad contract_version")
    if not isinstance(cb["bundle_id"], str) or cb["bundle_id"] == "":
        _fail("INVALID_CONTRACT_B", "bad bundle_id")
    if not _is_sha256_prefixed(cb["bundle_hash"]):
        _fail("INVALID_CONTRACT_B", "bad bundle_hash")
    if (cb["contract_version"] != contract_b_index["contract_version"]
            or cb["bundle_id"] != contract_b_index["bundle_id"]
            or cb["bundle_hash"] != contract_b_index["bundle_hash"]):
        _fail("CONTRACT_B_MISMATCH", "contract_b tuple does not equal supplied index")

    # --- producer ---
    prod = obj["producer"]
    _check_exact_fields(prod, PRODUCER_FIELDS, "producer")
    if not _is_lower_hex(prod.get("semantic_implementation_sha"), 40):
        _fail("INVALID_PRODUCER", "bad semantic_implementation_sha")
    if not _is_lower_hex(prod.get("policy_sha256"), 64):
        _fail("INVALID_PRODUCER", "bad policy_sha256")
    if not _is_lower_hex(prod.get("policy_resolver_commit_sha"), 40):
        _fail("INVALID_PRODUCER", "bad policy_resolver_commit_sha")
    if prod["semantic_implementation_sha"] != expected_authority["semantic_implementation_sha"]:
        _fail("PRODUCER_MISMATCH", "semantic_implementation_sha mismatch")
    if prod["policy_sha256"] != expected_authority["policy_sha256"]:
        _fail("PRODUCER_MISMATCH", "policy_sha256 mismatch")
    if prod["policy_resolver_commit_sha"] != expected_authority["policy_resolver_commit_sha"]:
        _fail("RESOLVER_MISMATCH", "policy_resolver_commit_sha mismatch")

    # --- result_set_id format ---
    rsid = obj["result_set_id"]
    if not _is_sha256_prefixed(rsid):
        _fail("INVALID_RESULT_SET_ID", "malformed result_set_id")

    # --- result-set execution ---
    rs_exec = obj["execution"]
    _check_exact_fields(rs_exec, RS_EXEC_FIELDS, "execution")
    if rs_exec["state"] not in RS_EXEC_STATES:
        _fail("INVALID_EXECUTION_STATE", "bad result-set execution state")

    # --- propositions container ---
    props = obj["propositions"]
    if not isinstance(props, list):
        _fail("INVALID_PROPOSITIONS", "propositions must be an array")
    if rs_exec["state"] in ("failed", "incomplete") and len(props) != 0:
        _fail("RESULT_SET_EXECUTION_MISMATCH", "failed/incomplete result-set must have zero propositions")

    # Build passage lookup: (source_id, passage_id) -> True
    index_pairs = set()
    for pid, pentry in contract_b_index["passages"].items():
        index_pairs.add((pentry["source_id"], pid))

    seen_prop_ids = set()
    for p in props:
        if not isinstance(p, dict):
            _fail("INVALID_PROPOSITION_RECORD", "proposition record must be an object")
        _check_exact_fields(p, PROP_RECORD_FIELDS, "proposition record")

        # proposition binding
        pb = p["proposition"]
        _check_exact_fields(pb, PROP_BINDING_FIELDS, "proposition binding")
        qid = pb.get("proposition_id")
        csha = pb.get("content_sha256")
        if not isinstance(qid, str) or qid == "":
            _fail("INVALID_PROPOSITION_BINDING", "bad proposition_id")
        if not _is_sha256_prefixed(csha):
            _fail("INVALID_PROPOSITION_BINDING", "bad content_sha256")
        if qid in seen_prop_ids:
            _fail("DUPLICATE_PROPOSITION_ID", "duplicate proposition_id: %s" % qid)
        seen_prop_ids.add(qid)
        if qid not in contract_b_index["propositions"]:
            _fail("UNKNOWN_PROPOSITION", "proposition_id not in Contract-B index: %s" % qid)
        expected_csha = "sha256:" + contract_b_index["propositions"][qid]
        if csha != expected_csha:
            _fail("PROPOSITION_DIGEST_MISMATCH", "content_sha256 mismatch for %s" % qid)

        # proposition execution
        pe = p["execution"]
        _check_exact_fields(pe, PROP_EXEC_FIELDS, "proposition execution")
        pstate = pe.get("state")
        comp = pe.get("completion")
        if pstate not in PROP_EXEC_STATES:
            _fail("INVALID_PROPOSITION_EXECUTION", "bad proposition execution state")
        if comp is not None and comp not in COMPLETIONS:
            _fail("INVALID_PROPOSITION_EXECUTION", "bad proposition completion")
        if pstate == "completed":
            if comp not in ("assessed", "not_checkable"):
                _fail("EXECUTION_COMPLETION_MISMATCH", "completed requires assessed/not_checkable")
        else:
            if comp is not None:
                _fail("EXECUTION_TERMINAL_LAUNDERING", "failed/incomplete requires completion null")
            if p["terminal"] is not None:
                _fail("EXECUTION_TERMINAL_LAUNDERING", "failed/incomplete requires terminal null")
            if p["participants"] != []:
                _fail("EXECUTION_TERMINAL_LAUNDERING", "failed/incomplete requires no participants")
            if p["basis_groups"] != []:
                _fail("EXECUTION_TERMINAL_LAUNDERING", "failed/incomplete requires no basis groups")
            continue  # no further per-proposition checks for non-completed

        # terminal (completed only)
        term = p["terminal"]
        if not isinstance(term, dict):
            _fail("INVALID_TERMINAL", "completed proposition requires terminal object")
        _check_exact_fields(term, TERMINAL_FIELDS, "terminal")
        verdict = term.get("verdict")
        reason = term.get("reason")
        if verdict not in VERDICTS:
            _fail("INVALID_VERDICT", "bad verdict: %r" % (verdict,))
        if reason not in REASONS:
            _fail("INVALID_REASON", "bad reason: %r" % (reason,))
        # completion/verdict coherence
        if comp == "assessed":
            if verdict not in ("supported", "contradicted"):
                _fail("COMPLETION_VERDICT_INCOHERENCE", "assessed permits only supported/contradicted")
        elif comp == "not_checkable":
            if verdict != "not_checkable":
                _fail("COMPLETION_VERDICT_INCOHERENCE", "not_checkable requires verdict not_checkable")
        # verdict/reason coherence
        if verdict == "supported":
            if reason != "categorical_support":
                _fail("VERDICT_REASON_INCOHERENCE", "supported requires categorical_support")
        elif verdict == "contradicted":
            if reason != "categorical_refutation":
                _fail("VERDICT_REASON_INCOHERENCE", "contradicted requires categorical_refutation")
        elif verdict == "not_checkable":
            if reason not in ("MIXED_RELATIONS", "unresolved_categorical_relation",
                              "joint_public_cause", "no_deciding_relation",
                              "UNSUPPORTED_SEMANTIC_FAMILY"):
                _fail("VERDICT_REASON_INCOHERENCE", "bad reason for not_checkable")

        # participants
        parts = p["participants"]
        if not isinstance(parts, list):
            _fail("INVALID_PARTICIPANTS", "participants must be an array")
        seen_refs = set()
        ref_to_info = {}
        for part in parts:
            if not isinstance(part, dict):
                _fail("INVALID_PARTICIPANT", "participant must be an object")
            _check_exact_fields(part, PARTICIPANT_FIELDS, "participant")
            er = part["evidence_ref"]
            if not isinstance(er, dict):
                _fail("INVALID_EVIDENCE_REF", "evidence_ref must be an object")
            _check_exact_fields(er, EVIDENCE_REF_FIELDS, "evidence_ref")
            sid = er.get("source_id")
            pid2 = er.get("passage_id")
            if not isinstance(sid, str) or sid == "":
                _fail("INVALID_EVIDENCE_REF", "bad source_id")
            if not isinstance(pid2, str) or pid2 == "":
                _fail("INVALID_EVIDENCE_REF", "bad passage_id")
            key = (sid, pid2)
            if key in seen_refs:
                _fail("DUPLICATE_PARTICIPANT", "duplicate participant: %s" % (key,))
            seen_refs.add(key)
            if key not in index_pairs:
                _fail("UNKNOWN_EVIDENCE_REFERENCE", "evidence reference absent from Contract-B index: %s" % (key,))
            rel = part.get("relation")
            role = part.get("role")
            if rel not in RELATIONS:
                _fail("INVALID_RELATION", "bad relation: %r" % (rel,))
            if role not in ROLES:
                _fail("INVALID_ROLE", "bad role: %r" % (role,))
            ref_to_info[key] = {"relation": rel, "role": role}

        # basis_groups
        groups = p["basis_groups"]
        if not isinstance(groups, list):
            _fail("INVALID_BASIS_GROUPS", "basis_groups must be an array")
        group_sets = []
        for g in groups:
            if not isinstance(g, list):
                _fail("INVALID_BASIS_GROUP", "basis group must be an array")
            if len(g) == 0:
                _fail("EMPTY_BASIS_GROUP", "basis group must be non-empty")
            members = []
            seen_members = set()
            for m in g:
                if not isinstance(m, dict):
                    _fail("INVALID_BASIS_MEMBER", "basis member must be an object")
                _check_exact_fields(m, EVIDENCE_REF_FIELDS, "basis member")
                sid = m.get("source_id")
                pid2 = m.get("passage_id")
                if not isinstance(sid, str) or sid == "":
                    _fail("INVALID_BASIS_MEMBER", "bad source_id in basis")
                if not isinstance(pid2, str) or pid2 == "":
                    _fail("INVALID_BASIS_MEMBER", "bad passage_id in basis")
                key = (sid, pid2)
                if key in seen_members:
                    _fail("DUPLICATE_BASIS_MEMBER", "duplicate basis member: %s" % (key,))
                seen_members.add(key)
                if key not in ref_to_info:
                    _fail("UNKNOWN_BASIS_PARTICIPANT", "basis member not a retained participant: %s" % (key,))
                if ref_to_info[key]["role"] != "causal":
                    _fail("RESIDUAL_IN_BASIS", "residual participant in basis: %s" % (key,))
                members.append(key)
            group_sets.append(frozenset(members))

        # duplicate equivalent groups (same member set, order-insensitive)
        if len(set(group_sets)) != len(group_sets):
            _fail("DUPLICATE_BASIS_GROUP", "duplicate equivalent basis group")

        # strict superset (non-minimal)
        for i in range(len(group_sets)):
            for j in range(len(group_sets)):
                if i == j:
                    continue
                if group_sets[i] > group_sets[j]:
                    _fail("NON_MINIMAL_BASIS_GROUP", "basis group is strict superset of another")

        # union coverage: must equal exactly causal set
        causal_set = frozenset(k for k, v in ref_to_info.items() if v["role"] == "causal")
        union = frozenset().union(*group_sets) if group_sets else frozenset()
        if union != causal_set:
            _fail("BASIS_COVERAGE_MISMATCH", "basis family union must equal causal set")

        # terminal causal coherence
        if verdict == "supported":
            if len(group_sets) < 1:
                _fail("TERMINAL_CAUSAL_INCOHERENCE", "supported requires at least one basis group")
            for gs in group_sets:
                for k in gs:
                    if ref_to_info[k]["relation"] != "supports":
                        _fail("TERMINAL_CAUSAL_INCOHERENCE", "supported groups must contain supports only")
        elif verdict == "contradicted":
            if len(group_sets) < 1:
                _fail("TERMINAL_CAUSAL_INCOHERENCE", "contradicted requires at least one basis group")
            for gs in group_sets:
                for k in gs:
                    if ref_to_info[k]["relation"] != "refutes":
                        _fail("TERMINAL_CAUSAL_INCOHERENCE", "contradicted groups must contain refutes only")
        elif reason == "MIXED_RELATIONS":
            if len(group_sets) < 1:
                _fail("TERMINAL_CAUSAL_INCOHERENCE", "MIXED_RELATIONS requires at least one basis group")
            for gs in group_sets:
                rels = set(ref_to_info[k]["relation"] for k in gs)
                if "supports" not in rels or "refutes" not in rels:
                    _fail("TERMINAL_CAUSAL_INCOHERENCE", "mixed group must contain supports and refutes")
                if "non_polarized" in rels:
                    _fail("TERMINAL_CAUSAL_INCOHERENCE", "mixed group must not contain non_polarized")
        elif reason in ("unresolved_categorical_relation", "joint_public_cause"):
            if len(group_sets) < 1:
                _fail("TERMINAL_CAUSAL_INCOHERENCE", "%s requires at least one basis group" % reason)
            for gs in group_sets:
                for k in gs:
                    if ref_to_info[k]["relation"] != "non_polarized":
                        _fail("TERMINAL_CAUSAL_INCOHERENCE", "%s groups must be non_polarized only" % reason)
        elif reason in ("no_deciding_relation", "UNSUPPORTED_SEMANTIC_FAMILY"):
            if len(group_sets) != 0:
                _fail("TERMINAL_CAUSAL_INCOHERENCE", "%s requires empty basis_groups" % reason)
            for k, v in ref_to_info.items():
                if v["relation"] != "non_polarized" or v["role"] != "residual":
                    _fail("TERMINAL_CAUSAL_INCOHERENCE", "%s requires all non_polarized/residual" % reason)
        else:
            _fail("INVALID_REASON", "unhandled reason: %s" % reason)

    # --- canonical JSON and local identity ---
    local_obj = {k: v for k, v in obj.items() if k != "result_set_id"}
    normalized_local = _normalize(local_obj)
    local_canonical = _canonical_bytes(normalized_local)
    computed_rsid = "sha256:" + hashlib.sha256(local_canonical).hexdigest()
    if rsid != computed_rsid:
        _fail("INVALID_RESULT_SET_ID", "result_set_id mismatch")

    normalized_full = _normalize(obj)
    full_canonical = _canonical_bytes(normalized_full)
    if full_canonical != raw:
        _fail("NON_CANONICAL_BYTES", "raw bytes are not canonical")

    # --- independent whole-object authority ---
    computed_whole = "sha256:" + hashlib.sha256(raw).hexdigest()
    if expected_authority["whole_object_sha256"] != computed_whole:
        _fail("WHOLE_OBJECT_MISMATCH", "whole-object digest mismatch")

    # --- successful normalized result (deterministic, no invented fields) ---
    result = json.loads(json.dumps(
        normalized_full, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ))
    return result
