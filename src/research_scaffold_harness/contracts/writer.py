"""C-A scaffold-run directory writer.

Takes typed model inputs and emits a complete scaffold-run-{run_id}/ directory
tree that satisfies Evidence Bundler verify-intake.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from research_scaffold_harness.contracts.hashing import (
    compute_corpus_hash,
    hash_file,
    write_sha256sums,
)
from research_scaffold_harness.contracts.yaml_io import dump_yaml, write_model_yaml
from research_scaffold_harness.models.ca import (
    ClaimsRegistry,
    ScaffoldRunManifest,
    SourceMetadata,
    SourcePassages,
)
from research_scaffold_harness.models.common import WRITER_SCHEMA_VERSION


class CAWriterError(Exception):
    """Raised when an integrity check fails during C-A artifact write."""


@dataclass(frozen=True)
class SourceWriteInput:
    """One source to write into corpus/{source_id}/."""

    source_id: str
    content_path: Path
    metadata: SourceMetadata
    passages: SourcePassages


@dataclass(frozen=True)
class IntermediatesWriteInput:
    """Optional intermediates for full_scaffold condition."""

    disconfirmation_pass: dict
    claim_table_draft: dict


@dataclass(frozen=True)
class SidecarTextWriteInput:
    """Non-schema text artifact to write inside a scaffold-run directory."""

    relative_path: str
    text: str


@dataclass(frozen=True)
class CAWriteInput:
    """All data needed to write a complete C-A artifact."""

    manifest: ScaffoldRunManifest
    claims: ClaimsRegistry
    sources: list[SourceWriteInput] = field(default_factory=list)
    intermediates: IntermediatesWriteInput | None = None
    sidecars: list[SidecarTextWriteInput] = field(default_factory=list)


def write_scaffold_run(write_input: CAWriteInput, output_dir: Path) -> Path:
    """Write a complete C-A scaffold-run artifact.

    Returns the path to the created scaffold-run-{run_id}/ directory.
    """
    run_id = write_input.manifest.run_id
    run_dir = output_dir / f"scaffold-run-{run_id}"
    run_dir.mkdir(parents=True, exist_ok=False)

    _verify_total_sources(write_input)
    _verify_cross_references(write_input)

    corpus_dir = run_dir / "corpus"
    corpus_dir.mkdir()
    for source in write_input.sources:
        _write_source(source, corpus_dir)

    _verify_corpus_hash(write_input.manifest, corpus_dir)

    write_model_yaml(write_input.manifest, run_dir / "scaffold_run.yaml")
    write_model_yaml(write_input.claims, run_dir / "claims.yaml")

    if write_input.intermediates is not None:
        _write_intermediates(write_input.intermediates, run_dir)

    _write_sidecars(write_input.sidecars, run_dir)

    (run_dir / "CONTRACT_VERSION").write_text(
        WRITER_SCHEMA_VERSION + "\n", encoding="utf-8"
    )

    write_sha256sums(run_dir)
    return run_dir


def _write_source(source: SourceWriteInput, corpus_dir: Path) -> None:
    source_dir = corpus_dir / source.source_id
    source_dir.mkdir()

    if not source.content_path.exists():
        raise CAWriterError(
            f"Content file missing for {source.source_id}: {source.content_path}"
        )

    dest = source_dir / f"content{source.content_path.suffix}"
    shutil.copy2(source.content_path, dest)

    actual_hash = hash_file(dest)
    if actual_hash != source.metadata.content_hash:
        raise CAWriterError(
            f"content_hash mismatch for {source.source_id}: "
            f"expected {source.metadata.content_hash}, got {actual_hash}"
        )

    write_model_yaml(source.metadata, source_dir / "metadata.yaml", exclude_none=True)
    write_model_yaml(source.passages, source_dir / "passages.yaml", exclude_none=True)


def _write_intermediates(intermediates: IntermediatesWriteInput, run_dir: Path) -> None:
    intermediates_dir = run_dir / "intermediates"
    intermediates_dir.mkdir()
    dump_yaml(intermediates.disconfirmation_pass, intermediates_dir / "disconfirmation_pass.yaml")
    dump_yaml(intermediates.claim_table_draft, intermediates_dir / "claim_table_draft.yaml")


def _write_sidecars(sidecars: list[SidecarTextWriteInput], run_dir: Path) -> None:
    seen: set[str] = set()
    for sidecar in sidecars:
        destination = _resolve_sidecar_path(run_dir, sidecar.relative_path)
        rel = destination.relative_to(run_dir).as_posix()
        if rel in seen:
            raise CAWriterError(f"Duplicate sidecar path: {rel}")
        seen.add(rel)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(sidecar.text, encoding="utf-8")


def _resolve_sidecar_path(run_dir: Path, relative_path: str) -> Path:
    rel_path = Path(relative_path)
    if not relative_path or rel_path.is_absolute():
        raise CAWriterError(f"Invalid sidecar path: {relative_path!r}")
    if any(part in {"", ".", ".."} for part in rel_path.parts):
        raise CAWriterError(f"Unsafe sidecar path: {relative_path!r}")
    if rel_path.parts[0] == "corpus":
        raise CAWriterError("Sidecars must not be written under corpus/")
    if rel_path.as_posix() in {
        "scaffold_run.yaml",
        "claims.yaml",
        "CONTRACT_VERSION",
        "SHA256SUMS",
    }:
        raise CAWriterError(f"Sidecar path would overwrite required file: {relative_path}")

    destination = run_dir / rel_path
    resolved_run_dir = run_dir.resolve()
    resolved_destination_parent = destination.parent.resolve()
    if resolved_run_dir != resolved_destination_parent and (
        resolved_run_dir not in resolved_destination_parent.parents
    ):
        raise CAWriterError(f"Unsafe sidecar path escapes run directory: {relative_path!r}")
    return destination


def _verify_total_sources(write_input: CAWriteInput) -> None:
    expected = write_input.manifest.corpus.total_sources
    actual = len(write_input.sources)
    if expected != actual:
        raise CAWriterError(
            f"total_sources mismatch: manifest says {expected}, got {actual} sources"
        )


def _verify_corpus_hash(manifest: ScaffoldRunManifest, corpus_dir: Path) -> None:
    expected = manifest.corpus.corpus_hash
    actual = compute_corpus_hash(corpus_dir)
    if actual != expected:
        raise CAWriterError(
            f"corpus_hash mismatch: manifest says {expected}, computed {actual}"
        )


def _verify_cross_references(write_input: CAWriteInput) -> None:
    passage_keys: set[tuple[str, str]] = set()
    for source in write_input.sources:
        for passage in source.passages.passages:
            passage_keys.add((source.source_id, passage.passage_id))

    for claim in write_input.claims.claims:
        for ref in claim.source_refs:
            if (ref.source_id, ref.passage_id) not in passage_keys:
                raise CAWriterError(
                    f"claim {claim.claim_id} references missing passage "
                    f"{ref.source_id}/{ref.passage_id}"
                )
