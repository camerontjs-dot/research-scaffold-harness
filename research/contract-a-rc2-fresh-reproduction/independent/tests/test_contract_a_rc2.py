from __future__ import annotations

import copy
import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from contract_a_rc2 import (  # noqa: E402
    ContractAValidationError,
    compute_handoff_sha256,
    parse_json,
    retrieval_targets,
    sha256_text,
    source_contract_projection,
    validate_candidate,
)


def finalize(obj):
    obj = copy.deepcopy(obj)
    obj["handoff_sha256"] = compute_handoff_sha256(obj)
    return obj


def root_only(state="not_decomposed", sources=None):
    if sources is None:
        sources = []
    return finalize(
        {
            "schema": "contract-a-wire-candidate-rc2",
            "handoff_id": "handoff-1",
            "producer": {"producer_id": "producer-1", "producer_version": "build-abc"},
            "work": {"work_id": "work-1"},
            "root_proposition": {
                "proposition_id": "root-1",
                "text": "The root proposition is exact.",
                "text_sha256": sha256_text("The root proposition is exact."),
            },
            "decomposition": {"state": state},
            "sources": sources,
            "handoff_sha256": "sha256:" + "0" * 64,
        }
    )


def declared():
    return finalize(
        {
            "schema": "contract-a-wire-candidate-rc2",
            "handoff_id": "handoff-declared",
            "producer": {"producer_id": "producer-1", "producer_version": "build-abc"},
            "work": {"work_id": "work-declared"},
            "root_proposition": {
                "proposition_id": "root-d",
                "text": "A and B are both true.",
                "text_sha256": sha256_text("A and B are both true."),
            },
            "decomposition": {
                "state": "declared",
                "decomposition_id": "decomp-1",
                "operator": "all_of",
                "children": [
                    {
                        "proposition_id": "child-a",
                        "text": "A is true.",
                        "text_sha256": sha256_text("A is true."),
                        "sequence": 1,
                    },
                    {
                        "proposition_id": "child-b",
                        "text": "B is true.",
                        "text_sha256": sha256_text("B is true."),
                        "sequence": 2,
                    },
                ],
            },
            "sources": [
                {
                    "source_id": "source-1",
                    "media_type": "text/markdown; charset=utf-8",
                    "content": "Résumé — exact source bytes after UTF-8 encoding.",
                    "content_sha256": sha256_text("Résumé — exact source bytes after UTF-8 encoding."),
                }
            ],
            "handoff_sha256": "sha256:" + "0" * 64,
        }
    )


class ContractARC2Tests(unittest.TestCase):
    def assertInvalid(self, obj):
        with self.assertRaises(ContractAValidationError):
            validate_candidate(obj)

    def test_valid_not_decomposed_with_explicit_empty_sources(self):
        obj = root_only("not_decomposed", [])
        validate_candidate(obj)
        parsed = parse_json(json.dumps(obj, ensure_ascii=False))
        self.assertEqual(parsed.supplied_sources(), [])

    def test_valid_failed_and_unknown(self):
        for state in ("failed", "unknown"):
            with self.subTest(state=state):
                validate_candidate(root_only(state))

    def test_valid_declared_all_of(self):
        obj = declared()
        validate_candidate(obj)
        self.assertEqual(obj["decomposition"]["operator"], "all_of")

    def test_whole_object_integrity_verification(self):
        obj = root_only()
        obj["work"]["work_id"] = "tampered"
        self.assertInvalid(obj)

    def test_root_and_child_text_hash_verification(self):
        obj = root_only()
        obj["root_proposition"]["text_sha256"] = sha256_text("different")
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

        obj = declared()
        obj["decomposition"]["children"][1]["text_sha256"] = sha256_text("different")
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

    def test_source_content_hash_verification(self):
        obj = declared()
        obj["sources"][0]["content"] += " tampered"
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

    def test_unknown_extra_field_rejected(self):
        obj = root_only()
        obj["extra"] = "not authority"
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

        obj = root_only()
        obj["producer"]["model_id"] = "not-contract-a"
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

    def test_missing_required_identity_rejected(self):
        obj = root_only()
        del obj["work"]["work_id"]
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

    def test_duplicate_and_invalid_child_identity_or_order_rejected(self):
        obj = declared()
        obj["decomposition"]["children"][1]["proposition_id"] = "child-a"
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

        obj = declared()
        obj["decomposition"]["children"][0]["proposition_id"] = "root-d"
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

        obj = declared()
        obj["decomposition"]["children"][1]["sequence"] = 3
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

        obj = declared()
        obj["decomposition"]["children"][1]["text"] = "A is true."
        obj["decomposition"]["children"][1]["text_sha256"] = sha256_text("A is true.")
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

    def test_duplicate_source_id_rejected_but_duplicate_content_allowed(self):
        source = {
            "source_id": "s1",
            "media_type": "text/plain; charset=utf-8",
            "content": "same",
            "content_sha256": sha256_text("same"),
        }
        obj = root_only(sources=[source, {**source, "source_id": "s2"}])
        validate_candidate(obj)

        obj = root_only(sources=[source, copy.deepcopy(source)])
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)

    def test_retrieval_targets_for_every_decomposition_state(self):
        for state in ("not_decomposed", "failed", "unknown"):
            with self.subTest(state=state):
                targets = retrieval_targets(root_only(state))
                self.assertEqual(len(targets), 1)
                self.assertEqual(targets[0]["proposition_id"], "root-1")
                self.assertEqual(targets[0]["text"], "The root proposition is exact.")
                self.assertEqual(targets[0]["decomposition_state"], state)

        targets = retrieval_targets(declared())
        self.assertEqual([t["proposition_id"] for t in targets], ["child-a", "child-b"])
        self.assertEqual([t["sequence"] for t in targets], [1, 2])
        self.assertEqual([t["text"] for t in targets], ["A is true.", "B is true."])

    def test_source_contract_projection_root_only(self):
        obj = root_only("unknown")
        projection = source_contract_projection(obj)
        self.assertEqual(projection["origin"], "source_contract")
        self.assertEqual(projection["operator"], "single")
        self.assertEqual(projection["decomposition_state"], "unknown")
        self.assertEqual(projection["reference_id"], "handoff-1")
        self.assertEqual(projection["reference_sha256"], obj["handoff_sha256"])
        self.assertEqual([a["proposition_id"] for a in projection["atoms"]], ["root-1"])

    def test_source_contract_projection_declared(self):
        obj = declared()
        projection = source_contract_projection(obj)
        self.assertEqual(projection["origin"], "source_contract")
        self.assertEqual(projection["operator"], "all_of")
        self.assertEqual(projection["reference_id"], "decomp-1")
        self.assertEqual(projection["reference_sha256"], obj["handoff_sha256"])
        self.assertEqual([a["sequence"] for a in projection["atoms"]], [1, 2])
        self.assertEqual([a["text"] for a in projection["atoms"]], ["A is true.", "B is true."])

    def test_parser_rejects_duplicate_json_members(self):
        obj = root_only()
        text = json.dumps(obj, separators=(",", ":"))
        text = text.replace('"schema":"contract-a-wire-candidate-rc2"', '"schema":"contract-a-wire-candidate-rc2","schema":"contract-a-wire-candidate-rc2"', 1)
        with self.assertRaises(ContractAValidationError):
            parse_json(text)

    def test_non_ascii_handoff_hash_uses_literal_utf8_interpretation(self):
        obj = declared()
        self.assertIn("Résumé".encode("utf-8"), __import__("contract_a_rc2").canonical_handoff_bytes(obj))
        validate_candidate(obj)

    def test_bool_is_not_integer_sequence(self):
        obj = declared()
        obj["decomposition"]["children"][0]["sequence"] = True
        obj["handoff_sha256"] = compute_handoff_sha256(obj)
        self.assertInvalid(obj)


if __name__ == "__main__":
    unittest.main()
