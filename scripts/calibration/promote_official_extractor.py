#!/usr/bin/env python3
"""Re-point matrix-v2 cells' official extractor stub -> Nemo (no regeneration).

Consumes the 2026-05-31 round-2 calibration decision (Mistral Nemo = official
extractor, F1 0.8916). For each ``scaffold-run-*`` cell this:

  1. promotes the frozen Nemo sidecar
     (``intermediates/claims_extractor_nemo.yaml``) to the official
     ``claims.yaml`` -- re-stamping the registry's run_id + write timestamp so
     it stays aligned with the run disposition, exactly as the writer bridge
     would have done had Nemo been official at write time;
  2. recomputes ``run_disposition.yaml`` through the writer bridge's own
     disposition gate (``build_run_disposition_fields``) -- claim count from the
     Nemo sidecar, answer surfaces recomputed from the frozen
     ``raw_output.txt`` so the body / think-block flags stay extractor-blind;
  3. refreshes ``SHA256SUMS``.

The generator is NEVER run (generation is temp-0.7, non-deterministic, and the
matrix-v2 ``raw_output.txt`` files are frozen + SHA-tracked). ``scaffold_run.yaml``
is left untouched on purpose: its ``scaffold.config_hash`` embeds the rendered-
prompt hash, which is not recoverable offline, and its ``run_metadata.notes``
record the *original* stub-official write provenance. Re-pointing therefore
layers a post-calibration official routing (claims.yaml + run_disposition.yaml)
over the preserved original-write manifest. See DECISIONS.md 2026-06-01.

The non-official sidecars (stub, small3) and the exploratory think-block
extraction are left intact. Idempotent: claims always come from the Nemo
sidecar, never from the (possibly already-promoted) claims.yaml.

Usage:
    python scripts/calibration/promote_official_extractor.py            # re-point all cells
    python scripts/calibration/promote_official_extractor.py --dry-run  # report only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ASSET_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC_PATH = _ASSET_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

from research_scaffold_harness.contracts.hashing import (  # noqa: E402
    verify_sha256sums,
    write_sha256sums,
)
from research_scaffold_harness.contracts.yaml_io import (  # noqa: E402
    load_yaml,
    write_model_yaml,
    yaml_to_string,
)
from research_scaffold_harness.models.ca import ClaimsRegistry  # noqa: E402
from research_scaffold_harness.runner.writer_bridge import (  # noqa: E402
    build_run_disposition_fields,
)

_DEFAULT_MATRIX = _ASSET_ROOT / "build" / "phase-2-unit4-matrix-v2"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--matrix-dir",
        type=Path,
        default=_DEFAULT_MATRIX,
        help="Directory holding scaffold-run-* cells (default: matrix-v2 build dir).",
    )
    parser.add_argument(
        "--official-extractor",
        choices=("stub", "nemo", "small3"),
        default="nemo",
        help="Sidecar to promote to official (default: nemo, the calibrated choice).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the prev->new disposition per cell without writing anything.",
    )
    return parser.parse_args()


def _promote_cell(cell: Path, official_slug: str, *, dry_run: bool) -> dict:
    sidecar_path = cell / "intermediates" / f"claims_extractor_{official_slug}.yaml"
    if not sidecar_path.exists():
        raise FileNotFoundError(f"{cell.name}: missing sidecar {sidecar_path.name}")

    sidecar = load_yaml(sidecar_path)
    existing_claims = load_yaml(cell / "claims.yaml")
    existing_disp = load_yaml(cell / "run_disposition.yaml")
    raw_output = (cell / "raw_output.txt").read_text(encoding="utf-8")

    # Official claims registry from the frozen sidecar. Preserve the cell's
    # original write run_id + timestamp (the sidecar carries its own slightly
    # earlier extraction time) so claims.yaml and the disposition stay aligned,
    # mirroring the writer bridge's re-stamp at write time.
    registry = ClaimsRegistry.model_validate(sidecar["claims"]).model_copy(
        update={
            "run_id": existing_claims["run_id"],
            "generated_at_utc": existing_claims["generated_at_utc"],
        }
    )

    disposition = build_run_disposition_fields(
        raw_output=raw_output,
        run_id=existing_disp["run_id"],
        task_id=existing_disp["task_id"],
        workflow_condition=existing_disp["workflow_condition"],
        generated_at_utc=existing_disp["generated_at_utc"],
        extractor_id=sidecar["extractor_id"],
        extractor_is_stub=sidecar["extractor_is_stub"],
        extracted_claim_count=sidecar["claim_count"],
        extractor_diagnostics=list(sidecar.get("diagnostics", [])),
    )

    result = {
        "cell": cell.name.replace("scaffold-run-", ""),
        "condition": existing_disp["workflow_condition"],
        "official_extractor": sidecar["extractor_id"],
        "claim_count": sidecar["claim_count"],
        "prev_disposition": existing_disp["disposition"],
        "new_disposition": disposition["disposition"],
        "prev_is_stub": existing_disp["extractor_is_stub"],
    }
    if dry_run:
        return result

    write_model_yaml(registry, cell / "claims.yaml")
    (cell / "run_disposition.yaml").write_text(
        yaml_to_string(disposition), encoding="utf-8"
    )
    write_sha256sums(cell)

    sha_errors = verify_sha256sums(cell)
    if sha_errors:
        raise RuntimeError(f"{cell.name}: SHA256SUMS failed to verify: {sha_errors}")
    written = load_yaml(cell / "claims.yaml")
    if len(written.get("claims") or []) != sidecar["claim_count"]:
        raise RuntimeError(
            f"{cell.name}: claims.yaml count != Nemo sidecar count "
            f"({len(written.get('claims') or [])} != {sidecar['claim_count']})"
        )
    return result


def main() -> int:
    args = _parse_args()
    cells = sorted(args.matrix_dir.glob("scaffold-run-*"))
    if not cells:
        raise SystemExit(f"No scaffold-run-* cells under {args.matrix_dir}")

    results = [_promote_cell(cell, args.official_extractor, dry_run=args.dry_run) for cell in cells]

    mode = "DRY-RUN (no writes)" if args.dry_run else "re-pointed"
    print(f"{mode}: {len(results)} cells, official={args.official_extractor}\n")
    header = (
        f"{'cell':16} {'condition':20} {'claims':6} "
        f"{'prev_disposition':24} -> new_disposition"
    )
    print(header)
    print("-" * len(header))
    transitions: dict[str, int] = {}
    new_counts: dict[str, int] = {}
    for row in results:
        arrow = "" if row["prev_disposition"] == row["new_disposition"] else "  *"
        print(
            f"{row['cell']:16} {row['condition']:20} {str(row['claim_count']):6} "
            f"{row['prev_disposition']:24} -> {row['new_disposition']}{arrow}"
        )
        key = f"{row['prev_disposition']} -> {row['new_disposition']}"
        transitions[key] = transitions.get(key, 0) + 1
        new_counts[row["new_disposition"]] = new_counts.get(row["new_disposition"], 0) + 1

    print("\nNew disposition counts (Nemo official):")
    for disp, n in sorted(new_counts.items()):
        print(f"  {disp:36} {n}")
    print("\nTransitions (stub-official -> Nemo-official):")
    for key, n in sorted(transitions.items()):
        print(f"  {key:52} {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
