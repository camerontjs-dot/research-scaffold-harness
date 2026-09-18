#!/usr/bin/env python3
"""Context-free verifier for a sealed CAL provenance run package.

The caller MUST provide an independently pinned expected manifest SHA-256.
Supplying the manifest's own declared hash is not an independent root and is
outside this verifier's qualification claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

APPARATUS_CONTRACTS_COMMIT = "1a5929295e735e351320cbd8c966dc43afed2859"
ATT_SCHEMA = Path("research/provenance-chain-v1-candidate/apparatus-attestation.schema.json")
MANIFEST_SCHEMA = Path("research/provenance-chain-v1-candidate/run-manifest.schema.json")


def canonical_json_bytes(obj: Any) -> bytes:
    return (
        json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def git_head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def manifest_digest(value: dict[str, Any]) -> str:
    base = dict(value)
    base.pop("manifest_id", None)
    base.pop("manifest_sha256", None)
    return sha256_bytes(canonical_json_bytes(base))


def attestation_digest(value: dict[str, Any]) -> str:
    base = dict(value)
    base.pop("attestation_id", None)
    base.pop("attestation_sha256", None)
    return sha256_bytes(canonical_json_bytes(base))


def expected_bytes_sha(commitments: list[dict[str, str]]) -> str | None:
    for row in commitments:
        if row["scheme"] == "sha256-bytes":
            value = row["value"]
            if re.fullmatch(r"sha256:[0-9a-f]{64}", value):
                return value.split(":", 1)[1]
    return None


def recover(entry: dict[str, Any], base: Path) -> tuple[bytes | None, str]:
    retention = entry["retention"]
    if retention["state"] in {"locator_absent", "unknown"} or not retention["locators"]:
        return None, "locator_absent"
    for locator in retention["locators"]:
        if locator["kind"] not in {"filesystem", "local_cas"}:
            continue
        p = Path(locator["value"])
        if not p.is_absolute():
            p = base / p
        if not p.exists() or not p.is_file():
            continue
        data = p.read_bytes()
        expected = expected_bytes_sha(entry["commitments"])
        if expected is not None and sha256_bytes(data) != expected:
            return None, "digest_mismatch"
        return data, "verified"
    return None, "bytes_unavailable"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=Path)
    p.add_argument("--expected-manifest-sha", required=True)
    p.add_argument("--apparatus-contracts-root", type=Path, required=True)
    p.add_argument("--out", type=Path)
    args = p.parse_args()

    expected_root = args.expected_manifest_sha.removeprefix("sha256:")
    if not re.fullmatch(r"[0-9a-f]{64}", expected_root):
        raise SystemExit("expected manifest root must be sha256:<64 hex> or <64 hex>")

    apparatus = args.apparatus_contracts_root.resolve()
    actual_apparatus = git_head(apparatus)
    if actual_apparatus != APPARATUS_CONTRACTS_COMMIT:
        raise SystemExit(
            f"wrong apparatus-contracts checkout: expected {APPARATUS_CONTRACTS_COMMIT}, "
            f"got {actual_apparatus}"
        )

    att_schema = read_json(apparatus / ATT_SCHEMA)
    manifest_schema = read_json(apparatus / MANIFEST_SCHEMA)
    manifest = read_json(args.manifest)
    Draft202012Validator(manifest_schema).validate(manifest)

    actual_root = manifest_digest(manifest)
    gaps: list[dict[str, str]] = []
    verified: list[str] = []
    attestation_verified: list[str] = []

    if actual_root != expected_root:
        result = {
            "schema": "cal-pipeline-context-free-reconstruction-result-v1",
            "status": "not_reconstructable",
            "root_verified": False,
            "expected_manifest_sha256": "sha256:" + expected_root,
            "actual_manifest_sha256": "sha256:" + actual_root,
            "verified_artifacts": [],
            "verified_attestations": [],
            "gaps": [{"artifact_id": "run_manifest", "reason": "digest_mismatch"}],
        }
    else:
        by_id = {row["artifact_id"]: row for row in manifest["artifacts"]}
        recovered: dict[str, bytes] = {}
        base = args.manifest.parent

        for artifact_id in manifest["reconstruction"]["required_artifact_ids"]:
            row = by_id.get(artifact_id)
            if row is None:
                gaps.append({"artifact_id": artifact_id, "reason": "identity_absent"})
                continue
            data, reason = recover(row, base)
            if data is None:
                gaps.append({"artifact_id": artifact_id, "reason": reason})
                continue
            recovered[artifact_id] = data
            verified.append(artifact_id)

        for stage in manifest["stages"]:
            if stage["state"] == "not_present":
                if stage["attestation_artifact_id"] is not None:
                    gaps.append(
                        {
                            "artifact_id": stage["attestation_artifact_id"],
                            "reason": "other",
                        }
                    )
                continue
            aid = stage["attestation_artifact_id"]
            if aid is None:
                gaps.append(
                    {"artifact_id": f"{stage['stage_id']}:attestation", "reason": "attestation_absent"}
                )
                continue
            data = recovered.get(aid)
            if data is None:
                row = by_id.get(aid)
                if row is None:
                    gaps.append({"artifact_id": aid, "reason": "attestation_absent"})
                    continue
                data, reason = recover(row, base)
                if data is None:
                    gaps.append({"artifact_id": aid, "reason": reason})
                    continue
            try:
                obj = json.loads(data.decode("utf-8"))
                Draft202012Validator(att_schema).validate(obj)
            except Exception:
                gaps.append({"artifact_id": aid, "reason": "schema_invalid"})
                continue
            digest = attestation_digest(obj)
            if obj["attestation_sha256"] != "sha256:" + digest:
                gaps.append({"artifact_id": aid, "reason": "digest_mismatch"})
                continue
            attestation_verified.append(aid)

        status = "reconstructable" if not gaps else ("partial" if verified else "not_reconstructable")
        result = {
            "schema": "cal-pipeline-context-free-reconstruction-result-v1",
            "status": status,
            "root_verified": True,
            "expected_manifest_sha256": "sha256:" + expected_root,
            "actual_manifest_sha256": "sha256:" + actual_root,
            "verified_artifacts": verified,
            "verified_attestations": attestation_verified,
            "gaps": gaps,
        }

    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "reconstructable" else 2


if __name__ == "__main__":
    raise SystemExit(main())
