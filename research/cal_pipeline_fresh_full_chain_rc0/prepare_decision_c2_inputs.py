#!/usr/bin/env python3
"""Prepare exact Decision Engine C2 supported-claim inputs from canonical C2."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("contract_c2", type=Path)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--proposition-id")
    args = p.parse_args()

    raw = args.contract_c2.read_bytes()
    value = json.loads(raw.decode("utf-8"))
    propositions = value.get("propositions")
    if not isinstance(propositions, list) or not propositions:
        raise SystemExit("Contract C2 has no proposition results")

    if args.proposition_id is None:
        if len(propositions) != 1:
            raise SystemExit(
                "Contract C2 contains multiple propositions; --proposition-id is required"
            )
        row = propositions[0]
    else:
        matches = [
            row
            for row in propositions
            if row.get("proposition", {}).get("proposition_id") == args.proposition_id
        ]
        if len(matches) != 1:
            raise SystemExit("proposition id must resolve exactly once in Contract C2")
        row = matches[0]

    proposition = row["proposition"]
    proposition_id = proposition["proposition_id"]
    expected_b = value["contract_b"]
    context = {
        "proposition_id": proposition_id,
        "target": {
            "kind": "claim",
            "id": proposition_id,
            "content_sha256": proposition["content_sha256"],
        },
    }

    args.out_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.out_dir / "expected-contract-b.json", expected_b)
    write_json(args.out_dir / "decision-context.json", context)
    (args.out_dir / "contract-c2-sha256.txt").write_text(
        sha256_bytes(raw) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "contract_c2_file_sha256": sha256_bytes(raw),
                "proposition_id": proposition_id,
                "expected_contract_b": expected_b,
                "policy": "decision-engine.contract-c.supported-claim-verification@1.0.0",
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
