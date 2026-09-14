from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from contract_c_successor import canonical_bytes, result_set_identity, validate_contract_c_bytes

A, B, C, D, E = (c * 64 for c in "abcde")
S40 = "1" * 40
CA, CB, CC = ("contribution:" + x for x in (A, B, C))


def pol(payload=None):
    payload = {"mode": "strict", "unicode": "café"} if payload is None else payload
    return {"canonical": payload, "sha256": hashlib.sha256(canonical_bytes(payload)).hexdigest()}


def contrib(cid=CA, channel="support", passage="p-a", source="s-a", digest=C):
    return {"contribution_id": cid, "channel": channel, "evidence_ref": {"source_id": source, "passage_id": passage, "passage_sha256": "sha256:" + digest}}


def slots():
    return {
        "eligibility": {"state": "performed", "value": "unknown"},
        "semantic_validity": {"state": "not_performed"},
        "aperture_completeness": {"state": "not_applicable"},
        "temporal_applicability": {"state": "failed"},
    }


def prop(cs=None, *, pid="prop-a", completion="assessed", verdict="supported", form="single_necessary", basis=None, residuals=None, roles=None, measurement=None):
    cs = [contrib()] if cs is None else cs
    basis = ([{"namespace": "contribution", "id": cs[0]["contribution_id"]}] if cs else []) if basis is None else basis
    if residuals is None:
        causal = {m["id"] for m in basis if m.get("namespace") == "contribution"}
        residuals = [c["contribution_id"] for c in cs if c["contribution_id"] not in causal]
    return {
        "proposition": {"proposition_id": pid, "text_sha256": B},
        "execution": {"state": "completed", "completion": completion},
        "assessments": slots(),
        "contributions": cs,
        "measurement": measurement,
        "conclusion": {"reported_verdict": verdict, "terminal_branch": "terminal", "causal_form": form, "basis_members": basis, "residual_contribution_ids": residuals, "rule_roles": [] if roles is None else roles},
    }


def obj(props=None, state="completed"):
    value = {
        "contract_c_version": "research-contract-c-successor-rc1",
        "input": {"contract_b": {"contract_version": "contract-b-test", "bundle_id": "bundle-a", "bundle_hash": "sha256:" + A}},
        "producer": {"semantic_implementation_sha": S40, "policy": pol()},
        "execution": {"state": state},
        "propositions": [prop()] if props is None else props,
        "result_set_id": "result-set:" + "0" * 64,
    }
    value["result_set_id"] = result_set_identity(value)
    return value


def wire(value):
    value = copy.deepcopy(value)
    value["result_set_id"] = result_set_identity(value)
    return canonical_bytes(value)


def index(value):
    propositions, passages = {}, {}
    for p in value["propositions"]:
        propositions[p["proposition"]["proposition_id"]] = p["proposition"]["text_sha256"]
        for c in p["contributions"]:
            r = c["evidence_ref"]
            passages[r["passage_id"]] = {"source_id": r["source_id"], "passage_sha256": r["passage_sha256"]}
    b = value["input"]["contract_b"]
    return {"contract_version": b["contract_version"], "bundle_id": b["bundle_id"], "bundle_hash": b["bundle_hash"], "propositions": propositions, "passages": passages}


class Tests(unittest.TestCase):
    def bad(self, data, **kwargs):
        errors = validate_contract_c_bytes(data, **kwargs)
        self.assertTrue(errors)
        return errors

    def test_valid_canonical_and_exact_version(self):
        self.assertEqual(validate_contract_c_bytes(wire(obj())), [])
        value = obj(); value["contract_c_version"] = "1.0.0"
        self.bad(wire(value))

    def test_three_channels_and_mixed_channel_roles(self):
        for channel in ("support", "counterevidence", "non_deciding"):
            with self.subTest(channel=channel):
                self.assertEqual(validate_contract_c_bytes(wire(obj([prop([contrib(channel=channel)])]))), [])
        cs = [contrib(CA, "support"), contrib(CB, "counterevidence", "p-b", "s-b", D), contrib(CC, "non_deciding", "p-c", "s-c", E)]
        p = prop(cs, form="jointly_sufficient", basis=[{"namespace": "contribution", "id": CB}, {"namespace": "contribution", "id": CC}], residuals=[CA])
        self.assertEqual(validate_contract_c_bytes(wire(obj([p]))), [])

    def test_neutral_causal_residual_and_independent_sufficient_multiplicity(self):
        self.assertEqual(validate_contract_c_bytes(wire(obj([prop([contrib(channel="non_deciding")])]))), [])
        cs = [contrib(CA, "support"), contrib(CB, "non_deciding", "p-b", "s-b", D)]
        p = prop(cs, basis=[{"namespace": "contribution", "id": CA}], residuals=[CB])
        self.assertEqual(validate_contract_c_bytes(wire(obj([p]))), [])
        basis = [{"namespace": "contribution", "id": CA}, {"namespace": "contribution", "id": CB}]
        p = prop([contrib(CA, "non_deciding"), contrib(CB, "non_deciding", "p-b", "s-b", D)], form="independent_sufficient_alternatives", basis=basis, residuals=[])
        self.assertEqual(validate_contract_c_bytes(wire(obj([p]))), [])

    def test_execution_conclusion_and_not_checkable(self):
        for state in ("failed", "incomplete"):
            p = prop(); p["execution"] = {"state": state}; p["conclusion"] = None
            self.assertEqual(validate_contract_c_bytes(wire(obj([p], state=state))), [])
            p["conclusion"] = prop()["conclusion"]
            self.bad(wire(obj([p], state=state)))
        p = prop(); p["conclusion"] = None
        self.bad(wire(obj([p])))
        self.assertEqual(validate_contract_c_bytes(wire(obj([prop(completion="not_checkable", verdict="not_checkable")]))), [])
        self.bad(wire(obj([prop(completion="not_checkable", verdict="x")])))
        self.bad(wire(obj([prop(completion="assessed", verdict="not_checkable")])))

    def test_result_execution_nonempty_rule_and_recorded_cross_level_interpretation(self):
        self.bad(wire(obj([], state="completed")))
        self.assertEqual(validate_contract_c_bytes(wire(obj([], state="failed"))), [])
        p = prop(); p["execution"] = {"state": "failed"}; p["conclusion"] = None
        self.assertEqual(validate_contract_c_bytes(wire(obj([p], state="completed"))), [])

    def test_identity_uniqueness(self):
        self.bad(wire(obj([prop(), prop()])))
        cs = [contrib(CA), contrib(CA, "counterevidence", "p-b", "s-b", D)]
        self.bad(wire(obj([prop(cs, residuals=[CA])])))
        p = prop(form="jointly_sufficient", basis=[{"namespace": "contribution", "id": CA}, {"namespace": "contribution", "id": CA}], residuals=[])
        self.bad(wire(obj([p])))
        p = prop([contrib(CA), contrib(CB, "non_deciding", "p-b", "s-b", D)], basis=[{"namespace": "contribution", "id": CA}], residuals=[CB, CB])
        self.bad(wire(obj([p])))
        rule = {"rule_id": "rule-role:x", "code": "X", "terminal_role": "causal"}
        p = prop(form="jointly_sufficient", basis=[{"namespace": "contribution", "id": CA}, {"namespace": "rule", "id": "rule-role:x"}], residuals=[], roles=[rule, copy.deepcopy(rule)])
        self.bad(wire(obj([p])))

    def test_classification_completeness_disjointness_and_reference_integrity(self):
        cs = [contrib(CA), contrib(CB, "non_deciding", "p-b", "s-b", D)]
        self.bad(wire(obj([prop(cs, basis=[{"namespace": "contribution", "id": CA}], residuals=[])])))
        self.bad(wire(obj([prop(residuals=[CA])])))
        self.bad(wire(obj([prop(residuals=[CB])])))
        self.bad(wire(obj([prop(basis=[{"namespace": "contribution", "id": CB}], residuals=[CA])])))

    def test_causal_cardinality_and_prefixes(self):
        self.bad(wire(obj([prop(form="single_necessary", basis=[], residuals=[CA])])))
        self.bad(wire(obj([prop(form="independent_sufficient_alternatives")])))
        self.bad(wire(obj([prop(form="jointly_sufficient")])))
        self.bad(wire(obj([prop(form="redundant_non_deciding", residuals=[])])))
        self.assertEqual(validate_contract_c_bytes(wire(obj([prop(form="redundant_non_deciding", basis=[], residuals=[CA])]))), [])
        self.bad(wire(obj([prop(basis=[{"namespace": "state", "id": "bad"}], residuals=[CA])])))

    def test_measurement_reference_integrity(self):
        m = {"kind": "score", "value": 1.25, "basis_contribution_ids": [CA]}
        self.assertEqual(validate_contract_c_bytes(wire(obj([prop(measurement=m)]))), [])
        for basis in ([CB], [CA, CA], []):
            with self.subTest(basis=basis):
                mm = {"kind": "score", "value": None, "basis_contribution_ids": basis}
                self.bad(wire(obj([prop(measurement=mm)])))
        self.bad(wire(obj([prop(measurement={"kind": "score", "value": True, "basis_contribution_ids": [CA]})])))

    def test_rule_role_integrity_and_recorded_converse_interpretation(self):
        basis = [{"namespace": "contribution", "id": CA}, {"namespace": "rule", "id": "rule-role:r1"}]
        causal = [{"rule_id": "rule-role:r1", "code": "R1", "terminal_role": "causal"}]
        self.assertEqual(validate_contract_c_bytes(wire(obj([prop(form="jointly_sufficient", basis=basis, residuals=[], roles=causal)]))), [])
        self.bad(wire(obj([prop(form="jointly_sufficient", basis=basis, residuals=[], roles=[])])))
        residual = [{"rule_id": "rule-role:r1", "code": "R1", "terminal_role": "residual"}]
        self.bad(wire(obj([prop(form="jointly_sufficient", basis=basis, residuals=[], roles=residual)])))
        unused = [{"rule_id": "rule-role:unused", "code": "U", "terminal_role": "causal"}]
        self.assertEqual(validate_contract_c_bytes(wire(obj([prop(roles=unused)]))), [])

    def test_exact_contract_b_binding(self):
        value = obj(); idx = index(value)
        self.assertEqual(validate_contract_c_bytes(wire(value), contract_b_index=idx), [])
        for mutate in ("top", "prop", "source", "hash", "missing"):
            bad = copy.deepcopy(idx)
            if mutate == "top": bad["bundle_id"] = "other"
            elif mutate == "prop": bad["propositions"]["prop-a"] = E
            elif mutate == "source": bad["passages"]["p-a"]["source_id"] = "other"
            elif mutate == "hash": bad["passages"]["p-a"]["passage_sha256"] = "sha256:" + D
            else: del bad["passages"]["p-a"]
            with self.subTest(mutate=mutate): self.bad(wire(value), contract_b_index=bad)
        bad = copy.deepcopy(idx); bad["extra"] = 1
        self.bad(wire(value), contract_b_index=bad)

    def test_policy_hash_binding_and_opaque_payload(self):
        value = obj(); value["producer"]["policy"]["sha256"] = E
        self.bad(wire(value))
        value = obj(); value["producer"]["policy"] = pol({"arbitrary": {"nested": [1, "x", None, True]}, "Ω": "λ"})
        self.assertEqual(validate_contract_c_bytes(wire(value)), [])
        payload = {"a": 1}; value = obj(); value["producer"]["policy"] = {"canonical": payload, "sha256": hashlib.sha256(canonical_bytes(payload)[:-1]).hexdigest()}
        self.bad(wire(value))

    def test_result_set_identity_and_external_exact_sha(self):
        value = obj(); data = wire(value)
        self.assertEqual(value["result_set_id"], result_set_identity(value))
        bad = copy.deepcopy(value); bad["result_set_id"] = "result-set:" + E
        self.bad(canonical_bytes(bad))
        digest = hashlib.sha256(data).hexdigest()
        self.assertEqual(validate_contract_c_bytes(data, expected_sha256=digest), [])
        self.assertEqual(validate_contract_c_bytes(data, expected_sha256="sha256:" + digest), [])
        self.bad(data, expected_sha256=E)
        self.bad(data, expected_sha256=digest.upper())

    def test_canonical_json_bytes(self):
        value = {"z": 1, "é": "雪", "a": {"b": 2, "a": 1}}
        self.assertEqual(canonical_bytes(value), '{"a":{"a":1,"b":2},"z":1,"é":"雪"}\n'.encode())
        valid = obj()
        noncanonical = [
            json.dumps(valid, ensure_ascii=False, sort_keys=False, separators=(",", ":")).encode() + b"\n",
            json.dumps(valid, ensure_ascii=False, sort_keys=True, indent=2).encode() + b"\n",
            wire(valid)[:-1], wire(valid) + b"\n",
            json.dumps(valid, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode() + b"\n",
        ]
        for data in noncanonical:
            with self.subTest(data=data[:20]): self.bad(data)

    def test_array_order_is_identity_not_silently_sorted(self):
        cs1 = [contrib(CA), contrib(CB, "non_deciding", "p-b", "s-b", D)]
        cs2 = list(reversed(copy.deepcopy(cs1)))
        p1 = prop(cs1, basis=[{"namespace": "contribution", "id": CA}], residuals=[CB])
        p2 = prop(cs2, basis=[{"namespace": "contribution", "id": CA}], residuals=[CB])
        a, b = obj([p1]), obj([p2])
        self.assertNotEqual(a["result_set_id"], b["result_set_id"])
        self.assertEqual(validate_contract_c_bytes(wire(a)), [])
        self.assertEqual(validate_contract_c_bytes(wire(b)), [])

    def test_duplicate_keys_malformed_utf8_nonfinite(self):
        bads = [
            b'{"x":1,"x":2}\n', b'{"x":]\n', b"\xff\xfe",
            b'{"x":NaN}\n', b'{"x":Infinity}\n', b'{"x":-Infinity}\n',
        ]
        for data in bads:
            with self.subTest(data=data): self.bad(data)

    def test_unknown_fields_and_vocabularies(self):
        value = obj(); value["extra"] = 1; self.bad(wire(value))
        value = obj(); value["propositions"][0]["conclusion"]["extra"] = 1; self.bad(wire(value))
        value = obj(); value["propositions"][0]["contributions"][0]["channel"] = "neutral"; self.bad(wire(value))
        value = obj(); value["propositions"][0]["conclusion"]["causal_form"] = "mystery"; self.bad(wire(value))
        value = obj(); value["propositions"][0]["assessments"]["eligibility"] = {"state": "performed", "value": "good"}; self.bad(wire(value))

    def test_no_downgrade_and_exact_hash_vocabularies(self):
        value = obj(); value["contract_c_version"] = "1.0.0"; self.bad(wire(value))
        value = obj(); value["propositions"][0]["proposition"]["text_sha256"] = B.upper(); self.bad(wire(value))
        value = obj(); value["propositions"][0]["contributions"][0]["contribution_id"] = "contribution:x"; value["propositions"][0]["conclusion"]["basis_members"][0]["id"] = "contribution:x"; self.bad(wire(value))

    def test_result_identity_removes_only_top_level_field(self):
        value = obj(); nested = copy.deepcopy(value)
        nested["producer"]["policy"]["canonical"]["result_set_id"] = "nested"
        nested["producer"]["policy"] = pol(nested["producer"]["policy"]["canonical"])
        nested["result_set_id"] = result_set_identity(nested)
        self.assertNotEqual(value["result_set_id"], nested["result_set_id"])
        self.assertEqual(validate_contract_c_bytes(canonical_bytes(nested)), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
