#!/usr/bin/env python3
"""Independent RC3 consumer for frozen EB retrieval-audit packages.

Standard-library only. Implements only the structural/integrity semantics in the
frozen RC3 specification. It intentionally makes no semantic, retrieval-quality,
authentication, authorization, or production-readiness claims.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Iterable

REPORT_SCHEMA = "eb-retrieval-audit-independent-consumer-rc3-report-v1"
ENVELOPE_SCHEMA = "eb-evidence-package-envelope-v1"
SIDECAR_SCHEMA = "eb-retrieval-audit-v1"
INTEGRITY_MODE = "sha256-content-binding-only"
EXPECTED_AUTHORITY = {
    "retrieval_audit_only": True,
    "admission_authority": False,
    "semantic_judgment_authority": False,
}
SHA256_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
HEX64_RE = re.compile(r"^[0-9a-f]{64}$")

ENVELOPE_FILE = "EB_EVIDENCE_PACKAGE_ENVELOPE.json"
SIDECAR_FILE = "EB_RETRIEVAL_AUDIT.json"
CONTRACT_DIR = "contract_b"
CONTRACT_VERSION_FILE = "CONTRACT_VERSION"
SHA256SUMS_FILE = "SHA256SUMS"
BUNDLE_MANIFEST_FILE = "bundle_manifest.yaml"
FACTUAL_CONTEXT_FILE = "extensions/contract-b-factual-context-v1.json"

ENVELOPE_REQUIRED = {
    "schema",
    "case_id",
    "integrity_mode",
    "authentication_provided",
    "contract_b",
    "retrieval_audit",
}
SIDECAR_REQUIRED = {
    "schema",
    "case_id",
    "retrieval_profile_sha256",
    "candidate_history_complete",
    "authority_boundary",
    "contract_b_binding",
    "queries",
    "candidates",
    "candidate_passages",
    "count_checks",
}
QUERY_REQUIRED = {
    "query_id",
    "proposition_id",
    "proposition_role",
    "query_text",
    "retrieval_lane",
    "candidate_count",
    "retained_count",
}
CANDIDATE_REQUIRED = {
    "query_id",
    "proposition_id",
    "proposition_role",
    "retrieval_lane",
    "evidence_id",
    "source_id",
    "rank",
    "score",
    "score_kind",
    "retained",
}
PASSAGE_REQUIRED = {
    "evidence_id",
    "source_id",
    "passage_text",
    "passage_sha256",
    "source_content_sha256",
}
COUNT_REQUIRED = {"proposition_id", "candidate", "retained"}


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        + b"\n"
    )


def sha256_prefixed(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _required_keys(obj: Any, required: set[str], prefix: str, errors: set[str]) -> bool:
    if not isinstance(obj, dict):
        errors.add(f"{prefix}_not_object")
        return False
    missing = sorted(required - obj.keys())
    for key in missing:
        errors.add(f"{prefix}_missing_field:{key}")
    return not missing


def _load_json(path: Path, label: str, errors: set[str]) -> Any | None:
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        errors.add(f"missing_file:{path.name if path.parent.name != 'extensions' else FACTUAL_CONTEXT_FILE}")
        return None
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        errors.add(f"{label}_invalid_json")
        return None


def _yaml_scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            decoded = json.loads(value)
            if isinstance(decoded, str):
                return decoded
        except json.JSONDecodeError:
            pass
    return value


def parse_bundle_manifest(path: Path, errors: set[str]) -> dict[str, str] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.add(f"missing_file:{BUNDLE_MANIFEST_FILE}")
        return None
    except UnicodeDecodeError:
        errors.add("bundle_manifest_invalid_utf8")
        return None

    top: dict[str, str] = {}
    bundle_hashes: list[str] = []
    in_bundle = False
    bundle_indent: int | None = None

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = raw_line.strip()
        if indent == 0:
            in_bundle = False
            bundle_indent = None
            if stripped == "bundle:":
                in_bundle = True
                bundle_indent = 0
                continue
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                if key in ("bundle_id", "schema_version"):
                    if key in top:
                        errors.add(f"bundle_manifest_duplicate_scalar:{key}")
                    else:
                        top[key] = _yaml_scalar(value)
            continue

        if bundle_indent == 0 and in_bundle and ":" in stripped:
            key, value = stripped.split(":", 1)
            if key == "bundle_hash":
                bundle_hashes.append(_yaml_scalar(value))

    for key in ("bundle_id", "schema_version"):
        if key not in top or top[key] == "":
            errors.add(f"bundle_manifest_missing_scalar:{key}")
    if len(bundle_hashes) != 1 or bundle_hashes[0] == "":
        errors.add("bundle_manifest_bundle_hash_cardinality")

    if errors & {
        "bundle_manifest_missing_scalar:bundle_id",
        "bundle_manifest_missing_scalar:schema_version",
        "bundle_manifest_bundle_hash_cardinality",
        "bundle_manifest_duplicate_scalar:bundle_id",
        "bundle_manifest_duplicate_scalar:schema_version",
    }:
        return None
    return {
        "bundle_id": top["bundle_id"],
        "contract_b_version": top["schema_version"],
        "bundle_hash": bundle_hashes[0],
    }


def verify_sha256sums(contract_dir: Path, errors: set[str]) -> bool:
    sums_path = contract_dir / SHA256SUMS_FILE
    try:
        lines = sums_path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        errors.add(f"missing_file:{CONTRACT_DIR}/{SHA256SUMS_FILE}")
        return False
    except UnicodeDecodeError:
        errors.add("contract_b_sha256sums_invalid_utf8")
        return False

    valid = True
    seen: set[str] = set()
    for lineno, line in enumerate(lines, 1):
        if not line:
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.add(f"contract_b_sha256sums_malformed_line:{lineno}")
            valid = False
            continue
        expected, rel_text = match.groups()
        if rel_text in seen:
            errors.add(f"contract_b_sha256sums_duplicate_path:{rel_text}")
            valid = False
            continue
        seen.add(rel_text)

        pp = PurePosixPath(rel_text)
        if pp.is_absolute() or ".." in pp.parts or "." in pp.parts or rel_text.endswith("/"):
            errors.add(f"contract_b_sha256sums_invalid_path:{rel_text}")
            valid = False
            continue
        target = contract_dir.joinpath(*pp.parts)
        if not target.is_file():
            errors.add(f"contract_b_sha256sums_missing_file:{rel_text}")
            valid = False
            continue
        actual = file_sha256(target)
        if actual != expected:
            errors.add(f"contract_b_sha256_mismatch:{rel_text}")
            valid = False

    return valid


def _tuple_from_mapping(mapping: Any, prefix: str, errors: set[str]) -> dict[str, str] | None:
    if not isinstance(mapping, dict):
        errors.add(f"{prefix}_not_object")
        return None
    keys = ("bundle_id", "contract_b_version", "bundle_hash")
    ok = True
    out: dict[str, str] = {}
    for key in keys:
        value = mapping.get(key)
        if not isinstance(value, str) or value == "":
            errors.add(f"{prefix}_invalid_field:{key}")
            ok = False
        else:
            out[key] = value
    return out if ok else None


def consume_case(case_dir: Path) -> dict[str, Any]:
    case_dir = Path(case_dir)
    fallback_case_id = case_dir.name
    errors: set[str] = set()

    required_paths = [
        case_dir / ENVELOPE_FILE,
        case_dir / SIDECAR_FILE,
        case_dir / CONTRACT_DIR / CONTRACT_VERSION_FILE,
        case_dir / CONTRACT_DIR / SHA256SUMS_FILE,
        case_dir / CONTRACT_DIR / BUNDLE_MANIFEST_FILE,
        case_dir / CONTRACT_DIR / FACTUAL_CONTEXT_FILE,
    ]
    for path in required_paths:
        if not path.is_file():
            rel = path.relative_to(case_dir).as_posix()
            errors.add(f"missing_file:{rel}")

    envelope = _load_json(case_dir / ENVELOPE_FILE, "envelope", errors)
    sidecar = _load_json(case_dir / SIDECAR_FILE, "sidecar", errors)
    factual = _load_json(case_dir / CONTRACT_DIR / FACTUAL_CONTEXT_FILE, "contract_b_factual_context", errors)

    contract_sha_valid = verify_sha256sums(case_dir / CONTRACT_DIR, errors)

    envelope_sidecar_digest_valid = False
    binding_tuple_valid = False
    authority_boundary_valid = False
    candidate_passage_hashes_valid = False
    candidate_count_consistent = False
    retention_contract_b_consistent = False

    report_case_id = fallback_case_id

    env_tuple: dict[str, str] | None = None
    side_tuple: dict[str, str] | None = None
    manifest_tuple: dict[str, str] | None = parse_bundle_manifest(
        case_dir / CONTRACT_DIR / BUNDLE_MANIFEST_FILE, errors
    )

    if envelope is not None and _required_keys(envelope, ENVELOPE_REQUIRED, "envelope", errors):
        if envelope.get("schema") != ENVELOPE_SCHEMA:
            errors.add("envelope_schema_invalid")
        if envelope.get("case_id") != fallback_case_id:
            errors.add("envelope_case_id_mismatch")
        if isinstance(envelope.get("case_id"), str):
            report_case_id = envelope["case_id"]
        if envelope.get("integrity_mode") != INTEGRITY_MODE:
            errors.add("envelope_integrity_mode_invalid")
        if envelope.get("authentication_provided") is not False:
            errors.add("envelope_authentication_provided_invalid")
        env_tuple = _tuple_from_mapping(envelope.get("contract_b"), "envelope_contract_b", errors)
        retrieval = envelope.get("retrieval_audit")
        if not isinstance(retrieval, dict):
            errors.add("envelope_retrieval_audit_not_object")
        else:
            if retrieval.get("schema") != SIDECAR_SCHEMA:
                errors.add("envelope_retrieval_audit_schema_invalid")
            if not isinstance(retrieval.get("sha256"), str) or not SHA256_RE.fullmatch(retrieval.get("sha256", "")):
                errors.add("envelope_retrieval_audit_sha256_invalid")

    queries: list[Any] = []
    candidates: list[Any] = []
    passages: list[Any] = []
    count_checks: list[Any] = []

    if sidecar is not None and _required_keys(sidecar, SIDECAR_REQUIRED, "sidecar", errors):
        if sidecar.get("schema") != SIDECAR_SCHEMA:
            errors.add("sidecar_schema_invalid")
        if sidecar.get("case_id") != fallback_case_id:
            errors.add("sidecar_case_id_mismatch")
        if not isinstance(sidecar.get("retrieval_profile_sha256"), str) or not SHA256_RE.fullmatch(sidecar.get("retrieval_profile_sha256", "")):
            errors.add("sidecar_retrieval_profile_sha256_invalid")
        if sidecar.get("candidate_history_complete") is not True:
            errors.add("sidecar_candidate_history_complete_invalid")

        authority_boundary_valid = sidecar.get("authority_boundary") == EXPECTED_AUTHORITY
        if not authority_boundary_valid:
            errors.add("authority_boundary_invalid")

        side_tuple = _tuple_from_mapping(sidecar.get("contract_b_binding"), "sidecar_contract_b_binding", errors)

        for name in ("queries", "candidates", "candidate_passages", "count_checks"):
            if not isinstance(sidecar.get(name), list):
                errors.add(f"sidecar_{name}_not_array")
        if isinstance(sidecar.get("queries"), list):
            queries = sidecar["queries"]
        if isinstance(sidecar.get("candidates"), list):
            candidates = sidecar["candidates"]
        if isinstance(sidecar.get("candidate_passages"), list):
            passages = sidecar["candidate_passages"]
        if isinstance(sidecar.get("count_checks"), list):
            count_checks = sidecar["count_checks"]

        if envelope is not None and isinstance(envelope, dict):
            expected_digest = None
            retrieval = envelope.get("retrieval_audit")
            if isinstance(retrieval, dict):
                expected_digest = retrieval.get("sha256")
            actual_digest = sha256_prefixed(canonical_json_bytes(sidecar))
            envelope_sidecar_digest_valid = (
                isinstance(expected_digest, str) and actual_digest == expected_digest
            )
            if not envelope_sidecar_digest_valid:
                errors.add("envelope_sidecar_digest_mismatch")

    if envelope is not None and sidecar is not None:
        if envelope.get("case_id") != sidecar.get("case_id"):
            errors.add("envelope_sidecar_case_id_mismatch")

    contract_version: str | None = None
    try:
        version_bytes = (case_dir / CONTRACT_DIR / CONTRACT_VERSION_FILE).read_bytes()
        contract_version = version_bytes.decode("utf-8").strip(" \t\r\n\f\v")
    except FileNotFoundError:
        pass
    except UnicodeDecodeError:
        errors.add("contract_version_invalid_utf8")

    tuple_components_ok = all(x is not None for x in (env_tuple, side_tuple, manifest_tuple))
    if tuple_components_ok:
        assert env_tuple is not None and side_tuple is not None and manifest_tuple is not None
        binding_tuple_valid = env_tuple == side_tuple == manifest_tuple
        if not binding_tuple_valid:
            errors.add("binding_tuple_mismatch")
        if contract_version != manifest_tuple["contract_b_version"]:
            binding_tuple_valid = False
            errors.add("contract_version_mismatch")
        if not SHA256_RE.fullmatch(manifest_tuple["bundle_hash"]):
            binding_tuple_valid = False
            errors.add("bundle_manifest_bundle_hash_invalid")
    else:
        binding_tuple_valid = False

    query_by_id: dict[str, dict[str, Any]] = {}
    query_props: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    query_validation_ok = True
    for idx, q in enumerate(queries):
        if not _required_keys(q, QUERY_REQUIRED, f"query:{idx}", errors):
            query_validation_ok = False
            continue
        qid = q.get("query_id")
        if not isinstance(qid, str) or not qid:
            errors.add(f"query_invalid_query_id:{idx}")
            query_validation_ok = False
            continue
        if qid in query_by_id:
            errors.add(f"query_id_duplicate:{qid}")
            query_validation_ok = False
        else:
            query_by_id[qid] = q
        for field in ("proposition_id", "proposition_role", "query_text", "retrieval_lane"):
            if not isinstance(q.get(field), str):
                errors.add(f"query_invalid_field:{qid}:{field}")
                query_validation_ok = False
        for field in ("candidate_count", "retained_count"):
            if not _is_int(q.get(field)) or q[field] < 0:
                errors.add(f"query_invalid_count:{qid}:{field}")
                query_validation_ok = False
        if _is_int(q.get("candidate_count")) and _is_int(q.get("retained_count")):
            if q["retained_count"] > q["candidate_count"]:
                errors.add(f"query_retained_exceeds_candidate:{qid}")
                query_validation_ok = False
        if isinstance(q.get("proposition_id"), str):
            query_props[q["proposition_id"]].append(q)

    passage_by_evidence: dict[str, dict[str, Any]] = {}
    passage_hash_ok = True
    for idx, p in enumerate(passages):
        if not _required_keys(p, PASSAGE_REQUIRED, f"candidate_passage:{idx}", errors):
            passage_hash_ok = False
            continue
        evid = p.get("evidence_id")
        if not isinstance(evid, str) or not evid:
            errors.add(f"candidate_passage_invalid_evidence_id:{idx}")
            passage_hash_ok = False
            continue
        if evid in passage_by_evidence:
            errors.add(f"candidate_passage_evidence_id_duplicate:{evid}")
            passage_hash_ok = False
        else:
            passage_by_evidence[evid] = p
        if not isinstance(p.get("source_id"), str):
            errors.add(f"candidate_passage_invalid_source_id:{evid}")
            passage_hash_ok = False
        if not isinstance(p.get("passage_text"), str):
            errors.add(f"candidate_passage_invalid_text:{evid}")
            passage_hash_ok = False
        else:
            actual = sha256_prefixed(p["passage_text"].encode("utf-8"))
            if p.get("passage_sha256") != actual:
                errors.add(f"candidate_passage_hash_mismatch:{evid}")
                passage_hash_ok = False
        if not isinstance(p.get("passage_sha256"), str) or not SHA256_RE.fullmatch(p.get("passage_sha256", "")):
            errors.add(f"candidate_passage_sha256_invalid:{evid}")
            passage_hash_ok = False
        if not isinstance(p.get("source_content_sha256"), str) or not SHA256_RE.fullmatch(p.get("source_content_sha256", "")):
            errors.add(f"candidate_source_content_sha256_invalid:{evid}")
            passage_hash_ok = False
    candidate_passage_hashes_valid = passage_hash_ok

    candidates_by_query: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    candidate_validation_ok = True
    seen_ranks: defaultdict[str, set[int]] = defaultdict(set)
    for idx, c in enumerate(candidates):
        if not _required_keys(c, CANDIDATE_REQUIRED, f"candidate:{idx}", errors):
            candidate_validation_ok = False
            continue
        qid = c.get("query_id")
        if not isinstance(qid, str) or qid not in query_by_id:
            errors.add(f"candidate_query_unresolved:{idx}")
            candidate_validation_ok = False
        else:
            q = query_by_id[qid]
            for field in ("proposition_id", "proposition_role", "retrieval_lane"):
                if c.get(field) != q.get(field):
                    errors.add(f"candidate_query_field_mismatch:{qid}:{field}")
                    candidate_validation_ok = False
            candidates_by_query[qid].append(c)
        rank = c.get("rank")
        if not _is_int(rank) or rank <= 0:
            errors.add(f"candidate_rank_invalid:{idx}")
            candidate_validation_ok = False
        elif isinstance(qid, str):
            if rank in seen_ranks[qid]:
                errors.add(f"candidate_rank_duplicate:{qid}:{rank}")
                candidate_validation_ok = False
            seen_ranks[qid].add(rank)
        if not isinstance(c.get("retained"), bool):
            errors.add(f"candidate_retained_invalid:{idx}")
            candidate_validation_ok = False
        evid = c.get("evidence_id")
        passage = passage_by_evidence.get(evid) if isinstance(evid, str) else None
        if passage is None:
            errors.add(f"candidate_passage_unresolved:{idx}")
            candidate_validation_ok = False
        elif c.get("source_id") != passage.get("source_id"):
            errors.add(f"candidate_source_mismatch:{qid}:{evid}")
            candidate_validation_ok = False

    count_by_prop: dict[str, dict[str, Any]] = {}
    count_validation_ok = True
    for idx, cc in enumerate(count_checks):
        if not _required_keys(cc, COUNT_REQUIRED, f"count_check:{idx}", errors):
            count_validation_ok = False
            continue
        prop = cc.get("proposition_id")
        if not isinstance(prop, str) or not prop:
            errors.add(f"count_check_invalid_proposition_id:{idx}")
            count_validation_ok = False
            continue
        if prop in count_by_prop:
            errors.add(f"count_check_duplicate:{prop}")
            count_validation_ok = False
        else:
            count_by_prop[prop] = cc
        for field in ("candidate", "retained"):
            if not _is_int(cc.get(field)) or cc[field] < 0:
                errors.add(f"count_check_invalid_count:{prop}:{field}")
                count_validation_ok = False

    candidate_count_consistent = query_validation_ok and candidate_validation_ok and count_validation_ok
    for qid, q in query_by_id.items():
        matches = candidates_by_query.get(qid, [])
        observed_candidate = len(matches)
        observed_retained = sum(1 for c in matches if c.get("retained") is True)
        if q.get("candidate_count") != observed_candidate:
            errors.add(f"candidate_count_query_mismatch:{qid}")
            candidate_count_consistent = False
        if q.get("retained_count") != observed_retained:
            errors.add(f"retained_count_query_mismatch:{qid}")
            candidate_count_consistent = False
        prop = q.get("proposition_id")
        cc = count_by_prop.get(prop) if isinstance(prop, str) else None
        if cc is None:
            errors.add(f"count_check_missing:{prop}")
            candidate_count_consistent = False
        else:
            if cc.get("candidate") != observed_candidate:
                errors.add(f"candidate_count_check_mismatch:{prop}")
                candidate_count_consistent = False
            if cc.get("retained") != observed_retained:
                errors.add(f"retained_count_check_mismatch:{prop}")
                candidate_count_consistent = False

    history_identity: set[tuple[str, str]] = set()
    review_rows: list[dict[str, Any]] = []
    factual_ok = isinstance(factual, dict)
    if not factual_ok:
        errors.add("contract_b_factual_context_not_object")
    history = factual.get("history") if factual_ok else None
    if not isinstance(history, list):
        errors.add("contract_b_history_not_array")
        history = []
        factual_ok = False
    for idx, row in enumerate(history):
        if not isinstance(row, dict):
            errors.add(f"contract_b_history_row_not_object:{idx}")
            factual_ok = False
            continue
        claim_id = row.get("claim_id")
        passage_id = row.get("passage_id")
        if not isinstance(claim_id, str) or not isinstance(passage_id, str):
            errors.add(f"contract_b_history_identity_invalid:{idx}")
            factual_ok = False
            continue
        identity = (claim_id, passage_id)
        if identity in history_identity:
            errors.add(f"contract_b_history_identity_duplicate:{claim_id}:{passage_id}")
            factual_ok = False
        history_identity.add(identity)
        review_rows.append(
            {
                "claim_id": claim_id,
                "passage_id": passage_id,
                "review": row.get("review"),
            }
        )
    review_rows.sort(key=lambda r: (r["claim_id"], r["passage_id"]))

    retained_identity = {
        (c.get("proposition_id"), c.get("evidence_id"))
        for c in candidates
        if isinstance(c, dict)
        and c.get("retained") is True
        and isinstance(c.get("proposition_id"), str)
        and isinstance(c.get("evidence_id"), str)
    }
    retention_contract_b_consistent = factual_ok and retained_identity == history_identity
    if not retention_contract_b_consistent:
        errors.add("retention_contract_b_mismatch")

    aperture = factual.get("aperture") if isinstance(factual, dict) else None
    if not isinstance(aperture, list):
        errors.add("contract_b_aperture_not_array")
        candidate_count_consistent = False
    else:
        seen_aperture_claims: set[str] = set()
        for idx, row in enumerate(aperture):
            if not isinstance(row, dict):
                errors.add(f"contract_b_aperture_row_not_object:{idx}")
                candidate_count_consistent = False
                continue
            claim_id = row.get("claim_id")
            if not isinstance(claim_id, str):
                errors.add(f"contract_b_aperture_claim_id_invalid:{idx}")
                candidate_count_consistent = False
                continue
            if claim_id in seen_aperture_claims:
                errors.add(f"contract_b_aperture_claim_duplicate:{claim_id}")
                candidate_count_consistent = False
            seen_aperture_claims.add(claim_id)
            outcome = row.get("outcome")
            if not isinstance(outcome, dict) or outcome.get("state") != "known":
                continue
            value = outcome.get("value")
            if not isinstance(value, dict):
                continue
            expected_count = value.get("candidate_count")
            if not _is_int(expected_count):
                continue
            matching_queries = query_props.get(claim_id, [])
            if len(matching_queries) != 1:
                errors.add(f"aperture_query_cardinality:{claim_id}")
                candidate_count_consistent = False
                continue
            if matching_queries[0].get("candidate_count") != expected_count:
                errors.add(f"aperture_candidate_count_mismatch:{claim_id}")
                candidate_count_consistent = False

    candidate_identities: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    retained_identities: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in candidates:
        if not isinstance(c, dict):
            continue
        prop = c.get("proposition_id")
        if not isinstance(prop, str):
            continue
        identity = {
            "query_id": c.get("query_id"),
            "rank": c.get("rank"),
            "evidence_id": c.get("evidence_id"),
            "source_id": c.get("source_id"),
        }
        candidate_identities[prop].append(identity)
        if c.get("retained") is True:
            retained_identities[prop].append(dict(identity))

    def identity_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        rank = row.get("rank")
        rank_key = rank if _is_int(rank) else 10**18
        return (rank_key, str(row.get("query_id")), str(row.get("evidence_id")), str(row.get("source_id")))

    candidate_output = {
        prop: sorted(rows, key=identity_sort_key)
        for prop, rows in sorted(candidate_identities.items())
    }
    retained_output = {
        prop: sorted(rows, key=identity_sort_key)
        for prop, rows in sorted(retained_identities.items())
    }

    package_valid = not errors
    return {
        "case_id": report_case_id,
        "package_valid": package_valid,
        "errors": sorted(errors),
        "contract_b_sha256s_valid": contract_sha_valid,
        "envelope_sidecar_digest_valid": envelope_sidecar_digest_valid,
        "binding_tuple_valid": binding_tuple_valid,
        "authority_boundary_valid": authority_boundary_valid,
        "candidate_passage_hashes_valid": candidate_passage_hashes_valid,
        "candidate_count_consistent": candidate_count_consistent,
        "retention_contract_b_consistent": retention_contract_b_consistent,
        "candidate_identities_by_proposition": candidate_output,
        "retained_identities_by_proposition": retained_output,
        "contract_b_review_admission_decisions": review_rows,
    }


def list_case_dirs(packages_root: Path) -> list[Path]:
    root = Path(packages_root)
    return sorted(
        [p for p in root.iterdir() if p.is_dir()],
        key=lambda p: p.name,
    )


def runtime_info() -> dict[str, Any]:
    return {
        "python_implementation": sys.implementation.name,
        "python_version": ".".join(map(str, sys.version_info[:3])),
        "dependencies": ["python-standard-library"],
    }


def build_report(
    packages_root: Path,
    *,
    aperture_head: str,
    artifact_zip_sha256: str,
    package_archive_sha256: str,
) -> dict[str, Any]:
    cases = [consume_case(p) for p in list_case_dirs(packages_root)]
    return {
        "schema": REPORT_SCHEMA,
        "aperture_head": aperture_head,
        "artifact_zip_sha256": artifact_zip_sha256,
        "package_archive_sha256": package_archive_sha256,
        "case_count": len(cases),
        "cases": cases,
        "global_valid": all(case["package_valid"] for case in cases),
        "implementation_runtime": runtime_info(),
        "non_claims": [
            "no semantic truth/support/refutation judgment",
            "no retrieval-quality or corpus-completeness claim",
            "no production-readiness claim",
            "no authentication, authorization, signer-identity, or trusted-time claim",
        ],
    }


def deterministic_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8")
        + b"\n"
    )


def write_report(
    packages_root: Path,
    output: Path,
    *,
    aperture_head: str,
    artifact_zip_sha256: str,
    package_archive_sha256: str,
) -> dict[str, Any]:
    report = build_report(
        packages_root,
        aperture_head=aperture_head,
        artifact_zip_sha256=artifact_zip_sha256,
        package_archive_sha256=package_archive_sha256,
    )
    Path(output).write_bytes(deterministic_json_bytes(report))
    return report


def _main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packages-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--aperture-head", required=True)
    parser.add_argument("--artifact-zip-sha256", required=True)
    parser.add_argument("--package-archive-sha256", required=True)
    args = parser.parse_args(argv)
    report = write_report(
        args.packages_root,
        args.output,
        aperture_head=args.aperture_head,
        artifact_zip_sha256=args.artifact_zip_sha256,
        package_archive_sha256=args.package_archive_sha256,
    )
    return 0 if report["global_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(_main())
