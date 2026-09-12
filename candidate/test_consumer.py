from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))

from consumer import ConsumerError, consume_contract_c, evaluate_supported_claim


RAW = b'{"contract_c_version":"research-non-deciding-rc0","execution":{"state":"completed"},"input":{"contract_b":{"bundle_hash":"sha256:2f4d964cacef0d236e1c33ef2936dbff277ce1bfb58414a129dc932a245baa7a","bundle_id":"handoff-bundle-non-deciding-rc0","contract_version":"1.2.0"}},"producer":{"policy":{"canonical":{"profile":"contract-c-non-deciding-shadow-rc0","semantics":"event-order-unresolved-provenance"},"sha256":"2ea761c2ec5d1f12bb904bb5ea98880942c426c34071ebaa195b5776218686d7"},"semantic_implementation_sha":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},"propositions":[{"assessments":{"aperture_completeness":{"state":"not_performed"},"eligibility":{"state":"not_performed"},"semantic_validity":{"state":"not_performed"},"temporal_applicability":{"state":"not_performed"}},"conclusion":{"basis_members":[{"id":"contribution:388c10facb8bd481ba37fee9874d59beb563fbd22c47e5e7f4f1299401a82158","namespace":"contribution"},{"id":"contribution:cbcf5aa36024d1b9b51001ae30ecd391e206a5d4532e5490d05d478edd3bdab2","namespace":"contribution"}],"causal_form":"independent_sufficient_alternatives","reported_verdict":"not_checkable","residual_contribution_ids":[],"rule_roles":[],"terminal_branch":"unresolved_categorical_relation"},"contributions":[{"channel":"non_deciding","contribution_id":"contribution:388c10facb8bd481ba37fee9874d59beb563fbd22c47e5e7f4f1299401a82158","evidence_ref":{"passage_id":"u-a","passage_sha256":"sha256:1055d389bfc901c54c17969d73a865cf8455052a13418fd5c9bbf7f51b874638","source_id":"src-temporal"}},{"channel":"non_deciding","contribution_id":"contribution:cbcf5aa36024d1b9b51001ae30ecd391e206a5d4532e5490d05d478edd3bdab2","evidence_ref":{"passage_id":"u-b","passage_sha256":"sha256:934354048cddf5a15117a6bb973b4a4bf4a8cd8f28bac6bc63128bce3ad77130","source_id":"src-temporal"}}],"execution":{"completion":"not_checkable","state":"completed"},"measurement":null,"proposition":{"proposition_id":"temporal-p1","text_sha256":"9bf7be755d7dd9a2dd375a7b5e8f516464394ce71ebfa210ea651fe9b8564371"}}],"result_set_id":"result-set:4483272c4f6fbd9cb2362be7e3174bbd00aff3cf761d6c374897f3478818c9f0"}\n'

INDEX = {
    "bundle_hash": "sha256:2f4d964cacef0d236e1c33ef2936dbff277ce1bfb58414a129dc932a245baa7a",
    "bundle_id": "handoff-bundle-non-deciding-rc0",
    "contract_version": "1.2.0",
    "passages": {
        "u-a": {
            "passage_sha256": "sha256:1055d389bfc901c54c17969d73a865cf8455052a13418fd5c9bbf7f51b874638",
            "source_id": "src-temporal",
        },
        "u-b": {
            "passage_sha256": "sha256:934354048cddf5a15117a6bb973b4a4bf4a8cd8f28bac6bc63128bce3ad77130",
            "source_id": "src-temporal",
        },
    },
    "propositions": {
        "temporal-p1": "9bf7be755d7dd9a2dd375a7b5e8f516464394ce71ebfa210ea651fe9b8564371"
    },
}

PROFILE = {
    "contract_c_version": "research-non-deciding-rc0",
    "whole_object_sha256": "sha256:325962ebcdbf6af836bb6193a451524ccd40b4d10f2394ff9f703fbfce1ec1e3",
    "result_set_id": "result-set:4483272c4f6fbd9cb2362be7e3174bbd00aff3cf761d6c374897f3478818c9f0",
}


def canonical(value):
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def parse_fixture():
    return json.loads(RAW.decode("utf-8"))


def rebind(obj):
    obj = copy.deepcopy(obj)
    obj.pop("result_set_id", None)
    result_set_id = "result-set:" + hashlib.sha256(canonical(obj)).hexdigest()
    obj["result_set_id"] = result_set_id
    raw = canonical(obj)
    profile = {
        "contract_c_version": "research-non-deciding-rc0",
        "whole_object_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
        "result_set_id": result_set_id,
    }
    return raw, profile


class ConsumerTests(unittest.TestCase):
    def assert_code(self, code, func, *args):
        with self.assertRaises(ConsumerError) as caught:
            func(*args)
        self.assertEqual(code, caught.exception.code)

    def test_exact_frozen_handoff_preserves_non_deciding_multiplicity(self):
        consumed = consume_contract_c(RAW, INDEX, PROFILE)
        self.assertEqual(PROFILE["whole_object_sha256"], consumed["whole_object_sha256"])
        prop = consumed["propositions"][0]
        self.assertEqual("temporal-p1", prop["proposition"]["proposition_id"])
        self.assertEqual("not_checkable", prop["reported_verdict"])
        self.assertEqual("unresolved_categorical_relation", prop["terminal_branch"])
        self.assertEqual("independent_sufficient_alternatives", prop["causal_form"])
        self.assertEqual(2, len(prop["causal_contributions"]))
        self.assertEqual(
            {"u-a", "u-b"},
            {c["evidence_ref"]["passage_id"] for c in prop["causal_contributions"]},
        )
        self.assertEqual(
            {"non_deciding"},
            {c["channel"] for c in prop["causal_contributions"]},
        )
        self.assertEqual([], prop["residual_contributions"])

    def test_wrong_external_digest_rejects(self):
        profile = dict(PROFILE)
        profile["whole_object_sha256"] = "sha256:" + "0" * 64
        self.assert_code("WHOLE_OBJECT_DIGEST_MISMATCH", consume_contract_c, RAW, INDEX, profile)

    def test_missing_and_malformed_expected_profile_reject(self):
        for profile in (None, {}, {"contract_c_version": "research-non-deciding-rc0"}):
            self.assert_code("EXPECTED_PROFILE_INVALID", consume_contract_c, RAW, INDEX, profile)
        malformed = dict(PROFILE)
        malformed["whole_object_sha256"] = "bad"
        self.assert_code("EXPECTED_PROFILE_INVALID", consume_contract_c, RAW, INDEX, malformed)

    def test_wrong_version_rejects_even_when_object_rebound(self):
        obj = parse_fixture()
        obj["contract_c_version"] = "1.0.0"
        raw, _ = rebind(obj)
        profile = dict(PROFILE)
        profile["whole_object_sha256"] = "sha256:" + hashlib.sha256(raw).hexdigest()
        profile["result_set_id"] = json.loads(raw)["result_set_id"]
        self.assert_code("CONTRACT_C_VERSION_MISMATCH", consume_contract_c, raw, INDEX, profile)

    def test_wrong_contract_b_binding_rejects(self):
        index = copy.deepcopy(INDEX)
        index["bundle_id"] = "different-bundle"
        self.assert_code("CONTRACT_B_BINDING_MISMATCH", consume_contract_c, RAW, index, PROFILE)

    def test_wrong_proposition_binding_rejects(self):
        index = copy.deepcopy(INDEX)
        index["propositions"]["temporal-p1"] = "0" * 64
        self.assert_code("PROPOSITION_BINDING_MISMATCH", consume_contract_c, RAW, index, PROFILE)

    def test_wrong_evidence_reference_rejects(self):
        index = copy.deepcopy(INDEX)
        index["passages"]["u-a"]["source_id"] = "wrong-source"
        self.assert_code("EVIDENCE_REF_MISMATCH", consume_contract_c, RAW, index, PROFILE)

    def test_missing_causal_contribution_rejects(self):
        obj = parse_fixture()
        obj["propositions"][0]["contributions"].pop()
        raw, profile = rebind(obj)
        self.assert_code("UNKNOWN_CAUSAL_CONTRIBUTION", consume_contract_c, raw, INDEX, profile)

    def test_causal_residual_overlap_rejects(self):
        obj = parse_fixture()
        cid = obj["propositions"][0]["contributions"][0]["contribution_id"]
        obj["propositions"][0]["conclusion"]["residual_contribution_ids"] = [cid]
        raw, profile = rebind(obj)
        self.assert_code("CAUSAL_RESIDUAL_OVERLAP", consume_contract_c, raw, INDEX, profile)

    def test_unclassified_retained_contribution_rejects(self):
        obj = parse_fixture()
        extra = copy.deepcopy(obj["propositions"][0]["contributions"][0])
        extra["contribution_id"] = "contribution:" + "0" * 64
        obj["propositions"][0]["contributions"].append(extra)
        raw, profile = rebind(obj)
        self.assert_code("UNCLASSIFIED_CONTRIBUTION", consume_contract_c, raw, INDEX, profile)

    def test_stale_result_set_id_rejects(self):
        obj = parse_fixture()
        obj["propositions"][0]["conclusion"]["terminal_branch"] = "changed"
        raw = canonical(obj)
        profile = dict(PROFILE)
        profile["whole_object_sha256"] = "sha256:" + hashlib.sha256(raw).hexdigest()
        self.assert_code("RESULT_SET_ID_MISMATCH", consume_contract_c, raw, INDEX, profile)

    def test_baseline_policy_probe_holds(self):
        consumed = consume_contract_c(RAW, INDEX, PROFILE)
        decision = evaluate_supported_claim(consumed, "temporal-p1")
        self.assertEqual("hold", decision["disposition"])

    def test_policy_probe_clears_only_completed_assessed_supported(self):
        consumed = consume_contract_c(RAW, INDEX, PROFILE)
        prop = consumed["propositions"][0]
        prop["execution"] = {"state": "completed", "completion": "assessed"}
        prop["reported_verdict"] = "supported"
        self.assertEqual(
            "clear", evaluate_supported_claim(consumed, "temporal-p1")["disposition"]
        )
        prop["reported_verdict"] = "not_checkable"
        self.assertEqual(
            "hold", evaluate_supported_claim(consumed, "temporal-p1")["disposition"]
        )

    def test_jointly_sufficient_same_members_remains_distinct(self):
        obj = parse_fixture()
        obj["propositions"][0]["conclusion"]["causal_form"] = "jointly_sufficient"
        raw, profile = rebind(obj)
        consumed = consume_contract_c(raw, INDEX, profile)
        prop = consumed["propositions"][0]
        self.assertEqual("jointly_sufficient", prop["causal_form"])
        self.assertEqual(2, len(prop["causal_contributions"]))

    def test_coherent_causal_residual_role_variant_remains_distinct(self):
        obj = parse_fixture()
        conclusion = obj["propositions"][0]["conclusion"]
        residual_id = conclusion["basis_members"].pop()["id"]
        conclusion["residual_contribution_ids"] = [residual_id]
        conclusion["causal_form"] = "single_necessary"
        raw, profile = rebind(obj)
        consumed = consume_contract_c(raw, INDEX, profile)
        prop = consumed["propositions"][0]
        self.assertEqual(1, len(prop["causal_contributions"]))
        self.assertEqual(1, len(prop["residual_contributions"]))
        self.assertEqual(residual_id, prop["residual_contributions"][0]["contribution_id"])

    def test_producer_policy_hash_binding_rejects(self):
        obj = parse_fixture()
        obj["producer"]["policy"]["canonical"]["profile"] = "changed"
        raw, profile = rebind(obj)
        self.assert_code("PRODUCER_POLICY_HASH_MISMATCH", consume_contract_c, raw, INDEX, profile)

    def test_unknown_channel_rejects(self):
        obj = parse_fixture()
        obj["propositions"][0]["contributions"][0]["channel"] = "winner"
        raw, profile = rebind(obj)
        self.assert_code("CONTRIBUTION_CHANNEL_INVALID", consume_contract_c, raw, INDEX, profile)

    def test_causal_cardinality_rejects(self):
        obj = parse_fixture()
        obj["propositions"][0]["conclusion"]["causal_form"] = "single_necessary"
        raw, profile = rebind(obj)
        self.assert_code("CAUSAL_CARDINALITY_INVALID", consume_contract_c, raw, INDEX, profile)

    def test_noncanonical_bytes_reject_when_externally_authorized(self):
        obj = parse_fixture()
        raw = (json.dumps(obj, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        profile = dict(PROFILE)
        profile["whole_object_sha256"] = "sha256:" + hashlib.sha256(raw).hexdigest()
        self.assert_code("NONCANONICAL_OBJECT_BYTES", consume_contract_c, raw, INDEX, profile)

    def test_duplicate_json_key_rejects_when_externally_authorized(self):
        raw = b'{"contract_c_version":"research-non-deciding-rc0","contract_c_version":"research-non-deciding-rc0"}\n'
        profile = dict(PROFILE)
        profile["whole_object_sha256"] = "sha256:" + hashlib.sha256(raw).hexdigest()
        self.assert_code("DUPLICATE_JSON_KEY", consume_contract_c, raw, INDEX, profile)

    def test_missing_proposition_probe_rejects(self):
        consumed = consume_contract_c(RAW, INDEX, PROFILE)
        self.assert_code("PROPOSITION_NOT_FOUND", evaluate_supported_claim, consumed, "absent")


if __name__ == "__main__":
    unittest.main()
