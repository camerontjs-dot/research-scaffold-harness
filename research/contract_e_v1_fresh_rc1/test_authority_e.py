import copy
import hashlib
import json
import math
import unittest

from authority_e import evaluate


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def identity(value):
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def make_reference(ref_id="target", kind="object", version="v1", immutable_id="obj-1"):
    ref = {
        "ref_id": ref_id,
        "kind": kind,
        "version": version,
        "immutable_id": immutable_id,
        "identity_sha256": "sha256:" + "0" * 64,
    }
    ref["identity_sha256"] = identity({"kind": kind, "version": version, "immutable_id": immutable_id})
    return ref


def make_state(target_ref, *, subject="alice", records=None):
    if records is None:
        records = [
            {
                "id": "root",
                "basis_type": "grant",
                "subject_id": subject,
                "domain": "deploy",
                "operation": "release",
                "scope": "prod",
                "target_class": "artifact",
                "target_ref": target_ref,
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_until": "2026-12-31T23:59:59Z",
                "revoked_at": None,
                "parent_id": None,
                "delegated_by": None,
            }
        ]
    state = {
        "schema": "contract-e-authority-state-candidate-rc1",
        "authority_state_id": "sha256:" + "0" * 64,
        "records": records,
    }
    state["authority_state_id"] = identity({"schema": state["schema"], "records": state["records"]})
    return state


def make_request(state, reference, *, subject="alice", jurisdiction=None):
    if jurisdiction is None:
        jurisdiction = {
            "domain": "deploy",
            "operation": "release",
            "scope": "prod",
            "target_class": "artifact",
            "target_ref": reference["identity_sha256"],
        }
    return {
        "schema": "contract-e-authorization-request-candidate-rc1",
        "request_id": "req-1",
        "authority_state_id": state["authority_state_id"],
        "evaluation_time": "2026-06-01T12:00:00Z",
        "subject_id": subject,
        "jurisdiction": jurisdiction,
        "references": [reference],
        "supporting_artifacts": [],
        "conflicts": [],
        "residues": [],
    }


class AuthorityETests(unittest.TestCase):
    def setUp(self):
        self.ref = make_reference()
        self.state = make_state(self.ref["identity_sha256"])
        self.request = make_request(self.state, self.ref)

    def test_positive_root_grant(self):
        receipt = evaluate(self.state, self.request)
        self.assertTrue(receipt["authorized"])
        self.assertEqual(receipt["authority_basis_id"], "root")
        self.assertFalse(receipt["authority_conferring"])

    def test_positive_non_amplifying_delegation(self):
        root = copy.deepcopy(self.state["records"][0])
        root["subject_id"] = "alice"
        delegated = copy.deepcopy(root)
        delegated.update({
            "id": "d1",
            "basis_type": "delegation",
            "subject_id": "bob",
            "parent_id": "root",
            "delegated_by": "alice",
        })
        state = make_state(self.ref["identity_sha256"], records=[root, delegated])
        request = make_request(state, self.ref, subject="bob")
        receipt = evaluate(state, request)
        self.assertTrue(receipt["authorized"])
        self.assertEqual(receipt["authority_basis_id"], "d1")

    def test_authority_state_identity_tamper_fails_closed(self):
        state = copy.deepcopy(self.state)
        state["records"][0]["scope"] = "other"
        receipt = evaluate(state, self.request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("AUTHORITY_STATE_ID_MISMATCH", receipt["diagnostics"])

    def test_unknown_request_field_fails_closed(self):
        request = copy.deepcopy(self.request)
        request["resolved_conflict_ids"] = []
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("INVALID_REQUEST_SCHEMA", receipt["diagnostics"])

    def test_reference_identity_is_recomputed(self):
        request = copy.deepcopy(self.request)
        request["references"][0]["identity_sha256"] = "sha256:" + "1" * 64
        request["jurisdiction"]["target_ref"] = request["references"][0]["identity_sha256"]
        state = make_state(request["jurisdiction"]["target_ref"])
        request["authority_state_id"] = state["authority_state_id"]
        receipt = evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("INVALID_REFERENCE_IDENTITY", receipt["diagnostics"])

    def test_terminal_subject_must_match(self):
        request = copy.deepcopy(self.request)
        request["subject_id"] = "bob"
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("SUBJECT_MISMATCH", receipt["diagnostics"])

    def test_terminal_jurisdiction_must_match_exactly(self):
        request = copy.deepcopy(self.request)
        request["jurisdiction"]["scope"] = "staging"
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("JURISDICTION_MISMATCH", receipt["diagnostics"])

    def test_request_authority_state_id_must_match_supplied_state(self):
        other_ref = make_reference(immutable_id="other-target")
        other_state = make_state(other_ref["identity_sha256"])
        request = copy.deepcopy(self.request)
        request["authority_state_id"] = other_state["authority_state_id"]
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("AUTHORITY_STATE_REQUEST_MISMATCH", receipt["diagnostics"])

    def test_fractional_timestamp_comparison_preserves_all_digits(self):
        state = copy.deepcopy(self.state)
        state["records"][0]["valid_until"] = "2026-06-01T12:00:00.1234567Z"
        state["authority_state_id"] = identity({"schema": state["schema"], "records": state["records"]})
        request = make_request(state, self.ref)
        request["evaluation_time"] = "2026-06-01T12:00:00.1234568Z"
        receipt = evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("AUTHORITY_RECORD_NOT_CURRENT", receipt["diagnostics"])

    def test_relevant_unresolved_conflict_blocks_ordinary_authorization(self):
        request = copy.deepcopy(self.request)
        request["conflicts"] = [{"id": "c1", "relevant": True, "status": "unresolved"}]
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("BLOCKING_CONFLICT_OR_RESIDUE", receipt["diagnostics"])

    def test_irrelevant_blocker_does_not_block(self):
        request = copy.deepcopy(self.request)
        request["residues"] = [{"id": "r1", "relevant": False, "status": "contested"}]
        self.assertTrue(evaluate(self.state, request)["authorized"])

    def test_resolution_request_can_be_authorized_despite_relevant_blocker(self):
        ref = make_reference(kind="conflict", immutable_id="conflict-1")
        jurisdiction = {
            "domain": "resolution",
            "operation": "resolve",
            "scope": "case-1",
            "target_class": "conflict",
            "target_ref": ref["identity_sha256"],
        }
        record = {
            "id": "resolution-root",
            "basis_type": "policy",
            "subject_id": "resolver",
            **jurisdiction,
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": None,
            "revoked_at": None,
            "parent_id": None,
            "delegated_by": None,
        }
        state = make_state(ref["identity_sha256"], records=[record])
        request = make_request(state, ref, subject="resolver", jurisdiction=jurisdiction)
        request["conflicts"] = [{"id": "c1", "relevant": True, "status": "unresolved"}]
        self.assertTrue(evaluate(state, request)["authorized"])

    def test_validity_bounds_are_inclusive(self):
        request = copy.deepcopy(self.request)
        request["evaluation_time"] = "2026-01-01T00:00:00Z"
        self.assertTrue(evaluate(self.state, request)["authorized"])
        request["evaluation_time"] = "2026-12-31T23:59:59Z"
        self.assertTrue(evaluate(self.state, request)["authorized"])

    def test_revocation_effective_at_revoked_at(self):
        state = copy.deepcopy(self.state)
        state["records"][0]["revoked_at"] = "2026-06-01T12:00:00Z"
        state["authority_state_id"] = identity({"schema": state["schema"], "records": state["records"]})
        request = make_request(state, self.ref)
        receipt = evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("AUTHORITY_RECORD_NOT_CURRENT", receipt["diagnostics"])

    def test_delegation_cannot_change_scope(self):
        root = copy.deepcopy(self.state["records"][0])
        delegated = copy.deepcopy(root)
        delegated.update({
            "id": "d1",
            "basis_type": "delegation",
            "subject_id": "bob",
            "parent_id": "root",
            "delegated_by": "alice",
            "scope": "staging",
        })
        state = make_state(self.ref["identity_sha256"], records=[root, delegated])
        request = make_request(state, self.ref, subject="bob")
        request["jurisdiction"]["scope"] = "staging"
        receipt = evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("INVALID_AUTHORITY_CHAIN", receipt["diagnostics"])

    def test_duplicate_record_ids_invalidate_state(self):
        root = copy.deepcopy(self.state["records"][0])
        delegated = copy.deepcopy(root)
        delegated.update({
            "basis_type": "delegation",
            "subject_id": "bob",
            "parent_id": "root",
            "delegated_by": "alice",
        })
        state = make_state(self.ref["identity_sha256"], records=[root, delegated])
        request = make_request(state, self.ref, subject="bob")
        receipt = evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("INVALID_AUTHORITY_CHAIN", receipt["diagnostics"])

    def test_target_ref_must_resolve_to_request_reference(self):
        other_ref = make_reference(ref_id="other", immutable_id="obj-2")
        request = copy.deepcopy(self.request)
        request["references"] = [other_ref]
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("TARGET_REFERENCE_NOT_FOUND", receipt["diagnostics"])

    def test_supporting_artifact_ref_must_resolve_locally(self):
        request = copy.deepcopy(self.request)
        request["supporting_artifacts"] = [
            {"id": "s1", "artifact_type": "qualification", "ref_id": "missing"}
        ]
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("INVALID_SUPPORTING_ARTIFACT_REFERENCE", receipt["diagnostics"])

    def test_supporting_artifact_cannot_cure_subject_mismatch(self):
        support_ref = make_reference(ref_id="support", kind="qualification", immutable_id="q-1")
        request = copy.deepcopy(self.request)
        request["references"].append(support_ref)
        request["supporting_artifacts"] = [
            {"id": "s1", "artifact_type": "qualification", "ref_id": "support"}
        ]
        request["subject_id"] = "bob"
        self.assertFalse(evaluate(self.state, request)["authorized"])

    def test_malformed_timestamp_fails_closed(self):
        request = copy.deepcopy(self.request)
        request["evaluation_time"] = "2026-99-99T00:00:00Z"
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("INVALID_REQUEST_SCHEMA", receipt["diagnostics"])

    def test_cyclic_request_fails_closed_without_raising(self):
        request = copy.deepcopy(self.request)
        request["extra"] = request
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("INVALID_REQUEST_JSON", receipt["diagnostics"])

    def test_unhashable_enum_value_fails_closed_without_raising(self):
        request = copy.deepcopy(self.request)
        request["conflicts"] = [{"id": "c1", "relevant": True, "status": []}]
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIn("INVALID_REQUEST_SCHEMA", receipt["diagnostics"])

    def test_non_utf8_surrogate_fails_closed_without_raising(self):
        request = copy.deepcopy(self.request)
        request["subject_id"] = "bad\ud800"
        receipt = evaluate(self.state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIsNone(receipt["request_sha256"])
        self.assertIn("INVALID_REQUEST_JSON", receipt["diagnostics"])

    def test_unicode_canonical_identity(self):
        ref = make_reference(immutable_id="Δ-object")
        state = make_state(ref["identity_sha256"])
        request = make_request(state, ref)
        self.assertTrue(evaluate(state, request)["authorized"])

    def test_receipt_is_deterministic_and_preserves_request_lists(self):
        request = copy.deepcopy(self.request)
        request["conflicts"] = [{"id": "c1", "relevant": False, "status": "unresolved"}]
        first = evaluate(self.state, request)
        second = evaluate(self.state, request)
        self.assertEqual(first, second)
        self.assertEqual(first["preserved"]["conflicts"], request["conflicts"])


if __name__ == "__main__":
    unittest.main()
