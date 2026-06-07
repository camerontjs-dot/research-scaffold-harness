"""Task-packet model tests for Phase 2 Unit 1."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from research_scaffold_harness.contracts.yaml_io import (
    dump_yaml,
    load_model_yaml,
)
from research_scaffold_harness.models.task import TaskSourceMeta, TaskSpec

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source-packet-minimal"


def test_task_spec_from_fixture_yaml() -> None:
    task = load_model_yaml(TaskSpec, _FIXTURE_DIR / "task.yaml")

    assert task.task_id == "rsh-001-fixture"
    assert task.source_scope == "bounded"
    assert task.excluded_knowledge_rule == "none"
    assert task.notes == ""


def test_task_source_meta_from_fixture_yaml() -> None:
    meta = load_model_yaml(
        TaskSourceMeta,
        _FIXTURE_DIR / "sources" / "src-001" / "metadata.yaml",
    )

    assert meta.source_type == "regulatory_guidance"
    assert meta.trust_level == "primary"
    assert meta.authors == []
    assert meta.publication_date is None


def test_task_spec_rejects_missing_task_id() -> None:
    with pytest.raises(ValidationError):
        TaskSpec.model_validate({
            "research_question": "What does the packet support?",
            "domain": "pharma_regulatory",
            "expert_checkable": True,
        })


def test_task_spec_rejects_blank_question() -> None:
    with pytest.raises(ValidationError):
        TaskSpec.model_validate({
            "task_id": "rsh-test",
            "research_question": " ",
            "domain": "pharma_regulatory",
            "expert_checkable": True,
        })


def test_task_spec_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TaskSpec.model_validate({
            "task_id": "rsh-test",
            "research_question": "What does the packet support?",
            "domain": "pharma_regulatory",
            "expert_checkable": True,
            "unexpected": "drift",
        })


def test_task_spec_rejects_invalid_source_scope() -> None:
    with pytest.raises(ValidationError):
        TaskSpec.model_validate({
            "task_id": "rsh-test",
            "research_question": "What does the packet support?",
            "domain": "pharma_regulatory",
            "expert_checkable": True,
            "source_scope": "live_web",
        })


def test_task_source_meta_rejects_invalid_trust_level() -> None:
    with pytest.raises(ValidationError):
        TaskSourceMeta.model_validate({
            "source_type": "regulatory_guidance",
            "title": "CGMP note",
            "url": "https://example.com/source",
            "trust_level": "tertiary",
        })


def test_task_source_meta_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        TaskSourceMeta.model_validate({
            "source_type": "regulatory_guidance",
            "title": "CGMP note",
            "url": "https://example.com/source",
            "trust_level": "primary",
            "content_hash": "not-yet",
        })


def test_task_spec_yaml_round_trip(tmp_path: Path) -> None:
    task = TaskSpec(
        task_id="rsh-round-trip",
        research_question="What does the packet support?",
        domain="pharma_regulatory",
        expert_checkable=True,
        ground_truth_ref="gold/rsh-round-trip.yaml",
        notes="fixture",
    )
    path = tmp_path / "task.yaml"

    dump_yaml(task.model_dump(mode="json"), path)

    assert load_model_yaml(TaskSpec, path) == task


def test_task_source_meta_yaml_round_trip(tmp_path: Path) -> None:
    meta = TaskSourceMeta(
        source_type="regulatory_guidance",
        title="CGMP note",
        url="https://example.com/source",
        trust_level="primary",
        authors=["FDA"],
        publication_date="2006-09",
    )
    path = tmp_path / "metadata.yaml"

    dump_yaml(meta.model_dump(mode="json"), path)

    assert load_model_yaml(TaskSourceMeta, path) == meta
