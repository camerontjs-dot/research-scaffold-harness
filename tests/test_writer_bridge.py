"""Writer-bridge tests using canned runner output and the stub extractor.

These tests verify that the bridge converts a deterministic offline run into
a C-A artifact directory that satisfies the Phase 1 writer's integrity
checks and, when Evidence Bundler is installed in the same venv, passes
``evidence-bundler verify-intake``.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import get_args

import pytest

from research_scaffold_harness.contracts.yaml_io import load_yaml
from research_scaffold_harness.extractor import (
    StubUniformExtractor,
    extract_claims_from_runner_result,
)
from research_scaffold_harness.models.common import WorkflowCondition
from research_scaffold_harness.runner import (
    RunnerSettings,
    StubModelAdapter,
    load_source_packet,
    run_source_packet,
)
from research_scaffold_harness.runner.writer_bridge import (
    WriterBridgeError,
    _encode_model_version,
    build_run_disposition_fields,
    find_evidence_bundler_binary,
    mint_run_id,
    resolve_official_extractor,
    select_official_extraction,
    write_scaffold_run_from_extraction,
)

# Identities used to fabricate live-extractor results offline (no MLX load).
_NEMO_ID = "mlx-mistral-nemo-12b"
_SMALL3_ID = "mlx-mistral-small3"


def _as_live(extraction, extractor_id: str):
    """Return a copy of a stub extraction stamped with a live extractor identity."""
    return replace(extraction, extractor_id=extractor_id, is_stub=False)

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source-packet-minimal"
_CONDITIONS = get_args(WorkflowCondition)


def _prepare_run(condition: str, *, run_id: str | None = None):
    packet = load_source_packet(_FIXTURE_DIR)
    adapter = StubModelAdapter()
    settings = RunnerSettings(temperature=0.0, max_tokens=512)
    runner_result = run_source_packet(packet, condition, adapter, settings)  # type: ignore[arg-type]
    run_id = run_id or mint_run_id()
    extraction = extract_claims_from_runner_result(
        result=runner_result,
        run_id=run_id,
        adapter=StubUniformExtractor(),
    )
    return packet, runner_result, extraction


def test_bridge_produces_complete_artifact_directory(tmp_path: Path) -> None:
    packet, runner_result, extraction = _prepare_run("baseline")

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    run_dir = bridge_result.scaffold_run_dir
    assert run_dir.is_dir()
    assert (run_dir / "scaffold_run.yaml").is_file()
    assert (run_dir / "claims.yaml").is_file()
    assert (run_dir / "CONTRACT_VERSION").is_file()
    assert (run_dir / "SHA256SUMS").is_file()
    assert (run_dir / "corpus" / "src-001" / "content.md").is_file()
    assert (run_dir / "corpus" / "src-001" / "metadata.yaml").is_file()
    assert (run_dir / "corpus" / "src-001" / "passages.yaml").is_file()


def test_bridge_run_id_matches_directory_and_extraction(tmp_path: Path) -> None:
    run_id = mint_run_id()
    packet, runner_result, extraction = _prepare_run("baseline", run_id=run_id)

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    assert bridge_result.run_id == run_id
    assert bridge_result.scaffold_run_dir.name == f"scaffold-run-{run_id}"


def test_bridge_rejects_blank_run_id(tmp_path: Path) -> None:
    packet, runner_result, extraction = _prepare_run("baseline")
    object.__setattr__(extraction.claims, "run_id", "")
    with pytest.raises(WriterBridgeError, match="run_id"):
        write_scaffold_run_from_extraction(
            runner_result=runner_result,
            extraction=extraction,
            source_packet=packet,
            output_dir=tmp_path,
        )


def test_bridge_preserves_extractor_identity_in_notes(tmp_path: Path) -> None:
    packet, runner_result, extraction = _prepare_run("baseline")

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    manifest = load_yaml(bridge_result.scaffold_run_dir / "scaffold_run.yaml")
    notes = manifest["run_metadata"]["notes"]
    assert "extractor_id: stub-offline-deterministic" in notes
    assert "extractor_is_stub: true" in notes
    assert "chat_template_applied:" in notes
    assert "raw_output_char_len:" in notes


def test_bridge_writes_raw_output_and_run_disposition_sidecars(tmp_path: Path) -> None:
    packet, runner_result, extraction = _prepare_run("baseline")

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    run_dir = bridge_result.scaffold_run_dir
    assert (run_dir / "raw_output.txt").read_text(encoding="utf-8") == (
        runner_result.output_text
    )
    disposition = load_yaml(run_dir / "run_disposition.yaml")
    assert disposition["disposition"] == "ready_for_audit"
    assert disposition["human_review_required"] is False
    assert disposition["extracted_claim_count"] >= 1
    assert "raw_output.txt" in (run_dir / "SHA256SUMS").read_text(encoding="utf-8")
    assert "run_disposition.yaml" in (run_dir / "SHA256SUMS").read_text(encoding="utf-8")


def test_bridge_zero_claims_require_human_scan(tmp_path: Path) -> None:
    packet, runner_result, extraction = _prepare_run("baseline")
    object.__setattr__(extraction.claims, "claims", [])
    object.__setattr__(extraction, "diagnostics", ("final-claims segment empty",))

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    disposition = load_yaml(bridge_result.scaffold_run_dir / "run_disposition.yaml")
    assert disposition["disposition"] == "requires_human_zero_claim_scan"
    assert disposition["human_review_required"] is True
    assert "valid_zero_claim_answer" in disposition["allowed_after_human_review"]


def test_bridge_blank_raw_output_marks_missing_raw_output(tmp_path: Path) -> None:
    packet, runner_result, extraction = _prepare_run("baseline")
    object.__setattr__(runner_result.response, "text", "")
    object.__setattr__(extraction.claims, "claims", [])

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    disposition = load_yaml(bridge_result.scaffold_run_dir / "run_disposition.yaml")
    assert disposition["disposition"] == "missing_raw_output"
    assert disposition["human_review_required"] is False


def test_bridge_think_only_output_marks_missing_final_answer(tmp_path: Path) -> None:
    packet, runner_result, extraction = _prepare_run("baseline")
    object.__setattr__(runner_result.response, "text", "<think>reasoning only</think>")
    object.__setattr__(extraction.claims, "claims", [])

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    disposition = load_yaml(bridge_result.scaffold_run_dir / "run_disposition.yaml")
    assert disposition["disposition"] == "missing_final_answer"
    assert disposition["think_block_present"] is True


def test_bridge_preserves_extractor_identity_in_claim_notes(tmp_path: Path) -> None:
    packet, runner_result, extraction = _prepare_run("baseline")

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    claims_doc = load_yaml(bridge_result.scaffold_run_dir / "claims.yaml")
    assert claims_doc["claims"], "stub extractor must produce at least one claim"
    for claim in claims_doc["claims"]:
        assert "extractor_id=stub-offline-deterministic" in claim["scaffold_notes"]
        assert "stub=true" in claim["scaffold_notes"]


def test_bridge_encodes_model_identity_into_model_version_field(tmp_path: Path) -> None:
    packet, runner_result, extraction = _prepare_run("baseline")

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    manifest = load_yaml(bridge_result.scaffold_run_dir / "scaffold_run.yaml")
    model = manifest["model"]
    assert model["model_id"] == "stub-offline-deterministic"
    assert model["model_version"].startswith("0.1.0")
    assert model["api_endpoint"] == "stub://offline"


def test_encode_model_version_includes_revision_and_quant_when_set() -> None:
    class _Response:
        model_version = "0.18.0"
        model_revision = "abc1234567890def"
        quantization = "qat-4bit"

    encoded = _encode_model_version(_Response())
    assert "0.18.0" in encoded
    assert "rev:abc123456789" in encoded
    assert "quant:qat-4bit" in encoded


def test_encode_model_version_handles_missing_fields() -> None:
    class _Response:
        model_version = "0.1.0"
        model_revision = ""
        quantization = ""

    encoded = _encode_model_version(_Response())
    assert encoded == "0.1.0"


@pytest.mark.parametrize("condition", _CONDITIONS)
def test_bridge_does_not_promote_scaffold_tables(
    condition: WorkflowCondition, tmp_path: Path,
) -> None:
    """Stub extractor output, not scaffold-native tables, populates claims.yaml.

    The ADR boundary says only the uniform extractor's final-claims segment
    feeds claims.yaml. Scaffold conditions emit claim/evidence/audit tables in
    the raw output; none of those rows must appear as official claims.
    """
    packet, runner_result, extraction = _prepare_run(condition)

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    claims_doc = load_yaml(bridge_result.scaffold_run_dir / "claims.yaml")
    raw_output = runner_result.output_text
    final_claims = extraction.final_claims_text

    assert "Final claims:" in raw_output
    assert final_claims
    for claim in claims_doc["claims"]:
        assert claim["claim_text"] in final_claims, (
            f"Claim {claim['claim_id']!r} not in final-claims segment for {condition}"
        )
        assert "| --- |" not in claim["claim_text"]
        assert "| claim text" not in claim["claim_text"]


@pytest.mark.parametrize("condition", _CONDITIONS)
def test_bridge_artifact_passes_verify_intake(
    condition: WorkflowCondition, tmp_path: Path,
) -> None:
    binary = find_evidence_bundler_binary()
    if binary is None:
        pytest.skip(
            "evidence-bundler CLI not found next to sys.executable or on PATH; "
            "install in the same venv to run this gate"
        )

    packet, runner_result, extraction = _prepare_run(condition)
    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    completed = subprocess.run(
        [str(binary), "verify-intake", str(bridge_result.scaffold_run_dir)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert completed.returncode == 0, (
        f"verify-intake failed for {condition}:\n"
        f"stdout: {completed.stdout}\nstderr: {completed.stderr}"
    )


def test_bridge_sidecar_rich_artifact_passes_verify_intake(tmp_path: Path) -> None:
    binary = find_evidence_bundler_binary()
    if binary is None:
        pytest.skip("evidence-bundler CLI not found")

    packet, runner_result, extraction = _prepare_run("baseline")
    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
        extractor_sidecars=[extraction],
        exploratory_think_extraction=extraction,
    )

    assert (
        bridge_result.scaffold_run_dir / "intermediates" / "claims_extractor_stub.yaml"
    ).is_file()
    assert (
        bridge_result.scaffold_run_dir / "exploratory" / "think_block_claims.yaml"
    ).is_file()
    completed = subprocess.run(
        [str(binary), "verify-intake", str(bridge_result.scaffold_run_dir)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr


def test_bridge_artifact_yaml_keys_use_existing_schema(tmp_path: Path) -> None:
    """No new YAML keys are introduced beyond the Phase 1 writer schema."""
    packet, runner_result, extraction = _prepare_run("baseline")

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )

    manifest = load_yaml(bridge_result.scaffold_run_dir / "scaffold_run.yaml")
    expected_top_level = {
        "run_id", "task_id", "workflow_condition", "timestamp_utc",
        "scaffold", "model", "task", "corpus",
        "intermediates_present", "run_metadata",
    }
    assert set(manifest.keys()) == expected_top_level
    assert set(manifest["model"].keys()) == {
        "model_id", "model_version", "api_endpoint", "temperature", "max_tokens",
    }


def test_two_runs_produce_distinct_run_ids(tmp_path: Path) -> None:
    packet, runner_result, _ = _prepare_run("baseline")

    extraction_a = extract_claims_from_runner_result(
        result=runner_result,
        run_id=mint_run_id(),
        adapter=StubUniformExtractor(),
    )
    bridge_a = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction_a,
        source_packet=packet,
        output_dir=tmp_path,
    )

    extraction_b = extract_claims_from_runner_result(
        result=runner_result,
        run_id=mint_run_id(),
        adapter=StubUniformExtractor(),
    )
    bridge_b = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=extraction_b,
        source_packet=packet,
        output_dir=tmp_path,
    )

    assert bridge_a.run_id != bridge_b.run_id
    assert bridge_a.scaffold_run_dir != bridge_b.scaffold_run_dir


# ---------------------------------------------------------------------------
# Official-extractor selection (post-calibration: Nemo is the official extractor)
# ---------------------------------------------------------------------------


def test_resolve_official_extractor_default_is_nemo_for_all_set() -> None:
    assert resolve_official_extractor("all", None) == "nemo"
    assert resolve_official_extractor("stub", None) == "stub"
    assert resolve_official_extractor("nemo", None) == "nemo"
    assert resolve_official_extractor("small3", None) == "small3"
    # An explicit request always wins over the default.
    assert resolve_official_extractor("all", "stub") == "stub"
    assert resolve_official_extractor("all", "small3") == "small3"


def test_select_official_extraction_picks_named_extractor() -> None:
    _, _, stub_extraction = _prepare_run("baseline")
    nemo = _as_live(stub_extraction, _NEMO_ID)
    small3 = _as_live(stub_extraction, _SMALL3_ID)
    extractions = [stub_extraction, nemo, small3]
    assert select_official_extraction(extractions, "nemo") is nemo
    assert select_official_extraction(extractions, "small3") is small3
    assert select_official_extraction(extractions, "stub") is stub_extraction


def test_select_official_extraction_raises_when_extractor_absent() -> None:
    _, _, stub_extraction = _prepare_run("baseline")
    with pytest.raises(WriterBridgeError, match="did not run"):
        select_official_extraction([stub_extraction], "nemo")


def test_bridge_writes_selected_nemo_official_not_stub(tmp_path: Path) -> None:
    """Selecting Nemo writes Nemo to claims.yaml + disposition; all sidecars persist."""
    packet, runner_result, stub_extraction = _prepare_run("baseline")
    nemo_extraction = _as_live(stub_extraction, _NEMO_ID)

    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=nemo_extraction,
        source_packet=packet,
        output_dir=tmp_path,
        extractor_sidecars=[stub_extraction, nemo_extraction],
    )

    assert bridge_result.extractor_id == _NEMO_ID
    assert bridge_result.is_stub is False

    run_dir = bridge_result.scaffold_run_dir
    disposition = load_yaml(run_dir / "run_disposition.yaml")
    assert disposition["extractor_id"] == _NEMO_ID
    assert disposition["extractor_is_stub"] is False
    assert disposition["extracted_claim_count"] == len(nemo_extraction.claims.claims)

    manifest = load_yaml(run_dir / "scaffold_run.yaml")
    assert "extractor_is_stub: false" in manifest["run_metadata"]["notes"]

    assert (run_dir / "intermediates" / "claims_extractor_stub.yaml").is_file()
    assert (run_dir / "intermediates" / "claims_extractor_nemo.yaml").is_file()


def test_build_run_disposition_fields_routes_zero_claim_body_to_human_scan() -> None:
    """Pure disposition core: zero claims but a visible body → human zero-claim scan."""
    fields = build_run_disposition_fields(
        raw_output="The core elements are governance and validation.",
        run_id="rsh-test",
        task_id="rsh-001-fixture",
        workflow_condition="baseline",
        generated_at_utc="2026-06-01T00:00:00Z",
        extractor_id=_NEMO_ID,
        extractor_is_stub=False,
        extracted_claim_count=0,
        extractor_diagnostics=["official-answer-body-empty"],
    )
    assert fields["disposition"] == "requires_human_zero_claim_scan"
    assert fields["human_review_required"] is True
    assert fields["extractor_is_stub"] is False


def test_build_run_disposition_fields_matches_bridge_output(tmp_path: Path) -> None:
    """The pure core and the object-based builder agree field-for-field.

    Guards the Stage-2 re-pointing tool: it recomputes dispositions via the pure
    core, which must stay byte-identical to what the writer bridge emits.
    """
    packet, runner_result, stub_extraction = _prepare_run("baseline")
    nemo_extraction = _as_live(stub_extraction, _NEMO_ID)
    bridge_result = write_scaffold_run_from_extraction(
        runner_result=runner_result,
        extraction=nemo_extraction,
        source_packet=packet,
        output_dir=tmp_path,
    )
    written = load_yaml(bridge_result.scaffold_run_dir / "run_disposition.yaml")
    recomputed = build_run_disposition_fields(
        raw_output=runner_result.response.text,
        run_id=written["run_id"],
        task_id=written["task_id"],
        workflow_condition=written["workflow_condition"],
        generated_at_utc=written["generated_at_utc"],
        extractor_id=nemo_extraction.extractor_id,
        extractor_is_stub=nemo_extraction.is_stub,
        extracted_claim_count=len(nemo_extraction.claims.claims),
        extractor_diagnostics=list(nemo_extraction.diagnostics),
    )
    assert recomputed == written


# ---------------------------------------------------------------------------
# CLI shape tests for the new --adapter mlx and --write flags
# ---------------------------------------------------------------------------


def _cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "research_scaffold_harness.cli", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_cli_write_requires_extract() -> None:
    result = _cli(
        "run-task",
        "--task", str(_FIXTURE_DIR),
        "--condition", "baseline",
        "--adapter", "stub",
        "--write",
    )
    assert result.returncode == 2
    assert "--write requires --extract" in result.stderr


def test_cli_write_requires_output_dir() -> None:
    result = _cli(
        "run-task",
        "--task", str(_FIXTURE_DIR),
        "--condition", "baseline",
        "--adapter", "stub",
        "--extract",
        "--write",
    )
    assert result.returncode == 2
    assert "--output-dir" in result.stderr


def test_cli_mlx_requires_model() -> None:
    result = _cli(
        "run-task",
        "--task", str(_FIXTURE_DIR),
        "--condition", "baseline",
        "--adapter", "mlx",
    )
    assert result.returncode == 2
    assert "--adapter=mlx requires --model" in result.stderr


def test_cli_run_task_help_advertises_official_extractor() -> None:
    result = _cli("run-task", "--help")
    assert result.returncode == 0
    assert "--official-extractor" in result.stdout


def test_cli_official_extractor_requires_matching_extractor_set(tmp_path: Path) -> None:
    """The pre-calibration hard block is gone; a mismatched official is a fast error."""
    result = _cli(
        "run-task",
        "--task", str(_FIXTURE_DIR),
        "--condition", "baseline",
        "--adapter", "stub",
        "--extract",
        "--extractor", "stub",
        "--official-extractor", "nemo",
        "--write",
        "--output-dir", str(tmp_path),
    )
    assert result.returncode == 2
    assert "requires --extractor=nemo or --extractor=all" in result.stderr
    # The deprecated pre-calibration message must no longer appear.
    assert "blocked before calibration" not in result.stderr


def test_cli_stub_write_produces_artifact(tmp_path: Path) -> None:
    result = _cli(
        "run-task",
        "--task", str(_FIXTURE_DIR),
        "--condition", "baseline",
        "--adapter", "stub",
        "--extract",
        "--write",
        "--output-dir", str(tmp_path),
    )
    assert result.returncode == 0, result.stderr
    assert "artifact:" in result.stdout
    assert "run_id:" in result.stdout
    assert "extractor: stub-offline-deterministic" in result.stdout
    assert "is_stub:   true" in result.stdout

    run_dirs = list(tmp_path.glob("scaffold-run-*"))
    assert len(run_dirs) == 1
    assert (run_dirs[0] / "scaffold_run.yaml").is_file()
    assert (run_dirs[0] / "claims.yaml").is_file()
    assert (run_dirs[0] / "raw_output.txt").is_file()
    assert (run_dirs[0] / "run_disposition.yaml").is_file()
