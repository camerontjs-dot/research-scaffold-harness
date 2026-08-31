from __future__ import annotations

from copy import deepcopy
import json
import unittest

from contract_d_independent import (
    ABSENT,
    ContractDError,
    OUTCOME_CANDIDATE,
    OUTCOME_CANNOT_ESTABLISH,
    OUTCOME_FAILED,
    OUTCOME_HOLD,
    OUTCOME_NOT_APPLICABLE,
    authority_projection,
    canonical_json_bytes,
    consume,
    consume_json_bytes,
    normalize_effect,
    parse_json_bytes,
    semantic_identity,
    validate_decision,
)
import weak_consumers

H = "sha256:" + "1" * 64
H2 = "sha256:" + "2" * 64

SOURCE_CLEAR = {
    "contract_d_version": "0.3.0-rc4",
    "effect": {"params": {"scope": "claim"}, "type": "knowledge.add_verified_tag", "version": "1"},
    "evaluation": {"disposition": "clear", "state": "completed"},
    "input_authority": {"id": "c1", "immutable_id": "result-set:" + "a" * 64, "kind": "contract-c"},
    "metadata": {"diagnostics": {"trace": "fixture"}, "explanation": "Research fixture", "reason_codes": ["policy_clear"]},
    "policy": {"id": "mainframe.source-audit", "version": "1"},
    "target": {"content_sha256": H, "id": "k1", "kind": "knowledge"},
}
OBJECT_CLEAR = {
    "contract_d_version": "0.3.0-rc4",
    "effect": {"params": {"scope": "object"}, "type": "knowledge.add_verified_tag", "version": "1"},
    "evaluation": {"disposition": "clear", "state": "completed"},
    "input_authority": {"id": "c5", "immutable_id": "result-set:" + "f" * 64, "kind": "contract-c"},
    "policy": {"id": "mainframe.source-audit", "version": "1"},
    "target": {"content_sha256": H, "id": "k5", "kind": "knowledge"},
}
CITATION_CLEAR = {
    "contract_d_version": "0.3.0-rc4",
    "effect": {"type": "knowledge.cite_as_evidence", "version": "1"},
    "evaluation": {"disposition": "clear", "state": "completed"},
    "input_authority": {"id": "c2", "immutable_id": "result-set:" + "b" * 64, "kind": "contract-c"},
    "policy": {"id": "mainframe.citation-use", "version": "1"},
    "target": {"content_sha256": H, "id": "k2", "kind": "knowledge"},
}
TASK_CLEAR = {
    "contract_d_version": "0.3.0-rc4",
    "effect": {"type": "task.dispatch", "version": "1"},
    "evaluation": {"disposition": "clear", "state": "completed"},
    "input_authority": {"id": "r1", "immutable_id": "task-review:" + "c" * 64, "kind": "task-review"},
    "policy": {"id": "mainframe.task-dispatch", "version": "1"},
    "target": {"content_sha256": H, "id": "t1", "kind": "task"},
}
HOLD = {
    "contract_d_version": "0.3.0-rc4",
    "effect": {"type": "knowledge.add_verified_tag", "version": "1"},
    "evaluation": {"disposition": "hold", "state": "completed"},
    "input_authority": {"id": "c3", "immutable_id": "result-set:" + "d" * 64, "kind": "contract-c"},
    "policy": {"id": "mainframe.source-audit", "version": "1"},
    "target": {"content_sha256": H, "id": "k3", "kind": "knowledge"},
}
FAILED = {
    "contract_d_version": "0.3.0-rc4",
    "evaluation": {"state": "failed"},
    "input_authority": {"id": "c4", "immutable_id": "result-set:" + "e" * 64, "kind": "contract-c"},
    "metadata": {"reason_codes": ["policy_evaluation_failure"]},
    "policy": {"id": "mainframe.source-audit", "version": "1"},
    "target": {"content_sha256": H, "id": "k4", "kind": "knowledge"},
}


def ctx(decision, operation=None, params=ABSENT):
    out = {
        "expected_upstream": deepcopy(decision["input_authority"]),
        "expected_policy": deepcopy(decision["policy"]),
        "expected_target": deepcopy(decision["target"]),
        "requested_operation": operation,
    }
    if params is not ABSENT:
        out["requested_effect_params"] = params
    return out


class PositiveAndPublicCases(unittest.TestCase):
    def test_source_audit_clear(self):
        self.assertEqual(consume(SOURCE_CLEAR, **ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope": "claim"})), OUTCOME_CANDIDATE)

    def test_citation_use_clear(self):
        self.assertEqual(consume(CITATION_CLEAR, **ctx(CITATION_CLEAR, "knowledge.cite_as_evidence")), OUTCOME_CANDIDATE)

    def test_task_dispatch_clear(self):
        self.assertEqual(consume(TASK_CLEAR, **ctx(TASK_CLEAR, "task.dispatch")), OUTCOME_CANDIDATE)

    def test_completed_hold(self):
        self.assertEqual(consume(HOLD, **ctx(HOLD, "knowledge.add_verified_tag")), OUTCOME_HOLD)

    def test_evaluation_failure(self):
        self.assertEqual(consume(FAILED, **ctx(FAILED, "knowledge.add_verified_tag")), OUTCOME_FAILED)

    def test_hold_distinct_from_failure(self):
        self.assertNotEqual(consume(HOLD, **ctx(HOLD, "knowledge.add_verified_tag")), consume(FAILED, **ctx(FAILED, "knowledge.add_verified_tag")))

    def test_public_case_omitted_requested_params_unconstrained(self):
        self.assertEqual(consume(OBJECT_CLEAR, **ctx(OBJECT_CLEAR, "knowledge.add_verified_tag")), OUTCOME_CANDIDATE)

    def test_public_case_explicit_requested_param_conflict(self):
        self.assertEqual(consume(OBJECT_CLEAR, **ctx(OBJECT_CLEAR, "knowledge.add_verified_tag", {"scope": "claim"})), OUTCOME_NOT_APPLICABLE)

    def test_public_case_hold_operation_replay(self):
        self.assertEqual(consume(HOLD, **ctx(HOLD, "task.dispatch")), OUTCOME_NOT_APPLICABLE)

    def test_public_case_hold_positive(self):
        self.assertEqual(consume(HOLD, **ctx(HOLD, "knowledge.add_verified_tag")), OUTCOME_HOLD)

    def test_public_case_target_content_replay(self):
        c = ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope": "claim"})
        c["expected_target"]["content_sha256"] = H2
        self.assertEqual(consume(SOURCE_CLEAR, **c), OUTCOME_NOT_APPLICABLE)


class RC4Discriminators(unittest.TestCase):
    def test_hold_different_requested_operation(self):
        self.assertEqual(consume(HOLD, **ctx(HOLD, "task.dispatch")), OUTCOME_NOT_APPLICABLE)

    def test_hold_conflicting_requested_parameter(self):
        self.assertEqual(consume(HOLD, **ctx(HOLD, "knowledge.add_verified_tag", {"scope": "object"})), OUTCOME_NOT_APPLICABLE)

    def test_hold_exact_operation_and_parameter(self):
        self.assertEqual(consume(HOLD, **ctx(HOLD, "knowledge.add_verified_tag", {"scope": "claim"})), OUTCOME_HOLD)

    def test_object_scope_no_external_params(self):
        self.assertEqual(consume(OBJECT_CLEAR, **ctx(OBJECT_CLEAR, "knowledge.add_verified_tag")), OUTCOME_CANDIDATE)

    def test_object_scope_empty_external_params(self):
        self.assertEqual(consume(OBJECT_CLEAR, **ctx(OBJECT_CLEAR, "knowledge.add_verified_tag", {})), OUTCOME_CANDIDATE)

    def test_object_scope_explicit_claim(self):
        self.assertEqual(consume(OBJECT_CLEAR, **ctx(OBJECT_CLEAR, "knowledge.add_verified_tag", {"scope": "claim"})), OUTCOME_NOT_APPLICABLE)

    def test_object_scope_explicit_object(self):
        self.assertEqual(consume(OBJECT_CLEAR, **ctx(OBJECT_CLEAR, "knowledge.add_verified_tag", {"scope": "object"})), OUTCOME_CANDIDATE)

    def test_invalid_utf8(self):
        self.assertEqual(consume_json_bytes(b'{"contract_d_version":"0.3.0-rc4","x":"\xff"}', **ctx(SOURCE_CLEAR, "knowledge.add_verified_tag")), OUTCOME_CANNOT_ESTABLISH)

    def test_duplicate_json_keys(self):
        raw = b'{"contract_d_version":"0.3.0-rc4","contract_d_version":"0.3.0-rc4"}'
        with self.assertRaises(ContractDError):
            parse_json_bytes(raw)

    def test_nonfinite_json_number(self):
        with self.assertRaises(ContractDError):
            parse_json_bytes(b'{"x":NaN}')
        with self.assertRaises(ContractDError):
            parse_json_bytes(b'{"x":Infinity}')

    def test_host_language_only_diagnostics(self):
        d = deepcopy(SOURCE_CLEAR)
        d["metadata"]["diagnostics"] = {"bad": {1, 2}}
        self.assertEqual(consume(d, **ctx(SOURCE_CLEAR, "knowledge.add_verified_tag")), OUTCOME_CANNOT_ESTABLISH)

    def test_nonstring_object_key(self):
        d = deepcopy(SOURCE_CLEAR)
        d["metadata"]["diagnostics"] = {1: "bad"}
        self.assertEqual(consume(d, **ctx(SOURCE_CLEAR, "knowledge.add_verified_tag")), OUTCOME_CANNOT_ESTABLISH)


class ValidationAndUnknowns(unittest.TestCase):
    def test_exact_version_only(self):
        for bad in ["0.3.0-rc5", "0.3.0-RC4", 0.3, None]:
            d = deepcopy(SOURCE_CLEAR)
            d["contract_d_version"] = bad
            with self.assertRaises(ContractDError):
                validate_decision(d)

    def test_unknown_structural_field_top(self):
        d = deepcopy(SOURCE_CLEAR); d["actor"] = "root"
        with self.assertRaises(ContractDError): validate_decision(d)

    def test_unknown_structural_fields_nested(self):
        mutations = [
            ("input_authority", "actor"), ("policy", "approval"), ("target", "receipt"), ("evaluation", "future"), ("effect", "approval"), ("metadata", "actor")
        ]
        for section, field in mutations:
            d = deepcopy(SOURCE_CLEAR); d[section][field] = True
            with self.assertRaises(ContractDError, msg=f"{section}.{field}"):
                validate_decision(d)

    def test_unknown_evaluation_state(self):
        d = deepcopy(SOURCE_CLEAR); d["evaluation"]["state"] = "future"
        with self.assertRaises(ContractDError): validate_decision(d)

    def test_unknown_disposition(self):
        d = deepcopy(SOURCE_CLEAR); d["evaluation"]["disposition"] = "maybe"
        with self.assertRaises(ContractDError): validate_decision(d)

    def test_unknown_effect_type(self):
        d = deepcopy(SOURCE_CLEAR); d["effect"]["type"] = "future.effect"
        with self.assertRaises(ContractDError): validate_decision(d)

    def test_unknown_effect_version(self):
        d = deepcopy(SOURCE_CLEAR); d["effect"]["version"] = "2"
        with self.assertRaises(ContractDError): validate_decision(d)

    def test_unknown_effect_parameter(self):
        d = deepcopy(SOURCE_CLEAR); d["effect"]["params"]["actor"] = "root"
        with self.assertRaises(ContractDError): validate_decision(d)

    def test_failed_forbids_effect_and_disposition(self):
        d = deepcopy(FAILED); d["effect"] = deepcopy(SOURCE_CLEAR["effect"])
        with self.assertRaises(ContractDError): validate_decision(d)
        d = deepcopy(FAILED); d["evaluation"]["disposition"] = "hold"
        with self.assertRaises(ContractDError): validate_decision(d)

    def test_completed_requires_effect(self):
        d = deepcopy(SOURCE_CLEAR); d.pop("effect")
        with self.assertRaises(ContractDError): validate_decision(d)

    def test_target_hash_shape(self):
        d = deepcopy(SOURCE_CLEAR); d["target"]["content_sha256"] = "sha256:ABC"
        with self.assertRaises(ContractDError): validate_decision(d)

    def test_cycles_are_not_finite_json(self):
        d = deepcopy(SOURCE_CLEAR)
        cycle = []; cycle.append(cycle); d["metadata"]["diagnostics"] = cycle
        with self.assertRaises(ContractDError): validate_decision(d)


class NormalizationCanonicalizationIdentity(unittest.TestCase):
    def test_safe_default_normalization_equivalence(self):
        variants = []
        for effect in [
            {"type":"knowledge.add_verified_tag","version":"1"},
            {"type":"knowledge.add_verified_tag","version":"1","params":{}},
            {"type":"knowledge.add_verified_tag","version":"1","params":{"scope":"claim"}},
        ]:
            d = deepcopy(SOURCE_CLEAR); d["effect"] = effect; variants.append(d)
        ids = {semantic_identity(v) for v in variants}
        self.assertEqual(len(ids), 1)
        for v in variants:
            self.assertEqual(normalize_effect(v["effect"])["params"], {"scope":"claim"})

    def test_explicit_object_scope_changes_identity(self):
        claim = deepcopy(SOURCE_CLEAR)
        obj = deepcopy(SOURCE_CLEAR); obj["effect"]["params"]["scope"] = "object"
        self.assertNotEqual(semantic_identity(claim), semantic_identity(obj))

    def test_metadata_invariance(self):
        base = semantic_identity(SOURCE_CLEAR)
        variants = []
        d = deepcopy(SOURCE_CLEAR); d.pop("metadata"); variants.append(d)
        d = deepcopy(SOURCE_CLEAR); d["metadata"]["reason_codes"] = ["other"]; variants.append(d)
        d = deepcopy(SOURCE_CLEAR); d["metadata"]["explanation"] = "Different"; variants.append(d)
        d = deepcopy(SOURCE_CLEAR); d["metadata"]["diagnostics"] = {"unicode":"雪","n":3}; variants.append(d)
        for v in variants:
            self.assertEqual(semantic_identity(v), base)
            self.assertEqual(consume(v, **ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope":"claim"})), OUTCOME_CANDIDATE)

    def test_authorization_context_not_in_identity(self):
        contexts = [
            {"actor":"a", "approval":False},
            {"actor":"b", "approval":True, "delegation":"x", "execution_receipt":"r"},
        ]
        ids = [semantic_identity(SOURCE_CLEAR) for _ in contexts]
        self.assertEqual(ids[0], ids[1])

    def test_authorization_injection_into_decision_is_invalid(self):
        for field in ["actor", "approval", "delegation", "autonomy", "profile", "trust", "execution_permission", "execution_state", "execution_receipt"]:
            d = deepcopy(SOURCE_CLEAR); d[field] = "x"
            with self.assertRaises(ContractDError): validate_decision(d)

    def test_key_order_and_formatting_canonicalize_equal(self):
        a = {"z":1,"a":{"β":"雪","a":2}}
        b = {"a":{"a":2,"β":"雪"},"z":1}
        self.assertEqual(canonical_json_bytes(a), canonical_json_bytes(b))
        self.assertTrue(canonical_json_bytes(a).endswith(b"\n"))
        self.assertIn("雪".encode("utf-8"), canonical_json_bytes(a))

    def test_transport_whitespace_does_not_change_decision_identity(self):
        raw1 = json.dumps(SOURCE_CLEAR, ensure_ascii=False).encode()
        raw2 = json.dumps(SOURCE_CLEAR, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
        self.assertEqual(semantic_identity(parse_json_bytes(raw1)), semantic_identity(parse_json_bytes(raw2)))

    def test_authority_projection_excludes_metadata(self):
        self.assertNotIn("metadata", authority_projection(SOURCE_CLEAR))
        self.assertNotIn("effect", authority_projection(FAILED))

    def test_zero_param_effect_normalizes_to_empty_params_object(self):
        self.assertEqual(normalize_effect(CITATION_CLEAR["effect"]), {"type":"knowledge.cite_as_evidence","version":"1","params":{}})


class SensitivityReplayAndApplicability(unittest.TestCase):
    def test_authority_bearing_mutations_change_identity_when_still_valid(self):
        mutators = [
            lambda d: d["input_authority"].__setitem__("kind", "other-kind"),
            lambda d: d["input_authority"].__setitem__("id", "other-id"),
            lambda d: d["input_authority"].__setitem__("immutable_id", "result-set:" + "9"*64),
            lambda d: d["policy"].__setitem__("id", "other.policy"),
            lambda d: d["policy"].__setitem__("version", "2"),
            lambda d: d["target"].__setitem__("kind", "other-kind"),
            lambda d: d["target"].__setitem__("id", "other-id"),
            lambda d: d["target"].__setitem__("content_sha256", H2),
            lambda d: d["evaluation"].__setitem__("disposition", "hold"),
            lambda d: d["effect"]["params"].__setitem__("scope", "object"),
        ]
        base = semantic_identity(SOURCE_CLEAR)
        for mutate in mutators:
            d = deepcopy(SOURCE_CLEAR); mutate(d)
            self.assertNotEqual(semantic_identity(d), base)

    def test_contract_version_mutation_invalid_not_new_authority(self):
        d = deepcopy(SOURCE_CLEAR); d["contract_d_version"] = "0.3.0-rc5"
        self.assertEqual(consume(d, **ctx(SOURCE_CLEAR, "knowledge.add_verified_tag")), OUTCOME_CANNOT_ESTABLISH)

    def test_evaluation_state_mutation_to_failed_requires_shape_change(self):
        d = deepcopy(SOURCE_CLEAR); d["evaluation"] = {"state":"failed"}; d.pop("effect")
        self.assertNotEqual(semantic_identity(d), semantic_identity(SOURCE_CLEAR))
        self.assertEqual(consume(d, **ctx(SOURCE_CLEAR, "knowledge.add_verified_tag")), OUTCOME_FAILED)

    def test_effect_type_and_version_unknown_fail_closed(self):
        for field, value in [("type","future.effect"),("version","2")]:
            d = deepcopy(SOURCE_CLEAR); d["effect"][field] = value
            self.assertEqual(consume(d, **ctx(SOURCE_CLEAR, "knowledge.add_verified_tag")), OUTCOME_CANNOT_ESTABLISH)

    def test_expected_upstream_each_field(self):
        for field, value in [("kind","x"),("id","x"),("immutable_id","x")]:
            c = ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope":"claim"}); c["expected_upstream"][field] = value
            self.assertEqual(consume(SOURCE_CLEAR, **c), OUTCOME_NOT_APPLICABLE)

    def test_expected_policy_each_field(self):
        for field in ["id", "version"]:
            c = ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope":"claim"}); c["expected_policy"][field] = "x"
            self.assertEqual(consume(SOURCE_CLEAR, **c), OUTCOME_NOT_APPLICABLE)

    def test_expected_target_each_field(self):
        mutations = {"kind":"x","id":"x","content_sha256":H2}
        for field, value in mutations.items():
            c = ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope":"claim"}); c["expected_target"][field] = value
            self.assertEqual(consume(SOURCE_CLEAR, **c), OUTCOME_NOT_APPLICABLE)

    def test_effect_reused_for_different_operation(self):
        self.assertEqual(consume(SOURCE_CLEAR, **ctx(SOURCE_CLEAR, "task.dispatch")), OUTCOME_NOT_APPLICABLE)

    def test_failed_binding_mismatch_precedes_failed_outcome(self):
        c = ctx(FAILED, "anything"); c["expected_target"]["id"] = "other"
        self.assertEqual(consume(FAILED, **c), OUTCOME_NOT_APPLICABLE)

    def test_requested_unknown_param_is_constraint_mismatch(self):
        self.assertEqual(consume(SOURCE_CLEAR, **ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"future": "x"})), OUTCOME_NOT_APPLICABLE)

    def test_requested_host_value_is_non_applicable(self):
        self.assertEqual(consume(SOURCE_CLEAR, **ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope": {1,2}})), OUTCOME_NOT_APPLICABLE)


class WeakConsumerDiscrimination(unittest.TestCase):
    def _cases(self):
        cases = []
        c = ctx(SOURCE_CLEAR, "task.dispatch"); cases.append((SOURCE_CLEAR, c, OUTCOME_NOT_APPLICABLE, "CLEAR/disposition-only"))
        c = ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope":"claim"}); c["expected_target"]["content_sha256"] = H2; cases.append((SOURCE_CLEAR, c, OUTCOME_NOT_APPLICABLE, "target-id-only"))
        c = ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope":"claim"}); c["expected_target"]["kind"] = "other"; cases.append((SOURCE_CLEAR, c, OUTCOME_NOT_APPLICABLE, "target ignores kind/content"))
        cases.append((HOLD, ctx(HOLD, "knowledge.add_verified_tag"), OUTCOME_HOLD, "HOLD/failure collapse"))
        reason = deepcopy(FAILED); reason["metadata"]["explanation"] = "task.dispatch"; cases.append((reason, ctx(reason, "task.dispatch"), OUTCOME_FAILED, "reason-text effect inference"))
        unknown = deepcopy(SOURCE_CLEAR); unknown["effect"] = {"type":"future.effect","version":"1"}; cases.append((unknown, ctx(unknown, "future.effect"), OUTCOME_CANNOT_ESTABLISH, "unknown-effect acceptance"))
        c = ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope":"claim"}); c["expected_policy"]["version"] = "2"; cases.append((SOURCE_CLEAR, c, OUTCOME_NOT_APPLICABLE, "policy-blind"))
        c = ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope":"claim"}); c["expected_upstream"]["immutable_id"] = "x"; cases.append((SOURCE_CLEAR, c, OUTCOME_NOT_APPLICABLE, "upstream-blind"))
        cases.append((OBJECT_CLEAR, ctx(OBJECT_CLEAR, "knowledge.add_verified_tag"), OUTCOME_CANDIDATE, "omitted requested params become defaults"))
        cases.append((HOLD, ctx(HOLD, "task.dispatch"), OUTCOME_NOT_APPLICABLE, "HOLD before applicability"))
        host = deepcopy(SOURCE_CLEAR); host["metadata"]["diagnostics"] = {"bad": {1}}; cases.append((host, ctx(SOURCE_CLEAR, "knowledge.add_verified_tag", {"scope":"claim"}), OUTCOME_CANNOT_ESTABLISH, "host-language-only diagnostics accepted"))
        return cases

    def test_every_outcome_weak_consumer_is_caught_by_decisive_gate(self):
        cases = self._cases()
        for name, consumer in weak_consumers.WEAK_OUTCOME_CONSUMERS.items():
            relevant = [x for x in cases if x[3] == name]
            self.assertEqual(len(relevant), 1, name)
            decision, c, expected, _ = relevant[0]
            self.assertNotEqual(consumer(decision, **c), expected, name)

    def test_authorization_contaminated_identity_is_caught(self):
        expected = semantic_identity(SOURCE_CLEAR)
        a = weak_consumers.authorization_contaminated_identity(SOURCE_CLEAR, {"actor":"a"})
        b = weak_consumers.authorization_contaminated_identity(SOURCE_CLEAR, {"actor":"b"})
        self.assertNotEqual(a, b)
        self.assertEqual(semantic_identity(SOURCE_CLEAR), expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)
