#!/usr/bin/env python3
"""Exploratory probe: does a "close </think> and answer" nudge rescue the reasoning-model zero cells?

Root cause (findings-log § 2026-06-03): the reasoning models do the whole task inside
`<think>`, never emit `</think>`, and EOS without a post-think answer — so the official
surface is empty. This probe appends a close-think-and-answer instruction (NUDGE) AFTER
the frozen condition prompt (via run_source_packet prompt_suffix; the frozen templates are
NOT modified) and re-runs the two reasoning models x 4 conditions at the SAME max_tokens=2048
as the pilot, so the ONLY changed variable is the nudge.

Measures, per cell: `</think>` closure count, finish_reason, output_tokens, Nemo-official
claim count, stub (footer) claim count — vs the original pilot cells.

Restart-safe: writes one JSON line per cell to results.jsonl and skips completed
(model, condition) on restart, so a machine sleep doesn't lose progress. Exploratory only;
nothing here promotes a support-rate, and it does not touch build/pilot-001-rsh-001.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ASSET = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ASSET / "src"))

from research_scaffold_harness.contracts.yaml_io import load_yaml  # noqa: E402
from research_scaffold_harness.extractor import (  # noqa: E402
    MlxNemoExtractor,
    StubUniformExtractor,
    extract_claims_from_runner_result,
)
from research_scaffold_harness.runner import (  # noqa: E402
    MLXModelAdapter,
    RunnerSettings,
    load_source_packet,
    run_source_packet,
)
from research_scaffold_harness.runner.writer_bridge import mint_run_id  # noqa: E402

NUDGE_ID = "close-think-and-answer-v1"
NUDGE = (
    "Output protocol (critical): Keep all reasoning inside a single "
    "`<think> ... </think>` block and CLOSE it with `</think>` before you finish. "
    "Only the text AFTER `</think>` is read and scored — your reasoning block is "
    "discarded. After `</think>`, write the deliverable as plain text: the claim "
    "table (if requested), the final answer, and the required `Final claims:` footer. "
    "Do NOT end your response while still inside `<think>`; if your reasoning is "
    "running long, stop, emit `</think>`, and write the answer."
)

# NUDGE_V2 (next test — Cameron 2026-06-03): state an *explicit* reasoning budget
# (a concrete number) at the START of the prompt, so the model plans its exit instead
# of being told "if running long". To place it at the start, add a `prompt_prefix`
# mirror of `prompt_suffix` in runner/core.py and pass it through run_source_packet,
# then set NUDGE = NUDGE_V2 (as prefix) below. Targets the stubborn Class A cells
# (Phi-4-reasoning-plus baseline, provenance) that still won't close </think> under v1.
NUDGE_V2_ID = "explicit-budget-close-think-v2"
NUDGE_V2 = (
    "Reasoning budget (read first): you have a hard budget of about 500 words of "
    "reasoning. Do all reasoning inside one `<think> ... </think>` block, keep it under "
    "~500 words, then CLOSE `</think>` and use the rest of the response for the "
    "deliverable: the claim table (if requested), the final answer, and the required "
    "`Final claims:` footer. Only text after `</think>` is read and scored. Plan "
    "backwards from this budget so you exit `<think>` with room to write the answer; "
    "never end while still inside `<think>`."
)

TASK_DIR = _ASSET / "pilots" / "pilot-001-rsh-001"
OUT = _ASSET / "build" / "pilot-001-nudge-probe"
ORIG = _ASSET / "build" / "pilot-001-rsh-001"
MODELS = [
    "lmstudio-community/Phi-4-mini-reasoning-MLX-4bit",
    "mlx-community/Phi-4-reasoning-plus-4bit",
]
CONDITIONS = ["baseline", "format_only", "provenance_scaffold", "full_scaffold"]


def _completed(results_path: Path) -> set[tuple[str, str]]:
    done: set[tuple[str, str]] = set()
    if results_path.exists():
        for line in results_path.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                done.add((r["model_id"], r["condition"]))
            except Exception:  # noqa: BLE001
                continue
    return done


def _original_index() -> dict[tuple[str, str], tuple[int, int]]:
    """(model_short, condition) -> (orig nemo claim count, orig </think> close count)."""
    idx: dict[tuple[str, str], tuple[int, int]] = {}
    for cell in ORIG.glob("scaffold-run-*"):
        disp = load_yaml(cell / "run_disposition.yaml")
        manifest_txt = (cell / "scaffold_run.yaml").read_text(encoding="utf-8")
        m = re.search(r"model_id:\s*(\S+)", manifest_txt)
        if not m:
            continue
        model_short = m.group(1).split("/")[-1]
        raw = (cell / "raw_output.txt").read_text(encoding="utf-8")
        idx[(model_short, disp["workflow_condition"])] = (
            disp.get("extracted_claim_count", 0),
            raw.count("</think>"),
        )
    return idx


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results_path = OUT / "results.jsonl"
    done = _completed(results_path)
    if done:
        print(f"[probe] resume: {len(done)} cell(s) already done, skipping them", flush=True)
    packet = load_source_packet(TASK_DIR)
    settings = RunnerSettings(temperature=0.7, max_tokens=2048)

    for model in MODELS:
        pending = [c for c in CONDITIONS if (model, c) not in done]
        if not pending:
            print(f"[probe] {model}: all done", flush=True)
            continue
        print(f"[probe] generator load: {model} -> {pending}", flush=True)
        adapter = MLXModelAdapter(model_id=model)
        raws = {}
        for cond in pending:
            res = run_source_packet(packet, cond, adapter, settings, prompt_suffix=NUDGE)
            raws[cond] = res
            r = res.response
            print(
                f"[probe]   gen {cond}: finish={r.finish_reason} tok={r.output_tokens} "
                f"</think>={r.text.count('</think>')}",
                flush=True,
            )
        adapter.close()

        nemo = MlxNemoExtractor()
        for cond in pending:
            res = raws[cond]
            raw = res.response.text
            nemo_ext = extract_claims_from_runner_result(
                result=res, run_id=mint_run_id(), adapter=nemo
            )
            stub_ext = extract_claims_from_runner_result(
                result=res, run_id=mint_run_id(), adapter=StubUniformExtractor()
            )
            row = {
                "model": model.split("/")[-1],
                "model_id": model,
                "condition": cond,
                "nudge_id": NUDGE_ID,
                "think_open": raw.count("<think>"),
                "think_close": raw.count("</think>"),
                "finish_reason": res.response.finish_reason,
                "output_tokens": res.response.output_tokens,
                "nemo_claims": len(nemo_ext.claims.claims),
                "stub_claims": len(stub_ext.claims.claims),
                "raw_chars": len(raw),
            }
            with results_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(row) + "\n")
            print(
                f"[probe]   {cond}: </think>x{row['think_close']} "
                f"nemo={row['nemo_claims']} stub={row['stub_claims']}",
                flush=True,
            )
        nemo.close()

    _write_report(results_path)
    return 0


def _write_report(results_path: Path) -> None:
    rows = [
        json.loads(line)
        for line in results_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    orig = _original_index()
    order = {m.split("/")[-1]: i for i, m in enumerate(MODELS)}
    rows.sort(key=lambda r: (order.get(r["model"], 9), CONDITIONS.index(r["condition"])))
    out = ["# PILOT-001 — `</think>` nudge probe (Exploratory)", ""]
    out.append(f"Nudge `{NUDGE_ID}` appended to the frozen condition prompt; max_tokens=2048 (held).")
    out.append("Compares nudged reasoning-model cells vs the original pilot (no nudge).")
    out.append("")
    out.append("| Model | Condition | orig claims / </think> | nudged claims / </think> | result |")
    out.append("|---|---|---|---|---|")
    flips = 0
    for r in rows:
        ocl, oclose = orig.get((r["model"], r["condition"]), ("?", "?"))
        flip = isinstance(ocl, int) and ocl == 0 and r["nemo_claims"] > 0
        if flip:
            flips += 1
        note = "**RESCUED**" if flip else ("still zero" if r["nemo_claims"] == 0 else "had answer")
        out.append(
            f"| {r['model']} | {r['condition']} | {ocl} / {oclose} | "
            f"{r['nemo_claims']} / {r['think_close']} | {note} |"
        )
    zero_now = sum(1 for r in rows if r["nemo_claims"] == 0)
    out.append("")
    out.append(f"**Nudged: {zero_now}/{len(rows)} still zero · {flips} rescued from the original zeros.**")
    out.append("")
    (OUT / "report.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"\n[probe] wrote {OUT / 'report.md'}")
    print(f"[probe] nudged: {zero_now}/{len(rows)} still zero; {flips} rescued")


if __name__ == "__main__":
    raise SystemExit(main())
