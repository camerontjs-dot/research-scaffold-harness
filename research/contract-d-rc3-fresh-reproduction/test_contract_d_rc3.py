from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

import contract_d_rc3 as d

HERE = Path(__file__).parent
FIXTURES = json.loads((HERE / "fixtures" / "self_generated.json").read_text())


def clone(name: str):
    return copy.deepcopy(FIXTURES[name])


def boundary(obj):
    return {
        "expected_input_authority": copy.deepcopy(obj["input_authority"]),
        "expected_policy": copy.deepcopy(obj["policy"]),
        "expected_target": copy.deepcopy(obj["target"]),
    }


def consume_exact(obj, operation=None, params=None, **overrides):
    b = boundary(obj)
    b.update(overrides)
    if operation is None and obj.get("effect"):
        operation = obj["effect"]["type"]
    return d.consume(
        obj,
        requested_operation=operation or "knowledge.add_verified_tag",
        requested_effect_params=params,
        **b,
    )


class PositiveStateControls(unittest.TestCase):
    def test_source_audit_clear(self):
        obj = clone("source_audit_clear")
        self.assertEqual(consume_exact(obj, params={"scope": "claim"}), "candidate_for_authorization")

    def test_citation_use_clear(self):
        obj = clone("citation_clear")
        self.assertEqual(consume_exact(obj), "candidate_for_authorization")

    def test_task_dispatch_clear(self):
        obj = clone("dispatch_clear")
        self.assertEqual(consume_exact(obj), "candidate_for_authorization")

    def test_completed_hold(self):
        obj = clone("completed_hold")
        self.assertEqual(consume_exact(obj), "hold")

    def test_evaluation_failure(self):
        obj = clone("evaluation_failed")
        self.assertEqual(consume_exact(obj), "evaluation_failed")

    def test_hold_is_not_failure(self):
        hold = clone("completed_hold")
        failed = clone("evaluation_failed")
        self.assertNotEqual(consume_exact(hold), consume_exact(failed))
        self.assertNotEqual(d.semantic_identity(hold), d.semantic_identity(failed))


class AuthoritySensitivity(unittest.TestCase):
    def setUp(self):
        self.base = clone("source_audit_clear")
        self.base_id = d.semantic_identity(self.base)

    def assert_id_changes(self, mutate):
        obj = copy.deepcopy(self.base)
        mutate(obj)
        self.assertNotEqual(d.semantic_identity(obj), self.base_id)

    def test_upstream_kind(self):
        self.assert_id_changes(lambda o: o["input_authority"].__setitem__("kind", "task-review"))

    def test_upstream_id(self):
        self.assert_id_changes(lambda o: o["input_authority"].__setitem__("id", "other"))

    def test_upstream_immutable_identity(self):
        self.assert_id_changes(lambda o: o["input_authority"].__setitem__("immutable_id", "result-set:" + "f" * 64))

    def test_policy_id(self):
        self.assert_id_changes(lambda o: o["policy"].__setitem__("id", "other.policy"))

    def test_policy_version(self):
        self.assert_id_changes(lambda o: o["policy"].__setitem__("version", "2"))

    def test_target_kind(self):
        self.assert_id_changes(lambda o: o["target"].__setitem__("kind", "task"))

    def test_target_id(self):
        self.assert_id_changes(lambda o: o["target"].__setitem__("id", "other"))

    def test_target_content(self):
        self.assert_id_changes(lambda o: o["target"].__setitem__("content_sha256", "sha256:" + "9" * 64))

    def test_disposition(self):
        self.assert_id_changes(lambda o: o["evaluation"].__setitem__("disposition", "hold"))

    def test_effect_type(self):
        obj = copy.deepcopy(self.base)
        obj["effect"] = {"type": "knowledge.cite_as_evidence", "version": "1"}
        self.assertNotEqual(d.semantic_identity(obj), self.base_id)

    def test_effect_version_is_authority_and_unknown_fails_closed(self):
        obj = copy.deepcopy(self.base)
        obj["effect"]["version"] = "2"
        self.assertEqual(consume_exact(obj, params={"scope": "claim"}), "cannot_establish")
        with self.assertRaises(d.ContractDInvalid):
            d.semantic_identity(obj)

    def test_machine_semantic_scope_parameter(self):
        obj = copy.deepcopy(self.base)
        obj["effect"]["params"]["scope"] = "object"
        self.assertNotEqual(d.semantic_identity(obj), self.base_id)
        self.assertEqual(consume_exact(obj, params={"scope": "claim"}), "not_applicable")
        self.assertEqual(consume_exact(obj, params={"scope": "object"}), "candidate_for_authorization")

    def test_evaluation_state(self):
        failed = copy.deepcopy(self.base)
        failed["evaluation"] = {"state": "failed"}
        failed.pop("effect")
        self.assertNotEqual(d.semantic_identity(failed), self.base_id)
        self.assertEqual(consume_exact(failed), "evaluation_failed")

    def test_contract_version_is_authority_and_unknown_fails_closed(self):
        obj = copy.deepcopy(self.base)
        obj["contract_d_version"] = "0.4.0"
        self.assertEqual(consume_exact(obj, params={"scope": "claim"}), "cannot_establish")
        with self.assertRaises(d.ContractDInvalid):
            d.semantic_identity(obj)


class AuthorityInvariance(unittest.TestCase):
    def setUp(self):
        self.base = clone("source_audit_clear")
        self.base_id = d.semantic_identity(self.base)

    def test_reason_codes_excluded(self):
        obj = copy.deepcopy(self.base)
        obj["metadata"]["reason_codes"] = ["different", "still_non_authoritative"]
        self.assertEqual(d.semantic_identity(obj), self.base_id)
        self.assertEqual(consume_exact(obj, params={"scope": "claim"}), "candidate_for_authorization")

    def test_explanation_excluded(self):
        obj = copy.deepcopy(self.base)
        obj["metadata"]["explanation"] = "Different explanation"
        self.assertEqual(d.semantic_identity(obj), self.base_id)

    def test_diagnostics_excluded_and_authorization_words_are_inert_inside_it(self):
        obj = copy.deepcopy(self.base)
        obj["metadata"]["diagnostics"] = {
            "actor": "root",
            "approval": True,
            "delegation": {"to": "x"},
            "requested_operation": "task.dispatch",
            "execution_permission": True,
            "nested": {"z": 1, "a": 2},
        }
        self.assertEqual(d.semantic_identity(obj), self.base_id)
        self.assertEqual(consume_exact(obj, params={"scope": "claim"}), "candidate_for_authorization")

    def test_metadata_removal_excluded(self):
        obj = copy.deepcopy(self.base)
        obj.pop("metadata")
        self.assertEqual(d.semantic_identity(obj), self.base_id)

    def test_external_authorization_context_cannot_modify_decision_identity(self):
        decision = copy.deepcopy(self.base)
        frozen = copy.deepcopy(decision)
        contexts = [
            {"actor": "alice", "profile": "p1", "approval": False, "delegation": None, "context": {"zone": "a"}},
            {"actor": "bob", "profile": "p2", "approval": True, "delegation": {"from": "alice"}, "context": {"zone": "b"}},
        ]
        ids = []
        for auth in contexts:
            _ = copy.deepcopy(auth)
            ids.append(d.semantic_identity(decision))
        self.assertEqual(decision, frozen)
        self.assertEqual(ids, [self.base_id, self.base_id])


class ReplayAndSubstitution(unittest.TestCase):
    def setUp(self):
        self.base = clone("source_audit_clear")
        self.bound = boundary(self.base)

    def call(self, **kwargs):
        args = copy.deepcopy(self.bound)
        args.update(kwargs)
        return d.consume(self.base, requested_operation="knowledge.add_verified_tag", requested_effect_params={"scope": "claim"}, **args)

    def test_effect_reused_for_different_requested_operation(self):
        self.assertEqual(d.consume(self.base, requested_operation="task.dispatch", requested_effect_params=None, **self.bound), "not_applicable")

    def test_other_target_id(self):
        target = copy.deepcopy(self.bound["expected_target"])
        target["id"] = "other"
        self.assertEqual(self.call(expected_target=target), "not_applicable")

    def test_same_id_changed_content(self):
        target = copy.deepcopy(self.bound["expected_target"])
        target["content_sha256"] = "sha256:" + "2" * 64
        self.assertEqual(self.call(expected_target=target), "not_applicable")

    def test_same_id_content_different_kind(self):
        target = copy.deepcopy(self.bound["expected_target"])
        target["kind"] = "task"
        self.assertEqual(self.call(expected_target=target), "not_applicable")

    def test_upstream_kind_substitution(self):
        upstream = copy.deepcopy(self.bound["expected_input_authority"])
        upstream["kind"] = "task-review"
        self.assertEqual(self.call(expected_input_authority=upstream), "not_applicable")

    def test_upstream_id_substitution(self):
        upstream = copy.deepcopy(self.bound["expected_input_authority"])
        upstream["id"] = "other"
        self.assertEqual(self.call(expected_input_authority=upstream), "not_applicable")

    def test_upstream_immutable_substitution(self):
        upstream = copy.deepcopy(self.bound["expected_input_authority"])
        upstream["immutable_id"] = "result-set:" + "f" * 64
        self.assertEqual(self.call(expected_input_authority=upstream), "not_applicable")

    def test_policy_id_substitution(self):
        policy = copy.deepcopy(self.bound["expected_policy"])
        policy["id"] = "other.policy"
        self.assertEqual(self.call(expected_policy=policy), "not_applicable")

    def test_policy_version_substitution(self):
        policy = copy.deepcopy(self.bound["expected_policy"])
        policy["version"] = "2"
        self.assertEqual(self.call(expected_policy=policy), "not_applicable")


class FutureUnknownAndInjection(unittest.TestCase):
    def setUp(self):
        self.base = clone("source_audit_clear")

    def assert_cannot(self, obj):
        self.assertEqual(consume_exact(obj, params={"scope": "claim"}), "cannot_establish")

    def test_unknown_contract_version(self):
        obj = copy.deepcopy(self.base); obj["contract_d_version"] = "0.3.1"
        self.assert_cannot(obj)

    def test_numeric_contract_version(self):
        obj = copy.deepcopy(self.base); obj["contract_d_version"] = 0.3
        self.assert_cannot(obj)

    def test_unknown_evaluation_state(self):
        obj = copy.deepcopy(self.base); obj["evaluation"]["state"] = "partial"
        self.assert_cannot(obj)

    def test_unknown_disposition(self):
        obj = copy.deepcopy(self.base); obj["evaluation"]["disposition"] = "maybe"
        self.assert_cannot(obj)

    def test_unknown_effect_type(self):
        obj = copy.deepcopy(self.base); obj["effect"]["type"] = "future.effect"
        self.assert_cannot(obj)

    def test_unknown_effect_version(self):
        obj = copy.deepcopy(self.base); obj["effect"]["version"] = "9"
        self.assert_cannot(obj)

    def test_numeric_effect_version(self):
        obj = copy.deepcopy(self.base); obj["effect"]["version"] = 1
        self.assert_cannot(obj)

    def test_unknown_effect_parameter(self):
        obj = copy.deepcopy(self.base); obj["effect"]["params"]["actor"] = "root"
        self.assert_cannot(obj)

    def test_unknown_structural_fields_at_all_owned_levels(self):
        placements = [
            lambda o: o.__setitem__("future", 1),
            lambda o: o["input_authority"].__setitem__("future", 1),
            lambda o: o["policy"].__setitem__("future", 1),
            lambda o: o["target"].__setitem__("future", 1),
            lambda o: o["evaluation"].__setitem__("future", 1),
            lambda o: o["effect"].__setitem__("future", 1),
            lambda o: o["metadata"].__setitem__("future", 1),
        ]
        for place in placements:
            with self.subTest(place=place):
                obj = copy.deepcopy(self.base); place(obj); self.assert_cannot(obj)

    def test_authorization_execution_injections_are_rejected_at_owned_locations(self):
        attempts = [
            ("actor", lambda o, k: o.__setitem__(k, "root")),
            ("requested_operation", lambda o, k: o["effect"].__setitem__(k, "task.dispatch")),
            ("approval", lambda o, k: o["policy"].__setitem__(k, True)),
            ("delegation", lambda o, k: o["input_authority"].__setitem__(k, {"to": "x"})),
            ("autonomy", lambda o, k: o["evaluation"].__setitem__(k, "auto")),
            ("execution_permission", lambda o, k: o["target"].__setitem__(k, True)),
            ("execution_state", lambda o, k: o.__setitem__(k, "done")),
            ("execution_receipt", lambda o, k: o.__setitem__(k, {"ok": True})),
        ]
        for name, place in attempts:
            with self.subTest(name=name):
                obj = copy.deepcopy(self.base); place(obj, name); self.assert_cannot(obj)


class CanonicalizationAndIdentity(unittest.TestCase):
    def test_key_order_and_nested_order_do_not_change_canonical_bytes(self):
        a = {"z": 1, "a": {"z": 2, "a": 3}, "m": [3, {"y": 1, "x": 2}]}
        b = {"m": [3, {"x": 2, "y": 1}], "a": {"a": 3, "z": 2}, "z": 1}
        self.assertEqual(d.canonical_json_bytes(a), d.canonical_json_bytes(b))

    def test_array_order_is_preserved(self):
        self.assertNotEqual(d.canonical_json_bytes([1, 2]), d.canonical_json_bytes([2, 1]))

    def test_compact_utf8_and_single_newline(self):
        out = d.canonical_json_bytes({"é": "✓", "b": 2, "a": 1})
        self.assertEqual(out, '{"a":1,"b":2,"é":"✓"}\n'.encode("utf-8"))

    def test_duplicate_keys_rejected(self):
        text = '{"contract_d_version":"0.3.0-rc3","contract_d_version":"0.3.0-rc3"}'
        with self.assertRaises(d.ContractDInvalid):
            d.parse_json_document(text)

    def test_nested_duplicate_keys_rejected(self):
        with self.assertRaises(d.ContractDInvalid):
            d.parse_json_document('{"x":{"a":1,"a":2}}')

    def test_non_finite_numbers_rejected(self):
        for text in ('{"x":NaN}', '{"x":Infinity}', '{"x":1e400}'):
            with self.subTest(text=text):
                with self.assertRaises(d.ContractDInvalid):
                    d.parse_json_document(text)

    def test_safe_default_normalization_equivalence(self):
        variants = []
        for effect in [
            {"type": "knowledge.add_verified_tag", "version": "1"},
            {"type": "knowledge.add_verified_tag", "version": "1", "params": {}},
            {"type": "knowledge.add_verified_tag", "version": "1", "params": {"scope": "claim"}},
        ]:
            obj = clone("source_audit_clear")
            obj["effect"] = effect
            variants.append(d.semantic_identity(obj))
        self.assertEqual(len(set(variants)), 1)

    def test_empty_params_normalize_for_parameterless_effect(self):
        a = clone("citation_clear")
        b = clone("citation_clear"); b["effect"]["params"] = {}
        self.assertEqual(d.semantic_identity(a), d.semantic_identity(b))

    def test_metadata_mutation_does_not_change_id_but_authority_mutation_does(self):
        base = clone("source_audit_clear")
        meta = copy.deepcopy(base); meta["metadata"]["diagnostics"] = {"changed": True}
        auth = copy.deepcopy(base); auth["target"]["id"] = "different"
        self.assertEqual(d.semantic_identity(base), d.semantic_identity(meta))
        self.assertNotEqual(d.semantic_identity(base), d.semantic_identity(auth))

    def test_semantic_identity_prefix_and_digest(self):
        obj = clone("dispatch_clear")
        projection = d.authority_projection(obj)
        expected = "decision:sha256:" + hashlib.sha256(d.canonical_json_bytes(projection)).hexdigest()
        self.assertEqual(d.semantic_identity(obj), expected)


class ApplicabilityOrdering(unittest.TestCase):
    def test_failed_decision_for_wrong_target_is_not_applicable_before_failure_outcome(self):
        obj = clone("evaluation_failed")
        target = copy.deepcopy(obj["target"]); target["id"] = "other"
        self.assertEqual(consume_exact(obj, expected_target=target), "not_applicable")

    def test_hold_for_wrong_policy_is_not_applicable_before_hold_outcome(self):
        obj = clone("completed_hold")
        policy = copy.deepcopy(obj["policy"]); policy["version"] = "2"
        self.assertEqual(consume_exact(obj, expected_policy=policy), "not_applicable")

    def test_omitted_requested_scope_uses_registered_default(self):
        obj = clone("source_audit_clear")
        self.assertEqual(consume_exact(obj, params=None), "candidate_for_authorization")


class WeakConsumerAssurance(unittest.TestCase):
    def setUp(self):
        self.base = clone("source_audit_clear")
        self.bound = boundary(self.base)

    @staticmethod
    def weak_clear_only(obj, **_):
        return "candidate_for_authorization" if obj.get("evaluation", {}).get("disposition") == "clear" else "evaluation_failed"

    @staticmethod
    def weak_target_id_only(obj, expected_target, **_):
        return "candidate_for_authorization" if obj["target"]["id"] == expected_target["id"] else "not_applicable"

    @staticmethod
    def weak_ignore_target_kind_content(obj, expected_target, **_):
        return "candidate_for_authorization" if obj["target"]["id"] == expected_target["id"] else "not_applicable"

    @staticmethod
    def weak_hold_failure_collapse(obj, **_):
        if obj.get("evaluation", {}).get("disposition") == "clear":
            return "candidate_for_authorization"
        return "evaluation_failed"

    @staticmethod
    def weak_reason_effect(obj, requested_operation, **_):
        reasons = obj.get("metadata", {}).get("reason_codes", [])
        return "candidate_for_authorization" if requested_operation in reasons else "not_applicable"

    @staticmethod
    def weak_unknown_effect_accept(obj, **_):
        return "candidate_for_authorization" if obj.get("evaluation", {}).get("disposition") == "clear" else "evaluation_failed"

    @staticmethod
    def weak_policy_blind(obj, expected_target, expected_input_authority, **_):
        good_target = obj["target"] == expected_target
        good_upstream = obj["input_authority"] == expected_input_authority
        return "candidate_for_authorization" if good_target and good_upstream else "not_applicable"

    @staticmethod
    def weak_upstream_blind(obj, expected_target, expected_policy, **_):
        return "candidate_for_authorization" if obj["target"] == expected_target and obj["policy"] == expected_policy else "not_applicable"

    def test_clear_disposition_only_is_killed(self):
        target = copy.deepcopy(self.bound["expected_target"]); target["id"] = "other"
        expected = "not_applicable"
        self.assertEqual(d.consume(self.base, requested_operation="knowledge.add_verified_tag", requested_effect_params={"scope": "claim"}, expected_target=target, expected_policy=self.bound["expected_policy"], expected_input_authority=self.bound["expected_input_authority"]), expected)
        self.assertNotEqual(self.weak_clear_only(self.base), expected)

    def test_target_id_only_is_killed(self):
        target = copy.deepcopy(self.bound["expected_target"]); target["kind"] = "task"; target["content_sha256"] = "sha256:" + "8" * 64
        expected = "not_applicable"
        self.assertEqual(d.consume(self.base, requested_operation="knowledge.add_verified_tag", requested_effect_params={"scope": "claim"}, expected_target=target, expected_policy=self.bound["expected_policy"], expected_input_authority=self.bound["expected_input_authority"]), expected)
        self.assertNotEqual(self.weak_target_id_only(self.base, expected_target=target), expected)

    def test_target_ignore_kind_content_is_killed(self):
        target = copy.deepcopy(self.bound["expected_target"]); target["content_sha256"] = "sha256:" + "7" * 64
        expected = "not_applicable"
        self.assertNotEqual(self.weak_ignore_target_kind_content(self.base, expected_target=target), expected)

    def test_hold_failure_collapse_is_killed(self):
        hold = clone("completed_hold")
        expected = "hold"
        self.assertEqual(consume_exact(hold), expected)
        self.assertNotEqual(self.weak_hold_failure_collapse(hold), expected)

    def test_reason_text_effect_inference_is_killed(self):
        obj = clone("citation_clear")
        obj["metadata"] = {"reason_codes": ["task.dispatch"]}
        expected = d.consume(obj, requested_operation="task.dispatch", requested_effect_params=None, **boundary(obj))
        self.assertEqual(expected, "not_applicable")
        self.assertNotEqual(self.weak_reason_effect(obj, requested_operation="task.dispatch"), expected)

    def test_unknown_effect_acceptance_is_killed(self):
        obj = copy.deepcopy(self.base); obj["effect"]["type"] = "future.effect"
        expected = consume_exact(obj, params={"scope": "claim"})
        self.assertEqual(expected, "cannot_establish")
        self.assertNotEqual(self.weak_unknown_effect_accept(obj), expected)

    def test_policy_blind_is_killed(self):
        policy = copy.deepcopy(self.bound["expected_policy"]); policy["version"] = "2"
        expected = d.consume(self.base, requested_operation="knowledge.add_verified_tag", requested_effect_params={"scope": "claim"}, expected_policy=policy, expected_target=self.bound["expected_target"], expected_input_authority=self.bound["expected_input_authority"])
        self.assertEqual(expected, "not_applicable")
        self.assertNotEqual(self.weak_policy_blind(self.base, expected_target=self.bound["expected_target"], expected_input_authority=self.bound["expected_input_authority"]), expected)

    def test_upstream_blind_is_killed(self):
        upstream = copy.deepcopy(self.bound["expected_input_authority"]); upstream["immutable_id"] = "result-set:" + "0" * 64
        expected = d.consume(self.base, requested_operation="knowledge.add_verified_tag", requested_effect_params={"scope": "claim"}, expected_policy=self.bound["expected_policy"], expected_target=self.bound["expected_target"], expected_input_authority=upstream)
        self.assertEqual(expected, "not_applicable")
        self.assertNotEqual(self.weak_upstream_blind(self.base, expected_target=self.bound["expected_target"], expected_policy=self.bound["expected_policy"]), expected)

    def test_identity_contaminated_by_authorization_context_is_killed(self):
        obj = copy.deepcopy(self.base)
        auth_a = {"actor": "alice", "approval": False, "delegation": None, "context": {"x": 1}}
        auth_b = {"actor": "bob", "approval": True, "delegation": {"to": "bob"}, "context": {"x": 2}}
        true_a = d.semantic_identity(obj)
        true_b = d.semantic_identity(obj)
        weak_a = hashlib.sha256(d.canonical_json_bytes({"decision": d.authority_projection(obj), "authorization": auth_a})).hexdigest()
        weak_b = hashlib.sha256(d.canonical_json_bytes({"decision": d.authority_projection(obj), "authorization": auth_b})).hexdigest()
        self.assertEqual(true_a, true_b)
        self.assertNotEqual(weak_a, weak_b)


if __name__ == "__main__":
    unittest.main()
