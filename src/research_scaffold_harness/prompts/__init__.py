"""Frozen prompt template loading, rendering, and hashing."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from importlib.resources import files
from typing import cast, get_args

import yaml

from research_scaffold_harness.contracts.hashing import hash_text
from research_scaffold_harness.models.common import WorkflowCondition
from research_scaffold_harness.models.task import TaskSpec


class PromptTemplateError(Exception):
    """Raised when a frozen prompt template is missing or malformed."""


@dataclass(frozen=True)
class PromptTemplate:
    """Frozen prompt template metadata and hashable body text."""

    template_id: str
    condition: WorkflowCondition
    version: str
    body: str


@dataclass(frozen=True)
class SourceContent:
    """Source text rendered into a bounded prompt source packet."""

    source_id: str
    text: str


def load_template(condition: WorkflowCondition) -> PromptTemplate:
    """Load a frozen prompt template by workflow condition."""
    valid_conditions = get_args(WorkflowCondition)
    if condition not in valid_conditions:
        raise PromptTemplateError(
            f"Invalid condition {condition!r}; expected one of {valid_conditions}"
        )

    template_file = files(__package__).joinpath(f"{condition}.md")
    try:
        text = template_file.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PromptTemplateError(f"Prompt template not found: {condition}") from exc
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    metadata, body = _split_frontmatter(text, str(template_file))
    template_condition = metadata["condition"]
    if template_condition != condition:
        raise PromptTemplateError(
            f"Template condition mismatch: requested {condition!r}, "
            f"file declares {template_condition!r}"
        )

    return PromptTemplate(
        template_id=metadata["template_id"],
        condition=cast(WorkflowCondition, template_condition),
        version=metadata["version"],
        body=body,
    )


def render_source_packet(sources: Sequence[SourceContent]) -> str:
    """Render source IDs and text into the prompt source-packet block."""
    return "\n\n".join(f"[Source: {source.source_id}]\n{source.text}" for source in sources)


def render_prompt(
    template: PromptTemplate,
    task: TaskSpec,
    sources: Sequence[SourceContent],
) -> str:
    """Render the prompt body for a task and bounded source packet."""
    replacements = {
        "{{ research_question }}": task.research_question,
        "{{ source_packet }}": render_source_packet(sources),
        "{{ source_ids }}": ", ".join(source.source_id for source in sources),
    }

    rendered = template.body
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    return rendered


def hash_template(template: PromptTemplate) -> str:
    """Hash the frozen template body, not a rendered task-specific prompt."""
    return hash_text(template.body)


def _split_frontmatter(text: str, source_name: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        raise PromptTemplateError(f"Missing YAML frontmatter in {source_name}")

    parts = text.split("---", 2)
    if len(parts) != 3:
        raise PromptTemplateError(f"Unclosed YAML frontmatter in {source_name}")

    raw_metadata = yaml.safe_load(parts[1])
    if not isinstance(raw_metadata, dict):
        raise PromptTemplateError(f"Invalid YAML frontmatter in {source_name}")

    required = ("template_id", "condition", "version")
    missing = [key for key in required if key not in raw_metadata]
    if missing:
        raise PromptTemplateError(
            f"Missing prompt frontmatter keys in {source_name}: {', '.join(missing)}"
        )

    metadata = {key: str(raw_metadata[key]) for key in required}
    return metadata, parts[2].lstrip("\n")
