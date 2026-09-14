"""Deliberately weaker binding/integrity consumer for evaluator discrimination.

This is NOT a candidate implementation. It models a superficially plausible
consumer that validates external bindings and local hashes but omits several
Contract-C semantic invariants. The post-reveal evaluator must distinguish it
from the independently frozen Consumer B.
"""

import copy
import hashlib
import json

PROFILE = "contract-c-successor-candidate-a-rc2-research"


class WeakConsumerError(Exception):
    pass


def _normalize(obj):
    n = copy.deepcopy(obj)
    props = n.get("propositions")
    if isinstance(props, list):
        for p in props:
            if not isinstance(p, dict):
                continue
            parts = p.get("participants")
            if isinstance(parts, list):
                parts.sort(key=lambda x: (
                    x.get("evidence_ref", {}).get("source_id", "") if isinstance(x, dict) else "",
                    x.get("evidence_ref", {}).get("passage_id", "") if isinstance(x, dict) else "",
                ))
            groups = p.get("basis_groups")
            if isinstance(groups, list):
                for g in groups:
                    if isinstance(g, list):
                        g.sort(key=lambda x: (
                            x.get("source_id", "") if isinstance(x, dict) else "",
                            x.get("passage_id", "") if isinstance(x, dict) else "",
                        ))
                groups.sort(key=lambda g: [
                    (m.get("source_id", ""), m.get("passage_id", ""))
                    for m in g if isinstance(m, dict)
                ] if isinstance(g, list) else [])
        props.sort(key=lambda p: (
            p.get("proposition", {}).get("proposition_id", "") if isinstance(p, dict) else "",
            p.get("proposition", {}).get("content_sha256", "") if isinstance(p, dict) else "",
        ))
    return n


def _canonical_bytes(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"


def consume_contract_c_weak(raw: bytes, contract_b_index: dict, expected_authority: dict) -> dict:
    """Validate bindings/integrity, intentionally omitting semantic invariants."""
    try:
        obj = json.loads(bytes(raw).decode("utf-8"))
    except Exception as exc:
        raise WeakConsumerError("parse") from exc
    if not isinstance(obj, dict):
        raise WeakConsumerError("shape")

    if obj.get("profile") != PROFILE or expected_authority.get("profile") != PROFILE:
        raise WeakConsumerError("profile")

    cb = obj.get("contract_b") or {}
    for key in ("contract_version", "bundle_id", "bundle_hash"):
        if cb.get(key) != contract_b_index.get(key):
            raise WeakConsumerError("contract_b")

    prod = obj.get("producer") or {}
    for key in ("semantic_implementation_sha", "policy_sha256", "policy_resolver_commit_sha"):
        if prod.get(key) != expected_authority.get(key):
            raise WeakConsumerError("producer")

    props = obj.get("propositions")
    if not isinstance(props, list):
        raise WeakConsumerError("propositions")
    known_passages = {
        (entry.get("source_id"), passage_id)
        for passage_id, entry in contract_b_index.get("passages", {}).items()
        if isinstance(entry, dict)
    }
    for p in props:
        if not isinstance(p, dict):
            raise WeakConsumerError("proposition")
        binding = p.get("proposition") or {}
        qid = binding.get("proposition_id")
        digest = contract_b_index.get("propositions", {}).get(qid)
        if digest is None or binding.get("content_sha256") != "sha256:" + digest:
            raise WeakConsumerError("proposition_binding")
        for part in p.get("participants", []):
            er = part.get("evidence_ref", {}) if isinstance(part, dict) else {}
            if (er.get("source_id"), er.get("passage_id")) not in known_passages:
                raise WeakConsumerError("evidence_ref")

    rsid = obj.get("result_set_id")
    local = copy.deepcopy(obj)
    local.pop("result_set_id", None)
    computed = "sha256:" + hashlib.sha256(_canonical_bytes(_normalize(local))).hexdigest()
    if rsid != computed:
        raise WeakConsumerError("result_set_id")

    whole = "sha256:" + hashlib.sha256(bytes(raw)).hexdigest()
    if expected_authority.get("whole_object_sha256") != whole:
        raise WeakConsumerError("whole_object")

    # Deliberately weak: does not require exact owned fields, canonical raw bytes,
    # exact public reason vocabulary, execution/terminal coherence, relation/role
    # coherence, basis minimality, full causal coverage, or policy-field firewall.
    return obj
