#!/usr/bin/env python3
"""Build the Nemo-official zero-claim adjudication packet (Phase 5 Step 12, Stage 4).

Reads the re-pointed matrix-v2 cells, finds every cell that extracts zero
official claims under Nemo, and emits a human-scannable markdown packet to
``docs/phase-5-step12-nemo-zero-adjudication.md``. The generator is the
audit-trail-reproducible source for that doc: re-run it after any re-point.

Two classes are distinguished mechanically:
  * Class A (genuine no-answer): the stub footer-reader ALSO found 0 claims.
  * Class B (footer-only answer): the stub footer-reader found > 0 claims that
    Nemo's body-reader misses because the model wrote its answer only in the
    ``Final claims:`` footer (the official surface strips the footer).
"""

from __future__ import annotations

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

_MATRIX = _ASSET_ROOT / "build" / "phase-2-unit4-matrix-v2"
_OUT = _ASSET_ROOT / "docs" / "phase-5-step12-nemo-zero-adjudication.md"
_QUEUE_STOP_THRESHOLD = 4


def _model_short(manifest: dict) -> str:
    return manifest.get("model", {}).get("model_id", "?").split("/")[-1]


def _footer_segment(raw_output: str) -> str:
    """Return the text from the last 'Final claims:'-style marker onward."""
    lowered = raw_output.lower()
    idx = lowered.rfind("final claims")
    if idx == -1:
        return ""
    return raw_output[idx:].strip()


def _collect() -> list[dict]:
    rows: list[dict] = []
    for cell in sorted(_MATRIX.glob("scaffold-run-*")):
        disp = load_yaml(cell / "run_disposition.yaml")
        if disp.get("extracted_claim_count", 0) != 0:
            continue
        manifest = load_yaml(cell / "scaffold_run.yaml")
        raw = (cell / "raw_output.txt").read_text(encoding="utf-8")
        stub_side = load_yaml(cell / "intermediates" / "claims_extractor_stub.yaml")
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
    return rows


def _classify(row: dict) -> str:
    return "B" if row["stub_count"] > 0 else "A"


def _render(rows: list[dict]) -> str:
    class_a = [r for r in rows if _classify(r) == "A"]
    class_b = [r for r in rows if _classify(r) == "B"]
    out: list[str] = []
    w = out.append

    w("# Phase 5 Step 12 — Nemo-Official Zero-Claim Adjudication Packet")
    w("")
    w("Date: 2026-06-01")
    w("Status: **OPEN — awaiting human sentence scan.** Confirmatory re-reporting is HALTED.")
    w("Decision of record: Mistral Nemo = official extractor (F1 0.8916, strong tier; "
      "DECISIONS § 2026-06-01, findings-log § 2026-05-31 round 2).")
    w("Source: `build/phase-2-unit4-matrix-v2` re-pointed Nemo-official via "
      "`scripts/calibration/promote_official_extractor.py`; regenerate this doc with "
      "`scripts/calibration/build_nemo_zero_adjudication.py`.")
    w("")
    w("---")
    w("")
    w("## Why this packet exists")
    w("")
    w(f"Under Nemo-official, **{len(rows)} of 20** matrix-v2 cells extract zero official "
      "claims. The run-disposition gate routes all of them to `missing_final_answer` "
      "(official answer body empty → excluded from the support-rate denominator, no "
      "human-review flag). But the zero-claim integrity rule is explicit: *never treat a "
      "zero-claim cell as zero-unsupported without a human sentence scan.* "
      f"{len(rows)} nemo-zero cells exceed the queue stop-threshold of "
      f"{_QUEUE_STOP_THRESHOLD}, so per the queue rule this packet is produced and "
      "confirmatory re-reporting halts until a human scans these cells.")
    w("")
    w("**Two classes (mechanically separated):**")
    w("")
    w(f"- **Class A — genuine no-answer ({len(class_a)} cells).** The stub footer-reader "
      "ALSO found 0 claims. The model exhausted its budget mid-`<think>` and never "
      "emitted a visible answer. `missing_final_answer` is appropriate; the human scan "
      "should *confirm* no answer is present.")
    w(f"- **Class B — footer-only answer ({len(class_b)} cells).** The stub footer-reader "
      "found claims that Nemo's body-reader misses, because the model wrote its answer "
      "ONLY in the `Final claims:` footer with no prose body — and the official surface "
      "(DECISIONS § 2026-05-25, *visible answer body is the official surface*) strips the "
      "footer. These cells carry a human-readable answer. Routing them to "
      "`missing_final_answer` silently drops real claims; the human must decide whether to "
      "(a) re-include via the footer, or (b) accept the body-only protocol and exclude.")
    w("")
    w("## Queue determination")
    w("")
    w("- Mechanical `requires_human_zero_claim_scan` count: **0** (every nemo-zero cell "
      "also has an empty official body, so the gate routes to `missing_final_answer`).")
    w(f"- Nemo-zero cells in total (spirit of the rule): **{len(rows)}** "
      f"(> {_QUEUE_STOP_THRESHOLD} → STOP).")
    w("- Already human-scanned in the calibration gold (`gold_2026-05-31.yaml`): the "
      "zero-claim non-answer cell `rsh-318e7831856f` (Phi-4-RP / format_only, Class A).")
    w("- **Action: produce this packet, halt before confirmatory re-reporting.** The "
      "Stage-3 re-interpretation is marked Methodological + Exploratory, not Confirmatory.")
    w("")
    w("## Cell index")
    w("")
    w("| run_id | model | condition | class | stub (footer) | nemo (body) | disposition |")
    w("|---|---|---|:--:|--:|--:|---|")
    for r in sorted(rows, key=lambda x: (_classify(x), x["model"], x["condition"])):
        w(f"| `{r['run_id']}` | {r['model']} | {r['condition']} | {_classify(r)} "
          f"| {r['stub_count']} | 0 | {r['disposition']} |")
    w("")

    for label, group in (("A — genuine no-answer", class_a), ("B — footer-only answer", class_b)):
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
                w(f"**Footer claims the stub recovered ({r['stub_count']}) — candidate "
                  "answer for human scan:**")
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
    rows = _collect()
    _OUT.write_text(_render(rows), encoding="utf-8")
    class_a = sum(1 for r in rows if _classify(r) == "A")
    class_b = sum(1 for r in rows if _classify(r) == "B")
    print(f"Wrote {_OUT.relative_to(_ASSET_ROOT)}")
    print(f"  nemo-zero cells: {len(rows)} (Class A genuine no-answer: {class_a}, "
          f"Class B footer-only: {class_b})")
    tripped = len(rows) > _QUEUE_STOP_THRESHOLD
    action = "STOP (produce packet, halt confirmatory)" if tripped else "proceed"
    print(f"  queue stop-threshold: {_QUEUE_STOP_THRESHOLD} -> {action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
