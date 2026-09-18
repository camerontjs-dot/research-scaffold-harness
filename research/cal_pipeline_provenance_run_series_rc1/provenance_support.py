#!/usr/bin/env python3
"""Small sealing/validation helpers for CAL provenance RC1.

Canonicalization intentionally matches the successful RC0 discriminator:
sorted JSON keys, compact separators, UTF-8, trailing newline. Attestation
identity/hash exclude attestation_id + attestation_sha256. Manifest
identity/hash exclude manifest_id + manifest_sha256.

This file does not create authority. In particular, seal-manifest only emits
a candidate manifest digest. A separately selected actor/control-plane must
pin that digest before reconstruction may treat it as a trust root.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
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


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def git_head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def require_apparatus_root(root: Path) -> None:
    actual = git_head(root)
    if actual != APPARATUS_CONTRACTS_COMMIT:
        raise SystemExit(
            "wrong apparatus-contracts checkout: "
            f"expected {APPARATUS_CONTRACTS_COMMIT}, got {actual}"
        )


def load_schema(root: Path, rel: Path) -> dict[str, Any]:
    require_apparatus_root(root)
    return json.loads((root / rel).read_text(encoding="utf-8"))


def seal_attestation(value: dict[str, Any]) -> dict[str, Any]:
    base = copy.deepcopy(value)
    base.pop("attestation_id", None)
    base.pop("attestation_sha256", None)
    digest = sha256_bytes(canonical_json_bytes(base))
    out = copy.deepcopy(base)
    out["attestation_id"] = f"attestation:sha256:{digest}"
    out["attestation_sha256"] = f"sha256:{digest}"
    return out


def seal_manifest(value: dict[str, Any]) -> dict[str, Any]:
    base = copy.deepcopy(value)
    base.pop("manifest_id", None)
    base.pop("manifest_sha256", None)
    digest = sha256_bytes(canonical_json_bytes(base))
    out = copy.deepcopy(base)
    out["manifest_id"] = f"run-manifest:sha256:{digest}"
    out["manifest_sha256"] = f"sha256:{digest}"
    return out


def manifest_digest(value: dict[str, Any]) -> str:
    base = copy.deepcopy(value)
    base.pop("manifest_id", None)
    base.pop("manifest_sha256", None)
    return sha256_bytes(canonical_json_bytes(base))


def artifact_ref(kind: str, logical_id: str, path: Path) -> dict[str, Any]:
    return {
        "kind": kind,
        "logical_id": logical_id,
        "commitments": [
            {"scheme": "sha256-bytes", "value": f"sha256:{sha256_file(path)}"}
        ],
    }


def artifact_entry(
    artifact_id: str,
    kind: str,
    logical_id: str,
    path: Path,
    *,
    locator_value: str | None = None,
    required: bool = True,
) -> dict[str, Any]:
    return {
        "artifact_id": artifact_id,
        "kind": kind,
        "logical_id": logical_id,
        "commitments": [
            {"scheme": "sha256-bytes", "value": f"sha256:{sha256_file(path)}"}
        ],
        "retention": {
            "state": "retained_verified",
            "locators": [
                {
                    "kind": "filesystem",
                    "value": locator_value if locator_value is not None else str(path),
                }
            ],
        },
        "required_for_reconstruction": required,
    }


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def cmd_seal_attestation(args: argparse.Namespace) -> int:
    root = args.apparatus_contracts_root.resolve()
    schema = load_schema(root, ATT_SCHEMA)
    value = seal_attestation(read_json(args.input))
    Draft202012Validator(schema).validate(value)
    write_json(args.output, value)
    print(value["attestation_sha256"])
    return 0


def cmd_seal_manifest(args: argparse.Namespace) -> int:
    root = args.apparatus_contracts_root.resolve()
    schema = load_schema(root, MANIFEST_SCHEMA)
    value = seal_manifest(read_json(args.input))
    Draft202012Validator(schema).validate(value)
    write_json(args.output, value)
    print(value["manifest_sha256"])
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    root = args.apparatus_contracts_root.resolve()
    kind = args.kind
    schema = load_schema(root, ATT_SCHEMA if kind == "attestation" else MANIFEST_SCHEMA)
    value = read_json(args.input)
    Draft202012Validator(schema).validate(value)
    if kind == "attestation":
        expected = seal_attestation(value)["attestation_sha256"]
        if value["attestation_sha256"] != expected:
            raise SystemExit("attestation digest mismatch")
    else:
        expected = "sha256:" + manifest_digest(value)
        if value["manifest_sha256"] != expected:
            raise SystemExit("manifest digest mismatch")
    print("OK")
    return 0


def cmd_digest(args: argparse.Namespace) -> int:
    print("sha256:" + sha256_file(args.input))
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)

    for name in ("seal-attestation", "seal-manifest"):
        s = sub.add_parser(name)
        s.add_argument("--apparatus-contracts-root", type=Path, required=True)
        s.add_argument("input", type=Path)
        s.add_argument("output", type=Path)
        s.set_defaults(func=cmd_seal_attestation if name == "seal-attestation" else cmd_seal_manifest)

    v = sub.add_parser("validate")
    v.add_argument("--apparatus-contracts-root", type=Path, required=True)
    v.add_argument("--kind", choices=("attestation", "manifest"), required=True)
    v.add_argument("input", type=Path)
    v.set_defaults(func=cmd_validate)

    d = sub.add_parser("digest")
    d.add_argument("input", type=Path)
    d.set_defaults(func=cmd_digest)
    return p


def main() -> int:
    args = parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
