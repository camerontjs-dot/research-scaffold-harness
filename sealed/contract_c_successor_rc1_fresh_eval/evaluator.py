"""Sealed evaluator for Contract C successor RC1 fresh reproduction.

Do not expose this file before implementation/test freeze.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

VERSION = "research-contract-c-successor-rc1"


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def hexsha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def shaid(raw: bytes) -> str:
    return "sha256:" + hexsha(raw)


def rid(value: dict[str, Any]) -> str:
    payload = deepcopy(value)
    payload.pop("result_set_id", None)
    return "result-set:" + hexsha(canon(payload))


def cid(label: str) -> str:
    return "contribution:" + hashlib.sha256(label.encode()).hexdigest()


def ph(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def evidence(source: str, passage: str, text: str) -> dict[str, str]:
    return {"source_id": source, "passage_id": passage, "passage_sha256": shaid(text.encode())}


def fixture(kind: str) -> tuple[dict[str, Any], dict[str, Any]]:
    pid = "p1"
    ptext = "Alpha precedes Beta."
    refs = {
        "a": evidence("src-a", "A", "Alpha precedes Beta."),
        "b": evidence("src-b", "B", "Beta timing is unresolved."),
        "c": evidence("src-c", "C", "Counter record."),
    }
    bundle_id = "bundle-clean-room-rc1"
    bundle_hash = shaid(canon({"bundle_id": bundle_id, "refs": refs, "proposition": ptext}))
    index = {
        "contract_version": "1.2.0",
        "bundle_id": bundle_id,
        "bundle_hash": bundle_hash,
        "propositions": {pid: ph(ptext)},
        "passages": {r["passage_id"]: {"source_id": r["source_id"], "passage_sha256": r["passage_sha256"]} for r in refs.values()},
    }
    policy = {"profile": "clean-room-rc1", "mode": "decision-agnostic"}
    base = {
        "contract_c_version": VERSION,
        "input": {"contract_b": {"contract_version": index["contract_version"], "bundle_id": bundle_id, "bundle_hash": bundle_hash}},
        "producer": {"semantic_implementation_sha": "a" * 40, "policy": {"sha256": hexsha(canon(policy)), "canonical": policy}},
        "execution": {"state": "completed"},
        "propositions": [],
    }

    ca, cb, cc = cid("a"), cid("b"), cid("c")
    assessments = {
        "eligibility": {"state": "not_performed"},
        "semantic_validity": {"state": "not_performed"},
        "aperture_completeness": {"state": "not_performed"},
        "temporal_applicability": {"state": "not_performed"},
    }
    prop: dict[str, Any] = {
        "proposition": {"proposition_id": pid, "text_sha256": ph(ptext)},
        "execution": {"state": "completed", "completion": "assessed"},
        "assessments": assessments,
        "contributions": [],
        "measurement": None,
        "conclusion": None,
    }

    if kind == "support_single":
        prop["contributions"] = [{"contribution_id": ca, "channel": "support", "evidence_ref": refs["a"]}]
        prop["measurement"] = {"kind": "m", "value": 0.8, "basis_contribution_ids": [ca]}
        prop["conclusion"] = {"reported_verdict": "supported", "terminal_branch": "supported", "causal_form": "single_necessary", "basis_members": [{"namespace": "contribution", "id": ca}], "residual_contribution_ids": [], "rule_roles": []}
    elif kind == "counter_single":
        prop["contributions"] = [{"contribution_id": cc, "channel": "counterevidence", "evidence_ref": refs["c"]}]
        prop["conclusion"] = {"reported_verdict": "contradicted", "terminal_branch": "counter", "causal_form": "single_necessary", "basis_members": [{"namespace": "contribution", "id": cc}], "residual_contribution_ids": [], "rule_roles": []}
    elif kind == "neutral_independent":
        prop["execution"] = {"state": "completed", "completion": "not_checkable"}
        prop["contributions"] = [
            {"contribution_id": ca, "channel": "non_deciding", "evidence_ref": refs["a"]},
            {"contribution_id": cb, "channel": "non_deciding", "evidence_ref": refs["b"]},
        ]
        prop["conclusion"] = {"reported_verdict": "not_checkable", "terminal_branch": "unresolved", "causal_form": "independent_sufficient_alternatives", "basis_members": [{"namespace": "contribution", "id": ca}, {"namespace": "contribution", "id": cb}], "residual_contribution_ids": [], "rule_roles": []}
    elif kind == "neutral_residual":
        prop["contributions"] = [
            {"contribution_id": ca, "channel": "support", "evidence_ref": refs["a"]},
            {"contribution_id": cb, "channel": "non_deciding", "evidence_ref": refs["b"]},
        ]
        prop["conclusion"] = {"reported_verdict": "supported", "terminal_branch": "supported_with_residual", "causal_form": "single_necessary", "basis_members": [{"namespace": "contribution", "id": ca}], "residual_contribution_ids": [cb], "rule_roles": []}
    elif kind == "mixed_causal":
        prop["contributions"] = [
            {"contribution_id": ca, "channel": "support", "evidence_ref": refs["a"]},
            {"contribution_id": cc, "channel": "counterevidence", "evidence_ref": refs["c"]},
        ]
        prop["conclusion"] = {"reported_verdict": "custom_mixed_state", "terminal_branch": "mixed", "causal_form": "jointly_sufficient", "basis_members": [{"namespace": "contribution", "id": ca}, {"namespace": "contribution", "id": cc}], "residual_contribution_ids": [], "rule_roles": []}
    elif kind == "failed":
        prop["execution"] = {"state": "failed"}
        prop["conclusion"] = None
    elif kind == "rule_basis":
        rule_id = "rule-role:r1"
        prop["conclusion"] = {"reported_verdict": "custom_rule_state", "terminal_branch": "rule", "causal_form": "single_necessary", "basis_members": [{"namespace": "rule", "id": rule_id}], "residual_contribution_ids": [], "rule_roles": [{"rule_id": rule_id, "code": "r1", "terminal_role": "causal"}]}
    else:
        raise ValueError(kind)

    base["propositions"] = [prop]
    base["result_set_id"] = rid(base)
    return base, index


def reid(value: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(value)
    out["result_set_id"] = rid(out)
    return out


def load_candidate(path: Path):
    spec = importlib.util.spec_from_file_location("candidate_contract_c_successor", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load candidate")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def validate(mod, obj: dict[str, Any], index: dict[str, Any] | None = None, raw: bytes | None = None, expected: str | None = None) -> list[str]:
    payload = canon(obj) if raw is None else raw
    return mod.validate_contract_c_bytes(payload, expected_sha256=expected, contract_b_index=index)


def run(candidate_path: Path) -> dict[str, Any]:
    mod = load_candidate(candidate_path)
    checks: dict[str, bool] = {}

    valids: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for name in ["support_single", "counter_single", "neutral_independent", "neutral_residual", "mixed_causal", "failed", "rule_basis"]:
        obj, index = fixture(name)
        valids[name] = (obj, index)
        checks[f"valid_{name}"] = validate(mod, obj, index) == []
        checks[f"canonical_{name}"] = mod.canonical_bytes(obj) == canon(obj)
        checks[f"identity_{name}"] = mod.result_set_identity(obj) == rid(obj)

    # Whole-object digest accepts bare or sha256-prefixed digest and rejects stale binding.
    base, base_index = valids["neutral_independent"]
    raw = canon(base)
    digest = hexsha(raw)
    checks["whole_hash_bare"] = validate(mod, base, base_index, raw=raw, expected=digest) == []
    checks["whole_hash_prefixed"] = validate(mod, base, base_index, raw=raw, expected="sha256:" + digest) == []
    checks["whole_hash_stale_rejected"] = bool(validate(mod, base, base_index, raw=raw, expected="0" * 64))

    # Unicode canonicalization is independent of semantic validation.
    unicode_obj = {"z": "é", "a": "雪", "nested": {"β": 2, "a": 1}}
    checks["unicode_canonical"] = mod.canonical_bytes(unicode_obj) == canon(unicode_obj)

    # Array order changes bytes/result identity but not validity where no ordering semantics are declared.
    ordered, ordered_index = fixture("neutral_independent")
    reversed_obj = deepcopy(ordered)
    reversed_obj["propositions"][0]["contributions"].reverse()
    reversed_obj["propositions"][0]["conclusion"]["basis_members"].reverse()
    reversed_obj = reid(reversed_obj)
    checks["array_reorder_still_valid"] = validate(mod, reversed_obj, ordered_index) == []
    checks["array_reorder_changes_identity"] = reversed_obj["result_set_id"] != ordered["result_set_id"] and canon(reversed_obj) != canon(ordered)

    invalids: dict[str, tuple[dict[str, Any], dict[str, Any] | None]] = {}
    def add(name: str, obj: dict[str, Any], index: dict[str, Any] | None = base_index, do_reid: bool = True) -> None:
        invalids[name] = (reid(obj) if do_reid else obj, index)

    x = deepcopy(base); x["contract_c_version"] = "1.0.0"; add("wrong_version", x)
    x = deepcopy(base); x["propositions"][0]["contributions"][0]["channel"] = "neutral"; add("unknown_channel", x)
    x = deepcopy(base); x["future_field"] = True; add("unknown_top_field", x)
    x = deepcopy(base); x["propositions"][0]["future_field"] = True; add("unknown_nested_field", x)
    x = deepcopy(base); x["propositions"].append(deepcopy(x["propositions"][0])); add("duplicate_proposition_id", x)
    x = deepcopy(base); x["propositions"] = []; add("completed_empty_result", x)
    x = deepcopy(base); x["propositions"][0]["contributions"][1]["contribution_id"] = x["propositions"][0]["contributions"][0]["contribution_id"]; x["propositions"][0]["conclusion"]["basis_members"][1]["id"] = x["propositions"][0]["contributions"][0]["contribution_id"]; add("duplicate_contribution_id", x)
    x = deepcopy(base); x["propositions"][0]["execution"] = {"state":"completed","completion":"not_checkable"}; x["propositions"][0]["conclusion"]["reported_verdict"] = "supported"; add("not_checkable_wrong_verdict", x)
    x, idx = fixture("support_single"); x["propositions"][0]["execution"] = {"state":"completed","completion":"assessed"}; x["propositions"][0]["conclusion"]["reported_verdict"] = "not_checkable"; add("assessed_not_checkable_verdict", x, idx)
    x, idx = fixture("failed"); x["propositions"][0]["conclusion"] = deepcopy(fixture("support_single")[0]["propositions"][0]["conclusion"]); add("failed_with_conclusion", x, idx)
    x, idx = fixture("support_single"); x["propositions"][0]["conclusion"] = None; add("completed_without_conclusion", x, idx)
    x, idx = fixture("support_single"); x["propositions"][0]["measurement"]["basis_contribution_ids"] = [cid("absent")]; add("measurement_unknown_contribution", x, idx)
    x = deepcopy(base); x["propositions"][0]["conclusion"]["basis_members"][0]["id"] = cid("absent"); add("basis_unknown_contribution", x)
    x = deepcopy(base); x["propositions"][0]["conclusion"]["residual_contribution_ids"] = [cid("absent")]; add("residual_unknown_contribution", x)
    x = deepcopy(base); x["propositions"][0]["conclusion"]["residual_contribution_ids"] = [x["propositions"][0]["contributions"][0]["contribution_id"]]; add("causal_residual_overlap", x)
    x = deepcopy(base); x["propositions"][0]["conclusion"]["basis_members"] = [x["propositions"][0]["conclusion"]["basis_members"][0]]; x["propositions"][0]["conclusion"]["causal_form"] = "single_necessary"; add("unclassified_retained_contribution", x)
    x = deepcopy(base); x["propositions"][0]["conclusion"]["causal_form"] = "single_necessary"; add("single_necessary_two_basis", x)
    x = deepcopy(base); x["propositions"][0]["conclusion"]["basis_members"] = [x["propositions"][0]["conclusion"]["basis_members"][0]]; x["propositions"][0]["conclusion"]["residual_contribution_ids"] = [x["propositions"][0]["contributions"][1]["contribution_id"]]; add("independent_one_basis", x)
    x = deepcopy(base); x["propositions"][0]["conclusion"]["causal_form"] = "redundant_non_deciding"; add("redundant_with_basis", x)
    x, idx = fixture("rule_basis"); x["propositions"][0]["conclusion"]["rule_roles"] = []; add("rule_basis_without_role", x, idx)
    x, idx = fixture("rule_basis"); x["propositions"][0]["conclusion"]["rule_roles"][0]["terminal_role"] = "residual"; add("residual_rule_in_basis", x, idx)
    x = deepcopy(base); x["producer"]["policy"]["sha256"] = "0" * 64; add("wrong_policy_hash", x)
    x = deepcopy(base); x["result_set_id"] = "result-set:" + "0" * 64; add("stale_result_set_id", x, do_reid=False)
    x = deepcopy(base); x["propositions"][0]["assessments"]["eligibility"] = {"state":"performed","value":"future"}; add("unknown_assessment_state", x)
    x = deepcopy(base); x["propositions"][0]["conclusion"]["basis_members"][0] = {"namespace":"contribution","id":"state:wrong-prefix"}; add("basis_namespace_prefix_mismatch", x)
    x = deepcopy(base); x["propositions"][0]["conclusion"]["basis_members"].append(deepcopy(x["propositions"][0]["conclusion"]["basis_members"][0])); add("duplicate_basis_member", x)

    for name, (obj, idx) in invalids.items():
        checks[f"reject_{name}"] = bool(validate(mod, obj, idx))

    # Contract-B index hostile variants against otherwise exact valid bytes.
    def bad_index(mutator):
        idx = deepcopy(base_index); mutator(idx); return idx
    checks["reject_b_bundle"] = bool(validate(mod, base, bad_index(lambda i: i.__setitem__("bundle_id", "wrong"))))
    checks["reject_b_proposition_absent"] = bool(validate(mod, base, bad_index(lambda i: i["propositions"].pop("p1"))))
    checks["reject_b_proposition_hash"] = bool(validate(mod, base, bad_index(lambda i: i["propositions"].__setitem__("p1", "0" * 64))))
    checks["reject_b_passage_absent"] = bool(validate(mod, base, bad_index(lambda i: i["passages"].pop("A"))))
    checks["reject_b_evidence_mismatch"] = bool(validate(mod, base, bad_index(lambda i: i["passages"]["A"].__setitem__("source_id", "wrong"))))

    # Non-canonical raw bytes and malformed parser cases.
    pretty = json.dumps(base, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    checks["reject_noncanonical_bytes"] = bool(mod.validate_contract_c_bytes(pretty, contract_b_index=base_index))
    checks["reject_duplicate_json_keys"] = bool(mod.validate_contract_c_bytes(b'{"contract_c_version":"x","contract_c_version":"y"}\n'))
    checks["reject_nonfinite_json"] = bool(mod.validate_contract_c_bytes(b'{"contract_c_version":NaN}\n'))
    checks["reject_non_utf8"] = bool(mod.validate_contract_c_bytes(b"\xff\xfe"))

    passed = all(checks.values())
    failed = sorted(k for k, v in checks.items() if not v)
    return {"passed": passed, "check_count": len(checks), "failed_checks": failed, "checks": checks}


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("candidate", type=Path)
    p.add_argument("--out", type=Path)
    args = p.parse_args(argv)
    result = run(args.candidate)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    print(json.dumps({"passed": result["passed"], "check_count": result["check_count"], "failed_checks": result["failed_checks"]}, sort_keys=True))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
