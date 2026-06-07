#!/usr/bin/env python3
"""Phase 2 Unit 4 smoke runner — one model, one condition, RSH-001, verify-intake.

Exit codes:
  0 — artifact produced and ``verify-intake`` returned 0
  1 — any gate failed (load, generate, write, verify-intake, blank revision)
  2 — invalid invocation

Prints a JSON result line on stdout so the matrix script can parse a cell
outcome without re-parsing the markdown report.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path

# Ensure ``src/`` is importable when running from the asset root.
_ASSET_ROOT = Path(__file__).resolve().parent.parent
_SRC_PATH = _ASSET_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

from research_scaffold_harness.extractor import (  # noqa: E402
    MlxNemoExtractor,
    MlxSmallExtractor,
    StubUniformExtractor,
    extract_claims_from_runner_result,
    extract_think_claims_from_runner_result,
)
from research_scaffold_harness.runner import (  # noqa: E402
    MLX_MODEL_ALLOWLIST,
    MLXAdapterError,
    MLXModelAdapter,
    RunnerSettings,
    load_source_packet,
    run_source_packet,
)
from research_scaffold_harness.runner.writer_bridge import (  # noqa: E402
    find_evidence_bundler_binary,
    mint_run_id,
    resolve_official_extractor,
    select_official_extraction,
    write_scaffold_run_from_extraction,
)

_DEFAULT_FIXTURE = (
    _ASSET_ROOT / "tests" / "fixtures" / "source-packet-minimal"
)
_DEFAULT_REPORT = _ASSET_ROOT / "build" / "phase-2-unit4-smoke-report.md"
_CONDITIONS = ("baseline", "format_only", "provenance_scaffold", "full_scaffold")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model",
        required=True,
        choices=MLX_MODEL_ALLOWLIST,
        help="HuggingFace MLX model id from the five-model ADR allowlist.",
    )
    parser.add_argument(
        "--condition",
        required=True,
        choices=_CONDITIONS,
        help="Workflow condition to run.",
    )
    parser.add_argument(
        "--task-dir",
        type=Path,
        default=_DEFAULT_FIXTURE,
        help="Source packet directory (defaults to the RSH-001 fixture).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Parent directory for the produced scaffold-run artifact.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=_DEFAULT_REPORT,
        help="Markdown report file. Appended; not overwritten.",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Generation temperature (locked to 0.7 per model-selection ADR).",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Max generated tokens.",
    )
    parser.add_argument(
        "--skip-verify-intake",
        action="store_true",
        help="Skip the evidence-bundler verify-intake subprocess gate.",
    )
    parser.add_argument(
        "--extractor",
        choices=("stub", "all"),
        default="stub",
        help="Extractor set. 'all' runs the stub, Nemo, and Small 3 as sidecars.",
    )
    parser.add_argument(
        "--official-extractor",
        choices=("stub", "nemo", "small3"),
        default=None,
        help=(
            "Which extraction is written to claims.yaml. Defaults to Nemo when "
            "--extractor=all (calibration of record: Nemo F1 0.8916), else the "
            "single extractor that ran."
        ),
    )
    return parser.parse_args()


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _emit_json_result(result: dict, fh) -> None:
    fh.write("CELL_RESULT_JSON " + json.dumps(result, sort_keys=True) + "\n")


def _append_report(
    report_path: Path,
    *,
    started_at: str,
    ended_at: str,
    args: argparse.Namespace,
    result: dict,
    raw_excerpt: str,
    notes_excerpt: str,
    verify_stdout: str,
    verify_stderr: str,
    error_block: str,
) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    initial = not report_path.exists()
    with report_path.open("a", encoding="utf-8") as fh:
        if initial:
            fh.write("# Phase 2 Unit 4 — Smoke Report\n\n")
            fh.write(
                "Append-only log. One entry per smoke invocation. Failures are kept "
                "in place so the audit trail preserves prior runs.\n\n"
            )
        fh.write("---\n\n")
        fh.write(f"## {started_at} — {args.model} / {args.condition}\n\n")
        fh.write(f"- started_at: `{started_at}`\n")
        fh.write(f"- ended_at: `{ended_at}`\n")
        fh.write(f"- model: `{args.model}`\n")
        fh.write(f"- condition: `{args.condition}`\n")
        fh.write(f"- task_dir: `{args.task_dir}`\n")
        fh.write(f"- temperature: `{args.temperature}`\n")
        fh.write(f"- max_tokens: `{args.max_tokens}`\n")
        for key in (
            "run_id",
            "scaffold_run_dir",
            "model_revision",
            "mlx_lm_version",
            "quantization",
            "chat_template_applied",
            "extractor_id",
            "is_stub",
            "raw_output_tokens",
            "claim_count",
            "verify_intake_returncode",
            "verify_intake_skipped",
            "elapsed_seconds",
            "status",
        ):
            if key in result:
                fh.write(f"- {key}: `{result[key]}`\n")
        if raw_excerpt:
            fh.write("\nraw_output_excerpt:\n\n```\n")
            fh.write(raw_excerpt)
            fh.write("\n```\n")
        if notes_excerpt:
            fh.write("\nrun_metadata_notes:\n\n```\n")
            fh.write(notes_excerpt)
            fh.write("\n```\n")
        if verify_stdout.strip():
            fh.write("\nverify_intake_stdout:\n\n```\n")
            fh.write(verify_stdout.strip()[:2000])
            fh.write("\n```\n")
        if verify_stderr.strip():
            fh.write("\nverify_intake_stderr:\n\n```\n")
            fh.write(verify_stderr.strip()[:2000])
            fh.write("\n```\n")
        if error_block:
            fh.write("\nerror:\n\n```\n")
            fh.write(error_block.strip()[:4000])
            fh.write("\n```\n")
        fh.write("\n")


def main() -> int:
    args = _parse_args()
    started_at = _now_iso()
    started_perf = time.perf_counter()

    result: dict = {
        "started_at": started_at,
        "model": args.model,
        "condition": args.condition,
        "status": "in_progress",
    }
    raw_excerpt = ""
    notes_excerpt = ""
    verify_stdout = ""
    verify_stderr = ""
    error_block = ""

    try:
        packet = load_source_packet(args.task_dir)
        adapter = MLXModelAdapter(model_id=args.model)
        settings = RunnerSettings(
            temperature=args.temperature, max_tokens=args.max_tokens
        )
        runner_result = run_source_packet(packet, args.condition, adapter, settings)
        run_id = mint_run_id()
        # Generator output is captured in runner_result; free the generator before
        # any extractor model loads so model residency stays sequential rather than
        # concurrent (ADR § 2026-05-25; 24 GB unified-memory budget).
        adapter.close()

        extractions = [
            extract_claims_from_runner_result(
                result=runner_result, run_id=run_id, adapter=StubUniformExtractor(),
            )
        ]
        exploratory_think = None
        if args.extractor == "all":
            # Nemo: load once, run its official and exploratory-think extractions,
            # then free it before Small 3.1 loads.
            nemo = MlxNemoExtractor()
            extractions.append(
                extract_claims_from_runner_result(
                    result=runner_result, run_id=run_id, adapter=nemo,
                )
            )
            exploratory_think = extract_think_claims_from_runner_result(
                result=runner_result, run_id=run_id, adapter=nemo,
            )
            nemo.close()
            # Small 3.1: load, extract, then free.
            small3 = MlxSmallExtractor()
            extractions.append(
                extract_claims_from_runner_result(
                    result=runner_result, run_id=run_id, adapter=small3,
                )
            )
            small3.close()
        official_slug = resolve_official_extractor(args.extractor, args.official_extractor)
        extraction = select_official_extraction(extractions, official_slug)
        args.output_dir.mkdir(parents=True, exist_ok=True)
        bridge_result = write_scaffold_run_from_extraction(
            runner_result=runner_result,
            extraction=extraction,
            source_packet=packet,
            output_dir=args.output_dir,
            extractor_sidecars=extractions if args.extractor == "all" else [],
            exploratory_think_extraction=exploratory_think,
        )

        response = runner_result.response
        result.update(
            {
                "run_id": bridge_result.run_id,
                "scaffold_run_dir": str(bridge_result.scaffold_run_dir),
                "model_revision": response.model_revision,
                "mlx_lm_version": response.model_version,
                "quantization": response.quantization,
                "chat_template_applied": response.chat_template_applied,
                "extractor_id": extraction.extractor_id,
                "extractor_set": args.extractor,
                "official_extractor": official_slug,
                "extractor_claim_counts": {
                    item.extractor_id: len(item.claims.claims)
                    for item in extractions
                },
                "is_stub": extraction.is_stub,
                "raw_output_tokens": response.output_tokens,
                "claim_count": len(extraction.claims.claims),
                "finish_reason": response.finish_reason,
            }
        )

        raw_excerpt = response.text[:2000]
        notes_excerpt = _read_notes(bridge_result.scaffold_run_dir)

        if not response.model_revision:
            raise RuntimeError(
                "model_revision is blank — HuggingFace commit SHA did not resolve. "
                "Treating as gate failure per Phase 2 Unit 4 plan."
            )

        if args.skip_verify_intake:
            result["verify_intake_skipped"] = True
        else:
            verify_returncode, verify_stdout, verify_stderr = _run_verify_intake(
                bridge_result.scaffold_run_dir
            )
            result["verify_intake_returncode"] = verify_returncode
            result["verify_intake_skipped"] = False
            if verify_returncode != 0:
                raise RuntimeError(
                    f"verify-intake returned {verify_returncode}"
                )

        result["status"] = "pass"
        exit_code = 0
    except (MLXAdapterError, FileNotFoundError, RuntimeError, Exception) as exc:  # noqa: BLE001
        error_block = traceback.format_exc()
        result["status"] = "fail"
        result["error"] = str(exc)
        exit_code = 1
    finally:
        ended_perf = time.perf_counter()
        ended_at = _now_iso()
        result["ended_at"] = ended_at
        result["elapsed_seconds"] = round(ended_perf - started_perf, 2)

        _append_report(
            args.report,
            started_at=started_at,
            ended_at=ended_at,
            args=args,
            result=result,
            raw_excerpt=raw_excerpt,
            notes_excerpt=notes_excerpt,
            verify_stdout=verify_stdout,
            verify_stderr=verify_stderr,
            error_block=error_block,
        )
        _emit_json_result(result, sys.stdout)

    return exit_code


def _read_notes(scaffold_run_dir: Path) -> str:
    manifest_path = scaffold_run_dir / "scaffold_run.yaml"
    if not manifest_path.exists():
        return ""
    try:
        text = manifest_path.read_text(encoding="utf-8")
    except Exception:
        return ""
    notes_lines: list[str] = []
    in_notes = False
    indent = ""
    for line in text.splitlines():
        if not in_notes:
            if line.startswith("run_metadata:"):
                in_notes = True
                indent = "  "
            continue
        if line and not line.startswith(indent):
            break
        notes_lines.append(line)
    return "\n".join(notes_lines)


def _run_verify_intake(scaffold_run_dir: Path) -> tuple[int, str, str]:
    binary = find_evidence_bundler_binary()
    if binary is None:
        return (
            127,
            "",
            "evidence-bundler CLI not found next to sys.executable or on PATH. "
            "Install in the same venv (pip install -e ../evidence-bundler) and re-run.",
        )
    completed = subprocess.run(
        [str(binary), "verify-intake", str(scaffold_run_dir)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    return completed.returncode, completed.stdout or "", completed.stderr or ""


if __name__ == "__main__":
    raise SystemExit(main())
