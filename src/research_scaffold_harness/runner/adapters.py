"""Model-adapter interfaces and deterministic offline adapters."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from research_scaffold_harness.contracts.hashing import hash_text
from research_scaffold_harness.models.common import WorkflowCondition
from research_scaffold_harness.models.task import TaskSpec
from research_scaffold_harness.prompts import SourceContent


@dataclass(frozen=True)
class ModelRequest:
    """Rendered prompt plus run context passed to a model adapter."""

    task: TaskSpec
    condition: WorkflowCondition
    prompt: str
    prompt_template_id: str
    prompt_template_hash: str
    rendered_prompt_hash: str
    sources: tuple[SourceContent, ...]
    temperature: float
    max_tokens: int


@dataclass(frozen=True)
class ModelResponse:
    """Raw response returned by a model adapter."""

    model_id: str
    model_version: str
    api_endpoint: str
    text: str
    finish_reason: str
    output_tokens: int
    model_revision: str = ""
    quantization: str = ""
    chat_template_applied: bool = False
    temperature: float = 0.0
    max_tokens: int = 0


@runtime_checkable
class ModelAdapter(Protocol):
    """Minimal interface shared by offline stubs and future MLX adapters."""

    @property
    def model_id(self) -> str:
        """Stable model identifier to record with the raw run result."""

    @property
    def model_version(self) -> str:
        """Adapter/model version string."""

    @property
    def api_endpoint(self) -> str:
        """Runtime endpoint descriptor, or a non-network sentinel for offline adapters."""

    def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a raw response for a rendered prompt."""


class StubModelAdapter:
    """Deterministic offline adapter for runner plumbing tests."""

    model_id = "stub-offline-deterministic"
    model_version = "0.1.0"
    api_endpoint = "stub://offline"

    def generate(self, request: ModelRequest) -> ModelResponse:
        """Return condition-shaped deterministic text without loading an ML model."""
        text = _stub_output(request)
        return ModelResponse(
            model_id=self.model_id,
            model_version=self.model_version,
            api_endpoint=self.api_endpoint,
            text=text,
            finish_reason="stop",
            output_tokens=len(text.split()),
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )


def _stub_output(request: ModelRequest) -> str:
    signature = hash_text("\n".join((
        request.task.task_id,
        request.condition,
        request.prompt_template_hash,
        request.rendered_prompt_hash,
        ",".join(source.source_id for source in request.sources),
    )))[len("sha256:"):][:16]
    source_ids = ", ".join(source.source_id for source in request.sources)
    excerpt = _first_source_excerpt(request.sources)

    header = "\n".join((
        "STUB MODEL OUTPUT - OFFLINE DETERMINISTIC",
        f"task_id: {request.task.task_id}",
        f"condition: {request.condition}",
        f"prompt_template_id: {request.prompt_template_id}",
        f"stub_signature: {signature}",
        "",
    ))

    if request.condition == "baseline":
        body = "\n".join((
            f"Using {source_ids}, the source packet supports a bounded answer to:",
            request.task.research_question,
            f"Representative source text: {excerpt}",
            "",
            "Final claims:",
            f"- The source packet supports a bounded answer to {request.task.research_question}",
            f"- Representative source text from {source_ids}: {excerpt}",
        ))
    elif request.condition == "format_only":
        body = "\n".join((
            "Claim table:",
            "| claim text |",
            "| --- |",
            f"| The bounded packet contains material responsive to {request.task.task_id}. |",
            "",
            f"A concise answer can be drafted from {source_ids}: {excerpt}",
            "",
            "Final claims:",
            f"- The bounded packet contains material responsive to {request.task.task_id}",
            f"- A concise answer can be drafted from {source_ids} using: {excerpt}",
        ))
    elif request.condition == "provenance_scaffold":
        body = "\n".join((
            "Claim table:",
            "| claim text | support status | source id | basis |",
            "| --- | --- | --- | --- |",
            (
                "| The packet gives bounded support for the requested assessment. "
                f"| sourced | {source_ids} | Stub excerpt: {excerpt} |"
            ),
            "",
            f"The answer should stay tied to {source_ids} and qualify anything beyond it.",
            "",
            "Final claims:",
            f"- The packet gives bounded support for the requested assessment from {source_ids}",
            f"- The answer should stay tied to {source_ids} and qualify anything beyond it",
        ))
    else:
        body = "\n".join((
            "Answer plan:",
            "- Use only the bounded source packet.",
            "- Retain supported observations and mark scope limits.",
            "",
            "Evidence note table:",
            f"- {source_ids}: {excerpt}",
            "",
            "Disconfirmation pass:",
            "- No live counterevidence search was performed by the offline stub.",
            "",
            "Final claim audit table:",
            "| claim | disposition | rationale |",
            "| --- | --- | --- |",
            "| Bounded source-packet answer | retained | Present in provided text. |",
            "",
            f"The response is constrained to {source_ids}; unsupported extensions stay out.",
            "",
            "Final claims:",
            f"- The bounded source-packet answer is retained for {source_ids}",
            f"- The response is constrained to {source_ids} and unsupported extensions stay out",
        ))

    return header + body + "\n"


def _first_source_excerpt(sources: Sequence[SourceContent], *, max_chars: int = 180) -> str:
    for source in sources:
        for line in source.text.splitlines():
            normalized = " ".join(line.split())
            if normalized and not normalized.startswith("#"):
                if len(normalized) <= max_chars:
                    return normalized
                return normalized[: max_chars - 3].rstrip() + "..."
    return "No non-heading source text supplied."
