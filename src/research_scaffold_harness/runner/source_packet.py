"""Source-packet loading for prompt runner inputs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from research_scaffold_harness.contracts.yaml_io import load_model_yaml
from research_scaffold_harness.models.task import TaskSourceMeta, TaskSpec
from research_scaffold_harness.prompts import SourceContent


class SourcePacketError(Exception):
    """Raised when a task source packet cannot be loaded for a runner."""


@dataclass(frozen=True)
class SourcePacketSource:
    """One source-packet source with prompt-readable text."""

    source_id: str
    content_path: Path
    metadata: TaskSourceMeta
    text: str

    def to_prompt_source(self) -> SourceContent:
        """Convert to the prompt renderer's minimal source content type."""
        return SourceContent(source_id=self.source_id, text=self.text)


@dataclass(frozen=True)
class SourcePacket:
    """Validated task spec plus prompt-readable source texts."""

    task: TaskSpec
    sources: tuple[SourcePacketSource, ...]

    def prompt_sources(self) -> tuple[SourceContent, ...]:
        """Return source text in the form expected by frozen prompt rendering."""
        return tuple(source.to_prompt_source() for source in self.sources)


def load_source_packet(task_dir: Path) -> SourcePacket:
    """Load a bounded task source packet for an offline runner.

    Unit 2 intentionally supports text-like source content only. PDF handling
    and the real RSH-001 source packet remain outside this deterministic slice.
    """
    task_path = task_dir / "task.yaml"
    if not task_path.exists():
        raise SourcePacketError(f"task.yaml not found in {task_dir}")

    try:
        task = load_model_yaml(TaskSpec, task_path)
    except Exception as exc:
        raise SourcePacketError(f"Invalid task.yaml in {task_dir}: {exc}") from exc

    sources_dir = task_dir / "sources"
    if not sources_dir.is_dir():
        raise SourcePacketError(f"sources/ directory not found in {task_dir}")

    sources: list[SourcePacketSource] = []
    for source_dir in sorted(path for path in sources_dir.iterdir() if path.is_dir()):
        content_path = _find_prompt_readable_content(source_dir)
        meta_path = source_dir / "metadata.yaml"
        if not meta_path.exists():
            raise SourcePacketError(f"metadata.yaml missing in {source_dir}")

        try:
            metadata = load_model_yaml(TaskSourceMeta, meta_path)
        except Exception as exc:
            raise SourcePacketError(f"Invalid metadata.yaml in {source_dir}: {exc}") from exc

        sources.append(SourcePacketSource(
            source_id=source_dir.name,
            content_path=content_path,
            metadata=metadata,
            text=content_path.read_text(encoding="utf-8"),
        ))

    if not sources:
        raise SourcePacketError(f"No source directories found under {sources_dir}")

    return SourcePacket(task=task, sources=tuple(sources))


def _find_prompt_readable_content(source_dir: Path) -> Path:
    matches = [
        candidate for candidate in (source_dir / "content.md", source_dir / "content.txt")
        if candidate.exists()
    ]
    if not matches:
        raise SourcePacketError(
            f"Prompt-readable content.md or content.txt missing in {source_dir}"
        )
    if len(matches) > 1:
        names = ", ".join(path.name for path in matches)
        raise SourcePacketError(f"Multiple prompt-readable content files in {source_dir}: {names}")
    return matches[0]
