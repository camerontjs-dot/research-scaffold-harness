"""Task-packet models for Phase 2 prompt rendering inputs."""

from __future__ import annotations

from typing import Literal, TypeAlias

from pydantic import Field

from research_scaffold_harness.models.common import (
    NonBlankStr,
    SourceType,
    StrictBaseModel,
    TrustLevel,
)

SourceScope: TypeAlias = Literal["bounded", "open"]


class TaskSpec(StrictBaseModel):
    """Source-packet task.yaml input."""

    task_id: NonBlankStr
    research_question: NonBlankStr
    domain: NonBlankStr
    expert_checkable: bool
    source_scope: SourceScope = "bounded"
    excluded_knowledge_rule: NonBlankStr = "none"
    ground_truth_ref: NonBlankStr | None = None
    notes: str = ""


class TaskSourceMeta(StrictBaseModel):
    """Lightweight source metadata used before C-A write-time expansion."""

    source_type: SourceType
    title: NonBlankStr
    url: NonBlankStr
    trust_level: TrustLevel
    authors: list[NonBlankStr] = Field(default_factory=list)
    publication_date: NonBlankStr | None = None
