"""Runner skeleton and deterministic stub adapter tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import get_args

import pytest

from research_scaffold_harness.models.common import WorkflowCondition
from research_scaffold_harness.prompts import hash_template, load_template
from research_scaffold_harness.runner import (
    RunnerError,
    RunnerSettings,
    SourcePacketError,
    StubModelAdapter,
    load_source_packet,
    run_source_packet,
)

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source-packet-minimal"
_CONDITIONS = get_args(WorkflowCondition)


def _cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "research_scaffold_harness.cli", *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_load_source_packet_consumes_task_and_source_text() -> None:
    packet = load_source_packet(_FIXTURE_DIR)

    assert packet.task.task_id == "rsh-001-fixture"
    assert packet.task.research_question.startswith("What are the core elements")
    assert len(packet.sources) == 1
    assert packet.sources[0].source_id == "src-001"
    assert "Management Responsibility" in packet.sources[0].text
    assert packet.prompt_sources()[0].text == packet.sources[0].text


def test_load_source_packet_rejects_missing_task(tmp_path: Path) -> None:
    with pytest.raises(SourcePacketError, match="task.yaml not found"):
        load_source_packet(tmp_path)


@pytest.mark.parametrize("condition", _CONDITIONS)
def test_stub_runner_renders_frozen_prompt_for_each_condition(
    condition: WorkflowCondition,
) -> None:
    packet = load_source_packet(_FIXTURE_DIR)
    result = run_source_packet(packet, condition, StubModelAdapter())
    template = load_template(condition)

    assert result.task_id == packet.task.task_id
    assert result.condition == condition
    assert result.prompt_template_id == template.template_id
    assert result.prompt_template_hash == hash_template(template)
    assert packet.task.research_question in result.prompt
    assert "Management Responsibility" in result.prompt
    assert "{{" not in result.prompt
    assert "}}" not in result.prompt
    assert result.response.model_id == "stub-offline-deterministic"
    assert "STUB MODEL OUTPUT - OFFLINE DETERMINISTIC" in result.output_text
    assert f"condition: {condition}" in result.output_text


def test_stub_runner_is_deterministic() -> None:
    packet = load_source_packet(_FIXTURE_DIR)
    adapter = StubModelAdapter()

    first = run_source_packet(packet, "full_scaffold", adapter)
    second = run_source_packet(packet, "full_scaffold", adapter)

    assert first.rendered_prompt_hash == second.rendered_prompt_hash
    assert first.output_text == second.output_text


def test_runner_rejects_empty_sources() -> None:
    packet = load_source_packet(_FIXTURE_DIR)

    with pytest.raises(RunnerError, match="at least one source"):
        from research_scaffold_harness.runner import run_task

        run_task(packet.task, (), "baseline", StubModelAdapter())


def test_runner_settings_validate_generation_bounds() -> None:
    with pytest.raises(RunnerError, match="temperature"):
        RunnerSettings(temperature=-0.1)

    with pytest.raises(RunnerError, match="max_tokens"):
        RunnerSettings(max_tokens=0)


@pytest.mark.parametrize("condition", _CONDITIONS)
def test_run_task_cli_uses_stub_adapter(condition: WorkflowCondition) -> None:
    result = _cli(
        "run-task",
        "--task", str(_FIXTURE_DIR),
        "--condition", condition,
        "--adapter", "stub",
    )

    assert result.returncode == 0, result.stderr
    assert "adapter:   stub-offline-deterministic" in result.stdout
    assert f"condition: {condition}" in result.stdout
    assert "STUB MODEL OUTPUT - OFFLINE DETERMINISTIC" in result.stdout


def test_run_task_cli_can_run_stub_uniform_extractor() -> None:
    result = _cli(
        "run-task",
        "--task", str(_FIXTURE_DIR),
        "--condition", "full_scaffold",
        "--adapter", "stub",
        "--extract",
    )

    assert result.returncode == 0, result.stderr
    assert "raw_output:" in result.stdout
    assert "extraction:" in result.stdout
    assert "extractor: stub-offline-deterministic" in result.stdout
    assert "is_stub: true" in result.stdout
    assert "claim_count: 2" in result.stdout
    assert "Final claim audit table:" in result.stdout
    assert "stub-extract-rsh-001-fixture-full_scaffold-c001" in result.stdout
