#!/usr/bin/env python3
"""Materialize exact Gate V1 input packets from the frozen EB challenge corpus.

This helper is preparation-only. It does not run Gate, EB, CAL, or Decision.
It refuses to read the benchmark from any EB checkout other than the exact
frozen integration commit used by this run series.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

EB_COMMIT = "4e1f6fe00e7c350b28f52bfea14f1f8988847884"
CORPUS = Path("benchmarks/eb-challenge-corpus-v1")
CASES = {
    "rimebridge-simple-support": ("case-dev-claim-001-a0", "ordinary_window"),
    "amberbraid-temporal-supersession": ("case-dev-claim-017-a0", "full"),
    "wick-missing-decisive": ("case-dev-claim-049-a0", "bounded_missing_decisive"),
}


def git_head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
    ).strip()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("series_case_id", choices=sorted(CASES))
    p.add_argument("--evidence-bundler-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    eb_root = args.evidence_bundler_root.resolve()
    actual = git_head(eb_root)
    if actual != EB_COMMIT:
        raise SystemExit(
            f"refusing non-frozen EB checkout: expected {EB_COMMIT}, got {actual}"
        )

    case_id, subset_id = CASES[args.series_case_id]
    corpus_root = eb_root / CORPUS
    cases = {row["case_id"]: row for row in load_jsonl(corpus_root / "cases/dev_cases.jsonl")}
    if case_id not in cases:
        raise SystemExit(f"missing frozen benchmark case {case_id}")
    case = cases[case_id]

    subsets_doc = load_json(corpus_root / "aperture/subsets.json")
    subsets = {row["subset_id"]: row for row in subsets_doc["subsets"]}
    if subset_id not in subsets:
        raise SystemExit(f"missing frozen subset {subset_id}")
    subset = subsets[subset_id]

    sources = []
    source_metadata = []
    for source_id in subset["source_ids"]:
        source_dir = corpus_root / "sources" / source_id
        metadata = load_json(source_dir / "metadata.json")
        content_bytes = (source_dir / metadata["content_path"]).read_bytes()
        if sha256(content_bytes) != metadata["content_hash"]:
            raise SystemExit(f"content hash mismatch for {source_id}")
        content = content_bytes.decode(metadata.get("content_encoding", "utf-8"))
        sources.append(
            {
                "source_id": source_id,
                "media_type": "text/plain",
                "content": content,
            }
        )
        meta_row: dict[str, Any] = {
            "source_id": source_id,
            "provenance": (
                f"Frozen EB challenge corpus {source_id} at "
                f"camerontjs-dot/evidence-bundler@{EB_COMMIT}"
            ),
            "source_role": "frozen_benchmark_source",
            "authority_basis": "content-addressed synthetic benchmark fixture",
            "document_type": metadata.get("document_type", "unknown"),
            "evidence_form": "document_text",
            "version": str(metadata.get("version", "unknown")),
            "currency_state": str(metadata.get("status", "unknown")),
        }
        temporal = metadata.get("effective_date") or metadata.get("publication_date")
        if temporal:
            meta_row["temporal_coverage"] = str(temporal)
        source_metadata.append(meta_row)

    if args.series_case_id == "wick-missing-decisive":
        gaps_state = "declared_some"
        gaps = [
            "The frozen bounded_missing_decisive subset intentionally omits src-wickarchive-current."
        ]
    else:
        gaps_state = "declared_none"
        gaps = []

    packet = {
        "request": {
            "handoff_id": f"provenance-rc1-{args.series_case_id}",
            "producer_id": "cal-pipeline-provenance-run-series-rc1",
            "producer_version": "2026-09-17",
            "work_id": f"provenance-rc1-{args.series_case_id}",
            "root_id": case["original_claim_id"],
            "root_text": case["claim_text"],
            "sources": sources,
        },
        "evidence_task": {
            "verification_world": "closed",
            "corpus_scope": (
                f"Exact frozen EB challenge corpus subset {subset_id} at "
                f"{EB_COMMIT}; source-list commitment {subset['source_list_sha256']}."
            ),
            "completeness_state": "complete_for_declared_frozen_subset",
            "known_gaps_state": gaps_state,
            "known_gaps": gaps,
        },
        "source_metadata": source_metadata,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "series_case_id": args.series_case_id,
                "benchmark_case_id": case_id,
                "subset_id": subset_id,
                "source_count": len(sources),
                "source_list_sha256": subset["source_list_sha256"],
                "packet_sha256": "sha256:" + sha256(args.out.read_bytes()),
                "out": str(args.out),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
