"""Post-reveal evaluator for the independently frozen Contract C Consumer B.

This evaluator is intentionally created only after candidate freeze. It tests
public-spec conformance and evaluator discrimination; it does not promote or
version Contract C.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import pathlib
import re
import subprocess
import sys
from typing import Any, Callable

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from candidate.consumer import ConsumerError, consume_contract_c  # noqa: E402
from post_reveal.weak_control import WeakConsumerError, consume_contract_c_weak  # noqa: E402

APERTURE = ROOT / "research" / "contract_c_candidate_a_rc2_consumer_b_aperture"
CANDIDATE = ROOT / "candidate"

EXPECTED_BLOBS = {
    "consumer.py": "1f0e64d22f11d7dbe620fef209852870e6b5203d",
    "test_consumer.py": "54e03ff388974fb3524b164c17b7af9f7cf9870c",
    "FREEZE_RECEIPT.json": "1f57979b23eb37d8611acfb58b288e4952eaa717",
}
EXPECTED_APERTURE_START = "07258b47477f8df4151b0ba531809e76a7c5641b"
EXPECTED_CANDIDATE_COMMIT = "99619c2582a5e632c29a622b878537d10f758698"
EXPECTED_FREEZE_COMMIT = "ba09743b28e57bc87dd1f315046ef79b93f24021"
PROFILE = "contract-c-successor-candidate-a-rc2-research"


def load_json(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_raw(path: pathlib.Path) -> bytes:
    return path.read_bytes()


def git_blob_sha1(data: bytes) -> str:
    header = b"blob " + str(len(data)).encode("ascii") + b"\x00"
    return hashlib.sha1(header + data).hexdigest()


def normalize(obj: Any) -> Any:
    n = copy.deepcopy(obj)
    props = n.get("propositions") if isinstance(n, dict) else None
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


def canonical_bytes(obj: dict) -> bytes:
    return json.dumps(
        obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8") + b"\n"


def reseal(obj: dict) -> bytes:
    work = copy.deepcopy(obj)
    work.pop("result_set_id", None)
    local = canonical_bytes(normalize(work))
    work["result_set_id"] = "sha256:" + hashlib.sha256(local).hexdigest()
    return canonical_bytes(normalize(work))


def raw_sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def ref_key(ref: dict) -> tuple[str, str]:
    return (ref["source_id"], ref["passage_id"])


def ref_copy(ref: dict) -> dict:
    return {"source_id": ref["source_id"], "passage_id": ref["passage_id"]}


def load_world():
    auth = load_json(APERTURE / "AUTHORITIES.json")
    indexes = load_json(APERTURE / "CONTRACT_B_INDEXES.json")
    raws = {}
    objs = {}
    for key, meta in auth["handoffs"].items():
        raw = load_raw(APERTURE / meta["file"])
        raws[key] = raw
        objs[key] = json.loads(raw.decode("utf-8"))
    return auth, indexes, raws, objs


def authority_for(auth: dict, key: str, whole_override: str | None = None) -> dict:
    common = auth["common"]
    return {
        "profile": common["profile"],
        "semantic_implementation_sha": common["semantic_implementation_sha"],
        "policy_sha256": common["policy_sha256"],
        "policy_resolver_commit_sha": common["policy_resolver_commit_sha"],
        "whole_object_sha256": whole_override or auth["handoffs"][key]["whole_object_sha256"],
    }


def index_for(auth: dict, indexes: dict, key: str) -> dict:
    return copy.deepcopy(indexes[auth["handoffs"][key]["contract_b_index"]])


def call_target(raw: bytes, idx: dict, authority: dict) -> dict:
    try:
        value = consume_contract_c(raw, idx, authority)
        return {"status": "accepted", "value": value}
    except ConsumerError as exc:
        return {"status": "rejected", "error": exc.code}
    except Exception as exc:  # a crash is not valid fail-closed behavior
        return {"status": "crash", "error": f"{type(exc).__name__}: {exc}"}


def call_weak(raw: bytes, idx: dict, authority: dict) -> dict:
    try:
        value = consume_contract_c_weak(raw, idx, authority)
        return {"status": "accepted", "value": value}
    except WeakConsumerError as exc:
        return {"status": "rejected", "error": str(exc)}
    except Exception as exc:
        return {"status": "crash", "error": f"{type(exc).__name__}: {exc}"}


def verify_subject_identity() -> dict:
    observed = {}
    checks = {}
    for name, expected in EXPECTED_BLOBS.items():
        data = (CANDIDATE / name).read_bytes()
        blob = git_blob_sha1(data)
        observed[name] = blob
        checks[name] = blob == expected

    receipt = load_json(CANDIDATE / "FREEZE_RECEIPT.json")
    receipt_checks = {
        "aperture_start": receipt.get("aperture_starting_commit") == EXPECTED_APERTURE_START,
        "candidate_commit": receipt.get("candidate_commit") == EXPECTED_CANDIDATE_COMMIT,
        "frozen_candidate_commit": receipt.get("frozen_candidate_commit") == EXPECTED_CANDIDATE_COMMIT,
        "consumer_blob": receipt.get("consumer_blob_id") == EXPECTED_BLOBS["consumer.py"],
        "test_blob": receipt.get("test_blob_id") == EXPECTED_BLOBS["test_consumer.py"],
        "contamination_clean": receipt.get("contamination_state") == "clean",
        "forbidden_inputs_empty": receipt.get("forbidden_inputs_read") == [],
        "terminal_ready": receipt.get("terminal_prereveal_state") == "FROZEN_CANDIDATE_READY_FOR_REVEAL",
    }
    return {
        "expected_blobs": EXPECTED_BLOBS,
        "observed_blobs": observed,
        "blob_checks": checks,
        "receipt_checks": receipt_checks,
        "all_ok": all(checks.values()) and all(receipt_checks.values()),
    }


def run_prereveal_suite() -> dict:
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "candidate.test_consumer", "-v"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    text = proc.stdout
    match = re.search(r"Ran\s+(\d+)\s+tests?", text)
    return {
        "returncode": proc.returncode,
        "tests_executed": int(match.group(1)) if match else None,
        "passed": proc.returncode == 0,
        "output_tail": text[-4000:],
    }


def make_attack(raw: bytes, obj: dict, mutate: Callable[[dict], None], *, reseal_whole: bool,
                authority: dict) -> tuple[bytes, dict]:
    mut = copy.deepcopy(obj)
    mutate(mut)
    raw2 = reseal(mut)
    auth2 = copy.deepcopy(authority)
    if reseal_whole:
        auth2["whole_object_sha256"] = raw_sha256(raw2)
    return raw2, auth2


def build_attacks(auth: dict, indexes: dict, raws: dict, objs: dict) -> list[dict]:
    attacks = []

    def add(name: str, key: str, raw: bytes, idx: dict, authority: dict, note: str):
        attacks.append({"name": name, "key": key, "raw": raw, "idx": idx, "authority": authority, "note": note})

    # 1. Delete an authoritative alternative and its unique participant. The
    # remaining object is structurally plausible, so unchanged external authority
    # must prevent artificial unique-winner selection.
    key = "alternative_joint_mixed"
    base = objs[key]
    original_auth = authority_for(auth, key)
    mut = copy.deepcopy(base)
    groups = mut["propositions"][0]["basis_groups"]
    kept = groups[0]
    kept_refs = {ref_key(x) for x in kept}
    mut["propositions"][0]["basis_groups"] = [copy.deepcopy(kept)]
    mut["propositions"][0]["participants"] = [
        p for p in mut["propositions"][0]["participants"]
        if ref_key(p["evidence_ref"]) in kept_refs
    ]
    raw2 = reseal(mut)
    add("delete_alternative_basis_original_authority", key, raw2, index_for(auth, indexes, key), original_auth,
        "coherent winner-selection mutation must fail against frozen external authority")

    # 2. Flatten all alternative-joint members into one pseudo-joint basis.
    mut = copy.deepcopy(base)
    union = {}
    for g in mut["propositions"][0]["basis_groups"]:
        for ref in g:
            union[ref_key(ref)] = ref_copy(ref)
    mut["propositions"][0]["basis_groups"] = [list(union.values())]
    raw2 = reseal(mut)
    add("flatten_alternative_joint_original_authority", key, raw2, index_for(auth, indexes, key), original_auth,
        "flattened semantic family is different exact object and must fail frozen external authority")

    # 3. Independent supports: pick one winner and delete the other alternative.
    key = "independent_supports"
    base = objs[key]
    original_auth = authority_for(auth, key)
    mut = copy.deepcopy(base)
    kept = copy.deepcopy(mut["propositions"][0]["basis_groups"][0])
    kept_refs = {ref_key(x) for x in kept}
    mut["propositions"][0]["basis_groups"] = [kept]
    mut["propositions"][0]["participants"] = [
        p for p in mut["propositions"][0]["participants"] if ref_key(p["evidence_ref"]) in kept_refs
    ]
    raw2 = reseal(mut)
    add("unique_winner_independent_supports_original_authority", key, raw2, index_for(auth, indexes, key), original_auth,
        "arbitrary winner deletion must not survive exact-object authority")

    # 4. non_polarized laundering under no_deciding, with new whole-object hash
    # supplied only to isolate the consumer's structural semantic checks.
    key = "no_deciding"
    base = objs[key]
    authority = authority_for(auth, key)
    raw2, auth2 = make_attack(raws[key], base,
        lambda x: x["propositions"][0]["participants"][0].__setitem__("relation", "supports"),
        reseal_whole=True, authority=authority)
    add("non_polarized_to_supports_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "resealed structural mutation must fail no_deciding terminal coherence")

    # 5. Exact unsupported/no-deciding alias with original authority.
    key = "unsupported_family"
    base = objs[key]
    mut = copy.deepcopy(base)
    mut["propositions"][0]["terminal"]["reason"] = "no_deciding_relation"
    raw2 = reseal(mut)
    add("unsupported_alias_to_no_deciding_original_authority", key, raw2, index_for(auth, indexes, key), authority_for(auth, key),
        "structurally similar public reasons remain distinct exact object state")

    # 6-7. Case-fold/substitute public reasons with resealed hash to isolate enum checks.
    key = "alternative_joint_mixed"
    raw2, auth2 = make_attack(raws[key], objs[key],
        lambda x: x["propositions"][0]["terminal"].__setitem__("reason", "mixed_relations"),
        reseal_whole=True, authority=authority_for(auth, key))
    add("casefold_mixed_relations_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "public reason identity is exact and case-sensitive")

    key = "unsupported_family"
    raw2, auth2 = make_attack(raws[key], objs[key],
        lambda x: x["propositions"][0]["terminal"].__setitem__("reason", "unsupported_semantic_family"),
        reseal_whole=True, authority=authority_for(auth, key))
    add("casefold_unsupported_family_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "public reason identity is exact and case-sensitive")

    # 8. stale local result_set_id, while whole-object authority matches attacked raw.
    key = "independent_supports"
    mut = copy.deepcopy(objs[key])
    old = mut["result_set_id"]
    mut["result_set_id"] = old[:-1] + ("0" if old[-1] != "0" else "1")
    raw2 = canonical_bytes(normalize(mut))
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("stale_local_result_set_id", key, raw2, index_for(auth, indexes, key), auth2,
        "local identity must be recomputed from canonical unsealed bytes")

    # 9. coherent local reseal but stale external authority.
    key = "no_deciding"
    mut = copy.deepcopy(objs[key])
    mut["propositions"][0]["terminal"]["reason"] = "UNSUPPORTED_SEMANTIC_FAMILY"
    raw2 = reseal(mut)
    add("coherent_local_reseal_stale_external_authority", key, raw2, index_for(auth, indexes, key), authority_for(auth, key),
        "local self-consistency cannot replace external exact-object authority")

    # 10. wrong Contract-B tuple supplied independently.
    key = "independent_supports"
    idx = index_for(auth, indexes, key)
    idx["bundle_id"] = idx["bundle_id"] + "-wrong"
    add("wrong_contract_b_tuple", key, raws[key], idx, authority_for(auth, key),
        "object Contract-B tuple must match independently supplied index")

    # 11. proposition substitution, resealed object and whole hash but unchanged B index.
    key = "independent_supports"
    raw2, auth2 = make_attack(raws[key], objs[key],
        lambda x: x["propositions"][0]["proposition"].__setitem__("content_sha256", "sha256:" + "f" * 64),
        reseal_whole=True, authority=authority_for(auth, key))
    add("proposition_substitution", key, raw2, index_for(auth, indexes, key), auth2,
        "proposition digest remains bound to exact Contract-B proposition index")

    # 12. absent evidence ref, mirrored into basis to avoid a trivial dangling-basis-only failure.
    key = "independent_supports"
    mut = copy.deepcopy(objs[key])
    p = mut["propositions"][0]
    old_ref = copy.deepcopy(p["participants"][0]["evidence_ref"])
    ghost = {"source_id": "src-postreveal-ghost", "passage_id": "POSTREVEAL-GHOST"}
    p["participants"][0]["evidence_ref"] = copy.deepcopy(ghost)
    for g in p["basis_groups"]:
        for member in g:
            if ref_key(member) == ref_key(old_ref):
                member.clear(); member.update(copy.deepcopy(ghost))
    raw2 = reseal(mut)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("evidence_ref_absent_from_contract_b", key, raw2, index_for(auth, indexes, key), auth2,
        "retained evidence refs must exist in exact Contract-B index")

    # 13-15. wrong producer / policy / resolver authority inputs.
    key = "independent_supports"
    for field, value, name in (
        ("semantic_implementation_sha", "0" * 40, "wrong_semantic_implementation_authority"),
        ("policy_sha256", "0" * 64, "wrong_policy_authority"),
        ("policy_resolver_commit_sha", "0" * 40, "wrong_resolver_authority"),
    ):
        bad = authority_for(auth, key)
        bad[field] = value
        add(name, key, raws[key], index_for(auth, indexes, key), bad,
            "embedded producer identity cannot self-select external authority")

    # 16. residual participant left inside basis, fully resealed.
    key = "independent_supports"
    raw2, auth2 = make_attack(raws[key], objs[key],
        lambda x: x["propositions"][0]["participants"][0].__setitem__("role", "residual"),
        reseal_whole=True, authority=authority_for(auth, key))
    add("residual_participant_in_basis_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "basis members must be causal")

    # 17. causal participant omitted from basis-family coverage, resealed.
    key = "independent_supports"
    mut = copy.deepcopy(objs[key])
    mut["propositions"][0]["basis_groups"] = mut["propositions"][0]["basis_groups"][:1]
    raw2 = reseal(mut)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("causal_participant_uncovered_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "basis-family union must equal exact causal set")

    # 18. add strict-superset basis beside two singleton sufficient alternatives.
    key = "independent_supports"
    mut = copy.deepcopy(objs[key])
    union = []
    seen = set()
    for g in mut["propositions"][0]["basis_groups"]:
        for member in g:
            if ref_key(member) not in seen:
                seen.add(ref_key(member)); union.append(ref_copy(member))
    mut["propositions"][0]["basis_groups"].append(union)
    raw2 = reseal(mut)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("nonminimal_strict_superset_basis_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "represented basis family may not contain strict-superset group")

    # 19. duplicate equivalent basis group.
    key = "independent_supports"
    mut = copy.deepcopy(objs[key])
    mut["propositions"][0]["basis_groups"].append(copy.deepcopy(mut["propositions"][0]["basis_groups"][0]))
    raw2 = reseal(mut)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("duplicate_equivalent_basis_group_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "equivalent duplicate bases are invalid semantic representation")

    # 20. duplicate basis member.
    key = "alternative_joint_mixed"
    mut = copy.deepcopy(objs[key])
    mut["propositions"][0]["basis_groups"][0].append(copy.deepcopy(mut["propositions"][0]["basis_groups"][0][0]))
    raw2 = reseal(mut)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("duplicate_basis_member_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "one represented basis cannot repeat a member")

    # 21. unknown basis participant that is not a retained participant.
    key = "alternative_joint_mixed"
    mut = copy.deepcopy(objs[key])
    mut["propositions"][0]["basis_groups"][0][0] = {"source_id": "src-ghost-basis", "passage_id": "GHOST-BASIS"}
    raw2 = reseal(mut)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("unknown_basis_participant_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "basis refs must resolve to retained causal participants")

    # 22. duplicate exact participant.
    key = "independent_supports"
    mut = copy.deepcopy(objs[key])
    mut["propositions"][0]["participants"].append(copy.deepcopy(mut["propositions"][0]["participants"][0]))
    raw2 = reseal(mut)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("duplicate_participant_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "duplicate exact participant is invalid")

    # 23. destination-policy / Authorization injection with coherent reseal.
    key = "independent_supports"
    mut = copy.deepcopy(objs[key])
    mut["authorization"] = {"decision": "CLEAR", "actor": "post-reveal-injection"}
    raw2 = reseal(mut)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("authorization_injection_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "Contract-C-owned unknown policy/Authorization fields must fail closed")

    # 24. valid semantic object encoded in noncanonical array order. Local identity
    # still matches after normalization; external digest is updated to attacked raw.
    key = "independent_supports"
    mut = copy.deepcopy(objs[key])
    mut["propositions"][0]["participants"] = list(reversed(mut["propositions"][0]["participants"]))
    mut["propositions"][0]["basis_groups"] = list(reversed(mut["propositions"][0]["basis_groups"]))
    raw2 = json.dumps(mut, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("noncanonical_array_permutation", key, raw2, index_for(auth, indexes, key), auth2,
        "raw bytes are normative canonical bytes; consumer must not silently repair order")

    # 25. failed proposition carrying terminal semantic state.
    key = "independent_supports"
    mut = copy.deepcopy(objs[key])
    mut["propositions"][0]["execution"] = {"state": "failed", "completion": None}
    raw2 = reseal(mut)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("failed_execution_terminal_laundering_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "failed/incomplete proposition cannot carry terminal/participants/bases")

    # 26. MIXED_RELATIONS with one causal member relabeled non_polarized.
    key = "alternative_joint_mixed"
    mut = copy.deepcopy(objs[key])
    mut["propositions"][0]["participants"][0]["relation"] = "non_polarized"
    raw2 = reseal(mut)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("mixed_relation_nonpolarized_laundering_resealed", key, raw2, index_for(auth, indexes, key), auth2,
        "mixed bases may contain supports/refutes only")

    # 27. duplicate JSON key raw attack. json.loads-based weak consumers often
    # silently accept last-wins semantics; exact parser must reject duplicates.
    key = "independent_supports"
    needle = (f'"profile":"{PROFILE}"').encode("utf-8")
    if raws[key].count(needle) != 1:
        raise RuntimeError("unexpected fixture profile encoding")
    raw2 = raws[key].replace(needle, needle + b"," + needle, 1)
    auth2 = authority_for(auth, key, raw_sha256(raw2))
    add("duplicate_json_key_raw", key, raw2, index_for(auth, indexes, key), auth2,
        "duplicate object keys must fail closed rather than last-wins parse")

    return attacks


def evaluate(output_path: pathlib.Path | None = None) -> dict:
    auth, indexes, raws, objs = load_world()
    subject = verify_subject_identity()
    prereveal = run_prereveal_suite()

    positives = {}
    positive_ok = True
    for key in ("independent_supports", "alternative_joint_mixed", "no_deciding", "unsupported_family"):
        idx = index_for(auth, indexes, key)
        expected_auth = authority_for(auth, key)
        result = call_target(raws[key], idx, expected_auth)
        expected_obj = json.loads(raws[key].decode("utf-8"))
        exact_preservation = result.get("status") == "accepted" and result.get("value") == expected_obj
        if result.get("status") == "accepted":
            p = result["value"]["propositions"][0]
            terminal = p["terminal"]
            basis_count = len(p["basis_groups"])
            basis_sizes = sorted(len(g) for g in p["basis_groups"])
        else:
            terminal = None; basis_count = None; basis_sizes = None
        positives[key] = {
            "status": result.get("status"),
            "error": result.get("error"),
            "exact_object_preserved": exact_preservation,
            "terminal": terminal,
            "basis_count": basis_count,
            "basis_sizes": basis_sizes,
        }
        positive_ok = positive_ok and exact_preservation

    attacks = build_attacks(auth, indexes, raws, objs)
    target_attack_results = {}
    weak_attack_results = {}
    target_all_reject = True
    weak_escape_count = 0
    weak_escape_names = []

    for attack in attacks:
        target = call_target(attack["raw"], copy.deepcopy(attack["idx"]), copy.deepcopy(attack["authority"]))
        weak = call_weak(attack["raw"], copy.deepcopy(attack["idx"]), copy.deepcopy(attack["authority"]))
        target_rejected = target["status"] == "rejected"
        weak_accepted = weak["status"] == "accepted"
        target_all_reject = target_all_reject and target_rejected
        if weak_accepted:
            weak_escape_count += 1
            weak_escape_names.append(attack["name"])
        target_attack_results[attack["name"]] = {
            "status": target["status"],
            "error": target.get("error"),
            "passed": target_rejected,
            "note": attack["note"],
        }
        weak_attack_results[attack["name"]] = {
            "status": weak["status"],
            "error": weak.get("error"),
            "accepted_attack": weak_accepted,
        }

    # The weak control must demonstrably escape multiple semantic/canonical
    # attacks; otherwise the evaluator has not shown useful discrimination.
    required_weak_escapes = {
        "non_polarized_to_supports_resealed",
        "casefold_mixed_relations_resealed",
        "casefold_unsupported_family_resealed",
        "residual_participant_in_basis_resealed",
        "causal_participant_uncovered_resealed",
        "nonminimal_strict_superset_basis_resealed",
        "duplicate_equivalent_basis_group_resealed",
        "authorization_injection_resealed",
        "noncanonical_array_permutation",
        "failed_execution_terminal_laundering_resealed",
        "duplicate_json_key_raw",
    }
    observed_required_escapes = sorted(required_weak_escapes.intersection(weak_escape_names))
    weak_killed = len(observed_required_escapes) >= 8

    evaluator_valid = subject["all_ok"] and prereveal["passed"] and weak_killed
    if not subject["all_ok"] or not prereveal["passed"] or not weak_killed:
        disposition = "INCONCLUSIVE_EVALUATOR_INVALID"
    elif not positive_ok or not target_all_reject:
        disposition = "FALSIFIED"
    else:
        disposition = "SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE"

    result = {
        "profile": "contract-c-candidate-a-rc2-consumer-b-post-reveal-evaluator-v1",
        "disposition": disposition,
        "production_promotion_authorized": False,
        "official_contract_c_version_assigned": False,
        "subject": subject,
        "prereveal_regression": prereveal,
        "authoritative_positives": positives,
        "attacks_total": len(attacks),
        "target_all_attacks_rejected_via_consumer_error": target_all_reject,
        "target_attack_results": target_attack_results,
        "weak_control": {
            "description": "binding/integrity consumer omitting semantic basis/reason/canonical/firewall invariants",
            "attacks_accepted": weak_escape_count,
            "accepted_attack_names": sorted(weak_escape_names),
            "required_escape_hits": observed_required_escapes,
            "killed_by_evaluator": weak_killed,
        },
        "weak_attack_results": weak_attack_results,
        "evaluator_valid": evaluator_valid,
        "process_deviation": {
            "accidental_main_placeholder_commit": "dfe5ce90364398c16ec28fd047b2dc8849525884",
            "immediate_revert_commit": "3ed53b13de18e16aa17e71a602218481bad4fc5e",
            "candidate_contamination_effect": "none observed; deviation occurred after frozen candidate and contained no evaluator semantics",
        },
        "boundary": "Research consumer conformance only; no Contract C production version, promotion, Decision policy, Contract E/Authorization, or execution authority.",
    }

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args()
    result = evaluate(args.output)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["disposition"] == "SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
