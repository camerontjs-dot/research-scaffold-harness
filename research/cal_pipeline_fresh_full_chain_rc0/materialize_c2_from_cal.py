#!/usr/bin/env python3
"""Materialize exact Contract C2 from one saved canonical CAL B-side run.

This adapter does not introduce semantic judgment. It re-prepares the exact
Contract B + typed target under the pinned CAL consumer, reruns deterministic
CAL semantics, requires byte identity with the already-saved CAL result.json,
then invokes the already-qualified CAL->C2 materializer and exact C2 resolver
authority.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

CAL_AUTHORITY_HEAD = "8204417f478cfbd891499145a7edec5ee33405ad"
CAL_SEMANTIC_SHA = "847cc970642bb648dc994b929c2053b5c9d4648c"
C2_AUTHORITY_HEAD = "b42c827acb0a9fe65353354d709add0e27bab307"
RESOLVER_HEAD = "1d33e0612befcf8016816197c90c062373796df9"


def git_head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def require_head(root: Path, expected: str, label: str) -> None:
    actual = git_head(root)
    if actual != expected:
        raise SystemExit(f"{label} head mismatch: expected {expected}, got {actual}")


def load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--bundle-dir", type=Path, required=True)
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--cal-result", type=Path, required=True)
    p.add_argument("--cal-root", type=Path, required=True)
    p.add_argument("--c2-root", type=Path, required=True)
    p.add_argument("--resolver-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--receipt", type=Path, required=True)
    args = p.parse_args()

    cal_root = args.cal_root.resolve()
    c2_root = args.c2_root.resolve()
    resolver_root = args.resolver_root.resolve()
    require_head(cal_root, CAL_AUTHORITY_HEAD, "CAL")
    require_head(c2_root, C2_AUTHORITY_HEAD, "Contract C2 authority")
    require_head(resolver_root, RESOLVER_HEAD, "resolver authority")

    from claim_audit_lab.production_v1 import SEMANTIC_IMPLEMENTATION_SHA
    from claim_audit_lab.production_v1.bundle_input import prepare_contract_b_input
    from claim_audit_lab.production_v1.render import canonical_json_bytes, result_record
    from claim_audit_lab.production_v1.semantic.engine import audit

    if SEMANTIC_IMPLEMENTATION_SHA != CAL_SEMANTIC_SHA:
        raise SystemExit(
            f"CAL semantic identity mismatch: expected {CAL_SEMANTIC_SHA}, "
            f"got {SEMANTIC_IMPLEMENTATION_SHA}"
        )

    prepared = prepare_contract_b_input(args.bundle_dir.resolve(), args.target.resolve())
    context = prepared.context
    result = audit(context)

    saved_bytes = args.cal_result.read_bytes()
    saved = json.loads(saved_bytes.decode("utf-8"))
    if not isinstance(saved, dict) or not isinstance(saved.get("input"), dict):
        raise SystemExit("saved CAL result is missing canonical input binding")
    recomputed = canonical_json_bytes(
        result_record(context, result, input_binding=saved["input"])
    )
    if recomputed != saved_bytes:
        raise SystemExit(
            "recomputed exact CAL semantic result does not match saved CAL result bytes"
        )

    materializer = load_module(
        "cal_full_chain_c2_materializer",
        cal_root / "research/contract_c2_current_cal_producer_conformance_rc1/materialize.py",
    )

    sys.path.insert(0, str(c2_root))
    try:
        c2 = importlib.import_module("validators.contract_c_v2")
    finally:
        sys.path.pop(0)

    unsealed = materializer.materialize_unsealed(
        context,
        result,
        policy_resolver_commit_sha=RESOLVER_HEAD,
    )
    sealed = c2.seal(unsealed)
    c2.validate_object(sealed)
    c2.verify_contract_b_references(
        sealed,
        exact_contract_b=unsealed["contract_b"],
        evidence_index={
            (passage.source_id, passage.passage_id)
            for passage in context.evidence_world.admitted_passages
        },
    )

    resolver_path = (
        resolver_root
        / "research/contract_c2_current_cal_resolver_successor_rc0/RESOLVER.json"
    )
    resolver = json.loads(resolver_path.read_text(encoding="utf-8"))
    resolved = c2.verify_policy_resolution(
        sealed,
        independently_selected_resolver_commit_sha=RESOLVER_HEAD,
        resolver_entries=resolver["entries"],
    )

    c2_bytes = c2.canonical_bytes(sealed)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(c2_bytes)
    whole = c2.whole_object_sha256(sealed)

    receipt: dict[str, Any] = {
        "schema": "cal-full-chain-c2-materialization-receipt-v1",
        "cal_authority_head": CAL_AUTHORITY_HEAD,
        "cal_semantic_implementation_sha": CAL_SEMANTIC_SHA,
        "saved_cal_result_sha256": sha256_bytes(saved_bytes),
        "saved_cal_result_byte_identity_reproduced": True,
        "contract_b": sealed["contract_b"],
        "contract_c2_authority_head": C2_AUTHORITY_HEAD,
        "policy_resolver_authority_head": RESOLVER_HEAD,
        "resolved_policy": resolved,
        "contract_c2_result_set_id": sealed["result_set_id"],
        "contract_c2_whole_object_sha256": whole,
        "contract_c2_file_sha256": sha256_bytes(c2_bytes),
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
