"""Offline prompt runner orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import get_args

from research_scaffold_harness.contracts.hashing import hash_text
from research_scaffold_harness.models.common import WorkflowCondition
from research_scaffold_harness.models.task import TaskSpec
from research_scaffold_harness.prompts import (
    SourceContent,
    hash_template,
    load_template,
    render_prompt,
)
from research_scaffold_harness.runner.adapters import (
    ModelAdapter,
    ModelRequest,
    ModelResponse,
)
from research_scaffold_harness.runner.source_packet import SourcePacket


class RunnerError(Exception):
    """Raised when runner inputs are invalid."""


@dataclass(frozen=True)
class RunnerSettings:
    """Generation settings shared by adapter requests."""

    temperature: float = 0.0
    max_tokens: int = 512

    def __post_init__(self) -> None:
        if self.temperature < 0:
            raise RunnerError("temperature must be >= 0")
        if self.max_tokens <= 0:
            raise RunnerError("max_tokens must be > 0")


@dataclass(frozen=True)
class RunnerResult:
    """Raw deterministic run result before extraction or C-A writing."""

    task_id: str
    condition: WorkflowCondition
    prompt_template_id: str
    prompt_template_hash: str
    rendered_prompt_hash: str
    prompt: str
    response: ModelResponse

    @property
    def output_text(self) -> str:
        """Adapter-generated raw output text."""
        return self.response.text


def run_source_packet(
    packet: SourcePacket,
    condition: WorkflowCondition,
    adapter: ModelAdapter,
    settings: RunnerSettings | None = None,
    prompt_suffix: str | None = None,
) -> RunnerResult:
    """Render a source-packet prompt and execute it with a model adapter."""
    return run_task(
        task=packet.task,
        sources=packet.prompt_sources(),
        condition=condition,
        adapter=adapter,
        settings=settings,
        prompt_suffix=prompt_suffix,
    )


def run_task(
    task: TaskSpec,
    sources: tuple[SourceContent, ...],
    condition: WorkflowCondition,
    adapter: ModelAdapter,
    settings: RunnerSettings | None = None,
    prompt_suffix: str | None = None,
) -> RunnerResult:
    """Run a rendered frozen prompt through an adapter and return raw output.

    ``prompt_suffix`` (Exploratory scaffold probes only) appends an instruction
    block AFTER the frozen rendered prompt. The frozen template body and its
    ``prompt_template_hash`` are unchanged; only ``rendered_prompt_hash`` shifts,
    so provenance distinguishes a nudged run from the frozen baseline.
    """
    if condition not in get_args(WorkflowCondition):
        raise RunnerError(f"Invalid condition {condition!r}")
    if not sources:
        raise RunnerError("at least one source is required")

    run_settings = settings or RunnerSettings()
    template = load_template(condition)
    prompt = render_prompt(template, task, sources)
    if prompt_suffix:
        prompt = f"{prompt.rstrip()}\n\n{prompt_suffix.strip()}\n"
    prompt_template_hash = hash_template(template)
    rendered_prompt_hash = hash_text(prompt)

    response = adapter.generate(ModelRequest(
        task=task,
        condition=condition,
        prompt=prompt,
        prompt_template_id=template.template_id,
        prompt_template_hash=prompt_template_hash,
        rendered_prompt_hash=rendered_prompt_hash,
        sources=sources,
        temperature=run_settings.temperature,
        max_tokens=run_settings.max_tokens,
    ))

    return RunnerResult(
        task_id=task.task_id,
        condition=condition,
        prompt_template_id=template.template_id,
        prompt_template_hash=prompt_template_hash,
        rendered_prompt_hash=rendered_prompt_hash,
        prompt=prompt,
        response=response,
    )
