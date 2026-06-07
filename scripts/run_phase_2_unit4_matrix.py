#!/usr/bin/env python3
"""Phase 2 Unit 4 closeout matrix — 5 models × 4 conditions × RSH-001.

Spawns the smoke script as a subprocess for each cell so each model loads in
a fresh process and releases memory before the next cell. Captures the
``CELL_RESULT_JSON`` line emitted by smoke and appends one row per cell to
``build/phase-2-unit4-matrix-report.md``.

Exit codes:
  0 — every cell's smoke + verify-intake returned 0
  1 — at least one cell failed
  2 — invalid invocation
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

_ASSET_ROOT = Path(__file__).resolve().parent.parent
_SRC_PATH = _ASSET_ROOT / "src"
if str(_SRC_PATH) not in sys.path:
    sys.path.insert(0, str(_SRC_PATH))

from research_scaffold_harness.contracts.yaml_io import load_yaml  # noqa: E402
from research_scaffold_harness.runner import MLX_MODEL_ALLOWLIST  # noqa: E402

_SMOKE_SCRIPT = Path(__file__).resolve().parent / "run_phase_2_unit4_smoke.py"
_DEFAULT_FIXTURE = (
    _ASSET_ROOT / "tests" / "fixtures" / "source-packet-minimal"
)
_DEFAULT_REPORT = _ASSET_ROOT / "build" / "phase-2-unit4-matrix-report.md"
_DEFAULT_SMOKE_REPORT = _ASSET_ROOT / "build" / "phase-2-unit4-matrix-smoke-report.md"
_CONDITIONS: tuple[str, ...] = (
    "baseline",
    "format_only",
    "provenance_scaffold",
    "full_scaffold",
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Parent directory for produced scaffold-run artifacts.",
    )
    parser.add_argument(
        "--task-dir",
        type=Path,
        default=_DEFAULT_FIXTURE,
        help="Source packet directory (defaults to the RSH-001 fixture).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=_DEFAULT_REPORT,
        help="Markdown report file. Appended; not overwritten.",
    )
    parser.add_argument(
        "--per-cell-report",
        type=Path,
        default=_DEFAULT_SMOKE_REPORT,
        help="Per-cell smoke report (passed to the spawned smoke script).",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        default=list(MLX_MODEL_ALLOWLIST),
        choices=list(MLX_MODEL_ALLOWLIST),
        help="Subset of models to run. Defaults to all five.",
    )
    parser.add_argument(
        "--conditions",
        nargs="+",
        default=list(_CONDITIONS),
        choices=list(_CONDITIONS),
        help="Subset of conditions to run. Defaults to all four.",
    )
    parser.add_argument(
        "--extractor",
        choices=("stub", "all"),
        default="stub",
        help=(
            "Extractor set passed to the per-cell smoke script. "
            "'all' runs the stub, Nemo, and Small 3 as sidecars."
        ),
    )
    parser.add_argument(
        "--official-extractor",
        choices=("stub", "nemo", "small3"),
        default=None,
        help=(
            "Which extraction each cell writes to claims.yaml. Defaults to Nemo "
            "when --extractor=all (calibration of record: Nemo F1 0.8916), else "
            "the single extractor that ran."
        ),
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Generation temperature.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=2048,
        help="Max generated tokens.",
    )
    parser.add_argument(
        "--cell-timeout",
        type=int,
        default=1800,
        help="Per-cell subprocess timeout in seconds (default 30 minutes).",
    )
    parser.add_argument(
        "--skip-verify-intake",
        action="store_true",
        help="Skip the evidence-bundler verify-intake gate (per-cell).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help=(
            "Skip (model, condition) cells that already have a completed "
            "scaffold-run in --output-dir, so an interrupted run self-heals on "
            "re-invocation instead of duplicating cells."
        ),
    )
    return parser.parse_args()


def _now_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _completed_pairs(output_dir: Path) -> set[tuple[str, str]]:
    """(model_id, condition) pairs that already have a completed cell.

    A cell counts as complete when its scaffold-run dir carries both
    ``run_disposition.yaml`` and ``scaffold_run.yaml``. Partial dirs (crashed
    mid-write) are ignored so the pair re-runs.
    """
    pairs: set[tuple[str, str]] = set()
    for cell in output_dir.glob("scaffold-run-*"):
        disp_path = cell / "run_disposition.yaml"
        manifest_path = cell / "scaffold_run.yaml"
        if not (disp_path.exists() and manifest_path.exists()):
            continue
        try:
            disp = load_yaml(disp_path)
            manifest = load_yaml(manifest_path)
        except Exception:  # noqa: BLE001 — a malformed cell just re-runs
            continue
        model_id = (manifest.get("model") or {}).get("model_id")
        condition = disp.get("workflow_condition")
        if model_id and condition:
            pairs.add((model_id, condition))
    return pairs


def _run_cell(args: argparse.Namespace, model: str, condition: str) -> dict:
    cmd = [
        sys.executable,
        str(_SMOKE_SCRIPT),
        "--model", model,
        "--condition", condition,
        "--task-dir", str(args.task_dir),
        "--output-dir", str(args.output_dir),
        "--report", str(args.per_cell_report),
        "--extractor", args.extractor,
        "--temperature", str(args.temperature),
        "--max-tokens", str(args.max_tokens),
    ]
    if args.official_extractor is not None:
        cmd.extend(["--official-extractor", args.official_extractor])
    if args.skip_verify_intake:
        cmd.append("--skip-verify-intake")

    started_at = _now_iso()
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=args.cell_timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "started_at": started_at,
            "ended_at": _now_iso(),
            "model": model,
            "condition": condition,
            "status": "fail",
            "error": f"timeout after {args.cell_timeout}s",
            "stdout_tail": "",
            "stderr_tail": "",
        }

    parsed = _parse_json_line(completed.stdout)
    if parsed is None:
        parsed = {
            "model": model,
            "condition": condition,
            "status": "fail",
            "error": "smoke script did not emit CELL_RESULT_JSON",
        }
    parsed["returncode"] = completed.returncode
    parsed["stdout_tail"] = completed.stdout.strip().splitlines()[-1:]
    parsed["stderr_tail"] = completed.stderr.strip().splitlines()[-5:]
    parsed.setdefault("started_at", started_at)
    parsed.setdefault("ended_at", _now_iso())
    if completed.returncode != 0 and parsed.get("status") == "pass":
        parsed["status"] = "fail"
        parsed.setdefault("error", f"smoke returncode={completed.returncode}")
    return parsed


def _parse_json_line(stdout: str) -> dict | None:
    for line in reversed(stdout.splitlines()):
        if line.startswith("CELL_RESULT_JSON "):
            try:
                return json.loads(line[len("CELL_RESULT_JSON "):])
            except json.JSONDecodeError:
                return None
    return None


def _append_header(report_path: Path, args: argparse.Namespace, started_at: str) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    initial = not report_path.exists()
    with report_path.open("a", encoding="utf-8") as fh:
        if initial:
            fh.write("# Phase 2 Unit 4 — Matrix Report\n\n")
            fh.write(
                "Append-only. Each run of the matrix script writes a fresh "
                "section. Re-runs after a fix are stacked here so the audit "
                "trail preserves prior failures.\n\n"
            )
        fh.write("---\n\n")
        fh.write(f"## Matrix run started {started_at}\n\n")
        fh.write(f"- task_dir: `{args.task_dir}`\n")
        fh.write(f"- output_dir: `{args.output_dir}`\n")
        fh.write(f"- per_cell_report: `{args.per_cell_report}`\n")
        fh.write(f"- temperature: `{args.temperature}`\n")
        fh.write(f"- max_tokens: `{args.max_tokens}`\n")
        fh.write(f"- models: `{args.models}`\n")
        fh.write(f"- conditions: `{args.conditions}`\n")
        fh.write(f"- extractor: `{args.extractor}`\n")
        fh.write(f"- official_extractor: `{args.official_extractor or 'auto (nemo if all)'}`\n")
        fh.write(f"- skip_verify_intake: `{args.skip_verify_intake}`\n")
        fh.write(f"- resume: `{args.resume}`\n\n")
        fh.write(
            "| Model | Condition | Status | run_id | "
            "verify_intake | revision | mlx-lm | elapsed_s | scaffold_run_dir |\n"
        )
        fh.write(
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
        )


def _append_row(report_path: Path, cell: dict) -> None:
    with report_path.open("a", encoding="utf-8") as fh:
        revision = cell.get("model_revision", "")
        short_revision = revision[:12] if revision else "—"
        if cell.get("verify_intake_skipped"):
            verify = "skipped"
        else:
            verify = cell.get("verify_intake_returncode", "—")
        fh.write(
            "| {model} | {condition} | {status} | `{run_id}` | "
            "`{verify}` | `{revision}` | `{mlx_lm_version}` | "
            "`{elapsed}` | `{scaffold_run_dir}` |\n".format(
                model=cell.get("model", "?"),
                condition=cell.get("condition", "?"),
                status=cell.get("status", "?"),
                run_id=cell.get("run_id", "—"),
                verify=verify,
                revision=short_revision,
                mlx_lm_version=cell.get("mlx_lm_version", "—"),
                elapsed=cell.get("elapsed_seconds", "—"),
                scaffold_run_dir=cell.get("scaffold_run_dir", "—"),
            )
        )


def _append_footer(report_path: Path, cells: list[dict], ended_at: str) -> None:
    total = len(cells)
    passes = sum(1 for c in cells if c.get("status") == "pass")
    skipped = sum(1 for c in cells if c.get("status") == "skipped")
    fails = total - passes - skipped
    failed_rows = [c for c in cells if c.get("status") not in ("pass", "skipped")]

    with report_path.open("a", encoding="utf-8") as fh:
        fh.write("\n")
        fh.write(f"### Summary — ended {ended_at}\n\n")
        fh.write(f"- total_cells: `{total}`\n")
        fh.write(f"- passed: `{passes}`\n")
        fh.write(f"- skipped_resume: `{skipped}`\n")
        fh.write(f"- failed: `{fails}`\n")
        if failed_rows:
            fh.write("\n#### Failed cells\n\n")
            for cell in failed_rows:
                fh.write(
                    f"- `{cell.get('model', '?')}` / "
                    f"`{cell.get('condition', '?')}` — "
                    f"{cell.get('error', 'no error captured')}\n"
                )
                tail = cell.get("stderr_tail") or []
                if tail:
                    fh.write("\n  stderr_tail:\n  ```\n")
                    for line in tail:
                        fh.write(f"  {line}\n")
                    fh.write("  ```\n")
        fh.write("\n")


def main() -> int:
    args = _parse_args()
    started_at = _now_iso()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    completed = _completed_pairs(args.output_dir) if args.resume else set()
    if args.resume:
        print(
            f"[matrix] resume: {len(completed)} completed cell(s) in "
            f"{args.output_dir} will be skipped",
            flush=True,
        )
    _append_header(args.report, args, started_at)

    cells: list[dict] = []
    for model in args.models:
        for condition in args.conditions:
            if (model, condition) in completed:
                print(
                    f"[matrix] {model} / {condition} — SKIP (already complete)",
                    flush=True,
                )
                skip_cell = {"model": model, "condition": condition, "status": "skipped"}
                _append_row(args.report, skip_cell)
                cells.append(skip_cell)
                continue
            print(f"[matrix] {model} / {condition}", flush=True)
            cell = _run_cell(args, model, condition)
            _append_row(args.report, cell)
            cells.append(cell)
            print(
                f"[matrix]   status={cell.get('status')} "
                f"elapsed={cell.get('elapsed_seconds')}s",
                flush=True,
            )

    ended_at = _now_iso()
    _append_footer(args.report, cells, ended_at)

    all_ok = all(c.get("status") in ("pass", "skipped") for c in cells)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
