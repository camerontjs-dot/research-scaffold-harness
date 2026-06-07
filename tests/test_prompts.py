"""Prompt template tests for Phase 2 Unit 1."""

from __future__ import annotations

from pathlib import Path
from typing import get_args

import pytest

from research_scaffold_harness.contracts.yaml_io import load_model_yaml
from research_scaffold_harness.models.common import WorkflowCondition
from research_scaffold_harness.models.task import TaskSpec
from research_scaffold_harness.prompts import (
    PromptTemplate,
    PromptTemplateError,
    SourceContent,
    hash_template,
    load_template,
    render_prompt,
    render_source_packet,
)

_FIXTURE_DIR = Path(__file__).parent / "fixtures" / "source-packet-minimal"
_CONDITIONS = get_args(WorkflowCondition)


@pytest.mark.parametrize("condition", _CONDITIONS)
def test_load_template_exists(condition: WorkflowCondition) -> None:
    template = load_template(condition)

    assert template.condition == condition
    assert template.template_id
    assert template.version == "1.0.0"


@pytest.mark.parametrize("condition", _CONDITIONS)
def test_template_body_contains_required_placeholders(condition: WorkflowCondition) -> None:
    template = load_template(condition)

    assert "{{ research_question }}" in template.body
    assert "{{ source_packet }}" in template.body


@pytest.mark.parametrize("condition", _CONDITIONS)
def test_template_condition_matches_filename(condition: WorkflowCondition) -> None:
    template = load_template(condition)

    assert template.condition == condition


def test_load_template_rejects_unknown_condition() -> None:
    with pytest.raises(PromptTemplateError, match="Invalid condition"):
        load_template("unknown")  # type: ignore[arg-type]


def test_render_source_packet_formats_sources() -> None:
    block = render_source_packet([
        SourceContent(source_id="src-001", text="First source text."),
        SourceContent(source_id="src-002", text="Second source text."),
    ])

    assert "[Source: src-001]" in block
    assert "First source text." in block
    assert "[Source: src-002]" in block
    assert "Second source text." in block


def test_render_prompt_substitutes_all_placeholders() -> None:
    task = load_model_yaml(TaskSpec, _FIXTURE_DIR / "task.yaml")
    source = SourceContent(source_id="src-001", text="Quality systems source text.")
    rendered = render_prompt(load_template("provenance_scaffold"), task, [source])

    assert "{{" not in rendered
    assert "}}" not in rendered


def test_render_prompt_contains_question_source_content_and_ids() -> None:
    task = load_model_yaml(TaskSpec, _FIXTURE_DIR / "task.yaml")
    source = SourceContent(source_id="src-001", text="Quality systems source text.")
    rendered = render_prompt(load_template("full_scaffold"), task, [source])

    assert task.research_question in rendered
    assert "Quality systems source text." in rendered
    assert "src-001" in rendered


def test_hash_template_deterministic() -> None:
    template = load_template("baseline")

    assert hash_template(template) == hash_template(template)


def test_hash_template_changes_on_edit() -> None:
    template = load_template("baseline")
    edited = PromptTemplate(
        template_id=template.template_id,
        condition=template.condition,
        version=template.version,
        body=template.body + "\nAdditional frozen instruction.",
    )

    assert hash_template(edited) != hash_template(template)


def test_hash_template_independent_of_task_data() -> None:
    template = load_template("format_only")
    first = TaskSpec(
        task_id="task-a",
        research_question="Question A?",
        domain="pharma_regulatory",
        expert_checkable=True,
    )
    second = TaskSpec(
        task_id="task-b",
        research_question="Question B?",
        domain="pharma_regulatory",
        expert_checkable=True,
    )

    render_prompt(template, first, [SourceContent(source_id="src-a", text="A")])
    render_prompt(template, second, [SourceContent(source_id="src-b", text="B")])

    assert hash_template(template) == hash_template(load_template("format_only"))
