#!/usr/bin/env python3
"""Prereveal tests for the independent RC3 consumer.

Expected identities/counts are never hard-coded. Tests derive only structural
invariants from the frozen specification and the supplied frozen package bytes.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import consumer

APERTURE_HEAD = "13959ae5a56548fc07f5c87780b44bb45bc85639"
EXPECTED_ARTIFACT_ZIP_SHA256 = "29aa32fd940937fc409880fa556d2e2d5e0e19c2a2d9f654e2c20b7fbaa2b7f1"
EXPECTED_INNER_ARCHIVE_SHA256 = "f9ef205585bf9d981fa4f4e14df28fc42c057cf7512c3a99f52263929ea73215"


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_snapshot(root: Path) -> dict[str, str]:
    return {
        p.relative_to(root).as_posix(): file_hash(p)
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    path.write_bytes(consumer.deterministic_json_bytes(value))


def reseal(case_dir: Path, sidecar: dict) -> None:
    write_json(case_dir / consumer.SIDECAR_FILE, sidecar)
    envelope_path = case_dir / consumer.ENVELOPE_FILE
    envelope = load_json(envelope_path)
    envelope["retrieval_audit"]["sha256"] = consumer.sha256_prefixed(
        consumer.canonical_json_bytes(sidecar)
    )
    write_json(envelope_path, envelope)


def matching_error(record: dict, prefix: str) -> bool:
    return any(err == prefix or err.startswith(prefix + ":") for err in record["errors"])


class IndependentConsumerPrerevealTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.packages_root = Path(os.environ["EB_RC3_PACKAGES_ROOT"]).resolve()
            cls.artifact_zip = Path(os.environ["EB_RC3_ARTIFACT_ZIP"]).resolve()
            cls.inner_archive = Path(os.environ["EB_RC3_INNER_ARCHIVE"]).resolve()
        except KeyError as exc:
            raise RuntimeError(f"missing required environment variable: {exc.args[0]}") from exc
        if not cls.packages_root.is_dir():
            raise RuntimeError("EB_RC3_PACKAGES_ROOT is not a directory")
        cls.case_dirs = consumer.list_case_dirs(cls.packages_root)
        if len(cls.case_dirs) < 2:
            raise RuntimeError("negative controls require at least two frozen cases")
        cls.before_tree = tree_snapshot(cls.packages_root)
        cls.before_zip_hash = file_hash(cls.artifact_zip)
        cls.before_archive_hash = file_hash(cls.inner_archive)

    @classmethod
    def tearDownClass(cls):
        if tree_snapshot(cls.packages_root) != cls.before_tree:
            raise AssertionError("frozen package tree changed during tests")
        if file_hash(cls.artifact_zip) != cls.before_zip_hash:
            raise AssertionError("artifact ZIP changed during tests")
        if file_hash(cls.inner_archive) != cls.before_archive_hash:
            raise AssertionError("inner archive changed during tests")

    def copy_case(self, source: Path) -> tuple[tempfile.TemporaryDirectory, Path]:
        temp = tempfile.TemporaryDirectory()
        target = Path(temp.name) / source.name
        shutil.copytree(source, target)
        return temp, target

    def test_artifact_and_archive_hashes(self):
        self.assertEqual(file_hash(self.artifact_zip), EXPECTED_ARTIFACT_ZIP_SHA256)
        self.assertEqual(file_hash(self.inner_archive), EXPECTED_INNER_ARCHIVE_SHA256)

    def test_extracted_frozen_inputs_match_inner_archive(self):
        expected_files: dict[str, str] = {}
        with tarfile.open(self.inner_archive, "r:gz") as tf:
            for member in tf.getmembers():
                if not member.isfile():
                    continue
                self.assertTrue(member.name.startswith("packages/"))
                f = tf.extractfile(member)
                self.assertIsNotNone(f)
                data = f.read()
                rel = member.name.removeprefix("packages/")
                expected_files[rel] = hashlib.sha256(data).hexdigest()
        actual_files = {
            p.relative_to(self.packages_root).as_posix(): file_hash(p)
            for p in sorted(self.packages_root.rglob("*"))
            if p.is_file()
        }
        self.assertEqual(actual_files, expected_files)

    def test_all_frozen_cases_process_and_required_invariants(self):
        for case_dir in self.case_dirs:
            with self.subTest(case=case_dir.name):
                record = consumer.consume_case(case_dir)
                self.assertTrue(record["package_valid"], record["errors"])
                self.assertEqual(record["errors"], [])
                self.assertTrue(record["contract_b_sha256s_valid"])
                self.assertTrue(record["envelope_sidecar_digest_valid"])
                self.assertTrue(record["binding_tuple_valid"])
                self.assertTrue(record["authority_boundary_valid"])
                self.assertTrue(record["candidate_passage_hashes_valid"])
                self.assertTrue(record["candidate_count_consistent"])
                self.assertTrue(record["retention_contract_b_consistent"])

                side = load_json(case_dir / consumer.SIDECAR_FILE)
                reconstructed = sum(
                    len(rows) for rows in record["candidate_identities_by_proposition"].values()
                )
                reconstructed_retained = sum(
                    len(rows) for rows in record["retained_identities_by_proposition"].values()
                )
                self.assertEqual(reconstructed, len(side["candidates"]))
                self.assertEqual(
                    reconstructed_retained,
                    sum(1 for c in side["candidates"] if c["retained"] is True),
                )
                for prop, rows in record["candidate_identities_by_proposition"].items():
                    ranks = [row["rank"] for row in rows]
                    self.assertEqual(ranks, sorted(ranks), prop)
                for prop, rows in record["retained_identities_by_proposition"].items():
                    ranks = [row["rank"] for row in rows]
                    self.assertEqual(ranks, sorted(ranks), prop)

                ext = load_json(case_dir / consumer.CONTRACT_DIR / consumer.FACTUAL_CONTEXT_FILE)
                expected_reviews = sorted(
                    [
                        {
                            "claim_id": row["claim_id"],
                            "passage_id": row["passage_id"],
                            "review": row.get("review"),
                        }
                        for row in ext["history"]
                    ],
                    key=lambda r: (r["claim_id"], r["passage_id"]),
                )
                self.assertEqual(record["contract_b_review_admission_decisions"], expected_reviews)

    def test_sidecar_canonicalization_matches_envelope(self):
        for case_dir in self.case_dirs:
            with self.subTest(case=case_dir.name):
                side = load_json(case_dir / consumer.SIDECAR_FILE)
                env = load_json(case_dir / consumer.ENVELOPE_FILE)
                actual = consumer.sha256_prefixed(consumer.canonical_json_bytes(side))
                self.assertEqual(actual, env["retrieval_audit"]["sha256"])
                self.assertTrue(actual.startswith("sha256:"))
                self.assertEqual(len(actual), len("sha256:") + 64)

    def test_report_generation_is_deterministic(self):
        kwargs = dict(
            aperture_head=APERTURE_HEAD,
            artifact_zip_sha256=EXPECTED_ARTIFACT_ZIP_SHA256,
            package_archive_sha256=EXPECTED_INNER_ARCHIVE_SHA256,
        )
        first = consumer.build_report(self.packages_root, **kwargs)
        second = consumer.build_report(self.packages_root, **kwargs)
        self.assertEqual(first, second)
        self.assertEqual(
            consumer.deterministic_json_bytes(first),
            consumer.deterministic_json_bytes(second),
        )
        self.assertTrue(first["global_valid"])
        self.assertEqual(first["case_count"], len(self.case_dirs))

    def test_sidecar_review_like_data_cannot_override_contract_b(self):
        source = self.case_dirs[0]
        temp, case_dir = self.copy_case(source)
        try:
            baseline = consumer.consume_case(case_dir)["contract_b_review_admission_decisions"]
            side = load_json(case_dir / consumer.SIDECAR_FILE)
            side["claimed_review_admission_state"] = {
                "authority": "sidecar",
                "decision": "forged-placeholder",
            }
            if side["candidates"]:
                side["candidates"][0]["review"] = {"decision": "forged-placeholder"}
            reseal(case_dir, side)
            record = consumer.consume_case(case_dir)
            self.assertTrue(record["package_valid"], record["errors"])
            self.assertEqual(record["contract_b_review_admission_decisions"], baseline)
        finally:
            temp.cleanup()

    def test_negative_1_unsealed_sidecar_mutation_detected(self):
        source = self.case_dirs[0]
        temp, case_dir = self.copy_case(source)
        try:
            side_path = case_dir / consumer.SIDECAR_FILE
            side = load_json(side_path)
            replacement = "sha256:" + "0" * 64
            if side["retrieval_profile_sha256"] == replacement:
                replacement = "sha256:" + "1" * 64
            side["retrieval_profile_sha256"] = replacement
            write_json(side_path, side)
            record = consumer.consume_case(case_dir)
            self.assertFalse(record["package_valid"])
            self.assertIn("envelope_sidecar_digest_mismatch", record["errors"])
            self.assertFalse(record["envelope_sidecar_digest_valid"])
        finally:
            temp.cleanup()

    def test_negative_2_swapped_sidecar_detected(self):
        source_a, source_b = self.case_dirs[:2]
        temp, case_dir = self.copy_case(source_a)
        try:
            shutil.copyfile(
                source_b / consumer.SIDECAR_FILE,
                case_dir / consumer.SIDECAR_FILE,
            )
            record = consumer.consume_case(case_dir)
            self.assertFalse(record["package_valid"])
            self.assertIn("envelope_sidecar_digest_mismatch", record["errors"])
            self.assertFalse(record["envelope_sidecar_digest_valid"])
        finally:
            temp.cleanup()

    def test_negative_3_contract_b_listed_file_mutation_detected(self):
        source = self.case_dirs[0]
        temp, case_dir = self.copy_case(source)
        try:
            sums = (case_dir / consumer.CONTRACT_DIR / consumer.SHA256SUMS_FILE).read_text(
                encoding="utf-8"
            ).splitlines()
            paths = [line.split("  ", 1)[1] for line in sums if "  " in line]
            excluded = {
                consumer.CONTRACT_VERSION_FILE,
                consumer.BUNDLE_MANIFEST_FILE,
                consumer.FACTUAL_CONTEXT_FILE,
            }
            chosen = next((p for p in paths if p not in excluded), paths[0])
            target = case_dir / consumer.CONTRACT_DIR / chosen
            target.write_bytes(target.read_bytes() + b"\nRC3_NEGATIVE_CONTROL_3\n")
            record = consumer.consume_case(case_dir)
            self.assertFalse(record["package_valid"])
            self.assertIn(f"contract_b_sha256_mismatch:{chosen}", record["errors"])
            self.assertFalse(record["contract_b_sha256s_valid"])
        finally:
            temp.cleanup()

    def test_negative_4_resealed_retained_flip_detected_by_contract_b_history(self):
        source = self.case_dirs[0]
        temp, case_dir = self.copy_case(source)
        try:
            side = load_json(case_dir / consumer.SIDECAR_FILE)
            candidate = side["candidates"][0]
            candidate["retained"] = not candidate["retained"]
            qid = candidate["query_id"]
            prop = candidate["proposition_id"]
            q_candidates = [c for c in side["candidates"] if c["query_id"] == qid]
            observed_retained = sum(1 for c in q_candidates if c["retained"] is True)
            for q in side["queries"]:
                if q["query_id"] == qid:
                    q["retained_count"] = observed_retained
            for cc in side["count_checks"]:
                if cc["proposition_id"] == prop:
                    cc["retained"] = observed_retained
            reseal(case_dir, side)

            record = consumer.consume_case(case_dir)
            self.assertFalse(record["package_valid"])
            self.assertTrue(record["envelope_sidecar_digest_valid"])
            self.assertIn("retention_contract_b_mismatch", record["errors"])
            self.assertFalse(record["retention_contract_b_consistent"])
            self.assertFalse(matching_error(record, "retained_count_query_mismatch"))
            self.assertFalse(matching_error(record, "retained_count_check_mismatch"))
        finally:
            temp.cleanup()

    def test_negative_5_resealed_candidate_removal_detected_by_contract_b_aperture(self):
        source = self.case_dirs[0]
        temp, case_dir = self.copy_case(source)
        try:
            side = load_json(case_dir / consumer.SIDECAR_FILE)
            remove_index = next(
                (i for i, c in enumerate(side["candidates"]) if c["retained"] is False),
                0,
            )
            removed = side["candidates"].pop(remove_index)
            qid = removed["query_id"]
            prop = removed["proposition_id"]
            q_candidates = [c for c in side["candidates"] if c["query_id"] == qid]
            observed_candidate = len(q_candidates)
            observed_retained = sum(1 for c in q_candidates if c["retained"] is True)
            for q in side["queries"]:
                if q["query_id"] == qid:
                    q["candidate_count"] = observed_candidate
                    q["retained_count"] = observed_retained
            for cc in side["count_checks"]:
                if cc["proposition_id"] == prop:
                    cc["candidate"] = observed_candidate
                    cc["retained"] = observed_retained
            reseal(case_dir, side)

            record = consumer.consume_case(case_dir)
            self.assertFalse(record["package_valid"])
            self.assertTrue(record["envelope_sidecar_digest_valid"])
            self.assertTrue(matching_error(record, "aperture_candidate_count_mismatch"))
            self.assertFalse(matching_error(record, "candidate_count_query_mismatch"))
            self.assertFalse(matching_error(record, "candidate_count_check_mismatch"))
            self.assertFalse(matching_error(record, "retained_count_query_mismatch"))
            self.assertFalse(matching_error(record, "retained_count_check_mismatch"))
        finally:
            temp.cleanup()

    def test_negative_6_resealed_authority_claim_detected(self):
        source = self.case_dirs[0]
        temp, case_dir = self.copy_case(source)
        try:
            side = load_json(case_dir / consumer.SIDECAR_FILE)
            side["authority_boundary"]["semantic_judgment_authority"] = True
            reseal(case_dir, side)
            record = consumer.consume_case(case_dir)
            self.assertFalse(record["package_valid"])
            self.assertTrue(record["envelope_sidecar_digest_valid"])
            self.assertIn("authority_boundary_invalid", record["errors"])
            self.assertFalse(record["authority_boundary_valid"])
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
