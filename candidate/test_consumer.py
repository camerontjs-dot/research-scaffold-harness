import copy
import hashlib
import json
import unittest

from consumer import ConsumerError, consume_parent_bound_contract_c


INNER_PROFILE = "contract-c-successor-candidate-a-rc2-research"
OUTER_PROFILE = "contract-c-cal-v1-parent-recomposition-rc0"
CAL_FREEZE = "a" * 40
CAL_SOURCE = "b" * 40
SEMANTIC_IMPL = "c" * 40
POLICY = "d" * 64
POLICY_RESOLVER = "e" * 40


def canonical(value, *, lf=False):
    result = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return result + (b"\n" if lf else b"")


def digest_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def tagged_bytes(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def native_result(proposition_id, text_sha256, proposition_sha256, conclusion, *, marker=None):
    result = {
        "proposition": {
            "proposition_id": proposition_id,
            "proposition_sha256": proposition_sha256,
            "text_sha256": text_sha256,
        },
        "result": {"conclusion": conclusion},
    }
    if marker is not None:
        result["run_marker"] = marker
    return canonical(result)


def child_identity(proposition_id, text_sha256, native_raw, conclusion):
    material = {
        "proposition_id": proposition_id,
        "text_sha256": text_sha256,
        "audit_result_sha256": tagged_bytes(native_raw),
        "conclusion": conclusion,
    }
    return "cal-child-result:" + hashlib.sha256(canonical(material)).hexdigest()


def make_participant(source_id, passage_id, relation, role):
    return {
        "evidence_ref": {"source_id": source_id, "passage_id": passage_id},
        "relation": relation,
        "role": role,
    }


def make_proposition(proposition_id, content_sha256, conclusion, ref, *, reason=None):
    source_id, passage_id = ref
    if conclusion == "supported":
        relation = "supports"
        role = "causal"
        terminal_reason = "categorical_support"
        completion = "assessed"
        groups = [[{"source_id": source_id, "passage_id": passage_id}]]
    elif conclusion == "contradicted":
        relation = "refutes"
        role = "causal"
        terminal_reason = "categorical_refutation"
        completion = "assessed"
        groups = [[{"source_id": source_id, "passage_id": passage_id}]]
    else:
        relation = "non_polarized"
        role = "residual"
        terminal_reason = reason or "no_deciding_relation"
        completion = "not_checkable"
        groups = []
    return {
        "proposition": {
            "content_sha256": content_sha256,
            "proposition_id": proposition_id,
        },
        "execution": {"completion": completion, "state": "completed"},
        "terminal": {"reason": terminal_reason, "verdict": conclusion},
        "participants": [make_participant(source_id, passage_id, relation, role)],
        "basis_groups": groups,
    }


def make_fixture(conclusions=("supported", "supported")):
    child_ids = ["child-a", "child-b"]
    root_text = "The composed parent proposition."
    child_texts = ["First child proposition.", "Second child proposition."]
    child_text_hashes = [digest_text(value) for value in child_texts]
    content_hashes = [digest_text(value + " content") for value in child_ids]
    refs = [("source-a", "passage-a"), ("source-b", "passage-b")]

    contract_b_index = {
        "contract_version": "1.2.0",
        "bundle_id": "bundle-contract-b-1",
        "bundle_hash": "sha256:" + "1" * 64,
        "passages": [
            {"passage_id": passage_id, "source_id": source_id}
            for source_id, passage_id in refs
        ],
        "propositions": [
            {"content_sha256": "sha256:" + content_hash, "proposition_id": child_id}
            for child_id, content_hash in zip(child_ids, content_hashes)
        ],
    }
    authority = {
        "cal_freeze_commit": CAL_FREEZE,
        "cal_semantic_source_commit": CAL_SOURCE,
        "profile": INNER_PROFILE,
        "semantic_implementation_sha": SEMANTIC_IMPL,
        "policy_sha256": POLICY,
        "policy_resolver_commit_sha": POLICY_RESOLVER,
        "whole_object_sha256": "sha256:" + "0" * 64,
    }

    native = {}
    propositions = []
    for child_id, text_hash, content_hash, conclusion, ref in zip(
        child_ids, child_text_hashes, content_hashes, conclusions, refs
    ):
        proposition = make_proposition(
            child_id,
            "sha256:" + content_hash,
            conclusion,
            ref,
        )
        propositions.append(proposition)
        native[child_id] = native_result(
            child_id,
            text_hash,
            content_hash,
            conclusion,
        )

    rc2 = {
        "profile": INNER_PROFILE,
        "result_set_id": "sha256:" + "0" * 64,
        "contract_b": {
            "bundle_hash": contract_b_index["bundle_hash"],
            "bundle_id": contract_b_index["bundle_id"],
            "contract_version": contract_b_index["contract_version"],
        },
        "producer": {
            "policy_resolver_commit_sha": POLICY_RESOLVER,
            "policy_sha256": POLICY,
            "semantic_implementation_sha": SEMANTIC_IMPL,
        },
        "execution": {"state": "completed"},
        "propositions": propositions,
    }
    rc2_without_id = copy.deepcopy(rc2)
    rc2_without_id.pop("result_set_id")
    rc2["result_set_id"] = tagged_bytes(canonical(rc2_without_id, lf=True))

    decomposition = {
        "state": "declared",
        "decomposition_id": "decomposition-1",
        "operator": "all_of",
        "root": {
            "proposition_id": "root-parent",
            "text_sha256": "sha256:" + digest_text(root_text),
        },
        "children": [
            {
                "sequence": sequence,
                "proposition_id": child_id,
                "text_sha256": "sha256:" + text_hash,
            }
            for sequence, child_id, text_hash in zip(
                range(1, 3), child_ids, child_text_hashes
            )
        ],
    }

    ordered_children = []
    for sequence, child_id, text_hash, content_hash, conclusion in zip(
        range(1, 3), child_ids, child_text_hashes, content_hashes, conclusions
    ):
        ordered_children.append(
            {
                "sequence": sequence,
                "proposition_id": child_id,
                "text_sha256": "sha256:" + text_hash,
                "contract_c_content_sha256": "sha256:" + content_hash,
                "native_result_sha256": tagged_bytes(native[child_id]),
                "cal_result_id": child_identity(
                    child_id,
                    "sha256:" + text_hash,
                    native[child_id],
                    conclusion,
                ),
                "conclusion": conclusion,
            }
        )

    parent_conclusion = (
        "contradicted"
        if "contradicted" in conclusions
        else "supported"
        if all(value == "supported" for value in conclusions)
        else "not_checkable"
    )
    receipt = {
        "root_proposition_id": decomposition["root"]["proposition_id"],
        "root_text_sha256": decomposition["root"]["text_sha256"],
        "decomposition_state": "declared",
        "decomposition_id": decomposition["decomposition_id"],
        "operator": "all_of",
        "ordered_children": [
            {
                "proposition_id": child["proposition_id"],
                "text_sha256": child["text_sha256"],
                "result_id": child["cal_result_id"],
                "conclusion": child["conclusion"],
            }
            for child in ordered_children
        ],
        "root_result_id": None,
        "parent_conclusion": parent_conclusion,
    }
    recomposition = {
        "cal_freeze_commit": CAL_FREEZE,
        "cal_semantic_source_commit": CAL_SOURCE,
        "root": copy.deepcopy(decomposition["root"]),
        "decomposition_id": decomposition["decomposition_id"],
        "operator": "all_of",
        "ordered_children": ordered_children,
        "decomposition_receipt_id": hashlib.sha256(canonical(receipt)).hexdigest(),
        "parent_conclusion": parent_conclusion,
    }
    outer = {
        "profile": OUTER_PROFILE,
        "result_set_id": "sha256:" + "0" * 64,
        "rc2_result": rc2,
        "recomposition": recomposition,
    }
    outer_without_id = copy.deepcopy(outer)
    outer_without_id.pop("result_set_id")
    outer["result_set_id"] = tagged_bytes(canonical(outer_without_id, lf=True))
    raw = canonical(outer, lf=True)
    authority["whole_object_sha256"] = tagged_bytes(raw)
    return {
        "raw": raw,
        "outer": outer,
        "contract_b_index": contract_b_index,
        "authority": authority,
        "decomposition": decomposition,
        "native": native,
    }


def reseal_outer(fixture):
    """Recompute local identities for mutation tests, retaining authority."""
    outer = copy.deepcopy(fixture["outer"])
    native = fixture["native"]
    rc2 = outer["rc2_result"]
    rc2_without_id = copy.deepcopy(rc2)
    rc2_without_id.pop("result_set_id")
    rc2["result_set_id"] = tagged_bytes(canonical(rc2_without_id, lf=True))
    for child in outer["recomposition"]["ordered_children"]:
        child_id = child["proposition_id"]
        child["native_result_sha256"] = tagged_bytes(native[child_id])
        child["cal_result_id"] = child_identity(
            child_id,
            child["text_sha256"],
            native[child_id],
            child["conclusion"],
        )
    receipt = {
        "root_proposition_id": outer["recomposition"]["root"]["proposition_id"],
        "root_text_sha256": outer["recomposition"]["root"]["text_sha256"],
        "decomposition_state": "declared",
        "decomposition_id": outer["recomposition"]["decomposition_id"],
        "operator": "all_of",
        "ordered_children": [
            {
                "proposition_id": child["proposition_id"],
                "text_sha256": child["text_sha256"],
                "result_id": child["cal_result_id"],
                "conclusion": child["conclusion"],
            }
            for child in sorted(
                outer["recomposition"]["ordered_children"], key=lambda child: child["sequence"]
            )
        ],
        "root_result_id": None,
        "parent_conclusion": outer["recomposition"]["parent_conclusion"],
    }
    outer["recomposition"]["decomposition_receipt_id"] = hashlib.sha256(canonical(receipt)).hexdigest()
    outer_without_id = copy.deepcopy(outer)
    outer_without_id.pop("result_set_id")
    outer["result_set_id"] = tagged_bytes(canonical(outer_without_id, lf=True))
    return canonical(outer, lf=True)


class ConsumerTests(unittest.TestCase):
    def assertAccepted(self, conclusions):
        fixture = make_fixture(conclusions)
        result = consume_parent_bound_contract_c(
            fixture["raw"],
            contract_b_index=fixture["contract_b_index"],
            expected_authority=fixture["authority"],
            contract_a_decomposition=fixture["decomposition"],
            native_child_results=fixture["native"],
        )
        self.assertEqual(result["recomposition"]["parent_conclusion"], "contradicted" if "contradicted" in conclusions else "supported" if all(value == "supported" for value in conclusions) else "not_checkable")
        self.assertNotIn("decision", result)
        self.assertNotIn("authorization", result)

    def assertRejected(self, fixture, *, raw=None, authority=None, native=None, message=None):
        with self.assertRaises(ConsumerError) as context:
            consume_parent_bound_contract_c(
                fixture["raw"] if raw is None else raw,
                contract_b_index=fixture["contract_b_index"],
                expected_authority=fixture["authority"] if authority is None else authority,
                contract_a_decomposition=fixture["decomposition"],
                native_child_results=fixture["native"] if native is None else native,
            )
        if message is not None:
            self.assertEqual(context.exception.code, message)

    def test_parent_supported_supported(self):
        self.assertAccepted(("supported", "supported"))

    def test_parent_contradicted_supported(self):
        self.assertAccepted(("contradicted", "supported"))

    def test_parent_supported_not_checkable(self):
        self.assertAccepted(("supported", "not_checkable"))

    def test_parent_contradicted_not_checkable(self):
        self.assertAccepted(("contradicted", "not_checkable"))

    def test_child_result_identity_mutation_rejected(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        mutated["recomposition"]["ordered_children"][0]["cal_result_id"] = "cal-child-result:" + "f" * 64
        self.assertRejected(fixture, raw=canonical(mutated, lf=True))

    def test_native_result_bytes_mutation_rejected(self):
        fixture = make_fixture()
        native = dict(fixture["native"])
        native["child-a"] = native_result(
            "child-a",
            digest_text("First child proposition."),
            digest_text("child-a content"),
            "supported",
            marker="different-run",
        )
        self.assertRejected(fixture, native=native)

    def test_child_omission_rejected(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        mutated["recomposition"]["ordered_children"].pop()
        self.assertRejected(fixture, raw=canonical(mutated, lf=True))

    def test_reversed_wire_order_rejected_as_noncanonical(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        mutated["recomposition"]["ordered_children"].reverse()
        self.assertRejected(fixture, raw=canonical(mutated, lf=True), message="NON_CANONICAL_OUTER_BYTES")

    def test_sequence_mutation_rejected(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        mutated["recomposition"]["ordered_children"][0]["sequence"] = 2
        self.assertRejected(fixture, raw=canonical(mutated, lf=True))

    def test_root_binding_mutation_rejected(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        mutated["recomposition"]["root"]["proposition_id"] = "different-root"
        self.assertRejected(fixture, raw=canonical(mutated, lf=True))

    def test_receipt_identity_mutation_rejected(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        mutated["recomposition"]["decomposition_receipt_id"] = "0" * 64
        self.assertRejected(fixture, raw=canonical(mutated, lf=True))

    def test_parent_conclusion_mutation_rejected(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        mutated["recomposition"]["parent_conclusion"] = "contradicted"
        self.assertRejected(fixture, raw=canonical(mutated, lf=True))

    def test_cross_run_replay_rejected(self):
        fixture = make_fixture()
        native = dict(fixture["native"])
        native["child-a"] = native_result(
            "child-a",
            digest_text("First child proposition."),
            digest_text("child-a content"),
            "supported",
            marker="other-run",
        )
        self.assertRejected(fixture, native=native)

    def test_coherent_reseal_fails_fixed_external_authority(self):
        fixture = make_fixture()
        resealed_fixture = copy.deepcopy(fixture)
        resealed_fixture["native"]["child-a"] = native_result(
            "child-a",
            digest_text("First child proposition."),
            digest_text("child-a content"),
            "supported",
            marker="coherently-resealed-run",
        )
        raw = reseal_outer(resealed_fixture)
        self.assertRejected(
            fixture,
            raw=raw,
            native=resealed_fixture["native"],
            message="WHOLE_OBJECT_AUTHORITY_MISMATCH",
        )

    def test_private_codec_result_id_rejected(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        mutated["recomposition"]["ordered_children"][0]["cal_result_id"] = "private-codec:child-a"
        self.assertRejected(fixture, raw=canonical(mutated, lf=True), message="INVALID_CAL_RESULT_ID")

    def test_inner_substitution_rejected(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        mutated["rc2_result"]["propositions"][0]["proposition"]["content_sha256"] = "sha256:" + "8" * 64
        self.assertRejected(fixture, raw=canonical(mutated, lf=True))

    def test_external_whole_object_mismatch_rejected(self):
        fixture = make_fixture()
        authority = copy.deepcopy(fixture["authority"])
        authority["whole_object_sha256"] = "sha256:" + "f" * 64
        self.assertRejected(fixture, authority=authority, message="WHOLE_OBJECT_AUTHORITY_MISMATCH")

    def test_destination_policy_injection_rejected(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        mutated["decision"] = "CLEAR"
        self.assertRejected(fixture, raw=canonical(mutated, lf=True), message="INVALID_OUTER_OBJECT")

    def test_duplicate_json_key_rejected(self):
        fixture = make_fixture()
        raw = fixture["raw"].replace(b'"profile":"' + OUTER_PROFILE.encode(), b'"profile":"' + OUTER_PROFILE.encode() + b'","profile":"' + OUTER_PROFILE.encode(), 1)
        self.assertRejected(fixture, raw=raw, message="INVALID_OUTER_JSON")

    def test_inner_reason_case_is_not_normalized(self):
        fixture = make_fixture(("not_checkable", "supported"))
        mutated = copy.deepcopy(fixture["outer"])
        mutated["rc2_result"]["propositions"][0]["terminal"]["reason"] = "unsupported_semantic_family"
        self.assertRejected(fixture, raw=canonical(mutated, lf=True))

    def test_relation_laundering_rejected(self):
        fixture = make_fixture()
        mutated = copy.deepcopy(fixture["outer"])
        participant = mutated["rc2_result"]["propositions"][0]["participants"][0]
        participant["relation"] = "non_polarized"
        self.assertRejected(fixture, raw=canonical(mutated, lf=True))


if __name__ == "__main__":
    unittest.main()
