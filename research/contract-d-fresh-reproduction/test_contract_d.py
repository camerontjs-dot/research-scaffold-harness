from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from contract_d import (
    ContractDValidationError,
    authorization_evaluate,
    canonical_json_bytes,
    parse_and_validate,
    produce_decision,
)

ROOT = Path(__file__).parent
FIXTURES = ROOT / "fixtures"


def load(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ContractDFreshReproductionTests(unittest.TestCase):
    def setUp(self):
        self.audit = load("valid-knowledge-tag-clear.json")
        self.citation = load("valid-citation-use-clear.json")
        self.task = load("valid-task-dispatch-clear.json")
        self.hold = load("completed-hold.json")
        self.failed = load("evaluation-failed.json")
        self.unknown_version = load("unknown-effect-version.json")
        self.unknown_type = load("unknown-effect-type.json")
        self.target = copy.deepcopy(self.audit["target"])
        self.profile = {
            "accepted_input_authorities": [
                [self.audit["input_authority"]["kind"], self.audit["input_authority"]["id"]]
            ],
            "accepted_policies": [
                [self.audit["policy"]["id"], self.audit["policy"]["version"]]
            ],
            "allowed_actors": ["actor-a"],
            "allowed_operations": ["knowledge.apply_tag"],
            "required_context": {"environment": "research"},
            "require_human_approval": False,
        }

    def auth(self, decision=None, **overrides):
        args = dict(
            decision_obj=self.audit if decision is None else decision,
            actor="actor-a",
            requested_operation="knowledge.apply_tag",
            request_target=copy.deepcopy(self.target),
            context={"environment": "research", "tag": "audited_verified"},
            authorization_profile=copy.deepcopy(self.profile),
            human_approval=None,
        )
        args.update(overrides)
        return authorization_evaluate(**args)

    def test_valid_fixture_round_trip_and_identity(self):
        for name in [
            "valid-knowledge-tag-clear.json",
            "valid-citation-use-clear.json",
            "valid-task-dispatch-clear.json",
            "completed-hold.json",
            "evaluation-failed.json",
            "unknown-effect-version.json",
            "unknown-effect-type.json",
        ]:
            obj = load(name)
            parsed = parse_and_validate(obj)
            self.assertEqual(parsed.value["decision_id"], parsed.semantic_identity)
            self.assertEqual(parsed.canonical_bytes, canonical_json_bytes(parsed.value))

    def test_clear_is_only_candidate_not_execution_authority(self):
        self.assertEqual(
            self.auth(),
            {"decision_status": "candidate_for_authorization", "authorization": "permit"},
        )
        denied = self.auth(actor="actor-b")
        self.assertEqual(denied["decision_status"], "candidate_for_authorization")
        self.assertEqual(denied["authorization"], "deny")

    def test_hold_and_evaluation_failure_remain_distinct(self):
        hold = self.auth(self.hold)
        failed = self.auth(self.failed)
        self.assertEqual(hold, {"decision_status": "not_candidate", "authorization": "deny"})
        self.assertEqual(
            failed, {"decision_status": "not_candidate", "authorization": "cannot_establish"}
        )
        self.assertNotEqual(
            parse_and_validate(self.hold).semantic_identity,
            parse_and_validate(self.failed).semantic_identity,
        )

    def test_unknown_effect_type_and_version_fail_closed_but_parse(self):
        for obj in [self.unknown_type, self.unknown_version]:
            parsed = parse_and_validate(obj)
            self.assertTrue(parsed.semantic_identity.startswith("sha256:"))
            result = self.auth(obj)
            self.assertEqual(result["decision_status"], "unknown_effect")
            self.assertEqual(result["authorization"], "cannot_establish")

    def test_cross_operation_replay_is_not_applicable(self):
        result = self.auth(
            requested_operation="task.dispatch",
            context={"environment": "research", "dispatch_class": "human_review_queue"},
        )
        self.assertEqual(result["decision_status"], "not_applicable")
        self.assertEqual(result["authorization"], "cannot_establish")

    def test_target_id_replay_is_not_applicable(self):
        changed = copy.deepcopy(self.target)
        changed["id"] = "ko-999"
        self.assertEqual(self.auth(request_target=changed)["decision_status"], "not_applicable")

    def test_changed_content_same_target_id_is_not_applicable(self):
        changed = copy.deepcopy(self.target)
        changed["content_hash"] = "sha256:" + "9" * 64
        self.assertEqual(self.auth(request_target=changed)["decision_status"], "not_applicable")

    def test_policy_version_replay_is_not_applicable(self):
        profile = copy.deepcopy(self.profile)
        profile["accepted_policies"] = [[self.audit["policy"]["id"], "different-version"]]
        self.assertEqual(
            self.auth(authorization_profile=profile)["decision_status"], "not_applicable"
        )

    def test_upstream_authority_replay_is_not_applicable(self):
        profile = copy.deepcopy(self.profile)
        profile["accepted_input_authorities"] = [
            [self.audit["input_authority"]["kind"], "different-input"]
        ]
        self.assertEqual(
            self.auth(authorization_profile=profile)["decision_status"], "not_applicable"
        )

    def test_authorization_invariance_actor_profile_approval_context(self):
        before_bytes = canonical_json_bytes(self.audit)
        before_identity = parse_and_validate(self.audit).semantic_identity
        cases = []

        cases.append(self.auth(actor="actor-b"))

        high_trust = copy.deepcopy(self.profile)
        high_trust["allowed_actors"].append("actor-b")
        cases.append(self.auth(actor="actor-b", authorization_profile=high_trust))

        approval_profile = copy.deepcopy(self.profile)
        approval_profile["require_human_approval"] = True
        cases.append(self.auth(authorization_profile=approval_profile, human_approval=None))
        cases.append(self.auth(authorization_profile=approval_profile, human_approval=True))

        restrictive = copy.deepcopy(self.profile)
        restrictive["required_context"] = {"environment": "prod"}
        cases.append(self.auth(authorization_profile=restrictive))
        cases.append(
            self.auth(
                authorization_profile=restrictive,
                context={"environment": "prod", "tag": "audited_verified"},
            )
        )

        self.assertIn("deny", {x["authorization"] for x in cases})
        self.assertIn("permit", {x["authorization"] for x in cases})
        self.assertIn("cannot_establish", {x["authorization"] for x in cases})
        self.assertEqual(before_bytes, canonical_json_bytes(self.audit))
        self.assertEqual(before_identity, parse_and_validate(self.audit).semantic_identity)

    def test_decision_sensitivity_core_mutations_change_identity(self):
        baseline = parse_and_validate(self.audit).semantic_identity
        mutations = []

        x = copy.deepcopy(self.audit)
        x["input_authority"]["id"] = "result-set:other"
        mutations.append(x)

        x = copy.deepcopy(self.audit)
        x["policy"]["id"] = "decision.policy.other"
        mutations.append(x)

        x = copy.deepcopy(self.audit)
        x["policy"]["version"] = "next"
        mutations.append(x)

        x = copy.deepcopy(self.audit)
        x["target"]["id"] = "ko-other"
        mutations.append(x)

        x = copy.deepcopy(self.audit)
        x["target"]["content_hash"] = "sha256:" + "8" * 64
        mutations.append(x)

        x = copy.deepcopy(self.audit)
        x["disposition"] = "HOLD"
        mutations.append(x)

        x = copy.deepcopy(self.audit)
        x["effect"] = {"type": "citation.use", "version": 1, "params": {}}
        mutations.append(x)

        x = copy.deepcopy(self.audit)
        x["effect"]["version"] = 2
        x["effect"]["params"] = {"tag": "audited_verified"}
        mutations.append(x)

        x = copy.deepcopy(self.audit)
        x["effect"]["params"]["tag"] = "other"
        # known effect param is invalid rather than a valid identity change.
        with self.assertRaises(ContractDValidationError):
            x.pop("decision_id", None)
            parse_and_validate(x)

        for mutated in mutations:
            mutated.pop("decision_id", None)
            parsed = parse_and_validate(mutated)
            self.assertNotEqual(baseline, parsed.semantic_identity)

    def test_effect_machine_parameter_changes_identity_when_semantic(self):
        base = copy.deepcopy(self.task)
        baseline = parse_and_validate(base).semantic_identity
        changed = copy.deepcopy(base)
        changed.pop("decision_id", None)
        changed["effect"]["params"]["dispatch_class"] = "standard"
        self.assertNotEqual(baseline, parse_and_validate(changed).semantic_identity)

    def test_optional_defaulted_machine_parameter_normalizes_semantic_identity(self):
        omitted = copy.deepcopy(self.citation)
        explicit = copy.deepcopy(self.citation)
        omitted.pop("decision_id", None)
        explicit.pop("decision_id", None)
        explicit["effect"]["params"]["scope"] = "same_target"
        p1 = parse_and_validate(omitted)
        p2 = parse_and_validate(explicit)
        self.assertEqual(p1.semantic_identity, p2.semantic_identity)
        self.assertNotEqual(p1.canonical_bytes, p2.canonical_bytes)

    def test_reason_explanation_diagnostics_do_not_change_semantic_identity_or_auth(self):
        baseline_id = parse_and_validate(self.audit).semantic_identity
        baseline_auth = self.auth()

        changed = copy.deepcopy(self.audit)
        changed.pop("decision_id", None)
        changed["metadata"] = {
            "reason_codes": ["COMPLETELY_DIFFERENT_REASON"],
            "explanation": "Different prose.",
            "diagnostic": {"debug": True},
        }
        changed["decision_id"] = parse_and_validate(changed).semantic_identity

        self.assertEqual(baseline_id, parse_and_validate(changed).semantic_identity)
        self.assertEqual(baseline_auth, self.auth(changed))
        self.assertNotEqual(canonical_json_bytes(self.audit), canonical_json_bytes(changed))

    def test_top_level_authorization_and_execution_injections_rejected(self):
        fields = {
            "actor": "actor-a",
            "human_approval": True,
            "requested_operation": "knowledge.apply_tag",
            "autonomy_level": "high",
            "delegation": {"to": "actor-a"},
            "automatic_execution_permission": True,
            "execution_success": True,
            "execution_receipt": "receipt-1",
        }
        for field, value in fields.items():
            x = copy.deepcopy(self.audit)
            x[field] = value
            with self.assertRaises(ContractDValidationError, msg=field):
                parse_and_validate(x)

    def test_same_injections_inside_metadata_have_no_authority(self):
        baseline_id = parse_and_validate(self.audit).semantic_identity
        baseline_auth = self.auth()
        x = copy.deepcopy(self.audit)
        x.pop("decision_id", None)
        x["metadata"].update(
            {
                "actor": "actor-b",
                "human_approval": True,
                "requested_operation": "task.dispatch",
                "autonomy_level": "unrestricted",
                "delegation": {"to": "actor-b"},
                "automatic_execution_permission": True,
                "execution_success": True,
                "execution_receipt": "fake",
            }
        )
        x["decision_id"] = parse_and_validate(x).semantic_identity
        self.assertEqual(baseline_id, parse_and_validate(x).semantic_identity)
        self.assertEqual(baseline_auth, self.auth(x))

    def test_unknown_additional_field_policy_is_strict_for_declared_version(self):
        x = copy.deepcopy(self.audit)
        x["future_top_level"] = 1
        with self.assertRaises(ContractDValidationError):
            parse_and_validate(x)

        x = copy.deepcopy(self.audit)
        x["effect"]["future_nested"] = 1
        with self.assertRaises(ContractDValidationError):
            parse_and_validate(x)

    def test_unknown_machine_parameter_for_known_effect_version_is_invalid(self):
        x = copy.deepcopy(self.citation)
        x.pop("decision_id", None)
        x["effect"]["params"]["new_machine_semantics"] = "surprise"
        with self.assertRaises(ContractDValidationError):
            parse_and_validate(x)

    def test_future_effect_version_can_carry_future_params_without_being_interpreted(self):
        parsed = parse_and_validate(self.unknown_version)
        self.assertEqual(parsed.value["effect"]["version"], 2)
        self.assertEqual(self.auth(self.unknown_version)["decision_status"], "unknown_effect")

    def test_completed_clear_to_hold_changes_authorization_eligibility(self):
        clear = self.auth()
        hold_obj = copy.deepcopy(self.audit)
        hold_obj.pop("decision_id", None)
        hold_obj["disposition"] = "HOLD"
        hold_obj["decision_id"] = parse_and_validate(hold_obj).semantic_identity
        hold = self.auth(hold_obj)
        self.assertEqual(clear["decision_status"], "candidate_for_authorization")
        self.assertEqual(hold["decision_status"], "not_candidate")

    def test_effect_switch_changes_operation_applicability(self):
        citation_profile = copy.deepcopy(self.profile)
        citation_profile["accepted_policies"] = [
            [self.citation["policy"]["id"], self.citation["policy"]["version"]]
        ]
        citation_profile["allowed_operations"] = ["citation.use"]
        citation_result = authorization_evaluate(
            self.citation,
            actor="actor-a",
            requested_operation="citation.use",
            request_target=copy.deepcopy(self.citation["target"]),
            context={"environment": "research"},
            authorization_profile=citation_profile,
        )
        self.assertEqual(citation_result["decision_status"], "candidate_for_authorization")
        replay = authorization_evaluate(
            self.citation,
            actor="actor-a",
            requested_operation="knowledge.apply_tag",
            request_target=copy.deepcopy(self.citation["target"]),
            context={"environment": "research", "tag": "audited_verified"},
            authorization_profile=citation_profile,
        )
        self.assertEqual(replay["decision_status"], "not_applicable")

    def test_field_ablation_semantic_capabilities(self):
        cases = {
            "contract_version": ("invalid", lambda x: x.pop("contract_version")),
            "input_authority.kind": ("invalid", lambda x: x["input_authority"].pop("kind")),
            "input_authority.id": ("invalid", lambda x: x["input_authority"].pop("id")),
            "policy.id": ("invalid", lambda x: x["policy"].pop("id")),
            "policy.version": ("invalid", lambda x: x["policy"].pop("version")),
            "target.kind": ("invalid", lambda x: x["target"].pop("kind")),
            "target.id": ("invalid", lambda x: x["target"].pop("id")),
            "target.content_hash": ("invalid", lambda x: x["target"].pop("content_hash")),
            "evaluation_state": ("invalid", lambda x: x.pop("evaluation_state")),
            "disposition": ("invalid", lambda x: x.pop("disposition")),
            "effect.type": ("invalid", lambda x: x["effect"].pop("type")),
            "effect.version": ("invalid", lambda x: x["effect"].pop("version")),
            "effect.params": ("invalid", lambda x: x["effect"].pop("params")),
            "effect.params.tag": ("invalid", lambda x: x["effect"]["params"].pop("tag")),
        }
        for name, (_, mutate) in cases.items():
            x = copy.deepcopy(self.audit)
            x.pop("decision_id", None)
            mutate(x)
            with self.assertRaises(ContractDValidationError, msg=name):
                parse_and_validate(x)

    def test_reason_basis_and_stored_id_ablation_do_not_remove_authority_semantics(self):
        baseline = parse_and_validate(self.audit).semantic_identity
        no_metadata = copy.deepcopy(self.audit)
        no_metadata.pop("metadata", None)
        no_metadata.pop("decision_id", None)
        parsed = parse_and_validate(no_metadata)
        self.assertEqual(parsed.semantic_identity, baseline)

        no_id = copy.deepcopy(self.audit)
        no_id.pop("decision_id")
        parsed2 = parse_and_validate(no_id)
        self.assertEqual(parsed2.semantic_identity, baseline)

    def test_stored_id_is_redundant_and_tamper_evident(self):
        x = copy.deepcopy(self.audit)
        x["decision_id"] = "sha256:" + "0" * 64
        with self.assertRaises(ContractDValidationError):
            parse_and_validate(x)

    def test_failed_evaluation_forbids_disposition_and_effect(self):
        for field, value in [
            ("disposition", "HOLD"),
            ("effect", {"type": "knowledge.tag", "version": 1, "params": {"tag": "audited_verified"}}),
        ]:
            x = copy.deepcopy(self.failed)
            x.pop("decision_id", None)
            x[field] = value
            with self.assertRaises(ContractDValidationError):
                parse_and_validate(x)

    def test_unknown_disposition_fails_closed(self):
        x = copy.deepcopy(self.audit)
        x.pop("decision_id", None)
        x["disposition"] = "FUTURE_CLEARISH"
        with self.assertRaises(ContractDValidationError):
            parse_and_validate(x)

    def test_canonicalization_deterministic_under_key_order(self):
        parsed = parse_and_validate(self.audit)
        reordered = dict(reversed(list(self.audit.items())))
        parsed2 = parse_and_validate(reordered)
        self.assertEqual(parsed.canonical_bytes, parsed2.canonical_bytes)
        self.assertEqual(parsed.semantic_identity, parsed2.semantic_identity)

    def test_producer_generates_valid_hash_bound_object(self):
        obj = produce_decision(
            input_authority={"kind": "contract_c_result_set", "id": "rs:new"},
            policy={"id": "decision.policy.task-dispatch", "version": "3"},
            target={"kind": "task", "id": "t-new", "content_hash": "sha256:" + "a" * 64},
            evaluation_state="completed",
            disposition="CLEAR",
            effect={
                "type": "task.dispatch",
                "version": 1,
                "params": {"dispatch_class": "standard"},
            },
            metadata={"reason_codes": ["NEW"]},
        )
        self.assertEqual(obj["decision_id"], parse_and_validate(obj).semantic_identity)


if __name__ == "__main__":
    unittest.main(verbosity=2)
