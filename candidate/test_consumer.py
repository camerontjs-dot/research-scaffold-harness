"""Synthetic prereveal tests for the context-free consumer."""

from __future__ import annotations

import copy
import hashlib
import json
import unittest

from candidate.consumer import ConsumerError, consume_parent_bound_contract_c


OUTER_PROFILE = "contract-c-cal-v1-parent-recomposition-rc0"
INNER_PROFILE = "contract-c-successor-candidate-a-rc2-research"
CAL_FREEZE = "d" * 40
CAL_SOURCE = "e" * 40
SEMANTIC = "a" * 40
POLICY = "b" * 64
RESOLVER = "c" * 40


def _compact(value: object, *, trailing_lf: bool = False) -> bytes:
    text = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return text.encode("utf-8") + (b"\n" if trailing_lf else b"")


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _tag(raw: bytes) -> str:
    return "sha256:" + _sha(raw)


def _normalize_inner(value: dict) -> dict:
    result = copy.deepcopy(value)
    result["propositions"] = []
    for proposition in value["propositions"]:
        item = copy.deepcopy(proposition)
        item["participants"].sort(
            key=lambda participant: (
                participant["evidence_ref"]["source_id"],
                participant["evidence_ref"]["passage_id"],
            )
        )
        for group in item["basis_groups"]:
            group.sort(key=lambda member: (member["source_id"], member["passage_id"]))
        item["basis_groups"].sort(
            key=lambda group: tuple((member["source_id"], member["passage_id"]) for member in group)
        )
        result["propositions"].append(item)
    result["propositions"].sort(
        key=lambda item: (
            item["proposition"]["proposition_id"],
            item["proposition"]["content_sha256"],
        )
    )
    return result


def _child_result_id(proposition_id: str, text_sha256: str, native_digest: str, conclusion: str) -> str:
    material = {
        "proposition_id": proposition_id,
        "text_sha256": text_sha256,
        "audit_result_sha256": native_digest,
        "conclusion": conclusion,
    }
    return "cal-child-result:" + _sha(_compact(material))


def _receipt_id(recomposition: dict) -> str:
    material = {
        "root_proposition_id": recomposition["root"]["proposition_id"],
        "root_text_sha256": recomposition["root"]["text_sha256"],
        "decomposition_state": "declared",
        "decomposition_id": recomposition["decomposition_id"],
        "operator": "all_of",
        "ordered_children": [
            {
                "proposition_id": child["proposition_id"],
                "text_sha256": child["text_sha256"],
                "result_id": child["cal_result_id"],
                "conclusion": child["conclusion"],
            }
            for child in sorted(recomposition["ordered_children"], key=lambda item: item["sequence"])
        ],
        "root_result_id": None,
        "parent_conclusion": recomposition["parent_conclusion"],
    }
    return _sha(_compact(material))


def _seal(outer: dict) -> bytes:
    inner = _normalize_inner(outer["rc2_result"])
    without_inner_id = copy.deepcopy(inner)
    without_inner_id.pop("result_set_id")
    inner["result_set_id"] = _tag(_compact(without_inner_id, trailing_lf=True))
    outer["rc2_result"] = inner
    outer["recomposition"]["ordered_children"].sort(key=lambda item: item["sequence"])
    outer_without_id = copy.deepcopy(outer)
    outer_without_id.pop("result_set_id")
    outer["result_set_id"] = _tag(_compact(outer_without_id, trailing_lf=True))
    return _compact(outer, trailing_lf=True)


def _fixture(conclusions: tuple[str, str] = ("supported", "supported"), run_marker: str = "run-a") -> dict:
    content_hashes = ("1" * 64, "2" * 64)
    text_hashes = ("3" * 64, "4" * 64)
    contract_b = {
        "contract_version": "1.2.0",
        "bundle_id": "bundle-synthetic",
        "bundle_hash": "sha256:" + "f" * 64,
    }
    index = {
        **contract_b,
        "propositions": {
            "child-1": {"content_sha256": content_hashes[0]},
            "child-2": {"content_sha256": content_hashes[1]},
        },
        "passages": [
            {"source_id": "source-1", "passage_id": "passage-1", "passage_sha256": "5" * 64},
            {"source_id": "source-2", "passage_id": "passage-2", "passage_sha256": "6" * 64},
        ],
    }
    decomposition = {
        "state": "declared",
        "decomposition_id": "decomposition-synthetic",
        "operator": "all_of",
        "root": {"proposition_id": "root", "text_sha256": "sha256:" + "7" * 64},
        "children": [
            {"sequence": 1, "proposition_id": "child-1", "text_sha256": "sha256:" + text_hashes[0]},
            {"sequence": 2, "proposition_id": "child-2", "text_sha256": "sha256:" + text_hashes[1]},
        ],
    }
    authority = {
        "profile": OUTER_PROFILE,
        "inner_profile": INNER_PROFILE,
        "cal_freeze_commit": CAL_FREEZE,
        "cal_semantic_source_commit": CAL_SOURCE,
        "semantic_implementation_sha": SEMANTIC,
        "policy_sha256": POLICY,
        "policy_resolver_commit_sha": RESOLVER,
        "whole_object_sha256": "sha256:" + "0" * 64,
    }

    propositions = []
    natives: dict[str, bytes] = {}
    children = []
    for number, conclusion in enumerate(conclusions, start=1):
        proposition_id = f"child-{number}"
        text_sha256 = "sha256:" + text_hashes[number - 1]
        ref = {"source_id": f"source-{number}", "passage_id": f"passage-{number}"}
        if conclusion == "supported":
            participant = {"evidence_ref": ref, "relation": "supports", "role": "causal"}
            terminal = {"verdict": "supported", "reason": "categorical_support"}
            completion = "assessed"
            basis_groups = [[ref]]
        elif conclusion == "contradicted":
            participant = {"evidence_ref": ref, "relation": "refutes", "role": "causal"}
            terminal = {"verdict": "contradicted", "reason": "categorical_refutation"}
            completion = "assessed"
            basis_groups = [[ref]]
        else:
            participant = {"evidence_ref": ref, "relation": "non_polarized", "role": "residual"}
            terminal = {"verdict": "not_checkable", "reason": "no_deciding_relation"}
            completion = "not_checkable"
            basis_groups = []
        propositions.append(
            {
                "proposition": {"proposition_id": proposition_id, "content_sha256": "sha256:" + content_hashes[number - 1]},
                "execution": {"state": "completed", "completion": completion},
                "terminal": terminal,
                "participants": [participant],
                "basis_groups": basis_groups,
            }
        )
        native = {
            "proposition": {
                "proposition_id": proposition_id,
                "text_sha256": text_sha256,
                "proposition_sha256": content_hashes[number - 1],
            },
            "result": {"conclusion": conclusion},
            "private_trace": {"run": run_marker, "child": proposition_id},
        }
        native_bytes = _compact(native)
        natives[proposition_id] = native_bytes
        native_digest = _tag(native_bytes)
        children.append(
            {
                "sequence": number,
                "proposition_id": proposition_id,
                "text_sha256": text_sha256,
                "contract_c_content_sha256": "sha256:" + content_hashes[number - 1],
                "native_result_sha256": native_digest,
                "cal_result_id": _child_result_id(proposition_id, text_sha256, native_digest, conclusion),
                "conclusion": conclusion,
            }
        )

    inner = {
        "profile": INNER_PROFILE,
        "result_set_id": "sha256:" + "0" * 64,
        "contract_b": contract_b,
        "producer": {
            "semantic_implementation_sha": SEMANTIC,
            "policy_sha256": POLICY,
            "policy_resolver_commit_sha": RESOLVER,
        },
        "execution": {"state": "completed"},
        "propositions": propositions,
    }
    recomposition = {
        "cal_freeze_commit": CAL_FREEZE,
        "cal_semantic_source_commit": CAL_SOURCE,
        "root": copy.deepcopy(decomposition["root"]),
        "decomposition_id": decomposition["decomposition_id"],
        "operator": "all_of",
        "ordered_children": children,
        "decomposition_receipt_id": "0" * 64,
        "parent_conclusion": (
            "contradicted"
            if "contradicted" in conclusions
            else "supported"
            if all(conclusion == "supported" for conclusion in conclusions)
            else "not_checkable"
        ),
    }
    recomposition["decomposition_receipt_id"] = _receipt_id(recomposition)
    outer = {
        "profile": OUTER_PROFILE,
        "result_set_id": "sha256:" + "0" * 64,
        "rc2_result": inner,
        "recomposition": recomposition,
    }
    raw = _seal(outer)
    authority["whole_object_sha256"] = _tag(raw)
    return {
        "raw": raw,
        "outer": outer,
        "index": index,
        "authority": authority,
        "decomposition": decomposition,
        "natives": natives,
    }


def _invoke(fixture: dict, *, raw: bytes | None = None, natives: dict[str, bytes] | None = None, authority: dict | None = None):
    return consume_parent_bound_contract_c(
        fixture["raw"] if raw is None else raw,
        contract_b_index=fixture["index"],
        expected_authority=fixture["authority"] if authority is None else authority,
        contract_a_decomposition=fixture["decomposition"],
        native_child_results=fixture["natives"] if natives is None else natives,
    )


class ConsumerPrerevealTests(unittest.TestCase):
    def test_success_parent_conclusion_matrix(self) -> None:
        expected = {
            ("supported", "supported"): "supported",
            ("contradicted", "supported"): "contradicted",
            ("supported", "not_checkable"): "not_checkable",
            ("contradicted", "not_checkable"): "contradicted",
        }
        for conclusions, parent in expected.items():
            with self.subTest(conclusions=conclusions):
                fixture = _fixture(conclusions)
                result = _invoke(fixture)
                self.assertEqual(result["recomposition"]["parent_conclusion"], parent)
                self.assertEqual(result["whole_object_sha256"], fixture["authority"]["whole_object_sha256"])
                self.assertEqual(
                    {item["proposition"]["proposition_id"] for item in result["rc2_result"]["propositions"]},
                    {"child-1", "child-2"},
                )

    def assert_rejects(self, fixture: dict, *, raw: bytes | None = None, natives: dict | None = None, authority: dict | None = None) -> None:
        with self.assertRaises(ConsumerError):
            _invoke(fixture, raw=raw, natives=natives, authority=authority)

    def test_child_result_identity_mutation(self) -> None:
        fixture = _fixture()
        value = copy.deepcopy(fixture["outer"])
        value["recomposition"]["ordered_children"][0]["cal_result_id"] = "cal-child-result:" + "0" * 64
        self.assert_rejects(fixture, raw=_compact(value, trailing_lf=True))

    def test_native_result_bytes_mutation(self) -> None:
        fixture = _fixture()
        natives = copy.deepcopy(fixture["natives"])
        changed = json.loads(natives["child-1"].decode("utf-8"))
        changed["private_trace"]["mutated"] = True
        natives["child-1"] = _compact(changed)
        self.assert_rejects(fixture, natives=natives)

    def test_child_omission(self) -> None:
        fixture = _fixture()
        value = copy.deepcopy(fixture["outer"])
        value["recomposition"]["ordered_children"].pop()
        self.assert_rejects(fixture, raw=_compact(value, trailing_lf=True))

    def test_sequence_and_order_mutations(self) -> None:
        fixture = _fixture()
        value = copy.deepcopy(fixture["outer"])
        value["recomposition"]["ordered_children"][0]["sequence"] = 3
        self.assert_rejects(fixture, raw=_compact(value, trailing_lf=True))

        value = copy.deepcopy(fixture["outer"])
        value["recomposition"]["ordered_children"].reverse()
        self.assert_rejects(fixture, raw=_compact(value, trailing_lf=True))

    def test_root_receipt_and_parent_mutations(self) -> None:
        fixture = _fixture()
        value = copy.deepcopy(fixture["outer"])
        value["recomposition"]["root"]["proposition_id"] = "different-root"
        self.assert_rejects(fixture, raw=_compact(value, trailing_lf=True))

        value = copy.deepcopy(fixture["outer"])
        value["recomposition"]["decomposition_receipt_id"] = "0" * 64
        self.assert_rejects(fixture, raw=_compact(value, trailing_lf=True))

        value = copy.deepcopy(fixture["outer"])
        value["recomposition"]["parent_conclusion"] = "not_checkable"
        self.assert_rejects(fixture, raw=_compact(value, trailing_lf=True))

    def test_cross_run_replay_and_private_codec_result_id(self) -> None:
        fixture = _fixture(run_marker="run-a")
        other = _fixture(run_marker="run-b")
        self.assert_rejects(fixture, natives=other["natives"])

        value = copy.deepcopy(fixture["outer"])
        value["recomposition"]["ordered_children"][0]["cal_result_id"] = "private-codec-id"
        self.assert_rejects(fixture, raw=_compact(value, trailing_lf=True))

    def test_inner_substitution_and_external_digest_mismatch(self) -> None:
        fixture = _fixture()
        value = copy.deepcopy(fixture["outer"])
        value["rc2_result"]["propositions"][0]["proposition"]["content_sha256"] = "sha256:" + "9" * 64
        self.assert_rejects(fixture, raw=_compact(value, trailing_lf=True))

        authority = copy.deepcopy(fixture["authority"])
        authority["whole_object_sha256"] = "sha256:" + "9" * 64
        self.assert_rejects(fixture, authority=authority)

    def test_coherent_reseal_fails_external_authority(self) -> None:
        fixture = _fixture()
        value = copy.deepcopy(fixture["outer"])
        natives = copy.deepcopy(fixture["natives"])
        changed = json.loads(natives["child-1"].decode("utf-8"))
        changed["private_trace"]["run"] = "resealed-run"
        natives["child-1"] = _compact(changed)
        child = value["recomposition"]["ordered_children"][0]
        native_digest = _tag(natives["child-1"])
        child["native_result_sha256"] = native_digest
        child["cal_result_id"] = _child_result_id(
            child["proposition_id"], child["text_sha256"], native_digest, child["conclusion"]
        )
        value["recomposition"]["decomposition_receipt_id"] = _receipt_id(value["recomposition"])
        resealed = _seal(value)
        self.assertNotEqual(resealed, fixture["raw"])
        self.assert_rejects(fixture, raw=resealed, natives=natives)

    def test_destination_policy_injection(self) -> None:
        fixture = _fixture()
        value = copy.deepcopy(fixture["outer"])
        value["recomposition"]["destination_policy"] = "CLEAR"
        self.assert_rejects(fixture, raw=_compact(value, trailing_lf=True))


if __name__ == "__main__":
    unittest.main()
