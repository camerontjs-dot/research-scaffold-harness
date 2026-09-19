from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
APPARATUS_ROOT = Path(os.environ["APPARATUS_ROOT"]).resolve()
CAL_ROOT = Path(os.environ["CAL_ROOT"]).resolve()
EB_ROOT = Path(os.environ["EB_ROOT"]).resolve()
C2_ROOT = Path(os.environ["C2_ROOT"]).resolve()
RESOLVER_JSON = Path(os.environ["RESOLVER_JSON"]).resolve()

sys.path.insert(0, str(ROOT))
from candidate.consumer import ConsumerError, consume_parent_bound_contract_c  # noqa: E402

PRODUCER_EVALUATOR = (
    APPARATUS_ROOT
    / "research"
    / "contract_c_cal_v1_parent_recomposition_rc0_20260919"
    / "evaluate.py"
)


def _load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


producer = _load_module(PRODUCER_EVALUATOR, "frozen_parent_binding_producer")
integration = producer._load_integration_module()


def _canonical_no_lf(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _tagged(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _child_result_id(child: dict[str, Any]) -> str:
    material = {
        "proposition_id": child["proposition_id"],
        "text_sha256": child["text_sha256"],
        "audit_result_sha256": child["native_result_sha256"],
        "conclusion": child["conclusion"],
    }
    return "cal-child-result:" + hashlib.sha256(_canonical_no_lf(material)).hexdigest()


def _receipt_id(recomposition: dict[str, Any]) -> str:
    material = {
        "root_proposition_id": recomposition["root"]["proposition_id"],
        "root_text_sha256": recomposition["root"]["text_sha256"],
        "decomposition_state": "declared",
        "decomposition_id": recomposition["decomposition_id"],
        "operator": recomposition["operator"],
        "ordered_children": [
            {
                "proposition_id": child["proposition_id"],
                "text_sha256": child["text_sha256"],
                "result_id": child["cal_result_id"],
                "conclusion": child["conclusion"],
            }
            for child in sorted(
                recomposition["ordered_children"], key=lambda item: item["sequence"]
            )
        ],
        "root_result_id": None,
        "parent_conclusion": recomposition["parent_conclusion"],
    }
    return hashlib.sha256(_canonical_no_lf(material)).hexdigest()


def _contract_b_index(result: dict[str, Any], outer: dict[str, Any]) -> dict[str, Any]:
    inner = outer["rc2_result"]
    propositions = {
        row["proposition"]["proposition_id"]: {
            "content_sha256": row["proposition"]["content_sha256"]
        }
        for row in inner["propositions"]
    }
    passages: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in result["package"]["candidates"]:
        key = (str(row["source_id"]), str(row["passage_id"]))
        if key in seen:
            continue
        seen.add(key)
        passages.append({"source_id": key[0], "passage_id": key[1]})
    return {
        **inner["contract_b"],
        "propositions": propositions,
        "passages": passages,
    }


def _decomposition_input(contract_a: dict[str, Any]) -> dict[str, Any]:
    root = contract_a["root_proposition"]
    decomposition = contract_a["decomposition"]
    return {
        "state": decomposition["state"],
        "decomposition_id": decomposition["decomposition_id"],
        "operator": decomposition["operator"],
        "root": {
            "proposition_id": root["proposition_id"],
            "text_sha256": root["text_sha256"],
        },
        "children": [
            {
                "sequence": row["sequence"],
                "proposition_id": row["proposition_id"],
                "text_sha256": row["text_sha256"],
            }
            for row in decomposition["children"]
        ],
    }


def _authority(whole_object_sha256: str) -> dict[str, str]:
    return {
        "profile": producer.rc2.PROFILE,
        "inner_profile": producer.rc2.PROFILE,
        "cal_freeze_commit": producer.candidate.CAL_FREEZE_COMMIT,
        "cal_semantic_source_commit": producer.candidate.CAL_SEMANTIC_SOURCE_COMMIT,
        "semantic_implementation_sha": producer.candidate.CAL_SEMANTIC_IMPLEMENTATION,
        "policy_sha256": producer.candidate.POLICY_SHA256,
        "policy_resolver_commit_sha": producer.candidate.POLICY_RESOLVER_COMMIT,
        "whole_object_sha256": whole_object_sha256,
    }


def _native_results(result: dict[str, Any]) -> dict[str, bytes]:
    return {
        str(result["c1"].proposition_id): result["c1_bytes"],
        str(result["c2"].proposition_id): result["c2_bytes"],
    }


def _raw_outer(outer: dict[str, Any]) -> bytes:
    return producer.candidate.canonical_bytes(outer, rc2_validator=producer.rc2)


def _invoke(
    *,
    raw: bytes,
    index: dict[str, Any],
    authority: dict[str, str],
    decomposition: dict[str, Any],
    natives: dict[str, bytes],
) -> dict[str, Any]:
    return consume_parent_bound_contract_c(
        raw,
        contract_b_index=index,
        expected_authority=authority,
        contract_a_decomposition=decomposition,
        native_child_results=natives,
    )


def _expect_reject(
    *,
    raw: bytes,
    index: dict[str, Any],
    authority: dict[str, str],
    decomposition: dict[str, Any],
    natives: dict[str, bytes],
) -> tuple[bool, str | None]:
    try:
        _invoke(
            raw=raw,
            index=index,
            authority=authority,
            decomposition=decomposition,
            natives=natives,
        )
    except ConsumerError as exc:
        return True, exc.code
    except Exception as exc:
        return True, f"{type(exc).__name__}:{exc}"
    return False, None


def _seal_outer(value: dict[str, Any]) -> bytes:
    unsealed = copy.deepcopy(value)
    unsealed.pop("result_set_id", None)
    sealed = producer.candidate.seal(unsealed)
    return (
        json.dumps(
            sealed,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _reseal_inner_and_outer(value: dict[str, Any]) -> bytes:
    working = copy.deepcopy(value)
    inner = working["rc2_result"]
    inner.pop("result_set_id", None)
    working["rc2_result"] = producer.rc2.seal(inner)
    return _seal_outer(working)


def _real_mutations(
    case_id: str,
    case: dict[str, Any],
    all_cases: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    outer = case["outer"]
    index = case["index"]
    authority = case["authority"]
    decomposition = case["decomposition"]
    natives = case["natives"]
    tests: dict[str, dict[str, Any]] = {}

    def add(name: str, *, raw: bytes | None = None, auth: dict[str, str] | None = None,
            native_map: dict[str, bytes] | None = None, idx: dict[str, Any] | None = None,
            decomp: dict[str, Any] | None = None) -> None:
        ok, code = _expect_reject(
            raw=case["raw"] if raw is None else raw,
            index=index if idx is None else idx,
            authority=authority if auth is None else auth,
            decomposition=decomposition if decomp is None else decomp,
            natives=natives if native_map is None else native_map,
        )
        tests[name] = {"rejected": ok, "error_code": code}

    changed = copy.deepcopy(outer)
    changed["recomposition"]["ordered_children"][0]["cal_result_id"] = (
        "cal-child-result:" + "0" * 64
    )
    add("wrong_child_result_id", raw=_seal_outer(changed))

    changed = copy.deepcopy(outer)
    changed["recomposition"]["ordered_children"][0]["native_result_sha256"] = (
        "sha256:" + "1" * 64
    )
    add("changed_native_result_hash", raw=_seal_outer(changed))

    changed = copy.deepcopy(outer)
    changed["recomposition"]["ordered_children"] = changed["recomposition"][
        "ordered_children"
    ][:-1]
    add("omitted_child", raw=_seal_outer(changed))

    changed = copy.deepcopy(outer)
    first, second = changed["recomposition"]["ordered_children"][:2]
    first["sequence"], second["sequence"] = second["sequence"], first["sequence"]
    add("semantic_sequence_change", raw=_seal_outer(changed))

    changed = copy.deepcopy(outer)
    changed["recomposition"]["root"]["text_sha256"] = "sha256:" + "2" * 64
    add("wrong_root", raw=_seal_outer(changed))

    changed = copy.deepcopy(outer)
    changed["recomposition"]["decomposition_receipt_id"] = "3" * 64
    add("stale_decomposition_receipt", raw=_seal_outer(changed))

    changed = copy.deepcopy(outer)
    current_parent = changed["recomposition"]["parent_conclusion"]
    changed["recomposition"]["parent_conclusion"] = (
        "contradicted" if current_parent != "contradicted" else "supported"
    )
    add("parent_conclusion_mutation", raw=_seal_outer(changed))

    changed = copy.deepcopy(outer)
    changed["recomposition"]["ordered_children"][0]["cal_result_id"] = "state:private-codec"
    raw = (
        json.dumps(changed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")
    add("opaque_private_codec_result_id", raw=raw)

    changed = copy.deepcopy(outer)
    changed["rc2_result"]["propositions"][0]["proposition"]["content_sha256"] = (
        "sha256:" + "4" * 64
    )
    add("inner_rc2_child_content_substitution", raw=_reseal_inner_and_outer(changed))

    child_id = str(case["result"]["c1"].proposition_id)
    coherent_natives = copy.deepcopy(natives)
    coherent_natives[child_id] = coherent_natives[child_id] + b" "
    changed = copy.deepcopy(outer)
    child = next(
        row
        for row in changed["recomposition"]["ordered_children"]
        if row["proposition_id"] == child_id
    )
    child["native_result_sha256"] = _tagged(coherent_natives[child_id])
    child["cal_result_id"] = _child_result_id(child)
    changed["recomposition"]["decomposition_receipt_id"] = _receipt_id(
        changed["recomposition"]
    )
    add(
        "coherent_reseal_against_fixed_authority",
        raw=_seal_outer(changed),
        native_map=coherent_natives,
    )

    bad_authority = copy.deepcopy(authority)
    bad_authority["whole_object_sha256"] = "sha256:" + "9" * 64
    add("external_whole_object_mismatch", auth=bad_authority)

    changed = copy.deepcopy(outer)
    changed["recomposition"]["destination_policy"] = "CLEAR"
    raw = (
        json.dumps(changed, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")
    add("destination_policy_injection", raw=raw)

    if case_id == "PIPE01":
        source = all_cases["PIPE03"]
        source_child_id = str(source["result"]["c1"].proposition_id)
        replay_natives = copy.deepcopy(natives)
        replay_natives[child_id] = source["natives"][source_child_id]
        changed = copy.deepcopy(outer)
        source_child = next(
            row
            for row in source["outer"]["recomposition"]["ordered_children"]
            if row["proposition_id"] == source_child_id
        )
        target_child = next(
            row
            for row in changed["recomposition"]["ordered_children"]
            if row["proposition_id"] == child_id
        )
        target_child["native_result_sha256"] = source_child["native_result_sha256"]
        target_child["cal_result_id"] = source_child["cal_result_id"]
        changed["recomposition"]["decomposition_receipt_id"] = _receipt_id(
            changed["recomposition"]
        )
        add(
            "cross_run_same_proposition_same_conclusion_replay",
            raw=_seal_outer(changed),
            native_map=replay_natives,
        )

    return tests


def main() -> None:
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    resolver = json.loads(RESOLVER_JSON.read_text(encoding="utf-8"))

    cases: dict[str, dict[str, Any]] = {}
    positive: dict[str, dict[str, Any]] = {}
    positive_failures: list[str] = []

    for case_spec in integration.CASES:
        result = integration._execute_case(case_spec, output.parent / "cal-runs")
        outer, _ = producer._build_case(result, resolver)
        raw = _raw_outer(outer)
        whole = producer.candidate.whole_object_sha256(
            outer, rc2_validator=producer.rc2
        )
        index = _contract_b_index(result, outer)
        decomposition = _decomposition_input(result["contract_a"])
        natives = _native_results(result)
        authority = _authority(whole)
        cases[case_spec.case_id] = {
            "result": result,
            "outer": outer,
            "raw": raw,
            "index": index,
            "decomposition": decomposition,
            "natives": natives,
            "authority": authority,
        }

        try:
            consumed = _invoke(
                raw=raw,
                index=index,
                authority=authority,
                decomposition=decomposition,
                natives=natives,
            )
            actual_parent = consumed["recomposition"]["parent_conclusion"]
            expected_parent = result["parent"].conclusion.value
            accepted = (
                consumed["whole_object_sha256"] == whole
                and actual_parent == expected_parent
            )
            error = None
        except Exception as exc:
            accepted = False
            actual_parent = None
            error = (
                exc.code
                if isinstance(exc, ConsumerError)
                else f"{type(exc).__name__}:{exc}"
            )

        positive[case_spec.case_id] = {
            "accepted": accepted,
            "expected_parent": result["parent"].conclusion.value,
            "actual_parent": actual_parent,
            "whole_object_sha256": whole,
            "error": error,
        }
        if not accepted:
            positive_failures.append(case_spec.case_id)

    negative: dict[str, dict[str, Any]] = {}
    false_accepts: list[str] = []
    for case_id, case in cases.items():
        checks = _real_mutations(case_id, case, cases)
        negative[case_id] = checks
        for name, record in checks.items():
            if not record["rejected"]:
                false_accepts.append(f"{case_id}:{name}")

    if positive_failures:
        disposition = "FALSIFIED_INDEPENDENT_CONSUMER_REAL_HANDOFF_REJECTION"
    elif false_accepts:
        disposition = "FALSIFIED_INDEPENDENT_CONSUMER_FALSE_ACCEPT"
    else:
        disposition = "SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE_RC1"

    result = {
        "schema": "contract-c-cal-v1-parent-consumer-postfreeze-rc1-result-v1",
        "disposition": disposition,
        "frozen_consumer": {
            "freeze_commit": "12e7e640b229619501960b1b89cf4716d8d985b3",
            "candidate_commit": "cc30821c15d8dd17301f8d8935feebe86e6ce0f4",
            "consumer_blob": "662e94c4445d2be9034e786711429394f217c0a6",
            "test_blob": "50f3104650a946b834c3ff6415bafb347863e836",
            "freeze_receipt_blob": "cb99cd2ee29d38e19c845771654898561b91552f",
        },
        "producer_subject": {
            "apparatus_rc0_head": "7138f6c1599b9b8f8c655f85c9eba0c264fb3b26",
            "candidate_blob": "df6b6ed410f52cafaeadfe1578d770f480a34b09",
            "cal_freeze_commit": producer.candidate.CAL_FREEZE_COMMIT,
            "cal_semantic_source_commit": producer.candidate.CAL_SEMANTIC_SOURCE_COMMIT,
            "cal_semantic_implementation_sha": producer.candidate.CAL_SEMANTIC_IMPLEMENTATION,
            "evidence_bundler_commit": "4e1f6fe00e7c350b28f52bfea14f1f8988847884",
            "rc2_authority": "b42c827acb0a9fe65353354d709add0e27bab307",
            "resolver": producer.candidate.POLICY_RESOLVER_COMMIT,
        },
        "positive_real_handoffs": positive,
        "positive_failures": positive_failures,
        "negative_real_mutations": negative,
        "false_accepts": false_accepts,
        "consumer_modified_post_freeze": False,
        "adapter_used": False,
        "production_promotion_authorized": False,
    }
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    if positive_failures or false_accepts:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
