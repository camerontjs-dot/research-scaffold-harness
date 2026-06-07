"""Uniform claim extractor tests for raw runner output."""

from __future__ import annotations

from pathlib import Path
from typing import get_args

import pytest

from research_scaffold_harness.extractor import (
    StubUniformExtractor,
    extract_claims_from_runner_result,
)
from research_scaffold_harness.models.common import WRITER_SCHEMA_VERSION, WorkflowCondition
from research_scaffold_harness.runner import (
    ModelResponse,
    RunnerResult,
    StubModelAdapter,
    load_source_packet,
    run_source_packet,
)

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source-packet-minimal"
_CONDITIONS = get_args(WorkflowCondition)


@pytest.mark.parametrize("condition", _CONDITIONS)
def test_stub_extractor_processes_final_claims_for_each_condition(
    condition: WorkflowCondition,
) -> None:
    packet = load_source_packet(_FIXTURE_DIR)
    runner_result = run_source_packet(packet, condition, StubModelAdapter())
    extraction = extract_claims_from_runner_result(
        result=runner_result,
        run_id=f"unit3-{condition}",
        adapter=StubUniformExtractor(),
        generated_at_utc="2026-05-17T00:00:00Z",
    )

    assert extraction.extractor_id == "stub-offline-deterministic"
    assert extraction.extractor_version == "0.1.0"
    assert extraction.is_stub is True
    assert extraction.diagnostics == ()
    assert extraction.claims.schema_version == WRITER_SCHEMA_VERSION
    assert extraction.claims.run_id == f"unit3-{condition}"
    assert len(extraction.claims.claims) >= 1

    claim_texts = [claim.claim_text for claim in extraction.claims.claims]
    assert all("STUB MODEL OUTPUT" not in text for text in claim_texts)
    assert all("task_id:" not in text for text in claim_texts)
    assert all("condition:" not in text for text in claim_texts)
    assert all("Claim table:" not in text for text in claim_texts)
    assert all("Final claim audit table:" not in text for text in claim_texts)

    for index, claim in enumerate(extraction.claims.claims, start=1):
        assert claim.claim_id == f"unit3-{condition}-c{index:03d}"
        assert claim.claim_type == "extracted_claim"
        assert claim.support_status == "uncertain"
        assert claim.claim_strength == 0.5
        assert claim.extraction_fidelity == 0.5
        assert claim.source_refs == []
        assert claim.counterevidence_checked is False
        assert claim.counterevidence_found is False
        assert claim.downgraded is False
        assert "extractor_id=stub-offline-deterministic" in claim.scaffold_notes


@pytest.mark.parametrize("condition", ("format_only", "provenance_scaffold", "full_scaffold"))
def test_stub_extractor_ignores_scaffold_preamble_segments(
    condition: WorkflowCondition,
) -> None:
    packet = load_source_packet(_FIXTURE_DIR)
    runner_result = run_source_packet(packet, condition, StubModelAdapter())

    extraction = extract_claims_from_runner_result(
        result=runner_result,
        run_id=f"segment-{condition}",
        adapter=StubUniformExtractor(),
    )

    assert "Claim table:" in runner_result.output_text or "Final claim audit table:" in (
        runner_result.output_text
    )
    assert "Claim table:" not in extraction.final_claims_text
    assert "Final claim audit table:" not in extraction.final_claims_text
    # final_claims_text is the segment AFTER the marker; the marker line itself
    # is stripped by the extractor.
    assert not extraction.final_claims_text.lstrip().lower().startswith("final claims:")


def test_stub_extractor_deduplicates_exact_repeated_claims() -> None:
    runner_result = _runner_result(
        "Final claims:\n"
        "The packet supports a quality-system claim.\n"
        "The packet supports a quality-system claim.\n"
        "A second extracted claim remains available."
    )

    extraction = extract_claims_from_runner_result(
        result=runner_result,
        run_id="dedupe-run",
        adapter=StubUniformExtractor(),
    )

    assert [claim.claim_text for claim in extraction.claims.claims] == [
        "The packet supports a quality-system claim.",
        "A second extracted claim remains available.",
    ]


def test_stub_extractor_returns_empty_registry_without_final_claims_marker() -> None:
    runner_result = _runner_result(
        "STUB MODEL OUTPUT - OFFLINE DETERMINISTIC\n"
        "task_id: rsh-001-fixture\n"
        "This output has no final-claims marker."
    )

    extraction = extract_claims_from_runner_result(
        result=runner_result,
        run_id="missing-final-claims",
        adapter=StubUniformExtractor(),
    )

    assert extraction.final_claims_text == ""
    assert extraction.claims.run_id == "missing-final-claims"
    assert extraction.claims.claims == []
    assert extraction.diagnostics == ("final-claims marker not found",)


def test_stub_extractor_reports_empty_final_claims_segment() -> None:
    runner_result = _runner_result("Final claims:\n")

    extraction = extract_claims_from_runner_result(
        result=runner_result,
        run_id="empty-final-claims",
        adapter=StubUniformExtractor(),
    )

    assert extraction.claims.claims == []
    assert extraction.diagnostics == ("final-claims segment contained no extractable claims",)


def test_stub_extractor_recovers_latest_nonempty_final_claims_segment() -> None:
    runner_result = _runner_result(
        "Answer text.\n\n"
        "Final claims:\n"
        "- Management responsibility is part of the quality-system picture.\n"
        "- CAPA includes correction and prevention activities.\n\n"
        "Final claims:\n"
        "- \n"
        "- \n"
    )

    extraction = extract_claims_from_runner_result(
        result=runner_result,
        run_id="double-marker-run",
        adapter=StubUniformExtractor(),
    )

    assert [claim.claim_text for claim in extraction.claims.claims] == [
        "Management responsibility is part of the quality-system picture.",
        "CAPA includes correction and prevention activities.",
    ]
    assert extraction.diagnostics == ()


def test_stub_extractor_keeps_empty_diagnostic_when_all_markers_are_empty() -> None:
    runner_result = _runner_result("Final claims:\n- \n\nFinal claims:\n- \n")

    extraction = extract_claims_from_runner_result(
        result=runner_result,
        run_id="all-empty-markers",
        adapter=StubUniformExtractor(),
    )

    assert extraction.claims.claims == []
    assert extraction.diagnostics == ("final-claims segment contained no extractable claims",)


def _runner_result(raw_output: str) -> RunnerResult:
    return RunnerResult(
        task_id="rsh-001-fixture",
        condition="baseline",
        prompt_template_id="baseline-v1",
        prompt_template_hash="sha256:" + "a" * 64,
        rendered_prompt_hash="sha256:" + "b" * 64,
        prompt="Rendered prompt",
        response=ModelResponse(
            model_id="stub-offline-deterministic",
            model_version="0.1.0",
            api_endpoint="stub://offline",
            text=raw_output,
            finish_reason="stop",
            output_tokens=len(raw_output.split()),
        ),
    )
