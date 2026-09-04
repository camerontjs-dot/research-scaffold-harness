import copy
import hashlib
import unittest

import authority_e


ZERO_SHA = "sha256:" + ("0" * 64)
ONE_SHA = "sha256:" + ("1" * 64)


def h(value):
    return "sha256:" + hashlib.sha256(authority_e._canonical_bytes(value)).hexdigest()


def make_reference(ref_id="target", kind="contract-d", version="v1", immutable_id="decision-1"):
    projection = {"kind": kind, "version": version, "immutable_id": immutable_id}
    return {
        "ref_id": ref_id,
        "kind": kind,
        "version": version,
        "immutable_id": immutable_id,
        "identity_sha256": h(projection),
    }


def make_state_and_request(
    *,
    subject="worker-1",
    domain="deployment",
    operation="execute",
    scope="prod/east",
    target_class="decision",
    evaluation_time="2026-09-04T12:00:00Z",
    valid_from="2026-09-04T11:00:00Z",
    valid_until="2026-09-04T13:00:00Z",
    revoked_at=None,
    delegation=False,
):
    reference = make_reference()
    target_ref = reference["identity_sha256"]
    root_subject = "delegator" if delegation else subject
    root = {
        "id": "basis-root",
        "basis_type": "grant",
        "subject_id": root_subject,
        "domain": domain,
        "operation": operation,
        "scope": scope,
        "target_class": target_class,
        "target_ref": target_ref,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "revoked_at": revoked_at,
        "parent_id": None,
        "delegated_by": None,
    }
    records = [root]
    if delegation:
        records.append({
            "id": "basis-child",
            "basis_type": "delegation",
            "subject_id": subject,
            "domain": domain,
            "operation": operation,
            "scope": scope,
            "target_class": target_class,
            "target_ref": target_ref,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "revoked_at": revoked_at,
            "parent_id": "basis-root",
            "delegated_by": "delegator",
        })
    state = {
        "schema": "contract-e-authority-state-candidate-rc3",
        "authority_state_id": ZERO_SHA,
        "records": records,
    }
    state["authority_state_id"] = h({"schema": state["schema"], "records": records})
    request = {
        "schema": "contract-e-authorization-request-candidate-rc3",
        "request_id": "request-1",
        "authority_state_id": state["authority_state_id"],
        "evaluation_time": evaluation_time,
        "subject_id": subject,
        "jurisdiction": {
            "domain": domain,
            "operation": operation,
            "scope": scope,
            "target_class": target_class,
            "target_ref": target_ref,
        },
        "references": [reference],
        "supporting_artifacts": [],
        "conflicts": [],
        "residues": [],
    }
    return state, request


def rehash_state(state):
    state["authority_state_id"] = h({k: v for k, v in state.items() if k != "authority_state_id"})


class CanonicalizationTests(unittest.TestCase):
    def test_jcs_lf_and_number_thresholds(self):
        self.assertEqual(authority_e._canonical_bytes({"n": 1e-7}), b'{"n":1e-7}\n')
        self.assertEqual(authority_e._canonical_bytes({"n": 1e-6}), b'{"n":0.000001}\n')
        self.assertEqual(
            authority_e._canonical_bytes({"n": 1e20}),
            b'{"n":100000000000000000000}\n',
        )
        self.assertEqual(authority_e._canonical_bytes({"n": 1e21}), b'{"n":1e+21}\n')
        self.assertEqual(authority_e._canonical_bytes({"n": -0.0}), b'{"n":0}\n')
        self.assertEqual(
            authority_e._canonical_bytes({"n": 333333333.33333329}),
            b'{"n":333333333.3333333}\n',
        )

    def test_unicode_utf16_key_order_and_escaping(self):
        value = {"\ue000": 1, "😀": 2, "x": "\x0f\n\\\"é"}
        expected = '{"x":"\\u000f\\n\\\\\\\"é","😀":2,"\ue000":1}\n'.encode("utf-8")
        self.assertEqual(authority_e._canonical_bytes(value), expected)

    def test_jcs_rejects_host_values_outside_domain(self):
        for value in (
            {"n": float("nan")},
            {"n": float("inf")},
            {"n": 2**53},
            {1: "non-string-key"},
            {"s": "\ud800"},
            {"x": (1, 2)},
        ):
            with self.subTest(value=repr(value)):
                self.assertIsNone(authority_e._hash_json(value))
        cyclic = []
        cyclic.append(cyclic)
        self.assertIsNone(authority_e._hash_json(cyclic))


class AuthorizationTests(unittest.TestCase):
    def test_positive_exact_authorization(self):
        state, request = make_state_and_request()
        receipt = authority_e.evaluate(state, request)
        self.assertTrue(receipt["authorized"])
        self.assertFalse(receipt["authority_conferring"])
        self.assertEqual(receipt["authority_basis_id"], "basis-root")
        self.assertEqual(receipt["claimed_authority_state_id"], state["authority_state_id"])
        self.assertEqual(receipt["recomputed_authority_state_id"], state["authority_state_id"])
        self.assertEqual(receipt["request_sha256"], h(request))

    def test_terminal_subject_and_jurisdiction_are_exact(self):
        fields = ["subject_id", "domain", "operation", "scope", "target_class", "target_ref"]
        for field in fields:
            state, request = make_state_and_request()
            if field == "subject_id":
                request[field] = "other"
            elif field == "target_ref":
                request["jurisdiction"][field] = ONE_SHA
            else:
                request["jurisdiction"][field] += "-other"
            with self.subTest(field=field):
                self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_valid_delegation_authorizes_terminal_subject(self):
        state, request = make_state_and_request(delegation=True)
        receipt = authority_e.evaluate(state, request)
        self.assertTrue(receipt["authorized"])
        self.assertEqual(receipt["authority_basis_id"], "basis-child")

    def test_invalid_delegation_links_or_amplification_deny(self):
        mutations = [
            ("parent_id", "not-root"),
            ("delegated_by", "not-delegator"),
            ("domain", "other-domain"),
            ("operation", "other-op"),
            ("scope", "other-scope"),
            ("target_class", "other-target-class"),
            ("target_ref", ONE_SHA),
            ("basis_type", "grant"),
            ("id", "basis-root"),
        ]
        for key, value in mutations:
            state, request = make_state_and_request(delegation=True)
            state["records"][1][key] = value
            rehash_state(state)
            request["authority_state_id"] = state["authority_state_id"]
            with self.subTest(key=key):
                self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_forged_claimed_state_identity_yields_dual_nonnull_ids_and_denial(self):
        state, request = make_state_and_request()
        genuine = state["authority_state_id"]
        state["authority_state_id"] = ONE_SHA if genuine != ONE_SHA else ZERO_SHA
        request["authority_state_id"] = state["authority_state_id"]
        receipt = authority_e.evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertEqual(receipt["claimed_authority_state_id"], state["authority_state_id"])
        self.assertEqual(receipt["recomputed_authority_state_id"], genuine)
        self.assertNotEqual(receipt["claimed_authority_state_id"], receipt["recomputed_authority_state_id"])

    def test_invalid_claim_syntax_is_null_but_recomputation_still_occurs(self):
        state, request = make_state_and_request()
        genuine = state["authority_state_id"]
        state["authority_state_id"] = "not-a-sha"
        receipt = authority_e.evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIsNone(receipt["claimed_authority_state_id"])
        self.assertEqual(receipt["recomputed_authority_state_id"], genuine)

    def test_canonicalizable_structurally_invalid_state_is_still_recomputed(self):
        state, request = make_state_and_request()
        state["unknown"] = "field"
        expected = h({k: v for k, v in state.items() if k != "authority_state_id"})
        receipt = authority_e.evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertEqual(receipt["recomputed_authority_state_id"], expected)

    def test_request_state_identity_binding_is_exact(self):
        state, request = make_state_and_request()
        request["authority_state_id"] = ONE_SHA if state["authority_state_id"] != ONE_SHA else ZERO_SHA
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_exact_fractional_ordering_beyond_microseconds(self):
        state, request = make_state_and_request(
            valid_from="2026-09-04T12:00:00.0000000002Z",
            evaluation_time="2026-09-04T12:00:00.00000000010Z",
            valid_until="2026-09-04T13:00:00Z",
        )
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])
        request["evaluation_time"] = "2026-09-04T12:00:00.00000000020Z"
        self.assertTrue(authority_e.evaluate(state, request)["authorized"])

    def test_valid_from_and_valid_until_are_inclusive(self):
        for eval_time in ("2026-09-04T11:00:00Z", "2026-09-04T13:00:00Z"):
            state, request = make_state_and_request(evaluation_time=eval_time)
            with self.subTest(eval_time=eval_time):
                self.assertTrue(authority_e.evaluate(state, request)["authorized"])

    def test_revocation_is_effective_at_boundary(self):
        state, request = make_state_and_request(
            evaluation_time="2026-09-04T12:00:00.1234567890119Z",
            revoked_at="2026-09-04T12:00:00.123456789012Z",
        )
        self.assertTrue(authority_e.evaluate(state, request)["authorized"])
        request["evaluation_time"] = "2026-09-04T12:00:00.1234567890120Z"
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_invalid_calendar_timestamp_denies_and_is_not_preserved_as_evaluation_time(self):
        state, request = make_state_and_request()
        request["evaluation_time"] = "2026-02-30T12:00:00Z"
        receipt = authority_e.evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIsNone(receipt["evaluation_time"])

    def test_reference_identity_integrity(self):
        state, request = make_state_and_request()
        request["references"][0]["identity_sha256"] = ONE_SHA
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_reference_ref_id_uniqueness(self):
        state, request = make_state_and_request()
        extra = make_reference(ref_id="target", kind="other", immutable_id="other")
        request["references"].append(extra)
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_target_identity_must_resolve_to_exactly_one_validated_reference(self):
        state, request = make_state_and_request()
        duplicate_identity = copy.deepcopy(request["references"][0])
        duplicate_identity["ref_id"] = "target-alias"
        request["references"].append(duplicate_identity)
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_supporting_artifact_resolves_locally_but_does_not_confer(self):
        state, request = make_state_and_request()
        request["supporting_artifacts"] = [
            {"id": "artifact-1", "artifact_type": "prior-receipt", "ref_id": "target"}
        ]
        self.assertTrue(authority_e.evaluate(state, request)["authorized"])
        request["supporting_artifacts"][0]["ref_id"] = "missing"
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])

        state2, request2 = make_state_and_request()
        request2["supporting_artifacts"] = [
            {"id": "artifact-1", "artifact_type": "claimed-authority", "ref_id": "target"}
        ]
        state2["records"][0]["subject_id"] = "someone-else"
        rehash_state(state2)
        request2["authority_state_id"] = state2["authority_state_id"]
        self.assertFalse(authority_e.evaluate(state2, request2)["authorized"])

    def test_supporting_artifact_ids_are_unique(self):
        state, request = make_state_and_request()
        artifact = {"id": "a", "artifact_type": "evidence", "ref_id": "target"}
        request["supporting_artifacts"] = [artifact, copy.deepcopy(artifact)]
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_relevant_conflict_or_residue_blocks_regardless_status(self):
        cases = [
            ("conflicts", "unresolved"),
            ("conflicts", "contested"),
            ("residues", "unresolved"),
            ("residues", "contested"),
        ]
        for list_name, status in cases:
            state, request = make_state_and_request()
            request[list_name] = [{"id": "b", "relevant": True, "status": status}]
            with self.subTest(list_name=list_name, status=status):
                self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_irrelevant_blocker_does_not_block(self):
        state, request = make_state_and_request()
        request["conflicts"] = [{"id": "b", "relevant": False, "status": "contested"}]
        self.assertTrue(authority_e.evaluate(state, request)["authorized"])

    def test_resolution_request_with_relevant_blocker_still_denied(self):
        state, request = make_state_and_request(domain="resolution", operation="resolve")
        request["conflicts"] = [{"id": "c", "relevant": True, "status": "unresolved"}]
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_blocker_ids_unique_within_each_list(self):
        state, request = make_state_and_request()
        b = {"id": "dup", "relevant": False, "status": "unresolved"}
        request["conflicts"] = [b, copy.deepcopy(b)]
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_unknown_or_missing_request_fields_fail_closed(self):
        for mutation in ("unknown", "missing"):
            state, request = make_state_and_request()
            if mutation == "unknown":
                request["unknown"] = 1
            else:
                del request["subject_id"]
            with self.subTest(mutation=mutation):
                self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_unknown_authority_record_field_fails_closed(self):
        state, request = make_state_and_request()
        state["records"][0]["extra"] = "x"
        rehash_state(state)
        request["authority_state_id"] = state["authority_state_id"]
        self.assertFalse(authority_e.evaluate(state, request)["authorized"])

    def test_structurally_valid_request_preserves_exact_deep_copies(self):
        state, request = make_state_and_request()
        request["conflicts"] = [{"id": "obs", "relevant": False, "status": "contested"}]
        receipt = authority_e.evaluate(state, request)
        self.assertEqual(receipt["preserved"]["references"], request["references"])
        self.assertEqual(receipt["preserved"]["conflicts"], request["conflicts"])
        request["references"][0]["kind"] = "mutated"
        request["conflicts"][0]["id"] = "mutated"
        self.assertNotEqual(receipt["preserved"]["references"], request["references"])
        self.assertNotEqual(receipt["preserved"]["conflicts"], request["conflicts"])

    def test_invalid_request_preserves_only_individually_schema_shaped_lists(self):
        state, request = make_state_and_request()
        request["unknown"] = "makes-request-invalid"
        request["supporting_artifacts"] = [
            {"id": "a", "artifact_type": "opaque", "ref_id": "not-resolved"}
        ]
        receipt = authority_e.evaluate(state, request)
        self.assertEqual(receipt["preserved"]["references"], request["references"])
        self.assertEqual(receipt["preserved"]["supporting_artifacts"], request["supporting_artifacts"])

        request["references"] = [{"bad": "shape"}]
        receipt2 = authority_e.evaluate(state, request)
        self.assertEqual(receipt2["preserved"]["references"], [])
        self.assertEqual(receipt2["preserved"]["supporting_artifacts"], request["supporting_artifacts"])

    def test_canonicalizable_invalid_request_still_gets_complete_request_hash(self):
        state, request = make_state_and_request()
        request["unknown"] = "x"
        receipt = authority_e.evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertEqual(receipt["request_sha256"], h(request))

    def test_noncanonicalizable_request_gets_null_request_hash(self):
        state, request = make_state_and_request()
        request["unknown"] = float("nan")
        receipt = authority_e.evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIsNone(receipt["request_sha256"])

    def test_receipt_semantic_identity_excludes_only_receipt_id_and_diagnostics(self):
        state, request = make_state_and_request()
        receipt = authority_e.evaluate(state, request)
        projection = {
            key: value for key, value in receipt.items()
            if key not in {"receipt_id", "diagnostics"}
        }
        expected = h(projection)
        self.assertEqual(receipt["receipt_id"], expected)

        altered = copy.deepcopy(receipt)
        altered["diagnostics"] = ["completely-different-diagnostic"]
        projection2 = {
            key: value for key, value in altered.items()
            if key not in {"receipt_id", "diagnostics"}
        }
        self.assertEqual(h(projection2), receipt["receipt_id"])

    def test_denial_never_carries_authority_basis(self):
        state, request = make_state_and_request()
        request["subject_id"] = "wrong"
        receipt = authority_e.evaluate(state, request)
        self.assertFalse(receipt["authorized"])
        self.assertIsNone(receipt["authority_basis_id"])
        self.assertFalse(receipt["authority_conferring"])

    def test_numeric_equivalent_fraction_forms_are_same_instant(self):
        self.assertEqual(
            authority_e._compare_timestamps(
                "2026-09-04T12:00:00.1Z", "2026-09-04T12:00:00.100000000000Z"
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
