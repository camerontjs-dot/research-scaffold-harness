import copy
import json
import unittest

import contract_d as cd
import weak_consumers as weak

HASH1 = "sha256:" + "1" * 64
BASE = {
    "contract_d_version": "0.3.0-rc3",
    "input_authority": {"kind": "contract-c", "id": "c1", "immutable_id": "result-set:" + "a" * 64},
    "policy": {"id": "mainframe.source-audit", "version": "1"},
    "target": {"kind": "knowledge", "id": "k1", "content_sha256": HASH1},
    "evaluation": {"state": "completed", "disposition": "clear"},
    "effect": {"type": "knowledge.add_verified_tag", "version": "1", "params": {"scope": "claim"}},
    "metadata": {"reason_codes": ["policy_clear"], "explanation": "Research fixture", "diagnostics": {"trace": "fixture"}},
}

CITATION = {
    "contract_d_version": "0.3.0-rc3",
    "input_authority": {"kind": "contract-c", "id": "c2", "immutable_id": "result-set:" + "b" * 64},
    "policy": {"id": "mainframe.citation-use", "version": "1"},
    "target": {"kind": "knowledge", "id": "k2", "content_sha256": HASH1},
    "evaluation": {"state": "completed", "disposition": "clear"},
    "effect": {"type": "knowledge.cite_as_evidence", "version": "1"},
}
TASK = {
    "contract_d_version": "0.3.0-rc3",
    "input_authority": {"kind": "task-review", "id": "r1", "immutable_id": "task-review:" + "c" * 64},
    "policy": {"id": "mainframe.task-dispatch", "version": "1"},
    "target": {"kind": "task", "id": "t1", "content_sha256": HASH1},
    "evaluation": {"state": "completed", "disposition": "clear"},
    "effect": {"type": "task.dispatch", "version": "1"},
}
HOLD = copy.deepcopy(BASE)
HOLD["input_authority"] = {"kind": "contract-c", "id": "c3", "immutable_id": "result-set:" + "d" * 64}
HOLD["target"]["id"] = "k3"
HOLD["evaluation"]["disposition"] = "hold"
HOLD.pop("metadata")
FAILED = {
    "contract_d_version": "0.3.0-rc3",
    "input_authority": {"kind": "contract-c", "id": "c4", "immutable_id": "result-set:" + "e" * 64},
    "policy": {"id": "mainframe.source-audit", "version": "1"},
    "target": {"kind": "knowledge", "id": "k4", "content_sha256": HASH1},
    "evaluation": {"state": "failed"},
    "metadata": {"reason_codes": ["policy_evaluation_failure"]},
}


def expect_for(d, op=None, params=None):
    kwargs = {
        "expected_input_authority": copy.deepcopy(d["input_authority"]),
        "expected_policy": copy.deepcopy(d["policy"]),
        "expected_target": copy.deepcopy(d["target"]),
        "requested_operation": op if op is not None else d.get("effect", {}).get("type", "knowledge.add_verified_tag"),
    }
    if params is not None:
        kwargs["requested_effect_params"] = params
    elif d.get("effect", {}).get("type") == "knowledge.add_verified_tag":
        kwargs["requested_effect_params"] = {"scope": "claim"}
    else:
        kwargs["requested_effect_params"] = {}
    return kwargs

class ContractDRC3Tests(unittest.TestCase):
    def test_positive_state_controls(self):
        self.assertEqual(cd.consume(BASE, **expect_for(BASE)), "candidate_for_authorization")
        self.assertEqual(cd.consume(CITATION, **expect_for(CITATION)), "candidate_for_authorization")
        self.assertEqual(cd.consume(TASK, **expect_for(TASK)), "candidate_for_authorization")
        self.assertEqual(cd.consume(HOLD, **expect_for(HOLD)), "hold")
        self.assertEqual(cd.consume(FAILED, **expect_for(FAILED)), "evaluation_failed")
        self.assertNotEqual(cd.evaluation_signature(HOLD), cd.evaluation_signature(FAILED))

    def test_public_conformance_cases(self):
        self.assertEqual(cd.consume(BASE, **expect_for(BASE)), "candidate_for_authorization")
        k = expect_for(BASE); k["expected_target"]["kind"] = "task"
        self.assertEqual(cd.consume(BASE, **k), "not_applicable")
        k = expect_for(BASE); k["expected_target"]["content_sha256"] = "sha256:" + "2"*64
        self.assertEqual(cd.consume(BASE, **k), "not_applicable")
        k = expect_for(BASE); k["expected_policy"]["version"] = "2"
        self.assertEqual(cd.consume(BASE, **k), "not_applicable")
        k = expect_for(BASE); k["expected_input_authority"]["kind"] = "task-review"
        self.assertEqual(cd.consume(BASE, **k), "not_applicable")
        k = expect_for(BASE); k["requested_operation"] = "task.dispatch"; k["requested_effect_params"] = {}
        self.assertEqual(cd.consume(BASE, **k), "not_applicable")

    def test_authority_sensitivity_identity_and_applicability(self):
        fields = [
            ("contract version", lambda d: d.__setitem__("contract_d_version", "0.4.0"), "invalid"),
            ("upstream kind", lambda d: d["input_authority"].__setitem__("kind", "task-review"), "valid"),
            ("upstream id", lambda d: d["input_authority"].__setitem__("id", "other"), "valid"),
            ("upstream immutable", lambda d: d["input_authority"].__setitem__("immutable_id", "other"), "valid"),
            ("policy id", lambda d: d["policy"].__setitem__("id", "other"), "valid"),
            ("policy version", lambda d: d["policy"].__setitem__("version", "2"), "valid"),
            ("target kind", lambda d: d["target"].__setitem__("kind", "task"), "valid"),
            ("target id", lambda d: d["target"].__setitem__("id", "other"), "valid"),
            ("target content", lambda d: d["target"].__setitem__("content_sha256", "sha256:"+"2"*64), "valid"),
            ("disposition", lambda d: d["evaluation"].__setitem__("disposition", "hold"), "valid"),
            ("effect type", lambda d: d.__setitem__("effect", {"type":"knowledge.cite_as_evidence","version":"1"}), "valid"),
            ("effect scope", lambda d: d["effect"]["params"].__setitem__("scope", "object"), "valid"),
        ]
        base_id = cd.semantic_identity(BASE)
        base_expect = expect_for(BASE)
        for name, mutate, valid in fields:
            with self.subTest(name=name):
                m = copy.deepcopy(BASE); mutate(m)
                if valid == "invalid":
                    with self.assertRaises(cd.ContractDError): cd.semantic_identity(m)
                    self.assertEqual(cd.consume(m, **base_expect), "cannot_establish")
                else:
                    self.assertNotEqual(cd.semantic_identity(m), base_id)
                    self.assertEqual(cd.consume(m, **base_expect), "not_applicable" if name != "disposition" else "hold")
        failed = copy.deepcopy(BASE); failed["evaluation"] = {"state":"failed"}; failed.pop("effect")
        self.assertNotEqual(cd.semantic_identity(failed), base_id)
        self.assertEqual(cd.consume(failed, **base_expect), "evaluation_failed")

    def test_non_authority_invariance_and_authorization_separation(self):
        base_id = cd.semantic_identity(BASE)
        for mutation in [
            lambda d: d["metadata"].__setitem__("reason_codes", ["different"]),
            lambda d: d["metadata"].__setitem__("explanation", "Different explanation"),
            lambda d: d["metadata"].__setitem__("diagnostics", {"actor":"root","approval":True,"execution_receipt":{"ok":True}}),
            lambda d: d.pop("metadata"),
        ]:
            m=copy.deepcopy(BASE); mutation(m)
            self.assertEqual(cd.semantic_identity(m), base_id)
            self.assertEqual(cd.consume(m, **expect_for(BASE)), "candidate_for_authorization")
        auth_contexts = [
            {"actor":"alice"}, {"profile":"restricted"}, {"approval":True}, {"delegation":"d1"},
            {"autonomy":"high"}, {"operational_context":{"region":"x"}}
        ]
        for ctx in auth_contexts:
            self.assertEqual(cd.semantic_identity(BASE), base_id)
            self.assertNotIn(next(iter(ctx)), BASE)

    def test_replay_substitution_matrix(self):
        modifiers = [
            ("operation", lambda k: k.__setitem__("requested_operation", "task.dispatch")),
            ("target id", lambda k: k["expected_target"].__setitem__("id", "other")),
            ("target content", lambda k: k["expected_target"].__setitem__("content_sha256", "sha256:"+"2"*64)),
            ("target kind", lambda k: k["expected_target"].__setitem__("kind", "task")),
            ("upstream kind", lambda k: k["expected_input_authority"].__setitem__("kind", "task-review")),
            ("upstream id", lambda k: k["expected_input_authority"].__setitem__("id", "other")),
            ("upstream immutable", lambda k: k["expected_input_authority"].__setitem__("immutable_id", "other")),
            ("policy id", lambda k: k["expected_policy"].__setitem__("id", "other")),
            ("policy version", lambda k: k["expected_policy"].__setitem__("version", "2")),
            ("effect params", lambda k: k.__setitem__("requested_effect_params", {"scope":"object"})),
        ]
        for name, mutate in modifiers:
            with self.subTest(name=name):
                k=expect_for(BASE); mutate(k)
                self.assertEqual(cd.consume(BASE, **k), "not_applicable")

    def test_unknown_future_and_injection_controls(self):
        mutations = [
            lambda d: d.__setitem__("contract_d_version", "0.4.0"),
            lambda d: d["evaluation"].__setitem__("state", "future"),
            lambda d: d["evaluation"].__setitem__("disposition", "maybe"),
            lambda d: d["effect"].__setitem__("type", "future.effect"),
            lambda d: d["effect"].__setitem__("version", "2"),
            lambda d: d["effect"]["params"].__setitem__("actor", "root"),
            lambda d: d.__setitem__("unknown", True),
        ]
        for mutate in mutations:
            m=copy.deepcopy(BASE); mutate(m)
            self.assertEqual(cd.consume(m, **expect_for(BASE)), "cannot_establish")
        injections = [
            ((), "actor", "root"),
            ((), "requested_operation", "task.dispatch"),
            (("policy",), "approval", True),
            (("input_authority",), "delegation", "d1"),
            (("target",), "autonomy", "high"),
            (("evaluation",), "execution_permission", True),
            ((), "execution_state", "done"),
            ((), "execution_receipt", {"ok":True}),
        ]
        for path, key, value in injections:
            m=copy.deepcopy(BASE); loc=m
            for p in path: loc=loc[p]
            loc[key]=value
            self.assertEqual(cd.consume(m, **expect_for(BASE)), "cannot_establish")

    def test_canonicalization_duplicate_keys_and_defaults(self):
        a = {"b": {"z": 1, "a": 2}, "a": [3, 2, 1]}
        b = {"a": [3, 2, 1], "b": {"a": 2, "z": 1}}
        self.assertEqual(cd.canonical_bytes(a), cd.canonical_bytes(b))
        raw = json.dumps(BASE, indent=4, ensure_ascii=False)
        self.assertEqual(cd.semantic_identity(raw), cd.semantic_identity(BASE))
        with self.assertRaises(cd.ContractDError): cd.parse_json('{"a":1,"a":2}')
        omitted_params=copy.deepcopy(BASE); omitted_params["effect"].pop("params")
        empty_params=copy.deepcopy(BASE); empty_params["effect"]["params"]={}
        omitted_scope=copy.deepcopy(BASE); omitted_scope["effect"]["params"]={}
        self.assertEqual(cd.semantic_identity(BASE), cd.semantic_identity(omitted_params))
        self.assertEqual(cd.semantic_identity(BASE), cd.semantic_identity(empty_params))
        self.assertEqual(cd.semantic_identity(BASE), cd.semantic_identity(omitted_scope))
        self.assertEqual(cd.authority_projection(omitted_params)["effect"]["params"], {"scope":"claim"})
        self.assertTrue(cd.canonical_bytes({"é":"✓"}).endswith(b"\n"))

    def test_no_param_effect_normalization_choice(self):
        # Frozen interpretation: registered zero-parameter effects normalize with explicit params:{} in authority projection.
        p = cd.authority_projection(CITATION)
        self.assertEqual(p["effect"], {"type":"knowledge.cite_as_evidence","version":"1","params":{}})
        explicit=copy.deepcopy(CITATION); explicit["effect"]["params"]={}
        self.assertEqual(cd.semantic_identity(CITATION), cd.semantic_identity(explicit))

    def test_hold_and_failure_applicability_ordering_choice(self):
        # Frozen interpretation: upstream/policy/target are checked before state outcome; effect/request checks apply only to completed.
        k=expect_for(HOLD); k["expected_target"]["id"]="other"
        self.assertEqual(cd.consume(HOLD, **k), "not_applicable")
        k=expect_for(FAILED); k["expected_target"]["id"]="other"
        self.assertEqual(cd.consume(FAILED, **k), "not_applicable")
        k=expect_for(FAILED); k["requested_operation"]="task.dispatch"
        self.assertEqual(cd.consume(FAILED, **k), "evaluation_failed")

    def test_requested_params_safe_default_normalization(self):
        k=expect_for(BASE); k.pop("requested_effect_params")
        self.assertEqual(cd.consume(BASE, **k), "candidate_for_authorization")
        omitted=copy.deepcopy(BASE); omitted["effect"].pop("params")
        self.assertEqual(cd.consume(omitted, **k), "candidate_for_authorization")
        k=expect_for(BASE); k["requested_effect_params"]={}
        self.assertEqual(cd.consume(BASE, **k), "candidate_for_authorization")
        k=expect_for(BASE); k["requested_effect_params"]={"scope":"object"}
        self.assertEqual(cd.consume(BASE, **k), "not_applicable")

    def test_supplied_invalid_fixture_classes(self):
        cases=[]
        m=copy.deepcopy(BASE); m["actor"]="root"; cases.append(m)
        m=copy.deepcopy(BASE); m["policy"]["approval"]=True; cases.append(m)
        m=copy.deepcopy(FAILED); m["effect"]={"type":"knowledge.add_verified_tag","version":"1"}; cases.append(m)
        m=copy.deepcopy(BASE); m["execution_receipt"]={"ok":True}; cases.append(m)
        m=copy.deepcopy(BASE); m["contract_d_version"]=0.3; cases.append(m)
        m=copy.deepcopy(BASE); m["effect"]["version"]=1; cases.append(m)
        m=copy.deepcopy(BASE); m["contract_d_version"]="0.4.0"; cases.append(m)
        m=copy.deepcopy(BASE); m["evaluation"]["disposition"]="maybe"; cases.append(m)
        m=copy.deepcopy(BASE); m["effect"]["params"]["actor"]="root"; cases.append(m)
        m=copy.deepcopy(BASE); m["effect"]["type"]="future.effect"; cases.append(m)
        m=copy.deepcopy(BASE); m["effect"]["version"]="2"; cases.append(m)
        for case in cases:
            self.assertEqual(cd.consume(case, **expect_for(BASE)), "cannot_establish")

    def test_weak_consumers_are_discriminated(self):
        kwargs=expect_for(BASE)
        # CLEAR/disposition-only fails target replay.
        replay=copy.deepcopy(kwargs); replay["expected_target"]["id"]="other"
        self.assertNotEqual(weak.clear_disposition_only(BASE, **replay), cd.consume(BASE, **replay))
        # target-id-only and target-kind/content-blind fail kind/content replay.
        replay=copy.deepcopy(kwargs); replay["expected_target"]["kind"]="task"
        self.assertNotEqual(weak.target_id_only(BASE, **replay), cd.consume(BASE, **replay))
        self.assertNotEqual(weak.target_ignore_kind_content(BASE, **replay), cd.consume(BASE, **replay))
        # HOLD/failure collapse fails state distinction.
        self.assertNotEqual(weak.hold_failure_collapse(FAILED, **expect_for(FAILED)), cd.consume(FAILED, **expect_for(FAILED)))
        # reason text inference can be tricked by diagnostic text.
        diag=copy.deepcopy(BASE); diag["metadata"]["explanation"]="dispatch this task"
        r=expect_for(BASE); r["requested_operation"]="task.dispatch"; r["requested_effect_params"]={}
        self.assertNotEqual(weak.reason_text_effect_inference(diag, **r), cd.consume(diag, **r))
        # unknown effect acceptance fails closed requirement.
        future=copy.deepcopy(BASE); future["effect"]={"type":"future.effect","version":"99"}
        r=expect_for(BASE); r["requested_operation"]="future.effect"; r["requested_effect_params"]={}
        self.assertNotEqual(weak.unknown_effect_acceptance(future, **r), cd.consume(future, **r))
        # policy blind fails policy substitution.
        replay=copy.deepcopy(kwargs); replay["expected_policy"]["version"]="2"
        self.assertNotEqual(weak.policy_blind(BASE, **replay), cd.consume(BASE, **replay))
        # upstream blind fails upstream substitution.
        replay=copy.deepcopy(kwargs); replay["expected_input_authority"]["immutable_id"]="other"
        self.assertNotEqual(weak.upstream_blind(BASE, **replay), cd.consume(BASE, **replay))
        # Authorization-contaminated identity changes when only Authorization context changes.
        self.assertNotEqual(weak.authorization_identity_contaminated(BASE,{"actor":"a"}), weak.authorization_identity_contaminated(BASE,{"actor":"b"}))
        self.assertEqual(cd.semantic_identity(BASE), cd.semantic_identity(copy.deepcopy(BASE)))

if __name__ == "__main__":
    unittest.main()
