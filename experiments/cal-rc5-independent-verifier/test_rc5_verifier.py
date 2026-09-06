import base64
import copy
import hashlib
import json
import unittest

import rc5_verifier as v

SEMANTIC = r'''{"context_id":"cal.rc5.asymmetric-two-receipt.strict-comparison.v1","authority_case":{"case_id":"diagnostic:public-vector-001","execution_state":"completed","evidence_admitted":true,"authority_subject_id":"authority:subject:rc5:001","raw_source_id":"source:rc5:001","authority_subject_source_id":"source:rc5:001","raw_bundle_id":"bundle:rc5:001","authority_subject_bundle_id":"bundle:rc5:001","raw_passage_id":"passage:rc5:001","authority_subject_passage_id":"passage:rc5:001","admitted_passage_span":[0,100],"raw_claim_id":"claim:rc5:001","authority_subject_claim_id":"claim:rc5:001","target_atom_id":"atom:rc5:a-gt-b","authority_subject_atom_id":"atom:rc5:a-gt-b","proposal":{"authority_subject_id":"authority:subject:rc5:001","family":"comparison","source_span":[10,20],"extra_modifiers":[],"fields":{"lhs_entity":"A","rhs_entity":"B","comparison_direction":"greater_than"}},"assertion":{"authority_subject_id":"authority:subject:rc5:001","state":"asserted"},"operator":{"authority_subject_id":"authority:subject:rc5:001","domain":"comparison","applicability":"applicable","governed_span":[0,100],"jurisdiction_fields":["lhs_entity","rhs_entity","comparison_direction"]},"field_warrants":{"lhs_entity":{"authority_subject_id":"authority:subject:rc5:001","span":[10,12],"status":"established","value":"A"},"rhs_entity":{"authority_subject_id":"authority:subject:rc5:001","span":[13,15],"status":"established","value":"B"},"comparison_direction":{"authority_subject_id":"authority:subject:rc5:001","span":[16,20],"status":"established","value":"greater_than"}},"required_fields":["lhs_entity","rhs_entity","comparison_direction"],"composition":{"authority_subject_id":"authority:subject:rc5:001","required":false,"state":"not_required"},"aperture":{"authority_subject_id":"authority:subject:rc5:001","required":false,"state":"not_required"},"instrument_ids":["diagnostic:not-bound"],"reader_agreement_count":1},"proposition":{"claim_id":"claim:rc5:001","family":"comparison","lhs_entity":"A","rhs_entity":"B","comparison_direction":"greater_than"}}'''

ATOM = r'''{"signature_base64url":"96sPaZ-9Gm6ooyZTimJUc8f0KSaXN5KFr9qgH8wxqqzHzIgog_P_nly-6VYSG35tAPh-jU1DWmvOhKGGQF7XDQ","statement":{"atom_id":"atom:rc5:a-gt-b","atom_projection":{"admitted_passage_span":[0,100],"aperture":{"authority_subject_id":"authority:subject:rc5:001","required":false,"state":"not_required"},"assertion":{"authority_subject_id":"authority:subject:rc5:001","state":"asserted"},"authority_subject_atom_id":"atom:rc5:a-gt-b","authority_subject_bundle_id":"bundle:rc5:001","authority_subject_claim_id":"claim:rc5:001","authority_subject_id":"authority:subject:rc5:001","authority_subject_passage_id":"passage:rc5:001","authority_subject_source_id":"source:rc5:001","composition":{"authority_subject_id":"authority:subject:rc5:001","required":false,"state":"not_required"},"evidence_admitted":true,"execution_state":"completed","field_warrants":{"comparison_direction":{"authority_subject_id":"authority:subject:rc5:001","span":[16,20],"status":"established","value":"greater_than"},"lhs_entity":{"authority_subject_id":"authority:subject:rc5:001","span":[10,12],"status":"established","value":"A"},"rhs_entity":{"authority_subject_id":"authority:subject:rc5:001","span":[13,15],"status":"established","value":"B"}},"operator":{"applicability":"applicable","authority_subject_id":"authority:subject:rc5:001","domain":"comparison","governed_span":[0,100],"jurisdiction_fields":["lhs_entity","rhs_entity","comparison_direction"]},"proposal":{"authority_subject_id":"authority:subject:rc5:001","extra_modifiers":[],"family":"comparison","fields":{"comparison_direction":"greater_than","lhs_entity":"A","rhs_entity":"B"},"source_span":[10,20]},"raw_bundle_id":"bundle:rc5:001","raw_claim_id":"claim:rc5:001","raw_passage_id":"passage:rc5:001","raw_source_id":"source:rc5:001","required_fields":["lhs_entity","rhs_entity","comparison_direction"],"target_atom_id":"atom:rc5:a-gt-b"},"authority_profile_id":"CAL.RC8J/claim-bound@8e75c6782bb95c3763d06230b9c5df2b6af44054:blob:f55156e43e0c1b4a7868bc8339585b8892edda38","authority_reason":"ALL_REQUIRED_WARRANT_ESTABLISHED","authority_status":"WARRANTED","claim_id":"claim:rc5:001","context_id":"cal.rc5.asymmetric-two-receipt.strict-comparison.v1","issuer_key_id":"KA-ATOM-RC5-001","receipt_type":"CAL.AtomWarrant/v1","schema_major":1,"signature_profile":"Ed25519"},"statement_digest_sha256":"b802449edc6f517d1c24c2792dec5cc6f7af37f3657ed4259d10942f59fa637b"}'''

PROP = r'''{"signature_base64url":"1MBR7ueQlTCtqugpz5kZkNu1AmJaDPzL_Si49ueNQd1RcMPVvOwYlSTDscFz18EeZzJ68Z5FLCHlTcoMZYj4AA","statement":{"claim_id":"claim:rc5:001","claim_namespace":"cal.rc5.experimental.claims.v1","context_id":"cal.rc5.asymmetric-two-receipt.strict-comparison.v1","issuer_key_id":"KP-PROP-RC5-001","proposition_projection":{"comparison_direction":"greater_than","family":"comparison","lhs_entity":"A","rhs_entity":"B"},"receipt_type":"CAL.PropositionBinding/v1","schema_major":1,"signature_profile":"Ed25519"},"statement_digest_sha256":"babfa4c1a9c821c72331760ebc38995f0c20ada6c9b64f8cdafe8076cb74c4a7"}'''

PUBLIC_KEYS = r'''{
  "key_set_version": "cal.rc5.public-keys.v1",
  "context_id": "cal.rc5.asymmetric-two-receipt.strict-comparison.v1",
  "signature_profile": "Ed25519",
  "keys": [
    {
      "key_id": "KA-ATOM-RC5-001",
      "algorithm": "Ed25519",
      "public_key_encoding": "raw-32-byte/base64url-no-padding",
      "public_key_base64url": "7JFfnzDnDoDEBI_l_ipHhx7Km8C5K5lxHao4A5eJy4Q",
      "public_key_sha256": "e1256f1f7f3b289b0d0c9730fe4d41045dfbd80bea52d203457b36ed6e0fa1eb"
    },
    {
      "key_id": "KP-PROP-RC5-001",
      "algorithm": "Ed25519",
      "public_key_encoding": "raw-32-byte/base64url-no-padding",
      "public_key_base64url": "J9ErtlEtW19Q2QL0n2MdtM6CYGckRIyQubBW9A1Fkj0",
      "public_key_sha256": "6b76eca6c2c18aa7505c81b9fa07c0d994f597292503f846f6045ea56c45b0d5"
    }
  ]
}'''

TRUST_POLICY = r'''{
  "policy_version": "cal.rc5.trust-policy.v1",
  "context_id": "cal.rc5.asymmetric-two-receipt.strict-comparison.v1",
  "default": "DENY",
  "authorizations": [
    {
      "key_id": "KA-ATOM-RC5-001",
      "receipt_type": "CAL.AtomWarrant/v1",
      "schema_major": 1,
      "scope": {
        "context_id": "cal.rc5.asymmetric-two-receipt.strict-comparison.v1",
        "authority_profile_id": "CAL.RC8J/claim-bound@8e75c6782bb95c3763d06230b9c5df2b6af44054:blob:f55156e43e0c1b4a7868bc8339585b8892edda38"
      }
    },
    {
      "key_id": "KP-PROP-RC5-001",
      "receipt_type": "CAL.PropositionBinding/v1",
      "schema_major": 1,
      "scope": {
        "context_id": "cal.rc5.asymmetric-two-receipt.strict-comparison.v1",
        "claim_namespace": "cal.rc5.experimental.claims.v1"
      }
    }
  ]
}'''

ATOM_CANONICAL = r'''{"atom_id":"atom:rc5:a-gt-b","atom_projection":{"admitted_passage_span":[0,100],"aperture":{"authority_subject_id":"authority:subject:rc5:001","required":false,"state":"not_required"},"assertion":{"authority_subject_id":"authority:subject:rc5:001","state":"asserted"},"authority_subject_atom_id":"atom:rc5:a-gt-b","authority_subject_bundle_id":"bundle:rc5:001","authority_subject_claim_id":"claim:rc5:001","authority_subject_id":"authority:subject:rc5:001","authority_subject_passage_id":"passage:rc5:001","authority_subject_source_id":"source:rc5:001","composition":{"authority_subject_id":"authority:subject:rc5:001","required":false,"state":"not_required"},"evidence_admitted":true,"execution_state":"completed","field_warrants":{"comparison_direction":{"authority_subject_id":"authority:subject:rc5:001","span":[16,20],"status":"established","value":"greater_than"},"lhs_entity":{"authority_subject_id":"authority:subject:rc5:001","span":[10,12],"status":"established","value":"A"},"rhs_entity":{"authority_subject_id":"authority:subject:rc5:001","span":[13,15],"status":"established","value":"B"}},"operator":{"applicability":"applicable","authority_subject_id":"authority:subject:rc5:001","domain":"comparison","governed_span":[0,100],"jurisdiction_fields":["lhs_entity","rhs_entity","comparison_direction"]},"proposal":{"authority_subject_id":"authority:subject:rc5:001","extra_modifiers":[],"family":"comparison","fields":{"comparison_direction":"greater_than","lhs_entity":"A","rhs_entity":"B"},"source_span":[10,20]},"raw_bundle_id":"bundle:rc5:001","raw_claim_id":"claim:rc5:001","raw_passage_id":"passage:rc5:001","raw_source_id":"source:rc5:001","required_fields":["lhs_entity","rhs_entity","comparison_direction"],"target_atom_id":"atom:rc5:a-gt-b"},"authority_profile_id":"CAL.RC8J/claim-bound@8e75c6782bb95c3763d06230b9c5df2b6af44054:blob:f55156e43e0c1b4a7868bc8339585b8892edda38","authority_reason":"ALL_REQUIRED_WARRANT_ESTABLISHED","authority_status":"WARRANTED","claim_id":"claim:rc5:001","context_id":"cal.rc5.asymmetric-two-receipt.strict-comparison.v1","issuer_key_id":"KA-ATOM-RC5-001","receipt_type":"CAL.AtomWarrant/v1","schema_major":1,"signature_profile":"Ed25519"}'''
PROP_CANONICAL = r'''{"claim_id":"claim:rc5:001","claim_namespace":"cal.rc5.experimental.claims.v1","context_id":"cal.rc5.asymmetric-two-receipt.strict-comparison.v1","issuer_key_id":"KP-PROP-RC5-001","proposition_projection":{"comparison_direction":"greater_than","family":"comparison","lhs_entity":"A","rhs_entity":"B"},"receipt_type":"CAL.PropositionBinding/v1","schema_major":1,"signature_profile":"Ed25519"}'''


def dumped(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def recompute_digest(receipt_obj):
    receipt_obj["statement_digest_sha256"] = hashlib.sha256(v.jcs_canonicalize(receipt_obj["statement"])).hexdigest()


class RC5VerifierTests(unittest.TestCase):
    def assert_code(self, result, code):
        self.assertEqual(result["decision"], "ACCEPT" if code == "ACCEPT" else "REFUSE")
        self.assertEqual(result["code"], code)

    def test_public_jcs_bytes_exact(self):
        atom_statement = json.loads(ATOM)["statement"]
        prop_statement = json.loads(PROP)["statement"]
        self.assertEqual(v.jcs_canonicalize(atom_statement), ATOM_CANONICAL.encode())
        self.assertEqual(v.jcs_canonicalize(prop_statement), PROP_CANONICAL.encode())

    def test_jcs_utf16_property_order(self):
        obj = {"דּ":"hebrew", "😀":"emoji", "€":"euro", "ö":"latin", "":"ctrl", "1":"one", "\r":"CR"}
        expected = "{\"\\r\":\"CR\",\"1\":\"one\",\"\":\"ctrl\",\"ö\":\"latin\",\"€\":\"euro\",\"😀\":\"emoji\",\"דּ\":\"hebrew\"}"
        self.assertEqual(v.jcs_canonicalize(obj).decode(), expected)

    def test_jcs_string_escaping(self):
        obj = {"s": "\b\t\n\f\r\x00\"\\/"}
        self.assertEqual(v.jcs_canonicalize(obj), b'{"s":"\\b\\t\\n\\f\\r\\u0000\\"\\\\/"}')

    def test_known_good_atom(self):
        self.assert_code(v.verify_atom_receipt(SEMANTIC, ATOM, PUBLIC_KEYS, TRUST_POLICY), "ACCEPT")

    def test_known_good_proposition(self):
        self.assert_code(v.verify_proposition_receipt(SEMANTIC, PROP, PUBLIC_KEYS, TRUST_POLICY), "ACCEPT")

    def test_known_good_pair(self):
        result = v.verify_pair(SEMANTIC, ATOM, PROP, PUBLIC_KEYS, TRUST_POLICY)
        self.assertEqual(result, {"decision":"ACCEPT","code":"ACCEPT","claim_id":"claim:rc5:001","atom_id":"atom:rc5:a-gt-b"})

    def test_stale_bound_semantic_mutation_refused(self):
        semantic = json.loads(SEMANTIC)
        semantic["authority_case"]["execution_state"] = "stale"
        self.assert_code(v.verify_pair(dumped(semantic), ATOM, PROP, PUBLIC_KEYS, TRUST_POLICY), "ATOM_BINDING_MISMATCH")

    def test_unbound_diagnostic_semantic_mutation_still_accepts(self):
        semantic = json.loads(SEMANTIC)
        semantic["authority_case"]["reader_agreement_count"] = 999
        self.assert_code(v.verify_pair(dumped(semantic), ATOM, PROP, PUBLIC_KEYS, TRUST_POLICY), "ACCEPT")

    def test_malformed_signature_refused(self):
        atom = json.loads(ATOM)
        atom["signature_base64url"] = "not-valid"
        self.assert_code(v.verify_pair(SEMANTIC, dumped(atom), PROP, PUBLIC_KEYS, TRUST_POLICY), "SIGNATURE_INVALID_FORMAT")

    def test_format_valid_bad_signature_refused(self):
        atom = json.loads(ATOM)
        raw = bytearray(base64.urlsafe_b64decode(atom["signature_base64url"] + "=="))
        raw[0] ^= 1
        atom["signature_base64url"] = base64.urlsafe_b64encode(bytes(raw)).decode().rstrip("=")
        self.assert_code(v.verify_pair(SEMANTIC, dumped(atom), PROP, PUBLIC_KEYS, TRUST_POLICY), "SIGNATURE_INVALID")

    def test_unknown_signer_refused_before_signature(self):
        atom = json.loads(ATOM)
        atom["statement"]["issuer_key_id"] = "UNKNOWN-RC5-KEY"
        recompute_digest(atom)
        self.assert_code(v.verify_pair(SEMANTIC, dumped(atom), PROP, PUBLIC_KEYS, TRUST_POLICY), "UNKNOWN_SIGNER")

    def test_duplicate_key_refused(self):
        duplicate = ATOM[:-1] + ',"statement_digest_sha256":"' + json.loads(ATOM)["statement_digest_sha256"] + '"}'
        self.assert_code(v.verify_pair(SEMANTIC, duplicate, PROP, PUBLIC_KEYS, TRUST_POLICY), "DUPLICATE_JSON_KEY")

    def test_nested_duplicate_key_refused(self):
        marker = '"atom_id":"atom:rc5:a-gt-b"'
        duplicate = ATOM.replace(marker, marker + ',"atom_id":"atom:rc5:a-gt-b"', 1)
        self.assert_code(v.verify_pair(SEMANTIC, duplicate, PROP, PUBLIC_KEYS, TRUST_POLICY), "DUPLICATE_JSON_KEY")

    def test_wrong_request_context_refused(self):
        semantic = json.loads(SEMANTIC)
        semantic["context_id"] = "cal.rc5.wrong-context.v1"
        self.assert_code(v.verify_pair(dumped(semantic), ATOM, PROP, PUBLIC_KEYS, TRUST_POLICY), "PAIR_CONTEXT_MISMATCH")

    def test_exact_representation_inverse_refused(self):
        semantic = json.loads(SEMANTIC)
        semantic["proposition"].update({"lhs_entity":"B","rhs_entity":"A","comparison_direction":"less_than"})
        self.assert_code(v.verify_pair(dumped(semantic), ATOM, PROP, PUBLIC_KEYS, TRUST_POLICY), "PROPOSITION_BINDING_MISMATCH")

    def test_policy_is_distinct_from_key_lookup(self):
        policy = json.loads(TRUST_POLICY)
        policy["authorizations"] = []
        self.assert_code(v.verify_pair(SEMANTIC, ATOM, PROP, PUBLIC_KEYS, dumped(policy)), "UNAUTHORIZED_ISSUER_SCOPE")

    def test_digest_mismatch_precedes_signature(self):
        atom = json.loads(ATOM)
        atom["statement_digest_sha256"] = "0" * 64
        atom["signature_base64url"] = "bad"
        self.assert_code(v.verify_pair(SEMANTIC, dumped(atom), PROP, PUBLIC_KEYS, TRUST_POLICY), "STATEMENT_DIGEST_MISMATCH")

    def test_unknown_envelope_field_refused(self):
        atom = json.loads(ATOM)
        atom["extra"] = True
        self.assert_code(v.verify_pair(SEMANTIC, dumped(atom), PROP, PUBLIC_KEYS, TRUST_POLICY), "INVALID_RECEIPT_SCHEMA")

    def test_unsupported_signature_profile_refused_at_schema_stage(self):
        atom = json.loads(ATOM)
        atom["statement"]["signature_profile"] = "Other"
        recompute_digest(atom)
        self.assert_code(v.verify_pair(SEMANTIC, dumped(atom), PROP, PUBLIC_KEYS, TRUST_POLICY), "UNSUPPORTED_PROFILE")

    def test_invalid_json_refused(self):
        self.assert_code(v.verify_pair(SEMANTIC, "{", PROP, PUBLIC_KEYS, TRUST_POLICY), "INVALID_JSON")

    def test_float_in_semantic_input_refused(self):
        semantic = json.loads(SEMANTIC)
        semantic["authority_case"]["diagnostic_float"] = 1.5
        self.assert_code(v.verify_pair(dumped(semantic), ATOM, PROP, PUBLIC_KEYS, TRUST_POLICY), "INVALID_INPUT")

    def test_out_of_safe_range_integer_in_receipt_refused(self):
        atom = json.loads(ATOM)
        atom["statement"]["atom_projection"]["proposal"]["diagnostic_int"] = v.MAX_SAFE_INTEGER + 1
        self.assert_code(v.verify_pair(SEMANTIC, dumped(atom), PROP, PUBLIC_KEYS, TRUST_POLICY), "INVALID_RECEIPT_SCHEMA")


if __name__ == "__main__":
    unittest.main(verbosity=2)
