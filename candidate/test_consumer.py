"""Prereveal tests for Contract C Candidate A RC2 Consumer B.

Derived only from research/contract_c_candidate_a_rc2_consumer_b_aperture/
SPEC.md, handoffs, CONTRACT_B_INDEXES.json and AUTHORITIES.json.
"""

import copy
import hashlib
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from consumer import ConsumerError, consume_contract_c

APERTURE = pathlib.Path(__file__).resolve().parent.parent / "research" / "contract_c_candidate_a_rc2_consumer_b_aperture"

FORBIDDEN_SUBSTRINGS = [
    "authorization", "Authorization", "CLEAR", "HOLD", "confidence",
    "score", "rank", "winner", "permission", "destination",
    "threshold", "requested_effect", "requested-effect", "actor",
    "delegation", "approval",
]


def load_json(name):
    with open(APERTURE / name, "r", encoding="utf-8") as f:
        return json.load(f)


def load_raw(name):
    with open(APERTURE / name, "rb") as f:
        return f.read()


def build_authority(common, whole):
    return {
        "profile": common["profile"],
        "semantic_implementation_sha": common["semantic_implementation_sha"],
        "policy_sha256": common["policy_sha256"],
        "policy_resolver_commit_sha": common["policy_resolver_commit_sha"],
        "whole_object_sha256": whole,
    }


def _normalize_test(obj):
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


def recanonicalize(mut_obj):
    """Recompute result_set_id + canonical bytes for a mutated object."""
    tmp = copy.deepcopy(mut_obj)
    tmp.pop("result_set_id", None)
    norm_local = _normalize_test(tmp)
    local_bytes = json.dumps(norm_local, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
    rsid = "sha256:" + hashlib.sha256(local_bytes).hexdigest()
    tmp["result_set_id"] = rsid
    norm_full = _normalize_test(tmp)
    full_bytes = json.dumps(norm_full, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
    return full_bytes, rsid


def parse_loose(raw: bytes):
    return json.loads(raw.decode("utf-8"))


class ConsumerBPrereveal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.indexes = load_json("CONTRACT_B_INDEXES.json")
        cls.auth = load_json("AUTHORITIES.json")
        cls.common = cls.auth["common"]
        cls.raw = {}
        cls.obj = {}
        for key, meta in cls.auth["handoffs"].items():
            r = load_raw(meta["file"])
            cls.raw[key] = r
            cls.obj[key] = parse_loose(r)

    def authority_for(self, key, whole_override=None):
        whole = whole_override or self.auth["handoffs"][key]["whole_object_sha256"]
        return build_authority(self.common, whole)

    def index_for(self, key):
        return copy.deepcopy(self.indexes[self.auth["handoffs"][key]["contract_b_index"]])

    # ---- valid handoffs ----

    def test_valid_independent_supports(self):
        raw = self.raw["independent_supports"]
        idx = self.index_for("independent_supports")
        auth = self.authority_for("independent_supports")
        out = consume_contract_c(raw, idx, auth)
        self.assertEqual(out["profile"], "contract-c-successor-candidate-a-rc2-research")
        self.assertEqual(out["result_set_id"], "sha256:0bab353e8c2ed35c49f9cc006aeca9f7920b0b11568026aece0bd03a37fa7011")
        self.assertEqual(out["contract_b"]["bundle_id"], "bundle-sp03")
        p = out["propositions"][0]
        self.assertEqual(p["terminal"], {"reason": "categorical_support", "verdict": "supported"})
        self.assertEqual(p["execution"], {"completion": "assessed", "state": "completed"})
        # two independent alternatives retained, no winner
        self.assertEqual(len(p["basis_groups"]), 2)
        sizes = sorted(len(g) for g in p["basis_groups"])
        self.assertEqual(sizes, [1, 1])
        rels = sorted(x["relation"] for x in p["participants"])
        self.assertEqual(rels, ["supports", "supports"])
        roles = sorted(x["role"] for x in p["participants"])
        self.assertEqual(roles, ["causal", "causal"])
        blob = json.dumps(out, sort_keys=True)
        for bad in FORBIDDEN_SUBSTRINGS:
            self.assertNotIn('"%s"' % bad, blob)

    def test_valid_alternative_joint_mixed(self):
        raw = self.raw["alternative_joint_mixed"]
        idx = self.index_for("alternative_joint_mixed")
        auth = self.authority_for("alternative_joint_mixed")
        out = consume_contract_c(raw, idx, auth)
        p = out["propositions"][0]
        self.assertEqual(p["terminal"], {"reason": "MIXED_RELATIONS", "verdict": "not_checkable"})
        self.assertEqual(len(p["basis_groups"]), 2)
        for g in p["basis_groups"]:
            self.assertEqual(len(g), 2)
        # each joint group has one supports and one refutes
        by_ref = {(x["evidence_ref"]["source_id"], x["evidence_ref"]["passage_id"]): x for x in p["participants"]}
        for g in p["basis_groups"]:
            rels = sorted(by_ref[(m["source_id"], m["passage_id"])]["relation"] for m in g)
            self.assertEqual(rels, ["refutes", "supports"])

    def test_valid_no_deciding(self):
        raw = self.raw["no_deciding"]
        idx = self.index_for("no_deciding")
        auth = self.authority_for("no_deciding")
        out = consume_contract_c(raw, idx, auth)
        p = out["propositions"][0]
        self.assertEqual(p["terminal"], {"reason": "no_deciding_relation", "verdict": "not_checkable"})
        self.assertEqual(p["basis_groups"], [])
        self.assertEqual(len(p["participants"]), 1)
        self.assertEqual(p["participants"][0]["relation"], "non_polarized")
        self.assertEqual(p["participants"][0]["role"], "residual")

    def test_valid_unsupported_family(self):
        raw = self.raw["unsupported_family"]
        idx = self.index_for("unsupported_family")
        auth = self.authority_for("unsupported_family")
        out = consume_contract_c(raw, idx, auth)
        p = out["propositions"][0]
        self.assertEqual(p["terminal"], {"reason": "UNSUPPORTED_SEMANTIC_FAMILY", "verdict": "not_checkable"})
        self.assertEqual(p["basis_groups"], [])
        for part in p["participants"]:
            self.assertEqual(part["relation"], "non_polarized")
            self.assertEqual(part["role"], "residual")

    def test_no_deciding_vs_unsupported_distinct(self):
        out_nd = consume_contract_c(self.raw["no_deciding"], self.index_for("no_deciding"), self.authority_for("no_deciding"))
        out_uf = consume_contract_c(self.raw["unsupported_family"], self.index_for("unsupported_family"), self.authority_for("unsupported_family"))
        self.assertNotEqual(
            out_nd["propositions"][0]["terminal"]["reason"],
            out_uf["propositions"][0]["terminal"]["reason"],
        )
        self.assertEqual(out_nd["propositions"][0]["terminal"]["reason"], "no_deciding_relation")
        self.assertEqual(out_uf["propositions"][0]["terminal"]["reason"], "UNSUPPORTED_SEMANTIC_FAMILY")

    def test_valid_failed_result_set_synthetic(self):
        # failed result-set with zero propositions is coherent per SPEC section 2.
        base = parse_loose(self.raw["independent_supports"])
        mut = copy.deepcopy(base)
        mut["execution"] = {"state": "failed"}
        mut["propositions"] = []
        raw2, _ = recanonicalize(mut)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        idx = self.index_for("independent_supports")
        auth = self.authority_for("independent_supports", whole_override=whole2)
        out = consume_contract_c(raw2, idx, auth)
        self.assertEqual(out["execution"], {"state": "failed"})
        self.assertEqual(out["propositions"], [])

    # ---- malformed / metamorphic ----

    def test_wrong_profile(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["profile"] = "contract-c-wrong"
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_unknown_top_level_field_destination_injection(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["authorization"] = {"decision": "CLEAR"}
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_unknown_nested_field_confidence(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["participants"][0]["confidence"] = 0.99
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_stale_result_set_id(self):
        raw = self.raw["independent_supports"]
        obj = parse_loose(raw)
        bad = obj["result_set_id"][:-1] + ("0" if obj["result_set_id"][-1] != "0" else "1")
        obj["result_set_id"] = bad
        # re-serialize canonically with the wrong id so bytes are canonical-shaped but id is stale
        norm = _normalize_test(obj)
        raw2 = json.dumps(norm, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports"))

    def test_non_canonical_pretty_print(self):
        obj = parse_loose(self.raw["independent_supports"])
        raw2 = json.dumps(obj, indent=2, sort_keys=True).encode("utf-8") + b"\n"
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports"))

    def test_non_canonical_unsorted_participants(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        # swap participant order; keep original rsid bytes shape by hand-serializing without normalization
        parts = base["propositions"][0]["participants"]
        base["propositions"][0]["participants"] = [parts[1], parts[0]]
        # keep original result_set_id (now stale for this ordering) but serialize canonically w.r.t. keys only
        raw2 = json.dumps(base, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"\n"
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports"))

    def test_wrong_whole_object_digest(self):
        raw = self.raw["independent_supports"]
        bad_auth = self.authority_for("independent_supports", whole_override="sha256:" + "0" * 64)
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw, self.index_for("independent_supports"), bad_auth)

    def test_wrong_contract_b_tuple(self):
        raw = self.raw["independent_supports"]
        idx = self.index_for("independent_supports")
        idx["bundle_id"] = "bundle-tampered"
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw, idx, self.authority_for("independent_supports"))

    def test_proposition_substitution(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["proposition"]["content_sha256"] = "sha256:" + "f" * 64
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_evidence_reference_absent(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["participants"].append({
            "evidence_ref": {"source_id": "src-ghost", "passage_id": "GHOST"},
            "relation": "supports", "role": "causal",
        })
        base["propositions"][0]["basis_groups"].append([{"source_id": "src-ghost", "passage_id": "GHOST"}])
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_wrong_producer_identity(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["producer"]["policy_sha256"] = "0" * 64
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_wrong_resolver_identity(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["producer"]["policy_resolver_commit_sha"] = "0" * 40
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_duplicate_participants(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        dup = copy.deepcopy(base["propositions"][0]["participants"][0])
        base["propositions"][0]["participants"].append(dup)
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_duplicate_basis_member(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["basis_groups"] = [[{"source_id": "src-s1", "passage_id": "S1"}, {"source_id": "src-s1", "passage_id": "S1"}]]
        base["propositions"][0]["participants"] = [base["propositions"][0]["participants"][0]]
        base["propositions"][0]["terminal"] = {"verdict": "supported", "reason": "categorical_support"}
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_duplicate_equivalent_basis_group(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        s1 = {"source_id": "src-s1", "passage_id": "S1"}
        base["propositions"][0]["basis_groups"] = [[s1], [dict(s1)]]
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_unknown_basis_participant(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["basis_groups"][0].append({"source_id": "src-s1", "passage_id": "S1"})
        # second group references S1 which is retained, but add ghost to first group via duplicate? Instead add ghost member:
        base["propositions"][0]["basis_groups"][0] = [{"source_id": "src-s1", "passage_id": "S1"}, {"source_id": "src-x", "passage_id": "SX"}]
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_residual_in_basis(self):
        base = copy.deepcopy(self.obj["no_deciding"])
        base["propositions"][0]["basis_groups"] = [[{"source_id": "src-n1", "passage_id": "N1"}]]
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("no_deciding"), self.authority_for("no_deciding", whole_override=whole2))

    def test_causal_omitted_from_coverage(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["basis_groups"] = [[{"source_id": "src-s1", "passage_id": "S1"}]]
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_non_minimal_superset(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["basis_groups"] = [
            [{"source_id": "src-s1", "passage_id": "S1"}],
            [{"source_id": "src-s1", "passage_id": "S1"}, {"source_id": "src-s2", "passage_id": "S2"}],
        ]
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_relation_terminal_incoherence(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        for part in base["propositions"][0]["participants"]:
            part["relation"] = "refutes"
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_execution_terminal_laundering(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["execution"] = {"state": "failed", "completion": None}
        # keep terminal non-null to launder
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_non_polarized_laundering(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["participants"][1]["relation"] = "non_polarized"
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_winner_deletion_fails_original_digest(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["participants"] = [base["propositions"][0]["participants"][0]]
        base["propositions"][0]["basis_groups"] = [[{"source_id": "src-s1", "passage_id": "S1"}]]
        raw2, _ = recanonicalize(base)
        # keep ORIGINAL authority digest: deletion + recomputed rsid is still a different object
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports"))

    def test_reason_case_folding_rejected(self):
        base = copy.deepcopy(self.obj["alternative_joint_mixed"])
        base["propositions"][0]["terminal"]["reason"] = "mixed_relations"
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("alternative_joint_mixed"), self.authority_for("alternative_joint_mixed", whole_override=whole2))

    def test_reason_substitution_incoherent(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["propositions"][0]["terminal"] = {"verdict": "not_checkable", "reason": "MIXED_RELATIONS"}
        base["propositions"][0]["execution"] = {"state": "completed", "completion": "not_checkable"}
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_mixed_with_non_polarized_rejected(self):
        base = copy.deepcopy(self.obj["alternative_joint_mixed"])
        # index has no non_polarized passage; reuse R1 but flip its relation to non_polarized
        for part in base["propositions"][0]["participants"]:
            if part["evidence_ref"]["passage_id"] == "R1":
                part["relation"] = "non_polarized"
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("alternative_joint_mixed"), self.authority_for("alternative_joint_mixed", whole_override=whole2))

    def test_duplicate_keys_rejected(self):
        raw = self.raw["independent_supports"]
        text = raw.decode("utf-8")
        # inject a duplicate top-level key before final brace
        dup_raw = text[:-2] + ', "profile":"tampered"}' + "\n"
        with self.assertRaises(ConsumerError):
            consume_contract_c(dup_raw.encode("utf-8"), self.index_for("independent_supports"), self.authority_for("independent_supports"))

    def test_trailing_data_rejected(self):
        raw = self.raw["independent_supports"]
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw + b"{}", self.index_for("independent_supports"), self.authority_for("independent_supports"))

    def test_non_finite_constant_rejected(self):
        raw = self.raw["independent_supports"]
        text = raw.decode("utf-8")
        bad = text.replace('"completed"', 'NaN', 1)
        self.assertNotEqual(bad, text)
        with self.assertRaises(ConsumerError):
            consume_contract_c(bad.encode("utf-8"), self.index_for("independent_supports"), self.authority_for("independent_supports"))

    def test_failed_result_set_with_propositions_rejected(self):
        base = copy.deepcopy(self.obj["independent_supports"])
        base["execution"] = {"state": "failed"}
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("independent_supports"), self.authority_for("independent_supports", whole_override=whole2))

    def test_unsupported_reason_case_variant_rejected(self):
        base = copy.deepcopy(self.obj["unsupported_family"])
        base["propositions"][0]["terminal"]["reason"] = "unsupported_semantic_family"
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("unsupported_family"), self.authority_for("unsupported_family", whole_override=whole2))

    def test_no_deciding_spelling_variant_rejected(self):
        base = copy.deepcopy(self.obj["no_deciding"])
        base["propositions"][0]["terminal"]["reason"] = "NO_DECIDING_RELATION"
        raw2, _ = recanonicalize(base)
        whole2 = "sha256:" + hashlib.sha256(raw2).hexdigest()
        with self.assertRaises(ConsumerError):
            consume_contract_c(raw2, self.index_for("no_deciding"), self.authority_for("no_deciding", whole_override=whole2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
