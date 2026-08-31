import unittest
from consumer import Consumer

class TestRC3DConsumer(unittest.TestCase):
    def setUp(self):
        self.consumer = Consumer()
        self.base_registry = {
            "schema": "registry-v1",
            "records": {
                "rec-1": {
                    "id": "rec-1",
                    "type": "grant",
                    "subject_ids": ["sub-1"],
                    "authority_domain": "source_access",
                    "operations": ["source.read"],
                    "scopes": ["scope-1"],
                    "target_classes": ["class-1"],
                    "target_ids": ["tgt-1"],
                    "current": True,
                    "valid_from": "2020-01-01T00:00:00Z",
                    "valid_until": "2030-01-01T00:00:00Z"
                },
                "rec-comp": {
                    "id": "rec-comp",
                    "type": "grant",
                    "subject_ids": ["sub-1"],
                    "authority_domain": "numeric_relation",
                    "operations": ["semantic.validate_numeric"],
                    "scopes": ["scope-1"],
                    "target_classes": ["class-1"],
                    "current": True
                }
            }
        }
        self.base_envelope = {
            "subject": {"id": "sub-1", "kind": "user"},
            "authority_domain": "source_access",
            "operation": "source.read",
            "target": {"class": "class-1", "id": "tgt-1", "current_hash": "hash-1"},
            "jurisdiction": {"scope": "scope-1", "applicable": True, "current": True},
            "authority_basis": [{"type": "grant", "id": "rec-1", "current": True}],
            "evaluated_at": "2025-01-01T00:00:00Z",
            "propagation": [],
            "non_implications": []
        }
        self.base_request = {
            "kind": "envelope",
            "mode": "new_exercise",
            "registry": self.base_registry,
            "envelope": self.base_envelope
        }
    
    # ---------------------------------------------------------
    # Authority/basis tests
    # ---------------------------------------------------------
    def test_subject_substitution(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, subject={"id": "bad-sub", "kind": "user"})
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_subject_mismatch")

    def test_domain_substitution(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, authority_domain="other_domain")
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_domain_mismatch")

    def test_operation_substitution(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, operation="bad.read")
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_operation_mismatch")

    def test_scope_substitution(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, jurisdiction={"scope": "bad-scope"})
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_scope_mismatch")

    def test_target_class_substitution(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, target={"class": "bad-class", "id": "tgt-1", "current_hash": "hash-1"})
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_target_class_mismatch")

    def test_exact_target_substitution(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, target={"class": "class-1", "id": "bad-tgt", "current_hash": "hash-1"})
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_target_id_mismatch")

    def test_unresolved_basis(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, authority_basis=[{"type": "grant", "id": "not-found", "current": True}])
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "unresolvable_authority_basis")

    def test_authority_reference_type_mismatch(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, authority_basis=[{"type": "policy", "id": "rec-1", "current": True}])
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_type_mismatch")

    def test_reference_current_false(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, authority_basis=[{"type": "grant", "id": "rec-1", "current": False}])
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_not_current")

    def test_resolved_record_current_false(self):
        req = dict(self.base_request)
        reg = dict(self.base_registry)
        reg["records"]["rec-1"]["current"] = False
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_not_current")

    def test_revocation_boundary(self):
        req = dict(self.base_request)
        reg = dict(self.base_registry)
        reg["records"]["rec-1"]["revoked_at"] = "2024-01-01T00:00:00Z"
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_not_current")

    def test_validity_interval_boundaries(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, evaluated_at="2035-01-01T00:00:00Z")
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_outside_validity_interval")

    # ---------------------------------------------------------
    # Competence / warrant tests
    # ---------------------------------------------------------
    def test_competence_present_but_authority_absent(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, authority_basis=[])
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "missing_domain_authority_basis")

    def test_authority_present_but_required_competence_absent(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, authority_domain="numeric_relation", operation="semantic.validate_numeric", authority_basis=[{"type": "grant", "id": "rec-comp", "current": True}])
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "missing_required_qualification")

    def test_qualification_mismatch(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, authority_domain="numeric_relation", operation="semantic.validate_numeric", authority_basis=[{"type": "grant", "id": "rec-comp", "current": True}], competence=[{"type": "wrong_type", "id": "q1", "subject_id": "sub-1", "scope": "scope-1", "current": True}])
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "qualification_type_mismatch")

    def test_warrant_absent_where_required(self):
        req = dict(self.base_request)
        req["envelope"] = dict(self.base_envelope, authority_domain="decision_mandate", operation="decision.make", competence=[{"type": "comp", "id": "q1", "subject_id": "sub-1", "scope": "scope-1", "current": True}])
        # We need a rec for decision_mandate
        req["registry"]["records"]["rec-dec"] = {"id": "rec-dec", "type": "policy", "subject_ids": ["sub-1"], "authority_domain": "decision_mandate", "operations": ["decision.make"], "scopes": ["scope-1"], "target_classes": ["class-1"], "current": True}
        req["envelope"]["authority_basis"] = [{"type": "policy", "id": "rec-dec", "current": True}]
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "missing_required_warrant")

    def test_warrant_cross_domain(self):
        req = dict(self.base_request)
        req["registry"]["records"]["rec-dec"] = {"id": "rec-dec", "type": "policy", "subject_ids": ["sub-1"], "authority_domain": "decision_mandate", "operations": ["decision.make"], "scopes": ["scope-1"], "target_classes": ["class-1"], "current": True}
        req["envelope"] = dict(self.base_envelope, authority_domain="decision_mandate", operation="decision.make", authority_basis=[{"type": "policy", "id": "rec-dec", "current": True}], warrant=[{"type": "decision-policy-v1", "authority_domain": "other", "operation": "decision.make"}])
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "warrant_domain_mismatch")

    def test_warrant_wrong_operation(self):
        req = dict(self.base_request)
        req["registry"]["records"]["rec-dec"] = {"id": "rec-dec", "type": "policy", "subject_ids": ["sub-1"], "authority_domain": "decision_mandate", "operations": ["decision.make"], "scopes": ["scope-1"], "target_classes": ["class-1"], "current": True}
        req["envelope"] = dict(self.base_envelope, authority_domain="decision_mandate", operation="decision.make", authority_basis=[{"type": "policy", "id": "rec-dec", "current": True}], warrant=[{"type": "decision-policy-v1", "authority_domain": "decision_mandate", "operation": "other"}])
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "warrant_operation_mismatch")

    def test_warrant_stale_inapplicable(self):
        req = dict(self.base_request)
        req["registry"]["records"]["rec-dec"] = {"id": "rec-dec", "type": "policy", "subject_ids": ["sub-1"], "authority_domain": "decision_mandate", "operations": ["decision.make"], "scopes": ["scope-1"], "target_classes": ["class-1"], "current": True}
        req["envelope"] = dict(self.base_envelope, authority_domain="decision_mandate", operation="decision.make", authority_basis=[{"type": "policy", "id": "rec-dec", "current": True}], warrant=[{"type": "decision-policy-v1", "authority_domain": "decision_mandate", "operation": "decision.make", "applicable": False}])
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "warrant_inapplicable")

    def test_warrant_target_hash_mismatch(self):
        req = dict(self.base_request)
        req["registry"]["records"]["rec-dec"] = {"id": "rec-dec", "type": "policy", "subject_ids": ["sub-1"], "authority_domain": "decision_mandate", "operations": ["decision.make"], "scopes": ["scope-1"], "target_classes": ["class-1"], "current": True}
        req["envelope"] = dict(self.base_envelope, authority_domain="decision_mandate", operation="decision.make", authority_basis=[{"type": "policy", "id": "rec-dec", "current": True}], warrant=[{"type": "decision-policy-v1", "authority_domain": "decision_mandate", "operation": "decision.make", "target_hash": "bad-hash", "target_id": "tgt-1"}])
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "warrant_target_hash_mismatch")

    # ---------------------------------------------------------
    # RC3D public interface tests
    # ---------------------------------------------------------
    def test_unknown_kind_rejects(self):
        res = self.consumer.evaluate({"kind": "unknown"})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "unknown_evaluation_kind")

    def test_unknown_evaluation_mode_rejects(self):
        req = dict(self.base_request, mode="unknown_mode")
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "unknown_evaluation_mode")

    def test_full_registry_document_wrapper_positive(self):
        res = self.consumer.evaluate(self.base_request)
        self.assertEqual(res["decision"], "permit")
        
    def test_malformed_registry_wrapper_negative(self):
        req = dict(self.base_request, registry={"records": {}})
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "malformed_registry_document")

    def test_registry_key_record_id_mismatch(self):
        req = dict(self.base_request)
        req["registry"]["records"]["bad-key"] = req["registry"]["records"]["rec-1"]
        res = self.consumer.evaluate(req)
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "malformed_registry_document")

    def test_propagation_canonical_fields_positive(self):
        res = self.consumer.evaluate({"kind": "propagation", "mode": "identity_provenance_only"})
        self.assertEqual(res["decision"], "permit")

    def test_native_requested_fields_alias_rejection(self):
        res = self.consumer.evaluate({"kind": "propagation", "mode": "explicit", "requested_fields": ["a"]})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "malformed_propagation_request")

    def test_explicit_propagation_without_fields(self):
        res = self.consumer.evaluate({"kind": "propagation", "mode": "explicit"})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "malformed_propagation_request")

    def test_unknown_propagation_mode(self):
        res = self.consumer.evaluate({"kind": "propagation", "mode": "unknown"})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "unknown_propagation_mode")
        
    def test_forbidden_semantic_authority_propagation(self):
        # implicit authority fields
        res = self.consumer.evaluate({"kind": "propagation", "mode": "explicit", "fields": ["authority_domain"]})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_requires_reestablishment")

    def test_required_reestablishment_behavior(self):
        res = self.consumer.evaluate({"kind": "propagation", "mode": "explicit", "fields": ["authority_domain"], "separately_reauthorized": True})
        self.assertEqual(res["decision"], "permit")

    def test_positive_parent_authority_child_delegation_subset(self):
        parent = {"id": "p1", "authority_domain": "source_access", "operations": ["read"], "scope": ["a"], "current": True}
        child = {"id": "c1", "parent_authority_id": "p1", "authority_domain": "source_access", "operations": ["read"], "scope": ["a"], "current": True}
        res = self.consumer.evaluate({"kind": "delegation", "mode": "new_exercise", "parent": parent, "child": child})
        self.assertEqual(res["decision"], "permit")
        
    def test_parent_link_mismatch(self):
        parent = {"id": "p1", "authority_domain": "source_access", "operations": ["read"], "scope": ["a"], "current": True}
        child = {"id": "c1", "parent_authority_id": "p2", "authority_domain": "source_access", "operations": ["read"], "scope": ["a"], "current": True}
        res = self.consumer.evaluate({"kind": "delegation", "mode": "new_exercise", "parent": parent, "child": child})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "delegation_parent_mismatch")

    def test_operation_amplification(self):
        parent = {"id": "p1", "authority_domain": "source_access", "operations": ["read"], "scope": ["a"], "current": True}
        child = {"id": "c1", "parent_authority_id": "p1", "authority_domain": "source_access", "operations": ["read", "write"], "scope": ["a"], "current": True}
        res = self.consumer.evaluate({"kind": "delegation", "mode": "new_exercise", "parent": parent, "child": child})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "delegation_operation_amplification")

    def test_scope_amplification(self):
        parent = {"id": "p1", "authority_domain": "source_access", "operations": ["read"], "scope": ["a"], "current": True}
        child = {"id": "c1", "parent_authority_id": "p1", "authority_domain": "source_access", "operations": ["read"], "scope": ["a", "b"], "current": True}
        res = self.consumer.evaluate({"kind": "delegation", "mode": "new_exercise", "parent": parent, "child": child})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "delegation_scope_amplification")

    def test_expiry_amplification(self):
        parent = {"id": "p1", "authority_domain": "source_access", "operations": ["read"], "scope": ["a"], "current": True, "valid_until": "2024-01-01T00:00:00Z"}
        child = {"id": "c1", "parent_authority_id": "p1", "authority_domain": "source_access", "operations": ["read"], "scope": ["a"], "current": True, "valid_until": "2025-01-01T00:00:00Z"}
        res = self.consumer.evaluate({"kind": "delegation", "mode": "new_exercise", "parent": parent, "child": child})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "delegation_expiry_amplification")

    def test_non_current_parent_child(self):
        parent = {"id": "p1", "authority_domain": "source_access", "operations": ["read"], "scope": ["a"], "current": False}
        child = {"id": "c1", "parent_authority_id": "p1", "authority_domain": "source_access", "operations": ["read"], "scope": ["a"], "current": True}
        res = self.consumer.evaluate({"kind": "delegation", "mode": "new_exercise", "parent": parent, "child": child})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "delegation_not_current")

    def test_historical_inspection_of_prior_valid_authority(self):
        res = self.consumer.evaluate({"kind": "historical", "mode": "historical_inspection", "record": {}})
        self.assertEqual(res["decision"], "permit")

    def test_new_exercise_after_revocation(self):
        # We covered this via test_revocation_boundary
        pass
        
    def test_unknown_historical_mode_token(self):
        res = self.consumer.evaluate({"kind": "historical", "mode": "unknown", "record": {}})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "unknown_evaluation_mode")

    def test_new_exercise_historical_rejects(self):
        res = self.consumer.evaluate({"kind": "historical", "mode": "new_exercise", "record": {}})
        self.assertEqual(res["decision"], "reject")
        self.assertEqual(res["reason"], "authority_basis_not_current")

    # ---------------------------------------------------------
    # Metamorphic
    # ---------------------------------------------------------
    def test_metamorphic_payload_mutation(self):
        req1 = dict(self.base_request)
        req1["envelope"]["result"] = {"status": "positive", "confidence": 0.99}
        res1 = self.consumer.evaluate(req1)

        req2 = dict(self.base_request)
        req2["envelope"]["result"] = {"status": "negative", "reason": "failed"}
        res2 = self.consumer.evaluate(req2)
        
        self.assertEqual(res1["decision"], "permit")
        self.assertEqual(res2["decision"], "permit")
        # Authority signature hasn't changed.

if __name__ == "__main__":
    unittest.main()
