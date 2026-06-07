#!/usr/bin/env python3
"""Nemo-official zero-claim adjudication for the PILOT-001 / RSH-001 FDA run.

Pilot sibling of ``build_nemo_zero_adjudication.py``. Same mechanical core —
read each Nemo-official cell, keep the ones that extract zero official claims,
and split them into two classes — but pointed at an arbitrary run directory
(default ``build/pilot-001-rsh-001``, the first real FDA-grounded evidence run)
rather than the hard-coded matrix-v2 calibration corpus, and with pilot framing.

The matrix-v2 generator stays the untouched reproducible source for the
matrix-v2 doc; this one never reads or writes matrix-v2.

Two classes (distinguished mechanically, identical rule to the matrix-v2 packet):
  * Class A (genuine no-answer): the stub footer-reader ALSO found 0 claims.
  * Class B (footer-only answer): the stub footer-reader found > 0 claims that
    Nemo's body-reader misses because the model wrote its answer only in the
    ``Final claims:`` footer (the official surface strips the footer).

Queue rule: if the zero-claim cell count exceeds the stop-threshold (4), emit the
packet and HALT confirmatory re-reporting until a human scans the cells. Below the
threshold the queue does not force a halt, but results stay Exploratory until the
downstream Evidence-Bundler + Claim-Audit-Lab human-calibrated audit either way.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ASSET_ROOT = Path(__file__).resolve().parent.parent.parent
_SRC_PATH = _ASSET_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

from research_scaffold_harness.contracts.yaml_io import load_yaml  # noqa: E402
from research_scaffold_harness.extractor.surfaces import (  # noqa: E402
    prepare_extraction_surfaces,
)

_DEFAULT_MATRIX = _ASSET_ROOT / "build" / "pilot-001-rsh-001"
_DEFAULT_OUT = _ASSET_ROOT / "docs" / "pilot-001-rsh-001-nemo-zero-adjudication.md"
_QUEUE_STOP_THRESHOLD = 4
_RUN_DATE = "2026-06-02"
_RUN_PROVENANCE = (
    "Run provenance: 20 cells (5 models x 4 conditions), one run per cell, temp 0.7, "
    "max_tokens 2048, Nemo official, --extractor all --skip-verify-intake. Completed in two "
    "segments after an overnight machine-sleep interruption: 16 cells on 2026-06-01 21:57-23:16, "
    "then Phi-4-reasoning-plus x4 resumed 2026-06-02 06:34-07:00. Each cell mints a fresh run_id; "
    "no cell was run twice (verified: every model x condition appears exactly once)."
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix-dir", type=Path, default=_DEFAULT_MATRIX,
                        help="Directory of scaffold-run-* cells to adjudicate.")
    parser.add_argument("--out", type=Path, default=_DEFAULT_OUT,
                        help="Markdown packet output path.")
    parser.add_argument("--threshold", type=int, default=_QUEUE_STOP_THRESHOLD,
                        help="Queue stop-threshold (halt confirmatory if exceeded).")
    return parser.parse_args()


def _model_short(manifest: dict) -> str:
    return manifest.get("model", {}).get("model_id", "?").split("/")[-1]


def _footer_segment(raw_output: str) -> str:
    """Return the text from the last 'Final claims:'-style marker onward."""
    lowered = raw_output.lower()
    idx = lowered.rfind("final claims")
    if idx == -1:
        return ""
    return raw_output[idx:].strip()


def _collect(matrix_dir: Path) -> tuple[list[dict], int]:
    """Return (zero-claim rows, total cells that produced a disposition)."""
    rows: list[dict] = []
    total = 0
    for cell in sorted(matrix_dir.glob("scaffold-run-*")):
        disp_path = cell / "run_disposition.yaml"
        if not disp_path.exists():
            # Cell never wrote a disposition (e.g. it failed before write).
            # It is not a zero-claim cell; surface it via the run report instead.
            continue
        disp = load_yaml(disp_path)
        total += 1
        if disp.get("extracted_claim_count", 0) != 0:
            continue
        manifest = load_yaml(cell / "scaffold_run.yaml")
        raw = (cell / "raw_output.txt").read_text(encoding="utf-8")
        stub_path = cell / "intermediates" / "claims_extractor_stub.yaml"
        stub_side = load_yaml(stub_path) if stub_path.exists() else {}
        surfaces = prepare_extraction_surfaces(raw)
        stub_claims = [
            c["claim_text"] for c in stub_side.get("claims", {}).get("claims", [])
        ]
        rows.append({
            "run_id": cell.name.replace("scaffold-run-", ""),
            "model": _model_short(manifest),
            "condition": disp["workflow_condition"],
            "disposition": disp["disposition"],
            "surface_diagnostics": disp.get("surface_diagnostics", []),
            "nemo_diagnostics": disp.get("extractor_diagnostics", []),
            "official_body": surfaces.official_answer_text,
            "stub_count": len(stub_claims),
            "stub_claims": stub_claims,
            "footer": _footer_segment(raw),
            "raw_len": len(raw),
            "raw_tail": raw[-700:].strip(),
        })
    return rows, total


def _classify(row: dict) -> str:
    return "B" if row["stub_count"] > 0 else "A"


def _render(rows: list[dict], total: int, threshold: int) -> str:
    class_a = [r for r in rows if _classify(r) == "A"]
    class_b = [r for r in rows if _classify(r) == "B"]
    tripped = len(rows) > threshold
    out: list[str] = []
    w = out.append

    w("# PILOT-001 / RSH-001 — Nemo-Official Zero-Claim Adjudication Packet")
    w("")
    w(f"Date: {_RUN_DATE}")
    if tripped:
        w("Status: **OPEN — awaiting human sentence scan.** Confirmatory reporting is HALTED "
          "(queue stop-threshold exceeded).")
    else:
        w("Status: **Queue stop-threshold NOT exceeded.** No forced halt from the queue rule. "
          "Per-cell zero-claim integrity scans still apply, and results remain **Exploratory** "
          "(not Confirmatory) until the downstream human-calibrated audit.")
    w("Decision of record: Mistral Nemo = official extractor (F1 0.8916, strong tier; "
      "DECISIONS § 2026-06-01).")
    w("Source: first real FDA-grounded evidence run — `build/pilot-001-rsh-001` over the "
      "`pilots/pilot-001-rsh-001` packet (FDA *Quality Systems Approach to CGMP* bounded excerpt "
      "+ fictional challenge memo). Distinct from the `build/phase-2-unit4-matrix-v2` calibration "
      "corpus. Regenerate this doc with `scripts/calibration/build_pilot_zero_adjudication.py`.")
    w("")
    w(_RUN_PROVENANCE)
    w("")
    w("---")
    w("")
    w("## Why this packet exists")
    w("")
    pct = f"{len(rows)} of {total}"
    if tripped:
        w(f"Under Nemo-official, **{pct}** pilot cells extract zero official claims. The "
          "run-disposition gate routes empty-body cells to `missing_final_answer` (excluded from "
          "the support-rate denominator, no human-review flag). But the zero-claim integrity rule "
          "is explicit: *never treat a zero-claim cell as zero-unsupported without a human sentence "
          f"scan.* {len(rows)} nemo-zero cells exceed the queue stop-threshold of {threshold}, so "
          "this packet is produced and confirmatory re-reporting halts until a human scans these "
          "cells.")
    else:
        w(f"Under Nemo-official, **{pct}** pilot cells extract zero official claims — at or below "
          f"the queue stop-threshold of {threshold}, so the queue rule does not force a halt. This "
          "packet is still emitted as the audit record for those cells: the zero-claim integrity "
          "rule (*never treat a zero-claim cell as zero-unsupported without a human sentence scan*) "
          "applies per-cell regardless of the count.")
    w("")
    w("**Two classes (mechanically separated):**")
    w("")
    w(f"- **Class A — genuine no-answer ({len(class_a)} cells).** The stub footer-reader ALSO found "
      "0 claims. The model exhausted its budget mid-`<think>` and never emitted a visible answer. "
      "`missing_final_answer` is appropriate; the human scan should *confirm* no answer is present.")
    w(f"- **Class B — footer-only answer ({len(class_b)} cells).** The stub footer-reader found "
      "claims that Nemo's body-reader misses, because the model wrote its answer ONLY in the "
      "`Final claims:` footer with no prose body — and the official surface (visible answer body) "
      "strips the footer. These cells carry a human-readable answer. Routing them to "
      "`missing_final_answer` silently drops real claims; the human must decide whether to (a) "
      "re-include via the footer, or (b) accept the body-only protocol and exclude.")
    w("")
    w("## Queue determination")
    w("")
    w(f"- Nemo-zero cells: **{len(rows)}** of **{total}** cells that produced a disposition "
      f"(Class A: {len(class_a)}, Class B: {len(class_b)}).")
    w(f"- Queue stop-threshold: **{threshold}**.")
    if tripped:
        w(f"- {len(rows)} > {threshold} → **STOP: produce this packet, halt before confirmatory "
          "re-reporting.**")
    else:
        w(f"- {len(rows)} ≤ {threshold} → queue rule does not force a halt. Cells below still "
          "require the standard zero-claim integrity scan before any support-rate denominator "
          "decision.")
    w("- Results stay **Exploratory, not Confirmatory**, until the Evidence-Bundler + "
      "Claim-Audit-Lab human-calibrated audit. No support-rate number is promoted from this packet.")
    w("")
    w("## Cell index")
    w("")
    if not rows:
        w("_No zero-claim cells. Every Nemo-official cell extracted ≥ 1 claim._")
        w("")
        return "\n".join(out) + "\n"
    w("| run_id | model | condition | class | stub (footer) | nemo (body) | disposition |")
    w("|---|---|---|:--:|--:|--:|---|")
    for r in sorted(rows, key=lambda x: (_classify(x), x["model"], x["condition"])):
        w(f"| `{r['run_id']}` | {r['model']} | {r['condition']} | {_classify(r)} "
          f"| {r['stub_count']} | 0 | {r['disposition']} |")
    w("")

    for label, group in (("A — genuine no-answer", class_a), ("B — footer-only answer", class_b)):
        if not group:
            continue
        w("---")
        w("")
        w(f"## Class {label}")
        w("")
        for r in sorted(group, key=lambda x: (x["model"], x["condition"])):
            w(f"### `{r['run_id']}` — {r['model']} / {r['condition']}")
            w("")
            body = r["official_body"]
            body_desc = "**empty**" if not body else f"{len(body)} chars"
            w(f"- disposition: `{r['disposition']}`  ·  raw_output: {r['raw_len']} chars")
            w(f"- nemo diagnostics: `{r['nemo_diagnostics']}`")
            w(f"- surface diagnostics: `{r['surface_diagnostics']}`")
            w(f"- official answer body (what Nemo reads): {body_desc}")
            w("")
            if _classify(r) == "B":
                w(f"**Footer claims the stub recovered ({r['stub_count']}) — candidate answer "
                  "for human scan:**")
                w("")
                for claim in r["stub_claims"]:
                    w(f"- {claim}")
                w("")
            else:
                w("**Raw output tail (last 700 chars) — confirm no answer was produced:**")
                w("")
                w("```")
                w(r["raw_tail"])
                w("```")
                w("")
    return "\n".join(out) + "\n"


def main() -> int:
    args = _parse_args()
    rows, total = _collect(args.matrix_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(_render(rows, total, args.threshold), encoding="utf-8")
    class_a = sum(1 for r in rows if _classify(r) == "A")
    class_b = sum(1 for r in rows if _classify(r) == "B")
    tripped = len(rows) > args.threshold
    try:
        rel = args.out.relative_to(_ASSET_ROOT)
    except ValueError:
        rel = args.out
    print(f"Wrote {rel}")
    print(f"  cells with a disposition: {total}")
    print(f"  nemo-zero cells: {len(rows)} (Class A genuine no-answer: {class_a}, "
          f"Class B footer-only: {class_b})")
    action = "STOP (produce packet, halt confirmatory)" if tripped else "proceed (no forced halt)"
    print(f"  queue stop-threshold: {args.threshold} -> {action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
